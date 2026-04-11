# Interaction Analysis Patterns

## Table of Contents
- Why interactions matter
- Two-way interaction queries
- Heatmap visualization
- Identifying meaningful interactions
- Segment-based analysis

## Why Interactions Matter

In CTR and classification problems, the majority of predictive signal often comes from feature interactions rather than marginal distributions. A feature with flat marginal label rate may become highly predictive when conditioned on another feature.

Example: hour_of_day may show flat CTR overall, but within age_group=18-24, late-night hours have 3x higher CTR. This interaction is invisible in single-feature analysis.

## Two-Way Interaction Queries

### Time x Time

```sql
SELECT
    day_of_week,
    hour_of_day,
    COUNT(*) AS n,
    AVG(CAST(label AS INT64)) AS label_rate
FROM `project.dataset.table`
GROUP BY day_of_week, hour_of_day
ORDER BY day_of_week, hour_of_day
```

### Feature x Segment

```sql
SELECT
    CASE
        WHEN user_age < 18 THEN '<18'
        WHEN user_age < 25 THEN '18-24'
        WHEN user_age < 35 THEN '25-34'
        WHEN user_age < 50 THEN '35-49'
        ELSE '50+'
    END AS age_group,
    hour_of_day,
    COUNT(*) AS n,
    AVG(CAST(label AS INT64)) AS label_rate
FROM `project.dataset.table`
GROUP BY age_group, hour_of_day
ORDER BY age_group, hour_of_day
```

### Popularity x Activity

```sql
SELECT
    CASE
        WHEN content_views < 10 THEN 'cold'
        WHEN content_views < 100 THEN 'warm'
        WHEN content_views < 1000 THEN 'popular'
        ELSE 'viral'
    END AS content_tier,
    CASE
        WHEN user_activity < 5 THEN 'low'
        WHEN user_activity < 20 THEN 'medium'
        ELSE 'high'
    END AS user_tier,
    COUNT(*) AS n,
    AVG(CAST(label AS INT64)) AS label_rate
FROM `project.dataset.table`
GROUP BY content_tier, user_tier
ORDER BY content_tier, user_tier
```

## Heatmap Visualization

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# df has columns: dim_a, dim_b, label_rate, n

# Pivot for heatmap
pivot_rate = df.pivot(index='dim_a', columns='dim_b', values='label_rate')
pivot_n = df.pivot(index='dim_a', columns='dim_b', values='n')

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Label rate heatmap
sns.heatmap(pivot_rate, annot=True, fmt='.3f', cmap='RdYlGn', ax=axes[0])
axes[0].set_title('Label Rate by Segment')

# Volume heatmap (log scale for readability)
import numpy as np
sns.heatmap(np.log10(pivot_n + 1), annot=pivot_n.values, fmt=',d', cmap='Blues', ax=axes[1])
axes[1].set_title('Volume by Segment (color = log10)')

plt.tight_layout()
plt.show()
```

Always show volume alongside label rate. High label rate with n=5 is noise, not signal.

## Identifying Meaningful Interactions

An interaction is meaningful when:

1. **Variance in label rate across cells is large** relative to the overall rate
2. **Each cell has sufficient volume** (rule of thumb: n > 100 for stable rate estimates)
3. **The pattern is not explained by marginals** — the cell rate deviates from what you'd expect from row and column averages alone

### Quick interaction strength check

```python
# After pivoting to get label_rate matrix
overall_rate = df['label_rate'].mean()
rate_range = pivot_rate.max().max() - pivot_rate.min().min()
relative_range = rate_range / overall_rate

# relative_range > 0.5: strong interaction worth modeling explicitly
# relative_range 0.2-0.5: moderate, tree models will capture automatically
# relative_range < 0.2: weak interaction
print(f"Interaction strength: {relative_range:.2f}x of base rate")
```

## Segment-Based Analysis

Create business-meaningful segments and compare.

Priority questions:
- Which user groups click most during which hours?
- Does popular content behave differently from cold content?
- Do new users respond differently from returning users?
- Are there time-of-day effects that differ by content type?

For each question, construct the appropriate two-way GROUP BY and visualize as a heatmap.
