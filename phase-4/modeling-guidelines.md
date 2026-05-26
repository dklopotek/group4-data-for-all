# Phase 4 Modeling Guidelines — Mycorrhizal Barcelona

Per CRISP-DM Phase 4 (Chapman et al. 2000, p. 31–33): Modeling. **Guidelines only — do NOT train models.** This document defines the modeling approach, evaluation strategy, and caveats for whoever executes Phase 4.

**Date:** 2026-05-26
**Status:** GUIDELINES — Phase 4 not executed

---

## 1. What Phase 4 Must Answer

The Phase 3 output (`data/scored_grid.geojson`) is a constructed index — it IS the deliverable. Phase 4's job is to **validate the index's internal structure**, not to build a predictive model on external labels (none exist).

Three modeling tasks ordered by priority:

| Priority | Task | Type | Input | Output |
|----------|------|------|-------|--------|
| P0 | Sensitivity analysis | Sensitivity | `scored_grid.geojson` (all 3 scenarios) | Jaccard stability report |
| P1 | Sub-score decomposition validation | Exploratory | `scored_grid.geojson` | PCA / correlation matrix / variance decomposition |
| P2 | Spatial pattern analysis | Spatial stats | `scored_grid.geojson` + `network_islands.geojson` | Moran's I, LISA, spatial cross-correlogram |

**DO NOT train a classifier/regressor.** There is no ground-truth label for "mycorrhizal barrier." Any supervised model trained on the composite score is circular.

---

## 2. P0 — Sensitivity Analysis

### 2.1 Weight sensitivity

The pipeline produces three composite scores (A/B/C). Phase 4 must quantify how much the choice of weights matters.

**Method:**
1. Compute top-N cells (N=15, 30, 50) for each scenario.
2. Compute pairwise Jaccard similarity: `|intersection| / |union|` for each N.
3. Compute Kendall's τ rank correlation between scenario pairs (full 495-cell ranking).
4. Report: which scenario pairs are most/least concordant? Which cells switch in/out of top-15 across scenarios?

**Current partial result (from notebook 05):**
- Top-15 Jaccard A-B: 0.364, B-C: 0.364, A-C: 0.538
- Rankings are weight-sensitive — scenario choice matters.

**Additional sensitivity dimensions:**
- AM/EM edge threshold (±5m from 15m/35m defaults)
- Barrier sealed_pct threshold (±0.1 from 0.7)
- LST z-score clipping range (±0.5σ from ±2σ)
- MYCO_LOOKUP extension (add 10 most frequent species beyond top-20)

### 2.2 Grid resolution sensitivity

Re-run scoring at 200m and 800m grids. Quantify MAUP effect:
- How many top-15 cells at 400m remain top-quartile at 200m and 800m?
- Does the intervention_type assignment change with resolution?

---

## 3. P1 — Sub-Score Decomposition

### 3.1 Variance structure

**Method:**
1. Principal Component Analysis (PCA) on the 4 sub-scores (495 × 4 matrix).
2. Report variance explained per PC.
3. Interpretation: if PC1 explains >80%, a single composite index is justified. If <50%, the sub-scores measure independent dimensions and the weighted sum conflates them.

**Hypothesis:** S1 (sealed) and S3 (inverted NDVI) will be highly correlated (sealed surface → low vegetation). S2 (LST) will correlate with S1 (sealed surfaces heat up). S4 (mismatch) will be weakly correlated with S1-S3 (biological, not physical).

### 3.2 Correlation matrix

Compute Spearman ρ between all 39 columns of `scored_grid.geojson`. Flag:
- ρ > 0.8: near-redundant columns (consider dropping for Phase 4 models).
- ρ < 0.05 with composite_B: columns contributing no information to the primary score.
- Unexpected correlations: e.g., species_richness should correlate with total_trees (larger cells have more species), not with S4 (biological signal should be independent).

### 3.3 Sub-score calibration

For each sub-score, plot histogram + ECDF across 495 cells:
- S1 (sealed): expected right-skewed (many cells have high sealing).
- S2 (LST anomaly): expected normal-ish (z-score construction).
- S3 (inverted NDVI): expected left-skewed (most cells have moderate vegetation).
- S4 (mismatch): expected mode at 0.5 (AM-dominant majority).

Flag sub-scores with unexpected distributions — they indicate a construction bug or a real data surprise.

---

## 4. P2 — Spatial Pattern Analysis

### 4.1 Global spatial autocorrelation

