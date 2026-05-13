"""
download_data.py — NEXUS-Micro: Mycorrhizal Barcelona
======================================================

Downloads all programmatically-accessible datasets needed for the pipeline.
Run once from the repo root or from the data/ directory:

    python data/download_data.py

Idempotent: any file that already exists on disk is skipped automatically.
All downloads write into the same directory as this script (data/).

DATASET INVENTORY
-----------------
1. arbrat-viari.csv  — Ajuntament BCN street-tree inventory (145 478 rows).
   Source : Open Data BCN (ajuntament.barcelona.cat/opendata)
   License: CC-BY 4.0. Attribution: Ajuntament de Barcelona, Open Data BCN.
   Format : CSV, ~43 MB

2. arbrat-zona.csv   — Ajuntament BCN park/zone-tree inventory (43 612 rows).
   Source : Open Data BCN
   License: CC-BY 4.0. Attribution: Ajuntament de Barcelona, Open Data BCN.
   Format : CSV, ~14 MB

3. gbif-fungi.json   — GBIF fungal occurrence records, Barcelona bbox,
                       2015-2024, kingdom=Fungi, hasCoordinate=true.
   Source : GBIF REST API (api.gbif.org). No API key required for occurrence
            search. Data are licensed CC-BY / CC0 depending on the publishing
            institution; always cite individual dataset DOIs from the response.
   Format : JSON (GBIF occurrence API page 0, up to 300 records).
            For a full download (>300 records) use the GBIF occurrence download
            portal at https://www.gbif.org/occurrence/search and export as CSV.

4. bcn-boundary.geojson — Barcelona municipal boundary polygon.
   Source : Overpass API (OpenStreetMap data).
   License: ODbL (OpenStreetMap contributors).
   Format : GeoJSON

5. bcn-districts.geojson — Barcelona 10-district boundary polygons.
   Source : Open Data BCN — Districtes de Barcelona.
   License: CC-BY 4.0. Attribution: Ajuntament de Barcelona, Open Data BCN.
   Format : GeoJSON
   # VERIFY: URL below correct as of 2026-05. Confirm at
   # https://opendata-ajuntament.barcelona.cat/data/ca/dataset/
   #   20170706-districtes-barcelona

SATELLITE DATA (not downloaded here — see data/README-satellite.md)
--------------------------------------------------------------------
Urban Atlas, Sentinel-2, and Landsat imagery require manual portal download.
Refer to data/README-satellite.md for step-by-step instructions.
"""

import json
import os
import sys
import time

import requests
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Resolve the data/ directory relative to this script, regardless of where
# the user runs it from.
# ---------------------------------------------------------------------------
DATA_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _skip(path: str) -> bool:
    """Return True and print a message if the file already exists."""
    if os.path.isfile(path):
        size_mb = os.path.getsize(path) / 1_048_576
        print(f"  [skip] {os.path.basename(path)} already exists ({size_mb:.1f} MB)")
        return True
    return False


def _download_binary(url: str, dest: str, description: str, timeout: int = 120) -> None:
    """Stream-download a binary file with a tqdm progress bar."""
    print(f"\n[download] {description}")
    print(f"  URL : {url}")
    print(f"  Dest: {dest}")

    resp = requests.get(url, stream=True, timeout=timeout,
                        headers={"User-Agent": "NEXUS-Micro/1.0 (academic research)"})
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    chunk = 8_192

    with open(dest, "wb") as fh, tqdm(
        total=total, unit="B", unit_scale=True, unit_divisor=1024, desc=description[:40]
    ) as bar:
        for data in resp.iter_content(chunk_size=chunk):
            fh.write(data)
            bar.update(len(data))

    size_mb = os.path.getsize(dest) / 1_048_576
    print(f"  Done: {size_mb:.1f} MB written to {dest}")


# ---------------------------------------------------------------------------
# 1. Tree inventory CSVs
# ---------------------------------------------------------------------------

