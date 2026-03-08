"""TheSoul Deep Research — Phase 2: Content-focused actionable insights."""
import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

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

# ============================================================
# 1. CONTENT DURATION SWEET SPOT (granular)
# ============================================================
print("=" * 70)
print("1. CONTENT DURATION SWEET SPOT — Optimal length per platform/format")
print("=" * 70)

# YouTube detailed duration analysis
yt = df1[(df1['platform'] == 'YouTube') & df1['duration_seconds'].notna()].copy()
bins = [0, 15, 30, 60, 120, 300, 480, 600, 900, 1200, 1800, 3600, 99999]
labels = ['0-15s', '15-30s', '30-60s', '1-2m', '2-5m', '5-8m', '8-10m', '10-15m', '15-20m', '20-30m', '30-60m', '60m+']
yt['dur_bucket'] = pd.cut(yt['duration_seconds'], bins=bins, labels=labels)

dur_detail = yt.groupby('dur_bucket', observed=True).agg(
    n=('video_id', 'count'),
    avg_revenue=('revenue_proxy', 'mean'),
    median_revenue=('revenue_proxy', 'median'),
    avg_views=('total_views', 'mean'),
    avg_cpm=('estimated_cpm', 'mean'),
    avg_retention=('avg_percentage_viewed', 'mean'),
    avg_watch_time=('watch_time_minutes', 'mean'),
    total_revenue=('revenue_proxy', 'sum'),
).round(2)
dur_detail['rev_share'] = (dur_detail['total_revenue'] / dur_detail['total_revenue'].sum() * 100).round(1)
dur_detail['supply_share'] = (dur_detail['n'] / dur_detail['n'].sum() * 100).round(1)

print("\nYouTube Duration Analysis:")
print(dur_detail[['n', 'supply_share', 'avg_revenue', 'avg_cpm', 'avg_retention', 'rev_share']].to_string())

# Revenue efficiency = revenue / supply_share
dur_detail['efficiency'] = dur_detail['rev_share'] / dur_detail['supply_share']
print("\n\nRevenue Efficiency (rev_share / supply_share):")
print(dur_detail[['supply_share', 'rev_share', 'efficiency']].to_string())
best_dur = dur_detail['efficiency'].idxmax()
print(f"\nMost efficient duration: {best_dur} (efficiency={dur_detail.loc[best_dur, 'efficiency']:.1f}x)")

# Facebook
fb = df1[(df1['platform'] == 'Facebook') & df1['duration_seconds'].notna()].copy()
fb_bins = [0, 60, 180, 300, 600, 1200, 99999]
fb_labels = ['0-1m', '1-3m', '3-5m', '5-10m', '10-20m', '20m+']
fb['dur_bucket'] = pd.cut(fb['duration_seconds'], bins=fb_bins, labels=fb_labels)

fb_dur = fb.groupby('dur_bucket', observed=True).agg(
    n=('video_id', 'count'),
    avg_revenue=('revenue_proxy', 'mean'),
    avg_views=('total_views', 'mean'),
).round(2)
print(f"\n\nFacebook Duration Analysis:")
print(fb_dur.to_string())

# Snapchat
snap = df1[(df1['platform'] == 'Snapchat') & df1['duration_seconds'].notna()].copy()
if len(snap) > 0:
    snap_bins = [0, 30, 60, 120, 300, 600, 99999]
    snap_labels = ['0-30s', '30-60s', '1-2m', '2-5m', '5-10m', '10m+']
    snap['dur_bucket'] = pd.cut(snap['duration_seconds'], bins=snap_bins, labels=snap_labels)
    snap_dur = snap.groupby('dur_bucket', observed=True).agg(
        n=('video_id', 'count'),
        avg_revenue=('revenue_proxy', 'mean'),
    ).round(2)
    print(f"\n\nSnapchat Duration Analysis:")
    print(snap_dur.to_string())

# ============================================================
# 2. CHANNEL ARCHETYPES — What makes top channels different?
# ============================================================
print("\n\n" + "=" * 70)
print("2. CHANNEL ARCHETYPES — Clustering channels by behavior")
print("=" * 70)

ch_stats = df1.groupby(['channel_id', 'platform']).agg(
    n_videos=('video_id', 'count'),
    total_revenue=('revenue_proxy', 'sum'),
    avg_revenue=('revenue_proxy', 'mean'),
    avg_views=('total_views', 'mean'),
    avg_cpm=('estimated_cpm', 'mean'),
    avg_engagement=('engagement_rate', 'mean'),
    avg_retention=('avg_percentage_viewed', 'mean'),
    avg_duration=('duration_seconds', 'mean'),
    total_watch_time=('watch_time_minutes', 'sum'),
    avg_watch_time=('watch_time_minutes', 'mean'),
).reset_index()

