---
name: eda
description: Conduct exploratory data analysis on large-scale datasets, especially BigQuery tables with mixed tabular and embedding features. Use when the user asks to explore data, profile a dataset, analyze distributions, investigate feature interactions, project embeddings, build baseline models, or perform error analysis. Triggers on "explore this data", "EDA", "data profiling", "feature analysis", "embedding analysis", "baseline model", "what does this dataset look like", or any request to understand data before modeling.
---

# Exploratory Data Analysis

Structured EDA workflow for large datasets with mixed tabular + embedding features.

## Core Principle

**SQL to reduce scale, Python to visualize and inspect.**

Never pull full tables into memory. Push aggregation, filtering, and sampling into the data warehouse. Use Python only for plotting, projection, and lightweight modeling on reduced data.

## Workflow

Execute stages in order. Each stage gates the next — skip only with explicit justification.

### Stage 0: Scope Definition

Before any query, establish with the user:

- Target variable and candidate features
- Business question driving the analysis
- Expected label distribution (balanced vs imbalanced)
- Data time window and freshness
- Cost/latency constraints (BigQuery billing, row limits)

If the user hasn't specified these, ask. Do not proceed without a clear target and question.

### Stage 1: Data Profiling

Run lightweight SQL queries to understand the table shape. See [references/profiling.md](references/profiling.md) for query templates.

Checklist:
- [ ] Row count and label balance (CTR, conversion rate, etc.)
- [ ] Missing value counts per feature
- [ ] Range checks (min/max/distinct) for all numeric columns
- [ ] Embedding integrity: consistent dimensions, no null/zero/NaN vectors, norm distribution

Flag anything unexpected before proceeding. Common issues: extreme nulls, impossible ranges, collapsed embeddings.

### Stage 2: Distribution Analysis

Analyze each feature independently via grouped SQL aggregations.

- Categorical/low-cardinality: GROUP BY + COUNT + AVG(label)
- Continuous: bin first (equal-width, log-scale, or quantile), then GROUP BY bucket
- Time features: GROUP BY directly (hour, day_of_week, month)

See [references/distributions.md](references/distributions.md) for binning strategies and query patterns.

Plot results in Python using bar charts, histograms, or line plots. Annotate with label rate overlay.

### Stage 3: Interaction Analysis

Single-feature analysis misses the signal in most CTR/classification problems.

Priority interactions to check:
- Time x Time (day_of_week x hour_of_day)
- Time x User segment (hour x age_bucket)
- User x Content (user_segment x content_popularity)
- Any feature x label rate

Use two-way GROUP BY in SQL, visualize as heatmaps in Python.

See [references/interactions.md](references/interactions.md) for patterns and interpretation guidance.

### Stage 4: Sampling and Visual EDA

For row-level plots (scatter, pair, box), extract a structured sample.

Sampling rules:
1. **Never naive random** on imbalanced data — stratify by label
2. Prefer deterministic hash sampling for reproducibility: `MOD(ABS(FARM_FINGERPRINT(CAST(id AS STRING))), N) = 0`
3. Consider time-window sampling if temporal drift matters
4. Sample size: 10K-100K rows depending on plot type

Plot types for sampled data:
- Scatter plots (feature vs feature, colored by label)
- Box plots (feature by segment)
- Pair plots (only on <10 features, <5K rows)

### Stage 5: Embedding EDA

Embeddings require specialized treatment. See [references/embeddings.md](references/embeddings.md) for full procedures.

Summary:
1. **Statistics**: norm distribution, cosine similarity distribution, nearest-neighbor distances
2. **Projection**: PCA first (fast, interpretable variance), UMAP second (nonlinear structure), t-SNE last (local separation only)
3. **Coloring**: project to 2D, color by label, user segment, content segment, time
4. **Neighbor inspection**: for sample points, retrieve k-NN and inspect metadata consistency

Key diagnostic questions:
- Do positive/negative labels separate in embedding space?
- Are there visible clusters? Are they label-pure or mixed?
- Are there outlier points? What do they represent?

### Stage 6: Feature Group Comparison

Compare predictive power across feature groups:
- Numeric-only baseline
- Embedding-only baseline
- All features combined

This answers whether embeddings add incremental signal over tabular features, and vice versa.

### Stage 7: Baseline Modeling

Train simple models as an EDA tool, not for production.

Model progression:
1. Logistic regression (linear separability check)
2. Gradient boosted trees (nonlinear, feature importance)
3. Optional: factorization machine or shallow neural net

Metrics to report:
- ROC-AUC and PR-AUC (discrimination)
- Log loss (calibration quality)
- Calibration plot (predicted vs actual by decile)
- Lift chart (top decile vs random)

See [references/baselines.md](references/baselines.md) for implementation patterns.

### Stage 8: Error Analysis

After baseline, inspect model errors to find data issues and feature gaps.

Focus on:
- High-confidence false positives and false negatives
- Segments with poor calibration (predicted != actual)
- Time periods with performance drift
- Embedding outliers with wrong predictions

Common discoveries: bad labels, stale embeddings, feature leakage, sparse segments.

Error analysis often triggers a return to Stage 1 with refined scope.

## Python Libraries

- `pandas` — summaries and sampled data
- `seaborn` — `histplot`, `boxplot`, `heatmap`
- `matplotlib` — custom plots and annotations
- `scikit-learn` — PCA, logistic regression, GBT, metrics
- `umap-learn` — embedding projection
- `google-cloud-bigquery` — data extraction

## Output Expectations

A complete EDA pass should answer:
1. Which features are predictive vs noisy
2. Which segments behave differently
3. Whether embeddings contain meaningful structure
4. Whether label imbalance or drift exists
5. Whether a simple model captures most signal
6. Where a complex model might help
7. What data quality issues need fixing before modeling
