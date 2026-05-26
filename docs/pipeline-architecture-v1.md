# Pipeline Architecture v1 — Mycorrhizal Barcelona

> **Document type:** Architecture decision record (pipeline-level)
> **Status:** ACCEPTED
> **Date:** 2026-05-26
> **Deciders:** Rafik, Claude
> **CRISP-DM Phase:** 3 (Data Preparation + Modeling)

## What changed since v0

v0 (`docs/system-sketch-v0.md`) drew boxes with verbs -- "Aggregate trees per 400m cell," "Join species -> mycorrhizal type" -- but no file paths, no function signatures, no failure modes. It was an aspiration diagram with 12 processing boxes and 8 data sources, all at uniform resolution.

v1 replaces those boxes with **implemented components** whose locations are known:

| v0 box | v1 equivalent | Where it lives |
|--------|---------------|----------------|
| P1 (Aggregate trees per 400m cell) | `build_grid` + `spatial_join_trees_to_grid` | `notebooks/02-grid-trees.ipynb` |
| P2 (Join species -> mycorrhizal type) | `normalize_species_names` + `join_fungalroot` | `notebooks/02-grid-trees.ipynb` |
| P3 (Expected type per cell) | `compute_tree_statistics` | `notebooks/02-grid-trees.ipynb` |
| P4 (GBIF spatial query) | N/A -- folded into S4 mismatch cell | `notebooks/03-scoring.ipynb` |
| P5 (Confirmation gap) | `compute_sub_scores` (S4 logic) | `notebooks/03-scoring.ipynb` |
| P6 (Sealed surface) | `zonal_stats_sealed` | `notebooks/03-scoring.ipynb` |
| P7 (LST anomaly) | `zonal_stats_lst` | `notebooks/03-scoring.ipynb` |
| P8 (NDVI) | `zonal_stats_ndvi` | `notebooks/03-scoring.ipynb` |
| P9 (Composite) | `compute_composite_scores` | `notebooks/03-scoring.ipynb` |
| P10 (Intervention type) | `classify_intervention` | `notebooks/03-scoring.ipynb` |
| P11 (Top-15 rank) | `select_top15_with_district_constraint` | `notebooks/03-scoring.ipynb` |
| P12 (Reference patch) | REMOVED -- peri-urban reference computation deferred to Phase 6 | N/A |

**Key structural changes from v0:**
1. **`src/clean_data.py` now exists** as the refactored pipeline. The diagram below uses `src/clean_data.py` paths; the notebooks (`notebooks/02-grid-trees.ipynb`, `notebooks/03-scoring.ipynb`, `notebooks/02-data-cleaning.ipynb`) remain the original exploratory implementations.
2. **Spread simulation is dead** (ADR-005). v0's P12 spread-modeling aspiration is replaced by a static 500m buffer.
3. **AM graph is demonstration-only** (ADR-004). v0 assumed full-city network analysis; v1 documents the SANT MARTÍ limitation.
4. **All bridge scores are zero** -- the network model has no inter-component bridging parameterised correctly. v0 did not anticipate this.
5. **Three weight scenarios, not one.** v0 described a single composite; v1 carries three scenarios + Jaccard sensitivity check (ADR-003).

---

## The diagram

```mermaid
flowchart LR
    subgraph raw [Raw Data]
        R1[arbrat-viari.csv]
        R2[arbrat-zona.csv]
        R3[fungalroot.csv]
        R4[gbif-fungi.json]
        R5[Urban Atlas · sealed_surface.tif]
        R6[Landsat · lst_summer_composite.tif]
        R7[Sentinel-2 · ndvi_summer_composite.tif]
        R8[bcn-boundary.geojson]
    end

    subgraph clean [Phase 3 · Cleaning + Scoring — notebooks/02 + 03]
        C1[normalize_species_names<br/>notebooks/02-grid-trees.ipynb]
        C2[join_fungalroot<br/>notebooks/02-grid-trees.ipynb]
        C3[assign_myco_type<br/>notebooks/02-grid-trees.ipynb]
        C4[build_grid<br/>notebooks/02-grid-trees.ipynb]
        C5[spatial_join_trees_to_grid<br/>notebooks/02-grid-trees.ipynb]
        C6[compute_tree_statistics<br/>notebooks/02-grid-trees.ipynb]
        C7[zonal_stats_sealed<br/>notebooks/03-scoring.ipynb]
        C8[zonal_stats_lst<br/>notebooks/03-scoring.ipynb]
        C9[zonal_stats_ndvi<br/>notebooks/03-scoring.ipynb]
        C10[compute_sub_scores<br/>notebooks/03-scoring.ipynb]
        C10b[compute_platanus_replacement_priority<br/>src/clean_data.py — Stage 11]
        C11[compute_composite_scores<br/>notebooks/03-scoring.ipynb]
        C12[classify_intervention + replacement_priority gate<br/>notebooks/03-scoring.ipynb]
    end

    subgraph processed [Processed — data/]
        P1[scored_grid.geojson]
        P2[(scored_grid.parquet — planned Phase 4)]
    end

    subgraph connectivity [Phase 3 · Connectivity — notebooks/04]
        N1[build_subgraph (AM demo · EM full)<br/>notebooks/04-connectivity.ipynb]
        N2[compute_components<br/>notebooks/04-connectivity.ipynb]
        N3[bridge_score_for_zone<br/>notebooks/04-connectivity.ipynb]
        N4[simulate_spread — DEPRECATED<br/>notebooks/04-connectivity.ipynb]
    end

    subgraph future [Future · Phase 4-7]
        F1["Baseline model / scenario analysis<br/>(planned · Session 4)"]
        F2["Evaluation + failure gallery<br/>(planned · Session 5-6)"]
        F3["Priority map + intervention brief<br/>(planned · Session 7)"]
    end

    R1 --> C1
    R2 --> C1
    R3 --> C2
    C1 --> C2 --> C3
    R8 --> C4
    C3 --> C5
    C4 --> C5
    C5 --> C6
    R5 --> C7
    R6 --> C8
    R7 --> C9
    C6 --> C10
    C7 --> C10
    C8 --> C10
    C9 --> C10
    C10 --> C10b --> C11 --> C12
    C6 --> C10b
    C12 --> P1
    P1 --> N1 --> N2 --> N3
    N4 -.->|DEPRECATED| N2
    P1 --> P2
    P2 --> F1 --> F2 --> F3
```

