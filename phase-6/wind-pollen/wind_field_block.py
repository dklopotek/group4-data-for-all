#!/usr/bin/env python3
"""
wind_field_block.py — Crop Infrared wind results to a single city block,
downsample to 5m, and attach tree positions.

Inputs:  wind_result_*.json (from wind_runner.py), platanus_trees.geojson
Output:  block_wind_field.json  (small, browser-ready)

Usage:
  python3 wind_field_block.py                     # sea_breeze (default)
  python3 wind_field_block.py --wind tramontane
  python3 wind_field_block.py --wind calm
"""

import json, math, sys
from pathlib import Path

HERE = Path(__file__).parent

# ── Block definition ──────────────────────────────────────────────────────────
# Central Eixample: Carrer de Provença x Carrer de Balmes area
BLOCK_CENTER = [2.1585, 41.3905]
BLOCK_HALF_M = 350          # ±350m → 700×700m window
DOWNSAMPLE   = 5            # every 5th cell of ~1m grid → ~5m output

M_PER_DEG_LAT = 111_000
M_PER_DEG_LNG = 111_000 * math.cos(math.radians(BLOCK_CENTER[1]))

dlat = BLOCK_HALF_M / M_PER_DEG_LAT
dlng = BLOCK_HALF_M / M_PER_DEG_LNG

BLOCK_BBOX = [
    BLOCK_CENTER[0] - dlng,
    BLOCK_CENTER[1] - dlat,
    BLOCK_CENTER[0] + dlng,
    BLOCK_CENTER[1] + dlat,
]

# ── Select scenario ───────────────────────────────────────────────────────────
scenario_key = "march_april_sea_breeze"
for a in sys.argv:
    if a in ("tramontane", "--tramontane"):
        scenario_key = "tramontane"
    elif a in ("calm", "--calm"):
        scenario_key = "calm"

src = HERE / f"wind_result_{scenario_key}.json"
if not src.exists():
    print(f"ERROR: {src.name} not found. Run wind_runner.py first.")
    sys.exit(1)

print(f"Loading {src.name} ...")
wr = json.loads(src.read_text())
full_grid  = wr["grid"]
n_rows, n_cols = wr["grid_shape"]
bW, bS, bE, bN = wr["bounds"]

print(f"Full grid: {n_rows}x{n_cols}, bounds [{bW:.4f},{bS:.4f},{bE:.4f},{bN:.4f}]")

# ── Crop to block ─────────────────────────────────────────────────────────────
def lng_to_col(lng):
    return int((lng - bW) / (bE - bW) * n_cols)

def lat_to_row(lat):
    return int((lat - bS) / (bN - bS) * n_rows)

c0 = max(0, lng_to_col(BLOCK_BBOX[0]))
c1 = min(n_cols - 1, lng_to_col(BLOCK_BBOX[2]))
r0 = max(0, lat_to_row(BLOCK_BBOX[1]))
r1 = min(n_rows - 1, lat_to_row(BLOCK_BBOX[3]))

print(f"Crop: rows {r0}-{r1}, cols {c0}-{c1}  ({r1-r0}x{c1-c0} cells)")

# ── Downsample ────────────────────────────────────────────────────────────────
step = DOWNSAMPLE
speed_grid = []
for r in range(r0, r1 + 1, step):
    row = []
    for c in range(c0, c1 + 1, step):
        v = full_grid[r][c]
        row.append(round(v, 3) if v is not None else 0.0)
    speed_grid.append(row)

out_rows = len(speed_grid)
out_cols = len(speed_grid[0]) if speed_grid else 0

# Actual geographic bbox of the cropped+downsampled grid
actual_bbox = [
    bW + c0 / n_cols * (bE - bW),
    bS + r0 / n_rows * (bN - bS),
    bW + c1 / n_cols * (bE - bW),
    bS + r1 / n_rows * (bN - bS),
]
print(f"Output grid: {out_rows}x{out_cols} at ~{step}m/cell")

# ── Load trees ────────────────────────────────────────────────────────────────
trees_fc = json.loads((HERE / "platanus_trees.geojson").read_text())
trees = []
for f in trees_fc["features"]:
    lng, lat = f["geometry"]["coordinates"][:2]
    if actual_bbox[0] <= lng <= actual_bbox[2] and actual_bbox[1] <= lat <= actual_bbox[3]:
        trees.append({
            "position": [lng, lat],
            "emission":  f["properties"].get("emission_weight", 0.7),
            "address":   f["properties"].get("address", ""),
            "categoria": f["properties"].get("categoria_arbrat", ""),
        })
print(f"Trees in block: {len(trees)}")

# ── Write output ──────────────────────────────────────────────────────────────
out = {
    "scenario":          scenario_key,
    "bbox":              actual_bbox,
    "grid_shape":        [out_rows, out_cols],
    "cell_size_m":       step,
    "wind_speed_ms":     wr.get("wind_speed_ms"),
    "wind_direction_deg": wr.get("wind_direction_deg"),
    "speed_grid":        speed_grid,
    "trees":             trees,
}

label_map = {
    "march_april_sea_breeze": "sea_breeze",
    "tramontane": "tramontane",
    "calm": "calm",
}
out_label = label_map.get(scenario_key, scenario_key)
out_path  = HERE / f"block_wind_field_{out_label}.json"
out_path.write_text(json.dumps(out, separators=(",", ":")))
kb = out_path.stat().st_size // 1024
print(f"Saved {out_path.name} ({kb} KB)  — {out_rows}x{out_cols} grid, {len(trees)} trees")
