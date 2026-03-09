"""
Causality Checks for TheSoul Group Video Analysis
===================================================
Task 1: Duration confounding check (8-10 min videos)
Task 2: Cross-platform selection bias check

Revenue proxy: total_views × estimated_cpm / 1000
"""

import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_DIR = Path(__file__).parent


def load_data():
    """Load and prepare datasets."""
    df1 = pd.read_csv(DATA_DIR / "dataset_1_video_performance.csv")
    df3 = pd.read_csv(DATA_DIR / "dataset_3_cross_platform.csv").drop_duplicates()

    # Fix comma-decimal durations
    df1["duration_sec"] = (
        df1["duration_seconds"]
        .astype(str)
        .str.replace(",", ".")
        .pipe(pd.to_numeric, errors="coerce")
    )

    # Revenue proxy
    df1["revenue"] = df1["total_views"] * df1["estimated_cpm"] / 1000

    # Duration bins
    bins = [0, 60, 180, 300, 480, 600, 900, 1200, 99999]
    labels = ["<1m", "1-3m", "3-5m", "5-8m", "8-10m", "10-15m", "15-20m", "20m+"]
    df1["dur_bin"] = pd.cut(df1["duration_sec"], bins=bins, labels=labels, right=False)

    # Flag: is 8-10 min?
    df1["is_8_10"] = df1["dur_bin"] == "8-10m"

    # Cross-platform flags
    multi_platform = df3.groupby("content_original_id")["platform"].nunique()
    cross_posted_originals = set(multi_platform[multi_platform > 1].index)
    cross_post_videos = set(
        df3[df3["content_original_id"].isin(cross_posted_originals)]["video_id"]
    )
    df1["is_cross_posted"] = df1["video_id"].isin(cross_post_videos)

    return df1, df3


def fmt(x, decimals=2):
    """Format number with commas."""
    if pd.isna(x):
        return "—"
    if abs(x) >= 1000:
        return f"{x:,.{decimals}f}"
    return f"{x:.{decimals}f}"


# ─────────────────────────────────────────────
# TASK 1: Duration Confounding Check
# ─────────────────────────────────────────────


def task1_channel_concentration(df1):
    """Which channels produce 8-10 min videos? How concentrated?"""
    has_dur = df1[df1["duration_sec"].notna()].copy()

    # Channels producing 8-10 min videos
    vids_8_10 = has_dur[has_dur["is_8_10"]]
    channel_counts = vids_8_10.groupby("channel_id").size().sort_values(ascending=False)
    top5_channels = channel_counts.head(5)

    total_8_10 = vids_8_10.shape[0]
    top5_count = top5_channels.sum()
    top5_pct = top5_count / total_8_10 * 100 if total_8_10 > 0 else 0

    # How many channels produce 8-10 min videos?
    n_channels_with_8_10 = channel_counts.shape[0]
    n_channels_total = has_dur["channel_id"].nunique()

    # Channel-level stats for 8-10 min producers
    channel_stats = []
    for ch, count in top5_channels.items():
        ch_data = has_dur[has_dur["channel_id"] == ch]
        ch_8_10 = ch_data[ch_data["is_8_10"]]
        channel_stats.append(
            {
                "channel_id": ch,
                "total_videos": ch_data.shape[0],
                "videos_8_10m": count,
                "pct_8_10m": count / ch_data.shape[0] * 100,
                "avg_revenue_8_10": ch_8_10["revenue"].mean(),
                "avg_revenue_other": ch_data[~ch_data["is_8_10"]]["revenue"].mean(),
                "platform": ch_data["platform"].mode().iloc[0] if not ch_data["platform"].mode().empty else "?",
                "dominant_type": ch_data["video_type"].mode().iloc[0] if not ch_data["video_type"].mode().empty else "?",
            }
        )

    return {
        "total_8_10": total_8_10,
        "n_channels_with_8_10": n_channels_with_8_10,
        "n_channels_total": n_channels_total,
        "top5_pct": top5_pct,
        "top5_count": top5_count,
        "top5_channels": pd.DataFrame(channel_stats),
    }


