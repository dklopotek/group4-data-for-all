#!/usr/bin/env python3
"""
pollen_dispersion.py — Gaussian plume pollen dispersion from Platanus trees.

Reads:
  platanus_trees.geojson   tree locations + emission weights
  wind_result_<scenario>.json   wind speed field from Infrared (or mock)
  config_barcelona.json    pollen physics parameters

Outputs:
  pollen_grid_<scenario>.json   pollen concentration grid (same shape as wind grid)
  pollen_grid_<scenario>.geojson  GeoJSON for deck.gl visualisation

Science:
  Gaussian plume (horizontal, 2D) per tree. Each tree contributes a pollen
  concentration field that decays downwind with distance and spreads laterally.
  The wind field from Infrared modulates local wind speed cell-by-cell, so
  pollen disperses faster in street corridors and pools behind sheltered blocks.

  C(x,y) proportional to  Q / (sigma_y * U)
                         * exp( -y^2 / (2 * sigma_y^2) )
  where:
    Q   = emission strength (tree height proxy)
    U   = local wind speed (from Infrared grid)
    x   = downwind distance from tree
    y   = crosswind distance from tree
    sigma_y = lateral spread = 0.22 * x^0.9  (Pasquill-Gifford D class)

Usage:
  python3 pollen_dispersion.py                         # sea_breeze scenario
  python3 pollen_dispersion.py --wind tramontane
  python3 pollen_dispersion.py --wind calm
"""

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent

# ── Wind scenario ─────────────────────────────────────────────────────────────
scenario = "march_april_sea_breeze"
for arg in sys.argv:
    if arg in ("--wind", ):
        idx = sys.argv.index(arg)
        if idx + 1 < len(sys.argv):
            scenario = sys.argv[idx + 1]
    elif arg in ("tramontane", "calm"):
        scenario = arg if arg != "tramontane" else "tramontane"
        if arg == "tramontane":
            scenario = "tramontane"
        elif arg == "calm":
            scenario = "calm"

# Normalise shorthand
if scenario == "tramontane":
    scenario = "tramontane"
elif scenario == "calm":
    scenario = "calm"
elif "sea" in scenario or scenario == "sea_breeze":
    scenario = "march_april_sea_breeze"

print(f"Pollen dispersion for wind scenario: {scenario}")

# ── Load inputs ───────────────────────────────────────────────────────────────
cfg = json.loads((HERE / "config_barcelona.json").read_text())
pollen_cfg = cfg["pollen"]

wind_path = HERE / f"wind_result_{scenario}.json"
if not wind_path.exists():
    print(f"ERROR: {wind_path.name} not found. Run wind_runner.py first.")
    sys.exit(1)
wind_data = json.loads(wind_path.read_text())

trees_path = HERE / "platanus_trees.geojson"
if not trees_path.exists():
    print("ERROR: platanus_trees.geojson not found. Run fetch_platanus.py first.")
    sys.exit(1)
trees_fc = json.loads(trees_path.read_text())
trees = trees_fc["features"]
print(f"Loaded {len(trees)} Platanus trees")

# ── Grid geometry ─────────────────────────────────────────────────────────────
grid_raw = wind_data["grid"]
n_rows = len(grid_raw)
n_cols = len(grid_raw[0]) if n_rows > 0 else 0
cell_m = wind_data.get("cell_size_m", 5)
bounds = wind_data["bounds"]  # [w, s, e, n]
W, S, E, N = bounds

wind_speed_ms = wind_data["wind_speed_ms"]
wind_dir_deg = wind_data["wind_direction_deg"]

# Wind travel direction (where pollen goes)
travel_rad = math.radians(wind_dir_deg + 180)
wind_dx = math.sin(travel_rad)   # east component
wind_dy = math.cos(travel_rad)   # north component

print(f"Grid: {n_rows}x{n_cols} cells at {cell_m}m/cell")
print(f"Wind: {wind_speed_ms}m/s from {wind_dir_deg}deg -> travel ({wind_dx:.2f}, {wind_dy:.2f})")

