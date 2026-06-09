"""Build the Phase-6 interactive deployment map (self-contained HTML).

Bakes simplified GeoJSON INLINE into one HTML file (works from file:// -- no fetch/CORS),
Leaflet from CDN, dark CartoDB basemap. Layers:
  - Census sections coloured by priority (default) -- the operational grain
  - 400 m cells coloured by priority (toggle) -- demonstrates MAUP live
  - Mature plane points for the top sections (toggle) -- the action layer
Click a section -> rank, planes, mature, population, priority + top streets to cut.

NOTE: the user explicitly chose to build a UI ("go full on"), overriding the course's
no-frontend constraint. This is an exploration/presentation artifact, not a hosted service.

Run:  python scripts/build_deploy_map.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "outputs" / "phase-6" / "section_priority.parquet"
CELLS = ROOT / "data" / "processed" / "allergen_layers.parquet"
ACTIONS = ROOT / "outputs" / "phase-6" / "street_removal_actions.csv"
OUT = ROOT / "outputs" / "phase-6" / "maps" / "deployment_map.html"
CRS = "EPSG:25831"


def minmax(x):
    x = np.asarray(x, float)
    lo, hi = np.nanmin(x), np.nanmax(x)
    return np.zeros_like(x) if hi - lo == 0 else (x - lo) / (hi - lo)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    # --- sections ---
    sec = gpd.read_parquet(SEC)
    if sec.crs is None:
        sec = sec.set_crs(CRS)
    sec = sec.sort_values("priority", ascending=False).reset_index(drop=True)
    sec["rank"] = range(1, len(sec) + 1)

    # top streets per section from the worklist
    streets = {}
    if ACTIONS.exists():
        a = pd.read_csv(ACTIONS)
        for key, g in a.groupby("section_key"):
            g = g.sort_values("n_mature", ascending=False).head(5)
            streets[str(key)] = [
                {"s": r.street, "m": int(r.n_mature), "r": int(r.suggested_remove)}
                for r in g.itertuples()
            ]

    sec_w = sec.copy()
    sec_w["geometry"] = sec_w.geometry.simplify(15)        # ~15 m tolerance, projected
    sec_w = sec_w.to_crs("EPSG:4326")
    sec_feats = []
    for r in sec_w.itertuples():
        key = str(r.key)
        sec_feats.append({
            "type": "Feature",
            "geometry": json.loads(gpd.GeoSeries([r.geometry]).to_json())["features"][0]["geometry"],
            "properties": {
                "rank": int(r.rank), "key": key, "district": r.district_lbl,
                "planes": int(r.plane_count), "mature": int(r.mature_count),
                "pop": int(round(r.exposure_pop)),
                "pri": round(float(r.priority_std), 4),
                "streets": streets.get(key, []),
            },
        })
    sec_gj = {"type": "FeatureCollection", "features": sec_feats}

    # --- 400 m cells (MAUP toggle) ---
    cells = gpd.read_parquet(CELLS)
    if cells.crs is None:
        cells = cells.set_crs(CRS)
    cell_pri = cells["source_std"].to_numpy(float) * cells["exposure_std"].to_numpy(float)
    cells = cells.assign(cell_pri=minmax(cell_pri))
    cells_w = cells[["cell_id", "district", "n_platanus", "cell_pri", "geometry"]].copy()
    cells_w["geometry"] = cells_w.geometry.simplify(15)
    cells_w = cells_w.to_crs("EPSG:4326")
    cell_feats = []
    for r in cells_w.itertuples():
        cell_feats.append({
            "type": "Feature",
            "geometry": json.loads(gpd.GeoSeries([r.geometry]).to_json())["features"][0]["geometry"],
            "properties": {"cell": r.cell_id, "district": r.district,
                           "planes": int(r.n_platanus), "pri": round(float(r.cell_pri), 4)},
        })
    cells_gj = {"type": "FeatureCollection", "features": cell_feats}

    # --- mature plane points for the top 15 sections (action layer) ---
    pts_gj = {"type": "FeatureCollection", "features": []}
    pgeo = ROOT / "outputs" / "phase-6" / "street_removal_points.geojson"
    if pgeo.exists():
        pts = gpd.read_file(pgeo)
        top15 = set(sec.head(15)["key"].astype(str))
        pts = pts[pts["section_key"].astype(str).isin(top15) & pts["is_mature"]]
        for r in pts.itertuples():
            pts_gj["features"].append({
                "type": "Feature",
                "geometry": {"type": "Point",
                             "coordinates": [r.geometry.x, r.geometry.y]},
                "properties": {"street": r.street, "section": r.section_key},
            })

    html = _template(sec_gj, cells_gj, pts_gj, n_sec=len(sec),
                     n_pts=len(pts_gj["features"]))
    OUT.write_text(html, encoding="utf-8")
    print("MAP built ->", OUT)
    print(f"  sections {len(sec_feats)}  cells {len(cell_feats)}  mature-points {len(pts_gj['features'])}")
    print(f"  file size: {OUT.stat().st_size/1e6:.2f} MB")


def _template(sec_gj, cells_gj, pts_gj, n_sec, n_pts):
    return """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Barcelona Plane-Tree Removal Priority -- Deployment Map</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<style>
 :root{--ink:#e6edf3;--mut:#8b949e;--pan:#11161f;--line:#2b3340;--teal:#39c5cf}
 html,body{margin:0;height:100%;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#0d1117}
 #map{position:absolute;inset:0}
 .panel{position:absolute;z-index:1000;background:rgba(17,22,31,.94);color:var(--ink);
   border:1px solid var(--line);border-radius:12px;padding:14px 16px;backdrop-filter:blur(6px)}
 #title{top:14px;left:14px;max-width:340px}
 #title h1{font-size:1.05rem;margin:0 0 .3rem} #title p{font-size:.82rem;color:var(--mut);margin:.25rem 0;line-height:1.4}
 #ctrl{top:14px;right:14px;font-size:.85rem}
 #ctrl label{display:block;padding:.28rem 0;cursor:pointer;user-select:none}
 #ctrl input{vertical-align:-2px;margin-right:.5rem}
 #legend{bottom:14px;left:14px;font-size:.78rem}
 .bar{height:11px;width:200px;border-radius:3px;margin:.3rem 0;
   background:linear-gradient(90deg,#2c2a1e,#7a5b1d,#c9821f,#ef6a2b,#f02d2d)}
 .lrow{display:flex;justify-content:space-between;color:var(--mut)}
 .maup{bottom:14px;right:14px;max-width:300px;font-size:.8rem;color:var(--mut);line-height:1.45;display:none}
 .maup b{color:var(--teal)}
 .lp-pop{font-size:.85rem} .lp-pop h3{margin:.1rem 0 .35rem;font-size:1rem}
 .lp-pop table{border-collapse:collapse;margin:.2rem 0} .lp-pop td{padding:1px 8px 1px 0}
 .lp-pop .k{color:#8b949e} .st{margin-top:.4rem;border-top:1px dashed #2b3340;padding-top:.3rem}
 .st div{display:flex;justify-content:space-between;gap:10px;padding:1px 0}
 .leaflet-popup-content-wrapper{background:#11161f;color:#e6edf3;border:1px solid #2b3340}
 .leaflet-popup-tip{background:#11161f}
 .pin{font-size:.7rem;color:var(--mut)}
</style></head><body>
<div id="map"></div>
<div id="title" class="panel">
 <h1>Where to cut plane trees first</h1>
 <p>Census sections of Barcelona scored by <b style="color:#ef6a2b">pollen-allergen priority</b>
    = mature plane trees x residents. Brighter = higher priority. Click a section for its
    streets and how many mature planes to remove.</p>
 <p class="pin">__NSEC__ sections &middot; allergen priority &middot; Group 4 (deployment / Phase 6)</p>
</div>
<div id="ctrl" class="panel">
 <label><input type="radio" name="lyr" value="sec" checked> Census sections (operational)</label>
 <label><input type="radio" name="lyr" value="cell"> 400 m cells (shows MAUP)</label>
 <label style="margin-top:.4rem;border-top:1px dashed #2b3340;padding-top:.4rem">
   <input type="checkbox" id="pts"> Mature plane points (top 15)</label>
</div>
<div id="legend" class="panel">
 <div>Priority (normalised 0&ndash;1)</div><div class="bar"></div>
 <div class="lrow"><span>low</span><span>high</span></div>
</div>
<div id="maup" class="panel maup">
 <b>MAUP, live.</b> Same method, different zoom = different answer. At 400&nbsp;m the population
 re-orders the top; at section grain a few park sections (Montjuic) with huge plane clusters
 dominate, so people stop mattering at the very top. Both views shipped, caveat documented.
</div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const SEC=__SEC__, CELLS=__CELLS__, PTS=__PTS__;
const map=L.map('map',{zoomControl:true}).setView([41.40,2.17],12);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
 {attribution:'&copy; OpenStreetMap, &copy; CARTO',subdomains:'abcd',maxZoom:19}).addTo(map);

function ramp(t){ // 0..1 -> warm sequential
 t=Math.max(0,Math.min(1,t));
 const stops=[[44,42,30],[122,91,29],[201,130,31],[239,106,43],[240,45,45]];
 const x=t*(stops.length-1), i=Math.floor(x), f=x-i, a=stops[i], b=stops[Math.min(i+1,stops.length-1)];
 return `rgb(${a.map((v,k)=>Math.round(v+(b[k]-v)*f)).join(',')})`;
}
function style(p){return {fillColor:ramp(p),weight:.5,color:'#0d1117',fillOpacity:.82};}

function secPopup(p){
 let s=`<div class="lp-pop"><h3>#${p.rank} &middot; ${p.district}</h3>
  <table>
   <tr><td class="k">section</td><td>${p.key}</td></tr>
   <tr><td class="k">plane trees</td><td>${p.planes} (${p.mature} mature)</td></tr>
   <tr><td class="k">residents</td><td>${p.pop.toLocaleString()}</td></tr>
   <tr><td class="k">priority</td><td>${p.pri}</td></tr>
  </table>`;
 if(p.streets&&p.streets.length){
  s+=`<div class="st"><b>Cut first (mature planes):</b>`;
  p.streets.forEach(x=>{s+=`<div><span>${x.s}</span><span>${x.r}/${x.m}</span></div>`;});
  s+=`<div class="pin" style="margin-top:.3rem">suggested / available mature &middot; allocation, not a street ranking</div></div>`;
 }
 return s+`</div>`;
}

const secLayer=L.geoJSON(SEC,{style:f=>style(f.properties.pri),
 onEachFeature:(f,l)=>{l.bindPopup(secPopup(f.properties));
  l.on('mouseover',()=>l.setStyle({weight:2,color:'#39c5cf'}));
  l.on('mouseout',()=>secLayer.resetStyle(l));}}).addTo(map);

const cellLayer=L.geoJSON(CELLS,{style:f=>style(f.properties.pri),
 onEachFeature:(f,l)=>l.bindPopup(
  `<div class="lp-pop"><h3>${f.properties.cell}</h3>
   <table><tr><td class="k">district</td><td>${f.properties.district}</td></tr>
   <tr><td class="k">plane trees</td><td>${f.properties.planes}</td></tr>
   <tr><td class="k">priority</td><td>${f.properties.pri}</td></tr></table></div>`)});

const ptLayer=L.geoJSON(PTS,{pointToLayer:(f,ll)=>L.circleMarker(ll,
 {radius:2.4,color:'#39c5cf',weight:0,fillOpacity:.7}).bindPopup(
  `<div class="lp-pop">mature plane<br><span class="k">${f.properties.street}</span></div>`)});

document.querySelectorAll('input[name=lyr]').forEach(r=>r.onchange=e=>{
 const v=e.target.value, maup=document.getElementById('maup');
 if(v==='sec'){map.addLayer(secLayer);map.removeLayer(cellLayer);maup.style.display='none';}
 else{map.addLayer(cellLayer);map.removeLayer(secLayer);maup.style.display='block';}
});
document.getElementById('pts').onchange=e=>{e.target.checked?map.addLayer(ptLayer):map.removeLayer(ptLayer);};
</script></body></html>""".replace("__SEC__", json.dumps(sec_gj)) \
        .replace("__CELLS__", json.dumps(cells_gj)) \
        .replace("__PTS__", json.dumps(pts_gj)) \
        .replace("__NSEC__", str(n_sec))


if __name__ == "__main__":
    main()
