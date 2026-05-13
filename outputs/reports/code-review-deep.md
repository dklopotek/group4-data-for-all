# Mycorrhizal Barcelona Pipeline — Deep Logic Review

**Scope:** Notebooks 02–05 plus `data/process_urban_atlas.py` and
`data/build_fungalroot.py`. We are reviewing **logic correctness and
meaningfulness**, not style.

**Reviewer verdict (TL;DR):**
- **CRITICAL data-integrity failures** in notebooks 02 and 03 silently
  corrupt every downstream artefact. The `em_pct` column is stuck at 0
  for every cell, the `sealed_pct` raster is double-divided by 100, and
  three cell-level thresholds are written on the wrong scale.
- The damage cascades into notebook 04 (every `bridge_score = 0`,
  spread-simulation gain is identically 0) and into notebook 05 (the
  produced map is internally consistent but built from broken inputs,
  with a mislabelled "Scenario B = LST-heavy" caption).
- The notebooks themselves are clean; the bugs are concentrated in a
  handful of identifiable lines and are fixable inside an afternoon.

Severity ladder used below: **CRITICAL** (numerical results invalidated),
**MAJOR** (logic wrong but limited blast radius), **MINOR**
(documentation / cosmetics), **VALIDATED** (checked and correct).

---

## Notebook 02 — `notebooks/02-grid-trees.ipynb`

### CRITICAL — `em_pct` is identically 0 for every cell because non-AM/EM/NM strings fall through silently
**File:** `notebooks/02-grid-trees.ipynb`, cell `o5p6q7r8` (P5 myco_type assignment) feeding cell `q7r8s9t0` (P6 fractions).

In P5 the FungalRoot CSV is loaded and uppercased:
```python
fr["myco_type"] = fr["myco_type"].str.upper().str.strip()
myco_map = dict(zip(fr["species_name"], fr["myco_type"]))
...
joined["myco_type"] = joined["cat_nom_cientific"].map(myco_map).fillna("NM")
```
The CSV produced by `build_fungalroot.py` returns values such as
`"EcM, AM undetermined"`, `"EcM, no AM colonization"`, `"EcM,AM"`,
`"non-mycorrhizal"`, etc. After uppercase these become
`"ECM, AM UNDETERMINED"`, `"NON-MYCORRHIZAL"`, etc. — **never the literal
strings `"AM"`, `"EM"`, or `"NM"`**.

The P6 aggregator then matches strict literals:
```python
am = counts.get("AM", 0); em = counts.get("EM", 0); nm = counts.get("NM", 0)
```
Result: every Pinus pinea / Pinus halepensis / Quercus ilex tree
(~9 100 trees city-wide) is silently bucketed into the
"ECM, AM UNDETERMINED" string, which is counted in nothing.
`em_pct = 0.0` for **every** cell, AM dominance is overstated, and NM
is also undercounted (e.g. Robinia pseudoacacia → "non-mycorrhizal"
becomes "NON-MYCORRHIZAL" and is also dropped).

Empirical confirmation from the produced `grid_trees.geojson`:
- `em_pct` unique values: `[0.0]` only.
- Mean EM% across cells: `0.0%`.
- Cell `o5p6q7r8` output already shows the warning sign:
  `myco_type` value_counts include `ECM, AM UNDETERMINED 11 937` and
  `ECM,AM 71`, none of which the downstream code understands.

**Suggested fix:** Normalise to a 3-symbol vocabulary inside the loader,
e.g.:
```python
def _normalise_myco(v: str) -> str:
    s = str(v).upper()
    if "ECM" in s or "ECTOMYCORRHIZAL" in s:
        return "EM"
    if "NON-MYCORRHIZAL" in s or "NM" == s:
        return "NM"
    if s.startswith("AM") or "ARBUSCULAR" in s:
        return "AM"
    return "NM"   # safer fallback than letting the raw string leak
fr["myco_type"] = fr["myco_type"].map(_normalise_myco)
```
The note in the markdown that says *"now that GBIF returns 'EcM, AM
undetermined' instead of 'EM'"* recognises the type mismatch but the
code was never updated.

---

### CRITICAL (downstream blast) — `myco_map.setdefault(sp, mt)` lets the broken CSV value override the correct stub
**File:** `notebooks/02-grid-trees.ipynb`, cell `o5p6q7r8`.

