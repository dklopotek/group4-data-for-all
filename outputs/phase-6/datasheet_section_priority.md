# Datasheet — `section_priority.parquet` / `.csv`

Gebru et al. (2021) datasheet for the Phase-6 deployment data product.

## 1. Motivation
Created to give a Barcelona greening planner a priority ranking at an **actionable, native grain**
(census section) for sequencing the committed plane-tree reduction by pollen-allergen exposure relief.
Created by Group 4 (MaAI01 25-26) for the CRISP-DM seminar; no external funder.

## 2. Composition
- **Instances:** 1,068 rows = Barcelona census sections (the full population, not a sample).
- **Fields:** `key` (section code, `DISTRICTE.zfill(2)+SEC_CENS.zfill(3)`), `district_lbl`,
  `plane_count`, `mature_count` (EXEMPLAR/PRIMERA Platanus), `exposure_pop` (residents),
  `source_std`, `exposure_std`, `priority` = source_std×exposure_std, `priority_std`, `geometry`
  (polygon, EPSG:25831). The `.csv` is the top-50 with a `rank`, no geometry.
- **Derived from:** street-tree inventory (40,444 Platanus), Padro 2026 population, section polygons.
- **No personal data.** All aggregate. 827 of 1,068 sections contain ≥1 plane; 11 Platanus fell
  outside all section polygons (edge) and are excluded.

## 3. Collection process
Spatial join of plane points (within section polygons) + native population join on section key.
Deterministic (`src/section_priority.py`, seed 42). Snapshot inputs hashed in `release/manifest.json`.

## 4. Preprocessing / cleaning
Platanus filtered by `cat_nom_cientific` prefix; maturity from `categoria_arbrat` (A1 assumption,
sensitivity-tested). No rows dropped from the section universe; zero-plane sections retained with 0.
Min-max standardisation per layer.

## 5. Uses
**Intended:** sequencing priority + the basis for the per-street worklist. **Known limitation that
shapes use:** at this grain the exposure re-ordering result does NOT hold (MAUP; T1 Spearman 0.97,
rollup vs 400 m 0.47) — treat as "large mature-plane clusters in populated sections," and read with the
400 m evidence grain. **Do not** use below section grain, as health evidence, or for street-level
priority.

## 6. Distribution & licence
In-repo under `outputs/phase-6/`. Data licence CC-BY-4.0; code MIT. DOI pending (Zenodo).

## 7. Maintenance
Maintainer: Group 4 (Rafik El Khoury) for the seminar; unmaintained-fork-freely after. Re-run on new
inventory/Padro (see `release/monitoring_plan.md`).

## 8. CRS & spatial notes
EPSG:25831 (ETRS89/UTM 31N) for area/joins; reprojected to EPSG:4326 only for the web map. Subject to
MAUP — see field-level note above and paper §8.
