# Three-Fixes Report — Mycorrhizal Barcelona Pipeline

**Date:** 2026-05-10
**Branch:** session-2/data-understanding-rafik
**Author:** Developer agent
**Driving reviews:**
- `outputs/geographer-review.md` — Geographer's spatial review (CSV staleness, intervention-label incoherence)
- `outputs/spread-model-audit.md` — Independent QA verdict: spread layer is illustrative, not a projection
- `outputs/storytelling-guidance.md` — Communication framing

Three surgical fixes applied. No refactoring, no creep.

---

## Fix 1 — Regenerate `priority_zones.csv` from current `scored_grid.geojson`

### Why

The Geographer flagged that `outputs/priority_zones.csv` predated the
sealed-raster correction and disagreed with the live `data/scored_grid.geojson`.
Spot-check showed the live geojson actually clusters the top-15 in **10
districts** (not 9 as the review described) and labels all 15 cells
"de-paving" under Scenario B. The CSV needed to be regenerated from the live
source with a tighter, planner-facing schema.

### What changed

Added a single regenerator script that is now the single source of truth for
the planner-facing CSV and HTML.

| File | Before | After |
|---|---|---|
| `data/regenerate_priority_csv.py` | did not exist | 7,619 B, runnable from repo root |
| `outputs/priority_zones.csv` | 1,486 B, 15 columns including bridge_score / appears_in_all_scenarios | 1,609 B, 12-column planner schema sorted by composite_B descending |
| `outputs/priority_zones.html` | stale (older schema) | 9,147 B, styled, intervention-coloured |

### How it works

```text
python data/regenerate_priority_csv.py
[regen] reading data\scored_grid.geojson
[regen] wrote outputs\priority_zones.csv rows=15 cols=12
[regen] wrote outputs\priority_zones.html

[sanity] districts represented: ['CIUTAT VELLA', 'EIXAMPLE', 'GRACIA',
  'HORTA - GUINARDO', 'LES CORTS', 'NOU BARRIS', 'SANT ANDREU', 'SANT MARTI',
  'SANTS - MONTJUIC', 'SARRIA - SANT GERVASI']
[sanity] intervention_type counts: {'de-paving': 15}
[sanity] composite_B range: 0.747 .. 0.855
```

CSV schema written by the regenerator:

```
rank,cell_id,nom_districte,barri_name,dominant_myco_type,
sealed_pct,lst_anomaly_celsius,mean_ndvi,am_blindness_flag,
composite_B,intervention_type,colonisation_uncertain
```

If notebook 03 is re-run after Fix 3, the regenerator picks up the new
`intervention_profile_str` column automatically and appends it as a 13th
column (it is feature-gated on column presence — see the `PROFILE_COLS`
list and `have_profile` flag in the script).

### Evidence

CSV first three rows after regeneration (verified UTF-8 encoding of
district names):

```
rank,cell_id,nom_districte,barri_name,dominant_myco_type,sealed_pct,lst_anomaly_celsius,mean_ndvi,am_blindness_flag,composite_B,intervention_type,colonisation_uncertain
1,C016_011,SANTS - MONTJUIC,LA MARINA DEL PORT,AM,0.802,7.916,-0.0062,True,0.8554,de-paving,False
2,C031_035,SANT ANDREU,EL BON PASTOR,AM,0.802,6.044,0.0184,True,0.8207,de-paving,False
3,C032_032,SANT ANDREU,EL BON PASTOR,AM,0.806,5.524,0.0173,True,0.8173,de-paving,False
```

The HTML version is styled with intervention-type colour pills and a yellow
caveat banner reminding planners that composite_B is sealed-weighted and the
profile column carries the compound interpretation.

### Files touched

- `C:/Users/Rafik/Documents/GitHub/group4-data-for-all/data/regenerate_priority_csv.py` (new)
- `C:/Users/Rafik/Documents/GitHub/group4-data-for-all/outputs/priority_zones.csv` (overwritten)
- `C:/Users/Rafik/Documents/GitHub/group4-data-for-all/outputs/priority_zones.html` (overwritten)

---

## Fix 2 — Honest relabel of the spread layer

### Why