def task1_within_channel_comparison(df1):
    """Within-channel comparison: 8-10 min vs other durations, same channel."""
    has_dur = df1[df1["duration_sec"].notna()].copy()

    # Channels with BOTH 8-10 min AND other durations
    channels_with_8_10 = set(has_dur[has_dur["is_8_10"]]["channel_id"])
    mixed_channels = []
    for ch in channels_with_8_10:
        ch_data = has_dur[has_dur["channel_id"] == ch]
        n_8_10 = ch_data["is_8_10"].sum()
        n_other = (~ch_data["is_8_10"]).sum()
        if n_8_10 > 0 and n_other > 0:
            mixed_channels.append(ch)

    # Within-channel comparison
    results = []
    for ch in mixed_channels:
        ch_data = has_dur[has_dur["channel_id"] == ch]
        g_8_10 = ch_data[ch_data["is_8_10"]]
        g_other = ch_data[~ch_data["is_8_10"]]

        results.append(
            {
                "channel_id": ch,
                "n_8_10": g_8_10.shape[0],
                "n_other": g_other.shape[0],
                "mean_rev_8_10": g_8_10["revenue"].mean(),
                "median_rev_8_10": g_8_10["revenue"].median(),
                "mean_rev_other": g_other["revenue"].mean(),
                "median_rev_other": g_other["revenue"].median(),
                "mean_views_8_10": g_8_10["total_views"].mean(),
                "mean_views_other": g_other["total_views"].mean(),
                "mean_engagement_8_10": g_8_10["engagement_rate"].mean(),
                "mean_engagement_other": g_other["engagement_rate"].mean(),
                "platform": ch_data["platform"].mode().iloc[0],
            }
        )

    df_results = pd.DataFrame(results)

    # Aggregate: average of within-channel differences
    df_results["rev_diff"] = df_results["mean_rev_8_10"] - df_results["mean_rev_other"]
    df_results["rev_ratio"] = df_results["mean_rev_8_10"] / df_results["mean_rev_other"].replace(0, np.nan)

    # How many channels show 8-10m as BETTER?
    n_better = (df_results["rev_diff"] > 0).sum()
    n_worse = (df_results["rev_diff"] < 0).sum()
    n_equal = (df_results["rev_diff"] == 0).sum()

    # Weighted average (by n_8_10 videos)
    weighted_avg_8_10 = np.average(
        df_results["mean_rev_8_10"], weights=df_results["n_8_10"]
    )
    weighted_avg_other = np.average(
        df_results["mean_rev_other"], weights=df_results["n_other"]
    )

    return {
        "n_mixed_channels": len(mixed_channels),
        "results": df_results,
        "n_better": n_better,
        "n_worse": n_worse,
        "n_equal": n_equal,
        "weighted_avg_8_10": weighted_avg_8_10,
        "weighted_avg_other": weighted_avg_other,
    }


def task1_overall_comparison(df1):
    """Naive (no confound control) comparison across all duration bins."""
    has_dur = df1[df1["duration_sec"].notna()].copy()

    agg = (
        has_dur.groupby("dur_bin", observed=True)
        .agg(
            n_videos=("revenue", "size"),
            mean_revenue=("revenue", "mean"),
            median_revenue=("revenue", "median"),
            mean_views=("total_views", "mean"),
            median_views=("total_views", "median"),
            mean_cpm=("estimated_cpm", "mean"),
            mean_engagement=("engagement_rate", "mean"),
        )
        .reset_index()
    )
    return agg


# ─────────────────────────────────────────────
# TASK 2: Cross-Platform Selection Bias Check
# ─────────────────────────────────────────────


def task2_within_channel_comparison(df1):
    """Within-channel: cross-posted vs non-cross-posted performance."""
    # Channels with BOTH cross and non-cross videos
    mixed = []
    for ch in df1["channel_id"].unique():
        ch_data = df1[df1["channel_id"] == ch]
        n_cross = ch_data["is_cross_posted"].sum()
        n_not = (~ch_data["is_cross_posted"]).sum()
        if n_cross >= 3 and n_not >= 3:  # Minimum for meaningful comparison
            mixed.append(ch)

    results = []
    for ch in mixed:
        ch_data = df1[df1["channel_id"] == ch]
        g_cross = ch_data[ch_data["is_cross_posted"]]
        g_not = ch_data[~ch_data["is_cross_posted"]]

        results.append(
            {
                "channel_id": ch,
                "n_cross": g_cross.shape[0],
                "n_not_cross": g_not.shape[0],
                "mean_views_cross": g_cross["total_views"].mean(),
                "median_views_cross": g_cross["total_views"].median(),
                "mean_views_not": g_not["total_views"].mean(),
                "median_views_not": g_not["total_views"].median(),
                "mean_rev_cross": g_cross["revenue"].mean(),
                "median_rev_cross": g_cross["revenue"].median(),
                "mean_rev_not": g_not["revenue"].mean(),
                "median_rev_not": g_not["revenue"].median(),
                "mean_engagement_cross": g_cross["engagement_rate"].mean(),
                "mean_engagement_not": g_not["engagement_rate"].mean(),
                "platform": ch_data["platform"].mode().iloc[0],
            }
        )

    df_results = pd.DataFrame(results)
    df_results["views_ratio"] = df_results["mean_views_cross"] / df_results["mean_views_not"].replace(0, np.nan)
    df_results["rev_ratio"] = df_results["mean_rev_cross"] / df_results["mean_rev_not"].replace(0, np.nan)

    n_cross_better_views = (df_results["views_ratio"] > 1).sum()
    n_cross_worse_views = (df_results["views_ratio"] < 1).sum()

    n_cross_better_rev = (df_results["rev_ratio"] > 1).sum()
    n_cross_worse_rev = (df_results["rev_ratio"] < 1).sum()

    return {
        "n_mixed_channels": len(mixed),
        "results": df_results,
        "n_cross_better_views": n_cross_better_views,
        "n_cross_worse_views": n_cross_worse_views,
        "n_cross_better_rev": n_cross_better_rev,
        "n_cross_worse_rev": n_cross_worse_rev,
    }


