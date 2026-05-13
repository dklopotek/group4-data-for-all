# Data Audit Report — Mycorrhizal Barcelona Pipeline
**Date:** 2026-05-10
**Auditor:** Data Engineer (automated Python audit via pandas 3.0.2 / geopandas 1.1.3)

---

## 1. `data/grid_trees.geojson`

### Basic shape
| Metric | Value |
|--------|-------|
| Cell count | 495 |
| CRS | EPSG:25831 (ETRS89 / UTM zone 31N) |
| Null cell_ids | 0 |
| Missing geometries | 0 |
| Invalid geometries | 0 |
| Duplicate cell_ids | 0 |

### Columns
`cell_id`, `tree_count`, `species_list`, `district_name`, `barri_name`, `dominant_myco_type`, `am_pct`, `em_pct`, `nm_pct`, `am_blindness_flag`, `trees_young_pct`, `cell_x0`, `cell_y0`, `geometry`

### dominant_myco_type distribution
| Value | Count |
|-------|-------|
| AM | 482 (97.4%) |
| NM | 13 (2.6%) |
| **EM** | **0** |

**Red flag:** EM is completely absent from `grid_trees`. However, `network_nodes.geojson` contains 9,139 EM-typed tree nodes, of which 9,031 sit inside cells that `grid_trees` classifies as AM-dominant. The root cause is that `em_pct` is identically 0.0 across all 495 cells — the EM-type signal from GBIF/FungalRoot is not being propagated into the cell-level percentage fields. See also Section 3 (network_islands carries EM) and Section 6 (cross-file inconsistency).

### tree_count per cell
| Statistic | Value |
|-----------|-------|
| Min | 1 |
| 25th pctl | 198.5 |
| Median | 385 |
| 75th pctl | 532 |
| 90th pctl | 675.4 |
| Max | 1,290 |
| Mean | 382.10 |
| **Total trees** | **189,140** |

Distribution is reasonable and right-skewed. No zeroes (every cell has at least one tree).

### am_pct / em_pct / nm_pct scale
- `am_pct` and `nm_pct` are stored as **0–100 scale** (percentage points), not 0–1 fractions. 489/495 cells have `am_pct > 1`, confirming this. Any downstream consumer expecting a 0–1 ratio will misinterpret the values.
- `em_pct` is universally 0.0 (see red flag above).

### am_blindness_flag
| Value | Count |
|-------|-------|
| True | 314 (63.4%) |
| False | 181 (36.6%) |

Among flagged cells, `am_pct` ranges 80–100 (mean 90.1), confirming the flag fires when AM dominates, signalling that the apparent AM dominance may be a data artefact rather than ecological reality. The 63% flag rate is notable — more than half the study area is marked uncertain.

### Verdict: PASS WITH WARNINGS
Geometry and IDs are clean. The `em_pct=0` across all cells is a structural pipeline gap, not corrupt data. Downstream models using `em_pct` as a feature will receive zero-variance input.

---

## 2. `data/scored_grid.geojson`

### Basic shape
| Metric | Value |
|--------|-------|
| Row count | 495 |
| CRS | EPSG:25831 |
| Null cells | 0 (all 36 non-geometry columns fully populated) |
| Duplicate cell_ids | 0 |

### Columns (36 total + geometry)
`cell_id`, `tree_count`, `species_list`, `nom_districte`, `barri_name`, `dominant_myco_type`, `am_pct`, `em_pct`, `nm_pct`, `am_blindness_flag`, `trees_young_pct`, `cell_x0`, `cell_y0`, `em_gbif_nearby`, `sealed_pct`, `s1_sealed`, `lst_anomaly_celsius`, `s2_lst`, `mean_ndvi`, `s3_ndvi`, `s4_mismatch`, `composite_A`, `rank_A`, `composite_B`, `rank_B`, `composite_C`, `rank_C`, `top15_scenario_A`, `top15_scenario_B`, `top15_scenario_C`, `sensitivity_warning`, `jaccard_AB`, `jaccard_AC`, `jaccard_BC`, `intervention_type`, `colonisation_uncertain`, `geometry`

