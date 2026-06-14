#!/usr/bin/env python3
"""
wind_runner.py — Run Infrared wind-speed simulation for the Barcelona study area.

Reads buildings.geojson (from fetch_platanus.py) and config_barcelona.json.
Calls the Infrared SDK wind_speed analysis and writes wind_result.json.

The wind_result.json grid gives wind speed magnitude at pedestrian height (1.5m)
for every 5m cell in the study polygon. pollen_dispersion.py uses this to weight
the Gaussian plume from each Platanus tree.

Adapted from HeatGuard/festival-shade/infrared_runner.py (IAAC x Infrared Hackathon 2026).
Key difference: WindModelRequest (single speed + direction) instead of UTCI.

Usage:
  python3 wind_runner.py                     # live — needs INFRARED_API_KEY in .env
  python3 wind_runner.py --mock              # synthetic wind field, no API key
  python3 wind_runner.py --wind tramontane   # use tramontane scenario from config
  INFRARED_MOCK=1 python3 wind_runner.py     # mock via env var

Wind scenarios (from config_barcelona.json):
  sea_breeze  : 4 m/s from SE 135deg  [DEFAULT — dominant March-April daytime]
  tramontane  : 6 m/s from NW 315deg  [strongest dispersal, episodic]
  calm        : 2 m/s from S  180deg  [worst case — pollen stays near source]
"""

import sys
import json
import os
import math
import random
from pathlib import Path

HERE = Path(__file__).parent

# ── Load config ───────────────────────────────────────────────────────────────
cfg = json.loads((HERE / "config_barcelona.json").read_text())
area = cfg["study_area"]
polygon = area["boundary"]
wind_scenarios = cfg["wind"]

# Select wind scenario
scenario_key = "march_april_sea_breeze"
for arg in sys.argv:
    if arg in ("--tramontane", "tramontane"):
        scenario_key = "tramontane"
    elif arg in ("--calm", "calm"):
        scenario_key = "calm"

scenario = wind_scenarios[scenario_key]
WIND_SPEED = scenario["speed_ms"]
WIND_DIR = scenario["direction_deg"]
USE_MOCK = "--mock" in sys.argv or os.environ.get("INFRARED_MOCK") == "1"

print(f"Wind scenario: {scenario['label']}")
print(f"  Speed: {WIND_SPEED} m/s | Direction: {WIND_DIR} deg")


# ── Mock wind field ───────────────────────────────────────────────────────────

def mock_wind_field(polygon: dict, speed: float, direction_deg: float) -> dict:
    """
    Synthetic wind field for offline testing.
    Simulates urban canyon channelling: wind accelerates in streets aligned
    with the wind direction and decelerates in sheltered zones behind buildings.
    Resolution: 5m/cell.
    """
    ring = polygon["coordinates"][0]
    lngs = [p[0] for p in ring]
    lats = [p[1] for p in ring]
    w, s = min(lngs), min(lats)
    e, n = max(lngs), max(lats)

    m_per_deg_lat = 111_000
    m_per_deg_lng = 111_000 * math.cos(math.radians((s + n) / 2))
    site_h = (n - s) * m_per_deg_lat
    site_w = (e - w) * m_per_deg_lng
    cell = 5
    height = max(10, round(site_h / cell))
    width = max(10, round(site_w / cell))

    # Direction vector (wind blows FROM direction_deg, so travel direction is opposite)
    dir_rad = math.radians(direction_deg + 180)
    dx = math.sin(dir_rad)
    dy = math.cos(dir_rad)

    random.seed(42)
    grid = []
    for r in range(height):
        row = []
        for c in range(width):
            # Street alignment factor: higher when cell aligns with wind
            norm_x = (c / width - 0.5)
            norm_y = (r / height - 0.5)
            alignment = abs(dx * norm_x + dy * norm_y)
            # Eixample block shadow: periodic low-wind zones behind blocks
            block_x = (c * cell) % 140  # 140m = block+street cycle
            block_y = (r * cell) % 140
            in_block = (10 < block_x < 120) and (10 < block_y < 120)
            shelter = 0.3 if in_block else 1.0
            noise = random.gauss(0, 0.3)
            v = max(0.1, speed * (0.5 + 0.5 * alignment) * shelter + noise)
            row.append(round(v, 2))
        grid.append(row)

    print(f"[MOCK] Wind field: {height}x{width} at 5m/cell ({site_h:.0f}x{site_w:.0f}m site)")
    return {
        "grid": grid,
        "bounds": [w, s, e, n],
        "grid_shape": [height, width],
        "cell_size_m": cell,
        "wind_speed_ms": speed,
        "wind_direction_deg": direction_deg,
        "scenario": scenario_key,
        "min_legend": 0.0,
        "max_legend": speed * 1.8,
    }


# ── Live Infrared SDK path ────────────────────────────────────────────────────

def live_wind_field(polygon: dict, speed: float, direction_deg: float) -> dict:
    from infrared_sdk import InfraredClient
    from infrared_sdk.analyses.types import WindModelRequest, AnalysesName

    payload = WindModelRequest(
        analysis_type=AnalysesName.wind_speed,
        wind_speed=int(round(speed)),
        wind_direction=int(round(direction_deg)),
    )

    print("Fetching buildings for polygon...")
    with InfraredClient() as client:
        area_data = client.buildings.get_area(polygon)
        print(f"Buildings fetched. Submitting wind job (speed={speed}m/s, dir={direction_deg}deg)...")
        result = client.run_area_and_wait(payload, polygon, buildings=area_data.buildings)

    print(f"Job done. Grid shape: {result.grid_shape}")

    import numpy as np
    grid = result.merged_grid
    grid_list = [[None if np.isnan(v) else float(v) for v in row] for row in grid]

    return {
        "grid": grid_list,
        "bounds": list(result.bounds) if result.bounds is not None else None,
        "grid_shape": list(result.grid_shape),
        "cell_size_m": 5,
        "wind_speed_ms": speed,
        "wind_direction_deg": direction_deg,
        "scenario": scenario_key,
        "min_legend": result.min_legend,
        "max_legend": result.max_legend,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

if USE_MOCK:
    output = mock_wind_field(polygon, WIND_SPEED, WIND_DIR)
else:
    output = live_wind_field(polygon, WIND_SPEED, WIND_DIR)

out_path = HERE / f"wind_result_{scenario_key}.json"
out_path.write_text(json.dumps(output))
print(f"Wind field saved -> {out_path.name}")
print(f"Next: python3 pollen_dispersion.py --wind {scenario_key}")
