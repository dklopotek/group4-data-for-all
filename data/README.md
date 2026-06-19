# `data/` — Raw inputs to the pipeline

Large raw files are gitignored. Re-download from the sources below before running
any notebook or `src/*.py` script. SHA-256 hashes: `phase-2/ingestion-log.md`.
Datasheets, schemas, and Croissant ML records: `phase-2/`.

---

## Data journey at a glance

Every source feeds `src/clean_data.py` → `data/processed/scored_grid.parquet` (the single source of truth).

| # | Source | Data type | Raw format | Output column(s) in `scored_grid.parquet` | Key cleaning step |
|---|---|---|---|---|---|
| 1 | Ajuntament trees | Tabular — municipal asset register | CSV · 43 MB + 14 MB · UTF-8 | `total_trees`, `am_pct`, `em_pct`, `platanus_count`, `colonisation_uncertain` | Normalise species to `genus species`; join FungalRoot; flag 24% unmatched as `myco_type='unknown'`; drop 36 irrelevant columns |
| 2 | FungalRoot v2.0 | Tabular — species trait lookup | CSV · 379 KB | In-memory join only (not stored) | Collapse 11 raw text categories → AM / EM / NM / unknown |
| 3 | GBIF fungi | Point occurrences — biodiversity | JSON · 3 MB (BCN) + 9 MB (Catalonia) | `gbif_obs` | Filter to coords + uncertainty ≤100 m; bin to presence/absence per cell (no abundance — observer-effort bias) |
| 4 | BCN boundaries | Vector — administrative polygons | GeoJSON · EPSG:4326 | Grid clip extent + `districte` label | None; reproject EPSG:4326 → EPSG:25831 in memory |
| 5 | Urban Atlas 2018 | Raster — sealed-surface fraction | FlatGeobuf · 206 MB · EPSG:3035 · values 0–1 | `sealed_surface` | **BUG-3 fix:** scale was misread as 0–100; corrected to 0–1; reproject EPSG:3035 → EPSG:25831 |
| 6 | Landsat 8/9 LST | Raster — land surface temperature | GeoTIFF · 3.1 MB · EPSG:32631 · °C | `lst_mean` | QA_PIXEL inspection deferred; reproject EPSG:32631 → EPSG:25831 |
| 7 | Sentinel-2 NDVI | Raster — vegetation index | GeoTIFF · 33.5 MB · EPSG:32631 · −1 to 1 | `ndvi_mean` | SCL cloud mask (classes 8, 9, 10 excluded) at compositing; reproject EPSG:32631 → EPSG:25831 |
| 8 | CALIOPE-Urban NO2 | Tabular — air quality model output | CSV · census-tract grain · annual mean NO2 µg/m³ | Potency modifier on exposure score (Phase 6 only) | Join on `ID_census` last-5 = section `key`; use March–April mean (`Dataset2B`), not annual mean |

Full cleaning decisions and residual concerns: `phase-3/data-cleaning-report.md`.

---

## Download instructions

### 1. Ajuntament BCN tree inventory (PRIMARY)

| | |
|---|---|
| Files | `data/arbrat-viari.csv` · `data/arbrat-zona.csv` |
| License | CC-BY 4.0 — *Ajuntament de Barcelona, Open Data BCN* |
| Artifacts | [datasheet](../phase-2/data-sheets/ajuntament-trees.md) · [schema](../phase-2/schemas/ajuntament-trees.py) · [Croissant](../phase-2/croissant/ajuntament-trees.jsonld) |

```bash
mkdir -p data
curl -L -o data/arbrat-viari.csv \
  "https://opendata-ajuntament.barcelona.cat/data/dataset/27b3f8a7-e536-4eea-b025-ce094817b2bd/resource/23124fd5-521f-40f8-85b8-efb1e71c2ec8/download"
curl -L -o data/arbrat-zona.csv \
  "https://opendata-ajuntament.barcelona.cat/data/dataset/9b525e1d-13b8-48f1-abf6-f5cd03baa1dd/resource/29cd5c1f-11b1-404b-b3a5-ae29940b8c55/download"
```

---

### 2. FungalRoot v2.0 (species trait lookup)

| | |
|---|---|
| File | `data/fungalroot.csv` |
| License | Open — New Phytologist supplementary (doi:10.1111/nph.18207) |
| Artifacts | [schema](../phase-2/schemas/fungalroot.py) · [Croissant](../phase-2/croissant/fungalroot.jsonld) |

Download from Zenodo mirror or journal supplementary and save to `data/fungalroot.csv`.

---

### 3. GBIF fungal occurrences (SECONDARY)

