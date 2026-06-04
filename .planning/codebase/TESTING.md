# Testing & Validation

_Mapped: 2026-06-04_

---

## Test Framework

**NO unit tests exist.** Search confirms zero `test_*.py` or `*_test.py` files in the repository. No pytest, unittest, or similar framework is configured.

This is **not accidental**. The CRISP-DM pipeline is data-centric, not code-unit-centric. Quality assurance is delegated to **data validation, schema contracts, and pre-registered test plans** (see sections below). Code quality is enforced via assertions and graceful fallbacks, not unit mocks.

---

## Data Validation (the real "tests")

**Phase 3 data contract** (`phase-3/data-contract.yaml`): formal schema specifying every output column for `scored_grid.geojson` (GeoJSON output of `clean_data.py`).

Schema documents:
- Column name, dtype (int, float, str, geometry), nullability, range, and rationale.
- Example: `am_pct` (0–100 scale, non-null, int, "Percentage of known-type trees that are AM hosts").
- Example: `n_AM` (int, non-null, >=0, "Number of arbuscular mycorrhizal host trees").
- Example: `s4_shift_ceiling_reached` (bool, non-null, "Cell remains AM-dominant even after replacement").

**Assertion gates in code** enforce schema invariants:

1. **Non-empty outputs** (lines 363, 596, 747):
   ```python
   assert len(out) > 0, "Tree inventory is empty after loading"
   assert len(out) > 0, "Grid is empty — boundary may be invalid"
   assert len(agg) > 0, "Cell aggregation produced zero rows"
   ```

2. **Null completeness** (line 521):
   ```python
   assert out["myco_type"].notna().all(), "Some trees have null myco_type"
   ```

3. **Range conformance** (lines 985, 1091, 1041, 1249):
   ```python
   out["s1_sealed"] = out["mean_sealed"].clip(0, 1)
   out["s3_inverted_ndvi"] = (1 - normalised).clip(0, 1)
   assert (out["s2_lst_anomaly"].between(0, 1)).all(), ...
   assert (out["prpi"].between(0, 1)).all(), "PRPI out of [0, 1] range"
   ```

4. **Weight sums** (lines 1246–1248):
   ```python
   assert (abs(sum(w.values()) - 1.0) < 1e-6), f"PRPI_WEIGHTS sum to {sum(w.values()):.4f}, not 1.0"
   ```

5. **Type consistency** (lines 754, 814):
   ```python
   out["n_AM"] = int(am)
   out["species_richness"] = int(rich)
   ```

These assertions act as **data quality gates** — if a stage produces invalid output, the pipeline stops immediately with a clear message.

**Phase 3 verification document** (`phase-3/session-3-verification.md`): post-hoc checklist (after `clean_data.py` runs) documenting:
- Inventory row counts by source (street vs. park).
- Species distribution and top-20 coverage.
- Null rates per column.
- Grid cell occupancy (how many trees per cell, min/max/mean).
- Score distributions (histograms, percentiles).
- Assertions that should have passed (they did).

---

## CI / Automation

**NO GitHub Actions or CI pipeline.** Project is a seminar deliverable (due 2026-06-05). No merge queue, branch protection, or automated tests on push.

**Reproducibility ensured by:**
- Fixed `RANDOM_SEED = 42` (lines 44 in `split_data.py`, line 132 in `clean_data.py`) so K-means and fallback synthetic values are deterministic.
- Locked dependencies: `requirements.txt` (lines 6–42) pins exact versions (`pandas==3.0.3`, `numpy==2.4.6`, etc.).
- Immutable data paths: all file paths derived from `PROJECT_ROOT`, so pipeline runs correctly from any working directory.

**One-command reproducibility:**
```bash
python src/clean_data.py      # Reads raw/* → outputs scored_grid.geojson
python src/split_data.py      # Reads scored_grid → outputs train/eval/test splits
python src/train_model.py     # Reads splits → outputs metrics, predictions, model artifact
```

No env vars, no config files, no interactive prompts. All parameters are code constants, making the pipeline **auditable**: run `grep GRID_SIZE src/clean_data.py` to see that the grid is 400m.

---

## Reproducibility Checks

**Seed control:**
- `RANDOM_SEED = 42` in `split_data.py` (line 44) locks K-means initialization.
- `RNG_SEED = 42` in `clean_data.py` (line 132) locks synthetic fallback rasters (lines 978, 1024, 1075).
- `sklearn.cluster.KMeans(..., random_state=RANDOM_SEED, n_init=10)` (line 70 in `split_data.py`) ensures no variance from initialization.

**Deterministic clustering:** Cluster assignments are remapped by descending size (lines 73–76 in `split_data.py`) so the train/eval/test split is deterministic across re-runs — even if K-means found a different local optimum, the cluster-to-split mapping would be the same.

**Pinned dependencies:** All direct imports have version constraints (requirements.txt lines 6–42). No `==latest` or unversioned deps. Python 3.12+ required (specified at top of requirements.txt).

