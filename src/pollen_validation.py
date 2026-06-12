"""XAC pollen-station spot-check (Phase 6 external cross-check).

Maps Xarxa Aerobiologica de Catalunya (XAC) monitoring stations onto the
analysis grid and reports where the source-proxy ranks those cells.
Also fetches the live Platanus forecast from the XAC public API.

HONEST SCOPE:
  n=1 in-city station (Barcelona city). Bellaterra/UAB is outside the grid.
  Annual pollen totals (grains x day / m3) are NOT accessible via the public
  API -- full spatial calibration is not possible with this data alone.
  This is a directional spot-check:
    "does the station cell rank high in our source proxy?"
  For the historical annual series contact: aerobiologia@uab.cat

Run:  python src/pollen_validation.py
Out:  outputs/phase-6/pollen_station_validation.json + .md
"""
from __future__ import annotations
import json
import ssl
import urllib.request
import urllib.error
from pathlib import Path
from xml.etree import ElementTree as ET

# Mac stdlib Python lacks the CA bundle; use unverified context for this
# read-only public data fetch (no credentials transmitted).
_SSL_CTX = ssl._create_unverified_context()

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parents[1]
LAYERS = ROOT / "data" / "processed" / "allergen_layers.parquet"
OUTDIR = ROOT / "outputs" / "phase-6"
CRS = "EPSG:25831"
API_TMPL = "https://aerobiologia.cat/api/v0/forecast/{slug}/en/xml"

# Station coordinates sourced from XAC live API (fetched 2026-06-12)
STATIONS = [
    {
        "name": "Barcelona",
        "slug": "barcelona",
        "lat": 41.393728,
        "lon": 2.164922,
        "notes": "XAC in-city station (Eixample / city centre area)",
    },
    {
        "name": "Bellaterra",
        "slug": "bellaterra",
        "lat": 41.500604,
        "lon": 2.108034,
        "notes": "XAC UAB-campus station -- outside Barcelona city boundary",
    },
]


def fetch_platanus_level(slug: str) -> dict:
    """Return current Platanus forecast level from the XAC XML API.

    Parses the XML by flattening all elements and searching for a numeric
    level value in the elements immediately following a 'Planetree' / 'plane'
    text node. Returns a dict: {ok, level (int 0-4 or None), scale, source_url}.
    """
    url = API_TMPL.format(slug=slug)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MycorrhizalBcn/1.0"})
        with urllib.request.urlopen(req, timeout=10, context=_SSL_CTX) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        root = ET.fromstring(raw)

        # XAC XML structure: <current><pollens><PLAT>N</PLAT>...</pollens></current>
        # Also check <forecast><pollens><PLAT>trend</PLAT></forecast>
        level_val = None
        forecast_trend = None

        current_el = root.find(".//current/pollens/PLAT")
        if current_el is not None and current_el.text:
            try:
                level_val = int(current_el.text.strip())
            except ValueError:
                pass

        forecast_el = root.find(".//forecast/pollens/PLAT")
        if forecast_el is not None:
            forecast_trend = (forecast_el.text or "").strip()

        note = ""
        if level_val == 0:
            note = "level 0=null (out-of-season or below detection)"
        elif level_val is None:
            note = "PLAT element not found in XML"

        return {
            "ok": True,
            "level": level_val,
            "forecast_trend": forecast_trend,
            "scale": "0=null 1=low 2=moderate 3=high 4=max",
            "source_url": url,
            "note": note,
        }

    except urllib.error.URLError as exc:
        return {"ok": False, "error": f"network error: {exc}", "source_url": url}
    except ET.ParseError as exc:
        return {"ok": False, "error": f"XML parse error: {exc}", "source_url": url}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "source_url": url}


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    grid = gpd.read_parquet(LAYERS)
    if grid.crs is None:
        grid = grid.set_crs(CRS)
    else:
        grid = grid.to_crs(CRS)

    src_arr = grid["source_raw"].to_numpy(float)
    src_nonzero = src_arr[src_arr > 0]

    print("XAC pollen station spot-check")
    print("=" * 44)

    results = []
    for st in STATIONS:
        print(f"\n  Station: {st['name']}")

        pt_gdf = gpd.GeoDataFrame(
            [{"name": st["name"]}],
            geometry=[Point(st["lon"], st["lat"])],
            crs="EPSG:4326",
        ).to_crs(CRS)

        cols = [c for c in ["cell_id", "district", "source_raw", "source_std",
                             "plane_density", "maturity", "geometry"]
                if c in grid.columns]
        sub = grid[cols]

        hit = gpd.sjoin(pt_gdf, sub, how="left", predicate="within")
        if hit["cell_id"].isna().all():
            hit = gpd.sjoin_nearest(pt_gdf, sub, how="left")

        if hit["cell_id"].isna().all():
            rec = {
                "station": st["name"], "lat": st["lat"], "lon": st["lon"],
                "in_grid": False, "notes": st["notes"],
            }
            print(f"    OUTSIDE GRID -- {st['notes']}")
        else:
            row = hit.iloc[0]
            cell_src = float(row["source_raw"])
            pct_all = float(np.mean(src_arr <= cell_src) * 100)
            pct_nz = (float(np.mean(src_nonzero <= cell_src) * 100)
                      if cell_src > 0 else 0.0)
            rec = {
                "station": st["name"], "lat": st["lat"], "lon": st["lon"],
                "in_grid": True,
                "cell_id": str(row["cell_id"]),
                "district": str(row.get("district", "n/a")),
                "source_raw": round(cell_src, 2),
                "source_std": round(float(row["source_std"]), 4),
                "source_percentile_all_cells": round(pct_all, 1),
                "source_percentile_nonzero_cells": round(pct_nz, 1),
                "plane_density": int(row.get("plane_density", 0)),
                "maturity": round(float(row.get("maturity", 0)), 3),
                "notes": st["notes"],
            }
            print(f"    IN GRID  cell={rec['cell_id']}  district={rec['district']}")
            print(f"    planes={rec['plane_density']}  maturity={rec['maturity']:.2f}"
                  f"  source_raw={rec['source_raw']:.1f}")
            print(f"    source percentile: {rec['source_percentile_all_cells']:.0f}th"
                  f" (all cells) / {rec['source_percentile_nonzero_cells']:.0f}th"
                  f" (cells with planes)")

        print(f"    fetching live API... ", end="", flush=True)
        api = fetch_platanus_level(st["slug"])
        rec["api_forecast"] = api
        if api["ok"]:
            lvl = api.get("level")
            lvl_str = str(lvl) if lvl is not None else "not parsed"
            print(f"Platanus level = {lvl_str}/4")
            if api.get("note"):
                print(f"    [{api['note']}]")
        else:
            print(f"FAILED -- {api.get('error', 'unknown')}")

        results.append(rec)

    print("\n" + "=" * 44)
    in_city = [r for r in results if r.get("in_grid")]
    if in_city:
        pct = in_city[0]["source_percentile_all_cells"]
        tier = ("top 25%" if pct >= 75 else "middle 50%" if pct >= 25 else "bottom 25%")
        verdict = "consistent" if pct >= 50 else "lower than expected -- investigate"
        print(f"  Spot-check: Barcelona station cell is in {tier} for source proxy")
        print(f"  Directional verdict: proxy is {verdict}")
        print(f"  (proxy ranks station area at {pct:.0f}th pct of all 400m cells)")
    print("\n  CALIBRATION STATUS: NOT FEASIBLE (n=1 in-city station)")
    print("  Annual totals needed -- contact: aerobiologia@uab.cat")

    out = {
        "method": "XAC station-to-cell spot-check",
        "scope": "n=1 in-city station; directional check only, not a calibration",
        "calibration_status": (
            "NOT FEASIBLE with current data. Annual pollen totals "
            "(grains x day / m3 per year) are not accessible via the public XAC API, "
            "which only exposes 7-day forecasts on a 0-4 ordinal scale. "
            "Contact aerobiologia@uab.cat for the historical Platanus series."
        ),
        "data_source": "XAC API https://aerobiologia.cat/api/v0/forecast/[station]/en/xml",
        "stations": results,
    }
    (OUTDIR / "pollen_station_validation.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8")
    _write_md(out, results, in_city)
    print(f"\n-> outputs/phase-6/pollen_station_validation.json")
    print(f"-> outputs/phase-6/pollen_station_validation.md")


