# Satellite Data — Manual Download Guide

This file documents the three satellite/remote-sensing datasets used by the
NEXUS-Micro scoring pipeline, why each is needed, and exactly how to download
each one from its portal. None of these can be fetched programmatically without
registration or bulk-API access, so they are not included in `download_data.py`.

If any of these files are absent when the pipeline runs, the pipeline falls back
to synthetic uniform-random sub-scores for the affected dimension (see the stub
fallback section at the bottom of this file).

---

## 1. Urban Atlas 2018 — Land use / impervious surface

### Why

Urban Atlas classifies Barcelona's surface cover at 10 m resolution into 27 land
use classes (continuous urban fabric, discontinuous urban, green urban areas,
forests, sport/leisure, etc.). The pipeline uses it to derive:

- Impervious surface fraction per 400 m cell (negatively correlated with
  mycorrhizal network connectivity)
- Green urban area fraction per cell (positively correlated)
- Identification of sealed-soil barriers that limit hyphal spread

### What files to save

```
data/
  urban-atlas/
    BCN_UA2018_v013.gpkg       # main vector GeoPackage
    BCN_UA2018_v013_UA_maps/   # optional rasterised tiles (if downloaded)
```

### How to download

1. Go to the Copernicus Land Monitoring Service Urban Atlas portal:
   `https://land.copernicus.eu/local/urban-atlas/urban-atlas-2018`
2. Click **Download** (requires a free Copernicus account — register at
   `https://land.copernicus.eu/en/user-corner/registration`).
3. In the download form, select:
   - **Country**: Spain
   - **City/FUA**: Barcelona (FUA code: ES002L1)
   - **Year**: 2018
   - **Format**: GeoPackage (.gpkg) — preferred; avoids shapefile encoding issues
4. Accept the licence (CLMS licence — free for non-commercial and research use).
5. Download the zip, extract it, and copy the `.gpkg` file to
   `data/urban-atlas/BCN_UA2018_v013.gpkg`.

Expected file size: approximately 80–200 MB (GeoPackage with geometry).

### License

Copernicus Land Monitoring Service (CLMS) licence. Free for research use.
Cite as: EEA (2021). Urban Atlas 2018. European Environment Agency.

---

## 2. Sentinel-2 L2A — Canopy NDVI / green cover

### Why

Sentinel-2 Level-2A (surface reflectance, 10 m) provides current vegetation
density via NDVI (Normalised Difference Vegetation Index). The pipeline uses it
to compute:

- Per-cell mean summer NDVI (July–August, cloud-free composite) as a proxy for
  tree canopy health and photosynthetic activity
- NDVI standard deviation across cells as a diversity proxy

Preferred acquisition window: July–August 2023 (peak growing season, low cloud
cover in Barcelona). Any year 2020–2024 is acceptable; document which year you
used in your analysis notebook.

### What files to save

```
data/
  sentinel2/
    T31TDF_20230801_B04_10m.jp2   # Red band (for NDVI)
    T31TDF_20230801_B08_10m.jp2   # NIR band (for NDVI)
    T31TDF_20230801_SCL_20m.jp2   # Scene Classification Layer (cloud mask)
```

Tile code for Barcelona: **T31TDF** (UTM zone 31N, covering Barcelona).

### How to download

**Option A — Copernicus Data Space Ecosystem (recommended, free)**

1. Register at `https://dataspace.copernicus.eu` (free account).
2. Go to the Browser: `https://browser.dataspace.copernicus.eu`
3. In the search panel:
   - **Collection**: Sentinel-2 L2A
   - **Time range**: 2023-07-01 to 2023-08-31
   - **Area**: draw a box over Barcelona or enter coordinates
     - Min lon: 2.05, Max lon: 2.23, Min lat: 41.31, Max lat: 41.48
   - **Cloud cover**: max 10%
4. Select a scene with tile code T31TDF and low cloud cover. Click the scene
   thumbnail to verify the Barcelona area is cloud-free.
5. Click **Download** (you may need to add to cart and then download as a zip).
6. From the downloaded SAFE folder, copy only the three bands listed above into
   `data/sentinel2/`. Rename files to match the pattern shown above if needed.

**Option B — Copernicus CLI (sentinelsat)**

```bash
pip install sentinelsat
sentinelsat --user YOUR_EMAIL --password YOUR_PASSWORD \
  --geometry "POLYGON((2.05 41.31, 2.23 41.31, 2.23 41.48, 2.05 41.48, 2.05 41.31))" \
  --start 20230701 --end 20230831 \
  --producttype S2MSI2A \
  --sentinel 2 \
  --cloud 10 \
  --download
```

Then copy B04, B08, and SCL granule files to `data/sentinel2/`.

Expected file sizes: B04 and B08 each ~100–150 MB (10 m, .jp2); SCL ~30 MB (20 m).

### License

Copernicus Sentinel data — free and open, CC-BY licence.
Cite as: Contains modified Copernicus Sentinel data [2023].

---

## 3. Landsat 8/9 OLI — Longer time series / thermal