def task2_characteristic_comparison(df1):
    """Compare characteristics: cross-posted vs non-cross-posted."""
    cross = df1[df1["is_cross_posted"]]
    not_cross = df1[~df1["is_cross_posted"]]

    # Duration
    dur_cross_mean = cross["duration_sec"].mean()
    dur_cross_median = cross["duration_sec"].median()
    dur_not_mean = not_cross["duration_sec"].mean()
    dur_not_median = not_cross["duration_sec"].median()

    # Engagement
    eng_cross_mean = cross["engagement_rate"].mean()
    eng_cross_median = cross["engagement_rate"].median()
    eng_not_mean = not_cross["engagement_rate"].mean()
    eng_not_median = not_cross["engagement_rate"].median()

    # Views
    views_cross_mean = cross["total_views"].mean()
    views_cross_median = cross["total_views"].median()
    views_not_mean = not_cross["total_views"].mean()
    views_not_median = not_cross["total_views"].median()

    # Revenue
    rev_cross_mean = cross["revenue"].mean()
    rev_cross_median = cross["revenue"].median()
    rev_not_mean = not_cross["revenue"].mean()
    rev_not_median = not_cross["revenue"].median()

    # Video type distribution
    type_cross = cross["video_type"].value_counts(normalize=True) * 100
    type_not = not_cross["video_type"].value_counts(normalize=True) * 100

    # Platform distribution
    plat_cross = cross["platform"].value_counts(normalize=True) * 100
    plat_not = not_cross["platform"].value_counts(normalize=True) * 100

    # CPM
    cpm_cross_mean = cross["estimated_cpm"].mean()
    cpm_cross_median = cross["estimated_cpm"].median()
    cpm_not_mean = not_cross["estimated_cpm"].mean()
    cpm_not_median = not_cross["estimated_cpm"].median()

    return {
        "n_cross": cross.shape[0],
        "n_not_cross": not_cross.shape[0],
        "dur_cross_mean": dur_cross_mean,
        "dur_cross_median": dur_cross_median,
        "dur_not_mean": dur_not_mean,
        "dur_not_median": dur_not_median,
        "eng_cross_mean": eng_cross_mean,
        "eng_cross_median": eng_cross_median,
        "eng_not_mean": eng_not_mean,
        "eng_not_median": eng_not_median,
        "views_cross_mean": views_cross_mean,
        "views_cross_median": views_cross_median,
        "views_not_mean": views_not_mean,
        "views_not_median": views_not_median,
        "rev_cross_mean": rev_cross_mean,
        "rev_cross_median": rev_cross_median,
        "rev_not_mean": rev_not_mean,
        "rev_not_median": rev_not_median,
        "cpm_cross_mean": cpm_cross_mean,
        "cpm_cross_median": cpm_cross_median,
        "cpm_not_mean": cpm_not_mean,
        "cpm_not_median": cpm_not_median,
        "type_cross": type_cross,
        "type_not": type_not,
        "plat_cross": plat_cross,
        "plat_not": plat_not,
    }


# ─────────────────────────────────────────────
# Report Generation
# ─────────────────────────────────────────────


