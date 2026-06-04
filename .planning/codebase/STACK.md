# Tech Stack
_Mapped: 2026-06-04_

## Languages & Runtime

- **Python 3.12+** (specified in `requirements.txt` comment)
- **Jupyter Notebooks** for exploratory analysis and data profiling
- **Python scripts** (`src/*.py`, `scripts/*.py`) for deterministic pipeline stages
- Single virtual environment; no Docker containerization

## Core Libraries

| Library | Version | Purpose | Category |
|---------|---------|---------|----------|
| pandas | 3.0.3 | DataFrames, CSV I/O, aggregation | Data wrangling |
| numpy | 2.4.6 | Numerical arrays, statistical ops | Data wrangling |
| scipy | 1.17.1 | `cKDTree` for spatial indexing, statistical functions | Data wrangling |
| scikit-learn | >=1.5,<2.0 | `LinearRegression`, `SimpleImputer`, ML metrics | ML (Phase 4) |
| geopandas | 1.1.3 | Spatial vector I/O, GeoDataFrames, spatial joins | Geospatial vector |
| shapely | 2.1.2 | Geometry operations (Point, box, polygon intersections) | Geospatial vector |
| fiona | 1.10.1 | Vector file I/O driver support (GeoJSON, Shapefile, GeoPackage) | Geospatial vector |
| pyogrio | 0.12.1 | GDAL/OGR bindings for vector file reading | Geospatial vector |
| rasterio | 1.5.0 | GeoTIFF raster I/O, zonal statistics via mask | Geospatial raster |
| rioxarray | 0.22.0 | xarray + rasterio integration (optional, conditional import) | Geospatial raster |
| matplotlib | 3.10.9 | Static plotting (histograms, scatter, bar charts) | Visualization |
| seaborn | 0.13.2 | Statistical visualization themes/palettes | Visualization |
| jupyter | 1.1.1 | Jupyter environment launcher | Notebook |
| ipykernel | 7.2.0 | IPython kernel for notebooks | Notebook |
| pyarrow | 24.0.0 | Parquet file I/O (`.parquet` format for train/test splits) | Data formats |
| requests | 2.34.2 | HTTP downloads: Zenodo, GBIF API, Nominatim, Overpass | Remote-sensing access |
| tqdm | 4.67.3 | Progress bars (download scripts, long-running notebooks) | CLI/UX |
| planetary-computer | 1.0.0 | STAC signing for Planetary Computer (Sentinel-2, Landsat) | Remote-sensing access |
| pystac-client | 0.9.0 | STAC catalog search (Sentinel-2, Landsat, low-cloud filtering) | Remote-sensing access |
| joblib | (indirect via sklearn) | Model serialization (`.joblib` artifacts in Phase 4) | ML |

## Pinned vs Floating Versions

- **Exact pins** (13 libraries): `pandas==3.0.3`, `numpy==2.4.6`, `scipy==1.17.1`, `geopandas==1.1.3`, `shapely==2.1.2`, `fiona==1.10.1`, `pyogrio==0.12.1`, `rasterio==1.5.0`, `rioxarray==0.22.0`, `matplotlib==3.10.9`, `seaborn==0.13.2`, `jupyter==1.1.1`, `ipykernel==7.2.0`, `pyarrow==24.0.0`, `requests==2.34.2`, `tqdm==4.67.3`, `planetary-computer==1.0.0`, `pystac-client==0.9.0`
- **Floating range** (1 library): `scikit-learn>=1.5,<2.0` (allows patch updates within major version; the regression trainer only tunes `fit_intercept` and does not sweep regularization)

**Reproducibility note:** Exact pins preserve deterministic raster math (zonal statistics, NDVI computation) and spatial indexing. The floating scikit-learn range avoids blocking on bugfix releases but keeps the API stable across v1.5–v1.9.

## Configuration & Environment

- **No `.env` or secrets file**: All data sources are public-access (GBIF, Zenodo, Planetary Computer, Nominatim, Overpass, Open Data Barcelona). No API keys required.
- **No `pyproject.toml` or `setup.cfg`**: Single flat `requirements.txt` (legacy style, suitable for seminar coursework).
- **No lockfile**: Floating scikit-learn + exact pins on everything else. Manual reproducibility by running `pip install -r requirements.txt`.
- **`.gitignore` entries** (relevant to data/env):
  - `*.env` — excluded (no secrets anyway)
  - `data/raw/*` except `data/raw/vpa-mediterranean-species.csv` (one small lookup table committed)
  - `*.csv`, `*.xlsx`, `*.zip`, `*.fgb` — large input/output files ignored
  - `__pycache__/`, `*.pyc` — Python cache
  - `.ipynb_checkpoints/` — Jupyter state
  - Course documents (`MaAI01 25-26...`) — kept local only

