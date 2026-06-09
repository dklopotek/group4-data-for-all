# Cycle-B Phase-4 ML Modeling — PRE-REGISTRATION

> **Binding pre-registration** (CLAUDE.md cardinal rule). Written *before* `src/section_features.py`,
> `src/section_source_model.py`, `src/section_typology.py`, `src/section_hotspots.py`. Every model
> declared here is built and reported — **including unfriendly results**. Results appended under
> `## Results` (dated). Decision to build all three: deep-research recommendation
> `research/crispdm/04-modeling-ml-options.md`.
>
> **Why this exists.** The shipped *priority* is a composite indicator (no measured target → correct
> per OECD/JRC 2008, Rudin 2019). This phase adds **trainable models for adjacent, legitimate sub-tasks**
> — NOT a model that re-predicts the priority from its own inputs. That re-prediction is the **Cycle-A
> tautology** (eval R² 0.999 → external null). The non-tautology guarantee is enforced by feature
> selection (below) and by spatial cross-validation.

---

## 0. The non-tautology contract (applies to all supervised work)

- **Target** is an *observed* quantity from the street-tree inventory: mature-Platanus density per
  section. It is NOT a composite or a transform of the predictors.
- **Predictors** are *urban-form + demographic* features, none derived from plane counts. **Explicitly
  excluded** (would leak): `plane_count`, `mature_count`, `n_platanus`, `total_trees`,
  `species_richness`, `source_*`, `priority`, `composite_*`, and anything built from them.
- **Headline metric is the SPATIAL cross-validation score**, not random-CV. Spatial autocorrelation
  inflates random-CV (Roberts et al. 2017; Ploton et al. 2020) — that inflation is precisely what
  produced Cycle A's false 0.999. We report random-CV and spatial-CV side by side; the **gap** is the
  audit. (Counterpoint disclosed: Wadoux et al. 2021 — interpret the random↔spatial range, not one number.)

---

## 1. Feature table (`section_features.parquet`) — declared before build

Per census section (1,068), assembled by `src/section_features.py`:
- **Urban form (area-weighted from the 400 m grid):** `mean_sealed`, `mean_ndvi`, `mean_lst_celsius`.
- **Geometry-derived:** `area_km2`, `dist_to_centre_km` (to the metric centroid of all sections),
  `compactness` (Polsby-Popper).
- **Demographic (independent of plane counts):** `pop_density` (residents/km²), `income` (gross/person).
- **Categorical:** `district` (one-hot).
- **Target:** `mature_density` = `mature_count / area_km2` (observed; for the supervised model only).

---

## 2. Model #1 — Source estimator (SUPERVISED regression)

- **Predicts:** `mature_density` (observed) from the urban-form/demographic features above.
- **Estimators:** (a) regularized linear (Ridge) as the interpretable baseline; (b) RandomForest as the
  flexible comparator. Standardized features; seed 42.
- **Evaluation — two protocols, report both:**
  - **Random 5-fold CV** (the naive, leakage-prone number — for contrast).
  - **Spatial cluster CV:** 5 folds = k-means on section centroids (k=5, seed 42); hold out one spatial
    cluster at a time (group CV). This is the honest generalization estimate.
  - Metrics: R², MAE (per protocol). Feature importance (RF) + standardized coefficients (Ridge).
- **Pre-registered success criterion:** the source estimator is **useful as a drift-resistant proxy iff
  spatial-CV R² ≥ 0.30**. Below that → **honest negative**: "urban form does not predict where the city
  historically planted planes" (plausible: planting is administrative/path-dependent). Either outcome is
  reported and kept.
- **Non-tautology:** target observed, predictors exclude all tree-derived columns (§0).
- **Failure-is-reportable:** a low spatial-CV R² is a finding, not a bug; it would *strengthen* the case
  that the inventory is irreplaceable.

## 3. Model #2 — Intervention typologies (UNSUPERVISED clustering)

- **Produces:** section archetypes from the layers (`mature_density`, `pop_density`, `income`,
  `mean_sealed`, `mean_ndvi`). *(Clustering may use the observed source layer — it is not prediction,
  so no tautology.)*
- **Algorithms (compare):** k-means, Gaussian Mixture, and **spatial contiguity-constrained Ward**
  (`sklearn.AgglomerativeClustering` with a queen-adjacency `connectivity` matrix — the regionalization
  family of SKATER, Assunção et al. 2006, implemented without new deps).
