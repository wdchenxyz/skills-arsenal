# Data Profiling Query Templates

## Table of Contents
- Row count and label balance
- Missing value audit
- Range and cardinality checks
- Embedding integrity checks
- Duplicate detection
- Temporal coverage

## Row Count and Label Balance

```sql
SELECT
    COUNT(*) AS total_rows,
    COUNTIF(label = 1) AS positives,
    COUNTIF(label = 0) AS negatives,
    AVG(CAST(label AS INT64)) AS positive_rate,
    SAFE_DIVIDE(COUNTIF(label = 1), COUNTIF(label = 0)) AS pos_neg_ratio
FROM `project.dataset.table`
```

Interpretation:
- positive_rate < 0.01: heavily imbalanced — stratified sampling mandatory, PR-AUC more informative than ROC-AUC
- positive_rate 0.01-0.10: moderate imbalance — standard but monitor calibration
- positive_rate > 0.10: relatively balanced — standard metrics apply

## Missing Value Audit

Generate one query covering all columns. Adapt column names to the actual schema.

```sql
SELECT
    COUNT(*) AS total_rows,
    COUNTIF(col_a IS NULL) AS col_a_nulls,
    ROUND(COUNTIF(col_a IS NULL) / COUNT(*) * 100, 2) AS col_a_null_pct,
    COUNTIF(col_b IS NULL) AS col_b_nulls,
    ROUND(COUNTIF(col_b IS NULL) / COUNT(*) * 100, 2) AS col_b_null_pct
    -- extend for all columns
FROM `project.dataset.table`
```

Action thresholds:
- < 1% nulls: safe to drop or impute with median/mode
- 1-10% nulls: impute carefully, check if missingness correlates with label
- > 10% nulls: investigate root cause before imputing — missingness may itself be a feature
- > 50% nulls: consider dropping the feature or treating it as a separate segment

## Range and Cardinality Checks

```sql
SELECT
    MIN(numeric_col) AS min_val,
    MAX(numeric_col) AS max_val,
    AVG(numeric_col) AS mean_val,
    APPROX_QUANTILES(numeric_col, 100)[OFFSET(50)] AS median_val,
    APPROX_QUANTILES(numeric_col, 100)[OFFSET(1)] AS p1,
    APPROX_QUANTILES(numeric_col, 100)[OFFSET(99)] AS p99,
    STDDEV(numeric_col) AS stddev_val,
    APPROX_COUNT_DISTINCT(numeric_col) AS distinct_count
FROM `project.dataset.table`
```

Red flags:
- min = max: constant feature, remove
- p1 and p99 very far from mean: heavy tails, consider log transform or winsorization
- distinct_count = 1 or 2: likely categorical, not numeric
- negative values in columns that should be non-negative (age, views, counts)

## Embedding Integrity Checks

### Dimension consistency

```sql
SELECT
    ARRAY_LENGTH(embedding_col) AS dim,
    COUNT(*) AS n
FROM `project.dataset.table`
GROUP BY dim
ORDER BY n DESC
```

If multiple dimensions appear, the embedding pipeline has inconsistencies.

### Null and zero vector detection

```sql
SELECT
    COUNTIF(embedding_col IS NULL) AS null_vectors,
    COUNTIF(
        (SELECT SUM(ABS(x)) FROM UNNEST(embedding_col) AS x) = 0
    ) AS zero_vectors,
    COUNT(*) AS total
FROM `project.dataset.table`
```

### Norm distribution (sample)

```sql
SELECT
    APPROX_QUANTILES(
        (SELECT SQRT(SUM(x * x)) FROM UNNEST(embedding_col) AS x),
        100
    )[OFFSET(50)] AS median_norm,
    APPROX_QUANTILES(
        (SELECT SQRT(SUM(x * x)) FROM UNNEST(embedding_col) AS x),
        100
    )[OFFSET(1)] AS p1_norm,
    APPROX_QUANTILES(
        (SELECT SQRT(SUM(x * x)) FROM UNNEST(embedding_col) AS x),
        100
    )[OFFSET(99)] AS p99_norm
FROM `project.dataset.table`
```

Red flags:
- All norms identical: likely pre-normalized (expected for some models, suspicious for others)
- Very small norm variance: embeddings may be collapsed (low information content)
- Very large norm spread: check for outlier/corrupted vectors

## Duplicate Detection

```sql
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT primary_key) AS unique_keys,
    COUNT(*) - COUNT(DISTINCT primary_key) AS duplicate_rows
FROM `project.dataset.table`
```

For feature-level duplicates (same features, different labels):

```sql
SELECT
    feature_hash,
    COUNT(*) AS n,
    AVG(CAST(label AS INT64)) AS label_rate
FROM (
    SELECT
        FARM_FINGERPRINT(CONCAT(
            CAST(feat_a AS STRING), '|',
            CAST(feat_b AS STRING), '|',
            CAST(feat_c AS STRING)
        )) AS feature_hash,
        label
    FROM `project.dataset.table`
)
GROUP BY feature_hash
HAVING n > 1
ORDER BY n DESC
LIMIT 100
```

## Temporal Coverage

```sql
SELECT
    DATE(timestamp_col) AS dt,
    COUNT(*) AS rows_per_day,
    AVG(CAST(label AS INT64)) AS daily_label_rate
FROM `project.dataset.table`
GROUP BY dt
ORDER BY dt
```

Look for:
- Missing dates (data pipeline gaps)
- Volume spikes or drops (traffic anomalies)
- Label rate drift over time (concept drift or seasonality)
