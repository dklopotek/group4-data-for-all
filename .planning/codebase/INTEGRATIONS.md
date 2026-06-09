# External Integrations
_Mapped: 2026-06-04_

## Data Sources (external APIs/portals)

| Source | What it provides | How accessed | Auth needed? | Fallback | Notes |
|--------|------------------|--------------|--------------|----------|-------|
| **Open Data Barcelona (Ajuntament)** | Tree inventory CSVs: street trees (`arbrat-viari.csv`, 145k rows) and park trees (`arbrat-zona.csv`, 43k rows) | HTTP direct download via 2 fixed resource URLs in `scripts/download_all.py` and `scripts/download_data.py` | No (public data, CC-BY 4.0) | None — required for pipeline | Snapshot from ~2026-01 (Q1). Contains species names, coordinates (ETRS89/UTM31N), planting dates, district/neighborhood codes. The authoritative Barcelona public-realm tree census. |
| **GBIF (Global Biodiversity Information Facility)** | Fungal occurrence records (Basidiomycota-biased for EM hosts), Barcelona bbox, 2015–2024 | REST API: `https://api.gbif.org/v1/occurrence/search` with bbox + fungal kingdom filter. `scripts/download_all.py` handles pagination (300 recs/page). API returns ~1024 records for Barcelona. | No (public occurrence search, no auth required) | Empty DataFrame (zero GBIF records) | Script polls with `kingdomKey=5` (Fungi), `decimalLatitude/decimalLongitude` constraints, `hasCoordinate=true`. For complete dataset (>300 records), user must download manually via GBIF portal and save to `data/gbif-fungi-full.csv`. Returned records are WGS84 (lon/lat); reprojected to EPSG:25831 on read. |
| **FungalRoot v2.0 (Zenodo)** | Species → mycorrhizal type (AM/EM/NM) lookup table. 11k+ species mapping. | Zenodo API (`https://zenodo.org/api/records/5596174`) fetches file URL, then HTTP download. `scripts/download_all.py` automates this. | No (open-access dataset, DOI 10.5281/zenodo.5596174) | Hardcoded top-20 species stub (lines 226–247 in `src/clean_data.py`) | CSV columns: `species_name`, `myco_type` (with variants like "EcM", "ECM, AM undetermined" → normalized to {AM, EM, NM}). Applied AFTER the CSV join for safety (BUG-2 fix: hardcoded overrides take precedence, lines 464–466). Sourced from Smith & Read (2008), Brundrett & Tedersoo (2018). |
| **Planetary Computer STAC** | Sentinel-2 L2A (Red [B04], NIR [B08] bands) and Landsat C2 L2 (thermal band ST_B10) for NDVI and LST computation | `pystac-client` (Python SDK) queries STAC catalog at `https://planetarycomputer.microsoft.com/api/stac/v1`, filtered by bbox + datetime + cloud cover. `planetary-computer.sign_inplace()` handles request signing (no token). `scripts/download_all.py` automates scene discovery and band download. | No (public imagery, no authentication required) | Synthetic Beta/Normal values (printed as `[SYNTHETIC]` flag) | Sentinel-2: searches T31TDF tile (Barcelona), summer 2023 (Jun–Sep), cloud <5% (relaxed to <15% if needed), returns ~3 candidates, uses lowest-cloud scene. Landsat: C2 L2 only (excludes Landsat 7), platform filter `["landsat-8", "landsat-9"]`, cloud <15%, returns best 10, uses first. Rasterio handles band reprojection, clipping, and masking on-the-fly. |
| **OpenStreetMap (Nominatim / Overpass API)** | Barcelona municipal boundary (multipolygon) and 10 district boundaries (polygons) | Nominatim polygon endpoint (`https://nominatim.openstreetmap.org/search?polygon_geojson=1`) for city boundary. Overpass API fallback (`https://overpass-api.de/api/interpreter`, relation 347950). `scripts/download_data.py` tries Nominatim first, falls back to Overpass if HTTP fails. User-Agent required (identifies as "NEXUS-Micro/1.0"). | No (ODbL-licensed OpenStreetMap data, attribution required) | Hardcoded bounding-box fallback (`BCN_XMIN/XMAX/YMIN/YMAX` in `src/clean_data.py`) | GeoJSON output saved to `data/bcn-boundary.geojson` and `data/bcn-districts.geojson`. Grid clipping algorithm in `build_grid()` uses boundary to snap cells to 400 m multiples. If file missing, falls back to approximate UTM31N bounding box (±0.5% error). Both Nominatim and Overpass have rate limits; `scripts/download_data.py` uses `time.sleep(1.1)` between district queries (1 req/sec max). |
| **Copernicus Land Monitoring Service (Urban Atlas 2018)** | Sealed surface / imperviousness raster (0–1 or 0–100 scale) for Barcelona municipality | Manual download from `https://land.copernicus.eu/local/urban-atlas/urban-atlas-2018` after free registration. User downloads GeoPackage or TIF and saves to `data/urban-atlas/sealed_surface.tif` or `imperviousness_2018.tif`. | Yes — requires **free account creation** (~2 min signup) | Synthetic Beta(2,5) distribution (flagged `[SYNTHETIC]`) | Only dataset requiring human intervention. `scripts/download_all.py` prints a 10-line instruction block at the end. Rasterio reads with optional masking; if absent, `src/clean_data.py` synthesizes values to avoid pipeline failure (lines 978–983). |
| **Mediterranean VPA lookup** | Species → allergenicity class (1–5) per Cariñanos & Marinangeli (2021) | CSV committed to repo at `data/raw/vpa-mediterranean-species.csv` (small, ~100 KB) | No (published in open-access journal) | Minimal stub (Platanus only, lines 1282–1287 in `src/clean_data.py`) | Used in Phase 3 for allergenicity weighting. Lookup is `load_vpa_lookup()` (lines 1256–1293). Unknown species default to VPA 2.5 (midpoint) to avoid zero-bias. |