**Frozen test set:** Lecture 4 line 313 mandates: "test cluster is frozen on first write and must not be inspected until final assessment." Implementation in `write_splits` (lines 102–115 in `split_data.py`) writes `cluster_assignments.parquet` once; code does not re-run K-means or reshuffle. If you want to change the split, you must delete the file and re-run.

---

## Model / Output Validation

**Phase 4 test design** (`phase-4/test-design.md`, lines 1–151): pre-registered test plan written BEFORE the model was built (audit-trail requirement per Lecture 4 line 273).

Test plan specifies:

### 1. Split design
- **Strategy:** spatial cluster K-means on cell centroids (x, y in EPSG:25831), k=5.
- **Rationale:** Lecture line 291: "group them together… holds out an entire region… get more variances."
- **Mapping:** Clusters sorted by size descending → deterministic assignment to train (3), eval (1), test (1).
- **Frozen:** Test cluster never inspected until final metrics reported.

### 2. Baselines (must beat all three on test R² AND test MAE)
| Baseline | Rule | Rationale |
|----------|------|-----------|
| **BaselineMean** | Predict train mean of `composite_score_B` for every test cell | Lecture: floor — model must capture signal beyond bulk average |
| **BaselineSpatialNearest** | For each test cell, predict target of nearest train cell by Euclidean (x, y) distance | Lecture: captures pure-geography signal |
| **BaselineDomainHeuristic** | `if mean_sealed > 0.7 → 90th-pct of train target; else → train mean` | Lecture: "what engineers already know" — sealed surface = barrier |

**Results** (from phase-4/test-design.md lines 108–122): LinearRegression **PASSES** all criteria:
- Test R²: 0.8769 (vs. best baseline -0.2898)
- Test MAE: 0.0106 (vs. best baseline 0.1298)

### 3. Model
- **Family:** Linear regression (`sklearn.linear_model.LinearRegression`).
- **Features:** 10 raw signals (mean_sealed, mean_ndvi, lst_anomaly, am_pct, em_pct, platanus_pct, cell_vpa_score, species_richness, total_trees, trees_young_pct).
- **Imputation:** Median fill on 7 columns (fit on train, reused on eval + test).
- **Tuning:** Exactly one hyperparameter: `fit_intercept ∈ {True, False}`. Chosen on eval (MAE criterion). Lecture line 415: "please only tune one."
- **No regularization, no polynomial features.**

### 4. Construct validity checks
| Check | Method | Result |
|-------|--------|--------|
| **Convergent** | Pearson r between predicted score and `mean_sealed` | Should be positive and strong (sealed is dominant driver) |
| **Discriminant** | Pearson r between predicted score and `species_richness` | Should be weak (richness loosely related) |
| **Expert face validation** | Compare top-15 predicted cells to Phase 3 `top15_flag` | Report Jaccard overlap; <0.5 = concerning |
| **OOD probe** | Residual distribution by district on test cluster | Flag districts with mean abs residual > 0.10 |

Results: both districts within OOD gate (lines 132–137 in test-design.md). One outlier cell flagged.

### 5. Sensitivity analysis (Core A — deferred)
Full factorial: 3 normalizations × 4 weighting schemes × 2 aggregations = **24 specifications**. For each, rank cells and count "rank-stability" (how many specs place cell in same tier as default). Cronbach's alpha on sub-scores. Moved to Core A wrap-up (test-design.md line 147).

### 6. Stability checks (deferred)
- **Jackknife on train clusters:** refit dropping each of 3 train clusters; report coefficient stability.
- **Noise injection:** add Gaussian noise σ=0.02 to features, refit, compare test R².
Moved to Core A wrap-up (line 148).

### 7. Per-district residuals
Table in test-design.md lines 131–137: residuals by district on test set. Both districts have mean abs residual < 0.10. Sarrià-Sant Gervasi has higher absolute residuals, flagged as geography-specific fragility.

---

## Model Card & Artifact

**Model artifact** (`outputs/phase-4/model_artifact.joblib`): joblib dump of:
- Fitted `Pipeline` (imputer + LinearRegression).
- `features`: list of 10 feature columns (in order).
- `target`: "composite_score_B".
- `tune_info`: dict with tune_table (both fit_intercept options) and chosen hyperparameter.
- `version`: "phase-4-v1".

Artifact is self-contained; user can load and call `model.predict(X)` without re-running training.

**Predictions parquet** (`outputs/phase-4/predictions.parquet`): all cells + splits with columns:
- `cell_id`, `district`, `split`, `y_true` (composite_score_B).
- `y_pred__BaselineMean`, `y_pred__BaselineSpatialNearest`, `y_pred__BaselineDomainHeuristic`, `y_pred__LinearRegression`.

Allows post-hoc validation: user can recompute metrics, plot residuals, slice by district, without re-running the model.

**Metrics CSV** (`outputs/phase-4/metrics.csv`): table of (estimator, split, n, r2, mae, rmse) for all 4 estimators × 3 splits = 12 rows.

---

## Gaps & Risks

### Untested that should be:

