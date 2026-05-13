# Fix report: `network_spread.html` green-everywhere bug

**Date:** 2026-05-10
**File:** `outputs/network_spread.html`
**Notebook cell patched:** `notebooks/05-visualisation.ipynb` cell id `d8e9f0a1`

---

## TL;DR

The "2030 projected spread" layer was rendering as solid green covering the entire
map view because the code called `geometry.buffer(500)` directly on a **WGS84
(lat/lon) GeoDataFrame**. In WGS84 the unit is **degrees**, not metres — so the
"500" produced a 500-degree buffer (~55 000 km radius) around every island.
That's larger than the planet, so every polygon trivially covered every pixel of
every map view.

The fix is the standard reproject -> buffer -> reproject pattern: project the
hulls to a metric CRS (EPSG:25831, ETRS89 / UTM 31N — correct for Barcelona),
buffer by 500 metres, project back to EPSG:4326 for Folium.

---

## Root cause

The user had two CRS-correct buffer blocks in the notebook (cell `c7d8e9f0` and
diagnostic cell `439fe984`), so it was tempting to assume the in-memory variable
`projected_hulls_top` was already correct. The user's own diagnostic confirmed
it was correct in memory. **But the cell that actually builds and saves `m2`
(cell `d8e9f0a1`) contained its own re-derivation that overwrote
`projected_hulls_top` with the broken WGS84-degree buffer immediately before
`folium.GeoJson(projected_hulls_top.to_json(), ...)`**:

```python
# BUGGY block inside cell d8e9f0a1, runs immediately before m2.save()
islands_hulls_spread = top_islands_spread.copy()
islands_hulls_spread["geometry"] = islands_hulls_spread.geometry.convex_hull.simplify(tolerance=10)

projected_hulls_top = islands_hulls_spread.copy()
projected_hulls_top["geometry"] = projected_hulls_top["geometry"].apply(
    lambda g: g.buffer(500) if g is not None else g   # <-- 500 *degrees*, not metres
)
```

This is exactly the failure mode from the candidate list — option (1) in the
brief: "the notebook cell that BUILDS m2 doesn't use the corrected
`projected_hulls_top` — maybe it re-defines it internally before adding to the
map." That's what was happening.

Why the upstream and diagnostic CRS-correct blocks didn't help:

- Cell `c7d8e9f0` produces a correct `projected_hulls_top` but cell `d8e9f0a1`
  re-derives it from `islands_hulls_spread` (which is itself re-derived inside
  `d8e9f0a1`).
- Diagnostic cell `439fe984` runs **after** `m2.save()`. It re-fixes the
  in-memory variable but doesn't re-save the HTML. Hence the user observed
  "variables look correct, but the HTML on disk still shows green everywhere."

---

## Evidence from the HTML on disk

Folium emits each GeoJson layer with a `geo_json_<hex>.addData({...})` call.
Walking braces over the on-disk HTML to recover the four FeatureCollection
literals (script: `tmp_inspect_html.py`):

### Before fix (HTML built at 22:52)

```
Block 0 (Baseline current islands, fill #8E44AD): 20 features
  lon 2.1223 .. 2.2141  lat 41.3586 .. 41.4433        OK — points around Barcelona

Block 1 (2030 projected spread, fill #27AE60): 20 features
  lon -497.8777 .. 502.2141  (span 1000.09°)          BUG — 500° buffer
  lat -458.6414 .. 541.4433  (span 1000.08°)          BUG — 500° buffer

Block 2 (intervention zone buffers, fill #27AE60): 3 features
  lon 2.1276 .. 2.2122  lat 41.3523 .. 41.4460        OK — used helper that reprojects

Block 3 (district boundaries): 10 features
  lon 2.0525 .. 2.2933  lat 41.3170 .. 41.4882        OK
```

The span of ~1000 degrees in Block 1 is the smoking gun. Every other layer was
fine; only `projected_hulls_top` had been buffered in lat/lon degrees.

### After fix (HTML rebuilt at 22:58)

```
Block 1 (2030 projected spread, fill #27AE60): 20 features
  lon 2.1163 .. 2.2201   (span 0.1038°)               FIXED
  lat 41.3541 .. 41.4478 (span 0.0937°)               FIXED
```

Per-feature sanity check (each buffer should be a ~500 m-radius disc, i.e.
~1000 m diameter; at lat 41.4 that's ~0.012° lon and ~0.009° lat):

```
feat  0  node_count=552  lon_span 0.0120° (~997 m)  lat_span 0.0090° (~1000 m)
feat  1  node_count=329  lon_span 0.0120° (~997 m)  lat_span 0.0090° (~1000 m)
...
feat 19  node_count= 95  lon_span 0.0120° (~997 m)  lat_span 0.0090° (~1000 m)
```

All 20 polygons are 500 m-radius discs centred on each island, exactly as the
brief asks for.

---

## The fix

Cell `d8e9f0a1` in `notebooks/05-visualisation.ipynb` was patched: the broken
WGS84 buffer was replaced with the standard reproject -> buffer -> reproject
idiom:

```python
# FIX: project to a metric CRS (UTM 31N / ETRS89, correct for Barcelona)
# *before* buffering. `.buffer(500)` on WGS84 lat/lon would mean 500 *degrees*
# (~55 000 km), which is why earlier versions of this map rendered solid green
# over the entire viewport.
_BUFFER_WORK_CRS = "EPSG:25831"
_BUFFER_DISPLAY_CRS = "EPSG:4326"
_islands_metric = islands_hulls_spread.to_crs(_BUFFER_WORK_CRS)
_islands_metric["geometry"] = _islands_metric.geometry.buffer(500)  # 500 metres
projected_hulls_top = _islands_metric.to_crs(_BUFFER_DISPLAY_CRS)
```

The HTML on disk was then regenerated and verified by parsing the FeatureCollection
JSON embedded in the file.

### Notes on the choice of CRS

- `EPSG:25831` (ETRS89 / UTM 31N) is the official metric CRS for the Iberian
  east coast including Barcelona. Buffer distances are accurate to a few cm at
  this latitude.
- The existing helper `_buffer_wgs84_to_metres` in cell `c7d8e9f0` uses
  Web Mercator (`EPSG:3857`) which is acceptable for point-buffer aesthetics in
  Barcelona (~25 % scale distortion at this latitude — a 500 m metric-CRS
  request becomes ~376 m on the ground if you don't compensate). The patched
  cell uses the more accurate UTM 31N to match the upstream cell `c7d8e9f0`
  `WORK_CRS = "EPSG:25831"` choice and the diagnostic cell `439fe984`.

### Pre-existing notebook issue (not fixed here)

Headless execution of the notebook with `nbconvert --execute` fails at cell
`c7d8e9f0` because it references `islands_hulls_spread` before `d8e9f0a1`
defines it. The user's interactive kernel evidently has these run out of order.
This is a latent bug but is outside the scope of this fix. Recommended follow-up:
move the `top_islands_spread` / `islands_hulls_spread` construction up into
cell `c7d8e9f0` (or into a cell that runs first), so cells execute cleanly top
to bottom.

---

## How to re-verify

```powershell
# Inspect every L.geoJson layer in the HTML and print bounds + feature counts
python tmp_inspect_html.py

# Standalone regenerator (avoids the notebook cell-ordering issue above)
python tmp_regen_network_spread.py
```

Expected output for the spread layer: 20 features, lon ~2.11–2.22, lat ~41.35–41.45,
with each polygon spanning ~0.012° × 0.009° (i.e. a ~500 m-radius disc).