### Why

Landsat 8/9 Collection 2 Level-2 (30 m) extends the historical record back to
2013 and adds Band 10 (Thermal Infrared / TIRS) for urban heat island mapping.
The pipeline uses it for:

- Surface temperature per cell (Band 10 ST) — high urban heat negatively
  correlates with ectomycorrhizal fruiting body density
- Multi-year NDVI trend (2015–2024) to detect greening or decline trends
  per grid cell

### What files to save

```
data/
  landsat/
    LC09_L2SP_197031_20230801_ST_B10.TIF   # Surface temperature (Landsat 9)
    LC09_L2SP_197031_20230801_SR_B4.TIF    # Red band (for NDVI)
    LC09_L2SP_197031_20230801_SR_B5.TIF    # NIR band (for LANDSAT NDVI)
    LC09_L2SP_197031_20230801_QA_PIXEL.TIF # Cloud/QA mask
```

Path/Row for Barcelona: **197/031**.

### How to download

1. Go to USGS EarthExplorer: `https://earthexplorer.usgs.gov`
   (free account required — register at `https://ers.cr.usgs.gov/register`)
2. In the **Search Criteria** tab:
   - Under **Coordinates**, enter:
     - Decimal: lat 41.38, lon 2.17 (city centre)
   - **Date range**: 2023-07-01 to 2023-08-31
3. In the **Data Sets** tab, expand:
   - Landsat > Landsat Collection 2 Level-2 > Landsat 8-9 OLI/TIRS C2 L2
4. Click **Results**. Filter for path 197, row 031 and cloud cover < 10%.
5. Click the download icon next to a suitable scene. Select **Level-2 Product**
   (includes SR and ST bands).
6. Extract the downloaded tar file. Copy the four band files listed above to
   `data/landsat/`. Rename to match the pattern if the scene date differs.

**Alternative — USGS STAC/bulk API (advanced)**

```bash
pip install pystac-client planetary-computer
# Query via Microsoft Planetary Computer (mirrors USGS Landsat C2):
# https://planetarycomputer.microsoft.com/api/stac/v1
# Collection: landsat-c2-l2, bbox over Barcelona, cloud_cover < 10
```

Expected file sizes: each TIF band ~50–80 MB; QA band ~20 MB.

### License

Landsat data are in the public domain (US Government work, no copyright).
Cite as: USGS Landsat Collection 2, courtesy of the U.S. Geological Survey.

---

## Stub Fallback — Absent Satellite Data

The scoring pipeline in `notebooks/` detects whether each satellite directory
contains the expected files. When files are absent, the pipeline substitutes
synthetic sub-scores drawn from a uniform distribution U(0.3, 0.7) for that
dimension rather than halting execution.

This allows the notebook to run end-to-end during development (e.g., on a
laptop without a large dataset download) while clearly flagging cells that
used synthetic data.

### Dimensions affected by the fallback

| Absent directory     | Affected sub-score               | Fallback value |
|----------------------|----------------------------------|----------------|
| `data/urban-atlas/`  | Impervious surface fraction      | U(0.3, 0.7)    |
| `data/sentinel2/`    | Summer canopy NDVI               | U(0.3, 0.7)    |
| `data/landsat/`      | Surface temperature (ST_B10)     | U(0.3, 0.7)    |
| `data/landsat/`      | Multi-year NDVI trend slope      | U(-0.01, 0.01) |

Cells that use synthetic values are tagged with `synthetic=True` in the output
GeoDataFrame and coloured grey on the output choropleth map so that readers
can immediately distinguish real from imputed scores.

**IMPORTANT**: Synthetic sub-scores must not be reported as real findings.
Any analysis or output that includes synthetic values must be labelled
"preliminary / data-incomplete" in figure captions and the Methods section.
Download the actual satellite data before producing results for the report.

---

## Directory Structure After All Downloads

```
data/
  arbrat-viari.csv             street trees (download_data.py)
  arbrat-zona.csv              park trees (download_data.py)
  gbif-fungi.json              GBIF records, first 300 (download_data.py)
  gbif-fungi-full.csv          GBIF full export (manual portal download)
  bcn-boundary.geojson         municipal boundary (download_data.py)
  bcn-districts.geojson        10 district polygons (download_data.py)
  urban-atlas/
    BCN_UA2018_v013.gpkg       Urban Atlas 2018 GeoPackage (manual)
  sentinel2/
    T31TDF_20230801_B04_10m.jp2
    T31TDF_20230801_B08_10m.jp2
    T31TDF_20230801_SCL_20m.jp2
  landsat/
    LC09_L2SP_197031_20230801_ST_B10.TIF
    LC09_L2SP_197031_20230801_SR_B4.TIF
    LC09_L2SP_197031_20230801_SR_B5.TIF
    LC09_L2SP_197031_20230801_QA_PIXEL.TIF
  README-satellite.md          this file
  README.md                    data/ overview
  profile-summary.json         machine-readable profiling snapshot
  download_data.py             automated download script
```
