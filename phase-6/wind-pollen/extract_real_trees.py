#!/usr/bin/env python3
"""
extract_real_trees.py — Extract real Platanus trees from the Ajuntament
arbrat-viari.csv and write platanus_trees.geojson for the Eixample study area.

Emission weight from categoria_arbrat maturity class:
  EXEMPLAR  → 1.00   (exceptional specimen, oldest/tallest, most pollen)
  PRIMERA   → 0.85   (first class, mature)
  SEGONA    → 0.65   (second class, medium maturity)
  TERCERA   → 0.45   (young / recently planted)
"""
import csv
import json
from pathlib import Path

HERE    = Path(__file__).parent
CSV     = HERE.parent.parent / "data" / "arbrat-viari.csv"

# Study area bounding box
W, S, E, N = 2.1490, 41.3820, 2.1700, 41.3960

EMISSION = {
    "EXEMPLAR": 1.00,
    "PRIMERA":  0.85,
    "SEGONA":   0.65,
    "TERCERA":  0.45,
}

features = []
skipped  = 0

with open(CSV, newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        if "Platanus" not in row.get("cat_nom_cientific", ""):
            continue
        try:
            lat = float(row["latitud"])
            lng = float(row["longitud"])
        except ValueError:
            skipped += 1
            continue
        if not (W <= lng <= E and S <= lat <= N):
            continue

        cat = row.get("categoria_arbrat", "TERCERA")
        emission = EMISSION.get(cat, 0.50)

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lng, 6), round(lat, 6)]},
            "properties": {
                "codi":            row["codi"],
                "species":         row["cat_nom_cientific"],
                "address":         row["adreca"],
                "categoria_arbrat": cat,
                "emission_weight": emission,
                "source":          "ajuntament-arbrat-viari",
            },
        })

out = HERE / "platanus_trees.geojson"
out.write_text(json.dumps({
    "type": "FeatureCollection",
    "features": features,
    "metadata": {
        "source": "data/arbrat-viari.csv",
        "n_total_city": 40398,
        "bbox": [W, S, E, N],
        "emission_key": EMISSION,
    }
}))

from collections import Counter
cats = Counter(f["properties"]["categoria_arbrat"] for f in features)
print(f"Real Platanus trees in Eixample bbox: {len(features)}")
for cat, n in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {cat:10s}: {n:4d}  (emission {EMISSION.get(cat,'?')})")
if skipped:
    print(f"Skipped {skipped} rows with missing coords")
print(f"Saved -> platanus_trees.geojson")
