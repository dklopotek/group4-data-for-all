"""Inspect every Folium geoJson addData block in network_spread.html."""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

html_path = r'C:/Users/Rafik/Documents/GitHub/group4-data-for-all/outputs/network_spread.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Folium pattern:
#   var geo_json_XYZ = L.geoJson(null, { onEachFeature: ... });
#   function geo_json_XYZ_add (data) { geo_json_XYZ.addData(data); }
#   geo_json_XYZ_add({...FeatureCollection...});
# So search for: geo_json_<hex>_add(\s*\{...\});

pat = re.compile(r'(geo_json_[a-f0-9]+)_add\(\s*\{', re.MULTILINE)

blocks = []
for match in pat.finditer(html):
    name = match.group(1)
    start = match.end() - 1  # the '{'
    depth = 0
    i = start
    in_string = False
    escape = False
    while i < len(html):
        c = html[i]
        if escape:
            escape = False
        elif c == "\\":
            escape = True
        elif c == '"':
            in_string = not in_string
        elif not in_string:
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    blocks.append((name, start, i + 1, html[start:i + 1]))
                    break
        i += 1

print(f"Found {len(blocks)} geo_json_*_add({{...}}) blocks\n")

for idx, (name, s, e, blob) in enumerate(blocks):
    try:
        fc = json.loads(blob)
    except Exception as ex:
        print(f"Block {idx} {name} parse fail: {ex}")
        continue
    feats = fc.get('features', [])
    lons, lats = [], []

    def walk(coords):
        if isinstance(coords, list):
            if coords and isinstance(coords[0], (int, float)) and len(coords) >= 2:
                lons.append(coords[0]); lats.append(coords[1])
            else:
                for c in coords:
                    walk(c)

    for f in feats:
        g = f.get('geometry') or {}
        walk(g.get('coordinates', []))

    # find which feature_group it gets added to
    after = html[e:e + 3000]
    fg_match = re.search(r'\.addTo\((feature_group_[a-f0-9]+)\)', after)
    fg_name = fg_match.group(1) if fg_match else "?"

    # find styling: look for the corresponding _styler function before block s
    pre = html[max(0, s - 3500):s]
    fill_match = re.search(r'"fillColor":\s*"(#[0-9A-Fa-f]+)"', pre)
    fill_color = fill_match.group(1) if fill_match else "?"

    # find display label in overlays dict near end
    # (do once outside the loop)

    print(f"=== Block {idx}: {name} -> {fg_name}  fillColor={fill_color} ===")
    print(f"  features: {len(feats)}")
    if lons:
        print(f"  lon range: {min(lons):.4f} .. {max(lons):.4f}  (span={max(lons) - min(lons):.4f})")
        print(f"  lat range: {min(lats):.4f} .. {max(lats):.4f}  (span={max(lats) - min(lats):.4f})")
    if feats:
        g0 = feats[0].get('geometry') or {}
        print(f"  first geom type: {g0.get('type')}")
        p0 = feats[0].get('properties') or {}
        print(f"  first props keys: {list(p0.keys())}")
    print()

# overlay label mapping
fg_to_label = {}
for m in re.finditer(r'"([^"]+)"\s*:\s*(feature_group_[a-f0-9]+)\b', html):
    fg_to_label[m.group(2)] = m.group(1)
print("=== feature_group -> label ===")
for k, v in fg_to_label.items():
    print(f"  {k}  =>  {v}")