**Method:** Moran's I on composite_score_B across 495 cells.
- Spatial weights: queen contiguity (8-neighbour) on 400m grid.
- Report I statistic, p-value, and interpretation.
- Expected: strong positive autocorrelation (barriers cluster spatially — sealed surfaces, heat islands are contiguous).

### 4.2 Local spatial autocorrelation (LISA)

**Method:** Local Moran's I (Anselin 1995) per cell.
- Map: High-High clusters (barrier hotspots), Low-Low clusters (low-barrier zones), High-Low outliers (isolated barrier cell in permeable area), Low-High outliers (permeable cell in barrier zone).
- Policy interpretation: High-High clusters are priority intervention zones (de-paving one cell helps neighbours). Low-High outliers are isolated oases — protect, don't develop.

### 4.3 Network-spatial cross-correlation

**Method:** Join `network_islands.geojson` (component spatial extents) to `scored_grid.geojson`.
- Spatial cross-correlogram: correlation between composite_B and component_size as function of distance.
- Test: do large fungal network islands occur in low-barrier areas? (Expected: yes — barriers fragment networks.)

---

## 5. What NOT to Do

### 5.1 Do NOT train a random forest / XGBoost on composite_score_B

The composite score is a linear weighted sum. Any nonlinear model trained to predict it from the sub-scores will recover the weights — this is circular reasoning, not modeling.

### 5.2 Do NOT use random train/test split

Grid cells are spatially autocorrelated. Random split leaks spatial information — a model trained on 80% of cells will have seen the neighbours of the 20% test cells. Use spatial block cross-validation:
- Divide Barcelona into 5 contiguous spatial blocks (not random cells).
- Train on 4 blocks, test on 1.
- Report mean ± std performance across folds.

### 5.3 Do NOT claim predictive power from an unsupervised index

The composite score has no ground truth. "Accuracy" is meaningless. Report stability, consistency, and sensitivity — not F1 scores.

### 5.4 Do NOT build a regression model to predict bridge_score

ALL bridge_scores are zero. The network model is structural — it produces zero bridging regardless of regression covariates. Fix the network parameters first (ADR-004 remediation path).

### 5.5 Do NOT claim "the model identifies priority areas"

The composite score identifies priority areas, based on documented construction choices. Phase 4 validates the score's stability, not its "accuracy." The score IS the model — there is no separate model to validate.

---

## 6. Evaluation Rubric

Phase 4 deliverables are evaluated on:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Sensitivity thoroughness | 40% | Weight, threshold, resolution, and MYCO_LOOKUP sensitivity all tested |
| Spatial validity | 25% | Spatial CV used; Moran's I computed; MAUP acknowledged |
| Variance understanding | 20% | PCA/correlation shows understanding of sub-score structure |
| Limitation honesty | 15% | Every known Phase 3 limitation carried forward and discussed |

**No model performance metric exists.** The grade is on analytical rigor, not predictive accuracy.

---

## 7. Deliverables Checklist

- [ ] `phase-4/sensitivity-report.md` — weight + threshold + resolution sensitivity
- [ ] `phase-4/variance-decomposition.md` — PCA + correlation matrix + sub-score calibration
- [ ] `phase-4/spatial-analysis.md` — Moran's I + LISA map + network correlation
- [ ] `phase-4/limitations.md` — updated limitations from Phase 3 + new findings from Phase 4
- [ ] `phase-4/notebooks/06-sensitivity.ipynb` (optional) — reproducible sensitivity code
- [ ] `phase-4/notebooks/07-spatial-stats.ipynb` (optional) — reproducible spatial analysis

---

## 8. Key References for Phase 4

- Anselin, L. (1995). Local Indicators of Spatial Association — LISA. *Geographical Analysis*, 27(2), 93–115.
- Arlot, S. & Celisse, A. (2010). A survey of cross-validation procedures for model selection. *Statistics Surveys*, 4, 40–79. (Spatial CV: §5.2)
- Roberts, D. R. et al. (2017). Cross-validation strategies for data with spatial, temporal, or phylogenetic structure. *Ecography*, 40(8), 913–929. (Spatial block CV: §3.2)
- Tobler, W. R. (1970). A computer movie simulating urban growth in the Detroit region. *Economic Geography*, 46(sup1), 234–240. (Tobler's First Law: why spatial independence is violated)
- O'Sullivan, D. & Unwin, D. J. (2010). *Geographic Information Analysis*. 2nd ed. Wiley. (Moran's I, LISA, spatial weights)

---

**Date:** 2026-05-26
**Guidelines by:** Claude (Phase 4 preparation, no execution)
**Status:** READY FOR PHASE 4 EXECUTION — do NOT train models
