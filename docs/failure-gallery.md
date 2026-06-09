# Failure Gallery — `barrier-score-regressor-v1` (Cycle A) · TRACK A

> **Track A** (we built a model). This is the gallery of where the **Cycle-A mycorrhizal
> model** breaks — the model that scored test R² 0.877 and was then **stopped** in evaluation.
> A model with no documented failures hasn't been evaluated, it's been admired. Every number
> here is reproduced in `notebooks/05-evaluation.ipynb` (Cells A1–A5).
>
> **The rule:** ≥5 cases, each with a *mechanism*, not "the model isn't perfect."

- **Model:** linear regressor of `composite_score_B`, `outputs/phase-4/model_artifact.joblib`
- **Evaluated on:** `data/splits/test.parquet` (the frozen test cluster, n=88) + an **external**
  GBIF target the model never saw (`data/gbif-fungi-all.json`)
- **Maintainer:** Group 4 (Rafik El Khoury)
- **Last updated:** 2026-06-09

---

## The cases

> **Case 1:** The external null — the host/biotic layer carries no ecological signal *(the kill)*
> - **The input — what made it hard:** 99 cells with ≥1 independent GBIF fungal record — data
>   that never touched the pipeline. The honest question: after the abiotic null (sealed + NDVI
>   + sampling effort), does the biotic/host block (am/em/platanus/mismatch/PRPI/richness/trees)
>   add any explanatory power for *real* fungal richness?
> - **Predicted vs actual:** M0 abiotic Adj-R² **0.6972** → M1 + biotic **0.6777**. Adding the
>   ecological block moves Adj-R² *down* by **0.0195**; partial-F = 0.178, **p = 0.989**. Pass
>   needed Δ ≥ 0.05 and p < 0.05.
> - **Diagnosis — the mechanism that broke:** the claim the whole project rested on (AM→EM host
>   mismatch indexes belowground recovery) is not in the data. The block adds no information
>   about external fungal occurrence beyond effort and the paved/green surface. Holds under
>   log-richness (p 0.57) and drop-effort (p 0.54); residuals not spatially autocorrelated
>   (Moran's I −0.047, p 0.21), so it is not a spatial-autocorrelation artifact.
> - **Class:** **systematic** — it falsifies the claim, not one prediction. → became the STOP
>   verdict and out-of-scope use "not ecological evidence."

> **Case 2:** Drop `mean_sealed` — the model is a sealed-surface re-skin
> - **The input — what made it hard:** the production stress of one feature going missing. We
>   set `mean_sealed` to NaN on the test set (the median imputer fills it) and re-predict.
> - **Predicted vs actual:** intact test MAE **0.0106** → with sealed dropped **0.1205** — an
>   **11× degradation**, by far the largest of any feature.
> - **Diagnosis — the mechanism that broke:** the linear model leans almost entirely on
>   sealed-surface fraction (convergent r(pred, sealed) = 0.94). Remove it and the model is
>   blind. This confirms the internal finding: `composite_score_B` is approximately a re-skin of
>   `mean_sealed`, so the "barrier-severity" prediction is mostly "how paved is this cell."
> - **Class:** **systematic** — structural property of the target, not a data glitch.

> **Case 3:** Drop any biotic / tree feature — the ecological inputs do nothing
> - **The input — what made it hard:** the same drop-feature stress, applied to the
>   *ecological* features: `total_trees`, `trees_young_pct`, `species_richness`, `cell_vpa_score`.
> - **Predicted vs actual:** dropping each leaves test MAE at **0.0106 (Δ ≈ 0.0000)** — no
>   measurable change. (Dropping `am_pct`/`em_pct` changes MAE only because they algebraically
>   sum to a constant with `n_unknown`; their VIF is ∞.)
> - **Diagnosis — the mechanism that broke:** the features that encode the *ecological* claim
>   carry ≈ 0 weight. The model can lose them entirely and predict identically. An indicator
>   whose headline subject contributes nothing is not measuring that subject.
> - **Class:** **systematic** — across all four ecological features.

> **Case 4:** The Sarrià outlier cell — one prediction the linear fit cannot place
> - **The input — what made it hard:** the test cluster is the wealthy, hilly NW corner
>   (Sarrià-Sant Gervasi + Les Corts). One Sarrià cell sits far off the linear surface.
> - **Predicted vs actual:** single-cell **|residual| = 0.334** — about **32× the test MAE** and
>   the worst error in the test set. Sarrià mean |residual| 0.0174 (n=51); Les Corts 0.0011 (n=37).
> - **Diagnosis — the mechanism that broke:** a local non-linearity in a wealthy low-density cell
>   the additive model smooths over. District-level mean |residual| stays < 0.10 everywhere (OOD
>   gate passes), so this is **spectacular, not systematic** — but it sets the floor on
>   trustworthy resolution: do not discriminate two cells whose predicted scores differ < 0.03.
> - **Class:** **spectacular** — one cell.

> **Case 5:** Eval → test — a 6× calibration cost on out-of-sample geography
> - **The input — what made it hard:** held-out *spatial cluster* generalization (not random
>   rows) — the lecture-mandated honest test.
> - **Predicted vs actual:** MAE **0.0017** on eval → **0.0106** on the held-out test cluster —
>   a **6× degradation**; R² 0.999 → 0.877.
> - **Diagnosis — the mechanism that broke:** the composite's normalizations are computed on the
>   training geography; move to a geographically distinct cluster and absolute calibration drops.
>   The structure is approximately additive *locally*; precise calibration is geography-dependent.
> - **Class:** **systematic** — the spatial-generalization cost, present by construction.

> **Case 6 (methodological self-catch):** the presence model's AUC = 1.0 is circular
> - **The input — what made it hard:** a secondary logistic test of `gbif_present`.
> - **Predicted vs actual:** CV-AUC **1.0** for *both* M0 and M1; LR p 0.99996.
> - **Diagnosis — the mechanism that broke:** `gbif_present` was defined as `effort ≥ 1` and
>   `log_effort` is a covariate, so effort predicts presence **by construction**. The AUC is
>   mechanical, not evidence. We **discounted this row** and let the richness model carry the
>   verdict (logged as a dated addendum, not silently re-run). Catching "right for the wrong
>   reason" is itself a passed evaluation check.
> - **Class:** systematic (design artifact) — reported, down-weighted, not hidden.

---

## Stress-test results

> From `notebooks/05-evaluation.ipynb` Cell A3. Drop each feature to NaN (median imputer fills),
> re-predict on the test set. A crash would be a failure too — there are none; the failure mode
> is *graceful degradation that exposes what the model actually leans on.*

| Dropped feature | test MAE | Δ vs intact (0.0106) | Flag |
|---|---|---|---|
| `mean_sealed` | 0.1205 | **+0.110 (11×)** | DEGRADED |
| `em_pct` | 0.0596 | +0.049 | DEGRADED |
| `am_pct` | 0.0533 | +0.043 | DEGRADED |
| `mean_ndvi` | 0.0421 | +0.032 | DEGRADED |
| `lst_anomaly` | 0.0297 | +0.019 | OK-ish |
| `platanus_pct` | 0.0205 | +0.010 | OK |
| `cell_vpa_score` | 0.0106 | +0.000 | OK (no effect) |
| `species_richness` | 0.0106 | +0.000 | OK (no effect) |
| `total_trees` | 0.0106 | +0.000 | OK (no effect) |
| `trees_young_pct` | 0.0106 | +0.000 | OK (no effect) |

**Reading:** sealed surface (and to a lesser degree NDVI / the am-em pair) carry the model; the
genuinely ecological inventory features are inert. No input crashes the model — the imputer
absorbs missingness — so the failure is *interpretive*, not operational.

---

## Summary — what the gallery changes

- **New out-of-scope uses for the model card:** (1) not ecological/mycorrhizal evidence;
  (2) not for discriminating cells whose predicted scores differ < 0.03; (3) not calibrated for
  geographies unlike the training clusters without re-fit.
- **Refuse-to-show rules for S6:** any "fungal recovery" labelling of the Cycle-A map.
- **The verdict's "where it fails" row:** the external null (Case 1) — the model is technically
  excellent (R² 0.877) and ecologically empty (Δ −0.0195, p 0.989). That single contrast is the
  STOP decision.

---

## Sign-off

- **Gallery built by:** Group 4 (Rafik El Khoury)
- **Reviewed by another team:** pending (Session-5 cross-team review)
- **Entries:** 6 cases (≥5 required) + a 10-row stress-test table.