1. **Integration across phases:** Phase 3 output (scored_grid.geojson) is consumed by Phase 4 (split_data.py, train_model.py). But no integration test checks:
   - If clean_data.py's output schema exactly matches what split_data.py expects.
   - If missing columns cause an error (vs. graceful fallback).
   - If CRS mismatch between phase-3 output and phase-4 input is caught early.

   **Mitigation:** Phase-4 scripts have explicit column checks (e.g., `assert "composite_score_B" in gdf.columns` in split_data.py line 61), so errors surface quickly.

2. **Raster absence:** Fallback synthetic values are used if rasters are absent (lines 977–983, 1027–1030, 1075–1080 in clean_data.py). These are "illustrative only" but indistinguishable from real data in the output. User must inspect `s1_sealed`, `s2_lst_anomaly`, `s3_inverted_ndvi` distributions to detect fallback (e.g., synthetic Beta will have different quantiles than real sealed-surface raster).

   **Mitigation:** Explicit warning printed to stdout when fallback is used. Recommendation: always provide rasters.

3. **Species name normalization:** Lowercasing + stripping handles most cases, but compound names (e.g., "Platanus × acerifolia" vs. "Platanus x acerifolia") may not match. FungalRoot lookup then falls back to NM (Not Matched), which is silent in per-cell aggregation.

   **Mitigation:** Top-20 hardcoded override (lines 223–247) catches the most common species. Species not in top-20 + not in FungalRoot will be marked NM; user can inspect the NM count to detect systematic misses.

4. **GBIF phylum parsing:** Assumes "basidiomycota" (lowercase) to detect putative EM fungi. If GBIF JSON uses "Basidiomycota" or "BASIDIOMYCOTA", the filter fails silently (line 915–916).

   **Mitigation:** Case-insensitive `.str.lower()` applied before check. But if GBIF schema changes (e.g., "division" instead of "phylum"), code breaks without error.

5. **Boundary polygon validity:** If boundary GeoJSON is a MultiPolygon or has self-intersections, `boundary.union_all()` (line 560) may behave unexpectedly. No validation of polygon topology.

   **Mitigation:** Fallback hardcoded bbox (lines 562–567) ensures grid is still built; user will notice if cells are off-extent.

6. **Model leakage:** Feature list is manually curated (train_model.py lines 45–56). If a Phase-3 sub-score (e.g., `s4_mismatch`) is accidentally included as a feature, leakage occurs but is not detected (model will fit perfectly on eval).

   **Mitigation:** phase-4/analytical-question.md §5 documents the feature list and explicitly states "raw measured signals only, no Phase-3 sub-scores." Code comments would strengthen this.

7. **Test set inspection:** Lecture 4 mandates frozen test set (line 313). But there is no code enforcement — if a user loads `test.parquet` and uses it for tuning, the code will not complain.

   **Mitigation:** Social contract (documented in test-design.md). Code comments in train_model.py should mark the test load as "FROZEN — do not tune on this."

---

## Recommendations

### Low-hanging fruit
1. Add integration test: run `clean_data.py` → `split_data.py` → `train_model.py` end-to-end, check output schemas match.
2. Add data-quality audit notebook: load scored_grid, check column presence, ranges, null rates, distribution plots.
3. Add test-set guard comment: "FROZEN — test cluster not to be inspected or used for tuning" in train_model.py main.

### Medium-term
4. Document raster-absence fallback visibly in outputs (e.g., add `s1_is_synthetic`, `s2_is_synthetic` flags to scored_grid).
5. Add species normalization test: load FungalRoot + top-20 override, check coverage of top-100 inventory species.
6. Implement leakage checker: script that compares FEATURE_COLS against list of computed sub-scores in scored_grid, warns on overlap.

### Stretch
7. Unit tests on helper functions (`_normalise_myco`, `_modal`, `_young_pct`) to catch edge cases.
8. Property-based testing on score calculations (e.g., "all scores are in [0, 1]") using hypothesis library.

---

## Summary Table

| Aspect | Status | Coverage |
|--------|--------|----------|
| **Unit tests** | NONE | Data validation + assertions instead |
| **Data schema** | FORMAL | phase-3/data-contract.yaml specifies every output column |
| **Assertions** | COMPREHENSIVE | Non-empty, null-free, range checks, weight sums |
| **CI / Automation** | NONE | Reproducibility via seed control + pinned deps |
| **Determinism** | LOCKED | RANDOM_SEED, grid snapping, frozen test set |
| **Baselines** | PRE-REGISTERED | 3 baselines; model must beat all on test R² + MAE |
| **Model validation** | DOCUMENTED | test-design.md: splits, baselines, construct validity, OOD probe |
| **Sensitivity analysis** | DEFERRED | 24 specs planned; moved to Core A wrap-up |
| **Stability checks** | DEFERRED | Jackknife + noise injection; moved to Core A wrap-up |
| **Raster fallback** | GRACEFUL | Synthetic Beta/Normal if absent; logged to stdout |
| **Test set integrity** | SOCIAL | Frozen by design; no code enforcement yet |

