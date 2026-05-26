# Profiling Plan — 8-Cell EDA Checklist

Per CRISP-DM Phase 2 Task 2 (Describe Data) and Task 3 (Explore Data). Adapted from the earn-the-data Step 9 template and executed in `notebooks/01-data-profiling.ipynb`.

## Profiling cells executed

| Cell | Dataset | Check | Status |
|------|---------|-------|--------|
| 1 | Ajuntament Trees | Load & combine street + park CSVs | Done — 189,090 rows, 23 cols |
| 2 | Ajuntament Trees | Shape & dtypes | Done — mixed str/float/int |
| 3 | Ajuntament Trees | Missing values (NA%) | Done — catalogacio 99.5%, planting_date 81% |
| 4 | Ajuntament Trees | Coordinate bounds & district coverage | Done — all 10 districts present, no OOB coords |
| 5 | Ajuntament Trees | Categorical cardinality | Done — 381 unique species, 10 districts |
| 6 | Ajuntament Trees | Species taxonomy: genus-only check | Done — 25 records (0.01%) genus-only |
| 7 | Ajuntament Trees | Top-20 species composition | Done — AM-host dominance confirmed |
| 8 | Ajuntament Trees | Planting date completeness & temporal range | Done — 81% missing, anomalies flagged |
| 9 | Ajuntament Trees | Anomaly hunt (coords, IDs, dates) | Done — 6 invalid districts, 28 future dates, 8 pre-1900 |
| 10 | Ajuntament Trees | Profile summary → JSON | Done — `data/profile-summary.json` |
| — | GBIF Fungi | Spot-check: record count, basisOfRecord | Done — 1,023 records, 98.3% HUMAN_OBSERVATION |
| — | GlobalAMFungi | Portal query attempt | Blocked — JS-only portal, retained INVESTIGATE |

## Cells still needed (deferred to Session 3 data prep)

| Cell | Dataset | Check | Reason deferred |
|------|---------|-------|-----------------|
| P1 | Urban Atlas | Sealed-surface raster: bounds, nodata, projection | Not ingested at profiling time |
| P2 | Sentinel-2 | NDVI composite: cloud mask %, scene count | Not ingested at profiling time |
| P3 | Landsat LST | Thermal band: valid range, emissivity flags | Not ingested at profiling time |
| P4 | FungalRoot v2.0 | Join table: species coverage against tree inventory | Deferred to notebook 03 scoring pipeline |
| P5 | All spatial | CRS cross-check: all layers reprojected to EPSG:25831 | Deferred to notebook 02 grid generation |

## Profiling tool posture

- **Tool:** Python 3.13 + pandas + matplotlib + seaborn
- **Notebook:** `notebooks/01-data-profiling.ipynb`
- **Output:** `docs/data-quality-audit.md` (narrative) + `data/profile-summary.json` (machine-readable)
- **No commercial tools. No cloud compute.**

## Sign-off

Profiling plan executed for the PRIMARY dataset (Ajuntament Trees) and spot-checked for GBIF. Remaining auxiliary datasets deferred to Session 3 ingestion pipeline.

**Date:** 2026-05-01
**Profiled by:** Rafik