---

## Components -- implemented (Phase 3)

### C1: `normalize_species_names`

| Property | Value |
|----------|-------|
| **File** | `notebooks/02-grid-trees.ipynb` -- Cell 3 (load_trees) + Cell 9 (species check) |
| **Input contract** | `data/arbrat-viari.csv` (145,478 street trees), `data/arbrat-zona.csv` (43,612 park trees). Expected columns: `codi`, `x_etrs89`, `y_etrs89`, `cat_nom_cientific`, `nom_districte`, `nom_barri`, `data_plantacio`. |
| **Output contract** | `pd.DataFrame` with 189,090 rows, 23 columns. Species names in `cat_nom_cientific` standardised to UTF-8. Genus-only entries (25 `Washingtonia sp`) detected and flagged but not dropped. |
| **Failure mode** | CSV missing or corrupt -> `SystemExit` with download instructions (Cell 2 guard). `cat_nom_cientific` column absent -> KeyError on `map()`. |
| **Tests / assertions** | Cell 2: file existence guard. Cell 8: `is_genus_only()` check -- 0.01% genus-only rate. Cell 7: `nunique()` on species column = 381. |
| **Cleaning log entry** | Street/park tagged with `source` column. `x_etrs89`/`y_etrs89` validated as EPSG:25831-native. `data_plantacio` parsed with `coerce` errors -> 81.0% null. |

### C2: `join_fungalroot`

| Property | Value |
|----------|-------|
| **File** | `notebooks/02-grid-trees.ipynb` -- Cell 5 (P5) |
| **Function** | `_normalise_myco(v)` -- collapses FungalRoot compound strings ("EcM, AM undetermined", "EcM, no AM colonization") into `{AM, EM, NM}` vocabulary. |
| **Input contract** | `data/fungalroot.csv` (or hardcoded `TOP20_MYCO` stub if CSV absent). FungalRoot CSV: 13,756 species mappings after normalisation. |
| **Output contract** | `myco_map`: `dict[str, str]` mapping species name to `"AM"`, `"EM"`, or `"NM"`. Top-20 species stub overrides CSV for safety (BUG-2 fix). |
| **Failure mode** | CSV exists but unexpected columns -> fallback to position-based column selection (`fr.columns[0]`, `fr.columns[1]`). No FungalRoot at all -> hardcoded stub covers only top-20 species. |
| **Tests / assertions** | Cell 5 coverage print: 86.7% of tree-rows assigned a myco type. Counter: 151,801 AM / 12,175 EM / 25,164 NM. |
| **Cleaning log entry** | 45,272 trees (24%) remain unassigned (species not in MYCO_LOOKUP top-20). These carry `NM` label -- they are counted in `tree_count` but excluded from myco-type fractions. Documented in limitations. |

### C3: `assign_myco_type`

| Property | Value |
|----------|-------|
| **File** | `notebooks/02-grid-trees.ipynb` -- Cell 5 (P5, continuation) |
| **Operation** | `joined["myco_type"] = joined["cat_nom_cientific"].map(myco_map).fillna("NM")` |
| **Input contract** | `joined` DataFrame (trees + grid cell_id via spatial join) + `myco_map` from C2. |
| **Output contract** | `joined` enriched with `myco_type` column. Every tree-row has a value in `{AM, EM, NM}`. NM includes both genuinely non-mycorrhizal species (Cupressus, Robinia) and unassigned species. |
| **Failure mode** | `map()` silently returns NaN for unmapped keys -> `.fillna("NM")` catches them. No breakage possible. |
| **Tests / assertions** | Cell 5: `(joined["myco_type"] != "NM").sum() / len(joined)` = 86.7% coverage. |
| **Cleaning log entry** | 13.3% of trees assigned NM by default (not in lookup). This is honest -- no species-level guesswork. |

### C4: `build_grid`

| Property | Value |
|----------|-------|
| **File** | `notebooks/02-grid-trees.ipynb` -- Cell 3 (P1) |
| **Function** | Inline: `math.floor/ceil` snap to 400m multiples. `shapely.geometry.box` tile generation. |
| **Input contract** | `data/bcn-boundary.geojson` in EPSG:25831. Boundary polygon must be a valid single/multi polygon. |
| **Output contract** | `grid`: `gpd.GeoDataFrame` with 772 cells intersecting BCN boundary. Columns: `cell_id` (e.g., `C016_011`), `cell_x0`, `cell_y0`, `geometry`. CRS: EPSG:25831. Grid envelope: X [420,800 -- 435,600], Y [4,574,000 -- 4,591,200]. 37 cols x 43 rows = 1,591 raw tiles before intersection. |
| **Failure mode** | Boundary file missing -> `SystemExit` in Cell 2 guard. Boundary in wrong CRS -> `to_crs()` in Cell 3 handles reprojection. Boundary is empty -> `bcn_poly.bounds` returns NaN -> `math.floor` errors on NaN. |
| **Tests / assertions** | Cell 3: `len(grid)` = 772 intersecting tiles. Boundary bounds printed for visual inspection. Grid origin snapped to 400m multiples -- deterministic across runs. |
| **Cleaning log entry** | Grid alignment: origin at (420800, 4574000) in EPSG:25831. See ADR-002 for integration-resolution rationale. MAUP sensitivity documented in `phase-2/geospatial-declarations.md`. |