# Wind speed grid as numpy array (replace None with background speed)
wind_grid = np.array([
    [wind_speed_ms if v is None else v for v in row]
    for row in grid_raw
], dtype=float)

# ── Grid coordinate helpers ──────────────────────────────────────────────────
m_per_deg_lat = 111_000
m_per_deg_lng = 111_000 * math.cos(math.radians((S + N) / 2))

def lng_to_col(lng: float) -> int:
    return int((lng - W) / (E - W) * n_cols)

def lat_to_row(lat: float) -> int:
    return int((lat - S) / (N - S) * n_rows)

def cell_center_m(row: int, col: int):
    """Return (x_m, y_m) of cell center relative to study area SW corner."""
    x = (col + 0.5) * cell_m
    y = (row + 0.5) * cell_m
    return x, y

def tree_pos_m(lng: float, lat: float):
    """Return (x_m, y_m) of a tree relative to study area SW corner."""
    x = (lng - W) * m_per_deg_lng
    y = (lat - S) * m_per_deg_lat
    return x, y

# ── Pollen physics parameters ─────────────────────────────────────────────────
MAX_RADIUS_M = cfg["simulation"]["max_dispersion_radius_m"]
SETTLING_V = pollen_cfg["settling_velocity_ms"]      # 0.003 m/s for 32um grain
RELEASE_H = pollen_cfg["release_height_m"]            # 18m above ground

def sigma_y(x_m: float) -> float:
    """Pasquill-Gifford lateral spread, stability class D (neutral — typical day)."""
    if x_m <= 0:
        return 0.5
    return 0.22 * (x_m ** 0.9)

def plume_concentration(x_down: float, y_cross: float, emission: float, u: float) -> float:
    """
    2D Gaussian plume concentration at (x_down, y_cross) from source.
    x_down: downwind distance (m), must be > 0
    y_cross: crosswind distance (m)
    emission: tree emission weight [0-1]
    u: local wind speed (m/s)
    Returns relative concentration [0-1 scaled].
    """
    if x_down <= 0 or u < 0.1:
        return 0.0
    sy = sigma_y(x_down)
    # Distance-limited settling: pollen settles after travel = U * H / Vs
    max_travel = u * RELEASE_H / max(SETTLING_V, 1e-6)
    if x_down > min(MAX_RADIUS_M, max_travel):
        return 0.0
    c = emission / (sy * u + 1e-6) * math.exp(-0.5 * (y_cross / sy) ** 2)
    return c

# ── Vectorized pollen accumulation ───────────────────────────────────────────
# Build a plume kernel once, then stamp it at each tree location (much faster
# than per-cell Python loops). Kernel is centred on the source tree.

radius_cells = int(MAX_RADIUS_M / cell_m)
kr = radius_cells
kernel_size = 2 * kr + 1

# Kernel coordinate offsets in metres (col = x/east, row = y/north)
ky_idx, kx_idx = np.mgrid[-kr:kr+1, -kr:kr+1]
kx_m = kx_idx.astype(float) * cell_m   # east offset
ky_m = ky_idx.astype(float) * cell_m   # north offset

# Project offsets onto wind axes (downwind / crosswind)
x_down_k = kx_m * wind_dx + ky_m * wind_dy
y_cross_k = -kx_m * wind_dy + ky_m * wind_dx

# Lateral spread sigma_y(x_down) — vectorized
valid = x_down_k > 0
sy_k = np.where(valid, 0.22 * np.abs(x_down_k) ** 0.9, 0.5)

# Max travel distance from settling
max_travel = wind_speed_ms * RELEASE_H / max(SETTLING_V, 1e-6)
in_range = valid & (x_down_k <= min(MAX_RADIUS_M, max_travel))

# Gaussian lateral decay (unit emission, unit wind speed)
gauss_k = np.where(
    in_range,
    np.exp(-0.5 * (y_cross_k / np.maximum(sy_k, 0.01)) ** 2) / (sy_k * wind_speed_ms + 1e-6),
    0.0,
)