TREE_DOWNLOADS = [
    {
        "url": (
            "https://opendata-ajuntament.barcelona.cat/data/dataset/"
            "27b3f8a7-e536-4eea-b025-ce094817b2bd/resource/"
            "23124fd5-521f-40f8-85b8-efb1e71c2ec8/download"
        ),
        "filename": "arbrat-viari.csv",
        "description": "BCN street-tree inventory (arbrat viari)",
    },
    {
        "url": (
            "https://opendata-ajuntament.barcelona.cat/data/dataset/"
            "9b525e1d-13b8-48f1-abf6-f5cd03baa1dd/resource/"
            "29cd5c1f-11b1-404b-b3a5-ae29940b8c55/download"
        ),
        "filename": "arbrat-zona.csv",
        "description": "BCN park/zone-tree inventory (arbrat de zona)",
    },
]


def download_tree_inventories() -> None:
    print("\n=== 1/4  Tree Inventory CSVs (Open Data BCN, CC-BY 4.0) ===")
    for item in TREE_DOWNLOADS:
        dest = os.path.join(DATA_DIR, item["filename"])
        if _skip(dest):
            continue
        _download_binary(item["url"], dest, item["description"])


# ---------------------------------------------------------------------------
# 2. GBIF fungal occurrences
# ---------------------------------------------------------------------------

GBIF_API = "https://api.gbif.org/v1/occurrence/search"

GBIF_PARAMS = {
    "kingdomKey": 5,           # Fungi kingdom key in GBIF taxonomy
    "hasCoordinate": "true",
    "decimalLongitude": "2.052,2.230",   # Barcelona bbox: lon min,max
    "decimalLatitude": "41.310,41.475",  # Barcelona bbox: lat min,max
    "year": "2015,2024",
    "limit": 300,              # max per page; for full dataset use GBIF download
    "offset": 0,
}


def download_gbif_fungi() -> None:
    print("\n=== 2/4  GBIF Fungal Occurrences (GBIF API) ===")
    dest = os.path.join(DATA_DIR, "gbif-fungi.json")
    if _skip(dest):
        return

    print(f"  Querying GBIF occurrence API...")
    print(f"  Bbox: lon 2.052–2.230, lat 41.310–41.475 | years 2015–2024 | kingdom=Fungi")

    resp = requests.get(GBIF_API, params=GBIF_PARAMS, timeout=60,
                        headers={"User-Agent": "NEXUS-Micro/1.0 (academic research)"})
    resp.raise_for_status()
    payload = resp.json()

    total_reported = payload.get("count", "unknown")
    returned = len(payload.get("results", []))
    print(f"  GBIF reports {total_reported} total matches; retrieved {returned} records (page 0).")

    if total_reported > 300:
        print(
            "  WARNING: more than 300 records available. This script downloads the first\n"
            "  300 only (API limit per request). For a complete download, use the GBIF\n"
            "  occurrence portal: https://www.gbif.org/occurrence/search\n"
            "  Apply the same filters and export as CSV, saving to data/gbif-fungi-full.csv"
        )

    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)

    size_kb = os.path.getsize(dest) / 1_024
    print(f"  Done: {returned} records, {size_kb:.1f} KB written to {dest}")


# ---------------------------------------------------------------------------
# 3. Barcelona municipal boundary
# ---------------------------------------------------------------------------

# Overpass API query: fetch the OSM relation for Barcelona municipality and
# return it as GeoJSON via the overpass-api.de endpoint.
# Relation 347950 = Ajuntament de Barcelona (municipality).
# # VERIFY: relation ID 347950 is correct for Barcelona municipality as of 2026.
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_BOUNDARY_QUERY = """
[out:json][timeout:60];
relation(347950);
out geom;
""".strip()


