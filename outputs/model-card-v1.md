# Model Card — Phase 4 Core B (Barrier-Score Regressor v1)

**Project:** Mycorrhizal Barcelona
**Author:** Rafik El Khoury (Group 4)
**Date:** 2026-05-26
**Schema source:** Mitchell et al. (2019) "Model Cards for Model Reporting", adapted per `crispdm-4-modeling §8`.
**Lecture anchor:** `Session 4/Lecture_4.md` lines 383-417 (model card requirements).
**Upstream pipeline commit:** `859bda9` (Phase 3 v1.2.0).

---

## 1. Purpose and intended use

A linear regression model that predicts the per-cell barrier-severity score
`composite_score_B` in [0, 1] for unseen 400m × 400m grid cells in the
Barcelona municipal extent, using ten raw geospatial features (sealed-surface
fraction, NDVI, LST anomaly, mycorrhizal-host fractions, Platanus fraction,
VPA allergenicity, species richness, tree count, young-tree fraction).

**Intended use:** triage tool for a capital-planning analyst at Ajuntament
de Barcelona — Espais Verds / Barcelona Regional to rank candidate cells
for FY-2026 Eixos Verds / Superilla intervention budget when (a) only raw
raster + tree-inventory aggregates are available for a new cell and (b) the
full Phase 3 sub-score pipeline has not been re-run for that cell.

**Decision the output informs:** ranking of cells by predicted barrier
severity, cross-referenced with `intervention_type` to slot cells into
de-paving, cooling, planting, multi-strategy, or species-replacement actions.

## 2. Out-of-scope uses (lecture requires ≥ 3)

This model is **NOT** for:

1. **Regulatory decisions.** The model does not produce legally defensible
   air-quality, biodiversity, or land-use determinations. Phase 3 sub-scores
   are derived from public rasters whose calibration uncertainty has not
   been propagated through the model.
2. **Cell-level public-health advice.** The PRPI inputs (`platanus_pct`,
   `cell_vpa_score`) reflect aggregate pollen-allergenicity hypotheses
   (Cariñanos & Marinangeli 2021) re-scoped after Osborne et al. (2017);
   they are not individual exposure estimates.
3. **Predictions outside the Barcelona municipal boundary.** The model was
   trained on cells inside `data/bcn-boundary.geojson`. Peri-urban cells
   (Collserola, Garraf, El Prat) are out-of-distribution and were not
   included in training, eval, or test.
4. **Predictions for cells where ≥ 3 of the 10 features are missing.** The
   median imputer was fit on the train cluster; large missingness shifts
   the imputed values away from the cell's local distribution.
5. **Forecasting future barrier scores** (e.g., post-intervention). The
   model is a static cross-sectional regressor on a single snapshot
   (arbrat-viari 2026_1T inventory + 2018-2025 raster composites). It has
   no temporal axis and no causal interpretation.

## 3. Input data summary

| Property | Value |
|---|---|
| Source artifact | `data/processed/scored_grid.parquet` |
| Row count | 494 cells |
| Primary key | `cell_id` |
| Geometry CRS | EPSG:25831 |
| Datasheet | `phase-3/datasheets/scored-grid.md` |
| Data contract | `phase-3/data-contract.yaml` v1.2.0 |
| Pipeline lineage | Phase 3 commit `859bda9` |

**Target column:** `composite_score_B` (sealed-dominant scenario, weights
`{s1: 0.45, s2: 0.20, s3: 0.15, s4: 0.05, prpi: 0.15}`).

**Feature columns (10):** `mean_sealed`, `mean_ndvi`, `lst_anomaly`, `am_pct`,
`em_pct`, `platanus_pct`, `cell_vpa_score`, `species_richness`,
`total_trees`, `trees_young_pct`.

**Explicitly excluded as leakage:** `s1_sealed`, `s2_lst_anomaly`,
`s3_inverted_ndvi`, `s4_mismatch`, `prpi`, `composite_score_A`,
`composite_score_C`, all `s*_contribution_pct`, `top15_flag`,
`replacement_priority`. Justification in `phase-4/analytical-question.md §5`.

## 4. Modeling technique

| Field | Value |
|---|---|
| Family | Supervised regression — interpretable linear (skill §5 Route 4C; Rudin 2019 gate passes) |
| Specific method | `sklearn.linear_model.LinearRegression` |
| Preprocessing | Median imputer (sklearn `SimpleImputer(strategy='median')`) fit on train only |
| Pipeline | `Pipeline([("imputer", SimpleImputer), ("regressor", LinearRegression)])` |
| Random seed | n/a for linear regression; k-means split seed `RANDOM_SEED = 42` |
| Hyperparameter swept | `fit_intercept ∈ {True, False}` (one parameter only — Lecture 4 line 415) |
| Hyperparameter chosen | `fit_intercept = False` (eval MAE 0.0017) |

## 5. Parameter and choice log

- **Split strategy: spatial cluster, k = 5, k-means on (x, y) centroid in
  EPSG:25831, seed 42.** Selected because Lecture 4 lines 291-301 explicitly
  recommend spatial cluster splits for environmental data; the lecture's
  example uses k = 5. Cluster IDs re-labelled by descending size so the
  assignment is deterministic across re-runs. Alternative considered: hold-out
  of 2 of 10 districts. Rejected because districts are correlated by a
  sea→Collserola gradient and give fewer folds.
- **Train / eval / test = clusters {0,1,2} / {3} / {4} (≈ 64 / 19 / 18 %).**
  Test cluster (cluster 4) was written at split time and touched exactly
  once at final assessment per Lecture 4 line 313.