| | |
|---|---|
| Files | `data/gbif-fungi.json` · `data/gbif-fungi-all.json` |
| License | CC0 / CC-BY per record — cite the download DOI |
| Artifacts | [datasheet](../phase-2/data-sheets/gbif-fungi.md) · [schema](../phase-2/schemas/gbif-fungi.py) · [Croissant](../phase-2/croissant/gbif-fungi.jsonld) |

```bash
# Barcelona municipal subset
curl -L -o data/gbif-fungi.json \
  "https://api.gbif.org/v1/occurrence/search?taxonKey=5&geometry=2.052,41.310,2.230,41.475&eventDate=2015,2024&hasCoordinate=true&limit=300"
# Catalonia-wide
curl -L -o data/gbif-fungi-all.json \
  "https://api.gbif.org/v1/occurrence/search?taxonKey=5&country=ES&eventDate=2015,2024&hasCoordinate=true&limit=300"
```

---

### 4. BCN administrative boundaries

| | |
|---|---|
| Files | `data/bcn-boundary.geojson` · `data/bcn-districts.geojson` |
| License | CC-BY (Open Data BCN) |
| Artifacts | [schema](../phase-2/schemas/spatial-layers.yaml) (`bcn-boundary`, `bcn-districts` entries) |

Download municipal boundary and district polygons GeoJSON exports from Open Data BCN portal.

---

### 5. Copernicus Urban Atlas 2018

| | |
|---|---|
| File | `data/urban-atlas/CLMS_UA_LCU_S2018_V025ha_ES002L2_BARCELONA_03035_V01_R00_20241115.fgb` |
| License | Free for any use (Copernicus terms) |
| Artifacts | [schema](../phase-2/schemas/spatial-layers.yaml) (`urban-atlas-sealed-surface`) · [Croissant](../phase-2/croissant/urban-atlas.jsonld) |

Download from Copernicus Land Monitoring Service (registration required) — select Barcelona FUA, Urban Atlas 2018.

---

### 6. Landsat 8/9 LST (Summer 2023 composite)

| | |
|---|---|
| Files | `data/landsat/ST_B10_raw.tif` · `data/landsat/lst_summer_composite.tif` · `data/landsat/lst_summer2023_celsius.tif` |
| License | USGS — public domain |
| Artifacts | [schema](../phase-2/schemas/spatial-layers.yaml) (`landsat-lst-summer2023`) · [Croissant](../phase-2/croissant/landsat-lst.jsonld) |

Download from USGS Earth Explorer: Landsat Collection 2 Level-2, path 198 / row 031, summer 2023 scenes. Convert ST_B10 to Celsius per the Collection 2 product guide.

---

### 7. Sentinel-2 L2A NDVI (Summer 2023 composite)

| | |
|---|---|
| Files | `data/sentinel2/B04_red.tif` · `data/sentinel2/B08_nir.tif` · `data/sentinel2/ndvi_summer_composite.tif` · `data/sentinel2/ndvi_summer2023.tif` |
| License | Free, no restrictions (Copernicus) |
| Artifacts | [schema](../phase-2/schemas/spatial-layers.yaml) (`sentinel2-ndvi-summer2023`) · [Croissant](../phase-2/croissant/sentinel2-ndvi.jsonld) |

Download tile T31TDF (bands B04 + B08), summer 2023, cloud cover <20% from Copernicus Data Space Ecosystem. Apply SCL mask (exclude classes 8, 9, 10); composite ≥3 clear scenes.

---

### 8. CALIOPE-Urban NO2 (Phase 6 allergenicity layer)

| | |
|---|---|
| File | `data/caliope-no2.csv` |
| License | CC-BY 4.0 (Zenodo 16737066) — confirm non-commercial caveat with BSC before non-academic deployment |
| Artifacts | [datasheet](../phase-2/pollen-gaps/data-sheets/caliope-urban-no2.md) · [gate analysis](../phase-2/pollen-gaps/caliope-gate.md) |

Download `Dataset2A` from Zenodo 16737066 (annual mean NO2, 1,068 BCN census tracts). For the final layer use `Dataset2B` March–April mean (season-matched). Join key: `ID_census` last-5 digits = section `key` (match rate 1.000).

---

## Committed files in this folder

- `profile-summary.json` — machine-readable profiling output, diffable across snapshots.

## Re-running the profiling notebook

```bash
pip install --user pandas numpy matplotlib seaborn nbformat nbconvert ipykernel
python build_notebook.py
```

Or open `notebooks/01-data-profiling.ipynb` in Jupyter and run all cells.
