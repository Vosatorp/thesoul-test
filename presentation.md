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

**Tools:** Python, pandas, scipy, matplotlib/seaborn

---

# Insight 1: The Short-Form Monetization Trap

## "Your best-performing format is your worst-earning one"

| Metric | YouTube Shorts | YouTube Production | Gap |
|--------|---------------|-------------------|-----|
| **CPM** | $0.06 | $1.94 | **35×** |
| **Revenue/video** | $1.27 | $9.68 | **7.6×** |
| Retention (avg % viewed) | 105% | 20% | — |
| Share of content | 74.4% | 20.6% | — |
| Views after 7 days | 12.0% | 23.7% | 2× |

**The trap:** Shorts dominate engagement dashboards but generate only 31% of YouTube revenue despite being 74% of content. Production videos >8 min unlock mid-roll ads → **35× CPM jump**.

**Recommendation:** Reallocate 10% of Shorts capacity → Production (>8 min).
Conservative (3:1 effort ratio): **+$1,197 net revenue** (+18% of Shorts revenue).

---

# Insight 2: Evergreen Content = Compound Returns

## 8.5% of videos generate 54.5% of tracked revenue

| Metric | Evergreen (8.5%) | Normal (91.5%) |
|--------|-----------------|----------------|
| **Lifetime revenue/video** | **$48.59** | $3.69 |
| Revenue after month 0 | 85.3% | 24.9% |
| Median duration | 13 min | 51 sec |

**Key insight:** Most content "dies" in month 1 (median retention: 0.2% of month 0). Evergreen videos keep generating revenue for 6+ months — **85% of their value comes after the first month**.

**Platform effect:** YouTube retains content **2.7× longer** than Facebook (month 1) and **32× longer** by month 3. YouTube's recommendation algorithm is the key evergreen driver.

**Recommendation:** Introduce "Evergreen Score" KPI (m3/m0 retention). Target: 8.5% → 15% evergreen share. Study top channels (channel_5998: 80% evergreen rate).

---

# Insight 3: Cross-Platform Synergy

## Multi-platform publishing amplifies — not cannibalizes — performance

| Platform | Single-platform | Multi-platform | Lift | p-value |
|----------|----------------|----------------|------|---------|
| **Facebook** | 11,764 views | 16,048 views | **+36%** | 0.0001 |
| **Snapchat** | 42,789 views | 56,177 views | **+31%** | 0.001 |
| YouTube | 2,297 views | 2,215 views | -4% | 0.86 (n.s.) |

**96% of content** is published on just 1 platform — only 4% is cross-posted.

**Not selection bias:** Same-channel comparison confirms the effect. Mann-Whitney U tests significant at p < 0.01 for Facebook and Snapchat.

**Watch time lift:** +58% on Facebook, +52% on Snapchat — deep engagement, not just clicks.

**Recommendation:** Scale cross-posting from 4% → 20%. Priority: Facebook ↔ Snapchat.
Conservative estimate: **+80M incremental views** (+9.5%) at zero additional production cost.

---

# What's Next

## Given more time and data, I'd investigate:

**Causal Inference**
- A/B test for cross-posting to isolate causal effect from selection bias
- Instrumental variable approach using platform-specific publishing constraints

**Revenue Optimization**
- Per-channel recommendation engine: optimal Shorts/Production mix
- True ROI with production cost data (the 7.6× revenue advantage may shift)

**Predictive Models**
- Evergreen content prediction from early signals (current: ROC AUC 0.66)
- Title/thumbnail NLP for topic-level evergreen patterns
- Automated scoring pipeline to prioritize promotion of likely-evergreen uploads

**Strategic Questions**
- Is the Shorts CPM gap narrowing as YouTube monetization matures?
- What's the actual audience overlap between Facebook and Snapchat?
- Seasonal effects on evergreen performance and cross-platform synergy

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

## Lifecycle Distribution (6,883 videos with cohort data)

| Segment | Share | Avg Revenue | Post-Month-0 Revenue |
|---------|-------|-------------|---------------------|
| Flash burn (m1/m0 < 1%) | 41.6% | $0.87 | 0.4% |
| Fast decay (1-5%) | 22.7% | $1.39 | 3.3% |
| Moderate (5-20%) | 16.0% | $2.49 | 11.5% |
| Sustained (20-50%) | 8.8% | $7.56 | 27.7% |
| Evergreen (>50%) | 10.6% | $13.47 | 60.9% |

---

# Limitations

1. **Snapchat dominates revenue** (91.7%) due to high views × moderate CPM — insights about YouTube formats have smaller absolute impact on total revenue

2. **No production cost data** — can't compute true ROI per format. The 7.6× revenue advantage of Production over Shorts may shrink once production effort is factored in

3. **Cross-platform correlation ≠ causation** — matched comparison and statistical tests reduce but don't eliminate selection bias. A proper A/B test is needed for causal claims

4. **Cohort data limited to 6-7 months** — true evergreen value is likely higher than estimated, as some content continues generating views well beyond the observation window

---

*Dmitry Protasov | TheSoul Group Applied AI Engineer Test Assignment | March 2026*