```python
myco_map = dict(zip(fr["species_name"], fr["myco_type"]))
...
for sp, mt in TOP20_MYCO.items():
    myco_map.setdefault(sp, mt)
```
`setdefault` only writes when the key is missing. Since FungalRoot
already contains `Pinus halepensis`, `Pinus pinea`, and `Quercus ilex`
with `"EcM, AM undetermined"` values, the curated stub entries
(`"Pinus halepensis": "EM"`, etc.) are **never used**. The hand-curated
canonical-EM mappings are dead code. Combined with the bug above this
guarantees that no tree is ever tagged `EM`.

(Note: `"Platanus × acerifolia"` does NOT match `"Platanus acerifolia"`
in FungalRoot, so the stub correctly fills the gap there. That single
case happens to work — by accident.)

**Suggested fix:** Either flip to `myco_map[sp] = mt` (stub wins) or run
the normalisation function above so the FungalRoot value resolves to
`"EM"` and the stub is unnecessary.

---

### MAJOR — silent failure mode masking via `.fillna("NM")`
**File:** `notebooks/02-grid-trees.ipynb`, cell `o5p6q7r8`, line:
```python
joined["myco_type"] = joined["cat_nom_cientific"].map(myco_map).fillna("NM")
```
The `.fillna("NM")` quietly converts lookup misses into NM. With ~24%
of trees outside the top-20 list this is a real signal-loss event, but
the printed "coverage" diagnostic (`(joined["myco_type"] != "NM").sum()`
on the next line) only checks `!= "NM"`, so cells with the dirty
`"ECM, AM UNDETERMINED"` string are reported as "covered" even though
they are downstream black holes. The 89.7% coverage figure is misleading.

**Suggested fix:** Track unmatched species separately and refuse to map
them to NM; fail loudly or tag as `"UNK"` so the aggregator can complain.

---

### VALIDATED — 400 m grid is in metres, not degrees
**File:** `notebooks/02-grid-trees.ipynb`, cells `c3d4e5f6` and `g7h8i9j0`.

`GRID_SIZE = 400`, `CRS_PROJ = "EPSG:25831"` (ETRS89 / UTM Zone 31N — a
metre-unit projection). Boundary loaded as WGS84 GeoJSON and reprojected
with `boundary.to_crs(CRS_PROJ)`. Bounding box reported as 14 679 m × 16 744 m,
matching Barcelona's true ~15 × 17 km extent. Tile geometries built with
`box(xi, yi, xi+GRID_SIZE, yi+GRID_SIZE)` after snapping `x0,y0,x1,y1` to
GRID_SIZE multiples. **No unit confusion** in the grid.

### VALIDATED — `am_blindness_flag` threshold logic
**File:** `notebooks/02-grid-trees.ipynb`, cell `s9t0u1v2`.

`am_pct` is on a 0–100 scale (`am / n * 100`). The flag uses
`am_pct >= 80.0`, which correctly means "≥ 80 %". Output is plausible
(63.4% of cells flagged AM-blind, matching the dominance of Platanus,
Celtis, Tipuana et al. confirmed independently in notebook 01). Note
that the *value* of `am_pct` is **incorrectly inflated** because EM
trees are misclassified, so even though the threshold logic is sound,
the flag fires too often. (This sits downstream of the CRITICAL bug
above, not as a separate issue.)

### VALIDATED — fraction-sum sanity check identifies the bug but is ignored
**File:** `notebooks/02-grid-trees.ipynb`, cell `s9t0u1v2`.

```python
frac_sum = (cell_stats["am_pct"] + cell_stats["em_pct"] + cell_stats["nm_pct"])
max_deviation = (frac_sum - 100).abs().max()
```
The output prints `Max fraction-sum deviation from 100%: 100.0000` —
i.e. for some cell, AM+EM+NM sums to ~0 (because all the trees in the
cell are bucketed as `"ECM, AM UNDETERMINED"`). This is a giant red
flag that the reporting glosses over with the comment "rounding only".
A 100-point deviation is not rounding. **The sanity check works; the
team just ignored the alarm.**

**Suggested fix:** Promote the assertion to `assert max_deviation < 1.0`
so the notebook fails fast.

---

## Notebook 03 — `notebooks/03-scoring.ipynb`

### CRITICAL — `sealed_pct` is divided by 100 twice; S1 is 100× too small
**File:** `notebooks/03-scoring.ipynb`, cell `cell-s1`, line:
```python
sealed_raw = zonal_mean_from_raster(SEALED_RASTER_PATH, grid, band=1, scale=1/100)
```
Comment says "Urban Atlas stores values as 0–100 % imperviousness →
divide by 100". But `data/process_urban_atlas.py` already writes the
raster in 0–1 fraction units (verified directly: `min=0.024, max=0.894,
mean=0.569`). The notebook divides by 100 again.