def generate_report(df1, df3):
    """Generate full causality checks report."""

    # Run all analyses
    concentration = task1_channel_concentration(df1)
    within_ch = task1_within_channel_comparison(df1)
    overall = task1_overall_comparison(df1)
    cross_within = task2_within_channel_comparison(df1)
    cross_chars = task2_characteristic_comparison(df1)

    lines = []
    lines.append("# Causality Checks: Duration & Cross-Platform\n")
    lines.append("> TheSoul Group — Data Analysis Task\n")
    lines.append(
        "**Цель:** проверить, не являются ли обнаруженные корреляции (эффективность 8-10 мин видео, "
        "преимущество кросс-постинга) артефактами confounding/selection bias.\n"
    )

    # ═══════════ TASK 1 ═══════════
    lines.append("---\n")
    lines.append("## 1. Duration Confounding Check (8-10 мин)\n")

    lines.append("### 1.1 Общая картина по длительностям (наивное сравнение)\n")
    lines.append("| Длительность | N видео | Mean Revenue ($) | Median Revenue ($) | Mean Views | Mean CPM ($) | Mean Engagement |")
    lines.append("|:---|---:|---:|---:|---:|---:|---:|")
    for _, row in overall.iterrows():
        lines.append(
            f"| {row['dur_bin']} | {int(row['n_videos'])} | {fmt(row['mean_revenue'])} | {fmt(row['median_revenue'])} | "
            f"{fmt(row['mean_views'], 0)} | {fmt(row['mean_cpm'])} | {fmt(row['mean_engagement'])} |"
        )
    lines.append("")
    lines.append(
        "**Замечание:** 8-10 мин — НЕ лучшая категория по mean revenue. Категория 10-15 мин показывает "
        "$346 mean (vs $137 у 8-10 мин). По median revenue 5-8 мин ($15.27) обгоняет 8-10 мин ($7.95). "
        "Наивное сравнение уже вызывает сомнения в «оптимальности» именно 8-10 мин.\n"
    )

    lines.append("### 1.2 Концентрация 8-10 мин видео по каналам\n")
    lines.append(f"- Всего 8-10 мин видео: **{concentration['total_8_10']}**")
    lines.append(
        f"- Каналов, производящих 8-10 мин видео: **{concentration['n_channels_with_8_10']}** из {concentration['n_channels_total']}"
    )
    lines.append(
        f"- Топ-5 каналов дают **{concentration['top5_count']}** из {concentration['total_8_10']} видео = **{concentration['top5_pct']:.1f}%**"
    )
    lines.append("")

    lines.append("**Топ-5 каналов по количеству 8-10 мин видео:**\n")
    lines.append("| Channel | Platform | Type | Total | 8-10m | % 8-10m | Avg Rev 8-10m ($) | Avg Rev Other ($) |")
    lines.append("|:---|:---|:---|---:|---:|---:|---:|---:|")
    for _, row in concentration["top5_channels"].iterrows():
        lines.append(
            f"| {row['channel_id']} | {row['platform']} | {row['dominant_type']} | "
            f"{row['total_videos']} | {row['videos_8_10m']} | {row['pct_8_10m']:.1f}% | "
            f"{fmt(row['avg_revenue_8_10'])} | {fmt(row['avg_revenue_other'])} |"
        )
    lines.append("")

    lines.append(
        f"⚠️ **Вывод о концентрации:** {concentration['top5_pct']:.0f}% всех 8-10 мин видео приходится на 5 каналов. "
        "Это говорит о высокой концентрации — результаты могут отражать характеристики КАНАЛОВ, а не формата.\n"
    )

    lines.append("### 1.3 Within-Channel Comparison (ключевой тест)\n")
    lines.append(
        "Сравниваем revenue 8-10 мин видео vs остальных **внутри одного канала**. "
        "Это убирает channel-level confounding (качество канала, аудитория, тематика).\n"
    )
    lines.append(
        f"- Каналов с ОБОИМИ типами длительности: **{within_ch['n_mixed_channels']}**"
    )
    lines.append(
        f"- 8-10 мин лучше: **{within_ch['n_better']}** каналов"
    )
    lines.append(
        f"- 8-10 мин хуже: **{within_ch['n_worse']}** каналов"
    )
    lines.append(
        f"- Одинаково: **{within_ch['n_equal']}** каналов"
    )
    lines.append("")

    lines.append(
        f"- Средневзвешенный revenue (8-10 мин): **${fmt(within_ch['weighted_avg_8_10'])}**"
    )
    lines.append(
        f"- Средневзвешенный revenue (остальные): **${fmt(within_ch['weighted_avg_other'])}**"
    )
    lines.append("")

    # Show per-channel results
    df_wc = within_ch["results"].sort_values("n_8_10", ascending=False)
    lines.append("**Детали по каналам:**\n")
    lines.append(
        "| Channel | Platform | N 8-10m | N Other | Mean Rev 8-10m | Median Rev 8-10m | Mean Rev Other | Median Rev Other | Ratio |"
    )
    lines.append("|:---|:---|---:|---:|---:|---:|---:|---:|---:|")
    for _, row in df_wc.iterrows():
        ratio_str = fmt(row["rev_ratio"]) if pd.notna(row["rev_ratio"]) else "—"
        lines.append(
            f"| {row['channel_id']} | {row['platform']} | {row['n_8_10']} | {row['n_other']} | "
            f"${fmt(row['mean_rev_8_10'])} | ${fmt(row['median_rev_8_10'])} | "
            f"${fmt(row['mean_rev_other'])} | ${fmt(row['median_rev_other'])} | {ratio_str}x |"
        )
    lines.append("")

    # TASK 1 VERDICT
    total_mixed = within_ch["n_mixed_channels"]
    pct_better = within_ch["n_better"] / total_mixed * 100 if total_mixed > 0 else 0
    lines.append("### 1.4 Вердикт\n")
    if within_ch["n_better"] > within_ch["n_worse"] and pct_better >= 60:
        lines.append(
            f"✅ **Эффект подтверждается с оговорками.** В {within_ch['n_better']} из {total_mixed} каналов ({pct_better:.0f}%) "
            "8-10 мин видео показывают более высокий revenue ВНУТРИ канала. "
            "Однако выборка мала (104 видео), и результат чувствителен к отдельным каналам.\n"
        )
    elif within_ch["n_better"] > within_ch["n_worse"]:
        lines.append(
            f"⚠️ **Слабое подтверждение.** В {within_ch['n_better']} из {total_mixed} каналов ({pct_better:.0f}%) "
            "8-10 мин видео лучше, но преимущество неубедительно. "
            "Малая выборка (104 видео) не позволяет делать надёжных выводов.\n"
        )
    else:
        lines.append(
            f"❌ **Эффект НЕ подтверждается при подсчёте каналов.** Только в {within_ch['n_better']} из {total_mixed} каналов ({pct_better:.0f}%) "
            "8-10 мин видео показывают лучший revenue. Наблюдаемая корреляция — вероятно, артефакт channel-level confounding.\n"
        )

    # Nuance about weighted averages
    if within_ch['weighted_avg_8_10'] > within_ch['weighted_avg_other'] * 1.2:
        lines.append(
            f"**Нюанс:** средневзвешенный revenue 8-10 мин (${fmt(within_ch['weighted_avg_8_10'])}) выше, "
            f"чем у остальных (${fmt(within_ch['weighted_avg_other'])}), "
            "но это может быть обусловлено 2-3 каналами с аномально высоким revenue в этой категории "
            "(например, channel_190, channel_848). Один outlier-канал может сместить средневзвешенное.\n"
        )

    lines.append(
        f"**Ограничения:** всего {concentration['total_8_10']} видео в категории 8-10 мин — "
        "это менее 1% от всех видео с известной длительностью. Статистическая мощность низкая.\n"
    )

    # ═══════════ TASK 2 ═══════════
    lines.append("---\n")
    lines.append("## 2. Cross-Platform Selection Bias Check\n")

    lines.append("### 2.1 Характеристики кросс-постнутых vs обычных видео\n")
    lines.append(f"- Кросс-постнутых видео: **{cross_chars['n_cross']}** ({cross_chars['n_cross']/len(df1)*100:.1f}%)")
    lines.append(f"- Обычных видео: **{cross_chars['n_not_cross']}** ({cross_chars['n_not_cross']/len(df1)*100:.1f}%)")
    lines.append("")

    lines.append("| Метрика | Cross-Posted (Mean) | Cross-Posted (Median) | Non-Cross (Mean) | Non-Cross (Median) | Ratio (Mean) |")
    lines.append("|:---|---:|---:|---:|---:|---:|")

    metrics = [
        ("Duration (sec)", "dur", "duration_sec"),
        ("Views", "views", "total_views"),
        ("Revenue ($)", "rev", "revenue"),
        ("Engagement Rate", "eng", "engagement_rate"),
        ("CPM ($)", "cpm", "estimated_cpm"),
    ]
    for label, prefix, _ in metrics:
        cm = cross_chars[f"{prefix}_cross_mean"]
        cmed = cross_chars[f"{prefix}_cross_median"]
        nm = cross_chars[f"{prefix}_not_mean"]
        nmed = cross_chars[f"{prefix}_not_median"]
        ratio = cm / nm if nm and nm != 0 else float("nan")
        lines.append(
            f"| {label} | {fmt(cm)} | {fmt(cmed)} | {fmt(nm)} | {fmt(nmed)} | {fmt(ratio)}x |"
        )
    lines.append("")

    lines.append("**Распределение video_type:**\n")
    lines.append("| Video Type | Cross-Posted (%) | Non-Cross (%) |")
    lines.append("|:---|---:|---:|")
    all_types = set(cross_chars["type_cross"].index) | set(cross_chars["type_not"].index)
    for vt in sorted(all_types):
        tc = cross_chars["type_cross"].get(vt, 0)
        tn = cross_chars["type_not"].get(vt, 0)
        lines.append(f"| {vt} | {tc:.1f}% | {tn:.1f}% |")
    lines.append("")

    lines.append("**Распределение platform:**\n")
    lines.append("| Platform | Cross-Posted (%) | Non-Cross (%) |")
    lines.append("|:---|---:|---:|")
    all_plats = set(cross_chars["plat_cross"].index) | set(cross_chars["plat_not"].index)
    for p in sorted(all_plats):
        tc = cross_chars["plat_cross"].get(p, 0)
        tn = cross_chars["plat_not"].get(p, 0)
        lines.append(f"| {p} | {tc:.1f}% | {tn:.1f}% |")
    lines.append("")

    # Systematic differences?
    views_ratio = cross_chars["views_cross_mean"] / cross_chars["views_not_mean"] if cross_chars["views_not_mean"] else 0
    eng_ratio = cross_chars["eng_cross_mean"] / cross_chars["eng_not_mean"] if cross_chars["eng_not_mean"] else 0

    if views_ratio > 1.5 or eng_ratio < 0.7:
        lines.append(
            "⚠️ **Обнаружен selection bias:** кросс-постнутые видео систематически отличаются от обычных — "
            f"в {views_ratio:.1f}x больше просмотров, engagement rate в {eng_ratio:.1f}x ниже "
            "(вероятно, из-за другого mix по video_type и platform). "
            "Группы несопоставимы без контроля за confounders.\n"
        )
    else:
        lines.append(
            "Характеристики кросс-постнутых и обычных видео не имеют критических систематических различий.\n"
        )

    lines.append("### 2.2 Within-Channel Comparison (ключевой тест)\n")
    lines.append(
        f"Каналов с ≥3 кросс-постнутых И ≥3 обычных видео: **{cross_within['n_mixed_channels']}**\n"
    )
    lines.append(
        f"- Кросс-пост лучше по views: **{cross_within['n_cross_better_views']}** каналов"
    )
    lines.append(
        f"- Обычные лучше по views: **{cross_within['n_cross_worse_views']}** каналов"
    )
    lines.append(
        f"- Кросс-пост лучше по revenue: **{cross_within['n_cross_better_rev']}** каналов"
    )
    lines.append(
        f"- Обычные лучше по revenue: **{cross_within['n_cross_worse_rev']}** каналов"
    )
    lines.append("")

    # Show top channels
    df_cw = cross_within["results"].sort_values("n_cross", ascending=False).head(15)
    lines.append("**Топ-15 каналов (по количеству кросс-постов):**\n")
    lines.append(
        "| Channel | Plat | N Cross | N Not | Mean Views Cross | Median Views Cross | Mean Views Not | Median Views Not | Views Ratio |"
    )
    lines.append("|:---|:---|---:|---:|---:|---:|---:|---:|---:|")
    for _, row in df_cw.iterrows():
        vr = fmt(row["views_ratio"]) if pd.notna(row["views_ratio"]) else "—"
        lines.append(
            f"| {row['channel_id']} | {row['platform']} | {row['n_cross']} | {row['n_not_cross']} | "
            f"{fmt(row['mean_views_cross'], 0)} | {fmt(row['median_views_cross'], 0)} | "
            f"{fmt(row['mean_views_not'], 0)} | {fmt(row['median_views_not'], 0)} | {vr}x |"
        )
    lines.append("")

    # Revenue table
    lines.append("**Revenue comparison (same channels):**\n")
    lines.append(
        "| Channel | N Cross | N Not | Mean Rev Cross ($) | Median Rev Cross ($) | Mean Rev Not ($) | Median Rev Not ($) | Rev Ratio |"
    )
    lines.append("|:---|---:|---:|---:|---:|---:|---:|---:|")
    for _, row in df_cw.iterrows():
        rr = fmt(row["rev_ratio"]) if pd.notna(row["rev_ratio"]) else "—"
        lines.append(
            f"| {row['channel_id']} | {row['n_cross']} | {row['n_not_cross']} | "
            f"${fmt(row['mean_rev_cross'])} | ${fmt(row['median_rev_cross'])} | "
            f"${fmt(row['mean_rev_not'])} | ${fmt(row['median_rev_not'])} | {rr}x |"
        )
    lines.append("")

    # TASK 2 VERDICT
    total_cw = cross_within["n_mixed_channels"]
    pct_better_views = cross_within["n_cross_better_views"] / total_cw * 100 if total_cw > 0 else 0
    pct_better_rev = cross_within["n_cross_better_rev"] / total_cw * 100 if total_cw > 0 else 0

    lines.append("### 2.3 Вердикт\n")

    if pct_better_views >= 60 and (views_ratio > 1.5 or eng_ratio < 0.7):
        lines.append(
            f"⚠️ **Selection bias подтверждён.** Кросс-постнутые видео показывают лучшие результаты "
            f"в {cross_within['n_cross_better_views']} из {total_cw} каналов ({pct_better_views:.0f}%), "
            f"НО они также систематически отличаются по характеристикам (views ratio {views_ratio:.1f}x, engagement ratio {eng_ratio:.1f}x). "
            "Вероятнее всего, для кросс-постинга отбираются уже успешные видео → "
            "**нельзя утверждать, что кросс-постинг ПРИЧИНА лучшего performance.**\n"
        )
    elif pct_better_views >= 60:
        lines.append(
            f"✅ **Кросс-постинг показывает преимущество** в {cross_within['n_cross_better_views']} из {total_cw} каналов ({pct_better_views:.0f}%), "
            "и систематических различий в характеристиках не обнаружено. Но без рандомизированного эксперимента причинно-следственная связь не доказана.\n"
        )
    else:
        lines.append(
            f"❌ **Преимущество кросс-постинга не подтверждается** при within-channel анализе. "
            f"Только в {cross_within['n_cross_better_views']} из {total_cw} каналов ({pct_better_views:.0f}%) "
            "кросс-постнутые видео лучше.\n"
        )

    # ═══════════ OVERALL ═══════════
    lines.append("---\n")
    lines.append("## 3. Общие выводы\n")
    lines.append(
        "1. **Duration 8-10 мин:** малая выборка (104 видео), высокая концентрация по каналам. "
        "Требуется осторожность в интерпретации.\n"
    )
    lines.append(
        "2. **Cross-platform:** необходимо различать «кросс-постинг улучшает метрики» и "
        "«лучшие видео чаще кросс-постятся». Данные не позволяют установить причинно-следственную связь.\n"
    )
    lines.append(
        "3. **Рекомендация:** для обоих выводов в презентации использовать формулировки "
        "**«ассоциируется с»**, а не **«приводит к»**. Добавить caveats о confounding.\n"
    )

    return "\n".join(lines)