## Data Formats In Use

| Format | Location(s) | Purpose | Count | Size(est.) |
|--------|------------|---------|-------|------------|
| CSV | `data/arbrat-viari.csv`, `data/arbrat-zona.csv` | Tree inventory (street + park) | 2 files | ~57 MB combined |
| CSV | `data/fungalroot.csv` | Species → mycorrhizal type lookup | 1 file | ~379 KB |
| CSV | `data/raw/vpa-mediterranean-species.csv` | Species → allergenicity (VPA class 1–5) | 1 file | Committed |
| CSV | `outputs/phase-4/metrics.csv`, `per_district.csv`, etc. | Model outputs (phase 4) | Multiple | Small |
| JSON | `data/gbif-fungi.json`, `gbif-fungi-all.json` | GBIF occurrence records (paginated API response) | 2 files | ~3–9 MB |
| JSON | `data/intervention_costs.json` | Lookup for intervention type → cost | 1 file | ~34 KB |
| JSON | `data/profile-summary.json` | Machine-readable data profiling summary | 1 file | ~3 KB |
| GeoJSON | `data/bcn-boundary.geojson`, `bcn-districts.geojson` | Municipal + district boundaries (polygons, OpenStreetMap/Nominatim) | 2 files | ~748 KB combined |
| GeoJSON | `data/grid_trees.geojson`, `network_*.geojson` | Spatial outputs (grid cells, connectivity networks) | Multiple | ~10 MB combined |
| GeoTIFF | `data/landsat/lst_summer*.tif` | Landsat-8/9 thermal band, surface temperature (Celsius) | 1–2 files | ~MB-level |
| GeoTIFF | `data/sentinel2/ndvi_summer*.tif`, `B04_red.tif`, `B08_nir.tif` | Sentinel-2 NDVI and bands (red, NIR) for NDVI computation | 3 files | ~MB-level each |
| GeoTIFF | `data/urban-atlas/sealed_surface.tif` | Urban Atlas 2018 imperviousness/sealed surface (0–1 scale) | 1 file | Manual download, Copernicus Land portal |
| Parquet | `data/splits/train.parquet`, `eval.parquet`, `test.parquet` | Train/eval/test splits (Phase 4), written by `src/split_data.py` | 3 files | Small–medium |
| Parquet | `outputs/phase-4/predictions.parquet` | Model predictions (cell_id, split, y_true, y_pred*) | 1 file | Small |
| Joblib | `outputs/phase-4/model_artifact.joblib` | Fitted sklearn Pipeline (imputer + LinearRegression) | 1 file | <100 KB |

## Notable Gaps

1. **No lockfile** (`poetry.lock`, `Pipenv.lock`, etc.): Reproducibility relies on the exact versions in `requirements.txt` and manual testing. For production deployment, consider adding `pip freeze > requirements-lock.txt` or adopting `pyproject.toml` + `uv` or `pdm`.

2. **No configuration management** (e.g., `hydra`, `pydantic.BaseSettings`): Constants are hardcoded in Python module headers (`GRID_SIZE=400`, `CRS_PROJ="EPSG:25831"`, threshold constants). Suitable for a seminar project; for multi-environment deployment, externalize to YAML or `.env`.

3. **No database** (PostgreSQL, DuckDB, etc.): The entire pipeline is **local file-based**. All intermediate outputs are written to `data/processed/` or `outputs/`. No persistence layer.

4. **Rasterio optional at runtime**: Conditional import in `src/clean_data.py` — if GeoTIFF rasters are absent, the pipeline falls back to synthetic Beta/Normal-distributed values and prints a `[SYNTHETIC]` flag. Designed for graceful degradation in teaching environments.

5. **No typing stubs or mypy**: Type hints are present (PEP 484 style) in function signatures but not enforced via static checking; docstrings use NumPy-style format.

6. **Urban Atlas requires manual download**: The only dataset that needs human intervention — Copernicus Land Monitoring Service requires free registration. `scripts/download_all.py` prints clear instructions but cannot auto-download.