# Video type distribution
type_mix = df1.groupby(['channel_id', 'video_type']).size().unstack(fill_value=0)
type_pct = type_mix.div(type_mix.sum(axis=1), axis=0)
for vt in ['Short', 'Production', 'Story', 'Live']:
    if vt in type_pct.columns:
        ch_stats = ch_stats.merge(
            type_pct[[vt]].rename(columns={vt: f'{vt.lower()}_pct'}),
            left_on='channel_id', right_index=True, how='left'
        )

# Publishing frequency
df1_dated = df1[df1['publish_date'].notna()]
ch_dates = df1_dated.groupby('channel_id').agg(
    first_pub=('publish_date', 'min'),
    last_pub=('publish_date', 'max'),
).reset_index()
ch_dates['days_active'] = (ch_dates['last_pub'] - ch_dates['first_pub']).dt.days + 1
ch_stats = ch_stats.merge(ch_dates[['channel_id', 'days_active']], on='channel_id', how='left')
ch_stats['pub_freq'] = ch_stats['n_videos'] / (ch_stats['days_active'] / 7)

# Classify channels
ch_stats['archetype'] = 'Other'
ch_stats.loc[ch_stats.get('short_pct', pd.Series(dtype=float)).fillna(0) > 0.7, 'archetype'] = 'Shorts Machine'
ch_stats.loc[ch_stats.get('production_pct', pd.Series(dtype=float)).fillna(0) > 0.7, 'archetype'] = 'Production Studio'
ch_stats.loc[ch_stats.get('story_pct', pd.Series(dtype=float)).fillna(0) > 0.7, 'archetype'] = 'Snapchat Native'
ch_stats.loc[ch_stats.get('live_pct', pd.Series(dtype=float)).fillna(0) > 0.5, 'archetype'] = 'Live Heavy'

# Mixed format channels
mixed_mask = ch_stats['archetype'] == 'Other'
for col in ['short_pct', 'production_pct', 'story_pct', 'live_pct']:
    if col in ch_stats.columns:
        mixed_mask &= ch_stats[col].fillna(0) < 0.7
ch_stats.loc[mixed_mask, 'archetype'] = 'Mixed'

arch_stats = ch_stats.groupby('archetype').agg(
    n_channels=('channel_id', 'count'),
    avg_revenue_per_video=('avg_revenue', 'mean'),
    avg_total_revenue=('total_revenue', 'mean'),
    avg_cpm=('avg_cpm', 'mean'),
    avg_pub_freq=('pub_freq', 'mean'),
    avg_videos=('n_videos', 'mean'),
).round(2)
print("\nChannel Archetypes:")
print(arch_stats.to_string())

# ============================================================
# 3. RETENTION PATTERNS — What makes content "stick"?
# ============================================================
print("\n\n" + "=" * 70)
print("3. RETENTION DEEP DIVE — 7d, 30d, lifetime views patterns")
print("=" * 70)

df1_ret = df1[(df1['first_7d_views'].notna()) & (df1['first_30d_views'].notna()) & (df1['total_views'] > 10)].copy()
df1_ret['pct_7d'] = df1_ret['first_7d_views'] / df1_ret['total_views']
df1_ret['pct_30d'] = df1_ret['first_30d_views'] / df1_ret['total_views']
df1_ret['pct_post30d'] = 1 - df1_ret['pct_30d']

# By platform × format
print("\nViews distribution by period:")
for plat in ['YouTube', 'Facebook', 'Snapchat']:
    sub = df1_ret[df1_ret['platform'] == plat]
    if len(sub) > 10:
        print(f"\n  {plat}:")
        for vt in sub['video_type'].unique():
            vt_sub = sub[sub['video_type'] == vt]
            if len(vt_sub) > 5:
                print(f"    {vt:12s} (n={len(vt_sub):4d}): "
                      f"7d={vt_sub['pct_7d'].median():5.1%}, "
                      f"30d={vt_sub['pct_30d'].median():5.1%}, "
                      f"post-30d={vt_sub['pct_post30d'].median():5.1%}, "
                      f"avg_rev=${vt_sub['revenue_proxy'].mean():.2f}")

