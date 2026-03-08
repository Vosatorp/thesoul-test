# TheSoul Group — Content Analytics

Test assignment for Applied AI Engineer. Analysis of 11,500 videos across YouTube, Facebook, and Snapchat.

**Author:** Dmitry Protasov | **Date:** March 2026

## Deliverables

| File | Description |
|------|-------------|
| `thesoul_analysis_v2.ipynb` | Main analysis notebook (runs end-to-end) |
| `presentation.md` | Executive summary (English) |
| `presentation_ru.md` | Executive summary (Russian) |
| `data/` | 3 CSV datasets + description |

## Quick Start

```bash
pip install pandas numpy scipy scikit-learn matplotlib seaborn
jupyter notebook thesoul_analysis_v2.ipynb
```

## Key Insights

### 1. Shorts Are More Efficient Than They Look
Shorts pay 35× less per view than Production videos — but produce 8.6× more revenue per hour of content created. Using duration as a production cost proxy, Shorts earn $167/hour vs $19/hour for Production. Longer Shorts (45-60s) earn 3.6× more than the dominant 15-30s format. Sunday publishing adds +159%. The 8-15 minute Production format remains the highest-ROI segment at 12.4× average efficiency.

### 2. Evergreen Content = Compound Returns
10.8% of videos keep growing after month 1 and generate 44.3% of tracked revenue. K-Means clustering reveals 3 content archetypes: Spike & Die (79%), Moderate Decay (12%), Evergreen (8.5%). A Gradient Boosting model (AUC = 0.87, cross-validated) flags evergreen candidates 7 days after publication.

### 3. Cross-Platform Publishing Doubles Views
Multi-platform content gets +100% views on Facebook and +134% on Snapchat (Mann-Whitney, p < 0.0001). Only 4% of content is cross-posted. Best combination: Facebook + Snapchat ($2,671 mean revenue per content piece).

### 4. Engagement Anti-Predicts Revenue
Engagement rate negatively correlates with revenue (Spearman ρ = -0.24) due to Simpson's paradox: Shorts dominate engagement metrics but have near-zero CPM. Watch time (ρ = +0.65) is the correct primary KPI. Within a single format, the paradox disappears.

### 5. Revenue Concentration Risk
One Snapchat channel = 46.4% of platform revenue (Gini = 0.73). Monitor and diversify.

## ML Model

| Component | Detail |
|-----------|--------|
| Algorithm | Gradient Boosting (200 trees, max_depth=4) |
| Features | 8 (view share 7d, watch time share 7d, duration, engagement, CPM, etc.) |
| AUC (5-fold CV) | **0.87** |
| Top feature | Share of views in first 7 days (66.6% importance) |
| Practical use | Flag evergreen candidates on day 7 → invest in promotion |

## Data

| Dataset | Rows | Description |
|---------|------|-------------|
| `dataset_1_video_performance.csv` | 11,500 | Views, CPM, engagement, retention |
| `dataset_2_cohort_analysis.csv` | 31,589 | Monthly views/watch time by cohort |
| `dataset_3_cross_platform.csv` | 26,030 | Cross-platform content mapping |

See `data/datasets_description.md` for full data dictionary.

## Methodology

- **Revenue proxy:** `total_views × estimated_cpm / 1000`
- **Evergreen definition:** >50% of total views arrive after month 0
- **Cross-platform matching:** via `content_original_id` in dataset 3
- **Statistical tests:** Mann-Whitney U (non-parametric), Spearman rank correlations
- **Clustering:** K-Means (k=3) on lifecycle retention features
- **ML:** Gradient Boosting with stratified 5-fold cross-validation

---

*Dmitry Protasov | March 2026*