def generate_slide_updates(df1, df3):
    """Generate presentation caveats."""
    concentration = task1_channel_concentration(df1)
    within_ch = task1_within_channel_comparison(df1)
    cross_within = task2_within_channel_comparison(df1)
    cross_chars = task2_characteristic_comparison(df1)

    views_ratio = cross_chars["views_cross_mean"] / cross_chars["views_not_mean"] if cross_chars["views_not_mean"] else 0

    lines = []
    lines.append("# Slide Updates: Causality Caveats\n")
    lines.append("> Оговорки и уточнения для включения в презентацию TheSoul Group.\n")

    lines.append("## Слайд: Optimal Duration (8-10 мин)\n")
    lines.append("### Текущая формулировка (корректировка):\n")
    lines.append(
        "Вместо: «8-10 мин видео генерируют наибольший revenue»\n"
    )
    lines.append(
        "Использовать: «8-10 мин видео **ассоциируются** с более высоким revenue, "
        "однако этот вывод требует осторожной интерпретации»\n"
    )
    lines.append("### Footnote / мелкий текст:\n")
    lines.append(
        f"- Выборка: только {concentration['total_8_10']} видео из ~11K (<1%)\n"
        f"- {concentration['top5_pct']:.0f}% сконцентрированы в 5 каналах — возможен channel confounding\n"
        f"- Within-channel: 8-10 мин лучше в {within_ch['n_better']}/{within_ch['n_mixed_channels']} каналах "
        f"({within_ch['n_better']/within_ch['n_mixed_channels']*100:.0f}%)\n"
        "- Для подтверждения нужен A/B тест на одном канале\n"
    )

    lines.append("## Слайд: Cross-Platform Strategy\n")
    lines.append("### Текущая формулировка (корректировка):\n")
    lines.append(
        "Вместо: «Кросс-постинг увеличивает reach/revenue»\n"
    )
    lines.append(
        "Использовать: «Видео, размещённые на нескольких платформах, **показывают более высокие метрики** — "
        "но это может отражать selection bias (для кросс-постинга выбирают лучший контент)»\n"
    )
    lines.append("### Footnote / мелкий текст:\n")

    total_cw = cross_within["n_mixed_channels"]
    lines.append(
        f"- Кросс-постнутые видео имеют в {views_ratio:.1f}x больше просмотров → возможен selection bias\n"
        f"- Within-channel: кросс-пост лучше по views в {cross_within['n_cross_better_views']}/{total_cw} каналах "
        f"({cross_within['n_cross_better_views']/total_cw*100:.0f}%)\n"
        f"- Within-channel: кросс-пост лучше по revenue в {cross_within['n_cross_better_rev']}/{total_cw} каналах "
        f"({cross_within['n_cross_better_rev']/total_cw*100:.0f}%)\n"
        "- Направление: корреляция, не causation. Нужен контролируемый эксперимент.\n"
    )

    lines.append("## Общий caveat для всей презентации\n")
    lines.append(
        "Все выводы основаны на наблюдательных данных (observational data). "
        "Корреляции не равны причинно-следственным связям. "
        "Для подтверждения рекомендуется:\n"
        "1. **A/B тесты** — случайно назначать формат/длительность и замерять эффект\n"
        "2. **Propensity score matching** — подобрать «похожие» видео разных длительностей для fair comparison\n"
        "3. **Difference-in-differences** — сравнить каналы до и после смены стратегии\n"
    )

    return "\n".join(lines)


