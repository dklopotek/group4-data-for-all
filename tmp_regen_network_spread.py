"""Standalone regenerator for outputs/network_spread.html with the WGS84-buffer bug fixed.

Mirrors notebook 05 cell d8e9f0a1 (which we already patched), but runs as a flat
script so cell-ordering issues in the notebook don't block headless execution.
"""
import io, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pandas as pd
import geopandas as gpd
import folium
import pyproj
from shapely.geometry import Point as SPoint
from shapely.ops import transform as shapely_transform

REPO = Path(r'C:/Users/Rafik/Documents/GitHub/group4-data-for-all')
DATA = REPO / 'data'
OUT_DIR = REPO / 'outputs'

BCN_LAT, BCN_LON = 41.3879, 2.1699

SOURCE_PATCHES = {
    "Collserola":   (41.4400, 2.1100),
    "Ciutadella":   (41.3880, 2.1880),
    "Montjuïc":     (41.3635, 2.1580),
}


def _buffer_wgs84_to_metres(geom, metres, from_epsg=4326, to_epsg=3857):
    project_fwd = pyproj.Transformer.from_crs(from_epsg, to_epsg, always_xy=True).transform
    project_bck = pyproj.Transformer.from_crs(to_epsg, from_epsg, always_xy=True).transform
    return shapely_transform(project_bck, shapely_transform(project_fwd, geom).buffer(metres))


# ── Load inputs ──────────────────────────────────────────────────────────────
network_islands = gpd.read_file(DATA / 'network_islands.geojson')
scored_grid = gpd.read_file(DATA / 'scored_grid.geojson')
bcn_districts = gpd.read_file(DATA / 'bcn-districts.geojson')

bridge_csv = DATA / 'bridge_scores.csv'
bridge_df = pd.read_csv(bridge_csv) if bridge_csv.exists() else pd.DataFrame()

# Build top15 with bridge_score merged in
if 'bridge_score' in bridge_df.columns and 'cell_id' in bridge_df.columns:
    score_col = 'composite_B' if 'composite_B' in scored_grid.columns else 'composite_A'
    top15_ids = bridge_df.nlargest(15, 'bridge_score')['cell_id'].tolist() if 'bridge_score' in bridge_df.columns else []
    top15 = scored_grid[scored_grid['cell_id'].isin(top15_ids)].merge(
        bridge_df[['cell_id', 'bridge_score']], on='cell_id', how='left'
    )
else:
    score_col = next((c for c in ['composite_B', 'composite_A', 'composite'] if c in scored_grid.columns), None)
    top15 = scored_grid.nlargest(15, score_col).copy() if score_col else scored_grid.head(15).copy()
    if 'bridge_score' not in top15.columns:
        top15['bridge_score'] = pd.NA

print(f"Loaded: {len(network_islands)} islands, {len(top15)} top-15 cells")

# Ensure GeoDataFrames are WGS84 (network_islands.geojson appears to carry UTM
# centroids in properties but geometry is WGS84 — confirm and force the CRS)
if network_islands.crs is None:
    network_islands.set_crs("EPSG:4326", inplace=True)
elif network_islands.crs.to_epsg() != 4326:
    network_islands = network_islands.to_crs("EPSG:4326")

if top15.crs is None:
    top15.set_crs("EPSG:4326", inplace=True)
elif top15.crs.to_epsg() != 4326:
    top15 = top15.to_crs("EPSG:4326")

# ── Cell c7d8e9f0 logic: identify top-3 bridge + intervention buffers ────────
if 'bridge_score' in top15.columns:
    top15['bridge_score'] = pd.to_numeric(top15['bridge_score'], errors='coerce')
    top3_bridge = top15.dropna(subset=['bridge_score']).nlargest(3, 'bridge_score')
    if len(top3_bridge) < 3:
        top3_bridge = top15.head(3)
else:
    top3_bridge = top15.head(3)

SPREAD_BUFFER_M = 500

intervention_buffers = []
for _, row in top3_bridge.iterrows():
    buf = _buffer_wgs84_to_metres(row.geometry.centroid, SPREAD_BUFFER_M)
    intervention_buffers.append({'geometry': buf, 'cell_id': row['cell_id']})

int_gdf = gpd.GeoDataFrame(intervention_buffers, crs="EPSG:4326") if intervention_buffers else \
          gpd.GeoDataFrame(columns=['geometry', 'cell_id'], crs="EPSG:4326")

print(f"Top-3 bridge zones: {top3_bridge['cell_id'].tolist()}")

# ── Cell d8e9f0a1 logic (PATCHED): top-20 islands + projected hulls (metric buffer) ──
if 'node_count' in network_islands.columns:
    top_islands_spread = network_islands.nlargest(20, 'node_count').copy()
else:
    top_islands_spread = network_islands.head(20).copy()

islands_hulls_spread = top_islands_spread.copy()
islands_hulls_spread['geometry'] = islands_hulls_spread.geometry.convex_hull.simplify(tolerance=10)

# FIX: project to metric CRS (UTM 31N / ETRS89) -> buffer 500 m -> back to WGS84.
# Earlier broken code: islands_hulls_spread.geometry.apply(lambda g: g.buffer(500))
# treated WGS84 degrees as metres, producing ~55,000 km buffers that filled the map.
_BUFFER_WORK_CRS = "EPSG:25831"
_BUFFER_DISPLAY_CRS = "EPSG:4326"
_islands_metric = islands_hulls_spread.to_crs(_BUFFER_WORK_CRS)
_islands_metric['geometry'] = _islands_metric.geometry.buffer(500)
projected_hulls_top = _islands_metric.to_crs(_BUFFER_DISPLAY_CRS)