def _write_md(out: dict, results: list, in_city: list) -> None:
    lines = [
        "# XAC Pollen Station Spot-Check",
        "",
        f"**Scope:** {out['scope']}",
        "",
        f"**Calibration status:** {out['calibration_status']}",
        "",
        "---",
        "",
    ]

    for r in in_city:
        api = r.get("api_forecast", {})
        lvl = api.get("level")
        api_str = (f"Platanus level = {lvl}/4 (0=null, 4=max)"
                   if api.get("ok") and lvl is not None
                   else "API fetch failed or level unparseable")
        pct = r["source_percentile_all_cells"]
        tier = "top 25%" if pct >= 75 else "middle 50%" if pct >= 25 else "bottom 25%"
        lines += [
            f"## {r['station']} (in-grid)",
            "",
            "| Field | Value |",
            "|---|---|",
            f"| Cell | `{r['cell_id']}` |",
            f"| District | {r['district']} |",
            f"| Plane trees | {r['plane_density']} |",
            f"| Maturity | {r['maturity']:.2f} |",
            f"| source_raw | {r['source_raw']:.1f} |",
            f"| source_std | {r['source_std']:.3f} |",
            f"| **Percentile (all cells)** | **{pct:.0f}th -- {tier}** |",
            f"| Percentile (cells with planes) | {r['source_percentile_nonzero_cells']:.0f}th |",
            f"| Live API (XAC) | {api_str} |",
            "",
        ]

    outside = [r for r in results if not r.get("in_grid")]
    if outside:
        lines += ["## Stations outside Barcelona city grid", ""]
        for r in outside:
            lines.append(f"- **{r['station']}** ({r['lat']}, {r['lon']}): {r['notes']}")
        lines.append("")

    lines += [
        "---",
        "",
        "## Honest limitations",
        "",
        "- **n=1 in-city station.** Spatial calibration across cells requires >= ~10 stations.",
        "- The percentile check answers only: *is the station area notable per our proxy?*",
        "  It cannot confirm whether the proxy rank order is correct city-wide.",
        "- The XAC public API exposes 7-day forecast levels (0-4 ordinal) only.",
        "  Annual pollen season integrals (grains x day / m3) are not accessible.",
        "- **To close model-card limitation #1** (not validated against measured pollen),",
        "  request the historical Platanus series from aerobiologia@uab.cat and populate",
        "  an `annual_pollen_index` column in `data/pollen_stations.csv`, then re-run.",
        "",
        "## What full calibration would require",
        "",
        "1. Annual pollen season integral for Barcelona station (5+ years) from XAC archives.",
        "2. Tree-inventory snapshots for the same years to match inter-annual proxy changes.",
        "3. At least 2-3 additional in-city stations for any spatial regression across cells.",
    ]

    out_path = ROOT / "outputs" / "phase-6" / "pollen_station_validation.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
