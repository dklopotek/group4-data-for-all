# Phase 4 — Pre-registered Test Design

**Date written:** 2026-05-26 (BEFORE final model build — required by skill §6)
**Author:** Rafik El Khoury (Group 4)
**Lecture anchor:** `Session 4/Lecture_4.md` lines 273–311 (splits), 313–328 (baselines), 354–391 (metrics + model cards)
**Skill anchor:** `crispdm-4-modeling §6 + §7`
**Rule:** every test below MUST be run on the final build, and every result reported — including unfriendly ones. Silently dropping a pre-registered test is the cardinal Phase 4 sin (skill §6).

---

## 1. Split design (Core B — regression)

**Strategy chosen:** spatial cluster split via k-means on cell centroid (lat, lon), k = 5.

**Rationale (lecture lines 291–294 + 301):**
> "Spatial or clustered. Basically you're trying to group them together within a specific domain… It basically holds out an entire region… you get more variances because you are testing different cities… a really, really good approach for what we're trying to do here."
>
> "This example chooses to cluster the entire data in five clusters."

**Why not random rows.** Lecture line 280: *"random splits are basically not evaluated as much as we want them to."* Adjacent 400m cells share rasters and tree-inventory aggregates → independence assumption false.

**Why not district hold-out.** Only 10 districts; correlated by sea→Collserola gradient; gives fewer folds than k-means and confounds cluster identity with district administration.

**Why not entity-grouped on `cell_id`.** Every cell is its own entity; reduces to row-level split.

**Implementation contract:**
- k-means seed: `RANDOM_SEED = 42` (locked in code).
- Run on cell centroid in EPSG:25831 (meters), not lat/lon (avoids cosine distortion).
- 5 clusters → 3 train, 1 eval, 1 test (60/20/20).
- Cluster assignments written to `data/splits/cluster_assignments.parquet` AT SPLIT TIME and never re-shuffled.
- Test cluster is **frozen on first write** and **must not be inspected** until final assessment (lecture line 313).

## 2. Baselines (Core B)

Lecture demands a baseline that the model must beat (lines 313–328). Three baselines pre-registered:

| Baseline | Type | Definition | Rationale |
|---|---|---|---|
| **BaselineMean** | dumb | Predict train mean of `composite_score_B` for every test cell | Lecture line 318: floor — model must capture signal beyond bulk average |
| **BaselineSpatialNearest** | spatial | For each test cell, predict the target of the nearest train cell by Euclidean distance on (x, y) | Lecture line 322–323: captures pure-geography signal |
| **BaselineDomainHeuristic** | expert | `if mean_sealed > 0.7 → 90th-pct of train target; else → train mean` | Lecture line 325: "what engineers/planners already know" — Espais Verds analyst already knows sealed = barrier |

**Persistence baseline (time series) explicitly DROPPED** — dataset is a single snapshot, no temporal axis.

**Pass criterion:** model must beat ALL THREE baselines on test-cluster R² AND on test-cluster MAE. If model loses to any baseline, lecture line 326–328 applies: either the brief is wrong, the features carry no signal, or the model is too weak — log it, do NOT silently retry.

## 3. Model (Core B)

**Family:** linear regression (`sklearn.linear_model.LinearRegression`) — lecture line 354–355: *"almost always a linear model just works. You don't need some deep learning."* Rudin (2019) interpretability gate passes trivially.

**Features** (10, listed in `phase-4/analytical-question.md §5`): raw measured signals only, no Phase-3 sub-scores (leakage).

**Imputation:** median impute on `mean_lst_celsius`, `lst_anomaly`, `mean_ndvi`, `am_pct`, `em_pct`, `trees_young_pct`, `cell_vpa_score` — fit on TRAIN only; reused on eval + test.

**Tuning:** exactly one hyperparameter sweep — `fit_intercept ∈ {True, False}`. Lecture line 415: *"please only tune one."* No regularization sweep, no PolynomialFeatures.

## 4. Sensitivity analysis (Core A — PRPI composite)

Skill §6 + §7 require sensitivity on EVERY substantive composite choice. Pre-registered grid:

| Fork | Variants | n |
|---|---|---|
| Normalization | (a) min-max [0,1] **DEFAULT**, (b) min-max winsorized 5th/95th pct, (c) z-score | 3 |
| Weighting | (a) Scenario A equal, (b) **Scenario B sealed-dominant DEFAULT**, (c) Scenario C heat+canopy, (d) PCA on 4 sub-scores | 4 |
| Aggregation | (a) linear weighted sum **DEFAULT**, (b) geometric weighted product | 2 |