- **Choosing k:** scan k = 3..8; report silhouette, Calinski-Harabasz, Davies-Bouldin; pick k by elbow +
  interpretability.
- **Pre-registered success criterion:** **silhouette ≥ 0.25** (weak-but-real structure) AND profiles
  are interpretable/nameable. Report indices regardless.
- **Validation without labels:** internal indices; spatial contiguity (constrained variant) by
  construction; **stability** = adjusted Rand index across seeds and across the kmeans/Ward choice.
- **Deliverable:** named archetypes ("dense-residential high-source", "park-cluster low-exposure",
  "low-everything") + per-section label, for planner segmentation + map colouring.

## 4. Model #3 — Hotspot layer (INFERENTIAL spatial statistics)

- **Computes:** Getis-Ord Gi* and Local Moran's I (LISA; Anselin 1995; Getis & Ord 1992) on the section
  `priority`, with a row-standardized queen-contiguity spatial weights matrix; **999-permutation
  pseudo-p-values** (seed 42). Hand-rolled (numpy), no PySAL dependency.
- **Produces:** per-section hot/cold-spot classification (Gi* z, p) and LISA quadrant
  (High-High / Low-Low / High-Low / Low-High); significant at p < 0.05.
- **Pre-registered expectation:** the parkland outlier (Montjuïc 03024) classifies as a **High-Low**
  spatial outlier (high source, low neighbourhood) — operationalizing the MAUP caveat. Report whatever
  it actually shows.
- **Role:** defensible clusters instead of arbitrary top-N; complements #1/#2.

---

## 5. Verification (run before declaring done)
- `section_features.py` → 1,068 sections, 0 nulls in features (imputation declared if any), no
  plane-derived column present (grep gate).
- `section_source_model.py` → prints random-CV vs spatial-CV R²/MAE for Ridge + RF; verdict vs the 0.30
  criterion.
- `section_typology.py` → indices table, chosen k, stability ARI, archetype profiles.
- `section_hotspots.py` → counts of significant hot/cold spots; Montjuïc classification.
- All seeded (42), ASCII console (cp1252).

---

## Results (2026-06-09)

### Model #1 — source estimator (supervised, spatial CV) → HONEST NEGATIVE
| model | random-CV R² | **spatial-CV R²** | leakage gap |
|---|---|---|---|
| Ridge | 0.41 | **−0.25** | 0.67 |
| RandomForest | 0.44 | **−0.37** | 0.81 |

Best spatial-CV R² = −0.25, **below** the pre-registered 0.30 bar — decisively. Top RF features:
`district_Eixample` (0.28), `mean_ndvi`, `pop_density`, `dist_to_centre`, `mean_lst`. The dominant
feature is the district indicator: the model memorizes *which district*, which does not transfer to
held-out geography. **Verdict:** urban form does not predict historical plane placement (planting is
path-dependent/administrative); the inventory is irreplaceable. The random→spatial collapse re-enacts
the Cycle-A leakage, this time caught by spatial CV before any number was believed. Reported and kept.
`outputs/phase-6/source_model_results.md`.

### Model #2 — typologies (unsupervised) → USABLE segmentation
k = 4 (silhouette 0.317 ≥ 0.25). Stability ARI: seed42-vs-seed7 = 1.0, vs GMM 0.32, vs spatial-Ward
0.53. Four archetypes; the structural finding is that **no high-source/high-population archetype
exists** — every high-source cluster is low-population/park-like, the large residential cluster (631
sections) is low-source. Independently confirms the §8.2 MAUP tension by a different method.
`outputs/phase-6/section_typology.md` + `section_typology.csv` (per-section labels).

### Model #3 — hotspots (Gi*/LISA, 999 perms) → defensible clusters
Getis-Ord Gi*: **100** significant hot-spots, 0 cold (p < 0.05). LISA significant quadrants: HH 76,
LH 48, HL 0, LL 0. **Pre-registration honesty:** we predicted Montjuïc 03024 would be a High-Low
outlier; it is in fact **High-High** (Gi* 5.80) — it sits inside a contiguous block of high-source
park-adjacent sections, not alone. Expectation falsified, reported as such.
`outputs/phase-6/section_hotspots.md` + `section_hotspots.csv`.

**Net:** the supervised probe's spatially-validated failure + the two unsupervised confirmations all
point the same way and reinforce the decision to ship a transparent composite, not an ML model.
