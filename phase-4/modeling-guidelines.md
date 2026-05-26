# Phase 4 Modeling Guidelines — Mycorrhizal Barcelona

**Date:** 2026-05-26 (rewritten post Session 4 lecture)
**Status:** CURRENT — lecture-aligned. Supersedes the pre-lecture draft of this file.
**Canonical Phase 4 record:** `phase-4/analytical-question.md` + `phase-4/test-design.md` + `outputs/model-card-v1.md`.

---

## 1. What Phase 4 Does (per Session 4 lecture)

Session 4 (Lecture_4.md) defines Phase 4 as: **split → baseline → train one model → assess → write a model card with ≥ 3 NOTs**. The lecture is the rubric. This file follows it.

The pipeline ships TWO analytical cores per `crispdm-4-modeling §4`:

| Core | Family | Status | Canonical artefact |
|---|---|---|---|
| **B (headline)** | Interpretable regression — `LinearRegression` predicting `composite_score_B` from raw raster + tree-inventory features | **DONE** Session 4 | `outputs/model-card-v1.md` + `phase-4/test-design.md` |
| **A (wrap-up)** | Composite-indicator finalization for PRPI — sensitivity grid + stability + face validation per OECD/JRC (2008) | DEFERRED to follow-up session | Pre-registered in `phase-4/test-design.md §4–§6`; second model card pending at `outputs/model-card-prpi-v1.md` |

---

## 2. Core B (DONE) — lecture-mandated regression

Headline (test cluster, n = 88, k-means k = 5 split, seed 42):

| Estimator | R² | MAE | RMSE |
|---|---|---|---|
| **LinearRegression** | **0.877** | **0.0106** | **0.0509** |
| BaselineSpatialNearest | -0.290 | 0.130 | 0.165 |
| BaselineMean | -0.616 | 0.142 | 0.185 |
| BaselineDomainHeuristic | -0.622 | 0.143 | 0.185 |

Pre-registered pass criterion (beat all three baselines on test R² AND test MAE) — **PASS**.

Code: `src/split_data.py` + `src/baselines.py` + `src/train_model.py`. Reproduce with `python src/clean_data.py && python src/split_data.py && python src/train_model.py`.

Leakage controls and feature list: see `phase-4/analytical-question.md §5`.

---

## 3. Core A (DEFERRED) — PRPI composite finalization

This is the work for the next session. Pre-registered in `phase-4/test-design.md` and summarized here as the methodology checklist.

### 3.1 Sensitivity grid

Run `3 × 4 × 2 = 24` specifications of the PRPI composite and quantify per-cell rank stability:

| Fork | Variants |
|---|---|
| Normalization | min-max, min-max winsorized 5/95, z-score |
| Weighting | Scenario A equal, **Scenario B sealed-dominant (default)**, Scenario C heat+canopy, PCA on 4 sub-scores |
| Aggregation | linear weighted sum (default), geometric weighted product |

Per-cell **rank-stability count** = how many of 24 specs place the cell in the same tier as the default. ≥ 22/24 → ROBUST. < 18/24 → FRAGILE (flagged in PRPI model card §7).

Internal consistency: Cronbach's α across the 4 sub-scores within Scenario B (Nardo et al. 2005).

### 3.2 Grid-resolution sensitivity (MAUP)

Re-run scoring at 200m and 800m grids. Track:
- Top-15 cells at 400m → fraction remaining in top-quartile at 200m and 800m.
- `intervention_type` reassignment rate across resolutions.

### 3.3 Sub-score decomposition

PCA on the 4 sub-scores (494 × 4). Report variance explained per component. If PC1 > 80% → a single composite is justified; if < 50% → sub-scores are independent and weighted-sum conflates them.

Spearman ρ between all numeric columns of `scored_grid.parquet`. Flag:
- ρ > 0.8 → near-redundant column.
- ρ < 0.05 with `composite_score_B` → no information contribution.
- Theoretically unexpected correlations.

Histograms + ECDF per sub-score, with expected shapes (skill §7 internal-consistency check).

### 3.4 Spatial diagnostics

Per `crispdm-4-modeling §5 Route 4D`:

- **Global Moran's I** on `composite_score_B` with queen-contiguity weights on the 400m grid.
- **Local Moran's I (LISA)** per cell. Map High-High clusters (priority intervention zones) and Low-High outliers (isolated low-barrier cells in barrier zones — protect, don't develop).
- **FDR correction** on local p-values (Caldas de Castro & Singer 2006).
- **MAUP rerun** at one alternate resolution.

### 3.5 Stability checks (carryover from Core B)