Empirical confirmation from `scored_grid.geojson`:
- `sealed_pct` range across all 495 cells: **[0.000243, 0.00894]**.
- `s1_sealed` is identical to `sealed_pct`.
- "Sealed-dominant" Scenario B uses `0.55 × s1_sealed` → max
  contribution to composite = `0.55 × 0.00894 = 0.0049`.
- The "sealed-dominant" weighting is therefore a misnomer — sealing
  contributes essentially nothing to the composite ranking.

**Effect cascades:**
1. Top-15 ranking is driven by LST + NDVI, not sealing as the brief
   demands.
2. Notebook 04 uses `SEAL_THRESHOLD = 0.7` to decide which trees are
   physically blocked. With sealed_pct < 0.01 everywhere, **zero trees
   are ever blocked**, so every `bridge_score = 0` and the spread
   simulation produces a `gain = +0 trees` for every season — the very
   "Top bridge zone" output in cell `cell-summary` reads
   `bridge_score=0`, which is a tell.

**Suggested fix:** Drop the `scale=1/100` argument:
```python
sealed_raw = zonal_mean_from_raster(SEALED_RASTER_PATH, grid, band=1)
```
Or, equivalently, fix the unit mismatch in `process_urban_atlas.py` if
some other consumer expects 0–100. The ambiguity itself is the disease;
pin the unit in one place and document it.

---

### CRITICAL — S4 mismatch thresholds are interpreted on a 0–1 scale, but the data is 0–100
**File:** `notebooks/03-scoring.ipynb`, cell `cell-s4`, function
`compute_mismatch_score`.

```python
em_dom = em_pct >= 0.5      # intends "≥ 50%"
...
am_dom = am_pct >= 0.8      # intends "≥ 80%"
```
But upstream notebook 02 emits `am_pct`, `em_pct` on a **0–100 scale**.
So:
- `am_pct >= 0.8` matches every cell with even 1% AM (≈ all 495).
- `em_pct >= 0.5` matches anything > 0.5% EM, but `em_pct = 0` due to
  the upstream bug, so this branch never fires.

Result: 489 cells get `s4_mismatch = 0.5` (AM-blind null), 6 cells get
`0.6` (mixed), 0 get the EM branches. S4 has effectively two values,
both close to the 0.5 fixed-point.

**Suggested fix:** Either rescale on entry (`am_frac = am_pct / 100`)
or change the thresholds to `>= 80` and `>= 50`. Pick a convention and
document it once.

---

