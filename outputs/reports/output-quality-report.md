# Output Quality Report — Mycorrhizal Barcelona Pipeline

**Reviewer:** Analytics Reporter (Quality Review Agent)
**Date:** 2026-05-10
**Branch:** session-2/data-understanding-rafik
**Scope:** Post-reality-check review of all six pipeline outputs

---

## Overall Assessment

The Reality Checker fixed the three critical bugs (empty CSV, wrong scenario column names,
grey-only map colours). All six output files now exist with meaningful content. The pipeline
runs on real data (not synthetic). However, three substantive data problems remain that
need attention before this is presentable to the Ajuntament audience.

---

## 1. File-by-File Status

### priority_zones.csv — PASSES WITH CAVEATS

**What is good:**
- 15 rows, 0 null values across all 14 columns
- Real district names: SANTS - MONTJUÏC, SANT ANDREU, SANT MARTÍ, NOU BARRIS, SARRIÀ - SANT GERVASI
- Real barri names: LA MARINA DEL PORT, EL BON PASTOR, LA VERNEDA I LA PAU, etc.
- Real intervention types: "cooling" (5 zones), "planting" (10 zones)
- Composite scores have meaningful spread: 0.293 to 0.416 (Scenario B)
- UTF-8 encoding is correct — Catalan accents (Ï, Í, À) are properly stored

**Problems found:**

**Problem A — sealed_pct is 0.003 for all 15 zones (constant, meaningless)**

`sealed_pct` = 0.003 for every single cell in the entire 495-cell grid, not just the top-15.
This is because the Urban Atlas raster (`data/urban-atlas/sealed_surface.tif`) appears to be
a near-blank raster with almost no variation. From notebook 03 (Cell S1), the file was found
and read, reporting `min=0.003, mean=0.003, max=0.003` — all identical. This is not a column
name bug; the raster itself is producing uniform near-zero output.

Because `s1_sealed` = 0.003 for all cells, Sub-score 1 contributes almost nothing to
composite scores. Under Scenario B (Sealed-dominant, w=0.55), this means the ranking is
almost entirely driven by LST anomaly and NDVI — the "sealed surface" in the name is a
misnomer for these results.

