#!/usr/bin/env python3
"""
fetch_platanus.py — Fetch OSM buildings and Platanus trees for the Barcelona study area.

Saves buildings.geojson and platanus_trees.geojson for use by wind_runner.py
and pollen_dispersion.py.

Adapted from HeatGuard/festival-shade/fetch_geodata.py (IAAC x Infrared City Hackathon 2026).
Key difference: Platanus-specific OSM tag filtering + integration with the
Ajuntament tree inventory as a fallback/enrichment source.

Usage:
  python3 fetch_platanus.py                 # reads config_barcelona.json
  python3 fetch_platanus.py --mock          # generates synthetic trees (no Overpass call)
"""

import json
import math
import sys
import random
import requests
from pathlib import Path

HERE = Path(__file__).parent
USE_MOCK = "--mock" in sys.argv

cfg = json.loads((HERE / "config_barcelona.json").read_text())
area = cfg["study_area"]
boundary = area["boundary"]["coordinates"][0]
lngs = [p[0] for p in boundary]
lats = [p[1] for p in boundary]
BBOX = f"{min(lats)},{min(lngs)},{max(lats)},{max(lngs)}"
POLY = " ".join(f"{p[1]} {p[0]}" for p in boundary)

OVERPASS = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "PollenDispersion/1.0 IAAC-Research"}

print(f"Study area: {area['name']}")
print(f"Bbox: {BBOX}")


# ── Buildings ────────────────────────────────────────────────────────────────

def fetch_buildings():
    q = f"""[out:json][timeout:60];
(
  way["building"](poly:"{POLY}");
);
out geom tags;"""
    print("Fetching buildings from Overpass...")
    r = requests.post(OVERPASS, data={"data": q}, headers=HEADERS, timeout=65, verify=False)
    r.raise_for_status()
    data = r.json()

    features = []
    for e in data.get("elements", []):
        geom = e.get("geometry") or []
        if len(geom) < 3:
            continue
        coords = [[n["lon"], n["lat"]] for n in geom]
        if coords[0] != coords[-1]:
            coords.append(coords[0])
        t = e.get("tags", {})
        try:
            h = float(t["height"])
        except (KeyError, ValueError):
            try:
                h = float(t["building:levels"]) * 3.2
            except (KeyError, ValueError):
                h = 20.0  # Eixample default ~6 floors
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [coords]},
            "properties": {"height": round(h, 1), "name": t.get("name", "")},
        })

    out = HERE / "buildings.geojson"
    out.write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    print(f"  {len(features)} buildings -> buildings.geojson")
    return features


def mock_buildings():
    """Synthetic Eixample-style block grid for offline testing."""
    w, e_lng = min(lngs), max(lngs)
    s, n = min(lats), max(lats)
    block = 0.00108  # ~120m Eixample block
    gap = 0.000180   # ~20m street
    features = []
    y = s + gap
    while y + block < n:
        x = w + gap
        while x + block < e_lng:
            h = random.choice([18.0, 21.0, 24.0])  # 5-7 floor Eixample
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [x, y], [x + block, y], [x + block, y + block],
                        [x, y + block], [x, y],
                    ]],
                },
                "properties": {"height": h, "name": ""},
            })
            x += block + gap
        y += block + gap

    out = HERE / "buildings.geojson"
    out.write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    print(f"  [MOCK] {len(features)} Eixample blocks -> buildings.geojson")
    return features


# ── Platanus trees ───────────────────────────────────────────────────────────

PLATANUS_TAGS = [
    "Platanus", "platanus", "Platanus x hispanica", "Platanus hispanica",
    "Platanus x acerifolia", "Platanus acerifolia", "Platanus x hybrida",
    "plane tree", "platan", "plataner",
]