## Remote Sensing / STAC

### Sentinel-2 L2A (NDVI computation)
- **Collection**: `sentinel-2-l2a` (Planetary Computer)
- **Bands used**: B04 (red, 10 m), B08 (NIR, 10 m)
- **Temporal coverage**: Summer 2023 (June 1 — September 30, 2023)
- **Tile filter**: T31TDF (Barcelona MGRS tile, avoids adjacent tile pollution)
- **Cloud filter**: <5% (relaxed to <15% if no scenes available)
- **Processing**: NDVI = (NIR - Red) / (NIR + Red), computed by `rasterio` with scale factor 1/10000 applied to L2A reflectance values
- **Output**: `data/sentinel2/ndvi_summer2023.tif` (float32, -1 to 1 scale)
- **Zonal stats**: `compute_s3_ndvi()` applies zonal mean per 400 m grid cell, normalizes to [0, 1], inverts (1 - norm) so lower canopy = higher barrier (sub-score S3)

### Landsat 8/9 C2 L2 (Land Surface Temperature)
- **Collection**: `landsat-c2-l2` (Planetary Computer)
- **Band used**: ST_B10 (thermal infrared, 11 µm, 30 m native resolution)
- **Temporal coverage**: Summer 2023 (June 1 — September 30, 2023)
- **Platform filter**: Landsat 8 or 9 only (excludes Landsat 7 LE07, which lacks ST_B10)
- **Cloud filter**: <15%
- **Processing**: DN → K: `T(K) = 0.00341802 * DN + 149.0` → C: `T(C) = T(K) - 273.15`
- **Output**: `data/landsat/lst_summer2023_celsius.tif` (float32, Celsius)
- **Zonal stats**: `compute_s2_lst()` computes per-cell mean, derives anomaly from city-wide median, normalizes to [0, 1] via min-max (sub-score S2)

### Notes on STAC usage
- Both Sentinel-2 and Landsat are queried and downloaded on-demand by `scripts/download_all.py`
- `pystac-client.Client.open()` with `planetary_computer.sign_inplace()` modifier handles signing; no authentication tokens needed
- Rasterio reprojection happens inline during clipping (lines 222–226 in `scripts/download_all.py`)
- If rasters are absent, `src/clean_data.py` gracefully falls back to synthetic distributions

