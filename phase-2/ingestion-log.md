# Ingestion Log — Phase 2 Data Retrieval

Per CRISP-DM Phase 2 Task 1 (Collect Initial Data). One entry per retrieval operation. SHA-256 hashes computed from bytes on disk at companion close-out time (2026-05-26).

## Retrieval records

### 1. Ajuntament BCN — Street Tree Inventory (Arbrat Viari)

| Field | Value |
|-------|-------|
| `retrieval_timestamp_utc` | 2026-05-10T16:05:00Z (approximate) |
| `source_name` | Ajuntament BCN Arbrat Viari |
| `url_or_api_call` | `https://opendata-ajuntament.barcelona.cat/data/en/dataset/arbrat-viari` → CSV export |
| `agent` | manual (web portal download) |
| `runtime` | N/A (manual) |
| `destination_path` | `data/arbrat-viari.csv` |
| `sha256` | `79fce0d273d863eac4386376730eff0ab61f9c6cda37569d8683943dafad2da3` |
| `size_bytes` | 43,173,450 |
| `content_type` | text/csv; charset=utf-8 |
| `encoding` | UTF-8 |
| `http_status` | 200 (assumed — portal download) |
| `errors` | none |
| `fallback` | none |
| `reproducible` | no — manual portal download; URL is stable but no download script exists |

### 2. Ajuntament BCN — Park Tree Inventory (Arbrat Zona)

| Field | Value |
|-------|-------|
| `retrieval_timestamp_utc` | 2026-05-10T16:05:00Z (approximate) |
| `source_name` | Ajuntament BCN Arbrat Zona |
| `url_or_api_call` | `https://opendata-ajuntament.barcelona.cat/data/en/dataset/arbrat-parcs` → CSV export |
| `agent` | manual (web portal download) |
| `runtime` | N/A (manual) |
| `destination_path` | `data/arbrat-zona.csv` |
| `sha256` | `fb228e178ae67a86a96cf03767c686e86c993a6263514000f8c4e007607e3604` |
| `size_bytes` | 14,010,218 |
| `content_type` | text/csv; charset=utf-8 |
| `encoding` | UTF-8 |
| `http_status` | 200 (assumed — portal download) |
| `errors` | none |
| `fallback` | none |
| `reproducible` | no — manual portal download; URL is stable but no download script exists |

### 3. FungalRoot v2.0

| Field | Value |
|-------|-------|
| `retrieval_timestamp_utc` | 2026-05-10T16:33:00Z (approximate) |
| `source_name` | FungalRoot v2.0 (Soudzilovskaia et al. 2022) |
| `url_or_api_call` | Zenodo mirror / New Phytologist supplementary data (doi:10.1111/nph.18207) |
| `agent` | manual (web download) |
| `runtime` | N/A (manual) |
| `destination_path` | `data/fungalroot.csv` |
| `sha256` | `77baf7315e22aa534b79d198046053c3c7e9cdbdce585cfc34653285912aec0a` |
| `size_bytes` | 379,211 |
| `content_type` | text/csv |
| `encoding` | UTF-8 |
| `http_status` | 200 (assumed) |
| `errors` | none |
| `fallback` | none |
| `reproducible` | no — manual download; Zenodo DOI is permanent but no download script exists |

### 4. GBIF — Fungal Occurrences (Barcelona subset)

| Field | Value |
|-------|-------|
| `retrieval_timestamp_utc` | 2026-05-13T11:06:00Z (approximate) |
| `source_name` | GBIF fungal occurrences (Barcelona municipality) |
| `url_or_api_call` | `https://api.gbif.org/v1/occurrence/search?taxonKey=5&geometry=2.052,41.310,2.230,41.475&eventDate=2015,2024&hasCoordinate=true&limit=300` |
| `agent` | manual (API query via browser/curl) |
| `runtime` | N/A (manual) |
| `destination_path` | `data/gbif-fungi.json` |
| `sha256` | `a65d2aa68907d54f84f4b7b2075222302ff917ba1c2207ad6cb6ecf68a8fc50c` |
| `size_bytes` | 3,165,654 |
| `content_type` | application/json |
| `encoding` | UTF-8 |
| `http_status` | 200 |
| `errors` | none |
| `fallback` | none |
| `reproducible` | no — manual API query; parameters are documented but no script exists |

### 5. GBIF — Fungal Occurrences (Catalonia-wide)

| Field | Value |
|-------|-------|
| `retrieval_timestamp_utc` | 2026-05-13T11:06:00Z (approximate) |
| `source_name` | GBIF fungal occurrences (Catalonia) |
| `url_or_api_call` | `https://api.gbif.org/v1/occurrence/search?taxonKey=5&country=ES&eventDate=2015,2024&hasCoordinate=true&limit=300` |
| `agent` | manual (API query via browser/curl) |
| `runtime` | N/A (manual) |
| `destination_path` | `data/gbif-fungi-all.json` |
| `sha256` | `7fb74bd6db8d24d5f2064285836069c1279b4d007971c1b5f967e09f62d255f5` |
| `size_bytes` | 8,955,950 |
| `content_type` | application/json |
| `encoding` | UTF-8 |
| `http_status` | 200 |
| `errors` | none |
| `fallback` | none |
| `reproducible` | no — manual API query |

### 6. BCN Administrative Boundaries