- **Median imputation on numeric features.** Fit on TRAIN only; same imputer
  reused on eval + test. Selected because (a) skill §5 Route 4C does not
  permit eval / test inspection during fit, (b) feature missingness is
  concentrated in `lst_anomaly` and `am_pct` (raster QA edge cases / no
  matched trees), and (c) mean imputation distorts skewed sealed-surface
  data.
- **Baselines: three (BaselineMean, BaselineSpatialNearest,
  BaselineDomainHeuristic).** Each fit on TRAIN only. The domain heuristic
  threshold (`mean_sealed > 0.7 → 90th-pct of train`, else train mean)
  encodes the rule "more sealed = more barrier" that the Espais Verds
  analyst already knows; selected per Lecture 4 line 325 as the
  most-useful baseline.
- **No regularization.** Lecture 4 line 415 caps tuning at one parameter
  for the chosen model. With 314 training rows and 10 features, OLS is not
  rank-deficient; ridge/lasso were not explored.

## 6. Test design and assessment results

Pre-registered in `phase-4/test-design.md` BEFORE the final build.
Results appended post-build to the same file under `## Results`.

Headline (test cluster, n = 88):

| Estimator | R² | MAE | RMSE |
|---|---|---|---|
| **LinearRegression** | **0.877** | **0.0106** | **0.0509** |
| BaselineSpatialNearest | -0.290 | 0.130 | 0.165 |
| BaselineMean | -0.616 | 0.142 | 0.185 |
| BaselineDomainHeuristic | -0.622 | 0.143 | 0.185 |

**Pre-registered pass criterion (`phase-4/test-design.md §2`): beat all
three baselines on test R² AND test MAE. PASS.**

## 7. Robustness statement

**Robust conclusion (substantive):** within the geographic distribution of
the training cells, `composite_score_B` is close to a linear combination of
its raw raster + tree-inventory inputs. A 10-feature OLS recovers the
composite to within ≈ 0.001 MAE on a held-out eval cluster from the same
city. Implication: the Phase 3 composite carries very little information
beyond a linear re-skin of `mean_sealed`, `mean_ndvi`, and friends.

**Fragile conclusion:** absolute calibration of the model on
out-of-distribution geography drops by ~6× (eval MAE 0.0017 → test MAE
0.0106). On the test cluster (Sarrià-Sant Gervasi + Les Corts) a single
cell shows residual 0.334. Implication: do NOT use this model to
discriminate between two cells whose predicted scores differ by < 0.03.

**Stability check status:** jackknife (drop-one train cluster) and
Gaussian-noise injection were pre-registered in `test-design.md §6` and
deferred to Core A wrap-up. Logged here as a gap.

## 8. Interpretability statement

Any cell's prediction can be reconstructed by:
1. Reading the cell's 10 feature values from `scored_grid.parquet`.
2. Median-imputing any missing values using the medians stored in
   `outputs/phase-4/model_artifact.joblib['model']['imputer']`.
3. Computing the dot product of the imputed feature vector with the
   regression coefficients from
   `outputs/phase-4/model_artifact.joblib['model']['regressor'].coef_`.

No nonlinearity, no ensembling, no hidden state. A domain expert can audit
any prediction in under a minute.

## 9. Known limitations and ethical considerations

- **MAUP.** All scores are at the 400m grid resolution. A 200m or
  1000m grid would re-rank cells. The Phase 3 grid was chosen for visual
  legibility on a Barcelona-scale map; Phase 4 inherits that choice.
- **Edge effects.** Cells along the municipal boundary truncate at the
  coastline / Collserola scarp; their feature aggregates are over partial
  polygons and were not re-weighted.
- **Wealthy-district test cluster.** The k-means seed produced a test
  cluster (Sarrià-Sant Gervasi + Les Corts) that is the wealthier, hillier
  NW corner. Out-of-sample performance reflects generalization to that
  specific demographic / topographic profile. A different seed (or a
  district-balanced split) would change the test cluster.
- **Equity.** Cells with low tree counts or recent plantings inflate the
  median imputer's influence — these tend to be the newer peri-central
  neighbourhoods (e.g., Marina del Prat Vermell) — so the model is *less*
  calibrated for the parts of the city that historically receive the
  *least* green investment. Predictions in such cells should be re-checked
  by hand before any capital-allocation decision.
- **Snapshot.** Inventory: arbrat-viari `2026_1T` (Open Data BCN, pulled
  2026-05-26). Re-pull on next inventory release.
- **Sensitivity coverage.** The 24-spec sensitivity grid for Core A
  (`phase-4/test-design.md §4`) was pre-registered but executed in the
  Core A wrap-up artefact, not this card. This card covers Core B only.

## 10. Versioning

| Field | Value |
|---|---|
| Code git SHA (at training time) | `859bda9` (Phase 3 head); Phase 4 commit pending |
| Input data SHA | `data/processed/scored_grid.parquet`, regenerable from `python src/clean_data.py` against the same input data and `REFERENCE_DATE = 2026-05-26` |
| Random seed | `RANDOM_SEED = 42` (in `src/split_data.py`) |
| Parameter config | hard-coded in `src/train_model.py` (`FEATURE_COLS`, `TARGET`, `SEALED_HIGH_THRESHOLD`); fitted model + tune info pickled to `outputs/phase-4/model_artifact.joblib` |
| Reproducibility command | `python src/clean_data.py && python src/split_data.py && python src/train_model.py` |

## 11. Authors and reviewers

- **Author:** Rafik El Khoury (Group 4)
- **Built with:** Claude Code (Opus 4.7, 1M context)
- **Reviewers (pending):** Roberto (instructor), Salvador (TA)
- **Review channel:** GitHub push per Lecture 4 line 187-193 action items.
