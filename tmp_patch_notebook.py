"""Patch cell d8e9f0a1 of 05-visualisation.ipynb to fix the WGS84-buffer-in-degrees bug.

Root cause:
    projected_hulls_top["geometry"] = projected_hulls_top["geometry"].apply(
        lambda g: g.buffer(500) if g is not None else g
    )
This buffers WGS84 lat/lon geometries by 500 *degrees* (~55,000 km), which covers
the entire planet — Folium renders solid green over the whole map view.

Fix: project to EPSG:25831 (UTM31N, ETRS89, metric, correct for Barcelona) before
buffering by 500 metres, then project back to EPSG:4326 for Folium.
"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

NB_PATH = r'C:/Users/Rafik/Documents/GitHub/group4-data-for-all/notebooks/05-visualisation.ipynb'

OLD_SNIPPET = '''projected_hulls_top = islands_hulls_spread.copy()
projected_hulls_top["geometry"] = projected_hulls_top["geometry"].apply(
    lambda g: g.buffer(500) if g is not None else g
)'''

NEW_SNIPPET = '''# Buffer in a metric CRS (UTM 31N / ETRS89, correct for Barcelona),
# NOT directly on WGS84 — `.buffer(500)` on lat/lon would mean 500 *degrees*
# (~55,000 km), which is why earlier versions of this map rendered solid green
# over the entire viewport. The fix is the standard reproject -> buffer -> reproject.
_BUFFER_WORK_CRS = "EPSG:25831"
_BUFFER_DISPLAY_CRS = "EPSG:4326"
_islands_metric = islands_hulls_spread.to_crs(_BUFFER_WORK_CRS)
_islands_metric["geometry"] = _islands_metric.geometry.buffer(500)  # 500 metres
projected_hulls_top = _islands_metric.to_crs(_BUFFER_DISPLAY_CRS)'''

with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)

target_idx = None
for i, cell in enumerate(nb['cells']):
    if cell.get('id') == 'd8e9f0a1':
        target_idx = i
        break

if target_idx is None:
    print("ERROR: cell d8e9f0a1 not found")
    sys.exit(1)

src_list = nb['cells'][target_idx]['source']
src_text = ''.join(src_list) if isinstance(src_list, list) else src_list

if OLD_SNIPPET not in src_text:
    print("ERROR: target snippet not found in cell d8e9f0a1")
    print("--- cell source ---")
    print(src_text)
    sys.exit(2)

new_src_text = src_text.replace(OLD_SNIPPET, NEW_SNIPPET, 1)

# Preserve newline-per-element list format that nbformat expects
new_lines = new_src_text.splitlines(keepends=True)
nb['cells'][target_idx]['source'] = new_lines

# clear stale outputs/execution_count for this cell so it's clear it needs re-running
if 'outputs' in nb['cells'][target_idx]:
    nb['cells'][target_idx]['outputs'] = []
if 'execution_count' in nb['cells'][target_idx]:
    nb['cells'][target_idx]['execution_count'] = None

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
    f.write('\n')

print(f"Patched cell {target_idx} (id=d8e9f0a1)")
print("Replaced WGS84-buffer-in-degrees with reproject-to-UTM31N -> buffer 500 m -> reproject-to-WGS84")
