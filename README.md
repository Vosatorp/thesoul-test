# TheSoul Group — Content Analytics

Test assignment for Applied AI Engineer / Data Scientist.
Analysis of 11,500 videos across YouTube, Facebook, and Snapchat.

**Author:** Dmitry Protasov | **Date:** March 2026

## Structure

| File | Description |
|------|-------------|
| `thesoul_analysis_v2.ipynb` | Main analysis notebook (runs end-to-end) |
| `presentation_ru.md` | Presentation with findings (Marp format) |
| `create_figures.py` | Script to regenerate all 14 charts |
| `figures/` | Charts used in the presentation |
| `data/` | 3 CSV datasets + description |
| `requirements.txt` | Python dependencies |

## Quick Start

```bash
pip install -r requirements.txt
jupyter notebook thesoul_analysis_v2.ipynb
```

To regenerate charts:
```bash
python create_figures.py
```

## Key Insights

### 1. Shorts Revenue Efficiency
Shorts pay 35× less CPM than Production — but produce 8.6× more revenue per hour of content. Longer Shorts (45-60s) earn 3.6× more per video than 15-30s.

### 2. Evergreen Content = Compound Returns
~9% of videos keep growing after month 1, generating disproportionate revenue. A Gradient Boosting model (AUC = 0.71, no data leakage) flags evergreen candidates 7 days after publication.

### 3. Cross-Platform Association
Multi-platform content is associated with higher views (+100% Facebook, +134% Snapchat), though selection bias cannot be ruled out without A/B testing.

### 4. Engagement Anti-Predicts Revenue
Simpson's paradox: engagement rate negatively correlates with revenue when mixing formats. Watch time (ρ = +0.65) is the correct KPI.

### 5. Revenue Concentration Risk
One Snapchat channel = 46% of platform revenue (Gini = 0.73).

### 6. Channel Format-Mix Drives Revenue
Top YouTube channels earn 130× more per video — driven by Production-heavy format mix (63% vs 18%), not publishing frequency.

## Data

| Dataset | Rows | Description |
|---------|------|-------------|
| `dataset_1_video_performance.csv` | 11,500 | Views, CPM, engagement, retention |
| `dataset_2_cohort_analysis.csv` | 31,589 | Monthly views/watch time by cohort |
| `dataset_3_cross_platform.csv` | 26,030 | Cross-platform content mapping |

---

*Dmitry Protasov | March 2026*