### C5: `spatial_join_trees_to_grid`

| Property | Value |
|----------|-------|
| **File** | `notebooks/02-grid-trees.ipynb` -- Cell 5 (P3) |
| **Operation** | `gpd.sjoin(trees, grid[["cell_id", "geometry"]], how="inner", predicate="within")` |
| **Input contract** | `trees`: gpd.GeoDataFrame with Point geometry in EPSG:25831. `grid`: gpd.GeoDataFrame with Polygon geometry in EPSG:25831 (from C4). |
| **Output contract** | `joined`: 189,140 tree-rows matched to 495 occupied cells. 80 trees (0.04%) unassigned (boundary-edge points not strictly "within" any cell). |
| **Failure mode** | CRS mismatch between trees and grid -> `sjoin` may produce empty result. CRS is enforced to EPSG:25831 for both. |
| **Tests / assertions** | Cell 5: `matched/total*100` = 99.96% matched. `joined['cell_id'].nunique()` = 495 occupied cells. |
| **Cleaning log entry** | 80 boundary-edge trees dropped. Acceptable loss (<0.1%). |

### C6: `compute_tree_statistics`

| Property | Value |
|----------|-------|
| **File** | `notebooks/02-grid-trees.ipynb` -- Cell 6 (P4) + Cell 7 (P6) + Cell 8 (P7) |
| **Functions** | `modal()`, `species_list_json()`, `young_pct()`, `myco_fractions()` |
| **Input contract** | `joined` from C5 (189,140 tree-rows with cell_id, myco_type, species, plant_date). |
| **Output contract** | Per-cell aggregates: `tree_count`, `species_list` (JSON string), `district_name`, `barri_name`, `trees_young_pct`, `am_pct`, `em_pct`, `nm_pct`, `dominant_myco_type` (AM/EM/NM), `am_blindness_flag`. |
| **Failure mode** | Empty group -> `modal()` returns "UNKNOWN". `young_pct()` returns 0.0 for zero-length series. `myco_fractions()` AM/EM/NM all 0 if group empty. |
| **Tests / assertions** | Cell 9: fraction-sum max deviation from 100% = 0.01 (rounding). Cell 10 summary: mean 382.1 trees/cell, 263 AM-blind cells (53.1%). |
| **Cleaning log entry** | `am_blindness_flag` = True when `am_pct >= 80`. 263 cells flagged. `dominant_myco_type` distribution: 460 AM, 18 NM, 17 EM. `expected_myco_type` (aliased in data contract) = `dominant_myco_type` renamed for clarity. |

### C7: `zonal_stats_sealed`

| Property | Value |
|----------|-------|
| **File** | `notebooks/03-scoring.ipynb` -- Cell 2 (S1) |
| **Function** | `zonal_mean_from_raster(raster_path, gdf, band=1, scale=1.0)` |
| **Input contract** | `data/urban-atlas/sealed_surface.tif` (EPSG:25831, 10m resolution, values 0-1). Grid cells from `data/grid_trees.geojson` (loaded in Cell 1). |
| **Output contract** | `grid["sealed_pct"]`: per-cell mean sealed fraction (0-1). Range: [0.024, 0.894], mean: 0.646. NaN cells filled with 0.0. |
| **Failure mode** | Raster absent -> synthetic Beta(2,5) fallback with warning. Raster CRS mismatch -> auto-reproject in `zonal_mean_from_raster`. Cell outside raster extent -> NaN -> filled 0.0. |
| **Tests / assertions** | Cell 2: prints min/mean/max. `USE_SYNTHETIC_SEALED` = False when real raster available. |
| **Cleaning log entry** | Urban Atlas raster CRS verified: EPSG:25831. Scale confirmed: 0-1 (not 0-100 -- BUG-3 fix verified). |

### C8: `zonal_stats_lst`

| Property | Value |
|----------|-------|
| **File** | `notebooks/03-scoring.ipynb` -- Cell 3 (S2) |
| **Function** | `zonal_mean_from_raster(raster_path, gdf, band=1)` |
| **Input contract** | `data/landsat/lst_summer_composite.tif` (summer composite, Landsat 8/9 Band 10 thermal, native 100m resampled to 30m). |
| **Output contract** | `grid["lst_anomaly_celsius"]`: per-cell LST anomaly from city-wide median. Range: [-9.04, +7.92] degrees C. Anomaly normalised to `s2_lst` [0,1] via min-max scaling. |
| **Failure mode** | Raster absent -> synthetic N(0, 2.5) fallback. All cells NaN -> city_median NaN -> all anomalies 0 -> denom = 0 -> `lst_score` = 0.5 for all cells. |
| **Tests / assertions** | Cell 3: prints city_min/city_max, S2 mean/std. `USE_SYNTHETIC_LST` = False when real raster available. |
| **Cleaning log entry** | Landsat QA band not independently verified (data contract limitation). Z-score relative to city mean, not absolute temperature threshold. |

### C9: `zonal_stats_ndvi`