Per `outputs/spread-model-audit.md`, the green "2030 projected spread under
top-3 bridge interventions" layer in `outputs/network_spread.html` is a
static 500 m buffer around the convex hull of each of the top-20 existing
islands. It encodes no time horizon, no AM/EM differentiation, and no
intervention sensitivity. The label was a category error: an illustration
sold as a projection. Verdict was REWRITE the label or DELETE the layer.

This fix takes the REWRITE path. The geometry is unchanged (it is still a
500 m buffer — the same illustrative neighbourhood), but every label, title,
legend entry, output filename, and notebook reference is rewritten to match
what the geometry actually shows.

### What changed in notebook `05-visualisation.ipynb`

Cell `d8e9f0a1` — the spread-map builder.

**Before (title banner):**
```
Mycorrhizal Network Spread Projection — Baseline vs. 2030 Top-3 Bridge Scenario
  Spread buffer is illustrative (500 m heuristic). Not a calibrated dispersal model.
  Showing top 20 largest islands.
```

**After:**
```
Mycorrhizal Network Connectivity Neighbourhoods (top 20 islands, 500m buffer)
  Buffer = 500m heuristic. Not a calibrated dispersal model.
  Does NOT show 2030 outcomes under intervention.
```

**Before (layer name):**
```python
spread_layer = folium.FeatureGroup(
    name="2030 projected spread (top-3 bridge interventions)", show=True
)
```

**After:**
```python
spread_layer = folium.FeatureGroup(
    name="500m connectivity neighbourhood around each island", show=True
)
```

**Before (legend entry):**
```html
<span>2030 projected spread</span>
```

**After:**
```html
<span>500 m connectivity neighbourhood (illustrative)</span>
```

**Before (file output):**
```python
out_spread = OUT_DIR / "network_spread.html"
m2.save(str(out_spread))
```

**After:**
```python
out_neighbourhoods = OUT_DIR / "network_neighborhoods.html"
m2.save(str(out_neighbourhoods))

_legacy_spread = OUT_DIR / "network_spread.html"
if _legacy_spread.exists() and out_neighbourhoods.exists():
    try:
        _legacy_spread.unlink()
        print(f"Removed legacy file: {_legacy_spread}")
    except OSError as _e:
        print(f"NOTE: could not remove legacy {_legacy_spread}: {_e}")
```

### Supporting edits (to keep the notebook coherent)

Three other cells in `05-visualisation.ipynb` referenced the old filename or
title. Left un-edited they would have caused inconsistencies and a false
MISSING entry in the verification cell.

| Cell id | Type | Change |
|---|---|---|
| `a1b2c3d4` | markdown intro | Outputs table entry: `network_spread.html (2030 scenario)` -> `network_neighborhoods.html (500m buffer, illustrative)` |
| `b6c7d8e9` | markdown section | "Output 5 — Network Spread Visualisation" -> "Output 5 — Network Connectivity Neighbourhoods"; bullet rewritten to drop "2030 projected" and point at the spread-model audit |
| `f0a1b2c3` | code verification | `OUT_DIR / "network_spread.html"` -> `OUT_DIR / "network_neighborhoods.html"` in `expected_outputs` list; stale cached outputs cleared |

The stale cached outputs of `d8e9f0a1` (which printed `Saved: ...network_spread.html`) were also cleared so the next run produces clean evidence.

### What changed in notebook `04-connectivity.ipynb`

A new markdown cell (id `e2150314`) was inserted **before** the
`cell-spread-fn` cell (between `cell-source-patches` and `cell-spread-fn`).
It is a blockquote-styled DEPRECATED warning:

```markdown
> ## DEPRECATED — `simulate_spread` is not used by the v1 deliverable
>
> **Status (2026-05-10):** The `simulate_spread` function below is retained
> for reference but is **not consumed by the visualisation in notebook 05**.
> The independent spread-model audit (`outputs/spread-model-audit.md`)
> documented that:
>
> 1. The current frontier-BFS halts at season 0 on the corrected inputs...
> 2. The function accepts the NetworkX graph `G` as a parameter but
>    never reads it...
> 3. There is no AM vs EM differentiation, no cost-distance along the path...
>
> **What the v1 deliverable uses instead:** notebook 05 renders a simpler,
> honestly-labelled *500 m connectivity neighbourhood* — a static buffer
> around the convex hull of each of the top-20 existing islands. That is
> not a projection and it does not depend on this function.
>
> A scientifically defensible rewrite would (a) traverse `G` with AM/EM
> rate differentiation, (b) compute cost-distance over a rasterised
> `sealed_pct` surface, (c) compare baseline vs intervention by running
> the BFS twice and rendering the difference. None of that ships in v1.
```