def fetch_platanus_trees():
    """
    Fetch Platanus trees from OSM within study polygon.
    OSM street trees tagged with genus=Platanus or species=Platanus*.
    Also fetches rows tagged natural=tree_row with genus=Platanus.
    """
    tag_filter = "|".join(PLATANUS_TAGS)
    q = f"""[out:json][timeout:60];
(
  node["natural"="tree"]["genus"="Platanus"](poly:"{POLY}");
  node["natural"="tree"]["species"~"Platanus"](poly:"{POLY}");
  node["natural"="tree"]["taxon"~"Platanus"](poly:"{POLY}");
  node["natural"="tree"]["name"~"[Pp]lat[aà]n"](poly:"{POLY}");
  way["natural"="tree_row"]["genus"="Platanus"](poly:"{POLY}");
  way["natural"="tree_row"]["species"~"Platanus"](poly:"{POLY}");
);
out geom tags;"""
    print("Fetching Platanus trees from Overpass...")
    r = requests.post(OVERPASS, data={"data": q}, headers=HEADERS, timeout=65, verify=False)
    r.raise_for_status()
    data = r.json()

    features = []
    for e in data.get("elements", []):
        t = e.get("tags", {})
        if e["type"] == "node":
            # Estimate maturity from height tag or default to medium
            try:
                h = float(t.get("height") or "18")
            except ValueError:
                h = 18.0
            # Emission weight: taller = more pollen (proxy for maturity)
            emission = min(1.0, h / 25.0)
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [e["lon"], e["lat"]]},
                "properties": {
                    "species": t.get("species", "Platanus x hybrida"),
                    "height_m": round(h, 1),
                    "emission_weight": round(emission, 2),
                    "source": "osm",
                },
            })
        elif e["type"] == "way" and e.get("geometry"):
            # Tree row — sample points along the way
            geom = [(n["lon"], n["lat"]) for n in e["geometry"]]
            for i in range(len(geom) - 1):
                x0, y0 = geom[i]
                x1, y1 = geom[i + 1]
                seg_m = math.hypot((x1 - x0) * 111000 * math.cos(math.radians(y0)), (y1 - y0) * 111000)
                n_trees = max(1, int(seg_m / 8))  # ~8m spacing for Platanus rows
                for k in range(n_trees):
                    t_frac = (k + 0.5) / n_trees
                    features.append({
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [
                            x0 + t_frac * (x1 - x0),
                            y0 + t_frac * (y1 - y0),
                        ]},
                        "properties": {
                            "species": "Platanus x hybrida",
                            "height_m": 18.0,
                            "emission_weight": 0.7,
                            "source": "osm_tree_row",
                        },
                    })

    out = HERE / "platanus_trees.geojson"
    out.write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    print(f"  {len(features)} Platanus trees -> platanus_trees.geojson")
    if len(features) < 10:
        print("  NOTE: OSM Platanus tags are sparse — consider enriching from")
        print("  the Ajuntament tree inventory (data/raw/arbrat_viari.csv).")
    return features


def mock_platanus_trees():
    """
    Synthetic Platanus trees: place them along street centre-lines of
    the mock Eixample grid, every ~8m, mimicking Barcelona's planting pattern.
    """
    w, e_lng = min(lngs), max(lngs)
    s, n = min(lats), max(lats)
    block = 0.00108
    gap = 0.000180
    step = 0.000075  # ~8m tree spacing
    random.seed(42)
    features = []

    # Horizontal streets
    y = s + gap / 2
    while y < n:
        x = w
        while x < e_lng:
            jx = x + random.uniform(-step * 0.2, step * 0.2)
            jy = y + random.uniform(-gap * 0.15, gap * 0.15)
            h = random.uniform(14, 22)
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [round(jx, 6), round(jy, 6)]},
                "properties": {
                    "species": "Platanus x hybrida",
                    "height_m": round(h, 1),
                    "emission_weight": round(min(1.0, h / 25.0), 2),
                    "source": "mock",
                },
            })
            x += step
        y += block + gap

    # Vertical streets
    x = w + gap / 2
    while x < e_lng:
        y = s
        while y < n:
            jx = x + random.uniform(-gap * 0.15, gap * 0.15)
            jy = y + random.uniform(-step * 0.2, step * 0.2)
            h = random.uniform(14, 22)
            features.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [round(jx, 6), round(jy, 6)]},
                "properties": {
                    "species": "Platanus x hybrida",
                    "height_m": round(h, 1),
                    "emission_weight": round(min(1.0, h / 25.0), 2),
                    "source": "mock",
                },
            })
            y += step
        x += block + gap

    out = HERE / "platanus_trees.geojson"
    out.write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    print(f"  [MOCK] {len(features)} synthetic Platanus trees -> platanus_trees.geojson")
    return features


# ── Main ─────────────────────────────────────────────────────────────────────

if USE_MOCK:
    print("[MOCK MODE] Generating synthetic geometry — no Overpass calls.")
    mock_buildings()
    mock_platanus_trees()
else:
    fetch_buildings()
    fetch_platanus_trees()

print("\nDone. Next: python3 wind_runner.py [--mock]")