## Auth / Credentials

- **API keys**: None required
- **OAuth flows**: None
- **Credentials in `.env` or `settings`: None — all data sources are public-access
- **Copernicus registration**: Single exception — Urban Atlas download requires manual account creation; no programmatic auth token needed (one-time download step)
- **User-Agent headers**: Set in HTTP requests to identify as "NEXUS-Micro/1.0 (academic research)" or similar, per API politeness norms (Nominatim, Overpass)

## Network Calls

| Caller | Endpoint | Method | Frequency | Rate-limit handling | Retry strategy |
|--------|----------|--------|-----------|-------------------|-----------------|
| `scripts/download_data.py` | `https://opendata-ajuntament.barcelona.cat/...` | HTTP GET (stream) | Once per run | None | `raise_for_status()` → hard fail |
| `scripts/download_data.py` | `https://api.gbif.org/v1/occurrence/search` | HTTP GET | Once per run (single page, 300 recs max) | Built-in: returns 300 items, marks `endOfRecords` flag | Timeout 60 s; `raise_for_status()` |
| `scripts/download_all.py` | GBIF API (paginated) | HTTP GET (loop, 300 recs/page) | Once per run (full download, all pages) | `time.sleep(0.5)` between pages | 30 s timeout; `raise_for_status()` |
| `scripts/download_all.py` | `https://zenodo.org/api/records/5596174` | HTTP GET | Once per run | None | Timeout 30 s; prints fallback manual URL on failure |
| `scripts/download_all.py` | Planetary Computer STAC | `pystac-client` search + `rasterio.open(href)` | Once per run (Sentinel-2 + Landsat) | Built-in: `max_items` limit (3–5 candidates) | Timeout 120 s; prints error + manual USGS fallback |
| `scripts/download_data.py` | `https://nominatim.openstreetmap.org/search` | HTTP GET (polygon_geojson=1) | Once per run (boundary + 10 districts) | Nominatim rate limit: 1 req/sec; `time.sleep(1.1)` between requests | 30 s timeout; falls back to Overpass on HTTP error |
| `scripts/download_data.py` | `https://overpass-api.de/api/interpreter` | HTTP POST (OSM query) | Once per run (fallback for boundary) | Free Overpass has soft limits; `time.sleep(1)` before fallback | 90 s timeout; prints error + manual download link |

## No Webhooks / Databases

- **Webhooks**: None. The pipeline is **batch-driven** — runs on-demand from the command line.
- **Databases**: None. All data is **file-based**:
  - Inputs: CSV (tree inventory, FungalRoot, VPA), GeoJSON (boundaries), GeoTIFF (rasters), JSON (GBIF, intervention costs)
  - Intermediates: Parquet splits (`data/splits/train.parquet`, etc.), GeoJSON networks (`data/network_*.geojson`)
  - Outputs: Parquet predictions, CSV metrics, GeoJSON results, Joblib model artifact
- **Caching**: None. Each run reads raw sources and recomputes from scratch (reproducible by design).
- **No background tasks, queues, or async patterns**: All scripts are synchronous, single-threaded or simple multiprocessing (if any). Designed for teaching environments.

### Pipeline execution model
1. User runs `python scripts/download_all.py` (or `download_data.py`) to fetch remote datasets
2. User runs `python src/clean_data.py` to execute the CRISP-DM Phase 3 pipeline (data preparation → scoring)
3. `src/split_data.py` reads scored output and creates train/eval/test splits (spatial split, Phase 4 Core A)
4. `src/train_model.py` trains linear regression + 3 baselines on splits and saves artifacts (Phase 4 Core B)
5. Outputs are written to `outputs/phase-4/` and `data/processed/` as CSVs, parquets, geojsons
6. Jupyter notebooks read from these outputs for visualization and narrative

**No deployment infrastructure**: No production server, no API endpoint, no monitoring. This is an **academic data pipeline** for a seminar project.
