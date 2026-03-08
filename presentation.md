---
title: "TheSoul Group — Content Analytics Insights"
author: "Dmitry Protasov"
date: "March 2026"
---

# Approach

## Data & Methodology

**3 datasets analyzed:** 11,500 videos across YouTube, Facebook, Snapchat

| Dataset | Size | Purpose |
|---------|------|---------|
| Video Performance | 11,500 × 22 | Views, CPM, engagement, retention |
| Cohort Analysis | 31,589 rows | Monthly views for 6+ months post-publish |
| Cross-Platform | 26,030 rows | Content mapping across platforms |

**Revenue model:** `views × CPM / 1000` — platforms pay per 1,000 ad impressions. CPM varies 35× between formats (Shorts: $0.06, Production: $1.94 on YouTube) because longer videos support mid-roll ads.

**Platform focus:** Snapchat drives 91.7% of total revenue through volume. But content strategy decisions (format, duration, cross-posting timing) are made based on YouTube and Facebook data. Snapchat revenue follows content strategy.

---

# Insight 1: Shorts Are More Efficient Than They Look

## The standard view: Shorts pay 35× less per view. But that misses production cost.

| Format | Total Revenue | Content Hours | Revenue per Hour of Content |
|--------|:------------:|:-------------:|:---------------------------:|
| Shorts | $6,603 | 39 hours | **$167/hr** |
| Production | $13,967 | 718 hours | **$19/hr** |

Using content duration as a cost proxy, **Shorts generate 8.6× more revenue per unit of content produced.** A 30-minute Production video earns 7.6× more per video — but takes 66× longer to create.

At realistic production cost ratios (3-5× for Production vs Shorts), Production still wins on absolute ROI. But the breakeven is at 7.6× — above that, Shorts are more profitable. Actual production costs would refine this analysis.

## Which Shorts perform best?

Three clear patterns emerge:

**Duration:** Longer Shorts earn more. 45-60 second Shorts earn $2.39 avg vs $0.67 for the most common 15-30s format (3.6× more).

| Duration | Share | Mean Revenue | Mean Views |
|:--------:|:-----:|:------------:|:----------:|
| 0-15s | 24% | $1.22 | 34,815 |
| 15-30s | 48% | $0.67 | 22,786 |
| 30-45s | 18% | $1.72 | 64,114 |
| 45-60s | 8% | **$2.39** | **86,660** |
| 60-120s | 1% | $2.20 | 193,806 |

**Day of week:** Sunday Shorts earn +159% more ($2.66 vs $1.03).

**Channel concentration:** 10 channels produce 43% of Shorts and earn 82% of Shorts revenue. One channel (channel_9119) averages $23.51 per Short vs $1.27 overall.

## Production video sweet spot: 8-15 minutes

Videos at 8-10 minutes are **12.4× more efficient** than average — they unlock mid-roll ads while keeping attention. Only 0.7% of content but 8.2% of YouTube revenue. 10-15 minutes: 2.0% of content, 20.5% of revenue (10.5× efficiency).

**Recommendation:** Shift Shorts mix toward 45-60s, increase Sunday publishing, scale top channel practices. For Production, target 8-15 minute formats — the most underutilized high-ROI segment.

---

# Insight 2: Evergreen Content = Compound Returns

## 10.8% of videos generate 44.3% of tracked revenue — and keep growing

| Metric | Evergreen (10.8%) | Normal (89.2%) |
|--------|:-----------------:|:--------------:|
| Mean revenue | $10.56 | $1.61 |
| Revenue share | 44.3% | 55.7% |
| Views after month 0 | 84% | 6% |

84% of evergreen views arrive AFTER the first month. This is compound returns in content — revenue keeps flowing for 6+ months.

## Content lifecycle clusters (K-Means, k=3)

| Cluster | Share | Revenue Share | Views After M0 | Profile |
|---------|:-----:|:------------:|:--------------:|---------|
| Spike & Die | 79.2% | 41.5% | 2.8% | Peak in week 1, then silence |
| Moderate Decay | 12.4% | 25.2% | 36.3% | Gradual decline over 2-3 months |
| Evergreen | 8.5% | 33.3% | 91.4% | Steady views for 6+ months |

## ML predictor: flagging evergreen content on day 7

Gradient Boosting (8 features available at day 7). **AUC = 0.87 (5-fold cross-validation).**

| Threshold | Precision | Recall | Videos Flagged |
|:---------:|:---------:|:------:|:--------------:|
| 0.1 | 50% | 69% | 837 |
| 0.2 | 61% | 63% | 615 |
| 0.3 | 67% | 59% | 535 |
| 0.5 | 75% | 54% | 431 |

Top feature: share of views in first 7 days (66.6% importance). If a video keeps accumulating views past day 7 instead of front-loading — it's likely evergreen.

**Practical application:** Video published 7 days ago → model scores probability 0.7 → flag as evergreen candidate → invest in promotion.

