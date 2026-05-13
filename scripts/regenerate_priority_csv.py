"""Regenerate outputs/priority_zones.csv and outputs/priority_zones.html
from the LIVE data/scored_grid.geojson.

Why this exists
---------------
The CSV at outputs/priority_zones.csv had been generated from an earlier
notebook run that pre-dated the sealed_pct raster fix and the
intervention_profile rewrite. The Geographer's review (2026-05-10) flagged
that priority_zones.csv was out of step with the live scored_grid.geojson.

This regenerator is the single source of truth for the planner-facing
CSV / HTML: it reads scored_grid.geojson, filters top15_scenario_B==True,
and writes a tight set of columns sorted by composite_B descending.

Run from repo root:
    python data/regenerate_priority_csv.py
"""

from pathlib import Path
import geopandas as gpd
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
SCORED_GRID = REPO / "data" / "scored_grid.geojson"
CSV_OUT = REPO / "outputs" / "priority_zones.csv"
HTML_OUT = REPO / "outputs" / "priority_zones.html"

COLUMNS = [
    "rank",
    "cell_id",
    "nom_districte",
    "barri_name",
    "dominant_myco_type",
    "sealed_pct",
    "lst_anomaly_celsius",
    "mean_ndvi",
    "am_blindness_flag",
    "composite_B",
    "intervention_type",
    "colonisation_uncertain",
]

# Optional columns we surface if present (added by Fix 3 in notebook 03):
PROFILE_COLS = ["intervention_profile_str"]

# Intervention-type colour palette (light, planner-friendly).
INTERVENTION_COLOURS = {
    "de-paving": "#8c5a2b",          # earth-brown
    "cooling": "#3d8bcc",            # cool-blue
    "planting": "#3fa34d",           # leaf-green
    "species-selection": "#9c5fbf",  # purple
}


def regenerate() -> pd.DataFrame:
    print(f"[regen] reading {SCORED_GRID.relative_to(REPO)}")
    g = gpd.read_file(SCORED_GRID)
    if "top15_scenario_B" not in g.columns:
        raise SystemExit("scored_grid.geojson missing top15_scenario_B column")

    top = g[g["top15_scenario_B"] == True].copy()  # noqa: E712
    if len(top) == 0:
        raise SystemExit("no rows with top15_scenario_B == True")

    top = top.sort_values("composite_B", ascending=False).reset_index(drop=True)
    top["rank"] = top.index + 1

    # Pick the subset of requested columns plus the profile string if it exists.
    have_profile = "intervention_profile_str" in top.columns
    out_cols = list(COLUMNS) + ([c for c in PROFILE_COLS if c in top.columns])
    out = top[out_cols].copy()

    # Tidy numerics
    out["sealed_pct"] = out["sealed_pct"].round(3)
    out["lst_anomaly_celsius"] = out["lst_anomaly_celsius"].round(3)
    out["mean_ndvi"] = out["mean_ndvi"].round(4)
    out["composite_B"] = out["composite_B"].round(4)

    # CSV
    out.to_csv(CSV_OUT, index=False, encoding="utf-8")
    print(f"[regen] wrote {CSV_OUT.relative_to(REPO)} rows={len(out)} cols={len(out_cols)}")

    # HTML (styled)
    write_html(out, have_profile=have_profile)
    return out