| Property | Value |
|----------|-------|
| **File** | `notebooks/03-scoring.ipynb` -- Cell 4 (S3) |
| **Function** | `zonal_mean_from_raster(raster_path, gdf, band=1)` |
| **Input contract** | `data/sentinel2/ndvi_summer_composite.tif` (Sentinel-2 L2A summer composite, 10m resolution, NDVI float32). |
| **Output contract** | `grid["mean_ndvi"]`: per-cell mean summer NDVI. Range: [-0.027, 0.364]. NaN filled with 0.3. Inverted to `s3_ndvi` = `1 - normalised_ndvi`, clipped [0,1]. |
| **Failure mode** | Raster absent -> synthetic Beta(3,3) rescaled to [0.1, 0.7] fallback. All cells NaN -> `mean_ndvi` = 0.3 constant -> `ndvi_range` = 0 -> `normalised_ndvi` = 0.5. |
| **Tests / assertions** | Cell 4: prints NDVI range, S3 mean/std. `USE_SYNTHETIC_NDVI` = False when real raster available. |
| **Cleaning log entry** | Sentinel-2 cloud mask not independently verified (data contract limitation). Negative NDVI values (-0.027) suggest water/shadows in some cells. |

### C10: `compute_sub_scores`

| Property | Value |
|----------|-------|
| **File** | `notebooks/03-scoring.ipynb` -- Cell 5 (S4) |
| **Function** | `compute_mismatch_score(am_pct, em_pct, em_gbif_nearby)` |
| **Input contract** | `grid` with columns: `am_pct` (0-100 scale), `em_pct` (0-100 scale), `em_gbif_nearby` (0/1 flag from notebook 02 -- NOTE: currently hardcoded to 0, see seam). |
| **Output contract** | `grid["s4_mismatch"]`: categorical scores -- 0.0 (EM confirmed), 0.5 (AM-dominant, informationally null), 0.6 (mixed), 0.8 (EM unconfirmed). Distribution: 263 cells score 0.5, 216 score 0.6, 16 score 0.8. |
| **Failure mode** | `am_pct`/`em_pct` on wrong scale (0-1 vs 0-100) -> BUG-4 fix ensures 0-100. `em_gbif_nearby` column missing -> default 0. All cells AM-dominant -> all score 0.5 -> S4 is constant. |
| **Tests / assertions** | Cell 5: `value_counts().sort_index()` -- 3 distinct scores present. AM-dominant count = 263 matches notebook 02. |
| **Cleaning log entry** | S4 mismatch sub-score is **informationally null for 53.1% of cells** (all AM-dominant cells). The 0.5 value is a categorical flag, not a measured barrier. This is the AM-blindness limit in operational form. |

### C10b: `compute_platanus_replacement_priority` (NEW · v1.1)

| Property | Value |
|----------|-------|
| **File** | `src/clean_data.py` -- pipeline stage 11 |
| **Function** | `compute_platanus_replacement_priority(gdf)` |
| **Input contract** | `gdf` with `n_platanus`, `tree_count`, `n_AM`, `n_EM`, `am_pct`, `s3_inverted_ndvi`, `s1_sealed`. Constants: `PRPI_WEIGHTS` (platanus 0.40, ndvi 0.20, s4_shift 0.20, feasibility 0.20), `PRPI_THRESHOLD = 0.5`, `SEAL_FEASIBILITY = 0.7`, `S4_SHIFT_ASSUMPTION = "EM"`, `PLATANUS_TARGET_PCT = 12.0` (city 2037 target). |
| **Output contract** | Six new columns: `platanus_pct` (0-100), `s4_shift_potential` (0-1, drop in AM% under EM replacement assumption), `s4_shift_ceiling_reached` (bool — cell stays >= 80% AM after replacement), `prpi` (0-1 weighted index). Observed range on 2026-05-26 run: PRPI [0.151, 0.832], mean 0.314. 165 cells (33%) hit the AM-blindness ceiling. 15 cells satisfy the strict `replacement_priority` gate. |
| **Failure mode** | `tree_count == 0` -> `platanus_pct` falls back to 0 via `replace(0, NaN).fillna(0)`. `S4_SHIFT_ASSUMPTION = "AM"` collapses `s4_shift_potential` to 0 everywhere -> PRPI degrades to pollen + canopy + feasibility. `n_platanus > n_AM` cannot happen (Platanus is in `TOP20_MYCO` as `AM`) but clip-at-zero guards anyway. |
| **Tests / assertions** | In-function: PRPI weights sum to 1.0; `prpi` in [0, 1]; `platanus_pct` in [0, 100]. In `assert_clean_invariants`: extended with `prpi`, `platanus_pct`, `s4_shift_potential` range checks and `n_platanus` non-negative-integer check. Inventory baseline check at runtime: `n_platanus.sum()` ≈ 42,820 / 42,828 (0.02% drop from spatial-join boundary edge, consistent). |
| **Policy anchor** | Pla Director de l'Arbrat de Barcelona 2017-2037 (Ajuntament de Barcelona, 2017): reduce *Platanus × acerifolia* from 27% to <12% of street-tree canopy by 2037. PRPI gives the city's ~1,500 trees/year replacement budget a defensible spatial allocation against the ~8,000/year pace needed. |

### C11: `compute_composite_scores`