- Jackknife: refit Core B Linear model dropping each of the 3 train clusters in turn; report coefficient stability.
- Gaussian noise injection (σ = 0.02 on features); refit; report test R² delta.

### 3.6 Construct validity

- Convergent: Pearson(predicted score, `mean_sealed`) — should be strongly positive.
- Discriminant: Pearson(predicted score, `species_richness`) — should be weak.
- Face validation: Jaccard overlap between top-15 predicted vs `top15_flag` from Phase 3. < 0.5 → investigate.

---

## 4. What Phase 4 must NOT do

Lecture lines 411–415:

- ❌ Generate fake / synthetic data (that is Session 5).
- ❌ Make galleries.
- ❌ Make UIs.
- ❌ Tune any secondary models — exactly one model gets tuned.
- ❌ Sweep multiple hyperparameters on the chosen model — one parameter only (`fit_intercept`).

---

## 5. Deliverables checklist

Session 4 (Core B) — DONE:

- [x] `phase-4/analytical-question.md`
- [x] `phase-4/test-design.md` (pre-registered + results appended)
- [x] `src/split_data.py`, `src/baselines.py`, `src/train_model.py`
- [x] `outputs/model-card-v1.md` (5 NOTs)
- [x] `outputs/phase-4/{metrics.csv, per_district.csv, predictions.parquet, model_artifact.joblib}`
- [x] `data/splits/{cluster_assignments, train, eval, test}.parquet`
- [x] `requirements.txt` updated (`scikit-learn`)
- [x] Pushed to GitHub for instructor review

Core A (follow-up session) — PENDING:

- [ ] `outputs/phase-4/sensitivity-grid.csv` — 24-spec rank-stability outputs
- [ ] `outputs/phase-4/variance-decomposition.md` — PCA + correlation matrix + sub-score calibration
- [ ] `outputs/phase-4/spatial-analysis.md` — Moran's I + LISA + FDR + MAUP
- [ ] `outputs/phase-4/stability.md` — jackknife + noise injection
- [ ] `outputs/model-card-prpi-v1.md` — Mitchell card for the PRPI composite
- [ ] `phase-4/limitations.md` — Phase-3 limitations carried forward + new Phase-4 findings

---

## 6. Evaluation criteria (per lecture)

Lecture lines 383–391 + 415–417:

| Criterion | What it means |
|---|---|
| Defensible split | Spatial cluster split, not random rows. **Done** (k = 5 k-means). |
| Defensible baseline | Beats baselines on the chosen metrics. **Done** (3 baselines, all beaten). |
| One tuned model | Linear regression, one hyperparameter swept. **Done**. |
| Train / eval / test metrics for every estimator | One segmented metrics table. **Done** (`outputs/phase-4/metrics.csv`). |
| ≥ 3 things the model is NOT for | In the model card. **Done** (5 NOTs). |
| Reproducible from one command | Yes. `python src/clean_data.py && python src/split_data.py && python src/train_model.py`. |
| Pushed to GitHub | Yes. Commit `3a4b9bb`, addendum `b77b554`. |

---

## 7. Key references

- Anselin, L. (1995). Local Indicators of Spatial Association — LISA. *Geographical Analysis*, 27(2), 93–115.
- Arlot, S. & Celisse, A. (2010). A survey of cross-validation procedures for model selection. *Statistics Surveys*, 4, 40–79.
- Caldas de Castro, M. & Singer, B. H. (2006). Controlling the false discovery rate. *Geographical Analysis*, 38(2), 180–208.
- Chapman, P. et al. (2000). *CRISP-DM 1.0: Step-by-Step Data Mining Guide*. SPSS.
- Mitchell, M. et al. (2019). Model cards for model reporting. *FAT* '19*, 220–229.
- Nardo, M. et al. (2005). *Tools for Composite Indicators Building*. JRC, EUR 21682 EN.
- OECD & JRC (2008). *Handbook on Constructing Composite Indicators*. OECD Publishing.
- Roberts, D. R. et al. (2017). Cross-validation strategies for data with spatial, temporal, or phylogenetic structure. *Ecography*, 40(8), 913–929.
- Rudin, C. (2019). Stop explaining black box machine learning models for high stakes decisions and use interpretable models instead. *Nature Machine Intelligence*, 1(5), 206–215.
- Saltelli, A. et al. (2008). *Global Sensitivity Analysis: The Primer*. Wiley.
- Tobler, W. R. (1970). A computer movie simulating urban growth in the Detroit region. *Economic Geography*, 46(sup1), 234–240.

---

**Rewritten by:** Claude (Opus 4.7, 1M ctx) at user request to override the pre-lecture stance and align this file with Session 4 lecture rubric. The earlier "do NOT train models" framing is removed.