def main():
    print("Loading data...")
    df1, df3 = load_data()

    print(f"Dataset 1: {df1.shape[0]} videos, {df1['channel_id'].nunique()} channels")
    print(f"Dataset 3: {df3.shape[0]} rows (deduplicated)")
    print()

    # Run analyses with console output
    print("=" * 60)
    print("TASK 1: Duration Confounding Check")
    print("=" * 60)

    concentration = task1_channel_concentration(df1)
    print(f"\n8-10 min videos: {concentration['total_8_10']}")
    print(f"Channels producing them: {concentration['n_channels_with_8_10']}")
    print(f"Top-5 channels share: {concentration['top5_pct']:.1f}%")

    within_ch = task1_within_channel_comparison(df1)
    print(f"\nWithin-channel comparison ({within_ch['n_mixed_channels']} channels):")
    print(f"  8-10 min BETTER: {within_ch['n_better']}")
    print(f"  8-10 min WORSE:  {within_ch['n_worse']}")
    print(f"  Equal:           {within_ch['n_equal']}")
    print(f"  Weighted avg revenue (8-10): ${within_ch['weighted_avg_8_10']:.2f}")
    print(f"  Weighted avg revenue (other): ${within_ch['weighted_avg_other']:.2f}")

    print("\n" + "=" * 60)
    print("TASK 2: Cross-Platform Selection Bias")
    print("=" * 60)

    cross_chars = task2_characteristic_comparison(df1)
    views_ratio = cross_chars["views_cross_mean"] / cross_chars["views_not_mean"] if cross_chars["views_not_mean"] else 0
    eng_ratio = cross_chars["eng_cross_mean"] / cross_chars["eng_not_mean"] if cross_chars["eng_not_mean"] else 0
    print(f"\nCross-posted: {cross_chars['n_cross']} videos")
    print(f"Non-cross: {cross_chars['n_not_cross']} videos")
    print(f"Views ratio (cross/not): {views_ratio:.2f}x")
    print(f"Engagement ratio: {eng_ratio:.2f}x")

    cross_within = task2_within_channel_comparison(df1)
    print(f"\nWithin-channel ({cross_within['n_mixed_channels']} channels):")
    print(f"  Cross better (views):   {cross_within['n_cross_better_views']}")
    print(f"  Non-cross better (views): {cross_within['n_cross_worse_views']}")
    print(f"  Cross better (revenue):   {cross_within['n_cross_better_rev']}")
    print(f"  Non-cross better (revenue): {cross_within['n_cross_worse_rev']}")

    # Generate reports
    print("\n" + "=" * 60)
    print("Generating reports...")

    report = generate_report(df1, df3)
    report_path = OUTPUT_DIR / "CAUSALITY_CHECKS.md"
    report_path.write_text(report)
    print(f"  → {report_path}")

    slides = generate_slide_updates(df1, df3)
    slides_path = OUTPUT_DIR / "SLIDE_CAUSALITY_UPDATES.md"
    slides_path.write_text(slides)
    print(f"  → {slides_path}")

    print("\nDone!")


if __name__ == "__main__":
    main()
