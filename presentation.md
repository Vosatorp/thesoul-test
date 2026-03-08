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

**Analysis pipeline:**
1. EDA → identify structural patterns in CPM, retention, and platform differences
2. Revenue proxy modeling → `views × CPM / 1000` to estimate monetization
3. Cohort-based lifecycle analysis → classify evergreen vs viral-decay content
4. Cross-platform matched comparison → control for selection bias
5. ML-based evergreen predictor → multi-feature Gradient Boosting (AUC = 0.93)

**Tools:** Python, pandas, scipy, scikit-learn, matplotlib/seaborn

> **Note on platform focus:** Snapchat dominates total revenue (91.7%) through high volume × moderate CPM. However, YouTube and Facebook are where content strategy decisions are made: format optimization, evergreen lifecycle management, and cross-platform synergy. Snapchat revenue follows content strategy, not the other way around.

---

# Insight 1: The Short-Form Monetization Trap

## "Your best-performing format is your worst-earning one"

| Metric | YouTube Shorts | YouTube Production | Gap |
|--------|---------------|-------------------|-----|
| **CPM** | $0.06 | $1.94 | **35×** |
| **Revenue/video** | $1.27 | $9.68 | **7.6×** |
| Retention (avg % viewed) | 105% | 20% | — |
| Share of content | 74.4% | 20.6% | — |
| Share of YT revenue | 31% | 66% | **inverted** |

**The trap:** Shorts dominate engagement dashboards but generate only 31% of YouTube revenue despite being 74% of content. Production videos >8 min unlock mid-roll ads → **35× CPM jump**.

**Recommendation:** Reallocate 10% of Shorts capacity → Production (>8 min).
Conservative (3:1 effort ratio): **+$1,019 net revenue** (+15% of Shorts revenue).

---

# Insight 2: Evergreen Content = Compound Returns

## 8.5% of videos generate 54.5% of tracked revenue

| Metric | Evergreen (8.5%) | Normal (91.5%) |
|--------|-----------------|----------------|
| **Lifetime revenue/video** | **$48.59** | $3.69 |
| Revenue after month 0 | 85.3% | 24.9% |
| Median duration | 13 min | 51 sec |

**Key insight:** Most content "dies" in month 1 (median retention: 0.2% of month 0). Evergreen videos keep generating revenue for 6+ months — **85% of their value comes after the first month**.

**ML-powered early detection:** Multi-feature Gradient Boosting model (8 features, AUC = 0.93) identifies evergreen content within 7 days. Top predictors: watch time concentration in first 7 days (44.8%) and view share in first 7 days (25.7%). The model catches **99% of evergreen videos** with near-zero false positives.

**Business impact of false negatives:** Each missed evergreen video = ~$48.59 in unrealized promotion value.

**Recommendation:** Deploy 7-day ML predictor to auto-flag evergreen candidates. Introduce "Evergreen Score" KPI (m3/m0 retention). Target: 8.5% → 15% evergreen share (+$4,400 lifetime value).

---

# Insight 3: Cross-Platform Synergy

## Multi-platform publishing amplifies — not cannibalizes — performance

| Platform | Single-platform | Multi-platform | Lift | p-value |
|----------|----------------|----------------|------|---------|
| **Facebook** | 11,764 views | 16,048 views | **+36%** | 0.0001 |
| **Snapchat** | 42,789 views | 56,177 views | **+31%** | 0.001 |
| YouTube | 2,297 views | 2,215 views | −4% | 0.86 (n.s.) |

**96% of content** is published on just 1 platform — only 4% is cross-posted.

**Robust to selection bias check:** Same-channel comparison confirms the effect. Mann-Whitney U tests significant at p < 0.01 for Facebook and Snapchat.

**Watch time lift:** +58% on Facebook, +52% on Snapchat — deep engagement, not just clicks.

**Recommendation:** Scale cross-posting from 4% → 20%. Priority: Facebook ↔ Snapchat. Conservative estimate: **+40M additional views**. Start with 4%→10% pilot to validate.

---

# Insight 4: Engagement Anti-Predicts Revenue

## The metric most teams optimize is negatively correlated with revenue

| Metric | Correlation with Revenue | Signal |
|--------|------------------------|--------|
| **Watch time** | r ≈ +0.65 | ✅ Best engagement proxy |
| Total views | r ≈ +0.62 | ✅ Strong |
| Likes | r ≈ +0.37 | ⚠️ Weak positive |
| Shares | r ≈ +0.33 | ⚠️ Positive (drives distribution) |
| Engagement rate | r ≈ −0.24 | ❌ Anti-correlated |
| Avg % viewed | r ≈ −0.42 | ❌ Anti-correlated |

**Only 13.4%** of top-engagement videos are also top-revenue — worse than the 25% random baseline.

**Why?** Engagement rate is dominated by Shorts (105% retention, near-zero revenue). Optimizing for engagement steers the content mix toward Shorts — exactly the wrong direction for revenue.

**Recommendation:** Replace engagement rate with **watch time** as primary KPI. Track share rate as secondary signal (shares → distribution → revenue).

---

# What's Next

## SMM Hypothesis: Human vs. Automated Publishing

**The question:** Does human SMM (custom thumbnails, titles, descriptions) meaningfully outperform automated posting?

**Approach:** Propensity score matching + A/B test across comparable content batches (4 weeks). If human SMM adds >15% CPM lift → ROI on SMM headcount is clear. If <5% → automation frees significant resources across 250+ channels.

## Automation Vision

This analysis → **production pipeline:**

`Data Ingestion → ML Scoring → Anomaly Detection → Weekly Reports → Slack Alerts`

- **Day 7 auto-scoring:** ML model flags evergreen candidates → Slack alert to promote
- **AI agents:** LLM-powered weekly analysis → natural-language insights for content teams
- **MVP timeline:** 2 weeks (ingestion + alerts). Full system: 2-3 months.

## Further Research
- **Causal inference** for cross-platform effect (A/B test / instrumental variables)
- **Revenue-per-minute-of-effort** with production cost data
- **NLP on titles/thumbnails** to enhance evergreen prediction
- **Audience overlap** between platforms
- **Seasonal CPM trends** — is the Shorts gap narrowing?

---

# Technical Appendix

## Revenue Landscape

| Segment | Revenue Share | Content Share |
|---------|:------------:|:-------------:|
| Snapchat Stories | 91.7% | 13.0% |
| YouTube Production | 4.5% | 12.5% |
| YouTube Shorts | 2.1% | 45.3% |
| Facebook Production | 1.5% | 26.1% |
| YouTube Live | 0.2% | 3.0% |

## Limitations

1. **Snapchat dominates revenue** (91.7%) — YouTube/Facebook insights drive content strategy decisions, while Snapchat revenue follows content volume
2. **No production cost data** — can't compute true ROI per format
3. **Cross-platform correlation ≠ causation** — A/B test needed for causal claims
4. **Cohort data limited to 6-7 months** — true evergreen value is likely higher

---

*Dmitry Protasov | TheSoul Group Applied AI Engineer Test Assignment | March 2026*
