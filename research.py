"""TheSoul Deep Research — 3 high-priority directions."""
import pandas as pd
import numpy as np
from scipy import stats
import json
import warnings
warnings.filterwarnings('ignore')

# Load data
df1 = pd.read_csv('data/dataset_1_video_performance.csv')
df2 = pd.read_csv('data/dataset_2_cohort_analysis.csv')
df3 = pd.read_csv('data/dataset_3_cross_platform.csv')

df1['duration_seconds'] = (
    df1['duration_seconds'].astype(str)
    .str.replace(',', '.', regex=False)
    .pipe(pd.to_numeric, errors='coerce')
)
df1['revenue_proxy'] = df1['total_views'] * df1['estimated_cpm'] / 1000
df1['publish_date'] = pd.to_datetime(df1['publish_date'], errors='coerce')

results = {}

# ============================================================
# RESEARCH 2.1: Channel-Level Efficiency Analysis
# ============================================================
print("=" * 60)
print("RESEARCH 2.1: Channel-Level Efficiency")
print("=" * 60)

# Per-channel stats
ch = df1.groupby(['channel_id', 'platform']).agg(
    n_videos=('video_id', 'count'),
    total_revenue=('revenue_proxy', 'sum'),
    avg_revenue=('revenue_proxy', 'mean'),
    median_revenue=('revenue_proxy', 'median'),
    total_views=('total_views', 'sum'),
    avg_views=('total_views', 'mean'),
    avg_cpm=('estimated_cpm', 'mean'),
    avg_engagement=('engagement_rate', 'mean'),
    avg_retention=('avg_percentage_viewed', 'mean'),
    avg_duration=('duration_seconds', 'mean'),
    avg_watch_time=('watch_time_minutes', 'mean'),
).reset_index()

ch['revenue_per_video'] = ch['total_revenue'] / ch['n_videos']

# Video type mix per channel
type_mix = df1.groupby(['channel_id', 'video_type']).size().unstack(fill_value=0)
type_mix_pct = type_mix.div(type_mix.sum(axis=1), axis=0)
if 'Production' in type_mix_pct.columns:
    ch = ch.merge(type_mix_pct[['Production']].rename(columns={'Production': 'production_share'}),
                  left_on='channel_id', right_index=True, how='left')
    ch['production_share'] = ch['production_share'].fillna(0)

# Evergreen rate per channel (from cohort data)
d2_pivot = df2.groupby(['video_id', 'months_since_publish'])['views'].sum().unstack(fill_value=0)
if 0 in d2_pivot.columns and 3 in d2_pivot.columns:
    d2_pivot['eg_ratio'] = d2_pivot[3] / d2_pivot[0].replace(0, np.nan)
    d2_pivot['is_evergreen'] = d2_pivot['eg_ratio'] > 0.10
    eg_by_video = d2_pivot[['is_evergreen']].reset_index()
    eg_by_channel = eg_by_video.merge(df1[['video_id', 'channel_id']], on='video_id')
    eg_rate = eg_by_channel.groupby('channel_id')['is_evergreen'].mean().rename('evergreen_rate')
    ch = ch.merge(eg_rate, left_on='channel_id', right_index=True, how='left')

# Top vs Bottom channels
ch_yt = ch[ch['platform'] == 'YouTube'].copy()
ch_snap = ch[ch['platform'] == 'Snapchat'].copy()