Position verified at runtime:

```text
OK nb04 deprecated note at index 20, follows cell-source-patches, precedes cell-spread-fn
```

### File rename note

`outputs/network_spread.html` (259,535 B) still exists at the time of this
report because the user has not yet re-run notebook 05. The new cell will
delete the legacy file the first time it runs successfully and write
`outputs/network_neighborhoods.html` in its place. Until then, do not
distribute the old file — the labels on it are the ones this fix invalidates.

### Files touched

- `C:/Users/Rafik/Documents/GitHub/group4-data-for-all/notebooks/04-connectivity.ipynb` (markdown cell inserted before cell-spread-fn)
- `C:/Users/Rafik/Documents/GitHub/group4-data-for-all/notebooks/05-visualisation.ipynb` (cells `a1b2c3d4`, `b6c7d8e9`, `d8e9f0a1`, `f0a1b2c3`)
- Backups kept alongside the notebook: `05-visualisation.ipynb.bak-fix2`, `.bak-fix2b`

---

## Fix 3 — Intervention profile vectors

### Why

Per the Geographer's review section 4: single intervention labels are
geographically incoherent because the top-15 cells score high on multiple
axes simultaneously. La Marina del Port has sealed=0.80, LST anomaly +7.9°C,
NDVI -0.006 — labelling it "de-paving" alone strips planners of the compound
context and risks producing unshaded bare-soil scars instead of integrated
interventions.

### What changed in `03-scoring.ipynb`

Cell `cell-intervention` rewritten end-to-end. The old single-label argmax
remains intact (the `intervention_type` column still exists and equals the
dominant element of the profile, so downstream consumers do not break),
but two new columns are added.

**Before:**
```python
# Weighted sub-scores under Scenario B (to make the argmax fair)
W_B = SCENARIOS["B"]
sub_scores_B = pd.DataFrame({
    "sealed":   grid["s1_sealed"]   * W_B["sealed"],
    "lst":      grid["s2_lst"]      * W_B["lst"],
    "ndvi":     grid["s3_ndvi"]     * W_B["ndvi"],
    "mismatch": grid["s4_mismatch"] * W_B["mismatch"],
})

dominant = sub_scores_B.idxmax(axis=1)
label_map = {
    "sealed":   "de-paving",
    "lst":      "cooling",
    "ndvi":     "planting",
    "mismatch": "species-selection",
}
grid["intervention_type"] = dominant.map(label_map)
```

**After (excerpt — the full cell is in the notebook):**
```python
SCENARIO_B_WEIGHTS = {
    "s1_sealed":   W_B["sealed"],   # 0.55
    "s2_lst":      W_B["lst"],      # 0.20
    "s3_ndvi":     W_B["ndvi"],     # 0.20
    "s4_mismatch": W_B["mismatch"], # 0.05
}
LABEL_MAP = {
    "s1_sealed":   "de-paving",
    "s2_lst":      "cooling",
    "s3_ndvi":     "planting",
    "s4_mismatch": "species-selection",
}

def _intervention_profile(row):
    contributions = {LABEL_MAP[k]: row[k] * w for k, w in SCENARIO_B_WEIGHTS.items()}
    total = sum(contributions.values())
    if total <= 0:
        return {label: 0.0 for label in LABEL_MAP.values()}
    return {label: round(v / total * 100.0, 1) for label, v in contributions.items()}

grid["intervention_profile"] = grid.apply(_intervention_profile, axis=1)
grid["intervention_type"] = grid["intervention_profile"].apply(
    lambda p: max(p.items(), key=lambda x: x[1])[0]
)

def _profile_str(p):
    sorted_items = sorted(p.items(), key=lambda x: -x[1])
    return " · ".join(f"{v:.0f}% {k}" for k, v in sorted_items if v >= 5)

grid["intervention_profile_str"] = grid["intervention_profile"].apply(_profile_str)
```