### composite_B scores
| Statistic | Value |
|-----------|-------|
| Min | 0.0557 |
| 10th pctl | 0.1859 |
| Median | 0.2553 |
| 75th pctl | 0.2805 |
| 90th pctl | 0.2991 |
| Max | 0.4158 |
| Mean | 0.2496 |
| Nulls | 0 |

Range is narrow (0.36 spread, std ~0.05). The full composite_A/B/C ranges are:

| Score | Min | Mean | Max |
|-------|-----|------|-----|
| composite_A | 0.1621 | 0.4047 | 0.6122 |
| composite_B | 0.0557 | 0.2496 | 0.4158 |
| composite_C | 0.1591 | 0.4501 | 0.6993 |

Scenario B consistently scores lower across the board. The compression likely reflects that `s1_sealed` (a major input) has zero variance (see red flag below).

### intervention_type value counts
| Value | Count |
|-------|-------|
| planting | 320 (64.7%) |
| cooling | 174 (35.1%) |
| species-selection | 1 (0.2%) |

The single `species-selection` cell is `C023_014`, which ranks 494th out of 495 in all three scenarios — the lowest-priority cell. This is not a data error, but the extreme rarity (one cell out of 495) may indicate the branching logic for this intervention category is nearly never triggered. Worth reviewing the threshold.

### top15_scenario_B
- `top15_scenario_B=True`: exactly **15 cells** (as expected)
- Top-15 sets for scenarios A, B, and C are **100% identical** — Jaccard similarity = 1.0 for all pairs

**Red flag:** All three scenario rankings produce the exact same 15 priority cells. This indicates the sub-scores are not differentiating enough to alter ranking at the top. The immediate cause is `s1_sealed` being constant (see below), which eliminates one dimension of variation between scenarios. The stored `jaccard_AB`, `jaccard_AC`, `jaccard_BC` columns each contain the scalar value 1.0 broadcast to all 495 rows — this is a structural oddity (these should be scalar report values, not per-row columns).

### Sub-score analysis: are s1/s2/s3 synthetic or real?

| Column | Source | Real/Synthetic | Issue |
|--------|--------|----------------|-------|
| `s1_sealed` | `sealed_pct` joined from Urban Atlas | **SUSPECT** | Identically 0.003 for all 495 cells — see critical bug below |
| `s2_lst` | Landsat LST anomaly (normalised) | Real, variable | Range 0.0–1.0, continuous distribution |
| `s3_ndvi` | Sentinel-2 NDVI (normalised) | Real, variable | Range 0.0–1.0, continuous distribution |
| `s4_mismatch` | AM blindness heuristic | Heuristic | 489 cells = 0.5, 6 cells = 0.6; near-constant |

**Critical bug — `sealed_pct` / `s1_sealed`:**
- `sealed_per_cell.csv` contains `sealed_pct ≈ 0.3` uniformly (confirmed below, Section 5)
- `scored_grid.geojson` carries `sealed_pct = 0.003` for every cell (100× smaller)
- `s1_sealed` is a direct copy of `sealed_pct` — also identically 0.003
- This is a unit conversion error: the source value 0.3 (dimensionless fraction, i.e. 30%) was divided by 100 somewhere in the pipeline, producing 0.003 (i.e. 0.3%)
- Because `s1_sealed` has zero variance, it contributes nothing to cross-cell differentiation in composite scores

### Other fields
- `lst_anomaly_celsius`: range −9.04 to +7.92°C, mean −0.15°C. Valid range for a thermal anomaly.
- `mean_ndvi`: range −0.027 to +0.364. Slightly negative values are possible for impervious surfaces; range is physically plausible.
- `em_gbif_nearby`: **identically 0 for all 495 cells**. No EM GBIF records are being picked up near any cell. This may reflect a missing spatial join step or empty GBIF query results for the study area.
- `sensitivity_warning`: same string in all 495 rows ("Rankings are weight-robust — Scenario B recommended as primary"). This is a report label, not a per-cell flag; storing it as a repeated string column adds no information and wastes space.
- `colonisation_uncertain`: 8 cells = True, 487 = False.

### Verdict: NEEDS REPROCESSING
The `sealed_pct`/`s1_sealed` bug is critical — fix the unit conversion (multiply by 100 or divide the source by 100 depending on which end is wrong), then rerun composite scoring. The `em_gbif_nearby=0` everywhere may be a second upstream issue to verify.