def _overpass_to_geojson(overpass_response: dict) -> dict:
    """
    Convert an Overpass API 'out geom' relation response into a minimal
    GeoJSON FeatureCollection with a single multipolygon feature.

    This handles the common case where the relation contains outer and inner
    members with geometry. For a simpler alternative, use the nominatim
    polygon endpoint (see comment in download_bcn_boundary).
    """
    import json

    # Collect outer ring coordinates from 'way' members
    outer_rings = []
    inner_rings = []

    for member in overpass_response.get("elements", [{}])[0].get("members", []):
        if member.get("type") != "way" or "geometry" not in member:
            continue
        coords = [[pt["lon"], pt["lat"]] for pt in member["geometry"]]
        if len(coords) < 2:
            continue
        # Close the ring if not already closed
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        role = member.get("role", "outer")
        if role == "outer":
            outer_rings.append(coords)
        elif role == "inner":
            inner_rings.append(coords)

    if not outer_rings:
        return {}

    # Build a MultiPolygon: each outer ring paired with any inner rings
    polygons = [[ring] for ring in outer_rings]
    for inner in inner_rings:
        polygons[0].append(inner)  # attach inners to first outer (simplification)

    feature = {
        "type": "Feature",
        "properties": {
            "name": "Barcelona",
            "osm_relation": 347950,
            "source": "OpenStreetMap via Overpass API",
            "license": "ODbL (OpenStreetMap contributors)",
        },
        "geometry": {
            "type": "MultiPolygon",
            "coordinates": polygons,
        },
    }
    return {"type": "FeatureCollection", "features": [feature]}


def download_bcn_boundary() -> None:
    print("\n=== 3/4  Barcelona Municipal Boundary (OpenStreetMap / Overpass API) ===")
    dest = os.path.join(DATA_DIR, "bcn-boundary.geojson")
    if _skip(dest):
        return

    # Primary: Nominatim polygon lookup — simpler, returns clean GeoJSON
    # # VERIFY: Nominatim polygon endpoint returns the full boundary polygon.
    nominatim_url = (
        "https://nominatim.openstreetmap.org/search"
        "?q=Barcelona%2C+Spain"
        "&format=geojson"
        "&polygon_geojson=1"
        "&limit=1"
        "&addressdetails=0"
    )
    print(f"  Querying Nominatim for Barcelona boundary polygon...")
    resp = requests.get(
        nominatim_url, timeout=30,
        headers={"User-Agent": "NEXUS-Micro/1.0 (academic research; elkhouryrafik@gmail.com)"}
    )

    if resp.status_code == 200:
        data = resp.json()
        features = data.get("features", [])
        if features and features[0].get("geometry", {}).get("type") in (
            "Polygon", "MultiPolygon"
        ):
            feat = features[0]
            feat["properties"] = {
                "name": "Barcelona",
                "source": "Nominatim / OpenStreetMap",
                "license": "ODbL (OpenStreetMap contributors)",
            }
            geojson = {"type": "FeatureCollection", "features": [feat]}
            with open(dest, "w", encoding="utf-8") as fh:
                json.dump(geojson, fh, ensure_ascii=False, indent=2)
            size_kb = os.path.getsize(dest) / 1_024
            print(f"  Done (Nominatim): {size_kb:.1f} KB written to {dest}")
            return
        else:
            print("  Nominatim returned no polygon geometry; falling back to Overpass API...")
    else:
        print(f"  Nominatim returned HTTP {resp.status_code}; falling back to Overpass API...")

    # Fallback: Overpass API
    time.sleep(1)  # be polite to the free Overpass endpoint
    print(f"  Querying Overpass API (relation 347950)...")
    resp2 = requests.post(
        OVERPASS_URL,
        data={"data": OVERPASS_BOUNDARY_QUERY},
        timeout=90,
        headers={"User-Agent": "NEXUS-Micro/1.0 (academic research)"}
    )
    resp2.raise_for_status()
    geojson = _overpass_to_geojson(resp2.json())

    if not geojson.get("features"):
        print(
            "  ERROR: Could not derive a boundary polygon from either Nominatim or Overpass.\n"
            "  Manual fallback: download from Open Data BCN —\n"
            "  https://opendata-ajuntament.barcelona.cat/data/ca/dataset/limitsbcn\n"
            "  and save as data/bcn-boundary.geojson"
        )
        return

    with open(dest, "w", encoding="utf-8") as fh:
        json.dump(geojson, fh, ensure_ascii=False, indent=2)
    size_kb = os.path.getsize(dest) / 1_024
    print(f"  Done (Overpass): {size_kb:.1f} KB written to {dest}")