def write_html(df: pd.DataFrame, have_profile: bool) -> None:
    rows_html = []
    for _, r in df.iterrows():
        colour = INTERVENTION_COLOURS.get(r["intervention_type"], "#666")
        profile_cell = ""
        if have_profile:
            profile_cell = f"<td class='profile'>{r.get('intervention_profile_str', '')}</td>"
        am_flag = "Y" if bool(r["am_blindness_flag"]) else ""
        col_flag = "Y" if bool(r["colonisation_uncertain"]) else ""
        rows_html.append(
            f"""<tr>
  <td class='rank'>{int(r['rank'])}</td>
  <td class='cell'>{r['cell_id']}</td>
  <td>{r['nom_districte']}</td>
  <td>{r['barri_name']}</td>
  <td>{r['dominant_myco_type']}</td>
  <td class='num'>{r['sealed_pct']:.3f}</td>
  <td class='num'>{r['lst_anomaly_celsius']:+.2f}</td>
  <td class='num'>{r['mean_ndvi']:+.4f}</td>
  <td class='flag'>{am_flag}</td>
  <td class='num composite'>{r['composite_B']:.3f}</td>
  <td><span class='pill' style='background:{colour}'>{r['intervention_type']}</span></td>
  {profile_cell}
  <td class='flag'>{col_flag}</td>
</tr>"""
        )

    profile_th = "<th>Profile</th>" if have_profile else ""

    html = f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<title>Priority Zones — Mycorrhizal Barcelona (Scenario B)</title>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         margin: 32px; color: #1a1a1a; background: #fafafa; }}
  h1 {{ font-size: 20px; margin-bottom: 4px; }}
  .subtitle {{ color: #555; font-size: 13px; margin-bottom: 20px; }}
  .caveat {{ background: #fff8e1; border-left: 4px solid #f4b400; padding: 10px 14px;
            font-size: 12px; color: #5c4500; margin-bottom: 18px; max-width: 920px; }}
  table {{ border-collapse: collapse; font-size: 13px; background: #fff;
           box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
  th, td {{ border-bottom: 1px solid #eee; padding: 7px 10px; text-align: left;
            vertical-align: middle; }}
  th {{ background: #f1f3f5; font-weight: 600; font-size: 12px; text-transform: uppercase;
        letter-spacing: 0.04em; color: #444; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  td.rank {{ font-weight: 600; color: #222; }}
  td.cell {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
             font-size: 12px; color: #444; }}
  td.composite {{ font-weight: 600; }}
  td.flag {{ text-align: center; color: #c0392b; font-weight: 600; }}
  td.profile {{ font-size: 12px; color: #333; max-width: 260px; }}
  .pill {{ display: inline-block; padding: 3px 10px; border-radius: 12px;
           color: white; font-size: 11px; font-weight: 600;
           letter-spacing: 0.02em; }}
  .legend {{ font-size: 12px; color: #555; margin-top: 14px; }}
  .legend .pill {{ margin-right: 6px; }}
</style>
</head>
<body>
<h1>Priority Zones — Mycorrhizal Barcelona (Scenario B)</h1>
<div class='subtitle'>Top {len(df)} barrier cells, sorted by composite_B.
Regenerated from <code>data/scored_grid.geojson</code> on demand.</div>

<div class='caveat'>
<strong>Read with care.</strong>
Composite_B is a sealed-surface-weighted composite (0.55 sealed · 0.20 LST · 0.20 NDVI · 0.05 mismatch).
The single <em>intervention_type</em> column is the dominant lever for each cell, but most top-15 cells
score high on multiple axes simultaneously — see the <em>Profile</em> column where available, and the
Geographer's review for a full compound interpretation.
</div>

<table>
<thead>
<tr>
  <th>Rank</th><th>Cell</th><th>District</th><th>Barri</th><th>Dom. Myco</th>
  <th>Sealed</th><th>LST Δ°C</th><th>NDVI</th><th>AM-blind</th>
  <th>composite_B</th><th>Intervention</th>{profile_th}<th>Colon. uncertain</th>
</tr>
</thead>
<tbody>
{chr(10).join(rows_html)}
</tbody>
</table>

<div class='legend'>
  Intervention legend:
  <span class='pill' style='background:#8c5a2b'>de-paving</span>
  <span class='pill' style='background:#3d8bcc'>cooling</span>
  <span class='pill' style='background:#3fa34d'>planting</span>
  <span class='pill' style='background:#9c5fbf'>species-selection</span>
</div>
</body>
</html>
"""
    HTML_OUT.write_text(html, encoding="utf-8")
    print(f"[regen] wrote {HTML_OUT.relative_to(REPO)}")


if __name__ == "__main__":
    df = regenerate()
    # Sanity check echoed to stdout.
    print("\n[sanity] districts represented:",
          sorted(df["nom_districte"].unique().tolist()))
    print("[sanity] intervention_type counts:",
          df["intervention_type"].value_counts().to_dict())
    print("[sanity] composite_B range:",
          f"{df['composite_B'].min():.3f} .. {df['composite_B'].max():.3f}")
