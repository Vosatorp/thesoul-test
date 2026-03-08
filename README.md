# TheSoul Group — Content Analytics

Test assignment for Applied AI Engineer. Analysis of 11,500 videos across YouTube, Facebook, and Snapchat.

**Author:** Dmitry Protasov | **Date:** March 2026

## Deliverables

| File | Description |
|------|-------------|
| `thesoul_analysis_v2.ipynb` | Main analysis notebook (run end-to-end) |
| `presentation.md` | Executive summary (English) |
| `presentation_ru.md` | Executive summary (Russian) |
| `data/` | 3 CSV datasets + description |

## Quick Start

```bash
pip install -r requirements.txt
jupyter notebook thesoul_analysis_v2.ipynb
```

## Key Insights

### 1. The Short-Form Monetization Trap
YouTube Shorts have ~105% retention but 35× lower CPM than Production videos. Each Production video earns 7.6× more revenue despite looking worse on engagement dashboards. **Action:** reallocate 10% Shorts → Production 8–15 min (+$1,019).

### 2. Evergreen Content = Compound Returns
8.5% of videos are "evergreen" but generate 54.5% of tracked revenue. 85% of their value comes after the first month. A multi-feature ML model (Gradient Boosting, 8 features, AUC = 0.93) identifies evergreen candidates within 7 days — catching 99% of evergreen with near-zero false positives.

### 3. Cross-Platform Synergy
Multi-platform content gets +36% views on Facebook and +31% on Snapchat (Mann-Whitney, p < 0.01). Only 4% of content is cross-posted — scaling to 20% yields +40M additional views.

### 4. Engagement Anti-Predicts Revenue
Engagement rate is negatively correlated with revenue (r = −0.24). Only 13.4% of top-engagement videos are also top-revenue (worse than random). Watch time (r = +0.65) is the correct primary KPI.

### 5. Revenue Concentration Risk
One Snapchat channel accounts for 46.4% of platform revenue (Gini = 0.73). Diversification and best-practice extraction recommended.

## ML Model

| Component | Detail |
|-----------|--------|
| Algorithm | Gradient Boosting (200 trees, max_depth=4) |
| Features | 8 (view share 7d, watch time share 7d, duration, engagement rate, etc.) |
| AUC (5-fold CV) | **0.93** |
| Recall | 99% |
| Business impact | Each missed evergreen ≈ $48.59 lost promotion value |

## What's Next

- **SMM hypothesis:** Does human SMM (thumbnails, titles) outperform auto-posting? Proposed: propensity score matching + A/B test
- **Automation vision:** Notebook → production pipeline (data ingestion → ML scoring → anomaly detection → Slack alerts → AI agent insights)
- **Further research:** causal inference for cross-platform, NLP on titles, audience overlap, seasonal CPM trends

## Data

| Dataset | Rows | Description |
|---------|------|-------------|
| `dataset_1_video_performance.csv` | 11,500 | Views, CPM, engagement, retention |
| `dataset_2_cohort_analysis.csv` | 31,589 | Monthly views/watch time by cohort |
| `dataset_3_cross_platform.csv` | 26,030 | Cross-platform content mapping |

See `data/datasets_description.md` for full data dictionary.

## Methodology

- **Revenue proxy:** `total_views × estimated_cpm / 1000`
- **Evergreen classification:** month 3 views > 10% of month 0 views
- **Cross-platform matching:** via `content_original_id` in dataset 3
- **Statistical tests:** Mann-Whitney U (non-parametric), Spearman correlations
- **ML model:** Gradient Boosting with 5-fold cross-validation

---

*Dmitry Protasov | March 2026*
