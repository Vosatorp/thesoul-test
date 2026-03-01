# TheSoul Group — Content Analytics

Test assignment for Applied AI Engineer. Analysis of 11,500 videos across YouTube, Facebook, and Snapchat.

**Author:** Dmitry Protasov | **Date:** March 2026

## Deliverables

| File | Description |
|------|-------------|
| `thesoul_analysis.ipynb` | Main analysis notebook (run end-to-end) |
| `presentation.md` | 7-slide summary (Markdown, `---` separated) |
| `data/` | 3 CSV datasets + description |

## Quick Start

```bash
pip install -r requirements.txt
jupyter notebook thesoul_analysis.ipynb
```

## Key Insights

### 1. The Short-Form Monetization Trap
YouTube Shorts have ~105% retention but 35× lower CPM than Production videos. Each Production video earns 7.6× more revenue despite looking worse on engagement dashboards.

### 2. Evergreen Content = Compound Returns
8.5% of videos are "evergreen" but generate 54.5% of tracked revenue. 85% of their value comes after the first month.

### 3. Cross-Platform Synergy
Multi-platform content gets +36% views on Facebook and +31% on Snapchat. Only 4% of content is cross-posted today.

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
- **Statistical tests:** Mann-Whitney U (non-parametric)

---

*Dmitry Protasov | March 2026*