### CRITICAL — `colonisation_uncertain` threshold has the same 0.3-vs-30 unit confusion
**File:** `notebooks/03-scoring.ipynb`, cell `cell-colonisation`.
```python
grid["colonisation_uncertain"] = (
    grid["top15_scenario_B"] & (grid["trees_young_pct"] >= 0.3)
)
```
`trees_young_pct` is on a 0–100 scale (notebook 02, cell `m3n4o5p6`:
`n_young / n_total * 100`). Threshold `0.3` therefore means "≥ 0.3 %",
not "≥ 30 %". Looking at the output table: cells flagged uncertain
include `trees_young_pct = 0.83` (less than 1%). This is far below the
intent stated in the markdown ("Cells in the top-15 where ≥ 30% of
trees were planted recently").

**Effect:** 9 / 15 top-15 cells get the warning flag; if the threshold
were a true 30%, only 0 / 15 would qualify (max value among top-15 is
25.72%). The output is over-warning by ~30×.

**Suggested fix:** `>= 30.0` (keep the 0–100 scale) or convert
`trees_young_pct` to a fraction at source.

---

### MAJOR — `intervention_type` is "highest WEIGHTED contribution", not "dominant SUB-SCORE"
**File:** `notebooks/03-scoring.ipynb`, cell `cell-intervention`.

Markdown promises "the dominant sub-score determines the intervention
recommendation per cell." Code does:
```python
sub_scores_B = pd.DataFrame({
    "sealed":   grid["s1_sealed"]   * W_B["sealed"],   # × 0.55
    "lst":      grid["s2_lst"]      * W_B["lst"],     # × 0.20
    "ndvi":     grid["s3_ndvi"]     * W_B["ndvi"],    # × 0.20
    "mismatch": grid["s4_mismatch"] * W_B["mismatch"],# × 0.05
})
dominant = sub_scores_B.idxmax(axis=1)
```
This is the argmax of weighted contributions, which, for a flat
sub-score profile, will lean toward whichever sub-score has the largest
weight. With weights {0.55, 0.20, 0.20, 0.05} you'd expect S1 to win
most of the time — but S1 is 100× too small (CRITICAL above), so S2
and S3 dominate, producing 174 cooling and 320 planting and only 1
species-selection city-wide, and zero `de-paving` cells. The
document-vs-code mismatch is therefore not catastrophic in current
data; in the *intended* state it would matter.

**Suggested fix:** Pick one and stick to it. If the deliverable is
"largest unweighted barrier dimension", use raw sub-scores. If it's
"what is dragging this cell up the ranking", use weighted, but rename
the column `dominant_weighted_contribution`. Don't say one and ship the
other.

---

### MAJOR — Scenario B is mis-labelled as "LST-heavy" / "Sealed-heavy" mixed-up downstream
**File:** `notebooks/03-scoring.ipynb`, cell `cell-composite` defines
- A: equal `(0.25, 0.25, 0.25, 0.25)`
- B: sealed-heavy `(0.55, 0.20, 0.20, 0.05)`
- C: heat+canopy `(0.17, 0.30, 0.30, 0.23)`

But in `notebooks/05-visualisation.ipynb` cell 19 the chart headers say:
```python
("Scenario B\n(LST-heavy)", ids_B_p),
("Scenario C\n(Sealed-heavy)", ids_C_p),
```
And `priority_zones.html` body text says
*"Scenario B: LST-heavy weighting"*.

The labels in the visual outputs do not match the actual weights. This
is communications-grade wrong: a planner reading the chart will think
B is the "thermal stress" scenario when it is the "physical sealing"
scenario.

**Suggested fix:** In notebook 05, change the column header to
`(Sealed-heavy 0.55)` and the HTML caption similarly.

---

### VALIDATED — weight sums to 1.0 after the 0.55/0.20/0.20/0.05 fix
**File:** `notebooks/03-scoring.ipynb`, cell `cell-composite`.
```python
assert abs(total_w - 1.0) < 1e-6, ...
```
`A: 0.25 ×4 = 1.0`, `B: 0.55+0.20+0.20+0.05 = 1.0`,
`C: 0.17+0.30+0.30+0.23 = 1.0`. All assertions pass at runtime. **VALIDATED.**

### VALIDATED — Jaccard sensitivity is genuine top-15 set comparison (not first-15 by index)
**File:** `notebooks/03-scoring.ipynb`, cell `cell-sensitivity`.

`top15_indices[label]` is the output of
`select_top15_with_district_constraint`, which returns the
**ranked-then-district-constrained** index labels. The index labels are
stable across scenarios (same DataFrame), so `set(v.tolist())`
produces a comparable set of cell identifiers, and
`jaccard(set_A, set_B)` returns the genuine top-15 overlap. Reported
values (0.875, 1.000, 0.875) are consistent with the manual reading of
the printed top-15 tables. **VALIDATED.**

### VALIDATED — NDVI inversion direction is correct
**File:** `notebooks/03-scoring.ipynb`, cell `cell-s3`.
```python
normalised_ndvi = (mean_ndvi - ndvi_min) / (ndvi_max - ndvi_min)
grid["s3_ndvi"] = (1 - normalised_ndvi).clip(0, 1)
```
Low NDVI → low normalised → s3 close to 1 (high barrier). High NDVI →
s3 close to 0. **Direction matches the markdown ("low canopy means high
mycorrhizal barrier").** VALIDATED.

### MINOR — sealed-surface raster zonal-mean inherits the LST bug pattern
The `zonal_mean_from_raster` helper does `data = data[data != src.nodata]`,
which is good, but this mask is applied AFTER `astype(np.float64)`, so
NaNs in the float band that are not equal to `src.nodata` are not
filtered. For NDVI raster, `src.nodata is None` (we verified) and NaNs
remain in `data`; then `np.nanmean` is used so NaNs are ignored. This
happens to work but it is fragile — a raster without `nodata` set and
without `NaN` could pollute the mean. Add `data = data[~np.isnan(data)]`
before the `nanmean` for safety.

---

## Notebook 04 — `notebooks/04-connectivity.ipynb`

### VALIDATED — cKDTree operates on UTM31N metres, not degrees
**File:** `notebooks/04-connectivity.ipynb`, function `build_subgraph`,
cell `cell-graph-fn`.
```python
coords = trees_subset[["x_etrs89", "y_etrs89"]].values
...
pairs = tree_index.query_pairs(r=distance_m, output_type="ndarray")
```
Coordinates come from `x_etrs89`/`y_etrs89` columns (ETRS89 UTM31N,
metre-unit). `AM_DISTANCE_M = 15.0` and `EM_DISTANCE_M = 35.0` are
therefore 15 m / 35 m, matching the spec from Jumpponen &
Egerton-Warburton. **No unit confusion** — VALIDATED.

The `bridge_score_for_zone` function similarly uses
`(x_etrs89, y_etrs89)` and `kd.query_ball_point(..., r=AM_DISTANCE_M)` —
correctly in metres.

The **spread simulation** also uses metre-unit coordinates and
`r = spread_m_per_season * season` with `spread_m_per_season = 2.0` m —
consistent units. VALIDATED.

### CRITICAL (downstream of notebook 03 sealing bug) — every `bridge_score = 0`
**File:** `notebooks/04-connectivity.ipynb`, cell `cell-bridge-fn` and
`cell-compute-bridges`.
```python
blocked = trees_gdf[
    (trees_gdf["cell_id"] == zone_cell_id) &
    (trees_gdf["sealed_pct"] >= SEAL_THRESHOLD)   # 0.7
].copy()
```
Because notebook 03 produces `sealed_pct < 0.01` for every cell (the
double-divide bug), `blocked` is always empty. Every zone's bridge
score is 0. The output table reads `bridge_score = 0` for all 15 zones,
making the entire "network leverage" deliverable meaningless.

This is a **propagated** failure, not an independent bug. Fixing the
notebook-03 unit error and re-running notebook 04 should make this
section produce real numbers.

### MAJOR — bridge_score double-counts when both endpoints are in the same blocked zone
**File:** `notebooks/04-connectivity.ipynb`, cell `cell-bridge-fn`.

```python
for bi, (bx, by) in enumerate(blocked_coords):
    ...
    nbr_idx = kd.query_ball_point([bx, by], r=dist_thresh)
    for j in nbr_idx:
        n_id = all_ids[j]
        ...
        if b_comp != n_comp:
            new_connections += 1
```
The outer loop iterates over every blocked tree `b` in the zone. For a
neighbour `n` that is **also in the blocked set**, the same potential
edge will be counted once with (b=tree₁, n=tree₂) and again with
(b=tree₂, n=tree₁). The condition `if n_id == b_id: continue` skips
self but does **not** dedupe ordered pairs. The previous reviewer
flagged this; the fix has not landed.

**Suggested fix:** Use a `set` keyed on `frozenset({b_id, n_id})`:
```python
seen_pairs = set()
...
key = frozenset((b_id, n_id))
if key in seen_pairs: continue
seen_pairs.add(key)
new_connections += 1
```
Or: only iterate over neighbours with `j > i` when both are in the
blocked set. Cross-zone (blocked ↔ unblocked) pairs are not
double-counted.

The bug is currently dormant (because no tree is ever blocked), but it
will surface as soon as the sealed_pct unit fix lands.

### MAJOR — spread simulation does not actually simulate hyphal *network* extension
**File:** `notebooks/04-connectivity.ipynb`, function `simulate_spread`,
cell `cell-spread-fn`.

```python
src_coords = non_barrier[src_mask][["x_etrs89", "y_etrs89"]].values
...
for src_xy in src_coords:
    nbr = kd.query_ball_point(src_xy, r=radius)
    reached_indices.update(nbr)
```
What this does: "find all non-barrier trees within `radius` metres of
**any source tree's original position**". With `radius = 2 × season`
m, season 5 means a 10 m radius from each of the 2 464 source trees.

What the markdown promises:
> "every fungal island extends by 2 m in all directions through
> non-sealed soil. We approximate this by expanding the convex hull of
> each island's tree points by `season × 2 m` and then checking which
> trees fall inside the expanded hull."

The code does NOT use island convex hulls, does NOT consume the
NetworkX graph `G`, and does NOT propagate hyphal growth from one
season's reached set into the next season's frontier. It is a single
fixed-radius range query around the original source-patch trees. The
"trees reachable" count therefore grows extremely slowly (2 464 → 2 512
over 5 seasons) and is independent of network topology.

The intervention layer would be expected to produce gains by un-blocking
trees inside the de-paved cells so they enter `non_barrier`. But:
1. With the sealed_pct bug all trees are already non-barrier, so
   `trees_intervened.loc[..., "sealed_pct"] = 0.0` is a no-op.
2. Even with that fixed, the gain would only be the un-blocked trees
   that happen to fall inside the 2 × season radius of an *original*
   source tree — a vanishingly thin slice.

**Effect:** The "Spread gain from top-3 bridge interventions" output is
identically 0 for every season (printed in the notebook). This is the
expected behaviour of the *current* code; it does not mean intervention
is useless.

**Suggested fix:** Either implement the convex-hull-per-island approach
described in the markdown, or do a true graph-traversal from source
nodes through `G` allowing 2 m of expansion per season at the frontier
(season-on-season, with each season's reached trees seeding the next).

### MINOR — AM graph only built for one demonstration district
**File:** `notebooks/04-connectivity.ipynb`, cell `cell-build-graph`.

This is documented honestly — both in markdown and in cell `cell-summary`
("EM graph covers all districts. AM graph covers demonstration district
only"). Acceptable as a runtime tradeoff. Not a bug.

### MINOR — `trees_gdf["sealed_pct"].fillna(0.5)` masks join failures
**File:** `notebooks/04-connectivity.ipynb`, cell `cell-grid-join`.
`fillna(0.5)` for unjoined trees is a soft default; with the
notebook-03 sealing bug nothing currently crosses the 0.7 threshold,
so this default is silent. Document the assumption or refuse to fill,
so a real spatial-join failure surfaces.

---

## Notebook 05 — `notebooks/05-visualisation.ipynb`

### VALIDATED — intervention colour codes are consistent across map and chart
**File:** `notebooks/05-visualisation.ipynb`, cell `INTERVENTION_COLOURS`
(after Cell 2):
```python
INTERVENTION_COLOURS = {
    "de-paving": "#E07B39", "cooling": "#C0392B",
    "planting":  "#27AE60", "species-selection": "#2980B9",
    "De-paving": "#E07B39", "Cooling": "#C0392B",
    "Planting":  "#27AE60", "Species-selection": "#2980B9",
}
```
Both the priority map (cell 14) and the sensitivity chart (cell 19)
look up colours via `_intervention_colour`/`INTERVENTION_COLOURS.get`,
so the same intervention type renders the same colour in both outputs.
**Consistent across the four codes.** VALIDATED.

### MAJOR — sensitivity-chart legend renders eight intervention entries instead of four
**File:** `notebooks/05-visualisation.ipynb`, cell 19, lines:
```python
for itype, colour in INTERVENTION_COLOURS.items():
    legend_elements.append(mpatches.Patch(facecolor=colour, label=f"Intervention: {itype}"))
```
Iterates over the 8-key dict (lowercase + title-case aliases), which
produces a duplicated 8-row legend (`Intervention: de-paving`,
`Intervention: De-paving`, `Intervention: cooling`,
`Intervention: Cooling`, ...). Visually noisy.

**Suggested fix:** Use a deduplicated tuple, e.g.
`for itype in ("de-paving","cooling","planting","species-selection"):`.

### MAJOR — Scenario labels are wrong in the chart and HTML
**File:** `notebooks/05-visualisation.ipynb`, cell 19 column headers:
```python
("Scenario B\n(LST-heavy)",  ids_B_p),
("Scenario C\n(Sealed-heavy)", ids_C_p),
```
And `priority_zones.html` body: `"Scenario B: LST-heavy weighting"`.

The actual notebook 03 weights are B = sealed-heavy (0.55), C = heat+canopy.
**Labels are swapped/incorrect.** Already filed under notebook 03
(MAJOR scenario mis-labelling). The fix lives in notebook 05.

### MAJOR — `DATA_LABEL` reflects file presence, not data validity
**File:** `notebooks/05-visualisation.ipynb`, cell 8.

`IS_SYNTHETIC = False` is set when every input file exists. The HTML
limitations footer then prints "REAL DATA" — but the inputs are
unit-broken (em_pct=0, sealed_pct≈0). A reader sees "REAL DATA" and
trusts the values. Either:
1. Keep this label as "files present" and add a separate data-quality
   gate, or
2. Add an upstream check: at minimum assert
   `scored_grid["sealed_pct"].max() > 0.05` and
   `(scored_grid["em_pct"] > 0).any()` before stamping "REAL DATA".

The limitations footer otherwise has good content (sections 1–8 are
substantive and honest), but the headline status is misleading without
the gate.

### VALIDATED — `_buffer_wgs84_to_metres` correctly buffers in metres via Web Mercator
**File:** `notebooks/05-visualisation.ipynb`, cell 26.
```python
project_fwd = pyproj.Transformer.from_crs(4326, 3857, always_xy=True).transform
geom_m = shapely_transform(project_fwd, geom)
buffered_m = geom_m.buffer(metres)
return shapely_transform(project_bck, buffered_m)
```
Web Mercator distorts north-south but at Barcelona's latitude (~41.4°)
the scale factor is ~1.32 (1 / cos(41.4°)). A 500 m buffer at 41.4° N
becomes ~660 m on the ground. This is acceptable for an "illustrative
heuristic" (the markdown explicitly disclaims calibration), but if a
calibrated metre is wanted the projection should be EPSG:25831 instead.
**Implementation matches the documented intent** (ALL caveats fall
under the existing "not a calibrated dispersal model" note in the
markdown.)

### MINOR — limitations footer contradicts itself on `colonisation_uncertain`
The footer says (section 5):
> *"The colonisation_uncertain flag in the tabular report identifies
> zones where this caveat is likely to apply based on sealed-surface
> fraction > 85% and/or LST anomaly > 4°C."*

But the actual computation in notebook 03 (cell `cell-colonisation`)
is `top15_scenario_B & (trees_young_pct >= 0.3)`. The flag is on
*tree age*, not sealing or LST. Either the doc is wrong or the
implementation drifted. Fix one to match the other.

---

## `data/process_urban_atlas.py`

### VALIDATED — area-weighted mean is genuinely area-weighted
**File:** `data/process_urban_atlas.py`, lines 100–107.
```python
overlay = gpd.overlay(grid[["cell_id", "geometry"]],
                      ua_clip[["sealed_frac", "geometry"]],
                      how="intersection", keep_geom_type=False)
overlay["area_m2"] = overlay.geometry.area
grouped = overlay.groupby("cell_id").apply(
    lambda df: np.average(df["sealed_frac"], weights=df["area_m2"])
).reset_index()
```
`gpd.overlay(..., how="intersection")` produces one row per (grid cell,
UA polygon) intersection geometry. `np.average(..., weights=area_m2)`
on each cell's group is the mathematically correct area-weighted mean.
Reprojection to EPSG:25831 (metre CRS) at line 80–82 is what makes
`.geometry.area` a true square-metre area. **Correctly area-weighted.**
VALIDATED.

### MINOR — `SEALED_FRACTION` lookup is broadly defensible but documented as level 1, not level 2
**File:** `data/process_urban_atlas.py`, lines 29–54.

The five-digit codes used (e.g. `11100`, `11210`, `12210`) are Urban
Atlas Level 2/3 codes (the official "code_2018" field), and the
fractions assigned are within the published per-class IS (Imperviousness)
ranges from Copernicus Urban Atlas Mapping Guide v6 Annex B and
Hermosilla et al. 2021:

- `11100` (Continuous Urban Fabric, IS > 80%) → 0.90 — defensible (mid-range)
- `11210` (Discontinuous dense, 50–80% IS) → 0.65 — mid-range, defensible
- `11220` (Discontinuous medium, 30–50%) → 0.40 — mid-range, defensible
- `11230` (Discontinuous low, 10–30%) → 0.20 — mid-range, defensible
- `11240` (Discontinuous very low, <10%) → 0.05 — mid-range, defensible
- `12100` (Industrial / commercial) → 0.80 — within published 50–90%
- `12210` (Fast transit roads) → 0.92 — defensible
- `14100` (Green urban areas) → 0.05 — defensible (mostly grass)
- `21000` / `22000` / `23000` (arable / crops / pastures) → 0.02 — within published <5%

**No values are out of band**, but two notes:
1. `12230` (Railways) at 0.70 is on the high end; published ranges put
   railway corridors at 30–60% IS depending on country. Suggest 0.50.
2. Default for unmatched codes is `0.30` (line 86) which is silently
   treated as a sentinel later (`matched = ua["sealed_frac"].ne(0.30).sum()`).
   Choose a non-coincidental fallback (e.g. `np.nan` and then a
   separate counter) to avoid spurious "matched" inflation if any real
   class genuinely deserves 0.30.

The mapping is fit-for-purpose; tighten the railway entry and the
sentinel default.

### MAJOR — TIF rasterisation uses 400 m pixels, but consumer reads it at native resolution
**File:** `data/process_urban_atlas.py`, lines 124–158.

The script computes `sealed_pct` per 400 m cell from the polygon overlay,
then rasterises to a `400 m × 400 m`-pixel TIF (`width = (xmax-xmin)/400`).
Notebook 03 then reads this TIF with
`rio_mask(src, [geom], crop=True)` over a 400 m grid cell — i.e. a
single pixel per cell. That is fine in itself. The actual values
(0.024 to 0.89) are sensible. The unit-confusion downstream (the
`scale=1/100` in notebook 03) is the problem; this file is internally
consistent. **Calling out only because the unit at the producer/consumer
boundary should be pinned in a docstring header**: e.g.
`"sealed_surface.tif is float32 in [0.0, 1.0] fraction; consumers must
not rescale."`

---

## `data/build_fungalroot.py`

### MAJOR — output schema is incompatible with the notebook 02 consumer
**File:** `data/build_fungalroot.py`, lines 53–59.

The "most-common myco_type per species" aggregation:
```python
result = (merged.groupby("species_name")["myco_type"]
          .agg(lambda x: x.value_counts().index[0])
          .reset_index())
```
preserves whatever string FungalRoot supplies (`"EcM, AM undetermined"`,
`"non-mycorrhizal"`, etc.). This is faithful to the source but produces
output that the notebook-02 consumer cannot parse (see Notebook 02
CRITICAL #1). The producer is **upstream** of the bug — it could
either:
1. Emit canonical `{AM, EM, NM, MIXED}` symbols as a second column
   (`myco_type_norm`), making the join trivial and unambiguous, OR
2. Stay raw, but require notebook 02 to apply a normalisation function
   on read.

Either is fine; pick one and own it. Currently neither end normalises,
which is why the data pipeline silently fails.

### MINOR — `requests.get(URL, timeout=180)` with no retry
**File:** `data/build_fungalroot.py`, line 23. GBIF orphans bucket is
not a high-uptime endpoint. Wrap in a `tenacity.retry` or even a simple
3-attempt loop so a transient 503 doesn't kill the build.

### MINOR — regex extraction loses cultivars and hybrid markers
**File:** `data/build_fungalroot.py`, line 35–36.
```python
occ["species_name"] = (occ["scientificName"].str.strip()
                       .str.extract(r"^([A-Z][a-z\-]+ [a-z\-x]+)"))
```
This regex captures only `Genus species` — it strips authorship and
infraspecific epithets but also drops the `×` hybrid marker. The BCN
inventory uses `Platanus × acerifolia` (with `×`); FungalRoot rows are
named `Platanus acerifolia`. The Notebook-02 stub patches this for
exactly one species. Document the convention or post-process to strip
`×` from BCN inventory names on join.

---

## Verdict by file

| File | Status | Why |
|------|--------|-----|
| `notebooks/02-grid-trees.ipynb` | **MAJOR-REWORK** | `myco_type` join silently drops every EM tree; `setdefault` orders the merge backwards; `fillna("NM")` masks the bug. Grid construction itself is clean. |
| `notebooks/03-scoring.ipynb` | **MAJOR-REWORK** | Three independent unit-confusion bugs (sealed_pct ÷100×2, S4 thresholds on 0–1 vs 0–100, colonisation flag on 0–1 vs 0–100). Composite ranking and intervention assignment compromised. Scenario weights themselves are correct. |
| `notebooks/04-connectivity.ipynb` | **MINOR-FIX** | Logic is mostly sound and CRS-correct. The bridge_score = 0 result is propagated from notebook 03; the only original bug is the bridge double-count (dormant) and the spread-simulation does-not-actually-simulate-spread mismatch with its docstring. |
| `notebooks/05-visualisation.ipynb` | **MINOR-FIX** | Scenario-label swap (B mis-labelled "LST-heavy"); duplicated legend entries; "REAL DATA" banner misleading without an integrity gate. Map/chart colour consistency and folium plumbing are all clean. |
| `data/process_urban_atlas.py` | **MINOR-FIX** | Area-weighted mean is correct; SEALED_FRACTION mapping is defensible. Document the output unit (0–1) at the producer boundary; reconsider 0.30 sentinel and the 0.70 railway value. |
| `data/build_fungalroot.py` | **MINOR-FIX** | Faithful FungalRoot dump but emits non-canonical strings. Either normalise at the producer or document the requirement clearly so notebook 02's loader is responsible. Consider preserving hybrid `×` markers. |

**Production-ready: none.** The pipeline is structurally sound and the
plumbing between notebooks is fine, but the three unit/scale errors in
notebook 03 (and the FungalRoot string bug in notebook 02) corrupt every
numeric deliverable. Fix order:

1. Notebook 02 myco-type normalisation (CRITICAL).
2. Notebook 03 sealed_pct unit (CRITICAL).
3. Notebook 03 S4 thresholds and colonisation_uncertain threshold (CRITICAL).
4. Notebook 04 bridge double-count and spread-simulation rewrite (MAJOR).
5. Notebook 05 scenario labels and legend dedup (MAJOR/MINOR).

After (1)–(3), re-run the whole pipeline — most of (4) and (5) become
checkable against meaningful numbers rather than the all-zero
placeholders the team is currently looking at.
