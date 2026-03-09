# Audit Report — TheSoul Group Presentation

**Date:** 2025-07-13  
**Scope:** Quick fixes for charts and presentation accuracy

---

## Fix 1: fig_06_shorts_by_duration.png — ✅ Already Correct

**Expected issue:** Chart shows TOTAL revenue instead of MEAN revenue per video.  
**Finding:** Code already uses `.mean()` aggregation with `n=` count annotations and red highlight on 45-60s bucket. No change needed.

**Verified values:**
| Bucket | Mean Revenue | Count |
|--------|-------------|-------|
| 0-15s | $1.22 | 1,246 |
| 15-30s | $0.67 | 2,473 |
| 30-45s | $1.72 | 937 |
| 45-60s | $2.39 | 420 |
| 60-120s | $2.20 | 62 |

45-60s is visually the highest bar. Title "Sweet Spot at 45-60s" is supported.

---

## Fix 2: ML Model Data Leakage — ✅ FIXED

**Issue:** Model used 14 features including `first_30d_views/total_views`, `watch_time_30d/watch_time_minutes`, `total_views`, `engagement_rate` (cumulative), `likes`, `comments`, `shares`, `ad_impressions`, `estimated_cpm` — none of which are available on day 7.

**Fix applied:**
- Reduced to 6 features available on day 7:
  1. `first_7d_views` (absolute, not ratio)
  2. `watch_time_7d`
  3. `duration_seconds`
  4. `avg_view_duration_seconds`
  5. `avg_percentage_viewed`
  6. `video_type` (encoded)
- **AUC dropped: 0.87 → 0.71** (5-fold CV)
- Updated `presentation_ru.md` with new AUC, feature list, and honest framing
- Removed precision/recall table (no longer accurate with new model)
- Regenerated `fig_10_feature_importance.png`

**Files changed:**
- `create_figures.py` — fig_10 section rewritten
- `presentation_ru.md` — ML section updated

---

## Fix 3: All 14 Charts Review — ✅ Checked

| # | Chart | Aggregation | Correct? | Notes |
|---|-------|-------------|----------|-------|
| 01 | Revenue by Platform | sum | ✅ | Total revenue is correct for platform comparison |
| 02 | Format Mix | count (normalized) | ✅ | Share of videos, correct |
| 03 | CPM Box Plots | distribution | ✅ | Median annotated, outliers clipped at p99 |
| 04 | Duration Histogram | count | ✅ | Histogram, correct |
| 05 | Revenue per Hour | sum/sum (total rev / total hours) | ✅ | Efficiency metric, correct |
| 06 | Shorts by Duration | mean | ✅ | Mean revenue per video with n= counts |
| 07 | Production Duration Efficiency | ratio (rev share / content share) | ✅ | Efficiency index, correct |
| 08 | Lifecycle Curves | mean (view_share per cluster) | ✅ | Normalized per video, then averaged |
| 09 | Evergreen Revenue Share | sum (donut) | ✅ | Revenue share, correct metric |
| 10 | Feature Importance | model importance | ✅ | Fixed (day-7 features only) |
| 11 | Cross-Platform Boost | mean views | ✅ | With Mann-Whitney U p-values |
| 12 | Simpson's Paradox | scatter (individual) | ✅ | Raw data, correct |
| 13 | Correlation Heatmap | Spearman ρ | ✅ | Correct method for non-normal data |
| 14 | Lorenz Curve | cumulative sum | ✅ | Standard Lorenz with Gini coefficient |

**No additional issues found.**

---

## Fix 4: Key Numbers in Presentation — ✅ All Verified

| Claim | Recalculated | Match? |
|-------|-------------|--------|
| "$167/hr" for Shorts | $6,602.86 / 39.5 hrs = **$167/hr** | ✅ |
| "3.6 раза" (45-60s vs 15-30s) | $2.39 / $0.67 = **3.6×** | ✅ |
| "44.3% выручки" from evergreen | **44.3%** | ✅ |
| "10.8% видео" evergreen | **10.8%** | ✅ |
| "$10.56 avg rev" evergreen | **$10.56** | ✅ |
| "$1.61 avg rev" other | **$1.61** | ✅ |
| "8.5× more efficient" (Shorts) | $167 / $19 = **8.5×** | ✅ |

All numbers are accurate.

---

## Summary

| Fix | Status | Impact |
|-----|--------|--------|
| Fig 06: Mean revenue | ✅ Already correct | None needed |
| Fig 10: ML leakage | ✅ **Fixed** | AUC 0.87→0.71, honest model |
| Charts review | ✅ All correct | No issues found |
| Numbers verification | ✅ All match | No changes needed |