# ---------------------------------------------------------------------------
# 4. Barcelona district boundaries
# ---------------------------------------------------------------------------

# Open Data BCN — Districtes de Barcelona, GeoJSON endpoint.
# Dataset: https://opendata-ajuntament.barcelona.cat/data/ca/dataset/
#   20170706-districtes-barcelona
# # VERIFY: URL below is the direct GeoJSON resource link. Confirm it still
# # resolves at the Open Data BCN portal before relying on it.
BCN_DISTRICTS_URL = (
    "https://opendata-ajuntament.barcelona.cat/data/dataset/"
    "808daafa-d9ce-48c0-925a-fa5afdb1ed41/resource/"
    "f0fec1f3-dae9-42d6-8b86-08f60cf5e3e3/download"
)

# Nominatim fallback for districts: query each district by name if the
# direct URL above is unavailable.
DISTRICT_NAMES = [
    "Ciutat Vella", "Eixample", "Sants-Montjuïc", "Les Corts",
    "Sarrià-Sant Gervasi", "Gràcia", "Horta-Guinardó",
    "Nou Barris", "Sant Andreu", "Sant Martí",
]


def download_bcn_districts() -> None:
    print("\n=== 4/4  Barcelona District Boundaries (Open Data BCN, CC-BY 4.0) ===")
    dest = os.path.join(DATA_DIR, "bcn-districts.geojson")
    if _skip(dest):
        return

    print(f"  URL : {BCN_DISTRICTS_URL}")
    resp = requests.get(
        BCN_DISTRICTS_URL, timeout=60,
        headers={"User-Agent": "NEXUS-Micro/1.0 (academic research)"}
    )

    if resp.status_code == 200:
        # Validate it looks like GeoJSON before saving
        try:
            data = resp.json()
            if "features" in data or data.get("type") in ("FeatureCollection", "Feature"):
                with open(dest, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=2)
                size_kb = os.path.getsize(dest) / 1_024
                print(f"  Done: {size_kb:.1f} KB written to {dest}")
                return
        except ValueError:
            pass
        # If we got bytes (e.g., a raw GeoJSON file without JSON content-type)
        with open(dest, "wb") as fh:
            fh.write(resp.content)
        size_kb = os.path.getsize(dest) / 1_024
        print(f"  Done (raw): {size_kb:.1f} KB written to {dest}")
    else:
        print(
            f"  HTTP {resp.status_code} from Open Data BCN districts endpoint.\n"
            f"  Manual fallback: download from Open Data BCN —\n"
            f"  https://opendata-ajuntament.barcelona.cat/data/ca/dataset/"
            f"20170706-districtes-barcelona\n"
            f"  Choose the GeoJSON resource and save as data/bcn-districts.geojson"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 60)
    print("NEXUS-Micro data download script")
    print(f"Writing to: {DATA_DIR}")
    print("=" * 60)

    download_tree_inventories()
    download_gbif_fungi()
    download_bcn_boundary()
    download_bcn_districts()

    print("\n" + "=" * 60)
    print("Download complete. Files in data/:")
    for fname in sorted(os.listdir(DATA_DIR)):
        fpath = os.path.join(DATA_DIR, fname)
        if os.path.isfile(fpath):
            size_mb = os.path.getsize(fpath) / 1_048_576
            print(f"  {fname:<35} {size_mb:>8.2f} MB")
    print("=" * 60)
    print(
        "\nNext steps:\n"
        "  - For full GBIF records (>300), use the portal download and save\n"
        "    as data/gbif-fungi-full.csv\n"
        "  - For satellite data, follow data/README-satellite.md\n"
        "  - Run: jupyter notebook notebooks/01-data-profiling.ipynb"
    )


if __name__ == "__main__":
    main()
