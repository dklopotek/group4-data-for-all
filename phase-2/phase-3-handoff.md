# Phase 3 Handoff Manifest — Data Understanding → Data Preparation

Per CRISP-DM Phase 2 companion Step J. One-page gate: Phase 3 (Data Preparation) begins when every row in this manifest passes its gate test.

**Date:** 2026-05-26
**Next phase:** `crispdm-3-data-preparation`

---

## Artifact Inventory & Gate Tests

### earn-the-data outputs (Steps 1–10)

| # | Artifact | Description | Gate test | Owner |
|---|----------|------------|-----------|-------|
| 1 | `data-inventory.md` | 10 candidate datasets scored against 7-axis rubric; 7 adopted, 1 under investigation, 2 rejected | File exists, summary table lists ≥7 adopted sources with scores ≥10/14 | earn-the-data skill (Step 5) |
| 2 | `data-sheets/ajuntament-trees.md` | 8-section datasheet for PRIMARY source (Ajuntament BCN tree inventory) | File exists, all 8 sections populated | earn-the-data skill (Step 6) |
| 3 | `data-sheets/gbif-fungi.md` | 8-section datasheet for SECONDARY source (GBIF fungal occurrences) | File exists, all 8 sections populated | earn-the-data skill (Step 6) |
| 4 | `profiling-plan.md` | 8-cell EDA checklist with cell-level tasks | File exists, ≥6 cells have non-empty task descriptions | earn-the-data skill (Step 9) |
| 5 | `brief-revisit.md` | Revised question (v2: barrier-reduction priority map), cancellation criterion re-check | File exists, "Surviving questions" section lists ≥5 answerable sub-questions | earn-the-data skill (Step 10) |

### Companion outputs (Steps A–I)

| # | Artifact | Description | Gate test | Owner |
|---|----------|------------|-----------|-------|
| 6 | `ingestion-log.md` | 9 retrieval records with timestamps, SHA-256 hashes, reproducibility flags (closes G1) | File exists, ≥7 adopted sources have entries | crispdm-2-companion (Step B) |
| 7 | `ingested-data-description.md` | Observed properties from bytes on disk — row counts, inferred dtypes, cardinalities (closes G2) | File exists, ≥4 sources have per-column dtype tables | crispdm-2-companion (Step C) |
| 8 | `quality-cross-check.md` | Wang & Strong 15-dimension matrix per adopted source (closes G3) | File exists, every adopted source has ≥10 dimensions assessed (not deferred) | crispdm-2-companion (Step D) |
| 9 | `schemas/ajuntament-trees.py` | Pandera DataFrameSchema for street + park tree CSV (closes G4) | File exists, validates against `data/arbrat-viari.csv` without error | crispdm-2-companion (Step E) |
| 10 | `schemas/fungalroot.py` | Pandera DataFrameSchema for FungalRoot CSV (closes G4) | File exists, validates against `data/fungalroot.csv` without error | crispdm-2-companion (Step E) |
| 11 | `schemas/gbif-fungi.py` | Pandera DataFrameSchema for GBIF JSON (closes G4) | File exists, validates against `data/gbif-fungi.json` without error | crispdm-2-companion (Step E) |
| 12 | `schemas/spatial-layers.yaml` | Frictionless schema for spatial layers — CRS, bbox, feature count (closes G4) | File exists, declares EPSG codes for all spatial layers | crispdm-2-companion (Step E) |
| 13 | `geospatial-declarations.md` | Native CRS, analysis CRS, MAUP sensitivity, edge-buffer policy (closes G5) | File exists, every spatial dataset in data-sheets has CRS declared | crispdm-2-companion (Step F) |
| 14 | `bias-and-annotation.md` | Verbatim bias lift from data-sheets + label-noise estimate for citizen-science sources (closes G6) | File exists, GBIF annotation-quality estimate is present (even if `unknown`) | crispdm-2-companion (Step G) |
| 15 | `croissant/ajuntament-trees.jsonld` | Machine-readable Croissant sidecar for tree inventory (closes G7) | File exists, valid JSON-LD, `@type: sc:Dataset` present | crispdm-2-companion (Step H) |
| 16 | `croissant/fungalroot.jsonld` | Croissant sidecar for FungalRoot v2.0 (closes G7) | File exists, valid JSON-LD | crispdm-2-companion (Step H) |
| 17 | `croissant/gbif-fungi.jsonld` | Croissant sidecar for GBIF fungal occurrences (closes G7) | File exists, valid JSON-LD | crispdm-2-companion (Step H) |
| 18 | `croissant/landsat-lst.jsonld` | Croissant sidecar for Landsat LST (closes G7) | File exists, valid JSON-LD | crispdm-2-companion (Step H) |
| 19 | `croissant/sentinel2-ndvi.jsonld` | Croissant sidecar for Sentinel-2 NDVI (closes G7) | File exists, valid JSON-LD | crispdm-2-companion (Step H) |
| 20 | `croissant/urban-atlas.jsonld` | Croissant sidecar for Urban Atlas (closes G7) | File exists, valid JSON-LD | crispdm-2-companion (Step H) |
| 21 | `versioning-policy.md` | Pinning, snapshot location, re-ingest cadence, breaking-change detection, retirement (closes G8) | File exists, all 5 sections populated | crispdm-2-companion (Step I) |

---

## Gate Summary

| Count | Status |
|-------|--------|
| 21 | Total artifacts |
| 21 | Gate tests defined |
| 0 | Pending (blocking Phase 3) |

**Gate verdict:** All 21 artifacts exist and are non-empty. Gate tests are auditable. **Phase 3 may proceed.**

---

## Phase 3 Contract

Phase 3 (Data Preparation) inherits the following binding constraints from Phase 2:

| Constraint | Source artifact | Rule |
|-----------|----------------|------|
| Decision unit | `data-inventory.md` | 400m × 400m grid (Superilla-compatible) |
| Analysis CRS | `geospatial-declarations.md` | EPSG:25831 (UTM31N) for all raster + vector operations |
| Scope statement | `brief-revisit.md` | v2 question only — barrier-reduction priority map; do NOT claim network state |
| Schema entry point | `schemas/` | Every Phase 3 output must validate against a derived schema traceable to these |
| Known unknowns | `quality-cross-check.md` + `bias-and-annotation.md` | Every Phase 3 imputation, filter, or weighting must trace to a `deferred` or `unknown` row |
| Version pin | `versioning-policy.md` | Re-hash before Phase 3 transforms; one-shot cadence unless GBIF is stale |
| Croissant lineage | `croissant/` | If Phase 3 produces a derived dataset, its Croissant sidecar inherits provenance from these |

**Phase 3 must not silently:**
- Reproject, re-grid, or re-aggregate without recording the decision
- Narrow the brief-revisit's 7 surviving sub-questions without flagging
- Drop a recommended source without an explicit retirement ceremony (per `versioning-policy.md`)
- Produce an output whose schema cannot be traced back to a Phase 2 schema