print("\n--- YouTube Channels (sorted by revenue/video) ---")
ch_yt_sorted = ch_yt.sort_values('revenue_per_video', ascending=False)
top10_yt = ch_yt_sorted.head(10)
bottom50_yt = ch_yt_sorted.tail(len(ch_yt_sorted) // 2)

print(f"\nTop-10 YouTube channels:")
for _, r in top10_yt.iterrows():
    eg = f", evergreen={r['evergreen_rate']:.1%}" if pd.notna(r.get('evergreen_rate')) else ""
    prod = f", prod_share={r['production_share']:.0%}" if pd.notna(r.get('production_share')) else ""
    print(f"  {r['channel_id']}: ${r['revenue_per_video']:.2f}/video, {r['n_videos']} videos{prod}{eg}")

print(f"\nTop-10 vs Bottom-50% comparison:")
for col in ['avg_revenue', 'avg_cpm', 'avg_retention', 'avg_duration', 'avg_engagement']:
    t_val = top10_yt[col].mean()
    b_val = bottom50_yt[col].mean()
    ratio = t_val / b_val if b_val > 0 else float('inf')
    print(f"  {col}: top={t_val:.2f}, bottom={b_val:.2f}, ratio={ratio:.1f}x")

if 'production_share' in ch_yt.columns:
    corr_prod_rev = ch_yt[['production_share', 'revenue_per_video']].dropna()
    if len(corr_prod_rev) > 5:
        r, p = stats.spearmanr(corr_prod_rev['production_share'], corr_prod_rev['revenue_per_video'])
        print(f"\n  Production share ↔ Revenue/video correlation: r={r:.3f}, p={p:.4f}")

if 'evergreen_rate' in ch_yt.columns:
    corr_eg_rev = ch_yt[['evergreen_rate', 'revenue_per_video']].dropna()
    if len(corr_eg_rev) > 5:
        r, p = stats.spearmanr(corr_eg_rev['evergreen_rate'], corr_eg_rev['revenue_per_video'])
        print(f"  Evergreen rate ↔ Revenue/video correlation: r={r:.3f}, p={p:.4f}")

print(f"\n--- Snapchat Channels ---")
ch_snap_sorted = ch_snap.sort_values('total_revenue', ascending=False)
print(f"Total Snapchat channels: {len(ch_snap)}")
print(f"Top-5 revenue share: {ch_snap_sorted.head(5)['total_revenue'].sum() / ch_snap_sorted['total_revenue'].sum():.1%}")
print(f"Top-10 revenue share: {ch_snap_sorted.head(10)['total_revenue'].sum() / ch_snap_sorted['total_revenue'].sum():.1%}")
print(f"\nTop-5 Snapchat channels:")
for _, r in ch_snap_sorted.head(5).iterrows():
    share = r['total_revenue'] / ch_snap_sorted['total_revenue'].sum() * 100
    print(f"  {r['channel_id']}: ${r['total_revenue']:,.0f} ({share:.1f}%), {r['n_videos']} videos, ${r['revenue_per_video']:.0f}/video")

# Gini coefficient for revenue concentration
def gini(arr):
    arr = np.sort(np.array(arr, dtype=float))
    n = len(arr)
    if n == 0: return 0
    idx = np.arange(1, n + 1)
    return (2 * np.sum(idx * arr) / (n * np.sum(arr))) - (n + 1) / n

for plat_name, plat_df in [('YouTube', ch_yt), ('Snapchat', ch_snap)]:
    g = gini(plat_df['total_revenue'].values)
    print(f"\n  {plat_name} channel revenue Gini: {g:.3f}")

results['2.1'] = {
    'yt_channels': len(ch_yt),
    'snap_channels': len(ch_snap),
    'snap_top5_share': f"{ch_snap_sorted.head(5)['total_revenue'].sum() / ch_snap_sorted['total_revenue'].sum():.1%}",
}

# ============================================================
# RESEARCH 2.2: Engagement → Revenue Disconnect
# ============================================================
print("\n" + "=" * 60)
print("RESEARCH 2.2: Engagement → Revenue Disconnect")
print("=" * 60)

# Correlation matrix: engagement metrics vs revenue
eng_cols = ['engagement_rate', 'likes', 'comments', 'shares', 'dislikes',
            'avg_percentage_viewed', 'avg_view_duration_seconds', 'watch_time_minutes',
            'ad_impressions', 'total_views']
target = 'revenue_proxy'

print("\n--- Spearman correlations with revenue_proxy ---")
corr_results = {}
for col in eng_cols:
    valid = df1[[col, target]].dropna()
    valid = valid[(valid[col] > 0) | (col == 'engagement_rate')]
    if len(valid) > 30:
        r, p = stats.spearmanr(valid[col], valid[target])
        corr_results[col] = {'r': r, 'p': p, 'n': len(valid)}
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'n.s.'
        print(f"  {col:35s}: r={r:+.3f} {sig} (n={len(valid):,})")

# By platform
print("\n--- Correlations by Platform ---")
for plat in ['YouTube', 'Facebook', 'Snapchat']:
    sub = df1[df1['platform'] == plat]
    print(f"\n  {plat}:")
    for col in ['engagement_rate', 'avg_percentage_viewed', 'watch_time_minutes', 'ad_impressions']:
        valid = sub[[col, target]].dropna()
        valid = valid[(valid[col] > 0) | (col == 'engagement_rate')]
        if len(valid) > 20:
            r, p = stats.spearmanr(valid[col], valid[target])
            sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'n.s.'
            print(f"    {col:35s}: r={r:+.3f} {sig} (n={len(valid):,})")

# By video type (YouTube)
print("\n--- YouTube: Engagement vs Revenue by Format ---")
for vtype in ['Short', 'Production', 'Live']:
    sub = df1[(df1['platform'] == 'YouTube') & (df1['video_type'] == vtype)]
    if len(sub) > 20:
        print(f"\n  {vtype} (n={len(sub)}):")
        for col in ['engagement_rate', 'avg_percentage_viewed', 'watch_time_minutes']:
            valid = sub[[col, target]].dropna()
            if len(valid) > 10:
                r, p = stats.spearmanr(valid[col], valid[target])
                sig = '***' if p < 0.001 else 'n.s.'
                print(f"    {col:35s}: r={r:+.3f} {sig}")

# High engagement vs high revenue overlap
yt = df1[df1['platform'] == 'YouTube'].copy()
yt['eng_q'] = pd.qcut(yt['engagement_rate'].rank(method='first'), 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
yt['rev_q'] = pd.qcut(yt['revenue_proxy'].rank(method='first'), 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])

confusion = pd.crosstab(yt['eng_q'], yt['rev_q'], normalize='all') * 100
print("\n--- YouTube: Engagement Quartile vs Revenue Quartile (%) ---")
print(confusion.round(1).to_string())

# What % of top-engagement videos are also top-revenue?
top_eng_top_rev = len(yt[(yt['eng_q'] == 'Q4') & (yt['rev_q'] == 'Q4')]) / len(yt[yt['eng_q'] == 'Q4']) * 100
print(f"\n  Top engagement quartile → also top revenue: {top_eng_top_rev:.1f}% (random=25%)")

# Best predictor search
print("\n--- Best single predictor of revenue (YouTube, Spearman r) ---")
predictors = ['engagement_rate', 'likes', 'comments', 'shares',
              'avg_percentage_viewed', 'avg_view_duration_seconds',
              'watch_time_minutes', 'ad_impressions', 'total_views', 'duration_seconds']
best_r = 0
best_col = ''
for col in predictors:
    valid = yt[[col, target]].dropna()
    if len(valid) > 20:
        r, _ = stats.spearmanr(valid[col], valid[target])
        if abs(r) > abs(best_r):
            best_r = r
            best_col = col
        print(f"  {col:35s}: r={r:+.3f}")
print(f"\n  BEST predictor: {best_col} (r={best_r:+.3f})")

# ============================================================
# RESEARCH 2.3: Content Velocity vs Quality
# ============================================================
print("\n" + "=" * 60)
print("RESEARCH 2.3: Content Velocity vs Quality")
print("=" * 60)

# Publishing frequency per channel
df1_dated = df1[df1['publish_date'].notna()].copy()

# Date range per channel
ch_dates = df1_dated.groupby('channel_id').agg(
    first_pub=('publish_date', 'min'),
    last_pub=('publish_date', 'max'),
    n_videos=('video_id', 'count'),
    total_revenue=('revenue_proxy', 'sum'),
    avg_revenue=('revenue_proxy', 'mean'),
    avg_views=('total_views', 'mean'),
).reset_index()

ch_dates['days_active'] = (ch_dates['last_pub'] - ch_dates['first_pub']).dt.days + 1
ch_dates['videos_per_week'] = ch_dates['n_videos'] / (ch_dates['days_active'] / 7)
ch_dates = ch_dates[ch_dates['days_active'] > 14]  # At least 2 weeks active
ch_dates = ch_dates[ch_dates['n_videos'] >= 5]  # At least 5 videos

print(f"\nChannels with enough data: {len(ch_dates)}")
print(f"Median publishing rate: {ch_dates['videos_per_week'].median():.1f} videos/week")

# Frequency buckets
ch_dates['freq_bucket'] = pd.cut(ch_dates['videos_per_week'],
                                  bins=[0, 1, 3, 7, 14, 100],
                                  labels=['<1/wk', '1-3/wk', '3-7/wk', '1-2/day', '>2/day'])

freq_stats = ch_dates.groupby('freq_bucket', observed=True).agg(
    n_channels=('channel_id', 'count'),
    avg_revenue_per_video=('avg_revenue', 'mean'),
    median_revenue_per_video=('avg_revenue', 'median'),
    avg_total_revenue=('total_revenue', 'mean'),
    avg_videos=('n_videos', 'mean'),
).round(2)
print("\n--- Revenue by Publishing Frequency ---")
print(freq_stats.to_string())

# Correlation: frequency vs revenue/video
r_freq, p_freq = stats.spearmanr(ch_dates['videos_per_week'], ch_dates['avg_revenue'])
print(f"\nPublishing frequency ↔ Revenue/video: r={r_freq:+.3f}, p={p_freq:.4f}")

r_freq_total, p_freq_total = stats.spearmanr(ch_dates['videos_per_week'], ch_dates['total_revenue'])
print(f"Publishing frequency ↔ Total revenue: r={r_freq_total:+.3f}, p={p_freq_total:.4f}")

# Add platform context
ch_plat = df1.groupby('channel_id')['platform'].first()
ch_dates = ch_dates.merge(ch_plat.rename('platform'), left_on='channel_id', right_index=True)

for plat in ['YouTube', 'Snapchat', 'Facebook']:
    sub = ch_dates[ch_dates['platform'] == plat]
    if len(sub) > 5:
        r, p = stats.spearmanr(sub['videos_per_week'], sub['avg_revenue'])
        print(f"  {plat}: freq↔rev/video r={r:+.3f}, p={p:.4f} (n={len(sub)})")

# Optimal frequency — peak revenue/video
print("\n--- Optimal Frequency (peak avg revenue/video by bucket) ---")
best_bucket = freq_stats['avg_revenue_per_video'].idxmax()
print(f"  Best bucket: {best_bucket} (avg ${freq_stats.loc[best_bucket, 'avg_revenue_per_video']:.2f}/video)")

# Video type mix by frequency
ch_type_mix = df1.groupby(['channel_id', 'video_type']).size().unstack(fill_value=0)
ch_type_mix_pct = ch_type_mix.div(ch_type_mix.sum(axis=1), axis=0)
ch_dates_mix = ch_dates.merge(ch_type_mix_pct, left_on='channel_id', right_index=True, how='left')

print("\n--- Format Mix by Publishing Frequency ---")
for bucket in freq_stats.index:
    sub = ch_dates_mix[ch_dates_mix['freq_bucket'] == bucket]
    if len(sub) > 0:
        mix_str = []
        for vt in ['Short', 'Production', 'Story', 'Live']:
            if vt in sub.columns:
                mix_str.append(f"{vt}={sub[vt].mean():.0%}")
        print(f"  {bucket}: {', '.join(mix_str)} (n={len(sub)} channels)")

# ============================================================
# BONUS: Quick checks on medium-priority items
# ============================================================
print("\n" + "=" * 60)
print("BONUS: Quick Medium-Priority Checks")
print("=" * 60)

# 2.4 Watch time efficiency
print("\n--- 2.4 Revenue per Watch Time Minute ---")
df1_wt = df1[df1['watch_time_minutes'] > 0].copy()
df1_wt['rev_per_wt_min'] = df1_wt['revenue_proxy'] / df1_wt['watch_time_minutes']

for plat in ['YouTube', 'Facebook', 'Snapchat']:
    sub = df1_wt[df1_wt['platform'] == plat]
    print(f"  {plat}: ${sub['rev_per_wt_min'].median():.4f}/min (median), ${sub['rev_per_wt_min'].mean():.4f}/min (mean)")
    if plat == 'YouTube':
        for vt in ['Short', 'Production', 'Live']:
            vt_sub = sub[sub['video_type'] == vt]
            if len(vt_sub) > 0:
                print(f"    {vt}: ${vt_sub['rev_per_wt_min'].median():.4f}/min (n={len(vt_sub)})")

# 2.5 First 7 days as predictor
print("\n--- 2.5 First 7 Days Predictor ---")
df1_7d = df1[(df1['first_7d_views'].notna()) & (df1['total_views'] > 0)].copy()
df1_7d['pct_7d'] = df1_7d['first_7d_views'] / df1_7d['total_views']

# Merge with evergreen classification
if 'is_evergreen' in eg_by_video.columns:
    df1_7d_eg = df1_7d.merge(eg_by_video[['video_id', 'is_evergreen']], on='video_id', how='inner')
    eg_7d = df1_7d_eg[df1_7d_eg['is_evergreen'] == True]['pct_7d']
    non_eg_7d = df1_7d_eg[df1_7d_eg['is_evergreen'] == False]['pct_7d']
    print(f"  Evergreen videos: {eg_7d.median():.1%} views in first 7 days (n={len(eg_7d)})")
    print(f"  Normal videos:    {non_eg_7d.median():.1%} views in first 7 days (n={len(non_eg_7d)})")
    
    # Can we predict evergreen from 7-day share?
    from sklearn.metrics import roc_auc_score
    valid = df1_7d_eg[['pct_7d', 'is_evergreen']].dropna()
    if len(valid) > 20:
        auc = roc_auc_score(valid['is_evergreen'], 1 - valid['pct_7d'])  # lower 7d share = more evergreen
        print(f"  ROC AUC (7-day share → evergreen): {auc:.3f}")

# 2.6 Day of week
print("\n--- 2.6 Day of Week Effect ---")
df1_dated['dow'] = df1_dated['publish_date'].dt.day_name()
dow_stats = df1_dated.groupby('dow').agg(
    n=('video_id', 'count'),
    avg_revenue=('revenue_proxy', 'mean'),
    avg_views=('total_views', 'mean'),
).round(2)
dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
dow_stats = dow_stats.reindex(dow_order)
print(dow_stats.to_string())

# 2.7 Dislike ratio
print("\n--- 2.7 Dislike Ratio ---")
yt_dis = df1[(df1['platform'] == 'YouTube') & (df1['likes'] + df1['dislikes'] > 5)].copy()
yt_dis['dislike_ratio'] = yt_dis['dislikes'] / (yt_dis['likes'] + yt_dis['dislikes'])
r_dis, p_dis = stats.spearmanr(yt_dis['dislike_ratio'], yt_dis['revenue_proxy'])
print(f"  Dislike ratio ↔ Revenue: r={r_dis:+.3f}, p={p_dis:.4f} (n={len(yt_dis)})")
r_dis_v, p_dis_v = stats.spearmanr(yt_dis['dislike_ratio'], yt_dis['total_views'])
print(f"  Dislike ratio ↔ Views:   r={r_dis_v:+.3f}, p={p_dis_v:.4f}")

# 2.8 Ad fill rate
print("\n--- 2.8 Ad Fill Rate ---")
df1_ad = df1[(df1['total_views'] > 0)].copy()
df1_ad['ad_fill'] = df1_ad['ad_impressions'] / df1_ad['total_views']
for plat in ['YouTube', 'Snapchat']:
    sub = df1_ad[df1_ad['platform'] == plat]
    print(f"  {plat}: median fill={sub['ad_fill'].median():.3f}, mean={sub['ad_fill'].mean():.3f}")
    if plat == 'YouTube':
        for vt in ['Short', 'Production', 'Live']:
            vt_sub = sub[sub['video_type'] == vt]
            if len(vt_sub) > 0:
                print(f"    {vt}: fill={vt_sub['ad_fill'].median():.3f} (n={len(vt_sub)})")

print("\n\n=== RESEARCH COMPLETE ===")
