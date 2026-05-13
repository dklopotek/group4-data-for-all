"""
download_all.py — Full data download, no stubs.
================================================
Downloads every dataset the pipeline needs:
  1. Tree inventory CSVs (Open Data BCN)
  2. GBIF fungal records — ALL records via pagination
  3. FungalRoot v2.0 CSV (Zenodo)
  4. Sentinel-2 L2A NDVI bands — via Planetary Computer (no login)
  5. Landsat 8/9 Surface Temperature — via Planetary Computer (no login)
  6. BCN municipal boundary + district polygons

Urban Atlas requires free registration at land.copernicus.eu — see
the note printed at the end of this script.

Run from repo root:
    python data/download_all.py
"""

import json
import time
from pathlib import Path

import numpy as np
import requests

DATA_DIR = Path(__file__).parent

# ── Barcelona bounding box (WGS84: lon_min, lat_min, lon_max, lat_max) ────
BCN_BBOX = [2.052, 41.310, 2.230, 41.475]


def _skip(path: Path) -> bool:
    if path.exists() and path.stat().st_size > 0:
        print(f"  [skip] {path.name} already exists ({path.stat().st_size // 1024} KB)")
        return True
    return False


# ══════════════════════════════════════════════════════════════════════════
# 1. TREE INVENTORY CSVs
# ══════════════════════════════════════════════════════════════════════════
def download_trees():
    print("\n── 1. Tree inventory CSVs ──────────────────────────────────────")
    urls = {
        "arbrat-viari.csv": (
            "https://opendata-ajuntament.barcelona.cat/data/dataset/"
            "27b3f8a7-e536-4eea-b025-ce094817b2bd/resource/"
            "23124fd5-521f-40f8-85b8-efb1e71c2ec8/download"
        ),
        "arbrat-zona.csv": (
            "https://opendata-ajuntament.barcelona.cat/data/dataset/"
            "9b525e1d-13b8-48f1-abf6-f5cd03baa1dd/resource/"
            "29cd5c1f-11b1-404b-b3a5-ae29940b8c55/download"
        ),
    }
    for fname, url in urls.items():
        dest = DATA_DIR / fname
        if _skip(dest):
            continue
        print(f"  Downloading {fname} …")
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
        print(f"  ✓ {fname} ({dest.stat().st_size // (1 << 20)} MB)")


