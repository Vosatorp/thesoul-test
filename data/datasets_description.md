# Test Datasets

All three datasets share the same `video_id` pool (~10,000+ videos across 3 platforms).
All metrics are real data from production QVDs. Only IDs are anonymized.

---

## Dataset 1 — Video Performance (`dataset_1_video_performance.csv`)

| Field | Description |
|-------|-------------|
| `video_id` | Anonymized video ID (`vid_000001`, …) |
| `channel_id` | Anonymized channel/publisher ID (`channel_001`, …) |
| `platform` | YouTube, Facebook, or Snapchat |
| `publish_date` | Publication date |
| `publish_hour` | Publication hour |
| `duration_seconds` | Video/story duration in seconds |
| `video_type` | Short / Production / Live / Story |
| `total_views` | Lifetime views |
| `first_7d_views` | Views within the first 7 days (YouTube, Facebook) |
| `first_30d_views` | Views within the first 30 days (YouTube, Facebook) |
| `watch_time_minutes` | Lifetime watch time in minutes |
| `watch_time_7d` | Watch time within the first 7 days (YouTube) |
| `watch_time_30d` | Watch time within the first 30 days (YouTube) |
| `likes` | Lifetime likes (YouTube) |
| `comments` | Lifetime comments (YouTube) |
| `shares` | Lifetime shares (YouTube) |
| `dislikes` | Lifetime dislikes (YouTube) |
| `ad_impressions` | Ad impressions (YouTube, Snapchat) |
| `engagement_rate` | Engagement rate % — calculated |
| `estimated_cpm` | Estimated CPM — calculated |
| `avg_view_duration_seconds` | Average view duration — calculated |
| `avg_percentage_viewed` | Average percentage viewed — calculated |

---

## Dataset 2 — Cohort Analysis (`dataset_2_cohort_analysis.csv`)

| Field | Description |
|-------|-------------|
| `video_id` | Anonymized video ID (subset of Dataset 1) |
| `platform` | YouTube or Facebook |
| `publish_month` | Cohort month (month of publication) |
| `data_month` | Calendar month of the data |
| `months_since_publish` | Months elapsed since publication |
| `views` | Views in that calendar month |
| `watch_time_minutes` | Watch time in that calendar month |

---

## Dataset 3 — Cross-Platform OCP (`dataset_3_cross_platform.csv`)

| Field | Description |
|-------|-------------|
| `video_id` | Anonymized video ID (subset of Dataset 1) |
| `content_original_id` | Anonymized original video ID (`vid_XXXXXX` — references Dataset 1) |
| `platform` | Platform where the content was posted |
| `publish_date` | Publication date |
| `total_views` | Lifetime views (from Dataset 1) |
| `watch_time_minutes` | Lifetime watch time (from Dataset 1) |