| Property | Value |
|----------|-------|
| **File** | `notebooks/03-scoring.ipynb` -- Cells 6, 7, 8 |
| **Functions** | `select_top15_with_district_constraint(grid, composite_col, district_col, k=15)`, `jaccard(set_a, set_b)` |
| **Input contract** | `grid` with columns `s1_sealed`, `s2_lst`, `s3_ndvi`, `s4_mismatch`. |
| **Output contract** | Three composite columns now 5-term (v1.1): `composite_A` (range [0.117, 0.746]), `composite_B` ([0.119, 0.787]), `composite_C` ([0.117, 0.754]). Scenario B weights rebalanced from `{s1: 0.55, s2: 0.20, s3: 0.20, s4: 0.05}` to `{s1: 0.45, s2: 0.20, s3: 0.15, s4: 0.05, prpi: 0.15}`. Three `top15_scenario_*` boolean flags. District-representation constraint enforced: all 10 districts represented in each top-15. `sensitivity_warning` text written to every row. |
| **Failure mode** | Weights do not sum to 1.0 -> `assert` fails hard (good -- catches config errors). Less than k districts in dataset -> `select_top15_with_district_constraint` grows set beyond k. `district_name` vs `nom_districte` column naming mismatch -> auto-rename fallback in Cell 7. |
| **Tests / assertions** | Cell 6: `abs(total_w - 1.0) < 1e-6` for all 3 scenarios. Cell 7: top-15 district uniqueness printed. Cell 8: Jaccard < 0.5 triggers `SENSITIVITY_WARNING`. |
| **Cleaning log entry** | BUG-6 fix applied: district constraint now correctly adds one cell per missing district (previous version only added the last missing district). Weight-sensitive recommendation: present all 3 scenarios. Scenario B (sealed-dominant, S1=0.55) is primary per ADR-003. |

### C12: `classify_intervention`