# Videos with strong post-30d tail
tail_strong = df1_ret[df1_ret['pct_post30d'] > 0.3]
print(f"\n\nVideos with >30% views after day 30: {len(tail_strong)} ({len(tail_strong)/len(df1_ret)*100:.1f}%)")
print(f"  Avg revenue: ${tail_strong['revenue_proxy'].mean():.2f} vs ${df1_ret['revenue_proxy'].mean():.2f} overall")
print(f"  By platform: {tail_strong['platform'].value_counts().to_dict()}")
if 'video_type' in tail_strong.columns:
    print(f"  By type: {tail_strong['video_type'].value_counts().to_dict()}")

# Duration of tail-strong videos
tail_dur = tail_strong['duration_seconds'].dropna()
overall_dur = df1_ret['duration_seconds'].dropna()
print(f"  Median duration: {tail_dur.median():.0f}s (vs {overall_dur.median():.0f}s overall)")

# ============================================================
# 4. SEASONALITY — Month-level patterns
# ============================================================
print("\n\n" + "=" * 70)
print("4. SEASONALITY — Monthly patterns")
print("=" * 70)

df1_month = df1[df1['publish_date'].notna()].copy()
df1_month['month'] = df1_month['publish_date'].dt.to_period('M')

month_stats = df1_month.groupby(['month', 'platform']).agg(
    n=('video_id', 'count'),
    avg_revenue=('revenue_proxy', 'mean'),
    total_revenue=('revenue_proxy', 'sum'),
    avg_views=('total_views', 'mean'),
).round(2)

print("\nMonthly revenue by platform:")
for plat in ['YouTube', 'Snapchat', 'Facebook']:
    sub = month_stats.xs(plat, level='platform') if plat in month_stats.index.get_level_values('platform') else None
    if sub is not None and len(sub) > 0:
        print(f"\n  {plat}:")
        for idx, row in sub.iterrows():
            print(f"    {idx}: {row['n']:4.0f} videos, ${row['avg_revenue']:.2f}/video, ${row['total_revenue']:,.0f} total")

# Month-over-month changes
print("\n\nMonth-over-month avg revenue changes:")
overall_monthly = df1_month.groupby('month')['revenue_proxy'].mean()
for i in range(1, len(overall_monthly)):
    prev = overall_monthly.iloc[i-1]
    curr = overall_monthly.iloc[i]
    if prev > 0:
        change = (curr / prev - 1) * 100
        print(f"  {overall_monthly.index[i]}: ${curr:.2f} ({change:+.1f}% vs prev)")

# ============================================================
# 5. CROSS-PLATFORM CONTENT JOURNEY
# ============================================================
print("\n\n" + "=" * 70)
print("5. CROSS-PLATFORM — Which content travels best?")
print("=" * 70)

df3_dedup = df3.drop_duplicates(subset=['video_id', 'content_original_id', 'platform'])
content_plats = df3_dedup.groupby('content_original_id')['platform'].apply(lambda x: sorted(set(x))).reset_index()
content_plats['n_platforms'] = content_plats['platform'].apply(len)
content_plats['combo'] = content_plats['platform'].apply(lambda x: '+'.join(x))

# Which combos perform best?
video_content = df3_dedup[['video_id', 'content_original_id', 'platform']].drop_duplicates(subset=['video_id', 'platform'])
video_n = video_content.merge(
    content_plats[['content_original_id', 'n_platforms', 'combo']],
    on='content_original_id', how='left'
).sort_values('n_platforms', ascending=False).drop_duplicates(subset=['video_id'])

df_xp = df1.merge(video_n[['video_id', 'content_original_id', 'n_platforms', 'combo']], on='video_id', how='inner')

# Performance by combo
multi = df_xp[df_xp['n_platforms'] >= 2]
combo_stats = multi.groupby('combo').agg(
    n_content=('content_original_id', 'nunique'),
    n_videos=('video_id', 'count'),
    avg_revenue=('revenue_proxy', 'mean'),
    avg_views=('total_views', 'mean'),
    total_revenue=('revenue_proxy', 'sum'),
).round(2)
combo_stats = combo_stats.sort_values('avg_revenue', ascending=False)
print("\nMulti-platform combos:")
print(combo_stats.to_string())