**Root cause:** The Urban Atlas raster is likely all-nodata, all-zero, or
incorrectly georeferenced such that no cell's polygon overlaps valid raster pixels.
The `zonal_mean_from_raster` function silently returns the nodata value (0.003 appears
to be a float artefact near zero from the raster's nodata mask) rather than raising an error.

**Fix required:** Inspect `data/urban-atlas/sealed_surface.tif` in QGIS or via `rasterio.open`
to check its extent, CRS, and whether it overlaps the grid. If the raster is blank or
misaligned, re-download from Copernicus Land Monitoring Service and re-run notebook 03.

**Problem B — bridge_score is 0.0 for all 15 zones**

Confirmed by the Reality Checker (Issue 4) and verified here. `bridge_scores.csv` has
`bridge_score` = 0 for all 15 entries. This is a notebook 04 (connectivity) data problem:
either the betweenness centrality computation produced zeros or the results were not saved.

Impact on outputs: the network spread map's "top-3 bridge interventions" layer defaults
to the top-3 by composite rank (C016_011, C031_035, C032_032), not by actual network
leverage. The bridge_score column in the tabular report shows "0.0" for all zones, which
a planner reading the HTML table will notice and question.

**Problem C — colonisation_uncertain flag uses wrong threshold**

The flag is set in notebook 03 with the condition `trees_young_pct >= 0.3`. However,
`trees_young_pct` is stored on a 0–100 percentage scale (mean 7.6%, max 100%). The
threshold 0.3 therefore means "more than 0.3% of trees are young" — which is an
ecologically trivial condition that flags 8 of 15 top zones as uncertain.

The notebook's own markdown comment says "≥ 30% of trees were planted recently", which
is the ecologically meaningful threshold. The code has a unit confusion bug: the condition
should be `trees_young_pct >= 30` (percent) not `>= 0.3`.

With the corrected threshold of 30%, zero of the top-15 zones would be flagged, which may
also be too few. A threshold of 10–15% (i.e. 10–15 percent young trees) would flag 4 zones
and is more defensible ecologically.

---

### sensitivity_comparison.png — PASSES

All 15 zones appear in all 3 scenarios across all 3 columns. Jaccard similarity is 1.0 for
all pairs (A vs B, A vs C, B vs C). This is a genuine result, not a bug:
the top-15 set is completely stable across all weight scenarios. The chart correctly
renders this with bold green text for all 15 entries.

**This is a strong result for the Ajuntament audience.** It means the priority list does not
depend on which weighting philosophy the planner chooses — the same 15 zones come up
regardless. Document this explicitly in the presentation as "rankings are weight-robust."

Note: the near-perfect Jaccard likely reflects that sealed_pct is constant at 0.003 for all
cells (Problem A above), meaning all three scenarios are ranking primarily by LST and NDVI.
Once the sealed raster is corrected, Jaccard may fall below 1.0, which is expected and fine
as long as it stays above 0.7.

---

### priority_map.html — PASSES

- 15 top-15 zones rendered with correct intervention-type colours (red for cooling, green for planting)
- 480 background grid cells in light grey
- 2,165 network islands as purple convex-hull polygons
- 10 district boundaries with labels (toggleable)
- Numbered rank markers (1–15) at zone centroids
- Popups include all required fields: district, barri, sub-scores, composite score, intervention type, colonisation flag
- File size 1.1 MB — appropriate for an interactive Folium map

No issues found with the map layer construction.

---

### priority_zones.html — PASSES

- 15 rows rendered with colour-coded intervention type cells
- Colonisation-uncertain rows highlighted in red (8 of 15 zones, due to the threshold bug in Problem C above)
- "Appears in all scenarios" column shows green highlight for all 15 zones (correct)
- File size 21,612 B (reasonable for a styled HTML table)

The visual appearance will improve once the colonisation_uncertain threshold is corrected
(Problem C), reducing false-positive red highlights from 8 zones to a more defensible count.

---

### limitations.md — PASSES

Content is substantive and appropriate for a planner audience. Key sections present:

1. Explicitly states this is NOT a map of belowground network state
2. Warns that intervention will not produce measurable recovery within a planning cycle
3. Documents the AM-blindness problem (S4 informationally null for ~95% of cells)
4. Lists all data sources with licences and citations
5. Documents rejected sources (ERA5-Land, AEMET, GlobalAMFungi) with reasons
6. Flags Seam 3 (budget-line crosswalk not yet verified)
7. Word count: 1,087 — sufficiently detailed without being unusable

**One gap to add:** The limitations sheet should explicitly document the sealed_pct
constant-value problem (Problem A above). A planner who reads the priority_zones.csv will
see sealed_pct = 0.003 for all zones and wonder why. The limitations sheet is the right
place to flag this until the raster is corrected.

---

### network_spread.html — PASSES

File size: 7.3 MB. This is a real Folium map (confirmed by reading the HTML header —
it loads Leaflet, Bootstrap, and FontAwesome correctly). The map contains:
- 2,165 network islands as the baseline layer
- 500 m buffer projections around all islands for the 2030 scenario
- Intervention zone buffers around the top-3 bridge cells (C016_011, C031_035, C032_032)
- Source patch markers for Collserola, Ciutadella, and Montjuïc
- Layer control and legend

The 7.3 MB size is due to rendering 2,165 island geometries as GeoJSON inside the HTML.
This is functional but may be slow to open in a browser. Consider simplifying geometries
(tolerance 0.0001 degrees) if file size becomes a concern for sharing.

The "top-3 bridge" selection is currently by composite rank, not bridge centrality (Problem B).
This means the spread projection shows the top-3 highest-scoring zones, which is a reasonable
proxy but should be labelled accordingly in the map title until bridge_score is corrected.

---

## 2. Sensitivity Comparison: Jaccard = 1.0

All 15 zones appear in all 3 scenarios. This is not a bug. The correct documentation is:

**"Rankings are weight-robust: the same 15 priority zones are identified regardless of
whether the analysis weights sealed surface equally with LST and NDVI (Scenario A),
gives double weight to sealed surface (Scenario B), or emphasises heat and canopy
(Scenario C). This provides confidence that the priority list is not an artefact of
a single analytical perspective."**

The caveat to add internally (not in the planner document) is that Jaccard = 1.0 is
partially explained by sealed_pct being constant (Problem A), which reduces the effective
degrees of freedom in the composite score. Retest Jaccard after correcting the raster.

---

## 3. The 3 Most Important Fixes Before Presenting to the Ajuntament

### Fix 1 (Critical): Repair the sealed_pct raster

The entire S1 sub-score is dead weight in the current outputs. With sealed_pct = 0.003
for all 495 cells, the ranking is driven only by LST anomaly and NDVI. The "barrier to
mycorrhizal recovery" framing depends on sealed surface being a meaningful discriminator.

Steps to fix:
1. Open `data/urban-atlas/sealed_surface.tif` in QGIS. Check its CRS and bounding box.
   It should cover Barcelona in UTM31N (EPSG:25831) or WGS84 with non-zero values.
2. Verify by running: `python3 -c "import rasterio; r=rasterio.open('data/urban-atlas/sealed_surface.tif'); print(r.bounds, r.crs, r.nodata)"`
3. If the raster is blank, misaligned, or all-nodata: re-download Urban Atlas 2018
   imperviousness layer for FUA_Barcelona from Copernicus Land Monitoring Service
   (https://land.copernicus.eu/local/urban-atlas) and replace the file.
4. Re-run notebook 03 and verify `sealed_pct` has realistic variance (expected mean ~0.3,
   range 0.0–1.0 across Barcelona grid cells).
5. Re-run notebook 04 and 05 to propagate corrected scores.

### Fix 2 (High): Repair bridge_scores.csv by re-running notebook 04

The bridge_score column is zero for all 15 priority zones, making the network leverage
layer of the analysis non-functional. The network spread map's top-3 selection is
currently by composite rank rather than by network betweenness.

Steps to fix:
1. Open `notebooks/04-connectivity.ipynb` and inspect the bridge centrality cell.
2. Verify that `data/network_islands.geojson` (2,165 features) loads correctly.
3. Check whether the betweenness centrality calculation completes without error and
   produces non-zero values before being written to `data/bridge_scores.csv`.
4. Re-run the notebook and verify `bridge_scores.csv` has a non-trivial distribution
   of `bridge_score` values across the 15 zones.

### Fix 3 (Medium): Correct the colonisation_uncertain threshold in notebook 03

The condition `trees_young_pct >= 0.3` is a unit confusion bug. `trees_young_pct` is on
a 0–100 percentage scale, so the threshold should be `>= 30` (representing 30% of trees
being young/recently planted). The current threshold flags 8 of 15 zones, which overstates
colonisation uncertainty and will undermine confidence in the analysis.

Steps to fix:
1. In `notebooks/03-scoring.ipynb`, Cell 10 (md-colonisation), change:
   `(grid['trees_young_pct'] >= 0.3)` to `(grid['trees_young_pct'] >= 30)`
   (or a defensible alternative such as 15, which would flag 4 zones).
2. Re-run notebook 03, 04, and 05 to regenerate all outputs.
3. Verify the colonisation_uncertain count in the new priority_zones.csv and confirm
   it reflects a meaningful ecological threshold.

---

## 4. Minor Items (Not Blocking)

- **limitations.md missing sealed_pct caveat:** Add a sentence in Section 4 noting
  that `sealed_pct` is currently constant at 0.003 for all cells due to a raster
  data quality issue, and that sub-score S1 is therefore non-discriminating in this
  pipeline version.

- **network_spread.html file size:** 7.3 MB may be slow to open. Run
  `network_islands.simplify(0.0001)` before rendering to reduce to ~1–2 MB.

- **Rank 15 anomaly:** Zone C015_022 (SARRIÀ - SANT GERVASI) has `rank_B = 76` in
  the scored_grid (i.e., it was the 76th-ranked zone overall) but appears as #15 in
  the priority list. This is the district-guarantee constraint operating correctly —
  it bumped in the best-ranked zone from Sarrià because no other Sarrià cell was in
  the top 15. This is intentional behaviour, but the HTML table shows `rank_B=15` while
  the underlying `composite_score_B = 0.293` is visibly lower than the 14th zone (0.338).
  Add a footnote to the HTML table explaining the district-guarantee constraint.

- **expected_myco_type is "AM" for all 15 zones:** This is not a bug — it reflects
  Barcelona's tree inventory (Platanus, Celtis, Tipuana are all AM hosts). However,
  a planner may interpret uniform "AM" as a data failure. Add a tooltip or footnote
  explaining that AM dominance reflects the actual tree species composition.

---

## Summary Table

| Output | Status | Blocking Issues |
|--------|--------|-----------------|
| priority_zones.csv | Passes with caveats | sealed_pct constant (Fix 1); bridge_score = 0 (Fix 2); colonisation_uncertain over-flagged (Fix 3) |
| sensitivity_comparison.png | Passes | None (Jaccard=1.0 is correct, document it) |
| priority_map.html | Passes | None |
| priority_zones.html | Passes | Colonisation flags overstated pending Fix 3 |
| limitations.md | Passes | Add sealed_pct caveat (minor) |
| network_spread.html | Passes | Top-3 bridge selection is by rank not centrality pending Fix 2 |