---

## 3. `data/network_islands.geojson`

### Basic shape
| Metric | Value |
|--------|-------|
| Island count | 2,165 |
| CRS | EPSG:25831 |
| Missing geometries | 0 |
| Duplicate component_ids | 0 |
| Nulls | 0 (all columns) |

### Columns
`component_id`, `node_count`, `dominant_myco_type`, `districts_spanned`, `district_names`, `centroid_x`, `centroid_y`, `geometry`

### node_count distribution
| Statistic | Value |
|-----------|-------|
| Min | 1 |
| Mean | 16.25 |
| Max | 1,557 |

The distribution is extremely right-skewed. A few large islands dominate:

| node_count | Count of islands |
|------------|-----------------|
| 1 | 583 (26.9%) |
| 2 | 312 (14.4%) |
| 3 | 194 (9.0%) |
| 4–10 | 424 (19.6%) |
| 11–50 | 403 (18.6%) |
| 51–200 | 121 (5.6%) |
| 201–500 | 25 (1.2%) |
| 501–1,000 | 13 (0.6%) |
| > 1,000 | 3 (0.14%): sizes 1,218 / 1,557 |

The three giant islands (888, 1,218, 1,557 nodes) are likely the main connected components spanning much of the city. The 583 singletons (node_count=1) represent isolated trees with no network neighbours — this is ecologically meaningful but worth confirming they are intentional rather than artefacts of a spatial threshold.

### dominant_myco_type breakdown
| Value | Count |
|-------|-------|
| AM | 1,248 (57.6%) |
| EM | 917 (42.4%) |

**Inconsistency with grid_trees:** `network_islands` shows 42% EM-dominant islands, while `grid_trees` shows 0% EM-dominant cells. The EM signal exists at the tree/node level (9,139 EM nodes in `network_nodes`) but is not reflected back into `grid_trees`'s per-cell percentages. The two files describe the same underlying trees but disagree on EM presence — this is a lineage break between the two computation paths.

### Verdict: PASS (file is internally consistent)
The file is clean. The EM inconsistency is inherited from the `grid_trees` pipeline gap, not an error in this file itself.

---

## 4. `data/bridge_scores.csv`

### Shape and dtypes
- **15 rows × 6 columns** (one row per top-15 priority cell)

| Column | dtype | Notes |
|--------|-------|-------|
| `cell_id` | str | No nulls |
| `bridge_score` | int64 | **All values = 0** — critical flag |
| `leverage_rank` | int64 | 1–15, sequential |
| `composite_B` | float64 | Range 0.063–0.416 |
| `nom_districte` | str | **Encoding corruption** — UTF-8 accent chars display as replacement characters |
| `intervention_type` | str | planting (9), cooling (6) |

**Critical flag — `bridge_score = 0` for all 15 rows:**
The `bridge_score` column is supposed to measure a cell's network bridging value (how many isolated mycorrhizal islands it connects). Every cell scores 0. This could mean: (a) the bridging calculation was never run or returned empty results; (b) all top-15 cells happen to be internal network nodes with no bridging capacity; or (c) a logic error set the field to a default of 0. Given that this is a key output metric, this needs to be investigated and almost certainly reprocessed.

**Encoding issue:**
District names with Catalan/Spanish accents are corrupted. Examples:
- `SARRIÀ - SANT GERVASI` appears as `SARRI� - SANT GERVASI`
- `SANTS - MONTJUÏC` appears as `SANTS - MONTJU�C`
- `GRÀCIA` appears as `GR�CIA`

The file was likely written with UTF-8 encoding but is being read as ASCII, or it was written with an incorrect codec. This is a display/portability issue — the underlying cell_id joins are unaffected — but the file should be rewritten with explicit UTF-8 encoding. Note: the same corruption exists in `scored_grid.geojson` and `grid_trees.geojson` for the same district name columns.

### Verdict: NEEDS REPROCESSING
The `bridge_score=0` column is the primary concern. Encoding should also be fixed.

---

## 5. `data/urban-atlas/sealed_per_cell.csv`

