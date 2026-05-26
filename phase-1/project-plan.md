# Project Plan

## Phase overview

| CRISP-DM Phase | Name | Duration | Status | Decision Gate |
|---|---|---|---|---|
| Phase 1 | Business Understanding | Complete (retrofitted 2026-05-26) | Artifacts in `phase-1/` | Exit checklist passed → Phase 2 |
| Phase 2 | Data Understanding | Sessions 1–2 (complete) | `docs/data-source-inventory.md`, `docs/data-quality-audit.md`, `docs/datasheets/`, `notebooks/01-data-profiling.ipynb` | Phase 2 companion skill → Phase 3 |
| Phase 3 | Data Preparation | Session 3 (in progress) | Notebooks 02–05 exist; need CRISP-DM retrofitting per `session-3/tasks.md` | All 5 notebooks pass P1–P5 validation → Phase 4 |
| Phase 4 | Modeling | Session 4 (upcoming) | Composite scoring + network analysis | Model output validated → Phase 5 |
| Phase 5 | Evaluation | Session 4 (upcoming) | Review against success criteria | All criteria met or limitations documented → Phase 6 |
| Phase 6 | Deployment | Session 4 (upcoming) | Final GeoJSON + product card + presentation | Submission |

## Session-level plan

### Session 3 (current) — Data Preparation

**Tasks:** See `session-3/tasks.md` for full breakdown.

- **P1–P4:** Retrofit notebooks 02–05 with CRISP-DM process documentation
- **P5:** New validation notebook (`00-data-validation.ipynb`)
- **D-DOMINIKA, D-JUAN:** Personal data layers with full CRISP-DM notebooks
- **DO1:** Session 3 README
- **DO2:** Restructure data-quality-audit with CRISP-DM framing

**Decision gate:** All notebooks log before/after row counts, design decisions, and bounds assertions. Validation notebook passes all range checks. Personal data layers exported. → Proceed to Phase 4.

### Session 4 (upcoming) — Modeling, Evaluation, Deployment

- Phase 4 (Modeling): Finalize composite scoring weights, network analysis thresholds, sensitivity analysis
- Phase 5 (Evaluation): Verify against success criteria in `phase-1/success-criteria.md`. Document all residual limitations.
- Phase 6 (Deployment): Package final GeoJSON, update product card, prepare presentation

**Decision gate:** All success criteria met or limitations explicitly documented. Product card finalized. → Submit.

## Initial tool assessment

| Tool | Purpose | Status |
|---|---|---|
| Python 3.13 | Core language | Installed |
| GeoPandas | Vector data processing | Installed |
| rasterio | Raster data processing | Installed |
| networkx | Network graph analysis | Installed |
| folium | Interactive HTML maps | Installed |
| matplotlib/seaborn | Static figures | Installed |
| scipy | Statistical functions | Installed |
| Jupyter | Notebook environment | Installed |
| Git | Version control | Current repo |

**Tool posture:** Python + open-source geospatial stack. No commercial tools. No cloud compute. All processing local.

## Quality gates (per CRISP-ML(Q))

| Gate | Phase | Check |
|---|---|---|
| G1 | Phase 1 → 2 | Decision statement, decision unit, output spec, and product card draft all on disk |
| G2 | Phase 2 → 3 | All adopted datasets have datasheets; data quality audit complete; ingestion log exists |
| G3 | Phase 3 → 4 | All transformations logged with before/after counts; bounds assertions pass; rejected rows have reason_codes |
| G4 | Phase 4 → 5 | Composite scores in [0,1]; intervention types valid; sensitivity analysis documented |
| G5 | Phase 5 → 6 | All success criteria verified; residual limitations documented; cancellation criterion re-checked |
| G6 | Phase 6 → submit | Clean clone reproducibility confirmed (or documented as best-effort); product card signed off |
