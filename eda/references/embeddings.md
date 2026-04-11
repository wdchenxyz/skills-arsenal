# Embedding EDA Procedures

## Table of Contents
- Embedding statistics
- Projection methods
- Visualization and coloring
- Nearest-neighbor inspection
- Diagnosing embedding quality

## Embedding Statistics

Compute these on a sample (10K-50K rows) after extracting embeddings to Python.

### Norm distribution

```python
import numpy as np

norms = np.linalg.norm(embeddings, axis=1)
print(f"Norm — mean: {norms.mean():.4f}, std: {norms.std():.4f}, "
      f"min: {norms.min():.4f}, max: {norms.max():.4f}")

# Histogram
import matplotlib.pyplot as plt
plt.hist(norms, bins=50, edgecolor='black')
plt.xlabel('L2 Norm')
plt.title('Embedding Norm Distribution')
plt.show()
```

Interpretation:
- Near-zero std: pre-normalized embeddings (expected for cosine-similarity models)
- Large std with outliers: check those outlier vectors for data issues
- Bimodal distribution: two different embedding sources may be mixed

### Cosine similarity distribution

```python
from sklearn.metrics.pairwise import cosine_similarity

# Sample pairs (don't compute full N x N)
n_pairs = 5000
idx_a = np.random.choice(len(embeddings), n_pairs)
idx_b = np.random.choice(len(embeddings), n_pairs)
sims = np.array([
    cosine_similarity(embeddings[a:a+1], embeddings[b:b+1])[0, 0]
    for a, b in zip(idx_a, idx_b)
])

plt.hist(sims, bins=50, edgecolor='black')
plt.xlabel('Cosine Similarity')
plt.title('Random Pair Cosine Similarity Distribution')
plt.show()
```

Interpretation:
- All similarities near 1.0: embeddings are collapsed (low information)
- Uniform distribution: embeddings are spread but possibly random
- Clear bimodal: natural clusters exist in the data

### Variance explained by PCA

```python
from sklearn.decomposition import PCA

pca_full = PCA().fit(embeddings)
cumvar = np.cumsum(pca_full.explained_variance_ratio_)

plt.plot(cumvar)
plt.xlabel('Number of Components')
plt.ylabel('Cumulative Variance Explained')
plt.axhline(y=0.9, color='r', linestyle='--', label='90%')
plt.title('PCA Variance Explained')
plt.legend()
plt.show()

# How many components for 90% variance?
n_90 = np.searchsorted(cumvar, 0.9) + 1
print(f"Components for 90% variance: {n_90} / {embeddings.shape[1]}")
```

If n_90 is much smaller than the embedding dimension, the effective dimensionality is low — PCA projection will be faithful.

## Projection Methods

### PCA (always start here)

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=2)
proj_pca = pca.fit_transform(embeddings)
print(f"Variance explained by 2 PCs: {pca.explained_variance_ratio_.sum():.2%}")
```

Pros: fast, deterministic, interpretable variance
Cons: linear only, may miss nonlinear structure

### UMAP (second pass)

```python
import umap

reducer = umap.UMAP(n_neighbors=30, min_dist=0.1, metric='cosine', random_state=42)
proj_umap = reducer.fit_transform(embeddings)
```

Pros: preserves nonlinear structure, good for cluster discovery
Cons: slower, hyperparameter-sensitive, non-deterministic

Key hyperparameters:
- `n_neighbors`: higher = more global structure (15-50 typical)
- `min_dist`: lower = tighter clusters (0.0-0.5 typical)
- `metric`: use 'cosine' for normalized embeddings, 'euclidean' otherwise

### t-SNE (only when needed)

```python
from sklearn.manifold import TSNE

proj_tsne = TSNE(n_components=2, perplexity=30, random_state=42).fit_transform(embeddings)
```

Use only when you need to inspect local neighborhood separation. t-SNE distorts global distances — do not interpret cluster distances or sizes.

## Visualization and Coloring

```python
import matplotlib.pyplot as plt

def plot_projection(coords, color_by, title, labels_map=None):
    fig, ax = plt.subplots(figsize=(10, 8))

    if labels_map:
        for val, label in labels_map.items():
            mask = color_by == val
            ax.scatter(coords[mask, 0], coords[mask, 1],
                      s=3, alpha=0.3, label=label)
        ax.legend(markerscale=5)
    else:
        scatter = ax.scatter(coords[:, 0], coords[:, 1],
                           c=color_by, s=3, alpha=0.3, cmap='RdYlGn')
        plt.colorbar(scatter)

    ax.set_title(title)
    ax.set_xlabel('Component 1')
    ax.set_ylabel('Component 2')
    plt.tight_layout()
    plt.show()

# Color by label
plot_projection(proj_umap, labels, 'UMAP colored by Click Label',
               labels_map={0: 'No Click', 1: 'Click'})

# Color by continuous feature
plot_projection(proj_umap, user_age, 'UMAP colored by User Age')
```

Always create these colorings:
1. By target label (primary diagnostic)
2. By user segment (check if segments cluster)
3. By content segment (check content structure)
4. By time period (check for temporal drift)

## Nearest-Neighbor Inspection

For a sample of anchor points, inspect their k nearest neighbors.

```python
from sklearn.neighbors import NearestNeighbors

nn = NearestNeighbors(n_neighbors=10, metric='cosine')
nn.fit(embeddings)

# Pick anchor points
anchor_indices = [0, 100, 500, 1000]  # or random sample

for idx in anchor_indices:
    distances, neighbor_idx = nn.kneighbors(embeddings[idx:idx+1])
    print(f"\nAnchor {idx}: label={labels[idx]}")
    for i, (dist, nidx) in enumerate(zip(distances[0], neighbor_idx[0])):
        print(f"  Neighbor {i}: dist={dist:.4f}, label={labels[nidx]}, "
              f"age={metadata['user_age'].iloc[nidx]}, "
              f"views={metadata['content_views'].iloc[nidx]}")
```

What to check:
- Are nearest neighbors semantically similar? (same content type, similar user)
- Do nearest neighbors share the same label? (embedding captures target signal)
- Are there distant outliers whose neighbors are dissimilar? (corrupted vectors)

## Diagnosing Embedding Quality

| Symptom | Diagnosis | Action |
|---|---|---|
| All cosine similarities > 0.95 | Collapsed embeddings | Check training, may need re-embedding |
| PCA 2 components explain > 80% | Very low effective dimension | Embeddings may be under-trained |
| No label separation in projection | Embeddings don't capture target signal | May still be useful in combination with tabular features |
| Clear clusters but label-mixed | Structure exists but is orthogonal to target | Embeddings capture something else (content type, language) |
| Temporal clusters visible | Embedding drift over time | Consider time-windowed training or recency features |
| Outlier points with wrong neighbors | Corrupted or stale vectors | Filter or re-compute for those entities |
