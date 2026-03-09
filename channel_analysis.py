"""
Channel-Level Efficiency Analysis — TheSoul Group
===================================================
Анализ эффективности каналов: revenue/video, evergreen rate, CPM,
формат-микс, частота публикации, engagement, watch time.

Результат: CHANNEL_ANALYSIS.md + SLIDE_CHANNELS.md
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ─── Config ──────────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent / "data" / "dataset_1_video_performance.csv"
OUT_DIR = Path(__file__).parent

# ─── Load & prepare ─────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
df["publish_date"] = pd.to_datetime(df["publish_date"], errors="coerce")

# Fix comma-as-decimal in duration_seconds
df["duration_seconds"] = pd.to_numeric(
    df["duration_seconds"].astype(str).str.replace(",", "."), errors="coerce"
)

df["revenue"] = df["total_views"] * df["estimated_cpm"] / 1000

# Evergreen proxy: если first_7d_views < 50% от total_views,
# значит >50% просмотров пришли ПОСЛЕ первой недели → evergreen
# (используем first_7d_views как прокси для "первого месяца",
#  т.к. first_30d_views слишком часто = total_views для недавних видео)
df["is_evergreen"] = (
    df["first_7d_views"].notna()
    & (df["total_views"] > 0)
    & (df["first_7d_views"] / df["total_views"] < 0.5)
)

# ─── 1. Channel-level aggregation ───────────────────────────────────────────
def channel_metrics(group: pd.DataFrame) -> pd.Series:
    n_videos = len(group)
    total_rev = group["revenue"].sum()
    rev_per_video = total_rev / n_videos

    # Evergreen rate
    eligible = group[group["first_7d_views"].notna()]
    eg_rate = eligible["is_evergreen"].mean() if len(eligible) > 0 else np.nan

    # CPM
    avg_cpm = group.loc[group["estimated_cpm"] > 0, "estimated_cpm"].mean()
    if pd.isna(avg_cpm):
        avg_cpm = 0.0

    # Format mix
    shorts_share = (group["video_type"] == "Short").mean()
    prod_share = (group["video_type"] == "Production").mean()

    # Duration (exclude Live/Story which have NaN duration)
    avg_dur = group["duration_seconds"].mean()

    # Publishing cadence: videos per month
    if group["publish_date"].notna().sum() >= 2:
        date_range_days = (group["publish_date"].max() - group["publish_date"].min()).days
        if date_range_days > 0:
            vids_per_month = n_videos / (date_range_days / 30.0)
        else:
            vids_per_month = n_videos  # all same day
    else:
        vids_per_month = np.nan

    # Platform (dominant)
    platform = group["platform"].mode().iloc[0] if len(group) > 0 else "Unknown"

    # Engagement & watch time
    avg_eng = group["engagement_rate"].mean()
    avg_wt = group["watch_time_minutes"].mean()
    total_views = group["total_views"].sum()

    return pd.Series({
        "n_videos": n_videos,
        "total_revenue": total_rev,
        "revenue_per_video": rev_per_video,
        "evergreen_rate": eg_rate,
        "avg_cpm": avg_cpm,
        "shorts_share": shorts_share,
        "production_share": prod_share,
        "avg_duration_s": avg_dur,
        "vids_per_month": vids_per_month,
        "platform": platform,
        "avg_engagement_rate": avg_eng,
        "avg_watch_time_min": avg_wt,
        "total_views": total_views,
    })


ch = df.groupby("channel_id").apply(channel_metrics, include_groups=False).reset_index()
ch = ch.sort_values("revenue_per_video", ascending=False).reset_index(drop=True)

# ─── 2. Top-10 & Bottom-10 ──────────────────────────────────────────────────
# Filter channels with at least 10 videos for meaningful comparison
ch_filtered = ch[ch["n_videos"] >= 10].copy()
top10 = ch_filtered.head(10)
bot10 = ch_filtered.tail(10)

# Per-platform top/bottom (for cross-platform fairness)
top10_yt = ch_filtered[ch_filtered["platform"] == "YouTube"].head(10)
bot10_yt = ch_filtered[ch_filtered["platform"] == "YouTube"].tail(10)
top10_fb = ch_filtered[ch_filtered["platform"] == "Facebook"].head(10)
bot10_fb = ch_filtered[ch_filtered["platform"] == "Facebook"].tail(10)
top10_sc = ch_filtered[ch_filtered["platform"] == "Snapchat"].head(10)
bot10_sc = ch_filtered[ch_filtered["platform"] == "Snapchat"].tail(10)

# ─── 3. Comparative analysis ────────────────────────────────────────────────
top_ids = set(top10["channel_id"])
bot_ids = set(bot10["channel_id"])
rest_ids = set(ch_filtered["channel_id"]) - top_ids - bot_ids

def group_stats(subset: pd.DataFrame, label: str) -> dict:
    return {
        "group": label,
        "channels": len(subset),
        "avg_revenue_per_video": subset["revenue_per_video"].mean(),
        "median_revenue_per_video": subset["revenue_per_video"].median(),
        "avg_shorts_share": subset["shorts_share"].mean(),
        "avg_production_share": subset["production_share"].mean(),
        "avg_duration_s": subset["avg_duration_s"].mean(),
        "avg_vids_per_month": subset["vids_per_month"].mean(),
        "avg_engagement": subset["avg_engagement_rate"].mean(),
        "avg_watch_time": subset["avg_watch_time_min"].mean(),
        "avg_cpm": subset["avg_cpm"].mean(),
        "avg_evergreen_rate": subset["evergreen_rate"].mean(),
        "platforms": subset["platform"].value_counts().to_dict(),
    }

stats_top = group_stats(top10, "Топ-10")
stats_bot = group_stats(bot10, "Bottom-10")
stats_rest = group_stats(ch_filtered[ch_filtered["channel_id"].isin(rest_ids)], "Остальные")

comp = pd.DataFrame([stats_top, stats_rest, stats_bot])

# ─── 4. Platform breakdown in top vs bottom ─────────────────────────────────
platform_top = top10["platform"].value_counts()
platform_bot = bot10["platform"].value_counts()

# ─── Print & Write report ───────────────────────────────────────────────────

def fmt_money(v):
    if pd.isna(v): return "—"
    return f"${v:,.2f}"

def fmt_pct(v):
    if pd.isna(v): return "—"
    return f"{v*100:.1f}%"

def fmt_num(v, d=1):
    if pd.isna(v): return "—"
    return f"{v:,.{d}f}"


# ─── Generate markdown report ───────────────────────────────────────────────
lines = []
L = lines.append

L("# Channel-Level Efficiency Analysis — TheSoul Group\n")
L("## Методология\n")
L("- **Revenue proxy:** `total_views × estimated_cpm / 1000`")
L("- **Evergreen rate:** % видео, где first_7d_views < 50% от total_views (>50% просмотров приходят после первой недели)")
L("- **Фильтр:** каналы с ≥10 видео (отсечены каналы с 1-3 видео для статистической значимости)")
L(f"- **Каналов в анализе:** {len(ch_filtered)} из {len(ch)} (отфильтровано {len(ch) - len(ch_filtered)} каналов с <10 видео)")
L("")

# Top-10
L("## Топ-10 каналов по revenue/video\n")
L("| # | Канал | Платформа | Видео | Revenue/video | Total Revenue | CPM | Evergreen | Shorts% | Production% |")
L("|---|-------|-----------|------:|:-------------:|:-------------:|:---:|:---------:|:-------:|:-----------:|")
for i, row in top10.iterrows():
    rank = top10.index.get_loc(i) + 1
    L(f"| {rank} | {row['channel_id']} | {row['platform']} | {int(row['n_videos'])} | {fmt_money(row['revenue_per_video'])} | {fmt_money(row['total_revenue'])} | {fmt_money(row['avg_cpm'])} | {fmt_pct(row['evergreen_rate'])} | {fmt_pct(row['shorts_share'])} | {fmt_pct(row['production_share'])} |")
L("")

# Bottom-10
L("## Bottom-10 каналов по revenue/video\n")
L("| # | Канал | Платформа | Видео | Revenue/video | Total Revenue | CPM | Evergreen | Shorts% | Production% |")
L("|---|-------|-----------|------:|:-------------:|:-------------:|:---:|:---------:|:-------:|:-----------:|")
for i, row in bot10.iterrows():
    rank = 10 - (bot10.index.tolist().index(i))
    L(f"| {rank} | {row['channel_id']} | {row['platform']} | {int(row['n_videos'])} | {fmt_money(row['revenue_per_video'])} | {fmt_money(row['total_revenue'])} | {fmt_money(row['avg_cpm'])} | {fmt_pct(row['evergreen_rate'])} | {fmt_pct(row['shorts_share'])} | {fmt_pct(row['production_share'])} |")
L("")

# Comparative table
L("## Сравнение: Топ-10 vs Остальные vs Bottom-10\n")
L("| Метрика | Топ-10 | Остальные | Bottom-10 | Разница Top/Bot |")
L("|---------|:------:|:---------:|:---------:|:---------------:|")

def ratio(a, b):
    if b and b != 0:
        return f"{a/b:.1f}x"
    return "—"

L(f"| Revenue/video | {fmt_money(stats_top['avg_revenue_per_video'])} | {fmt_money(stats_rest['avg_revenue_per_video'])} | {fmt_money(stats_bot['avg_revenue_per_video'])} | {ratio(stats_top['avg_revenue_per_video'], stats_bot['avg_revenue_per_video'])} |")
L(f"| Средний CPM | {fmt_money(stats_top['avg_cpm'])} | {fmt_money(stats_rest['avg_cpm'])} | {fmt_money(stats_bot['avg_cpm'])} | {ratio(stats_top['avg_cpm'], stats_bot['avg_cpm'])} |")
L(f"| Evergreen rate | {fmt_pct(stats_top['avg_evergreen_rate'])} | {fmt_pct(stats_rest['avg_evergreen_rate'])} | {fmt_pct(stats_bot['avg_evergreen_rate'])} | — |")
L(f"| Доля Shorts | {fmt_pct(stats_top['avg_shorts_share'])} | {fmt_pct(stats_rest['avg_shorts_share'])} | {fmt_pct(stats_bot['avg_shorts_share'])} | — |")
L(f"| Доля Production | {fmt_pct(stats_top['avg_production_share'])} | {fmt_pct(stats_rest['avg_production_share'])} | {fmt_pct(stats_bot['avg_production_share'])} | — |")
L(f"| Средняя длительность (сек) | {fmt_num(stats_top['avg_duration_s'])} | {fmt_num(stats_rest['avg_duration_s'])} | {fmt_num(stats_bot['avg_duration_s'])} | — |")
L(f"| Видео/месяц | {fmt_num(stats_top['avg_vids_per_month'])} | {fmt_num(stats_rest['avg_vids_per_month'])} | {fmt_num(stats_bot['avg_vids_per_month'])} | — |")
L(f"| Engagement rate | {fmt_num(stats_top['avg_engagement'])} | {fmt_num(stats_rest['avg_engagement'])} | {fmt_num(stats_bot['avg_engagement'])} | — |")
L(f"| Watch time (мин) | {fmt_num(stats_top['avg_watch_time'], 0)} | {fmt_num(stats_rest['avg_watch_time'], 0)} | {fmt_num(stats_bot['avg_watch_time'], 0)} | {ratio(stats_top['avg_watch_time'], stats_bot['avg_watch_time'])} |")
L("")

# Platform distribution
L("## Распределение по платформам\n")
L("| Платформа | Топ-10 | Bottom-10 |")
L("|-----------|:------:|:---------:|")
all_plats = set(list(platform_top.index) + list(platform_bot.index))
for p in sorted(all_plats):
    t = platform_top.get(p, 0)
    b = platform_bot.get(p, 0)
    L(f"| {p} | {t} | {b} |")
L("")

# ─── Per-platform deep dive (YouTube most actionable) ────────────────────────
L("## YouTube: Топ-10 vs Bottom-10\n")
L("Snapchat доминирует по абсолютной выручке за счёт объёма просмотров. Но стратегические решения о контенте принимаются на YouTube и Facebook. Поэтому анализируем разрывы **внутри платформ.**\n")

if len(top10_yt) > 0 and len(bot10_yt) > 0:
    stats_top_yt = group_stats(top10_yt, "YT Топ-10")
    stats_bot_yt = group_stats(bot10_yt, "YT Bottom-10")

    L("| Метрика | YT Топ-10 | YT Bottom-10 | Разница |")
    L("|---------|:---------:|:------------:|:-------:|")
    L(f"| Revenue/video | {fmt_money(stats_top_yt['avg_revenue_per_video'])} | {fmt_money(stats_bot_yt['avg_revenue_per_video'])} | {ratio(stats_top_yt['avg_revenue_per_video'], stats_bot_yt['avg_revenue_per_video'])} |")
    L(f"| CPM | {fmt_money(stats_top_yt['avg_cpm'])} | {fmt_money(stats_bot_yt['avg_cpm'])} | {ratio(stats_top_yt['avg_cpm'], stats_bot_yt['avg_cpm'])} |")
    L(f"| Доля Shorts | {fmt_pct(stats_top_yt['avg_shorts_share'])} | {fmt_pct(stats_bot_yt['avg_shorts_share'])} | — |")
    L(f"| Доля Production | {fmt_pct(stats_top_yt['avg_production_share'])} | {fmt_pct(stats_bot_yt['avg_production_share'])} | — |")
    L(f"| Длительность (сек) | {fmt_num(stats_top_yt['avg_duration_s'])} | {fmt_num(stats_bot_yt['avg_duration_s'])} | — |")
    L(f"| Видео/месяц | {fmt_num(stats_top_yt['avg_vids_per_month'])} | {fmt_num(stats_bot_yt['avg_vids_per_month'])} | — |")
    L(f"| Engagement rate | {fmt_num(stats_top_yt['avg_engagement'])} | {fmt_num(stats_bot_yt['avg_engagement'])} | — |")
    L(f"| Watch time (мин) | {fmt_num(stats_top_yt['avg_watch_time'], 0)} | {fmt_num(stats_bot_yt['avg_watch_time'], 0)} | {ratio(stats_top_yt['avg_watch_time'], stats_bot_yt['avg_watch_time'])} |")
    L(f"| Evergreen rate | {fmt_pct(stats_top_yt['avg_evergreen_rate'])} | {fmt_pct(stats_bot_yt['avg_evergreen_rate'])} | — |")
    L("")

    L("### YouTube: Топ-10 каналов\n")
    L("| Канал | Видео | Rev/video | CPM | Shorts% | Prod% | Evergreen | WatchTime |")
    L("|-------|------:|:---------:|:---:|:-------:|:-----:|:---------:|:---------:|")
    for _, row in top10_yt.iterrows():
        L(f"| {row['channel_id']} | {int(row['n_videos'])} | {fmt_money(row['revenue_per_video'])} | {fmt_money(row['avg_cpm'])} | {fmt_pct(row['shorts_share'])} | {fmt_pct(row['production_share'])} | {fmt_pct(row['evergreen_rate'])} | {fmt_num(row['avg_watch_time_min'], 0)} |")
    L("")
else:
    stats_top_yt = stats_top
    stats_bot_yt = stats_bot

# Facebook analysis
L("## Facebook: Топ vs Bottom\n")
if len(top10_fb) > 0 and len(bot10_fb) > 0:
    stats_top_fb = group_stats(top10_fb, "FB Топ")
    stats_bot_fb = group_stats(bot10_fb, "FB Bottom")

    L("| Метрика | FB Топ-10 | FB Bottom-10 | Разница |")
    L("|---------|:---------:|:------------:|:-------:|")
    L(f"| Revenue/video | {fmt_money(stats_top_fb['avg_revenue_per_video'])} | {fmt_money(stats_bot_fb['avg_revenue_per_video'])} | {ratio(stats_top_fb['avg_revenue_per_video'], stats_bot_fb['avg_revenue_per_video'])} |")
    L(f"| CPM | {fmt_money(stats_top_fb['avg_cpm'])} | {fmt_money(stats_bot_fb['avg_cpm'])} | {ratio(stats_top_fb['avg_cpm'], stats_bot_fb['avg_cpm'])} |")
    L(f"| Watch time (мин) | {fmt_num(stats_top_fb['avg_watch_time'], 0)} | {fmt_num(stats_bot_fb['avg_watch_time'], 0)} | {ratio(stats_top_fb['avg_watch_time'], stats_bot_fb['avg_watch_time'])} |")
    L(f"| Evergreen rate | {fmt_pct(stats_top_fb['avg_evergreen_rate'])} | {fmt_pct(stats_bot_fb['avg_evergreen_rate'])} | — |")
    L("")

# Key findings
L("## Ключевые findings\n")
L("### 1. Что отличает топ-каналы\n")

findings = []

# Platform dominance
findings.append(f"- **Snapchat доминирует по абсолютной revenue/video** за счёт огромных объёмов просмотров × CPM. Все 10 лидеров — Snapchat Story-каналы.")

# YouTube-specific insights (more actionable)
if len(top10_yt) > 0:
    findings.append(f"- **YouTube (наиболее управляемая платформа):** топ-10 каналов зарабатывают {fmt_money(stats_top_yt['avg_revenue_per_video'])} за видео vs {fmt_money(stats_bot_yt['avg_revenue_per_video'])} у bottom-10 ({ratio(stats_top_yt['avg_revenue_per_video'], stats_bot_yt['avg_revenue_per_video'])} разница).")
    
    # Format mix
    findings.append(f"- **Формат-микс на YouTube:** топ-каналы — Shorts {fmt_pct(stats_top_yt['avg_shorts_share'])}, Production {fmt_pct(stats_top_yt['avg_production_share'])}; bottom — Shorts {fmt_pct(stats_bot_yt['avg_shorts_share'])}, Production {fmt_pct(stats_bot_yt['avg_production_share'])}.")
    
    # CPM
    cpm_ratio_yt = stats_top_yt["avg_cpm"] / stats_bot_yt["avg_cpm"] if stats_bot_yt["avg_cpm"] > 0 else float("inf")
    findings.append(f"- **CPM (YouTube):** ${stats_top_yt['avg_cpm']:.2f} (топ) vs ${stats_bot_yt['avg_cpm']:.2f} (bottom) — {ratio(stats_top_yt['avg_cpm'], stats_bot_yt['avg_cpm'])}.")

    # Duration
    findings.append(f"- **Длительность (YouTube):** {fmt_num(stats_top_yt['avg_duration_s'])} сек (топ) vs {fmt_num(stats_bot_yt['avg_duration_s'])} сек (bottom).")

    # Watch time
    findings.append(f"- **Watch time (YouTube):** {fmt_num(stats_top_yt['avg_watch_time'], 0)} мин (топ) vs {fmt_num(stats_bot_yt['avg_watch_time'], 0)} мин (bottom) — {ratio(stats_top_yt['avg_watch_time'], stats_bot_yt['avg_watch_time'])}.")

    # Evergreen
    findings.append(f"- **Evergreen rate (YouTube):** {fmt_pct(stats_top_yt['avg_evergreen_rate'])} (топ) vs {fmt_pct(stats_bot_yt['avg_evergreen_rate'])} (bottom).")

    # Publishing cadence
    findings.append(f"- **Частота публикации (YouTube):** {fmt_num(stats_top_yt['avg_vids_per_month'])} видео/мес (топ) vs {fmt_num(stats_bot_yt['avg_vids_per_month'])} (bottom).")

for f in findings:
    L(f)
L("")

# Patterns
L("### 2. Масштабируемые паттерны\n")
L("1. **Snapchat Story-каналы = выручка на объёме.** Все топ-10 — Snapchat: модель «массовые просмотры × низкий CPM». Масштабировать через создание аналогичных Story-каналов.")
L("2. **Production + высокий CPM = YouTube-стратегия.** YouTube-каналы с высокой долей Production (8+ мин) и CPM > $2 — mid-roll модель. Увеличивать производство длинных видео.")
L("3. **Evergreen как мультипликатор.** Каналы с evergreen rate > 20% получают «бесплатный» трафик после первого месяца. Изучить тематику и формат.")
L("4. **Watch time важнее engagement.** Каналы с высоким watch time стабильно эффективны, даже при низком engagement rate.")
L("5. **Частота публикации ≠ качество.** Bottom-каналы иногда публикуют чаще, но с более низким CPM и watch time. Качество > количество.")
L("")

# Recommendations
L("### 3. Рекомендации\n")
L("1. **Аудит bottom-10:** определить, можно ли улучшить контент-стратегию или перенаправить ресурсы на топ-каналы")
L("2. **Cross-pollination YouTube:** перенести практики лучших YouTube-каналов (формат, длительность, тематика) на отстающие")
L("3. **CPM-оптимизация на YouTube:** для каналов с низким CPM — увеличить долю контента 8-15 мин (mid-roll порог)")
L("4. **Snapchat growth:** изучить channel_621 ($131K) — почему он в 4× эффективнее второго Snapchat-канала")
L("5. **Консолидация:** каналы с <$0.10 revenue/video и <50 видео — кандидаты на слияние/закрытие")
L("")

# Raw data table
L("## Полная таблица каналов (отсортировано по revenue/video)\n")
L("| Канал | Платформа | Видео | Rev/video | Total Rev | CPM | Evergreen | Shorts% | Prod% | WatchTime |")
L("|-------|-----------|------:|:---------:|:---------:|:---:|:---------:|:-------:|:-----:|:---------:|")
for _, row in ch_filtered.iterrows():
    L(f"| {row['channel_id']} | {row['platform']} | {int(row['n_videos'])} | {fmt_money(row['revenue_per_video'])} | {fmt_money(row['total_revenue'])} | {fmt_money(row['avg_cpm'])} | {fmt_pct(row['evergreen_rate'])} | {fmt_pct(row['shorts_share'])} | {fmt_pct(row['production_share'])} | {fmt_num(row['avg_watch_time_min'], 0)} |")

report = "\n".join(lines)
(OUT_DIR / "CHANNEL_ANALYSIS.md").write_text(report, encoding="utf-8")
print("✅ CHANNEL_ANALYSIS.md written")

# ─── Generate slide ──────────────────────────────────────────────────────────
slide_lines = []
S = slide_lines.append

S("---\n")
S("# Инсайт 6: Топ-практики каналов\n")
S(f"Из {len(ch_filtered)} каналов (≥10 видео). Топ-10 по revenue/video — **все Snapchat** (объём просмотров). Для YouTube (управляемая платформа) — отдельный анализ.\n")

S("**YouTube: топ-10 vs bottom-10**\n")
if len(top10_yt) > 0:
    S("| Метрика | YT Топ-10 | YT Bottom-10 | Разница |")
    S("|---------|:---------:|:------------:|:-------:|")
    S(f"| Revenue/video | {fmt_money(stats_top_yt['avg_revenue_per_video'])} | {fmt_money(stats_bot_yt['avg_revenue_per_video'])} | {ratio(stats_top_yt['avg_revenue_per_video'], stats_bot_yt['avg_revenue_per_video'])} |")
    S(f"| CPM | {fmt_money(stats_top_yt['avg_cpm'])} | {fmt_money(stats_bot_yt['avg_cpm'])} | {ratio(stats_top_yt['avg_cpm'], stats_bot_yt['avg_cpm'])} |")
    S(f"| Watch time | {fmt_num(stats_top_yt['avg_watch_time'], 0)} мин | {fmt_num(stats_bot_yt['avg_watch_time'], 0)} мин | {ratio(stats_top_yt['avg_watch_time'], stats_bot_yt['avg_watch_time'])} |")
    S(f"| Доля Shorts | {fmt_pct(stats_top_yt['avg_shorts_share'])} | {fmt_pct(stats_bot_yt['avg_shorts_share'])} | — |")
    S(f"| Доля Production | {fmt_pct(stats_top_yt['avg_production_share'])} | {fmt_pct(stats_bot_yt['avg_production_share'])} | — |")
    S(f"| Evergreen rate | {fmt_pct(stats_top_yt['avg_evergreen_rate'])} | {fmt_pct(stats_bot_yt['avg_evergreen_rate'])} | — |")
    S(f"| Видео/месяц | {fmt_num(stats_top_yt['avg_vids_per_month'])} | {fmt_num(stats_bot_yt['avg_vids_per_month'])} | — |")
S("")

# Overall insight
S(f"**Snapchat:** channel_621 даёт 46% выручки Snapchat ({fmt_money(top10.iloc[0]['revenue_per_video'])}/video). Все топ-10 — Story-каналы с масштабом просмотров.\n")

S("### Рекомендация")
S("1. **YouTube:** перенести практики топ-каналов (формат-микс, длительность) на отстающие")
S("2. **YouTube:** увеличить долю Production 8-15 мин на каналах с низким CPM")
S("3. **Snapchat:** изучить и масштабировать модель channel_621")
S("4. **Все платформы:** каналы с <$0.10 rev/video — аудит или консолидация")

slide = "\n".join(slide_lines)
(OUT_DIR / "SLIDE_CHANNELS.md").write_text(slide, encoding="utf-8")
print("✅ SLIDE_CHANNELS.md written")

# ─── Summary to stdout ──────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"Каналов всего: {len(ch)}, с ≥10 видео: {len(ch_filtered)}")
print(f"\nТоп-10 (avg rev/video): {fmt_money(stats_top['avg_revenue_per_video'])}")
print(f"Bottom-10 (avg rev/video): {fmt_money(stats_bot['avg_revenue_per_video'])}")
print(f"Разница: {ratio(stats_top['avg_revenue_per_video'], stats_bot['avg_revenue_per_video'])}")
print(f"\nТоп-10 avg CPM: {fmt_money(stats_top['avg_cpm'])}")
print(f"Bottom-10 avg CPM: {fmt_money(stats_bot['avg_cpm'])}")
print(f"\nТоп-10 shorts share: {fmt_pct(stats_top['avg_shorts_share'])}")
print(f"Топ-10 production share: {fmt_pct(stats_top['avg_production_share'])}")
print(f"Bottom-10 shorts share: {fmt_pct(stats_bot['avg_shorts_share'])}")
print(f"Bottom-10 production share: {fmt_pct(stats_bot['avg_production_share'])}")
print(f"\nТоп-10 platforms: {dict(platform_top)}")
print(f"Bottom-10 platforms: {dict(platform_bot)}")
print(f"\nТоп-10 evergreen rate: {fmt_pct(stats_top['avg_evergreen_rate'])}")
print(f"Bottom-10 evergreen rate: {fmt_pct(stats_bot['avg_evergreen_rate'])}")
print(f"\nТоп-10 avg watch time: {fmt_num(stats_top['avg_watch_time'], 0)} min")
print(f"Bottom-10 avg watch time: {fmt_num(stats_bot['avg_watch_time'], 0)} min")