| Property | Value |
|----------|-------|
| **File** | `notebooks/03-scoring.ipynb` -- Cell 9 |
| **Functions** | `_intervention_profile(row)`, `_profile_str(p)`. |
| **Input contract** | `grid` with `s1_sealed`, `s2_lst`, `s3_ndvi`, `s4_mismatch` + Scenario B weights. |
| **Output contract** | `intervention_type`: dominant label in `{de-paving, cooling, planting, multi-strategy, species-replacement}` (v1.1 extended). `intervention_profile`: dict of percentage contributions across all 5 sub-scores. `replacement_priority`: bool flag with strict gate — PRPI > 0.5 AND s4_shift_potential > 0 AND s1_sealed < 0.7 (independent of dominance). Observed 2026-05-26 distribution: 459 de-paving / 25 cooling / 7 planting / 3 species-replacement / 1 multi-strategy. 15 cells flagged `replacement_priority`. |
| **Failure mode** | All sub-scores zero -> total=0 -> every label gets 0.0 -> `max()` on zero dict picks first key arbitrarily. |
| **Tests / assertions** | Cell 9: top-15 Scenario B all labelled `de-paving` (profile str shows 52-65% de-paving contribution). |
| **Cleaning log entry** | Single-label intervention deprecated in favour of profile vector (Fix 3, 2026-05-10, per geographer's review). Top-15 cells under Scenario B all de-paving because sealed surface dominates the composite weight (S1=0.55). |

### Connectivity subgraph (also Phase 3)

These components live in `notebooks/04-connectivity.ipynb` and produce the network outputs. They are **supplementary** to the scoring pipeline -- the `scored_grid.geojson` contract does not depend on them.

#### N1: `build_subgraph`

| Property | Value |
|----------|-------|
| **File** | `notebooks/04-connectivity.ipynb` -- Cell 4 |
| **Function** | `build_subgraph(trees_subset, myco_type, distance_m, seal_threshold=0.7)` |
| **Input contract** | Tree GeoDataFrame from `load_tree_inventory()` + `load_grid_with_sealing()`. MYCO_LOOKUP: 20 species, 17 AM, 3 EM. |
| **Output contract** | Combined NetworkX graph `G`: 35,177 nodes, 54,357 edges. EM subgraph (all districts): 9,139 nodes, 41,347 edges. AM subgraph (SANT MARTI only): 26,038 nodes, 13,010 edges. Edge rules: AM-AM <=15m, EM-EM <=35m, no AM-EM edges. Both endpoints must have `sealed_pct < 0.7`. |
| **Failure mode** | Empty subset -> returns `(nx.Graph(), [])`. `sealed_pct` column absent -> KeyError. Non-EPSG:25831 coordinates -> KDTree distances in degrees (incorrect). |
| **Tests / assertions** | Cell 4: edge count printed. `G.number_of_nodes()` = 35,177. |
| **Cleaning log entry** | **AM graph covers only SANT MARTI district** (ADR-004). Full-city AM graph would require ~9.1B potential edge evaluations. ER graph runs city-wide. |

#### N2: `compute_components`

| Property | Value |
|----------|-------|
| **File** | `notebooks/04-connectivity.ipynb` -- Cell 5 |
| **Operation** | `list(nx.connected_components(G))` |
| **Input contract** | NetworkX graph `G` from N1. |
| **Output contract** | `network_islands.geojson`: 25,508 connected components. Largest island: 552 nodes (AM, SANT MARTI). `network_nodes.geojson`: 35,177 nodes with component_id, myco_type, district. `network_edges.geojson`: 5,344 edges for top-5 islands. |
| **Failure mode** | Empty graph -> 0 components. Singletons dominate (25,508 components for 35,177 nodes = mostly isolated trees). |
| **Tests / assertions** | Cell 5: top-10 components printed. All spanned districts = 1 (no cross-district islands). |
| **Cleaning log entry** | Combined graph statistics reflect SANT MARTI AM limitation. Non-Sant Marti district AM trees are missing from component analysis. |

#### N3: `bridge_score_for_zone`

| Property | Value |
|----------|-------|
| **File** | `notebooks/04-connectivity.ipynb` -- Cell 6 |
| **Function** | `bridge_score_for_zone(zone_cell_id, trees_gdf, node_to_comp, G)` |
| **Input contract** | Top-15 cell IDs from `scored_grid.geojson`, tree graph from N1. |
| **Output contract** | `bridge_scores.csv`: per-zone bridge_score. **ALL scores = 0** for all 15 priority zones. See open seams below. |
| **Failure mode** | Zone cell_id not in grid -> returns 0. No blocked trees in zone -> returns 0. |
| **Tests / assertions** | Cell 6: bridge scores printed for all 15 zones. |
| **Cleaning log entry** | BUG-7 fix applied (distinct component pairs, not raw edge count). All scores = 0 because (a) AM graph covers only SANT MARTI, (b) even within SANT MARTI, the 15m/35m thresholds + 0.7 sealed barrier produce no bridging. |

#### N4: `simulate_spread` (DEPRECATED)

| Property | Value |
|----------|-------|
| **File** | `notebooks/04-connectivity.ipynb` -- Cell 7 |
| **Function** | `simulate_spread(trees_gdf, source_nodes, G, n_seasons=5, spread_m_per_season=2.0)` |
| **Status** | **DEPRECATED** per ADR-005. Retained in notebook for reproducibility. |
| **Replaced by** | Static 500m connectivity neighbourhood buffer (rendered in `outputs/maps/network_neighborhoods.html`). |
| **Why deprecated** | Function never produced non-trivial growth (180 source trees reached, zero growth over 5 seasons). The BFS-based implementation bypassed the graph's own edge thresholds by building a fresh KDTree. No data exists to calibrate urban fungal colonisation rates. |

---

## Components -- planned (Phase 4-7)

| Component | Lands in | One-line role |
|-----------|----------|---------------|
| Baseline model | Session 4 | Predicts priority ranking from barrier sub-scores; sanity-check against known Eixos Verds |
| Scenario sensitivity | Session 5 | Tests weight perturbations on top-15 stability; Jaccard confidence intervals |
| Failure gallery | Session 6 | Documents edge cases (AM-dominant null-information cells, district gaps, zero-bridge zones) |
| Decision-facing output | Session 7 | Priority map + intervention brief for Barcelona Regional |
| Parquet conversion | Session 4 | `scored_grid.geojson` -> `scored_grid.parquet` with typed schema (data contract v1.0.0) |
| Code refactoring | Session 4 | Notebook functions extracted to `src/clean_data.py` with tested function signatures |
| `normalize_species_names()` -> `src/clean_data.py` | Session 4 | Species name normalisation (currently inline in notebook Cell 3) |
| `build_grid()` -> `src/clean_data.py` | Session 4 | Grid construction (currently inline in notebook Cell 3) |
| `join_fungalroot()` -> `src/clean_data.py` | Session 4 | FungalRoot merge + type normalisation (currently Cell 5) |
| `compute_tree_stats()` -> `src/clean_data.py` | Session 4 | Per-cell aggregation (currently Cells 6-8) |
| `zonal_stats()` -> `src/clean_data.py` | Session 4 | Raster zonal mean (currently duplicated in Cells 2-4 of notebook 03) |
| `compute_scores()` -> `src/clean_data.py` | Session 4 | Sub-score + composite + top-15 logic (currently Cells 5-9 of notebook 03) |

---

## The contracts -- `scored_grid` schema

Primary interface from Phase 3 to Phase 4. Defined in `phase-3/data-contract.yaml` (v1.0.0).

**File:** `data/scored_grid.geojson`
**Format:** GeoJSON, 495 features, EPSG:25831
**Backup format (planned):** `data/scored_grid.parquet` (Phase 4)

| Column | Type | Units / range | Source | Nullable | Description |
|--------|------|---------------|--------|----------|-------------|
| `cell_id` | str | e.g. `C016_011` | Notebook 02 | No | Grid cell identifier |
| `district` | str | 10 BCN districts | Ajuntament trees | Yes | Catalan district name |
| `barri` | str | 73 neighbourhoods | Ajuntament trees | Yes | Catalan neighbourhood name |
| `geometry` | Polygon | EPSG:25831 | Notebook 02 | No | 400m x 400m cell |
| `total_trees` | int | [0, 1290] | Notebook 02 | No | All trees, including unknown myco_type |
| `n_AM` | int | [0, 1281] | Notebook 02 | No | AM host trees in cell |
| `n_EM` | int | [0, 108] | Notebook 02 | No | EM host trees in cell |
| `n_unknown` | int | [0, 362] | Notebook 02 | No | Unassigned myco type trees |
| `am_pct` | float | [0, 100] | Notebook 02 | Yes (null if 0 known trees) | % of known-type trees that are AM |
| `em_pct` | float | [0, 100] | Notebook 02 | Yes | % of known-type trees that are EM |
| `trees_young_pct` | float | [0, 100] | Notebook 02 | Yes (null if no planting dates) | % planted within 5 years |
| `species_richness` | int | [1, 35] | Notebook 02 | No | Unique species in cell (matched subset) |
| `expected_myco_type` | str | {AM, EM, Mixed, Unknown} | Notebook 02 | No | Dominant type. Renamed from `dominant_myco_type` for clarity. |
| `s1_sealed` | float | [0, 1] | Urban Atlas via notebook 03 | No | Sealed surface barrier sub-score |
| `s2_lst_anomaly` | float | [0, 1] | Landsat LST via notebook 03 | No | LST anomaly sub-score (z-score clipped at +/-2-sigma) |
| `s3_inverted_ndvi` | float | [0, 1] | Sentinel-2 NDVI via notebook 03 | No | Inverted NDVI sub-score |
| `s4_mismatch` | float | {0.0, 0.5, 0.6, 0.8} | Notebook 03 | No | Host mycorrhizal mismatch. 0.5 = informationally null (AM-dominant) |
| `composite_score_A` | float | [0, 1] | Notebook 03 | No | Equal weights (0.25 each) |
| `composite_score_B` | float | [0, 1] | Notebook 03 | No | Sealed-dominant (0.55/0.20/0.20/0.05) PRIMARY |
| `composite_score_C` | float | [0, 1] | Notebook 03 | No | Heat+canopy (0.17/0.30/0.30/0.23) |
| `top15_flag` | bool | {True, False} | Notebook 03 | No | In Scenario B top-15 |
| `intervention_type` | str | {de-paving, cooling, planting, multi-strategy} | Notebook 03 | No | Dominant intervention label |
| `intervention_profile` | str | e.g. "52% de-paving . 23% cooling . 22% planting" | Notebook 03 | Yes | Human-readable contribution breakdown |
| `colonisation_uncertain` | bool | {True, False} | Notebook 03 | No | >= 30% trees planted <5 years ago |
| `s1_contribution_pct` | float | [0, 100] | Notebook 03 | No | % of composite_B from S1 |
| `s2_contribution_pct` | float | [0, 100] | Notebook 03 | No | % of composite_B from S2 |
| `s3_contribution_pct` | float | [0, 100] | Notebook 03 | No | % of composite_B from S3 |
| `s4_contribution_pct` | float | [0, 100] | Notebook 03 | No | % of composite_B from S4 |
| `mean_sealed` | float | [0, 1] | Urban Atlas | No | Raw mean sealed fraction |
| `mean_lst_celsius` | float | nullable | Landsat LST | Yes | Raw summer LST (null if no valid pixels) |
| `lst_anomaly` | float | nullable | Landsat LST | Yes | Anomaly from city-wide mean |
| `mean_ndvi` | float | [-0.027, 0.364] | Sentinel-2 NDVI | Yes | Raw summer NDVI (null if no valid pixels) |
| `gbif_records` | int | [0, n] | GBIF via notebook 03 | No | Fungal occurrence records in cell |
| `component_id` | int | nullable | Notebook 04 | Yes | Fungal network island ID (null if not in graph) |
| `component_size` | int | nullable | Notebook 04 | Yes | Trees in island (null if not in graph) |
| `cell_bbox_minx` | float | EPSG:25831 | Notebook 02 | No | Bounding box minimum X |
| `cell_bbox_miny` | float | EPSG:25831 | Notebook 02 | No | Bounding box minimum Y |
| `cell_bbox_maxx` | float | EPSG:25831 | Notebook 02 | No | Bounding box maximum X |
| `cell_bbox_maxy` | float | EPSG:25831 | Notebook 02 | No | Bounding box maximum Y |

**Validation rules** (from `phase-3/data-contract.yaml`):
- `row_count == 495`
- `gdf.crs == "EPSG:25831"`
- `geometry_type == "Polygon"`
- `cell_id.isna().sum() == 0`
- `all(composite_score_B.between(0, 1))`
- `top15_flag.sum() == 15`
- Scenario weights sum to 1.0 each

---

## Open seams

These are honest weak links the project carries. Each is rooted in a data limitation or architectural constraint documented in an ADR or the notebooks.

### Seam 1: AM graph restricted to SANT MARTI district only (ADR-004)

The full-city AM graph (134,809 nodes, ~9.1B potential edges) is computationally intractable in the current pandas/NetworkX pipeline. The AM graph was built for SANT MARTI only (26,038 nodes, 13,010 edges). This means:
- `component_id` and `component_size` in the scored grid are **missing for 89% of cells** (only SANT MARTI cells have AM graph data).
- Connected component statistics (25,508 components, largest = 552 trees) are valid for the combined graph but the AM component reflects only SANT MARTI.
- **All bridge_scores = 0** (Seam 4) is partially caused by this -- non-Sant Marti AM trees are invisible to the bridge analysis.

**Remediation path** (from ADR-004): (1) Partition AM graph by district (10 sub-graphs). District boundaries are natural AM dispersal barriers. (2) Use `STRtree` spatial indexing to reduce candidate pairs. (3) Cap each node at k=20 nearest neighbours within the 15m threshold. Target: <500K edges total.

### Seam 2: S4 mismatch sub-score = 0.5 for 263 cells (53.1%) -- informationally null

The AM-blindness limit makes the host-mismatch sub-score a categorical flag, not a measured barrier. For all 263 AM-dominant cells (`am_pct >= 80`), `s4_mismatch = 0.5` regardless of actual fungal presence. This means:
- S4 contributes to the composite but carries **no information** for 53.1% of cells.
- Scenario A (equal weights) gives S4 = 0.25 -- elevating a null proxy to co-equal with physically measured sealed surface. This is why Scenario A is not the primary (ADR-003).
- Downweighting S4 to 0.05 in Scenario B is an honest acknowledgement but does not solve the underlying information gap.

**No remediation within this project's scope.** AM fungi are invisible to citizen science. Full-resolution assessment requires soil metabarcoding, which is out of scope.

### Seam 3: No inter-component bridging detected (all bridge_scores = 0)

Every one of the 15 priority zones returned `bridge_score = 0`. After BUG-7 fix (distinct component pairs instead of raw edge count), this is a genuine structural result:
- The AM graph covers only one district -- it cannot find bridges to other districts.
- The 15m AM / 35m EM thresholds are conservative (ecologically justified but operationally produce no overlapping radii between components).
- The `sealed_pct >= 0.7` barrier threshold may be too aggressive -- softening to >= 0.85 could produce bridging in the zone edges.

**Consequence:** The connectivity analysis (notebook 04) currently contributes no information to the priority ranking. It illustrates method feasibility only.

### Seam 4: Spread simulation deprecated -- replaced by static 500m buffer (ADR-005)

Any claim of "projected spread" or "seasonal growth" from the current pipeline would be false. The `simulate_spread()` function:
- Never produced non-trivial growth (180 source trees, 0 growth over 5 seasons).
- Bypassed its own graph's edge thresholds.
- Cannot be calibrated -- no urban fungal colonisation rate data exists for Barcelona.

The output is relabelled "500m connectivity neighbourhood" (static buffer around current fungal islands). Phase 4 must not use the deprecated function.

### Seam 5: 24% of tree species excluded from mycorrhizal type assignment

Of 189,220 tree-rows, 45,272 (24%) are species not in the MYCO_LOOKUP top-20. These trees carry `myco_type = "NM"` (non-mycorrhizal / unknown). This means:
- `n_unknown` counts them but does not inflate AM or EM fractions.
- `species_richness` reports only matched subset species.
- If a cell has high `n_unknown` and low `n_AM` + `n_EM`, its `expected_myco_type` may be "Unknown" (18 cells) or biased toward whichever type dominates the known subset.

**Partial remediation:** Extend MYCO_LOOKUP beyond top-20 using the full FungalRoot CSV (13,756 species mappings already loaded). Notebook 02 uses the full CSV when present but the top-20 stub overrides it (safety override, BUG-2). Removing the override for species outside the top-20 would recover some of the 24%.

### Seam 6: Urban substrate domain shift for FungalRoot assignments (ADR-003)

FungalRoot v2.0 is a global database of plant mycorrhizal traits, derived primarily from natural and agricultural systems. Urban Barcelona's soils are heavily modified -- compaction, contamination, irrigation (`GOTEIG` drip irrigation on street trees), and structural-soil installations weaken the tree-presence-to-functional-mycorrhiza link relative to less disturbed systems.

**Consequence:** Even correctly assigned AM/EM types are assignments of *potential*, not *confirmation*. A *Platanus x acerifolia* in a structural-soil pit under 85% sealed surface may not host the same AM community as a *Platanus* in Collserola. This domain shift is undocumented in the FungalRoot metadata.

---

## Key Architectural Decisions (from ADRs)

### ADR-001: Canonical Analysis CRS -- EPSG:25831 (ETRS89 / UTM zone 31N)

**Decision:** All spatial layers reprojected to EPSG:25831 at ingest. Metre-based CRS required for distance thresholds (AM <=15m, EM <=35m) that are meaningless in degrees. EPSG:25831 is the official Catalan cartographic reference system.

**Consequences:** GeoJSON outputs carry EPSG:25831. Web maps (Folium) auto-reproject to EPSG:4326 for display. Back-transform via `gdf.to_crs('EPSG:4326')` available for external consumption.

### ADR-002: Integration Resolution -- 400m x 400m Grid

**Decision:** All analysis at 400m x 400m grid cell resolution, aligned to BCN bounding box in EPSG:25831. Grid origin snapped to 400m multiples. 495 occupied cells covering 10 districts.

**Rationale:** Superilla-compatible (~400m block scale). 2x rule satisfied with 13.3x margin (coarsest input = Landsat 30m). MAUP sensitivity documented.

**Consequences:** All vector-to-grid operations use `gpd.sjoin(predicate='within')`. All raster-to-grid zonal statistics use `rasterstats.zonal_stats(stats=['mean'])`. Phase 4 modelers must not re-grid to finer resolution.

### ADR-003: Primary Weight Scenario -- Scenario B (Sealed-Dominant)

**Decision:** Scenario B (S1=0.55, S2=0.20, S3=0.20, S4=0.05) is primary. Rationale: S1 is best-evidenced barrier (soil sealing mechanism uncontroversial). S4 downweighted correctly (AM-blindness makes it informationally null for 53.1% of cells). Sealed surface is most tractable intervention.

**Consequences:** All top-15 cells under Scenario B receive `intervention_type = "de-paving"`. Full sensitivity analysis (3 scenarios, Jaccard comparison) preserved in output. Rankings are weight-sensitive (A-B Jaccard = 0.364) -- all three scenarios presented.

### ADR-004: AM Graph -- Demonstration District Only (SANT MARTI)

**Decision:** AM graph limited to SANT MARTI district. EM graph runs city-wide (9,139 trees). Combined graph = 35,177 nodes, 54,357 edges.

**Rationale:** Full-city AM graph (134,809 nodes) has ~9.1B potential edges -- not tractable. SANT MARTI is the most populous district with active urban transformation (22@ district) and representative tree mix.

**Consequences:** Network analysis underrepresents AM-connected components in non-Sant Marti districts. Visualisation must disclose limitation. Remediation path documented (district partition + edge caps).

### ADR-005: Spread Simulation -- Deprecated, Replaced by Static Buffer

**Decision:** `simulate_spread()` deprecated. Replaced by static 500m connectivity neighbourhood buffer around connected components.

**Rationale:** Function never worked (0 growth over 5 seasons). Bypassed graph's own edge thresholds. No data exists to calibrate urban fungal colonisation rates.

**Consequences:** Output renamed `network_spread.html` -> `network_neighborhoods.html`. Visualisation relabelled "2030 projected spread" -> "500m connectivity neighbourhood". Phase 4 must not use deprecated function.

---

## Sign-off

**Team:** Rafik, Claude, [remaining team members]
**Drawn by:** Rafik, Claude
**Last updated:** 2026-05-26
**CRISP-DM Phase:** 3 (Data Preparation + Modeling -- scoring pipeline complete, connectivity demonstration-only)

**Pipeline source:** `notebooks/01-data-profiling.ipynb` -> `notebooks/02-grid-trees.ipynb` -> `notebooks/03-scoring.ipynb` -> `notebooks/04-connectivity.ipynb`
**Intermediate artifacts:** `data/grid_trees.geojson` -> `data/scored_grid.geojson` -> `data/network_nodes.geojson` + `data/network_islands.geojson` + `data/bridge_scores.csv`
**Phase 4 entry point:** `data/scored_grid.geojson` (schema: `phase-3/data-contract.yaml` v1.0.0)