print("projected_hulls_top bounds:", projected_hulls_top.total_bounds)
print("(expected lon ~2.1-2.2, lat ~41.3-41.5)")

# ── Build m2 ─────────────────────────────────────────────────────────────────
m2 = folium.Map(location=[BCN_LAT, BCN_LON], zoom_start=12,
                tiles="CartoDB positron", control_scale=True)

title2_html = """
<div style="position:fixed; top:10px; left:50%; transform:translateX(-50%);
     z-index:9999; background:rgba(255,255,255,0.92);
     border:1px solid #aaa; border-radius:5px;
     padding:8px 16px; font-family:Arial, sans-serif;
     font-size:13px; font-weight:bold; text-align:center;
     max-width:620px; box-shadow:2px 2px 6px rgba(0,0,0,0.2);">
  Mycorrhizal Network Spread Projection — Baseline vs. 2030 Top-3 Bridge Scenario
  <br><span style='font-weight:normal; font-size:10px; color:#c0392b;'>
    Spread buffer is illustrative (500 m heuristic). Not a calibrated dispersal model.
    Showing top 20 largest islands.
  </span>
</div>
"""
m2.get_root().html.add_child(folium.Element(title2_html))

# Baseline
baseline_layer = folium.FeatureGroup(name="Baseline: current network islands (top 20)", show=True)
tooltip_fields = [c for c in ['island_id', 'node_count'] if c in islands_hulls_spread.columns]
folium.GeoJson(
    islands_hulls_spread.to_json(),
    style_function=lambda _: {
        "fillColor": "#8E44AD", "color": "#6C3483",
        "weight": 2.0, "fillOpacity": 0.40,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=tooltip_fields,
        aliases=["Island #", "Trees"][:len(tooltip_fields)],
        localize=True,
    ) if tooltip_fields else None,
).add_to(baseline_layer)
baseline_layer.add_to(m2)

# Spread
spread_layer = folium.FeatureGroup(
    name="2030 projected spread (top-3 bridge interventions)", show=True
)
folium.GeoJson(
    projected_hulls_top.to_json(),
    style_function=lambda _: {
        "fillColor": "#27AE60", "color": "#1E8449",
        "weight": 1.5, "fillOpacity": 0.20, "dashArray": "6 4",
    },
).add_to(spread_layer)

if len(int_gdf):
    folium.GeoJson(
        int_gdf.to_json(),
        style_function=lambda _: {
            "fillColor": "#27AE60", "color": "#27AE60",
            "weight": 1.0, "fillOpacity": 0.15, "dashArray": "3 3",
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["cell_id"] if "cell_id" in int_gdf.columns else [],
            aliases=["Intervention cell:"] if "cell_id" in int_gdf.columns else [],
            localize=True,
        ),
    ).add_to(spread_layer)

spread_layer.add_to(m2)

# Source patches
source_layer = folium.FeatureGroup(name="Source patches", show=True)
for patch_name, (lat, lon) in SOURCE_PATCHES.items():
    folium.Marker(
        location=[lat, lon],
        icon=folium.Icon(color="green", icon="leaf", prefix="fa"),
        popup=folium.Popup(f"<b>{patch_name}</b><br>Peri-urban source patch", max_width=200),
        tooltip=f"{patch_name} (source patch)",
    ).add_to(source_layer)
source_layer.add_to(m2)

# District boundaries
dist_layer2 = folium.FeatureGroup(name="District boundaries", show=False)
folium.GeoJson(
    bcn_districts.to_json(),
    style_function=lambda _: {
        "fillColor": "transparent", "color": "#7F8C8D",
        "weight": 1.5, "fillOpacity": 0.0, "dashArray": "4 4",
    },
).add_to(dist_layer2)
dist_layer2.add_to(m2)

# Legend
spread_legend_html = """
<div style="position:fixed; bottom:30px; right:15px; z-index:9999;
     background:rgba(255,255,255,0.93); border:1px solid #aaa;
     border-radius:6px; padding:12px 16px;
     font-family:Arial, sans-serif; font-size:12px;
     box-shadow:2px 2px 6px rgba(0,0,0,0.2); min-width:200px;">
  <div style='font-weight:bold; margin-bottom:8px;'>Network spread layers</div>
  <div style='display:flex; align-items:center; margin-bottom:5px;'>
    <div style='width:14px; height:14px; background:#8E44AD; opacity:0.8;
                border-radius:50%; margin-right:8px;'></div>
    <span>Current network islands (top 20)</span></div>
  <div style='display:flex; align-items:center; margin-bottom:5px;'>
    <div style='width:14px; height:14px; background:#27AE60; opacity:0.6;
                border-radius:50%; margin-right:8px;'></div>
    <span>2030 projected spread</span></div>
  <div style='display:flex; align-items:center; margin-bottom:5px;'>
    <div style='width:14px; height:14px; background:#27AE60; opacity:0.3;
                border-radius:3px; margin-right:8px;'></div>
    <span>Intervention zone buffers</span></div>
  <div style='display:flex; align-items:center;'>
    <span style='margin-right:8px; font-size:16px;'>&#x1F343;</span>
    <span>Source patches</span></div>
  <hr style='margin:8px 0; border:none; border-top:1px solid #eee;'>
  <span style='color:#999; font-size:10px;'>Buffer = 500 m heuristic. Not calibrated.</span>
</div>
"""
m2.get_root().html.add_child(folium.Element(spread_legend_html))

folium.LayerControl(position="topleft", collapsed=False).add_to(m2)

out_spread = OUT_DIR / 'network_spread.html'
m2.save(str(out_spread))
print(f"Saved: {out_spread} ({out_spread.stat().st_size:,} bytes)")
