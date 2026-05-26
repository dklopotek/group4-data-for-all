# Phase 4 — Analytical Question

**Date:** 2026-05-26
**Author:** Rafik El Khoury (Group 4)
**Status:** locked
**Lecture anchor:** `MaAI01 25-26 - T03S13_Data -- DOCUMENTS/Session 4/Lecture_4.md`
**Skill anchor:** `crispdm-4-modeling §3` (required inputs)

---

## 1. Canonical analytical question (one sentence)

> For each 400m × 400m grid cell over Barcelona, the pipeline outputs a **predicted barrier-severity score in [0, 1]** that estimates `composite_score_B` (sealed-dominant scenario) from a small set of geospatial features, and is validated against held-out spatial clusters.

**Unit of analysis:** the 400m grid cell (`cell_id`), n = 494.
**Output type:** a continuous number in [0, 1].
**Concept measured:** mycorrhizal-network barrier severity, sealed-dominant scenario (Scenario B from Phase 3 PRPI v1.2).

## 2. Why this is the question (vs alternatives)

Two candidate questions surfaced:

| Candidate | Verdict |
|---|---|
| (a) "For each cell, output a ranked priority for capital allocation." | The Phase 3 composite (`composite_score_B`) is already the ranked priority. Re-running the composite is not Phase 4 work — it is Phase 3 work re-skinned. Rejected as Core B headline. |
| (b) **"For each held-out cell, predict `composite_score_B` from a feature subset."** | Treats Phase 4 as a predictive-modeling validation step — the lecture's framing. Forces a defensible split, a defensible baseline, and a per-segment model card. **Selected.** |

The lecture explicitly frames Phase 4 as: *"now we look at it. Today we actually build the systems that we said we wanted to build."* (lines 246–247). The skill permits multiple analytical cores; here we run Core B (predictive validation per lecture) as the headline, and Core A (PRPI composite sensitivity per skill §5 Route 4A) as a wrap-up artifact so both lecture rubric and skill exit criteria are satisfied.

`prpi_operational` (v1.2) becomes a secondary segment in the model card's per-segment metrics table.

## 3. Decision the output informs

A capital-planning analyst at **Ajuntament de Barcelona — Espais Verds / Barcelona Regional** uses the per-cell predicted barrier score to allocate **Eixos Verds / Superilla** intervention budget for the FY-2026 round. The score is consumed alongside the Phase 3 `intervention_type` column to choose between de-paving, cooling, planting, multi-strategy, or species-replacement actions.

Concretely: the analyst ranks cells by predicted score, takes the top decile, cross-references `intervention_type`, and slots them into the 2026 capital plan.

## 4. Phase 1 success criterion (in non-modeling language)

A successful Phase 4 model:

1. Predicts `composite_score_B` on **held-out spatial clusters** with R² and MAE meaningfully better than each of three baselines (dumb mean, spatial nearest, domain heuristic).
2. Holds within a calibrated error margin across districts — no district where the model is systematically wrong.
3. Comes with a model card that lists **at least three things the model is NOT for** (lecture line 405).
4. Is reproducible end-to-end from one command on a fresh checkout.
5. Reports train / eval / test metrics for every model AND the three baselines in one segmented table (lecture lines 385–390).

## 5. Prepared dataset

| Field | Value |
|---|---|
| Source artifact | `data/processed/scored_grid.parquet` (also `.geojson`) |
| Row count | 494 cells |
| Column count | 51 |
| Primary key | `cell_id` |
| Geometry CRS | EPSG:25831 |
| Data contract | `phase-3/data-contract.yaml` v1.2.0 |
| Lineage | Phase 3 commit `859bda9` |
| Datasheet | `phase-3/datasheets/scored-grid.md` |

**Target column for Core B:** `composite_score_B`.

**Feature columns for Core B (raw signals, no leakage):** `mean_sealed`, `mean_ndvi`, `lst_anomaly`, `am_pct`, `em_pct`, `platanus_pct`, `cell_vpa_score`, `species_richness`, `total_trees`, `trees_young_pct`.

**Leakage check.** The following columns are **EXCLUDED** because they are derived from or correlated by construction with the target:
- `s1_sealed`, `s2_lst_anomaly`, `s3_inverted_ndvi`, `s4_mismatch`, `prpi` — direct sub-scores summed into the composite. Including them would let a linear model recover the weights exactly (trivial leak).
- `composite_score_A`, `composite_score_C` — sibling composites built from the same sub-scores.
- All `s*_contribution_pct` columns — by-construction ratios of the target.
- `top15_flag`, `replacement_priority` — derived from the target via threshold.

The point of Phase 4 is to test whether raw measured signals (sealed-surface raster, LST raster, NDVI raster, tree-inventory aggregates) can recover the composite — i.e., whether the composite carries information beyond a linear combination of its own raw inputs. If yes, the composite is informative; if no, the composite is just a re-skin of `mean_sealed` and we should rethink Phase 3.

## 6. Pipeline-project confirmation (skill §3.5)

This is a pipeline project, NOT an ML training project. The dominant test-design family is **sensitivity analysis** for Core A (PRPI composite) and **spatial cross-validation** for Core B (regression). Lecture requires exactly one tuned model (line 415). Lecture forbids fake data, galleries, UI, secondary-model tuning (line 415). All these constraints carry forward.

## 7. Routing (skill §4 decision tree)

| Core | Route | Anchor |
|---|---|---|
| **B (headline)** | Route 4C — interpretable regression | Lecture §"80/20 modeling"; Rudin (2019) interpretable-models gate passes (linear regression on 10 features is fully interpretable) |
| **A (wrap-up)** | Route 4A — composite indicator finalization | OECD/JRC (2008); already built in Phase 3, needs sensitivity grid + model card |

Both cores get separate model cards. Skill §10 anti-pattern 11 (no composite + network mega-score) honored: Core A and Core B stay separate artifacts, never fused into a single score.