Full factorial: 3 × 4 × 2 = **24 specifications**. For each, compute per-cell composite, rank cells, and tag each cell's rank-tier (top-decile / mid / bottom). Report:

1. Per-cell **rank-stability count** — how many of the 24 specs place this cell in the same tier as the default (Scenario B, min-max, linear)?
2. Cells with rank-stability ≥ 22/24 → **ROBUST**. Cells < 18/24 → **FRAGILE** (flagged in model card).
3. Cronbach's alpha across the 4 sub-scores within Scenario B → internal-consistency report (Nardo et al. 2005).

## 5. Construct validity (both cores)

| Check | How |
|---|---|
| Convergent | Pearson correlation between predicted score and `mean_sealed` (should be positive and strong — sealed is the dominant driver) |
| Discriminant | Pearson correlation between predicted score and `species_richness` (should be weak — richness is loosely related but not a driver) |
| Expert face validation | Surface the top-15 predicted cells and compare to Phase 3 `top15_flag` (Phase 3's headline cells). Report Jaccard overlap. Below 0.5 = concerning; investigate. |
| OOD probe | Predict on the cluster excluded as TEST and check residual distribution by district — flag districts with mean |residual| > 0.10 |

## 6. Stability checks

- **Jackknife on train clusters:** refit dropping each of the 3 train clusters in turn; report coefficient stability (mean ± std across 3 refits).
- **Noise injection:** add Gaussian noise σ=0.02 to all features, refit, recompute test R². Report delta.

## 7. Cross-data validation

Out of scope for this session — no parallel Barcelona dataset, no peri-urban control patch in pipeline (HANDOFF.md open question #5). Logged in §10 known-limitations of the model card. Deferred to a future Session.

## 8. Reporting contract

After build, append a `## Results` section to THIS file with:
- All baseline + model metrics (train, eval, test) in one Markdown table.
- Per-cluster residual table.
- Sensitivity-grid rank-stability histogram.
- Construct-validity correlations.
- Stability deltas.

**Negative results stay in the report.** No edits to this pre-registered design after build except dated addenda explaining why a test could not be run.

---

## Results (Core B — appended 2026-05-26, post-build)

### Headline metrics (one row per estimator × split)

| Estimator | Split | n | R² | MAE | RMSE |
|---|---|---|---|---|---|
| LinearRegression | train | 314 | 0.9997 | 0.0010 | 0.0022 |
| LinearRegression | eval  |  92 | 0.9991 | 0.0017 | 0.0039 |
| **LinearRegression** | **test**  |  **88** | **0.8769** | **0.0106** | **0.0509** |
| BaselineDomainHeuristic | train | 314 | 0.1791 | 0.0758 | 0.1122 |
| BaselineDomainHeuristic | eval  |  92 | 0.2257 | 0.0725 | 0.1122 |
| BaselineDomainHeuristic | test  |  88 | -0.6217 | 0.1428 | 0.1849 |
| BaselineSpatialNearest | train | 314 | 1.0000 | 0.0000 | 0.0000 |
| BaselineSpatialNearest | eval  |  92 | 0.0134 | 0.0935 | 0.1267 |
| BaselineSpatialNearest | test  |  88 | -0.2898 | 0.1298 | 0.1649 |
| BaselineMean | train | 314 | 0.0 | 0.0986 | 0.1238 |
| BaselineMean | eval  |  92 | -0.0000 | 0.0973 | 0.1275 |
| BaselineMean | test  |  88 | -0.6160 | 0.1424 | 0.1845 |

### Pass-criterion verdict

- Pre-registered pass criterion (§2): model must beat all three baselines on test R² AND test MAE.
- Result: **PASS.** LinearRegression test R² 0.877 vs best baseline -0.29; test MAE 0.011 vs best baseline 0.130. The model recovers a near-linear structure inside the composite.
- Hyperparameter `fit_intercept = False` chosen on eval (eval MAE 0.0017 < intercept-True alternative).

### Per-district residuals (test cluster only)

| District | n | mean residual | mean abs residual | max abs residual |
|---|---|---|---|---|
| Sarrià - Sant Gervasi | 51 | +0.0107 | 0.0174 | 0.3339 |
| Les Corts | 37 | +0.0003 | 0.0011 | 0.0098 |

- Both within the §5 OOD-probe gate (mean |residual| < 0.10) — district-level systematic bias is not present.
- One outlier cell in Sarrià drives the max residual (0.334). Flagged as fragile in the model card §7.

### Interpretation

The test cluster is the wealthier, hillier NW corner (Sarrià-Sant Gervasi + Les Corts) — geographically distinct from the train cluster (Eixample, Sant Martí, central) and the eval cluster. The 6× MAE gap from eval (0.0017) to test (0.0106) is the **honest spatial generalization cost**.

The very high eval R² (0.999) confirms what `analytical-question.md §5` warned: `composite_score_B` is largely a linear re-skin of its raw raster inputs WHEN the cluster is geographically similar to train. The 0.877 test R² shows the linear approximation degrades — but does NOT collapse — on out-of-sample geography. This is the substantive Phase 4 finding: the headline composite is locally well-behaved and approximately additive, but its precise calibration depends on the geographic distribution of the cells used to compute its normalizations.

### Tests deferred (not in the build, logged here)

- §4 Sensitivity grid (24 specs for Core A) — moved to Core A wrap-up, runs separately.
- §5 Jackknife / noise stability — moved to Core A wrap-up so Core B closeout can ship today.
- §7 Cross-data validation — no parallel dataset; stays deferred per §7 above.

These deferrals are flagged in `outputs/model-card-v1.md §9 (limitations)`.



## Results (ROB/VAL, appended 2026-06-04)

**Correctness gate:** default spec reproduces `composite_score_B` at corr = 1.0.

**ROB-01..04 sensitivity grid (24 specs):** cells tagged {'ROBUST': 321, 'MODERATE': 97, 'FRAGILE': 76} (ROBUST >=22/24, FRAGILE <18/24). Artifact `outputs/phase-4/sensitivity-grid.csv`, figure `outputs/sensitivity-rank-stability.png`.

**ROB-03 Cronbach's alpha (4 sub-scores):** 0.5986.

**ROB-05 jackknife:** per-feature coef mean +/- std across 3 train-cluster refits (full table `outputs/phase-4/stability.json`). **ROB-06 noise (sigma 0.02 of train SD):** test-R2 0.8761 (delta -0.0008). **ROB-07 alt seeds:** test-R2 {1: 0.8774, 7: 0.8774, 123: 0.8769}. **ROB-08 alt-cut:** alt_cut_drop_SANTS - MONTJUÏC_test_r2 = 0.8778 vs baseline 0.8769.

**VAL-01 convergent** r(pred, sealed) = 0.9439. **VAL-02 discriminant** r(pred, richness) = 0.2527. **VAL-03 Jaccard** top-15 pred vs flag = 0.3636 (below 0.5: True). **VAL-04 OOD** districts with mean|resid|>0.10: [].


## Results (ROB/VAL, appended 2026-06-04)

**Correctness gate:** default spec reproduces `composite_score_B` at corr = 1.0.

**ROB-01..04 sensitivity grid (24 specs):** cells tagged {'ROBUST': 321, 'MODERATE': 97, 'FRAGILE': 76} (ROBUST >=22/24, FRAGILE <18/24). Artifact `outputs/phase-4/sensitivity-grid.csv`, figure `outputs/sensitivity-rank-stability.png`.

**ROB-03 Cronbach's alpha (4 sub-scores):** 0.5986.

**ROB-05 jackknife:** per-feature coef mean +/- std across 3 train-cluster refits (full table `outputs/phase-4/stability.json`). **ROB-06 noise (sigma 0.02 of train SD):** test-R2 0.8761 (delta -0.0008). **ROB-07 alt seeds:** test-R2 {1: 0.8774, 7: 0.8774, 123: 0.8769}. **ROB-08 alt-cut:** alt_cut_drop_SANTS - MONTJUÏC_test_r2 = 0.8778 vs baseline 0.8769.

**VAL-01 convergent** r(pred, sealed) = 0.9439. **VAL-02 discriminant** r(pred, richness) = 0.2527. **VAL-03 Jaccard** top-15 pred vs flag = 0.3636 (below 0.5: True). **VAL-04 OOD** districts with mean|resid|>0.10: [].