### Shape
- **495 rows × 2 columns**: `cell_id`, `sealed_pct`

### sealed_pct distribution
| Statistic | Value |
|-----------|-------|
| Min | 0.300 |
| 10th pctl | 0.300 |
| Median | 0.300 |
| 75th pctl | 0.300 |
| Max | 0.300 |
| Nulls | 0 |
| Values > 100 | 0 |
| Values < 0 | 0 |

**Red flag — near-uniform value of 0.3:**
All 495 cells report `sealed_pct ≈ 0.3` (three floating-point representations of the same value: 0.2999…, 0.3, 0.3000…0001 — these are the same number at machine precision, not genuinely different values).

Barcelona is a dense Mediterranean city where sealed surface fractions vary significantly by district (typically 30–90%). A uniform 30% for every cell across 10 districts is physically implausible and indicates the Urban Atlas raster zonal statistics either: (a) failed to run correctly and returned a fallback/default value; (b) were run against the wrong raster layer; or (c) only sampled a single reference area and broadcast it to all cells.

This is the upstream source of the `s1_sealed=0.003` bug in `scored_grid.geojson`: the value 0.3 from this file was divided by 100 somewhere in the pipeline, producing 0.003.

### Verdict: NEEDS REPROCESSING
The `sealed_per_cell.csv` file must be regenerated by re-running the Urban Atlas zonal statistics against the actual Barcelona grid. The uniform output of 0.3 is a failed computation, not real data.

---

## Cross-File Consistency Issues

| Issue | Files Affected | Severity |
|-------|---------------|----------|
| `em_pct=0` in all grid cells but 9,139 EM nodes exist in network | `grid_trees.geojson`, `network_nodes.geojson`, `network_islands.geojson` | High |
| `sealed_pct` uniform 0.3 in source CSV → propagated as 0.003 into scored_grid | `sealed_per_cell.csv`, `scored_grid.geojson` | Critical |
| `bridge_score=0` for all 15 top-priority cells | `bridge_scores.csv` | Critical |
| `em_gbif_nearby=0` for all 495 cells | `scored_grid.geojson` | High |
| All three scenario top-15 sets are identical (Jaccard=1.0) | `scored_grid.geojson` | High (consequence of s1_sealed=constant) |
| `jaccard_*` stored as per-row broadcast values instead of scalar | `scored_grid.geojson` | Low (schema smell) |
| `sensitivity_warning` is same string for all 495 rows | `scored_grid.geojson` | Low (schema smell) |
| District names with accents encoded incorrectly | `grid_trees.geojson`, `scored_grid.geojson`, `bridge_scores.csv` | Low (display only) |
| `am_pct`/`nm_pct` stored as 0–100 (percentage) vs `s1_sealed` in 0–1 (fraction) | `grid_trees.geojson`, `scored_grid.geojson` | Medium (consumer confusion) |

---

## Verdict Summary

| File | Status | Action Required |
|------|--------|----------------|
| `grid_trees.geojson` | Pass with warnings | Fix EM propagation into `em_pct`; confirm `am_pct`/`nm_pct` scale is intentional |
| `scored_grid.geojson` | Needs reprocessing | Fix `sealed_pct` unit bug; rerun composite scoring; investigate `em_gbif_nearby` |
| `network_islands.geojson` | Pass | No action (internally consistent; EM lineage gap is upstream) |
| `bridge_scores.csv` | Needs reprocessing | Rerun bridge score calculation; fix UTF-8 encoding |
| `sealed_per_cell.csv` | Needs reprocessing | Rerun Urban Atlas zonal statistics; result must show variation across cells |

### Minimum reprocessing sequence to unblock the pipeline
1. Rerun `process_urban_atlas.py` and verify `sealed_per_cell.csv` shows a distribution of values (not uniform 0.3)
2. Fix the 100× unit conversion bug before joining `sealed_pct` into `scored_grid`
3. Investigate why `em_pct` is 0 in `grid_trees` — check the FungalRoot/GBIF join step
4. Rerun composite scoring to produce `scored_grid.geojson` with corrected inputs
5. Rerun bridge score calculation to populate `bridge_scores.csv`
6. Re-export all CSVs and GeoJSONs with explicit UTF-8 encoding