New columns written into `data/scored_grid.geojson` when the notebook is re-run:

- `intervention_profile` — dict per cell, e.g. `{"de-paving": 60.2, "cooling": 27.5, "planting": 12.3, "species-selection": 0.0}`
- `intervention_profile_str` — display string, e.g. `"60% de-paving · 28% cooling · 12% planting"`
- `intervention_type` — preserved for back-compat; equals the dominant label of the profile

Note: I edited the notebook, but per the workflow the user will re-run
notebooks 03 -> 05 manually. Until then `scored_grid.geojson` does not yet
contain the profile columns and the regenerator in Fix 1 simply omits them.

### What changed in `05-visualisation.ipynb` (popup HTML)

Cell `a3b4c5d6` — the `_make_popup` function. A small italic line is now
rendered just below the rank/intervention coloured header:

**Before (popup body):**
```html
<div style='padding:8px 10px; border:1px solid #ddd;
            border-top:none; border-radius:0 0 4px 4px;'>
  <b>Cell:</b> {row.get('cell_id', 'n/a')}<br>
```

**After:**
```html
<div style='padding:8px 10px; border:1px solid #ddd;
            border-top:none; border-radius:0 0 4px 4px;'>
  <div style='font-style:italic; color:#444; margin-bottom:4px; font-size:12px;'>
    {row.get('intervention_profile_str', '')}
  </div>
  <b>Cell:</b> {row.get('cell_id', 'n/a')}<br>
```

Cell `e1f2a3b4` — the `_ensure_col` defaults list. Added a default of `""`
for `intervention_profile_str` so the popup degrades gracefully when the
user has not yet re-run notebook 03.

### Files touched

- `C:/Users/Rafik/Documents/GitHub/group4-data-for-all/notebooks/03-scoring.ipynb` (cell `cell-intervention`)
- `C:/Users/Rafik/Documents/GitHub/group4-data-for-all/notebooks/05-visualisation.ipynb` (cells `a3b4c5d6`, `e1f2a3b4`)
- Backups: `05-visualisation.ipynb.bak-fix3popup`, `.bak-fix3ensure`

---

## File-size summary

| File | Size | State |
|---|---|---|
| `data/regenerate_priority_csv.py` | 7,619 B | new |
| `outputs/priority_zones.csv` | 1,609 B | regenerated |
| `outputs/priority_zones.html` | 9,147 B | regenerated |
| `outputs/network_spread.html` | 259,535 B | will be deleted on next nb05 run |
| `notebooks/03-scoring.ipynb` | 46,922 B | cell `cell-intervention` rewritten |
| `notebooks/04-connectivity.ipynb` | 57,397 B | DEPRECATED markdown inserted before cell-spread-fn |
| `notebooks/05-visualisation.ipynb` | 152,466 B | 5 cells edited (a1b2c3d4, b6c7d8e9, d8e9f0a1, a3b4c5d6, e1f2a3b4, f0a1b2c3) |

---

## Verification

End-to-end automated check (run after the three fixes were applied):

```text
OK nb03 cell-intervention: profile vectors present
OK nb04 deprecated note at index 20, follows cell-source-patches, precedes cell-spread-fn
OK nb05 cell d8e9f0a1: all relabels applied
```

CSV regeneration sanity check:

```text
[sanity] districts represented: 10
[sanity] composite_B range: 0.747 .. 0.855
[sanity] intervention_type counts: {'de-paving': 15}
```

---

## What the user must do next

1. Re-run notebooks 03 -> 04 -> 05 manually (the user is editing notebooks
   live, so the agent did not execute kernels).
2. After notebook 05 runs, confirm `outputs/network_neighborhoods.html`
   exists and `outputs/network_spread.html` has been removed.
3. Re-run `python data/regenerate_priority_csv.py` to pick up the new
   `intervention_profile_str` column — the CSV will gain a 13th column
   automatically and the HTML table will show the compound profile.

No restart-and-run-all is required for notebook 03 alone — the
intervention-profile cell mutates an existing GeoDataFrame and the save
cell at the bottom writes it back out, so a fresh run of just that
notebook is enough to refresh `data/scored_grid.geojson`.