# ══════════════════════════════════════════════════════════════════════════
# 2. GBIF — ALL RECORDS via pagination
# ══════════════════════════════════════════════════════════════════════════
def download_gbif():
    print("\n── 2. GBIF fungal records (all, paginated) ─────────────────────")
    dest = DATA_DIR / "gbif-fungi-all.json"
    if _skip(dest):
        return

    lon_min, lat_min, lon_max, lat_max = BCN_BBOX
    base = "https://api.gbif.org/v1/occurrence/search"
    params = {
        "kingdomKey": 5,          # Fungi
        "decimalLongitude": f"{lon_min},{lon_max}",
        "decimalLatitude": f"{lat_min},{lat_max}",
        "year": "2015,2024",
        "hasCoordinate": "true",
        "limit": 300,
        "offset": 0,
    }

    all_records = []
    total = None
    while True:
        r = requests.get(base, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        if total is None:
            total = data.get("count", "?")
            print(f"  Total records on GBIF: {total}")
        batch = data.get("results", [])
        all_records.extend(batch)
        print(f"  Fetched {len(all_records)} / {total} …")
        if data.get("endOfRecords", True) or not batch:
            break
        params["offset"] += 300
        time.sleep(0.5)   # be polite to the API

    dest.write_text(json.dumps(all_records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  ✓ gbif-fungi-all.json ({len(all_records)} records)")


# ══════════════════════════════════════════════════════════════════════════
# 3. FungalRoot v2.0 (Zenodo)
# ══════════════════════════════════════════════════════════════════════════
def download_fungalroot():
    print("\n── 3. FungalRoot v2.0 (Zenodo) ─────────────────────────────────")
    dest = DATA_DIR / "fungalroot.csv"
    if _skip(dest):
        return

    # Zenodo record for FungalRoot v2.0 (Soudzilovskaia et al. 2022)
    # DOI: 10.5281/zenodo.5596174  →  record ID 5596174
    # The actual file URL is fetched via the Zenodo API to stay stable
    zenodo_api = "https://zenodo.org/api/records/5596174"
    print("  Fetching Zenodo record metadata …")
    meta = requests.get(zenodo_api, timeout=30)

    if meta.status_code == 200:
        files = meta.json().get("files", [])
        csv_files = [f for f in files if f.get("key", "").endswith(".csv")]
        if csv_files:
            url = csv_files[0]["links"]["self"]
            print(f"  Downloading {csv_files[0]['key']} ({csv_files[0]['size'] // 1024} KB) …")
            r = requests.get(url, stream=True, timeout=120)
            r.raise_for_status()
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    f.write(chunk)
            print(f"  ✓ fungalroot.csv")
        else:
            print("  WARNING: No CSV found in Zenodo record 5596174.")
            print("  Manual download: https://zenodo.org/records/5596174")
    else:
        print(f"  WARNING: Zenodo API returned {meta.status_code}.")
        print("  Try manually: https://zenodo.org/records/5596174 → download the CSV → save as data/fungalroot.csv")


# ══════════════════════════════════════════════════════════════════════════
# 4. Sentinel-2 L2A — NDVI bands via Planetary Computer
# ══════════════════════════════════════════════════════════════════════════
def download_sentinel2():
    print("\n── 4. Sentinel-2 L2A (NDVI bands, summer 2023) ─────────────────")
    out_dir = DATA_DIR / "sentinel2"
    out_dir.mkdir(exist_ok=True)

    b04_dest = out_dir / "B04_red.tif"
    b08_dest = out_dir / "B08_nir.tif"
    ndvi_dest = out_dir / "ndvi_summer2023.tif"

    if _skip(ndvi_dest):
        return

    try:
        import planetary_computer
        import pystac_client
        import rasterio
        from rasterio.crs import CRS
        from rasterio.mask import mask as rio_mask
        from rasterio.warp import transform_geom
        from shapely.geometry import box, mapping
    except ImportError as e:
        print(f"  Missing package: {e}")
        print("  Run: pip install planetary-computer pystac-client rasterio")
        return

    print("  Searching Planetary Computer for low-cloud Sentinel-2 scenes …")
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    lon_min, lat_min, lon_max, lat_max = BCN_BBOX
    bbox_geom_wgs84 = box(lon_min, lat_min, lon_max, lat_max)

    # Barcelona is on tile T31TDF — filter to avoid adjacent tiles
    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=BCN_BBOX,
        datetime="2023-06-01/2023-09-30",
        query={"eo:cloud_cover": {"lt": 5}, "s2:mgrs_tile": {"eq": "31TDF"}},
        sortby="+eo:cloud_cover",
        max_items=3,
    )
    items = list(search.items())
    if not items:
        print("  No T31TDF scenes <5% cloud. Relaxing to <15% …")
        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=BCN_BBOX,
            datetime="2023-06-01/2023-09-30",
            query={"eo:cloud_cover": {"lt": 15}, "s2:mgrs_tile": {"eq": "31TDF"}},
            sortby="+eo:cloud_cover",
            max_items=5,
        )
        items = list(search.items())

    if not items:
        print("  ERROR: No suitable Sentinel-2 scenes found for tile T31TDF.")
        return

    item = items[0]
    cloud = item.properties.get("eo:cloud_cover", "?")
    date  = item.properties.get("datetime", "?")[:10]
    print(f"  Best scene: {item.id}  date={date}  cloud={cloud}%")

    for band, dest in [("B04", b04_dest), ("B08", b08_dest)]:
        if dest.exists():
            continue
        href = item.assets[band].href
        print(f"  Downloading {band} …")
        with rasterio.open(href) as src:
            # Reproject clip geometry from WGS84 to the raster's native CRS
            clip_geom = [transform_geom(
                "EPSG:4326", src.crs.to_string(),
                mapping(bbox_geom_wgs84)
            )]
            out_image, out_transform = rio_mask(src, clip_geom, crop=True)
            out_meta = src.meta.copy()
            out_meta.update({
                "driver": "GTiff", "height": out_image.shape[1],
                "width": out_image.shape[2], "transform": out_transform,
            })
            with rasterio.open(dest, "w", **out_meta) as dst:
                dst.write(out_image)
        print(f"  ✓ {dest.name} ({dest.stat().st_size // 1024} KB)")

    # Compute NDVI = (NIR - Red) / (NIR + Red)
    print("  Computing NDVI raster …")
    with rasterio.open(b04_dest) as src_r, rasterio.open(b08_dest) as src_n:
        red = src_r.read(1).astype("float32")
        nir = src_n.read(1).astype("float32")
        # Sentinel-2 L2A scale factor: divide by 10000
        red /= 10000.0
        nir /= 10000.0
        denom = nir + red
        ndvi = np.where(denom > 0, (nir - red) / denom, np.nan).astype("float32")
        meta = src_r.meta.copy()
        meta.update({"dtype": "float32", "count": 1, "nodata": np.nan})
        with rasterio.open(ndvi_dest, "w", **meta) as dst:
            dst.write(ndvi, 1)
    print(f"  ✓ ndvi_summer2023.tif ({ndvi_dest.stat().st_size // 1024} KB)")


# ══════════════════════════════════════════════════════════════════════════
# 5. Landsat 8/9 Surface Temperature — via Planetary Computer
# ══════════════════════════════════════════════════════════════════════════
def download_landsat():
    print("\n── 5. Landsat 8/9 Surface Temperature (summer 2023) ────────────")
    out_dir = DATA_DIR / "landsat"
    out_dir.mkdir(exist_ok=True)
    lst_dest = out_dir / "lst_summer2023_celsius.tif"

    if _skip(lst_dest):
        return

    try:
        import planetary_computer
        import pystac_client
        import rasterio
        from rasterio.mask import mask as rio_mask
        from shapely.geometry import box, mapping
    except ImportError as e:
        print(f"  Missing package: {e}")
        return

    print("  Searching Planetary Computer for Landsat C2 L2 scenes …")
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )

    # Filter to Landsat 8 or 9 only — Landsat 7 (LE07) lacks the ST_B10 band
    # platform values: "landsat-8" or "landsat-9"
    search = catalog.search(
        collections=["landsat-c2-l2"],
        bbox=BCN_BBOX,
        datetime="2023-06-01/2023-09-30",
        query={
            "eo:cloud_cover": {"lt": 15},
            "platform": {"in": ["landsat-8", "landsat-9"]},
        },
        sortby="+eo:cloud_cover",
        max_items=10,
    )
    items = list(search.items())
    # Extra guard: exclude any LE07 scenes that slip through
    items = [i for i in items if not i.id.startswith("LE07")]
    if not items:
        print("  ERROR: No Landsat 8/9 scenes found. Try manual download from USGS EarthExplorer.")
        return

    item = items[0]
    cloud = item.properties.get("eo:cloud_cover", "?")
    date  = item.properties.get("datetime", "?")[:10]
    print(f"  Best scene: {item.id}  date={date}  cloud={cloud}%")

    # Reproject clip geometry to raster CRS (same fix as Sentinel-2)
    from rasterio.warp import transform_geom
    bbox_geom_wgs84 = box(*BCN_BBOX)

    # Planetary Computer names the thermal band "lwir11" (11µm = Band 10 on L8/L9)
    # Fallback chain covers any naming variant
    for candidate in ["lwir11", "ST_B10", "st", "thermal"]:
        if candidate in item.assets:
            band_key = candidate
            break
    else:
        band_key = next((k for k in item.assets if "lwir" in k or "st" in k.lower()), None)
    if band_key is None:
        print(f"  Available assets: {list(item.assets.keys())}")
        print("  ERROR: No thermal band found in this scene.")
        return
    print(f"  Using thermal band: {band_key}")

    raw_dest = out_dir / "ST_B10_raw.tif"
    if not raw_dest.exists():
        print(f"  Downloading {band_key} …")
        href = item.assets[band_key].href
        with rasterio.open(href) as src:
            clip_geom = [transform_geom("EPSG:4326", src.crs.to_string(),
                                        mapping(bbox_geom_wgs84))]
            out_image, out_transform = rio_mask(src, clip_geom, crop=True)
            out_meta = src.meta.copy()
            out_meta.update({
                "driver": "GTiff", "height": out_image.shape[1],
                "width": out_image.shape[2], "transform": out_transform,
            })
            with rasterio.open(raw_dest, "w", **out_meta) as dst:
                dst.write(out_image)
        print(f"  ✓ ST_B10_raw.tif ({raw_dest.stat().st_size // 1024} KB)")

    # Convert DN to Celsius: T(K) = 0.00341802 * DN + 149.0 → T(C) = T(K) - 273.15
    print("  Converting DN → Celsius …")
    with rasterio.open(raw_dest) as src:
        dn = src.read(1).astype("float32")
        nodata = src.nodata
        valid = dn != nodata if nodata is not None else np.ones_like(dn, dtype=bool)
        lst_kelvin = np.where(valid, 0.00341802 * dn + 149.0, np.nan)
        lst_celsius = np.where(valid, lst_kelvin - 273.15, np.nan).astype("float32")
        meta = src.meta.copy()
        meta.update({"dtype": "float32", "count": 1, "nodata": np.nan})
        with rasterio.open(lst_dest, "w", **meta) as dst:
            dst.write(lst_celsius, 1)

    city_mean = np.nanmean(lst_celsius)
    city_std  = np.nanstd(lst_celsius)
    print(f"  ✓ lst_summer2023_celsius.tif  mean={city_mean:.1f}°C  std={city_std:.1f}°C")