# Delayed vs same-day cross-posting
multi_content = df_xp[df_xp['n_platforms'] >= 2].copy()
pub_dates = multi_content.groupby(['content_original_id', 'platform'])['publish_date'].first().unstack()
if pub_dates.shape[1] >= 2:
    # Calculate delay between platforms
    cols = pub_dates.columns.tolist()
    for i in range(len(cols)):
        for j in range(i+1, len(cols)):
            pair = pub_dates[[cols[i], cols[j]]].dropna()
            if len(pair) > 5:
                delay = (pair[cols[j]] - pair[cols[i]]).dt.days.abs()
                print(f"\n  Delay {cols[i]}↔{cols[j]}: median={delay.median():.0f} days, mean={delay.mean():.0f} days (n={len(pair)})")

# ============================================================
# 6. ENGAGEMENT QUALITY — Likes vs Comments vs Shares
# ============================================================
print("\n\n" + "=" * 70)
print("6. ENGAGEMENT QUALITY — Which type of engagement matters?")
print("=" * 70)

# Normalize engagement metrics
yt_eng = df1[(df1['platform'] == 'YouTube') & (df1['total_views'] > 100)].copy()
yt_eng['like_rate'] = yt_eng['likes'] / yt_eng['total_views'] * 100
yt_eng['comment_rate'] = yt_eng['comments'] / yt_eng['total_views'] * 100
yt_eng['share_rate'] = yt_eng['shares'] / yt_eng['total_views'] * 100
yt_eng['dislike_rate'] = yt_eng['dislikes'] / yt_eng['total_views'] * 100

print("\nNormalized engagement rates vs revenue (YouTube, views>100):")
for col in ['like_rate', 'comment_rate', 'share_rate', 'dislike_rate', 'engagement_rate']:
    valid = yt_eng[[col, 'revenue_proxy']].dropna()
    valid = valid[valid[col].between(valid[col].quantile(0.01), valid[col].quantile(0.99))]
    if len(valid) > 20:
        r, p = stats.spearmanr(valid[col], valid['revenue_proxy'])
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'n.s.'
        print(f"  {col:20s}: r={r:+.3f} {sig} (n={len(valid)})")

# By format
for vt in ['Short', 'Production']:
    sub = yt_eng[yt_eng['video_type'] == vt]
    if len(sub) > 20:
        print(f"\n  {vt}:")
        for col in ['like_rate', 'share_rate', 'engagement_rate']:
            valid = sub[[col, 'revenue_proxy']].dropna()
            if len(valid) > 10:
                r, p = stats.spearmanr(valid[col], valid['revenue_proxy'])
                sig = '***' if p < 0.001 else 'n.s.'
                print(f"    {col:20s}: r={r:+.3f} {sig}")

# ============================================================
# 7. AD MONETIZATION EFFICIENCY
# ============================================================
print("\n\n" + "=" * 70)
print("7. AD MONETIZATION — Where are ads most efficient?")
print("=" * 70)

df1_ad = df1[(df1['ad_impressions'] > 0) & (df1['total_views'] > 0)].copy()
df1_ad['ad_per_view'] = df1_ad['ad_impressions'] / df1_ad['total_views']
df1_ad['revenue_per_ad'] = df1_ad['revenue_proxy'] / df1_ad['ad_impressions']

print("\nAd density and efficiency:")
for plat in ['YouTube', 'Snapchat']:
    sub = df1_ad[df1_ad['platform'] == plat]
    if len(sub) > 10:
        print(f"\n  {plat}:")
        print(f"    Ads/view: {sub['ad_per_view'].median():.3f} (median)")
        print(f"    Revenue/ad: ${sub['revenue_per_ad'].median():.4f} (median)")
        
        if plat == 'YouTube':
            for vt in ['Short', 'Production', 'Live']:
                vt_sub = sub[sub['video_type'] == vt]
                if len(vt_sub) > 5:
                    print(f"    {vt}: ads/view={vt_sub['ad_per_view'].median():.3f}, "
                          f"rev/ad=${vt_sub['revenue_per_ad'].median():.4f} (n={len(vt_sub)})")

# Ad density by duration bucket
yt_ad = df1_ad[(df1_ad['platform'] == 'YouTube') & df1_ad['duration_seconds'].notna()].copy()
yt_ad['dur_bucket'] = pd.cut(yt_ad['duration_seconds'],
                              bins=[0, 60, 480, 600, 900, 1800, 99999],
                              labels=['<1m', '1-8m', '8-10m', '10-15m', '15-30m', '30m+'])
ad_by_dur = yt_ad.groupby('dur_bucket', observed=True).agg(
    n=('video_id', 'count'),
    avg_ads_per_view=('ad_per_view', 'mean'),
    avg_revenue=('revenue_proxy', 'mean'),
).round(4)
print("\n\nAd density by duration (YouTube):")
print(ad_by_dur.to_string())