**What's needed next:** promotion spend data, organic vs paid traffic split, A/B test (promote flagged vs control, 4 weeks).

**Proposed KPI:** Evergreen Score = month 3 views / month 0 views. Target: grow evergreen share from 8.5% to 15%.

---

# Insight 3: Cross-Platform Publishing Doubles Views

## 96% of content is single-platform. The 4% that's cross-posted gets dramatically more views.

| Platform | Single-platform | Multi-platform | Lift | p-value |
|----------|:--------------:|:--------------:|:----:|:-------:|
| Facebook | 63,736 views | 127,373 views | **+100%** | < 0.0001 |
| Snapchat | 927,574 views | 2,172,797 views | **+134%** | < 0.0001 |
| YouTube | 12,131 views | 5,395 views | -56% | 0.18 (n.s.) |

This isn't cannibalization — Facebook and Snapchat audiences barely overlap. Publishing on a second platform adds new viewers.

YouTube shows no effect — likely because YouTube's algorithm independently determines distribution, and cross-platform traffic doesn't influence ranking.

**Best combination:** Facebook + Snapchat ($2,671 combined revenue per content piece, 238 examples). Mean delay between first and second publication: 87 days.

**Recommendation:** Scale cross-posting from 4% to 20%. Start with 4%→10% pilot on Facebook↔Snapchat. Measure view and revenue uplift, then run A/B test for causal confirmation (correlation ≠ causation).

---

# Insight 4: Engagement Anti-Predicts Revenue

## The metric most teams optimize is negatively correlated with revenue

**Spearman correlations with revenue (all platforms):**

| Metric | Correlation | Signal |
|--------|:----------:|--------|
| Watch time | +0.65 | Best revenue predictor |
| Total views | +0.62 | Strong |
| Likes | +0.45 | Moderate |
| Shares | +0.41 | Moderate (drives distribution) |
| Comments | +0.29 | Weak |
| Engagement rate | **-0.24** | Negative |
| Avg % viewed | **-0.39** | Negative |

Only 13.4% of top-engagement videos are also top-revenue — worse than the 25% random baseline.

## Why this happens (Simpson's paradox)

1. Shorts have highest engagement: 105% retention (viewers rewatch), engagement rate 1.41
2. Shorts have near-zero CPM: $0.06, mean revenue $1.27
3. Production videos: low engagement (20% retention), but 35× higher CPM ($1.94)

Mixing formats → high engagement signals "probably a Short" → low revenue.

**Within a single format, the paradox disappears.** Among Production videos, engagement positively correlates with revenue (ρ = +0.16).

**Recommendation:** Replace engagement rate with watch time as primary KPI. Don't compare engagement across Shorts and Production — they're different universes. Among engagement sub-metrics, track shares (drives distribution and revenue).

---

# Revenue Concentration Risk

46.4% of Snapchat revenue comes from one channel (channel_621). Gini coefficient = 0.73.

| Channel | Revenue | Share | Videos |
|---------|--------:|:-----:|:------:|
| channel_621 | $131K | 46.4% | 94 |
| channel_761 | $31K | 10.9% | 43 |
| channel_1367 | $22K | 7.6% | 44 |
| channel_438 | $13K | 4.4% | 46 |
| channel_190 | $9K | 3.2% | 41 |
| Other 27 | $78K | 27.5% | — |

**Recommendation:** Monitor channel_621 health, extract best practices from top 5, long-term target: no channel > 25% of platform revenue.

---

# Action Plan

**This Week:**
1. Replace engagement rate with watch time in dashboards
2. Deploy 7-day ML scoring for evergreen content detection
3. Start tracking cross-posting rate as operational metric (current: 4%)

**1-3 Months:**
4. Shift Shorts mix toward 45-60s format, increase Sunday publishing
5. Scale Facebook↔Snapchat cross-posting to 10%, measure impact
6. Introduce Evergreen Score KPI

**3-6 Months:**
7. A/B test ML-driven promotion (flagged vs control)
8. Reduce Snapchat revenue concentration (target: max 25% per channel)
9. Test SMM hypothesis: manual publishing vs automated across 250+ channels

---

# What's Next

## SMM Hypothesis: Human vs Automated Publishing
250+ channels, key question: does manual SMM meaningfully outperform automated posting?
Test via propensity score matching + 4-week A/B test. If >15% CPM lift → keep SMM teams. If <5% → automate.

## From One-Time Analysis to Production Pipeline
Automated system: ML scoring on day 7 → Slack alerts → anomaly detection → weekly reports.
MVP: 2 weeks. Full system: 2-3 months.

## Data Gaps to Fill
- Promotion spend per video (true ROI of evergreen promotion)
- SMM method labels (human vs automated)
- Audience demographics (content × audience fit)
- Production cost estimates (validate Shorts ROI with real costs)

---

*Dmitry Protasov | TheSoul Group Applied AI Engineer Test Assignment | March 2026*
