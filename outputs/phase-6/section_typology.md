# Intervention Typologies (Cycle-B Phase-4 Model #2)

Unsupervised clustering of 1,068 sections on ['mature_density', 'pop_density', 'income', 'mean_sealed', 'mean_ndvi']. No target -> no tautology.

**VERDICT: usable segmentation: silhouette 0.3168 >= 0.25, 4 interpretable archetypes**

## Choosing k (k-means)
| k | silhouette | Calinski-Harabasz | Davies-Bouldin |
|---|---|---|---|
| 3 | 0.2996 | 341.3 | 1.2417 |
| 4 | 0.3168 | 333.4 | 1.1407 |
| 5 | 0.2368 | 330.0 | 1.243 |
| 6 | 0.2217 | 313.9 | 1.2472 |
| 7 | 0.2158 | 295.0 | 1.2319 |
| 8 | 0.2089 | 279.9 | 1.2301 |
Chosen k = 4 (criterion: silhouette >= 0.25).

## Stability (Adjusted Rand Index)
{
  "kmeans_seed42_vs_seed7": 1.0,
  "kmeans_vs_gmm": 0.323,
  "kmeans_vs_spatial_ward": 0.5299
}

## Archetypes (k-means labels; raw-unit profiles in the JSON)
| cluster | archetype (source / pop / income) | suggested action | sections |
|---|---|---|---|
| 0 | high-source / low-pop / higher-income | defer (park-like) | 145 |
| 1 | low-source / high-pop / lower-income | monitor | 631 |
| 2 | high-source / low-pop / lower-income | defer (park-like) | 208 |
| 3 | high-source / low-pop / higher-income | defer (park-like) | 84 |

Per-section labels: `outputs/phase-6/section_typology.csv` (planner segmentation + map colouring).
Spatially-contiguous variant (Ward + queen adjacency) agreement with k-means: ARI
0.5299.