# ============================================================
# 8. WATCH TIME vs VIEWS — Which to optimize?
# ============================================================
print("\n\n" + "=" * 70)
print("8. WATCH TIME vs VIEWS — Revenue attribution")
print("=" * 70)

for plat in ['YouTube', 'Facebook', 'Snapchat']:
    sub = df1[(df1['platform'] == plat) & (df1['total_views'] > 0) & (df1['watch_time_minutes'] > 0)]
    r_views, _ = stats.spearmanr(sub['total_views'], sub['revenue_proxy'])
    r_wt, _ = stats.spearmanr(sub['watch_time_minutes'], sub['revenue_proxy'])
    print(f"\n  {plat}: views↔revenue r={r_views:+.3f}, watch_time↔revenue r={r_wt:+.3f}")
    print(f"    → {'Watch time' if r_wt > r_views else 'Views'} is better predictor")

# Revenue per 1000 views vs revenue per 1000 watch time minutes
print("\n\nRevenue efficiency comparison:")
for plat in ['YouTube', 'Facebook', 'Snapchat']:
    sub = df1[(df1['platform'] == plat) & (df1['revenue_proxy'] > 0)]
    rev_per_1k_views = sub['revenue_proxy'].sum() / sub['total_views'].sum() * 1000
    rev_per_1k_wt = sub['revenue_proxy'].sum() / sub['watch_time_minutes'].sum() * 1000
    print(f"  {plat}: ${rev_per_1k_views:.3f}/1K views, ${rev_per_1k_wt:.3f}/1K watch-min")

# ============================================================
# 9. CONTENT LIFECYCLE VELOCITY — How fast do videos peak?
# ============================================================
print("\n\n" + "=" * 70)
print("9. CONTENT LIFECYCLE VELOCITY — Peak timing")
print("=" * 70)

# Cohort data: when does content peak?
d2_wide = df2.groupby(['video_id', 'months_since_publish'])['views'].sum().unstack(fill_value=0)
d2_wide_pct = d2_wide.div(d2_wide.sum(axis=1), axis=0)

# Peak month
d2_wide['peak_month'] = d2_wide.iloc[:, :7].idxmax(axis=1)
peak_dist = d2_wide['peak_month'].value_counts().sort_index()
print("\nPeak month distribution:")
for m, cnt in peak_dist.items():
    pct = cnt / len(d2_wide) * 100
    print(f"  Month {m}: {cnt} videos ({pct:.1f}%)")

# Videos that peak AFTER month 0
late_peak = d2_wide[d2_wide['peak_month'] > 0]
print(f"\nVideos peaking after month 0: {len(late_peak)} ({len(late_peak)/len(d2_wide)*100:.1f}%)")

# Merge with df1 to see what they look like
late_peak_merged = late_peak.reset_index().merge(df1[['video_id', 'platform', 'video_type', 'duration_seconds', 'revenue_proxy']], on='video_id')
print(f"\n  Late-peaking by platform: {late_peak_merged['platform'].value_counts().to_dict()}")
print(f"  Late-peaking by type: {late_peak_merged['video_type'].value_counts().to_dict()}")
print(f"  Late-peaking avg revenue: ${late_peak_merged['revenue_proxy'].mean():.2f}")
print(f"  Overall avg revenue: ${df1['revenue_proxy'].mean():.2f}")

# ============================================================
# 10. PRACTICAL RECOMMENDATIONS MATRIX
# ============================================================
print("\n\n" + "=" * 70)
print("10. SUMMARY — Action Items by Impact")
print("=" * 70)

print("""
HIGH IMPACT + EASY:
1. Replace engagement_rate KPI with watch_time_minutes
2. 7-day evergreen detection rule (AUC=0.937)
3. Focus cross-posting on Facebook↔Snapchat

HIGH IMPACT + HARD:
4. Shift 10% Shorts → Production (8-16 min sweet spot)
5. Diversify Snapchat revenue (reduce channel_621 dependence)
6. Build evergreen prediction model with duration + 7d features

MEDIUM IMPACT:
7. Optimize publishing frequency to 3-7/week
8. Study channel_10846 (65.9% evergreen rate) for best practices
9. Experiment with morning publishing for YouTube Productions

LOW IMPACT (skip for now):
10. Day-of-week optimization (minimal signal)
11. Dislike ratio (no effect on revenue)
""")

print("=== PHASE 2 RESEARCH COMPLETE ===")