pollen_grid = np.zeros((n_rows, n_cols), dtype=float)
skipped = 0

print(f"Stamping plumes for {len(trees)} trees (kernel {kernel_size}x{kernel_size})...")
for feat in trees:
    coords = feat["geometry"]["coordinates"]
    emission = feat["properties"].get("emission_weight", 0.7)
    lng, lat = coords[0], coords[1]

    if not (W <= lng <= E and S <= lat <= N):
        skipped += 1
        continue

    t_col = lng_to_col(lng)
    t_row = lat_to_row(lat)

    # Grid slice bounds (clip to grid edges)
    r0_g = max(0, t_row - kr);  r1_g = min(n_rows, t_row + kr + 1)
    c0_g = max(0, t_col - kr);  c1_g = min(n_cols, t_col + kr + 1)
    r0_k = r0_g - (t_row - kr); r1_k = r0_k + (r1_g - r0_g)
    c0_k = c0_g - (t_col - kr); c1_k = c0_k + (c1_g - c0_g)

    pollen_grid[r0_g:r1_g, c0_g:c1_g] += emission * gauss_k[r0_k:r1_k, c0_k:c1_k]

if skipped:
    print(f"  Skipped {skipped} trees outside study area")

# ── Normalise to 0-1 ─────────────────────────────────────────────────────────
p_max = float(pollen_grid.max())
if p_max > 0:
    pollen_norm = pollen_grid / p_max
else:
    pollen_norm = pollen_grid

print(f"Peak raw concentration: {p_max:.4f}")
print(f"Cells with >50% max: {int((pollen_norm > 0.5).sum())} / {n_rows * n_cols}")

# ── Write pollen grid JSON ────────────────────────────────────────────────────
grid_list = [[round(float(v), 4) for v in row] for row in pollen_norm]
result = {
    "grid": grid_list,
    "bounds": bounds,
    "grid_shape": [n_rows, n_cols],
    "cell_size_m": cell_m,
    "scenario": scenario,
    "wind_speed_ms": wind_speed_ms,
    "wind_direction_deg": wind_dir_deg,
    "n_trees": len(trees) - skipped,
    "min_legend": 0.0,
    "max_legend": 1.0,
    "legend_label": "Relative pollen concentration (0=none, 1=peak)",
    "source": "Gaussian plume + Infrared wind field | Platanus x hybrida | March-April",
}
out_json = HERE / f"pollen_grid_{scenario}.json"
out_json.write_text(json.dumps(result))
print(f"Pollen grid -> {out_json.name}")

# ── Write GeoJSON for deck.gl ─────────────────────────────────────────────────
# Convert grid cells with concentration > 0.05 to polygon features
features = []
d_lng = (E - W) / n_cols
d_lat = (N - S) / n_rows

for r in range(n_rows):
    for c in range(n_cols):
        v = float(pollen_norm[r, c])
        if v < 0.05:
            continue
        cell_w = W + c * d_lng
        cell_s = S + r * d_lat
        cell_e = cell_w + d_lng
        cell_n = cell_s + d_lat
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[
                    [cell_w, cell_s], [cell_e, cell_s],
                    [cell_e, cell_n], [cell_w, cell_n],
                    [cell_w, cell_s],
                ]],
            },
            "properties": {
                "concentration": round(v, 3),
                "row": r, "col": c,
            },
        })

out_geojson = HERE / f"pollen_grid_{scenario}.geojson"
out_geojson.write_text(json.dumps({
    "type": "FeatureCollection",
    "features": features,
    "metadata": {
        "scenario": scenario,
        "n_source_trees": len(trees) - skipped,
        "wind_speed_ms": wind_speed_ms,
        "wind_direction_deg": wind_dir_deg,
    }
}))
print(f"GeoJSON for visualisation -> {out_geojson.name}")
print(f"  {len(features)} cells with concentration > 5% of peak")
print("\nDone. Load pollen_grid_*.geojson in QGIS or deck.gl to visualise.")
