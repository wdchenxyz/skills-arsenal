# Distribution Analysis Patterns

## Table of Contents
- Categorical and low-cardinality features
- Continuous features with binning
- Binning strategies
- Time-based features
- Visualization guidance

## Categorical and Low-Cardinality Features

Direct GROUP BY when distinct values < 50.

```sql
SELECT
    categorical_col,
    COUNT(*) AS n,
    AVG(CAST(label AS INT64)) AS label_rate,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) AS pct_of_total
FROM `project.dataset.table`
GROUP BY categorical_col
ORDER BY n DESC
```

Interpretation:
- Compare label_rate across categories — large differences indicate predictive signal
- Check for rare categories (< 0.1% of data) — these may cause overfitting
- Look for a single dominant category (> 90%) — low information, consider dropping

## Continuous Features with Binning

### Equal-width bins (uniform features)

```sql
SELECT
    FLOOR(numeric_col / 10) * 10 AS bin_start,
    COUNT(*) AS n,
    AVG(CAST(label AS INT64)) AS label_rate
FROM `project.dataset.table`
GROUP BY bin_start
ORDER BY bin_start
```

### Log-scale bins (skewed features like views, revenue, counts)

```sql
SELECT
    CASE
        WHEN val <= 0 THEN 'zero_or_neg'
        WHEN val < 10 THEN '1-9'
        WHEN val < 100 THEN '10-99'
        WHEN val < 1000 THEN '100-999'
        WHEN val < 10000 THEN '1K-9.9K'
        ELSE '10K+'
    END AS bucket,
    COUNT(*) AS n,
    AVG(CAST(label AS INT64)) AS label_rate
FROM `project.dataset.table`
GROUP BY bucket
ORDER BY MIN(val)
```

### Quantile bins (any distribution)

```sql
WITH quantiles AS (
    SELECT
        numeric_col,
        label,
        NTILE(10) OVER (ORDER BY numeric_col) AS decile
    FROM `project.dataset.table`
)
SELECT
    decile,
    MIN(numeric_col) AS bin_min,
    MAX(numeric_col) AS bin_max,
    COUNT(*) AS n,
    AVG(CAST(label AS INT64)) AS label_rate
FROM quantiles
GROUP BY decile
ORDER BY decile
```

## Binning Strategy Selection

| Data shape | Recommended binning | Why |
|---|---|---|
| Uniform (age, hour) | Equal-width or direct GROUP BY | Natural interpretation |
| Right-skewed (views, revenue) | Log-scale buckets | Prevents one huge bucket dominating |
| Unknown/complex | Quantile (decile/percentile) | Equal-count bins, always interpretable |
| Already categorical | Direct GROUP BY | No binning needed |

Rule of thumb: if max/min > 100, use log-scale or quantile bins.

## Time-Based Features

### Hour of day

```sql
SELECT
    hour_of_day,
    COUNT(*) AS n,
    AVG(CAST(label AS INT64)) AS label_rate
FROM `project.dataset.table`
GROUP BY hour_of_day
ORDER BY hour_of_day
```

### Day of week

```sql
SELECT
    day_of_week,
    COUNT(*) AS n,
    AVG(CAST(label AS INT64)) AS label_rate
FROM `project.dataset.table`
GROUP BY day_of_week
ORDER BY day_of_week
```

### Week over week trend

```sql
SELECT
    DATE_TRUNC(timestamp_col, WEEK) AS week_start,
    COUNT(*) AS n,
    AVG(CAST(label AS INT64)) AS label_rate
FROM `project.dataset.table`
GROUP BY week_start
ORDER BY week_start
```

## Visualization Guidance

### Python plotting for distribution results

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# After fetching grouped SQL results into a DataFrame `df`:

fig, ax1 = plt.subplots(figsize=(10, 5))

# Volume bars on primary axis
ax1.bar(df['bucket'], df['n'], alpha=0.3, color='steelblue', label='Volume')
ax1.set_ylabel('Count', color='steelblue')

# Label rate line on secondary axis
ax2 = ax1.twinx()
ax2.plot(df['bucket'], df['label_rate'], color='coral', marker='o', label='Label Rate')
ax2.set_ylabel('Label Rate', color='coral')

plt.title('Distribution with Label Rate Overlay')
fig.legend(loc='upper right')
plt.tight_layout()
plt.show()
```

This dual-axis pattern (volume bars + label rate line) is the most informative single-feature plot for classification EDA. Use it by default.

### What to look for

- **Monotonic label rate**: feature has clear directional signal (good for linear models)
- **Non-monotonic label rate**: feature has complex relationship (needs trees or bucketization)
- **Flat label rate**: feature has no predictive signal for the target
- **Extreme spikes**: possible data leakage or label noise in that segment
- **Empty buckets**: data sparsity in that range, may cause instability
