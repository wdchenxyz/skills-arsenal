# Baseline Modeling Patterns

## Table of Contents
- Model progression
- Data preparation
- Logistic regression baseline
- Gradient boosted trees baseline
- Evaluation metrics
- Feature importance
- Calibration analysis

## Model Progression

Train models in order of complexity. Each model answers a different question:

1. **Logistic regression**: Is the relationship linearly separable? Which features have directional signal?
2. **Gradient boosted trees**: What nonlinear patterns exist? Which features and interactions matter most?
3. **Optional deep model**: Is there signal in embeddings that trees can't capture?

## Data Preparation

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# Split before any processing to prevent leakage
X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.2, stratify=labels, random_state=42
)

# For time-series data, prefer temporal split instead:
# train: data before cutoff, test: data after cutoff
```

### Handling embeddings for tree models

Embeddings are high-dimensional. Two approaches:

```python
# Option A: PCA reduction (recommended for first pass)
from sklearn.decomposition import PCA
pca = PCA(n_components=32)
emb_reduced = pca.fit_transform(embeddings)
# Append to tabular features

# Option B: Use raw embeddings (only if tree model handles it well)
# XGBoost/LightGBM can handle 100-300 dim, but slower
```

## Logistic Regression Baseline

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

lr_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('lr', LogisticRegression(max_iter=1000, class_weight='balanced'))
])

lr_pipeline.fit(X_train, y_train)
y_pred_lr = lr_pipeline.predict_proba(X_test)[:, 1]
```

Check coefficients for feature direction:

```python
coefs = pd.Series(
    lr_pipeline.named_steps['lr'].coef_[0],
    index=feature_names
).sort_values()

print("Top positive features:")
print(coefs.tail(10))
print("\nTop negative features:")
print(coefs.head(10))
```

## Gradient Boosted Trees Baseline

```python
from sklearn.ensemble import GradientBoostingClassifier
# Or use xgboost/lightgbm for larger datasets

gbt = GradientBoostingClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.1,
    subsample=0.8,
    random_state=42
)
gbt.fit(X_train, y_train)
y_pred_gbt = gbt.predict_proba(X_test)[:, 1]
```

For large datasets (> 1M rows), prefer LightGBM:

```python
import lightgbm as lgb

dtrain = lgb.Dataset(X_train, label=y_train)
dtest = lgb.Dataset(X_test, label=y_test, reference=dtrain)

params = {
    'objective': 'binary',
    'metric': ['auc', 'binary_logloss'],
    'learning_rate': 0.05,
    'num_leaves': 63,
    'max_depth': -1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'verbose': -1
}

model = lgb.train(params, dtrain, num_boost_round=500,
                  valid_sets=[dtest], callbacks=[lgb.early_stopping(50)])
y_pred_lgb = model.predict(X_test)
```

## Evaluation Metrics

```python
from sklearn.metrics import (
    roc_auc_score, average_precision_score, log_loss,
    classification_report
)

def evaluate_model(y_true, y_pred, name):
    print(f"=== {name} ===")
    print(f"ROC-AUC:  {roc_auc_score(y_true, y_pred):.4f}")
    print(f"PR-AUC:   {average_precision_score(y_true, y_pred):.4f}")
    print(f"Log Loss: {log_loss(y_true, y_pred):.4f}")

evaluate_model(y_test, y_pred_lr, "Logistic Regression")
evaluate_model(y_test, y_pred_gbt, "Gradient Boosted Trees")
```

### Metric selection guidance

| Metric | When to prioritize |
|---|---|
| ROC-AUC | Balanced or moderately imbalanced data |
| PR-AUC | Heavily imbalanced data (CTR < 1%) |
| Log Loss | When calibrated probabilities matter (bidding, ranking) |
| Calibration | When predicted probabilities are used downstream |

## Feature Importance

```python
# For tree models
importances = pd.Series(
    gbt.feature_importances_,
    index=feature_names
).sort_values(ascending=False)

print("Top 15 features:")
print(importances.head(15))

# Plot
importances.head(20).plot(kind='barh', figsize=(8, 6))
plt.xlabel('Feature Importance')
plt.title('Top 20 Features')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()
```

Compare importance rankings between LR coefficients and tree importance. Disagreements reveal nonlinear effects worth investigating.

## Calibration Analysis

```python
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt

def plot_calibration(y_true, y_pred, name, n_bins=10):
    fraction_pos, mean_predicted = calibration_curve(
        y_true, y_pred, n_bins=n_bins, strategy='quantile'
    )

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Calibration curve
    axes[0].plot(mean_predicted, fraction_pos, 's-', label=name)
    axes[0].plot([0, 1], [0, 1], 'k--', label='Perfect')
    axes[0].set_xlabel('Mean Predicted Probability')
    axes[0].set_ylabel('Fraction of Positives')
    axes[0].set_title('Calibration Curve')
    axes[0].legend()

    # Prediction distribution
    axes[1].hist(y_pred[y_true == 0], bins=50, alpha=0.5, label='Negative', density=True)
    axes[1].hist(y_pred[y_true == 1], bins=50, alpha=0.5, label='Positive', density=True)
    axes[1].set_xlabel('Predicted Probability')
    axes[1].set_ylabel('Density')
    axes[1].set_title('Score Distribution by Class')
    axes[1].legend()

    plt.tight_layout()
    plt.show()

plot_calibration(y_test, y_pred_gbt, "GBT")
```

### Lift analysis by decile

```python
def lift_by_decile(y_true, y_pred):
    df = pd.DataFrame({'y_true': y_true, 'y_pred': y_pred})
    df['decile'] = pd.qcut(df['y_pred'], 10, labels=False, duplicates='drop')

    result = df.groupby('decile').agg(
        n=('y_true', 'count'),
        positives=('y_true', 'sum'),
        avg_pred=('y_pred', 'mean'),
        actual_rate=('y_true', 'mean')
    )
    base_rate = y_true.mean()
    result['lift'] = result['actual_rate'] / base_rate
    return result

print(lift_by_decile(y_test, y_pred_gbt))
```

Top decile lift > 3x indicates strong model discrimination. Bottom decile near 0 means the model effectively identifies non-converters.