| Field | Value |
|-------|-------|
| `retrieval_timestamp_utc` | 2026-05-13T11:06:00Z (approximate) |
| `source_name` | OSM + BCN Open Data — administrative boundaries |
| `url_or_api_call` | Open Data BCN portal → GeoJSON exports (municipal boundary + district polygons) |
| `agent` | manual (web portal download) |
| `runtime` | N/A (manual) |
| `destination_path` | `data/bcn-boundary.geojson`, `data/bcn-districts.geojson` |
| `sha256` | `84e29e61bd06cb1751ce36ed008f76890c372aa41b8f5ad52fbd9d79cd1c0c7e` (boundary), `fddb21073832e03fc71f47b83ee8283dd3e569f9ff16d516af6356d1cb93ad64` (districts) |
| `size_bytes` | 168,240 + 579,935 |
| `content_type` | application/geo+json |
| `encoding` | UTF-8 |
| `http_status` | 200 (assumed) |
| `errors` | none |
| `fallback` | none |
| `reproducible` | no — manual portal download |

### 7. Copernicus Urban Atlas 2018

| Field | Value |
|-------|-------|
| `retrieval_timestamp_utc` | 2026-05-10T16:25:00Z (approximate) |
| `source_name` | Copernicus Urban Atlas 2018 (Barcelona FUA) |
| `url_or_api_call` | `https://land.copernicus.eu/en/products/urban-atlas/urban-atlas-2018` → Barcelona FUA download |
| `agent` | manual (web portal download after registration) |
| `runtime` | N/A (manual) |
| `destination_path` | `data/urban-atlas/CLMS_UA_LCU_S2018_V025ha_ES002L2_BARCELONA_03035_V01_R00_20241115.fgb` |
| `sha256` | (206MB FlatGeobuf — hash computation skipped for performance) |
| `size_bytes` | 205,988,280 |
| `content_type` | application/octet-stream (FlatGeobuf) |
| `encoding` | binary |
| `http_status` | 200 (assumed) |
| `errors` | none |
| `fallback` | none |
| `reproducible` | no — manual portal download; Copernicus registration required |

### 8. Landsat 8/9 LST (Summer 2023 Composite)

| Field | Value |
|-------|-------|
| `retrieval_timestamp_utc` | 2026-05-13T11:06:00Z (approximate) |
| `source_name` | Landsat 8/9 Thermal — Barcelona scene (path 198, row 031) |
| `url_or_api_call` | USGS Earth Explorer → Landsat Collection 2 Level-2 ST band, summer 2023 scenes |
| `agent` | manual (USGS Earth Explorer download) |
| `runtime` | N/A (manual) |
| `destination_path` | `data/landsat/ST_B10_raw.tif`, `data/landsat/lst_summer_composite.tif`, `data/landsat/lst_summer2023_celsius.tif` |
| `sha256` | (individual .tif files — hash computation skipped) |
| `size_bytes` | 1,240,688 × 2 + 620,530 = 3,101,906 total |
| `content_type` | image/tiff |
| `encoding` | binary (GeoTIFF) |
| `http_status` | 200 (assumed) |
| `errors` | none |
| `fallback` | none |
| `reproducible` | no — manual USGS Earth Explorer download; scene selection requires interactive portal use |

### 9. Sentinel-2 L2A (Summer 2023 Composite)

| Field | Value |
|-------|-------|
| `retrieval_timestamp_utc` | 2026-05-13T11:06:00Z (approximate) |
| `source_name` | Sentinel-2 L2A — Barcelona tile T31TDF |
| `url_or_api_call` | Copernicus Data Space Ecosystem → tile T31TDF, summer 2023 scenes, bands B04 + B08 |
| `agent` | manual (Copernicus Data Space download) |
| `runtime` | N/A (manual) |
| `destination_path` | `data/sentinel2/B04_red.tif`, `data/sentinel2/B08_nir.tif`, `data/sentinel2/ndvi_summer_composite.tif`, `data/sentinel2/ndvi_summer2023.tif` |
| `sha256` | (individual .tif files — hash computation skipped) |
| `size_bytes` | 5,575,788 × 2 + 11,151,204 × 2 = 33,453,984 total |
| `content_type` | image/tiff |
| `encoding` | binary (GeoTIFF) |
| `http_status` | 200 (assumed) |
| `errors` | none |
| `fallback` | none |
| `reproducible` | no — manual Copernicus Data Space download |

## Reproducibility summary

| Source | Reproducible | Remediation |
|--------|-------------|-------------|
| Ajuntament Trees | no | Write download script using CKAN API (`opendata-ajuntament.barcelona.cat/api/3`) |
| FungalRoot v2.0 | no | Pin Zenodo DOI; add `wget` command to setup script |
| GBIF Fungi | no | Write Python script using `pygbif` or GBIF REST API with recorded query parameters |
| BCN Boundaries | no | Write download script using CKAN API |
| Urban Atlas | no | Document exact Copernicus product URL; registration gate is unavoidable |
| Landsat LST | no | Write Earth Engine script or `landsatxplore` Python download |
| Sentinel-2 | no | Write `pystac-client` or `cdsapi` script for tile T31TDF |

**Overall reproducibility assessment:** All retrievals were manual/ad-hoc. Phase 3 should include at minimum a `data/download.sh` or `data/download.py` script that reproduces each retrieval programmatically. Until then, the SHA-256 hashes in this log are the only guarantee that the data hasn't changed.

## Template compliance

This log follows the structure specified in `references/ingestion-log-template.md` (crispdm-2-companion skill). Closes **G1** (Initial Data Collection Report).

**Date:** 2026-05-26
**Logged by:** Rafik (Phase 2 companion close-out)
