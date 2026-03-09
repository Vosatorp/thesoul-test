#!/usr/bin/env python3
"""
TheSoul Group — Presentation Figures (14 charts)
All labels in English. Unified style. Production-ready.
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from scipy import stats
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
DATA = Path("data")
FIG = Path("figures")
FIG.mkdir(exist_ok=True)

# ── Global Style ───────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "savefig.bbox": "tight",
    "savefig.dpi": 150,
    "savefig.pad_inches": 0.15,
})

PALETTE_3 = sns.color_palette("husl", 3)
PALETTE_4 = sns.color_palette("husl", 4)
PALETTE_5 = sns.color_palette("husl", 5)
PALETTE_8 = sns.color_palette("husl", 8)

PLATFORM_COLORS = {"YouTube": PALETTE_3[0], "Facebook": PALETTE_3[1], "Snapchat": PALETTE_3[2]}
TYPE_ORDER = ["Short", "Production", "Live", "Story"]
TYPE_COLORS = {t: c for t, c in zip(TYPE_ORDER, PALETTE_4)}

# ── Load Data ──────────────────────────────────────────────────────────────
print("Loading data...")
d1 = pd.read_csv(DATA / "dataset_1_video_performance.csv")
d2 = pd.read_csv(DATA / "dataset_2_cohort_analysis.csv")
d3 = pd.read_csv(DATA / "dataset_3_cross_platform.csv")

d1["duration_seconds"] = pd.to_numeric(d1["duration_seconds"], errors="coerce")
d1["revenue"] = d1["total_views"] * d1["estimated_cpm"] / 1000

print(f"  D1: {len(d1)} rows, D2: {len(d2)} rows, D3: {len(d3)} rows")

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FIG 01 — Revenue by Platform                                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝
print("Fig 01: Revenue by Platform...")
fig, ax = plt.subplots(figsize=(10, 6))
rev_plat = d1.groupby("platform")["revenue"].sum().reindex(["YouTube", "Facebook", "Snapchat"])
total_rev = rev_plat.sum()
bars = ax.bar(rev_plat.index, rev_plat.values,
              color=[PLATFORM_COLORS[p] for p in rev_plat.index],
              edgecolor="white", linewidth=1.5, width=0.6)

for bar, val in zip(bars, rev_plat.values):
    pct = val / total_rev * 100
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + total_rev * 0.01,
            f"${val:,.0f}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=12, fontweight="bold")

ax.set_ylabel("Revenue (proxy), $")
ax.set_title("Revenue by Platform — Snapchat Dominates (~91%)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.set_ylim(0, rev_plat.max() * 1.18)
ax.yaxis.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(FIG / "fig_01_revenue_by_platform.png")
plt.close()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FIG 02 — Format Mix by Platform                                       ║
# ╚══════════════════════════════════════════════════════════════════════════╝
print("Fig 02: Format Mix...")
fig, ax = plt.subplots(figsize=(10, 6))
ct = pd.crosstab(d1["platform"], d1["video_type"], normalize="index")
ct = ct.reindex(index=["YouTube", "Facebook", "Snapchat"], columns=TYPE_ORDER).fillna(0)

ct.plot(kind="bar", stacked=True, ax=ax,
        color=[TYPE_COLORS[t] for t in ct.columns],
        edgecolor="white", linewidth=0.5, width=0.6)

# Annotate segments
for i, platform in enumerate(ct.index):
    cum = 0
    for typ in ct.columns:
        val = ct.loc[platform, typ]
        if val > 0.03:
            ax.text(i, cum + val / 2, f"{val:.0%}",
                    ha="center", va="center", fontsize=10, fontweight="bold", color="white")
        cum += val

ax.set_ylabel("Share of Videos")
ax.set_title("Content Format Mix by Platform")
ax.set_xticklabels(ct.index, rotation=0)
ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
ax.legend(title="Video Type", loc="upper right", frameon=False)
plt.tight_layout()
fig.savefig(FIG / "fig_02_format_mix.png")
plt.close()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FIG 03 — CPM Box Plots by Video Type                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝
print("Fig 03: CPM Box Plots...")
fig, ax = plt.subplots(figsize=(10, 6))
# Remove outliers beyond 99th percentile for readability
p99 = d1["estimated_cpm"].quantile(0.99)
d1_cpm = d1[d1["estimated_cpm"] <= p99].copy()

bp = sns.boxplot(data=d1_cpm, x="video_type", y="estimated_cpm",
                 order=TYPE_ORDER, palette=TYPE_COLORS,
                 ax=ax, showfliers=False, width=0.5)

# Add median annotations
medians = d1_cpm.groupby("video_type")["estimated_cpm"].median()
for i, typ in enumerate(TYPE_ORDER):
    med = medians.get(typ, 0)
    ax.text(i, med + p99 * 0.02, f"${med:.2f}", ha="center", va="bottom",
            fontsize=11, fontweight="bold")

ax.set_ylabel("Estimated CPM ($)")
ax.set_xlabel("Video Type")
ax.set_title("CPM Distribution by Video Type (≤99th percentile)")
ax.yaxis.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(FIG / "fig_03_cpm_boxplots.png")
plt.close()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FIG 04 — Duration Histogram (log scale)                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝
print("Fig 04: Duration Histogram...")
fig, ax = plt.subplots(figsize=(12, 5))
d1_dur = d1.dropna(subset=["duration_seconds"])
d1_dur = d1_dur[d1_dur["duration_seconds"] > 0]

bins = np.logspace(np.log10(1), np.log10(d1_dur["duration_seconds"].max()), 50)

for vtype in TYPE_ORDER:
    sub = d1_dur[d1_dur["video_type"] == vtype]
    if len(sub) > 0:
        ax.hist(sub["duration_seconds"], bins=bins, alpha=0.6,
                label=vtype, color=TYPE_COLORS[vtype], edgecolor="white", linewidth=0.3)

ax.set_xscale("log")
ax.set_xlabel("Duration (seconds, log scale)")
ax.set_ylabel("Number of Videos")
ax.set_title("Video Duration Distribution by Type")
ax.legend(frameon=False)

# Annotate the 8-15 min gap
ax.axvspan(480, 900, alpha=0.1, color="red", zorder=0)
ax.annotate("8–15 min\n(<3% of content)",
            xy=(660, ax.get_ylim()[1] * 0.5), fontsize=11,
            ha="center", color="red", fontstyle="italic",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="red", alpha=0.8))

ax.xaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"{int(x)}s" if x < 60 else f"{int(x/60)}m"))
ax.yaxis.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(FIG / "fig_04_duration_histogram.png")
plt.close()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FIG 05 — Revenue per Hour of Content                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝
print("Fig 05: Revenue per Hour...")
fig, ax = plt.subplots(figsize=(10, 6))

# Calculate total content hours and revenue by video_type
for_rev = d1.dropna(subset=["duration_seconds"])
rev_hours = for_rev.groupby("video_type").agg(
    total_rev=("revenue", "sum"),
    total_duration_s=("duration_seconds", "sum")
).reset_index()
rev_hours["content_hours"] = rev_hours["total_duration_s"] / 3600
rev_hours["rev_per_hour"] = rev_hours["total_rev"] / rev_hours["content_hours"]

# Focus on Shorts vs Production
focus = rev_hours[rev_hours["video_type"].isin(["Short", "Production"])].set_index("video_type")
focus = focus.reindex(["Short", "Production"])

bars = ax.bar(focus.index, focus["rev_per_hour"],
              color=[TYPE_COLORS[t] for t in focus.index],
              edgecolor="white", linewidth=1.5, width=0.5)

for bar, val in zip(bars, focus["rev_per_hour"]):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
            f"${val:.0f}/hr", ha="center", va="bottom", fontsize=14, fontweight="bold")

ax.set_ylabel("Revenue per Hour of Content ($)")
ax.set_title("Revenue Efficiency: Shorts vs Production Content")
ax.set_ylim(0, focus["rev_per_hour"].max() * 1.25)
ax.yaxis.grid(True, alpha=0.3)

# Add ratio annotation
ratio = focus.loc["Short", "rev_per_hour"] / focus.loc["Production", "rev_per_hour"]
ax.annotate(f"Shorts are {ratio:.0f}× more efficient",
            xy=(0.5, focus["rev_per_hour"].max() * 1.1),
            fontsize=13, ha="center", color="#333", fontstyle="italic")
plt.tight_layout()
fig.savefig(FIG / "fig_05_revenue_per_hour.png")
plt.close()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FIG 06 — Shorts Revenue by Duration Bucket                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝
print("Fig 06: Shorts by Duration...")
fig, ax = plt.subplots(figsize=(10, 6))

shorts = d1[(d1["video_type"] == "Short") & d1["duration_seconds"].notna()].copy()
bins_s = [0, 15, 30, 45, 60, 120]
labels_s = ["0–15s", "15–30s", "30–45s", "45–60s", "60–120s"]
shorts["dur_bucket"] = pd.cut(shorts["duration_seconds"], bins=bins_s, labels=labels_s, right=True)
bucket_rev = shorts.groupby("dur_bucket", observed=False)["revenue"].sum()

colors_s = sns.color_palette("husl", len(labels_s))
bars = ax.bar(bucket_rev.index.astype(str), bucket_rev.values,
              color=colors_s, edgecolor="white", linewidth=1.5, width=0.6)

# Annotate all bars
max_val = bucket_rev.max()
for bar, (label, val) in zip(bars, bucket_rev.items()):
    pct = val / bucket_rev.sum() * 100
    fontw = "bold" if label == "45–60s" else "normal"
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max_val * 0.02,
            f"${val:,.0f}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=10, fontweight=fontw)

# Highlight the 45-60s bucket
best_idx = labels_s.index("45–60s")
bars[best_idx].set_edgecolor("red")
bars[best_idx].set_linewidth(3)

ax.set_ylabel("Revenue ($)")
ax.set_xlabel("Duration Bucket")
ax.set_title("Shorts Revenue by Duration — Sweet Spot at 45–60s")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
ax.set_ylim(0, max_val * 1.25)
ax.yaxis.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(FIG / "fig_06_shorts_by_duration.png")
plt.close()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FIG 07 — Production Duration Efficiency                               ║
# ╚══════════════════════════════════════════════════════════════════════════╝
print("Fig 07: Production Duration Efficiency...")
fig, ax = plt.subplots(figsize=(12, 5))

prod = d1[(d1["video_type"] == "Production") & d1["duration_seconds"].notna()].copy()
bins_p = [0, 60, 180, 300, 480, 600, 900, 1800, float("inf")]
labels_p = ["0–1m", "1–3m", "3–5m", "5–8m", "8–10m", "10–15m", "15–30m", "30+m"]
prod["dur_bucket"] = pd.cut(prod["duration_seconds"], bins=bins_p, labels=labels_p, right=True)

# Revenue share and content share (by duration)
bucket_stats = prod.groupby("dur_bucket", observed=False).agg(
    rev=("revenue", "sum"),
    dur=("duration_seconds", "sum")
).reset_index()
bucket_stats["rev_share"] = bucket_stats["rev"] / bucket_stats["rev"].sum()
bucket_stats["content_share"] = bucket_stats["dur"] / bucket_stats["dur"].sum()
bucket_stats["efficiency"] = bucket_stats["rev_share"] / bucket_stats["content_share"].replace(0, np.nan)
bucket_stats["efficiency"] = bucket_stats["efficiency"].fillna(0)

colors_p = sns.color_palette("husl", len(labels_p))
bars = ax.bar(bucket_stats["dur_bucket"].astype(str), bucket_stats["efficiency"],
              color=colors_p, edgecolor="white", linewidth=1.5, width=0.65)

# Reference line at efficiency = 1
ax.axhline(1, color="gray", linestyle="--", alpha=0.5, linewidth=1)
ax.text(len(labels_p) - 0.5, 1.05, "Baseline (1.0)", fontsize=9, color="gray", ha="right")

# Annotate
max_eff = bucket_stats["efficiency"].max()
for bar, (_, row) in zip(bars, bucket_stats.iterrows()):
    if row["efficiency"] > 0:
        fontw = "bold" if row["dur_bucket"] == "8–10m" else "normal"
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max_eff * 0.02,
                f"{row['efficiency']:.2f}", ha="center", va="bottom", fontsize=10, fontweight=fontw)

# Highlight 8-10m
idx_8_10 = labels_p.index("8–10m")
if bucket_stats.loc[idx_8_10, "efficiency"] > 0:
    bars[idx_8_10].set_edgecolor("red")
    bars[idx_8_10].set_linewidth(3)

ax.set_ylabel("Efficiency (Revenue Share / Content Share)")
ax.set_xlabel("Duration Bucket")
ax.set_title("Production Content: Duration Efficiency Index")
ax.set_ylim(0, max_eff * 1.2)
ax.yaxis.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(FIG / "fig_07_production_duration_efficiency.png")
plt.close()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FIG 08 — Lifecycle Curves (K-Means clusters)  ★ KEY CHART ★           ║
# ╚══════════════════════════════════════════════════════════════════════════╝
print("Fig 08: Lifecycle Curves (KMeans)...")
fig, ax = plt.subplots(figsize=(10, 6))

# Build view share features from dataset_2
video_total = d2.groupby("video_id")["views"].sum().rename("total_v")
d2m = d2.merge(video_total, on="video_id")
d2m["view_share"] = d2m["views"] / d2m["total_v"]

pivot = d2m.pivot_table(index="video_id", columns="months_since_publish",
                        values="view_share", aggfunc="sum", fill_value=0)

# Features for clustering
feats = pd.DataFrame(index=pivot.index)
feats["m0"] = pivot[0] if 0 in pivot.columns else 0
feats["m1"] = pivot[1] if 1 in pivot.columns else 0
feats["m2plus"] = pivot[[c for c in pivot.columns if c >= 2]].sum(axis=1)

# Keep only videos with data beyond month 0 (meaningful lifecycle)
feats_multi = feats[feats["m2plus"] > 0].copy()

km = KMeans(n_clusters=3, random_state=42, n_init=10)
feats_multi["cluster"] = km.fit_predict(feats_multi[["m0", "m1", "m2plus"]])

# Label clusters by month-0 share (ascending = more evergreen)
centers = km.cluster_centers_
cluster_order = np.argsort(centers[:, 0])  # sort by month-0 share ascending
label_map = {}
cluster_names = ["Evergreen", "Moderate Decay", "Spike & Die"]
# lowest month-0 share → Evergreen; highest → Spike & Die
for rank, orig_idx in enumerate(cluster_order):
    label_map[orig_idx] = cluster_names[rank]
feats_multi["lifecycle"] = feats_multi["cluster"].map(label_map)

# Merge back to d2m to get view_share per month per cluster
d2_clustered = d2m.merge(feats_multi[["lifecycle"]], left_on="video_id", right_index=True)

# Use view_share directly (already normalized to sum=1 per video)
lifecycle_curves = d2_clustered.groupby(["lifecycle", "months_since_publish"])["view_share"].mean().reset_index()
lifecycle_curves = lifecycle_curves[lifecycle_curves["months_since_publish"] <= 6]
lifecycle_curves.rename(columns={"view_share": "norm_views"}, inplace=True)

lifecycle_colors = {"Spike & Die": "#e74c3c", "Moderate Decay": "#f39c12", "Evergreen": "#2ecc71"}
lifecycle_order = ["Spike & Die", "Moderate Decay", "Evergreen"]

for lc in lifecycle_order:
    sub = lifecycle_curves[lifecycle_curves["lifecycle"] == lc].sort_values("months_since_publish")
    count = (feats_multi["lifecycle"] == lc).sum()
    pct = count / len(feats_multi) * 100
    ax.plot(sub["months_since_publish"], sub["norm_views"],
            marker="o", linewidth=2.5, markersize=8,
            color=lifecycle_colors[lc], label=f"{lc} ({pct:.0f}%, n={count})")

ax.set_xlabel("Months Since Publish")
ax.set_ylabel("Share of Total Views")
ax.set_title("Video Lifecycle Curves — Three Distinct Patterns")
ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
ax.legend(frameon=False, fontsize=11, loc="upper right")
ax.set_xticks(range(7))
ax.yaxis.grid(True, alpha=0.3)
ax.set_xlim(-0.2, 6.2)
plt.tight_layout()
fig.savefig(FIG / "fig_08_lifecycle_curves.png")
plt.close()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FIG 09 — Evergreen Revenue Share (Donut)                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝
print("Fig 09: Evergreen Revenue Share...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Use combined Evergreen + Moderate Decay from D2 lifecycle clusters
eg_video_ids = set(feats_multi[feats_multi["lifecycle"].isin(["Evergreen", "Moderate Decay"])].index)
d1["is_long_lived"] = d1["video_id"].isin(eg_video_ids)

eg_count = d1["is_long_lived"].sum()
eg_pct = eg_count / len(d1) * 100
non_eg_pct = 100 - eg_pct

eg_rev = d1.loc[d1["is_long_lived"], "revenue"].sum()
eg_rev_pct = eg_rev / d1["revenue"].sum() * 100
non_eg_rev_pct = 100 - eg_rev_pct

colors_donut = ["#2ecc71", "#bdc3c7"]

# Compute avg revenue per video
avg_rev_eg = d1.loc[d1["is_long_lived"], "revenue"].mean()
avg_rev_other = d1.loc[~d1["is_long_lived"], "revenue"].mean()

# Left donut: Videos
w1, t1, a1 = ax1.pie([eg_pct, non_eg_pct], colors=colors_donut, explode=(0.05, 0),
                       autopct="%1.1f%%", pctdistance=0.75, startangle=90,
                       wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2))
ax1.set_title(f"Share of Videos\n(n={eg_count} long-lived)", fontsize=13)
for a in a1:
    a.set_fontsize(14)
    a.set_fontweight("bold")

# Right donut: Revenue
w2, t2, a2 = ax2.pie([eg_rev_pct, non_eg_rev_pct], colors=colors_donut, explode=(0.05, 0),
                       autopct="%1.1f%%", pctdistance=0.75, startangle=90,
                       wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2))
ax2.set_title(f"Share of Revenue\n(avg \\${avg_rev_eg:.0f}/video vs \\${avg_rev_other:.0f})", fontsize=13)
for a in a2:
    a.set_fontsize(14)
    a.set_fontweight("bold")

fig.legend(["Long-lived (Evergreen + Moderate)", "Spike & Die"],
           loc="lower center", ncol=2, frameon=False, fontsize=11,
           bbox_to_anchor=(0.5, -0.02))
fig.suptitle("Long-Lived Content: ~9% of Videos with Extended Lifecycle", fontsize=14, y=1.0)
plt.tight_layout()
fig.savefig(FIG / "fig_09_evergreen_revenue_share.png")
plt.close()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FIG 10 — Feature Importance (GradientBoosting)                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝
print("Fig 10: Feature Importance...")
fig, ax = plt.subplots(figsize=(10, 6))

# Prepare features
d1_model = d1.dropna(subset=["duration_seconds", "first_7d_views", "total_views"]).copy()
d1_model = d1_model[d1_model["total_views"] > 0].copy()

d1_model["first7_ratio"] = d1_model["first_7d_views"] / d1_model["total_views"]
d1_model["first30_ratio"] = d1_model["first_30d_views"] / d1_model["total_views"]
d1_model["wt_7d_ratio"] = d1_model["watch_time_7d"] / d1_model["watch_time_minutes"].replace(0, np.nan)
d1_model["wt_30d_ratio"] = d1_model["watch_time_30d"] / d1_model["watch_time_minutes"].replace(0, np.nan)
# Use dataset_2 cluster-based evergreen (more accurate than first7 proxy)
d1_model["is_evergreen"] = d1_model["video_id"].isin(eg_video_ids).astype(int)

feature_cols = [
    "first7_ratio", "first30_ratio", "duration_seconds", "engagement_rate",
    "estimated_cpm", "avg_percentage_viewed", "avg_view_duration_seconds",
    "wt_7d_ratio", "wt_30d_ratio", "likes", "comments", "shares",
    "ad_impressions", "total_views"
]

X = d1_model[feature_cols].fillna(0)
y = d1_model["is_evergreen"]

gb = GradientBoostingClassifier(n_estimators=200, max_depth=4, random_state=42,
                                 learning_rate=0.1, subsample=0.8)
gb.fit(X, y)

importances = pd.Series(gb.feature_importances_, index=feature_cols)
top8 = importances.nlargest(8).sort_values()

# Clean feature names for display
name_map = {
    "first7_ratio": "First 7-Day View Ratio",
    "first30_ratio": "First 30-Day View Ratio",
    "duration_seconds": "Video Duration",
    "engagement_rate": "Engagement Rate",
    "estimated_cpm": "Estimated CPM",
    "avg_percentage_viewed": "Avg % Viewed",
    "avg_view_duration_seconds": "Avg View Duration",
    "wt_7d_ratio": "Watch Time 7D Ratio",
    "wt_30d_ratio": "Watch Time 30D Ratio",
    "likes": "Likes",
    "comments": "Comments",
    "shares": "Shares",
    "ad_impressions": "Ad Impressions",
    "total_views": "Total Views",
}

colors_fi = sns.color_palette("husl", 8)
bars = ax.barh([name_map.get(f, f) for f in top8.index], top8.values,
               color=colors_fi, edgecolor="white", linewidth=1)

for bar, val in zip(bars, top8.values):
    ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
            f"{val:.3f}", va="center", fontsize=10)

ax.set_xlabel("Feature Importance")
ax.set_title("What Predicts Evergreen Content? (GradientBoosting)")
ax.set_xlim(0, top8.max() * 1.2)
ax.xaxis.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(FIG / "fig_10_feature_importance.png")
plt.close()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FIG 11 — Cross-Platform Boost                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝
print("Fig 11: Cross-Platform Boost...")
fig, ax = plt.subplots(figsize=(10, 6))

# Deduplicate d3 (there are duplicates)
d3_dedup = d3.drop_duplicates(subset=["video_id", "content_original_id", "platform"])

# Count unique platforms per content
content_nplat = d3_dedup.groupby("content_original_id")["platform"].nunique().rename("n_platforms")
d3_analysis = d3_dedup.merge(content_nplat, on="content_original_id")
d3_analysis["is_multi"] = d3_analysis["n_platforms"] > 1

platforms_cp = ["YouTube", "Facebook", "Snapchat"]
x_pos = np.arange(len(platforms_cp))
width = 0.35

single_means = []
multi_means = []
boosts = []
pvals = []

for plat in platforms_cp:
    sub = d3_analysis[d3_analysis["platform"] == plat]
    s = sub[~sub["is_multi"]]["total_views"]
    m = sub[sub["is_multi"]]["total_views"]
    single_means.append(s.mean())
    multi_means.append(m.mean())
    boost = (m.mean() / s.mean() - 1) * 100
    boosts.append(boost)
    _, p = stats.mannwhitneyu(s, m, alternative="two-sided")
    pvals.append(p)

bars1 = ax.bar(x_pos - width/2, single_means, width, label="Single Platform",
               color=sns.color_palette("husl", 2)[0], edgecolor="white", linewidth=1)
bars2 = ax.bar(x_pos + width/2, multi_means, width, label="Multi-Platform",
               color=sns.color_palette("husl", 2)[1], edgecolor="white", linewidth=1)

# Annotations
for i, (boost, pval) in enumerate(zip(boosts, pvals)):
    max_h = max(single_means[i], multi_means[i])
    stars = "***" if pval < 0.001 else ("**" if pval < 0.01 else ("*" if pval < 0.05 else "n.s."))
    sign = "+" if boost > 0 else ""
    if boost > 0:
        ax.text(x_pos[i] + width/2, max_h + max(multi_means) * 0.02,
                f"{sign}{boost:.0f}% {stars}", ha="center", va="bottom",
                fontsize=11, fontweight="bold", color="#2ecc71")
    else:
        ax.text(x_pos[i], max_h + max(multi_means) * 0.02,
                f"{sign}{boost:.0f}%", ha="center", va="bottom",
                fontsize=11, fontweight="bold", color="#e74c3c")

ax.set_xticks(x_pos)
ax.set_xticklabels(platforms_cp)
ax.set_ylabel("Average Views")
ax.set_title("Cross-Platform Publishing Boost: Single vs Multi-Platform")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
ax.legend(frameon=False, fontsize=11)
ax.yaxis.grid(True, alpha=0.3)
ax.set_ylim(0, max(multi_means) * 1.2)
plt.tight_layout()
fig.savefig(FIG / "fig_11_crossplatform_boost.png")
plt.close()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FIG 12 — Simpson's Paradox (Scatter)                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝
print("Fig 12: Simpson's Paradox...")
fig, ax = plt.subplots(figsize=(10, 6))

d1_scatter = d1[d1["engagement_rate"].notna()].copy()
d1_scatter["log_revenue"] = np.log1p(d1_scatter["revenue"])
# Clip engagement rate to 0–99th percentile for readability
p99_eng = d1_scatter["engagement_rate"].quantile(0.99)
p01_eng = d1_scatter["engagement_rate"].quantile(0.01)
d1_scatter = d1_scatter[(d1_scatter["engagement_rate"] >= p01_eng) &
                        (d1_scatter["engagement_rate"] <= p99_eng)]

# Plot Story and Shorts last (on top) for visibility
plot_order = ["Production", "Live", "Story", "Short"]
for vtype in plot_order:
    sub = d1_scatter[d1_scatter["video_type"] == vtype]
    if len(sub) > 0:
        ax.scatter(sub["engagement_rate"], sub["log_revenue"],
                   alpha=0.3, s=20, label=vtype, color=TYPE_COLORS[vtype],
                   edgecolors="none")

ax.set_xlabel("Engagement Rate (%)")
ax.set_ylabel("log(Revenue + 1)")
ax.set_title("Simpson's Paradox: High Engagement ≠ High Revenue")
ax.legend(frameon=False, fontsize=11, markerscale=3)

# Add annotation arrows for key clusters
shorts_data = d1_scatter[d1_scatter["video_type"] == "Short"]
story_data = d1_scatter[d1_scatter["video_type"] == "Story"]
if len(shorts_data) > 0:
    med_eng_s = shorts_data["engagement_rate"].median()
    med_rev_s = shorts_data["log_revenue"].median()
    ax.annotate("Shorts: high engagement\nbut low revenue",
                xy=(med_eng_s + 0.5, med_rev_s + 0.3),
                xytext=(max(med_eng_s + 1.5, 3), med_rev_s + 3),
                fontsize=10, color=TYPE_COLORS["Short"],
                arrowprops=dict(arrowstyle="->", color=TYPE_COLORS["Short"], lw=1.5),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor=TYPE_COLORS["Short"], alpha=0.9))

if len(story_data) > 0:
    med_eng_st = story_data["engagement_rate"].median()
    med_rev_st = story_data["log_revenue"].median()
    ax.annotate("Story (Snapchat):\nhigh revenue cluster",
                xy=(med_eng_st, med_rev_st + 1),
                xytext=(med_eng_st + 2, med_rev_st + 2),
                fontsize=10, color=TYPE_COLORS["Story"],
                arrowprops=dict(arrowstyle="->", color=TYPE_COLORS["Story"], lw=1.5),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                          edgecolor=TYPE_COLORS["Story"], alpha=0.9))

ax.yaxis.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(FIG / "fig_12_simpson_paradox.png")
plt.close()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FIG 13 — Correlation Heatmap                                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝
print("Fig 13: Correlation Heatmap...")
fig, ax = plt.subplots(figsize=(10, 8))

corr_cols = ["total_views", "watch_time_minutes", "likes", "comments", "shares",
             "engagement_rate", "avg_percentage_viewed", "estimated_cpm",
             "duration_seconds", "ad_impressions", "revenue"]

corr_labels = ["Total Views", "Watch Time", "Likes", "Comments", "Shares",
               "Engagement Rate", "Avg % Viewed", "CPM",
               "Duration", "Ad Impressions", "Revenue"]

corr_data = d1[corr_cols].dropna()
corr_matrix = corr_data.corr(method="spearman")

mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
cmap = sns.diverging_palette(220, 20, as_cmap=True)

sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap=cmap,
            center=0, vmin=-1, vmax=1, square=True,
            xticklabels=corr_labels, yticklabels=corr_labels,
            linewidths=0.5, linecolor="white",
            cbar_kws={"shrink": 0.8, "label": "Spearman ρ"},
            ax=ax, annot_kws={"size": 9})

ax.set_title("Spearman Correlation Matrix — Key Metrics vs Revenue")
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
fig.savefig(FIG / "fig_13_correlation_heatmap.png")
plt.close()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FIG 14 — Lorenz Curve (Snapchat Revenue Concentration)                ║
# ╚══════════════════════════════════════════════════════════════════════════╝
print("Fig 14: Lorenz Curve...")
fig, ax = plt.subplots(figsize=(10, 6))

snap = d1[d1["platform"] == "Snapchat"].copy()
ch_rev = snap.groupby("channel_id")["revenue"].sum().sort_values()
n = len(ch_rev)
cumrev = np.cumsum(ch_rev.values) / ch_rev.sum()
cumfrac = np.arange(1, n + 1) / n

# Gini coefficient
gini = 1 - 2 * np.trapz(cumrev, cumfrac)

# Plot
ax.plot([0, 1], [0, 1], "k--", alpha=0.4, label="Perfect Equality")
ax.fill_between(np.insert(cumfrac, 0, 0), np.insert(cumrev, 0, 0),
                np.insert(cumfrac, 0, 0), alpha=0.15, color=PALETTE_3[2])
ax.plot(np.insert(cumfrac, 0, 0), np.insert(cumrev, 0, 0),
        color=PALETTE_3[2], linewidth=2.5, label=f"Snapchat (Gini = {gini:.2f})")

# Mark channel_621
ch621_rev = ch_rev.get("channel_621", 0)
ch621_cumfrac = cumfrac[ch_rev.index.get_loc("channel_621")] if "channel_621" in ch_rev.index else None
ch621_cumrev = cumrev[ch_rev.index.get_loc("channel_621")] if "channel_621" in ch_rev.index else None

if ch621_cumfrac is not None:
    ax.scatter([ch621_cumfrac], [ch621_cumrev], s=120, color="red", zorder=5, edgecolors="white", linewidth=2)
    ch621_pct = ch621_rev / ch_rev.sum() * 100
    ax.annotate(f"channel_621\n({ch621_pct:.0f}% of revenue)",
                xy=(ch621_cumfrac, ch621_cumrev),
                xytext=(ch621_cumfrac - 0.25, ch621_cumrev - 0.15),
                fontsize=11, fontweight="bold", color="red",
                arrowprops=dict(arrowstyle="->", color="red", lw=1.5),
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="red", alpha=0.9))

ax.set_xlabel("Cumulative Share of Channels")
ax.set_ylabel("Cumulative Share of Revenue")
ax.set_title("Snapchat Revenue Concentration (Lorenz Curve)")
ax.legend(frameon=False, fontsize=11, loc="upper left")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_aspect("equal")
ax.yaxis.grid(True, alpha=0.3)
ax.xaxis.grid(True, alpha=0.3)
plt.tight_layout()
fig.savefig(FIG / "fig_14_lorenz_curve.png")
plt.close()

# ── Summary ────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("All figures saved to figures/")
print("="*60)
for f in sorted(FIG.glob("fig_*.png")):
    size_kb = f.stat().st_size / 1024
    print(f"  ✓ {f.name}  ({size_kb:.0f} KB)")
print(f"\nTotal: {len(list(FIG.glob('fig_*.png')))} figures")