# ══════════════════════════════════════════════════════════════════════════
# 6. BCN Boundaries
# ══════════════════════════════════════════════════════════════════════════
def download_boundaries():
    print("\n── 6. BCN municipal boundary + districts ───────────────────────")

    # Municipal boundary via Nominatim
    bdry_dest = DATA_DIR / "bcn-boundary.geojson"
    if not _skip(bdry_dest):
        print("  Fetching BCN boundary from Nominatim …")
        url = (
            "https://nominatim.openstreetmap.org/search"
            "?q=Barcelona%2C+Catalunya&polygon_geojson=1&format=json&limit=1"
        )
        headers = {"User-Agent": "MycorrhizalBarcelonaProject/1.0"}
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        results = r.json()
        if results and results[0].get("geojson"):
            import json as _json
            bdry_dest.write_text(
                _json.dumps({"type": "Feature", "geometry": results[0]["geojson"],
                             "properties": {"name": "Barcelona"}}, indent=2),
                encoding="utf-8",
            )
            print(f"  ✓ bcn-boundary.geojson")
        else:
            print("  WARNING: Nominatim returned no polygon. Download manually from OSM.")

    # Districts via Overpass API (OSM admin boundaries, level 9 = BCN districts)
    dist_dest = DATA_DIR / "bcn-districts.geojson"
    if not _skip(dist_dest):
        import json as _json
        print("  Fetching BCN district boundaries from Overpass API …")
        # Fetch each of the 10 Barcelona districts via Nominatim
        BCN_DISTRICTS = [
            "Ciutat Vella", "Eixample", "Sants-Montjuïc", "Les Corts",
            "Sarrià-Sant Gervasi", "Gràcia", "Horta-Guinardó",
            "Nou Barris", "Sant Andreu", "Sant Martí",
        ]
        headers = {"User-Agent": "MycorrhizalBarcelonaProject/1.0"}
        features = []
        for district in BCN_DISTRICTS:
            r = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": f"{district}, Barcelona", "polygon_geojson": 1,
                        "format": "json", "limit": 1},
                headers=headers, timeout=20,
            )
            results = r.json() if r.status_code == 200 else []
            if results and results[0].get("geojson"):
                features.append({
                    "type": "Feature",
                    "geometry": results[0]["geojson"],
                    "properties": {"name": district},
                })
                print(f"    ✓ {district}")
            else:
                print(f"    - {district}: not found")
            time.sleep(1.1)   # Nominatim rate limit: 1 req/sec

        fc = {"type": "FeatureCollection", "features": features}
        dist_dest.write_text(_json.dumps(fc, indent=2), encoding="utf-8")
        print(f"  ✓ bcn-districts.geojson ({len(features)}/10 districts)")


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  Mycorrhizal Barcelona — Full Data Download")
    print("=" * 60)

    download_trees()
    download_gbif()
    download_fungalroot()
    download_sentinel2()
    download_landsat()
    download_boundaries()

    print("\n" + "=" * 60)
    print("  DONE.")
    print("=" * 60)
    print("""
⚠️  ONE DATASET STILL NEEDS MANUAL DOWNLOAD: Urban Atlas 2018
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Urban Atlas requires a free account at the Copernicus Land
Monitoring Service. This takes ~2 minutes to register.

Steps:
  1. Go to: https://land.copernicus.eu/local/urban-atlas/urban-atlas-2018
  2. Click "Download" → create a free account if prompted
  3. Search for Barcelona (or download the Spain national file)
  4. Save the GeoPackage or raster to:
       data/urban-atlas/BCN_UA2018.gpkg
     OR the impervious surface raster to:
       data/urban-atlas/imperviousness_2018.tif

Until Urban Atlas is downloaded, notebook 03 uses a synthetic
sealed-surface sub-score (Beta distribution, flagged as SYNTHETIC).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
