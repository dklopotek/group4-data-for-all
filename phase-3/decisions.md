# Phase 3 Decision Log — Mycorrhizal Barcelona

Per CRISP-DM Phase 3 (Chapman et al. 2000, p. 27–30). Every transformation choice between raw input and `data/scored_grid.geojson` is logged with rationale, impact, and reversibility.

**Date:** 2026-05-26
**Notebooks audited:** 01-data-profiling, 02-grid-trees, 03-scoring, 04-connectivity, 05-visualisation
**Decision log compiled by:** Claude (retroactive audit of existing notebook pipeline)

---

## 3.1 SELECT DATA — Inclusion/Exclusion

| dec_id | source | scope | keep? | rationale | rows in | rows out | filter spec | reviewer | date |
|--------|--------|-------|-------|-----------|---------|----------|-------------|----------|------|
| SEL-001 | data-inventory.md (7 adopted) | full file | YES | Phase 2 earn-the-data scored ≥10/14 on 7-axis rubric; 2 rejected, 1 under investigation | 7 | 3 | — | RE | 2026-05-26 |
| SEL-002 | Ajuntament Arbrat Viari | full file | YES | PRIMARY source — street tree inventory, 143,610 rows | 143,610 | 0 | — | RE | 2026-05-26 |
| SEL-003 | Ajuntament Arbrat Zona | full file | YES | PRIMARY source — park tree inventory, 45,480 rows | 45,480 | 0 | — | RE | 2026-05-26 |
| SEL-004 | Ajuntament Trees (combined) | `tipus_element`, `cat_nom_cientific`, `categoria_arbrat`, `data_plantacio`, `nom_districte`, `nom_barri`, geometry | YES | columns needed for mycorrhizal lookup + spatial join + colonisation uncertainty | 189,090 | — | — | RE | 2026-05-26 |
| SEL-005 | Ajuntament Trees (combined) | `codi`, `adreca`, `num_catalog`, `lat`, `lon`, `alcada`, `capcada`, `amplada_voral`, `tipus_aigua` + 28 others | NO | irrelevant to mycorrhizal analysis; lat/lon redundant with geometry; catalog number carries no ecological signal | — | 36 columns | — | RE | 2026-05-26 |
| SEL-006 | FungalRoot v2.0 | `genus`, `species`, `myco_type` | YES | species→genus→mycorrhizal-type lookup table; core join key | 14,919 | — | — | RE | 2026-05-26 |
| SEL-007 | FungalRoot v2.0 | all other columns (family, order, myco_order, refs) | NO | not consumed by pipeline; type assignment already resolved | — | 10+ columns | — | RE | 2026-05-26 |
| SEL-008 | GBIF Fungi (BCN bbox) | `species`, `decimalLatitude`, `decimalLongitude`, `basisOfRecord`, `taxonRank` | YES | spatial presence context for EM-confirmation in S4 sub-score | 4,265 | — | — | RE | 2026-05-26 |
| SEL-009 | GBIF Fungi (Catalonia) | `species`, `decimalLatitude`, `decimalLongitude`, `basisOfRecord` | YES | wider-region context for Collserola reference patch | 8,114 | — | — | RE | 2026-05-26 |
| SEL-010 | Urban Atlas 2018 | `sealed_surface.tif` (single-band raster) | YES | S1 sub-score input — sealed-surface fraction per 400m cell | — | — | `gdalwarp -tr 400 400 -r average` | RE | 2026-05-26 |
| SEL-011 | Landsat 8/9 LST | summer composite .tif (median of cloud-free summer scenes) | YES | S2 sub-score input — surface temperature anomaly | — | — | composited via `notebooks/02-grid-trees.ipynb` | RE | 2026-05-26 |
| SEL-012 | Sentinel-2 L2A | summer NDVI composite .tif (median of cloud-free summer scenes) | YES | S3 sub-score input — inverted vegetation index | — | — | composited via `notebooks/02-grid-trees.ipynb` | RE | 2026-05-26 |
| SEL-013 | BCN Boundaries (OSM + Ajuntament OpenData) | boundary + district .geojson | YES | spatial framework — 400m grid clipping extent; auxiliary source, no datasheet required per data-inventory.md | — | — | `ST_Intersects(grid, boundary)` | RE | 2026-05-26 |
| SEL-014 | 400m grid | generated from BCN bbox | YES | decision unit per data-inventory.md — Superilla-compatible 400m × 400m | 495 | — | EPSG:25831, origin at bbox min | RE | 2026-05-26 |
| SEL-015 | MYCO_LOOKUP (hardcoded top-20) | 20 species → mycorrhizal type mapping | YES | reduces FungalRoot join to dominant urban species; 143,948 of 189,090 trees matched (76.1%) | 20 | 14,899 | species in top-20 by frequency | RE | 2026-05-26 |
| SEL-016 | Species outside MYCO_LOOKUP top-20 | 45,272 trees with species not in hardcoded dict | NO | `unknown` myco_type — cannot assign AM/EM; dropped from network graph but retained in grid-level statistics (am_pct, em_pct computed from matched subset) | 45,272 | — | `myco_type != 'unknown'` for graph construction only | RE | 2026-05-26 |

---

## 3.2 CLEAN DATA — Quality Remediation

| dec_id | dataset | issue | decision | rationale | mechanism (if NA) | rows affected | reversible? | reviewer | date |
|--------|---------|-------|----------|-----------|-------------------|---------------|-------------|----------|------|
| CLN-001 | Ajuntament Trees | species names inconsistent: `Quercus ilex` vs `Q. ilex` vs `quercus ilex` | normalize against FungalRoot `genus`+`species` columns; case-insensitive join on genus+species | FungalRoot is canonical taxonomy for this pipeline; unify before myco-type assignment | — | 189,090 | YES (raw names preserved in source CSV) | RE | 2026-05-26 |
| CLN-002 | Ajuntament Trees | 0.01% genus-only records (25 of 189,090) | assign `myco_type = 'unknown'` after FungalRoot genus-level fallback fails | cannot resolve AM/EM at genus-only level for genera with mixed types | — | 25 | YES (flagged, not dropped) | RE | 2026-05-26 |
| CLN-003 | Ajuntament Trees | 45,272 trees (24%) species not in MYCO_LOOKUP | dropped from network graph; retained in grid-level `total_trees` count, flagged `myco_type = 'unknown'` | MYCO_LOOKUP covers top-20 species by frequency; extending to 381 species requires FungalRoot full join (SEL-006 scope remains) | MAR (species rarity — rarer species ≠ FungalRoot resolved) | 45,272 | YES (retained in grid stats, excluded from graph) | RE | 2026-05-26 |
| CLN-004 | Urban Atlas | `sealed_surface.tif` scale misread as 0-100 (BUG-3) | fix reading scale: `scale=1.0` not `scale=0.01` | `process_urban_atlas.py` writes 0-1 scale; dividing by 100 produced 0-0.01 range, zeroing S1 discriminability | — | all cells | YES (source file unchanged) | RE | 2026-05-26 |
| CLN-005 | Tree-grid aggregation | `am_pct`/`em_pct` threshold compared against 0.8 instead of 80 (BUG-4) | fix threshold to ≥80 (scale is 0-100) | `am_pct = (n_AM / n_known) * 100` — stored on percent scale | — | all cells | YES (recomputed in notebook 03) | RE | 2026-05-26 |
| CLN-006 | Tree-grid aggregation | `trees_young_pct` threshold compared against 0.3 instead of 30 (BUG-5) | fix threshold to ≥30 (scale is 0-100) | same percent-scale issue as CLN-005 | — | all cells | YES | RE | 2026-05-26 |
| CLN-007 | District constraint | only last missing district got a representative cell (BUG-6) | accumulate representatives per missing district, not overwrite | `selected[-1]` overwrite pattern discarded all but last missing district | — | 5 districts | YES (recomputed) | RE | 2026-05-26 |
| CLN-008 | Bridge score | counted every inter-component edge instead of distinct component pairs (BUG-7) | count unique unordered `(component_a, component_b)` pairs | double-counting inflated bridge scores proportionally to component size; with fix, ALL scores = 0 | — | all edges | YES | RE | 2026-05-26 |
| CLN-009 | Spread simulation | static 500m buffer, not propagation (BUG-8) | rewrite as frontier-based BFS with per-season spread distance | static buffer ignored connectivity structure; though rewrite done, function is DEPRECATED — not used in v1 | — | all cells | YES (function rewritten but marked deprecated) | RE | 2026-05-26 |
| CLN-010 | Sensitivity chart | scenario labels did not match implemented weights (BUG-9) | update chart labels to actual scenario weights | scenario labels said "Equal / Sealed-Dominant / Heat+Canopy" but weights differed from code | — | 3 labels | YES | RE | 2026-05-26 |
| CLN-011 | Real-data verification | didn't check sub-score variance (BUG-10) | add low-variance warning (std <0.05 across sub-scores triggers "synthetic or homogeneous data" flag) | without variance check, real vs synthetic data indistinguishable | — | N/A | YES | RE | 2026-05-26 |
| CLN-012 | Sentinel-2 NDVI | cloud mask not verified for scene(s) | defer to Phase 3; report valid-pixel fraction per cell | bias-and-annotation.md flags this as `unknown`; Mediterranean summer cloud cover is low (<15% expected) | — | 0 | YES (deferred, not fixed) | RE | 2026-05-26 |
| CLN-013 | Landsat LST | QA_PIXEL band not inspected | defer to Phase 3; report valid-pixel fraction per cell | same as CLN-012 — flagged in bias-and-annotation.md | — | 0 | YES (deferred) | RE | 2026-05-26 |
| CLN-014 | All spatial layers | mixed CRS at ingest (EPSG:4326, EPSG:3035, EPSG:32631) | reproject all to EPSG:25831 (UTM31N, ETRS89) | canonical project CRS per ADR-001; single reprojection at ingest, no chain-reprojection | — | all features | YES (source files unchanged) | RE | 2026-05-26 |
| CLN-015 | Duplicate tree records | re-ingestion artifacts (byte-identical rows) | not checked | no SHA-256 row dedup run; low-priority — Ajuntament publishes deduplicated CSVs | — | unknown | YES (add SHA-256 row hash column) | RE | 2026-05-26 |
| CLN-016 | Missing `data_plantacio` values | unknown number of trees with null planting date | assign `colonisation_uncertain = True` for null dates | conservative: treat unknown-age trees as potentially pre-mycorrhizal-establishment | MAR | unknown | YES (flag, not drop) | RE | 2026-05-26 |

---

## 3.3 CONSTRUCT DATA — Feature Engineering

| dec_id | construct | formula / method | rationale | inputs | sensitivity | reviewer | date |
|---------|-----------|-----------------|-----------|--------|-------------|----------|------|
| CON-001 | S1 — Sealed surface barrier | `max(0, 1 - sealed_pct)` (linear inversion) | sealed surface is direct barrier to fungal dispersal; linear mapping justified by absence of non-linear threshold evidence | `sealed_surface.tif` | high — drives 52% of intervention recommendation in Scenario B | RE | 2026-05-26 |
| CON-002 | S2 — LST anomaly | `z_score(LST_cell)` clipped to ±2σ, then `(z + 2) / 4` to map to 0-1 | urban heat island creates hostile soil temperature microclimate; z-score normalises across city; clipping prevents single-cell dominance | `lst_summer_composite.tif` | moderate — LST anomaly range across Barcelona is ~4-6°C | RE | 2026-05-26 |
| CON-003 | S3 — Inverted NDVI | `max(0, 1 - NDVI)` | vegetation absence = barrier to fungal establishment; NDVI saturation at >0.8 not relevant in Mediterranean urban context | `ndvi_summer_composite.tif` | moderate — NDVI range 0.1-0.7 across Barcelona | RE | 2026-05-26 |
| CON-004 | S4 — Host-mycorrhizal mismatch | categorical: AM-dominant(≥80%)=0.5, EM-dominant+GBIF=0.0, EM-dominant no GBIF=0.8, Mixed=0.6 | AM-blindness: AM fungi invisible to citizen science → mismatch sub-score is information gap, not ecological score; 0.5 for AM-dominant encodes "we don't know" | `am_pct`, `em_pct`, GBIF presence | HIGHEST — 53.1% of cells are AM-dominant → S4 is 0.5 for majority of city; weight Scenario B assigns S4 only 5% | RE | 2026-05-26 |
| CON-005 | Composite score | `Σ(w_i × S_i)` for i=1..4 | weighted sum; three scenarios tested for sensitivity | S1, S2, S3, S4 | Jaccard A-B=0.364, B-C=0.364 → rankings are weight-sensitive | RE | 2026-05-26 |
| CON-006 | Scenario A (equal) | `w = [0.25, 0.25, 0.25, 0.25]` | baseline — all sub-scores equal; tests whether weighting matters | — | reference scenario only | RE | 2026-05-26 |
| CON-007 | Scenario B (sealed-dominant, RECOMMENDED) | `w = [0.55, 0.20, 0.20, 0.05]` | sealed surface best-evidenced barrier; S4 downweighted to 5% to reflect AM-blindness uncertainty | — | PRIMARY scenario for all deliverables | RE | 2026-05-26 |
| CON-008 | Scenario C (heat+canopy) | `w = [0.17, 0.30, 0.30, 0.23]` | LST+NDVI given equal weight; sealed surface de-prioritised | — | sensitivity test only | RE | 2026-05-26 |
| CON-009 | intervention_type | if S1_contribution ≥ 50%: "de-paving"; elif S2 ≥ 40%: "cooling"; elif S3 ≥ 40%: "planting"; else: "multi-strategy" | actionable recommendation from sub-score decomposition | S1, S2, S3 contributions | all top-15 cells get "de-paving" in Scenario B | RE | 2026-05-26 |
| CON-010 | intervention_profile | percentage string: `"{S1%:.0f}% de-paving · {S2%:.0f}% cooling · {S3%:.0f}% planting"` | human-readable action breakdown; S4 excluded because "reduce AM-blindness" not an action | S1, S2, S3 contributions | — | RE | 2026-05-26 |
| CON-011 | colonisation_uncertainty | `trees_young_pct ≥ 30` → flag | trees planted <5 years ago may not have established mycorrhizal colonisation (Jumpponen & Egerton-Warburton 2010) | `trees_young_pct` | 0 cells flagged in top-15 | RE | 2026-05-26 |
| CON-012 | MYCO_LOOKUP | hardcoded dict: 17 AM species, 3 EM species (top-20 by Barcelona tree frequency) | reduces FungalRoot join scope; covers 76.1% of trees; species outside dict dropped from graph | top-20 species from notebook 01 profiling | MAJOR — 24% tree loss; AM graph biased toward common species | RE | 2026-05-26 |
| CON-013 | AM edge threshold | `distance ≤ 15m` (cKDTree radius query) | AM fungi disperse over short distances (~10-20m typical); 15m conservative | tree coordinates (EPSG:25831) | unvalidated — literature range 1-50m | RE | 2026-05-26 |
| CON-014 | EM edge threshold | `distance ≤ 35m` (cKDTree radius query) | EM fungi disperse further than AM via wind-dispersed spores; 35m mid-range | tree coordinates (EPSG:25831) | unvalidated — literature range 10-100m+ | RE | 2026-05-26 |
| CON-015 | Barrier threshold | `sealed_pct ≥ 0.7` → cell is barrier to edge construction | trees in heavily sealed cells cannot form fungal connections across cell boundaries | `sealed_pct` per cell | 98,371 of 143,948 trees inside barrier cells | RE | 2026-05-26 |
| CON-016 | connected_components | NetworkX `connected_components(G)` | identifies fungal network "islands" — sets of trees mutually reachable via AM/EM edges | NetworkX graph G (AM+EM) | 25,508 components; largest island = 552 trees | RE | 2026-05-26 |
| CON-017 | bridge_score_for_zone | `len(set((c_a, c_b) for edge spanning components))` | counts distinct component pairs connected by de-paving a single cell | components from CON-016 | ALL scores = 0 — no inter-component bridging with current parameters | RE | 2026-05-26 |
| CON-018 | Network neighbourhood (replaces spread) | 500m static buffer around connected components | identifies area within walking-dispersal range of each fungal island; replaces deprecated BFS spread model | component centroids, 500m radius | static buffer — no temporal dynamics, no propagule pressure | RE | 2026-05-26 |
| CON-019 | top15_flag | rank by composite_B descending, flag top 15 | priority cells for intervention targeting | composite_B | top-15 list is deliverable output | RE | 2026-05-26 |

---

## 3.4 INTEGRATE DATA — Joins & Aggregation

| dec_id | integration | method | rationale | join keys | rows out | reviewer | date |
|---------|-------------|--------|-----------|-----------|----------|----------|------|
| INT-001 | Trees → 400m grid | spatial join: `gdf.sjoin(grid, how='left')` | assign each tree to its containing grid cell | `ST_Within(tree_geom, cell_geom)` in EPSG:25831 | 189,090 | RE | 2026-05-26 |
| INT-002 | Grid-level tree aggregation | per-cell: `total_trees`, `n_AM`, `n_EM`, `n_unknown`, `am_pct`, `em_pct`, `trees_young_pct`, `species_richness` | reduce tree points to grid-level statistics for scoring | `cell_id` | 495 | RE | 2026-05-26 |
| INT-003 | Raster → grid zonal statistics | `rasterstats.zonal_stats(cells, raster, stats=['mean'])` | extract mean sealed/LST/NDVI per 400m cell | cell geometry, raster band | 495 | RE | 2026-05-26 |
| INT-004 | FungalRoot → tree species | left join on `(genus, species)` lowercase | assign mycorrhizal type to each tree | `(cat_genere, cat_especie)` → `(genus, species)` | 143,948 matched | RE | 2026-05-26 |
| INT-005 | GBIF → grid | spatial join: `gdf.sjoin(grid, how='left')` | GBIF presence flag per cell for EM-confirmation in S4 | `ST_Within(gbif_geom, cell_geom)` | 495 (binary flag) | RE | 2026-05-26 |
| INT-006 | Landsat/Sentinel-2 compositing | median of summer (Jun-Aug) cloud-free scenes | reduce temporal noise; summer maximises thermal/vegetation contrast | pixel coordinate | 1 band per sensor | RE | 2026-05-26 |
| INT-007 | All layers → EPSG:25831 | `to_crs('EPSG:25831')` at ingest | single analysis CRS; no on-the-fly reprojection in QGIS/folium | — | all features | RE | 2026-05-26 |
| INT-008 | Tree graph construction | `cKDTree.query_ball_point(r=threshold)` per myco_type | spatial nearest-neighbour edge construction; separate trees by AM/EM threshold | tree coordinates (EPSG:25831) | 54,357 edges | RE | 2026-05-26 |
| INT-009 | AM graph scope | demonstration district only (SANT MARTÍ): 26,038 nodes, 13,010 edges | full-city AM graph (`n_AM = 134,809`) produces `n×(n-1)/2` potential edges — compute bound exceeded; district-limited for feasibility | `nom_districte == 'SANT MARTÍ'` | 26,038 of 134,809 AM trees | RE | 2026-05-26 |
| INT-010 | Combined graph | AM (SANT MARTÍ) + EM (all districts) | EM graph is small (9,139 nodes) so full-city feasible; combined graph inherits AM district limitation | NetworkX `compose(G_AM, G_EM)` | 35,177 nodes, 54,357 edges | RE | 2026-05-26 |

---

## 3.5 FORMAT DATA — Output Specification

| dec_id | output | format | schema | rationale | reviewer | date |
|---------|--------|--------|--------|-----------|----------|------|
| FMT-001 | `data/scored_grid.geojson` | GeoJSON, EPSG:25831 | 495 features, 39 columns (see data-contract.yaml) | primary Phase 4 input; human-readable + machine-readable; QGIS/folium compatible | RE | 2026-05-26 |
| FMT-002 | `data/network_nodes.geojson` | GeoJSON, EPSG:25831 | 35,177 features | tree nodes in fungal network with myco_type, component_id | RE | 2026-05-26 |
| FMT-003 | `data/network_edges.geojson` | GeoJSON (LineString) | 5,344 features (top-5 islands only) | edges between connected trees; full 54K edges too large for web rendering | RE | 2026-05-26 |
| FMT-004 | `data/network_islands.geojson` | GeoJSON (Polygon) | 25,508 features (convex hull per component) | component spatial extents; top 20 largest rendered in HTML | RE | 2026-05-26 |
| FMT-005 | `data/bridge_scores.csv` | CSV | cell_id, n_bridges, n_components_connected, bridge_score | bridge potential per cell; all scores = 0 | RE | 2026-05-26 |
| FMT-006 | `outputs/priority_zones.csv` | CSV | top-15 cells with all sub-scores + intervention profile | tabular priority list for policymaker consumption | RE | 2026-05-26 |
| FMT-007 | Interactive maps | HTML (Folium) | `priority_map.html`, `network_neighborhoods.html`, `sensitivity_comparison.png` | visual deliverables; teacher-facing | RE | 2026-05-26 |
| FMT-008 | Column naming convention | snake_case, English | `nom_districte→district`, `barri_name→barri`, `composite_A/B/C→composite_score_A/B/C`, `top15_scenario_B→top15_flag`, `dominant_myco_type→expected_myco_type`, `lst_anomaly_celsius→lst_anomaly` | consistent, code-friendly, English-preferred for international audience | RE | 2026-05-26 |
| FMT-009 | Output CRS | EPSG:25831 (ETRS89 / UTM zone 31N) | all GeoJSON outputs; analysis CRS per ADR-001 | RE | 2026-05-26 |
| FMT-010 | No Shapefile output | GeoJSON only | Shapefile silently truncates column names to 10 chars, destroys 39-column schema; Phase 3 policy: never produce Shapefile as canonical output | RE | 2026-05-26 |

---

## Known Limitations Carried Forward to Phase 4

| id | limitation | severity | documented in |
|----|-----------|----------|---------------|
| LIM-001 | 45,272 trees (24%) excluded from network — species outside MYCO_LOOKUP top-20 | MAJOR | CLN-003, CON-012 |
| LIM-002 | AM graph covers only SANT MARTÍ district — full-city AM graph infeasible | MAJOR | INT-009 |
| LIM-003 | ALL bridge_scores = 0 — no inter-component bridging with current parameters | MAJOR | CON-017 |
| LIM-004 | Spread simulation deprecated — static 500m buffer replaces BFS model | MODERATE | CON-018, CLN-009 |
| LIM-005 | 53.1% cells are AM-dominant → S4 = 0.5 (informationally null) | MODERATE | CON-004 |
| LIM-006 | AM/EM edge thresholds (15m/35m) unvalidated against empirical dispersal data | MODERATE | CON-013, CON-014 |
| LIM-007 | No Pandera schema validation at pipeline runtime — only inline checks | MINOR | CLN-015 |
| LIM-008 | Cloud mask / QA band not verified for satellite rasters | MINOR | CLN-012, CLN-013 |
| LIM-009 | No train/test split defined — Phase 4 must define spatial cross-validation | MINOR | (deferred to Phase 4) |
| LIM-010 | Colonisation uncertainty flag triggers on 0 cells in top-15 — threshold may be too strict | MINOR | CON-011 |

---

**Date:** 2026-05-26
**Audited by:** Claude (Phase 3 retroactive decision audit)
**Total decisions:** 64 (16 SEL + 16 CLN + 19 CON + 10 INT + 10 FMT — subset shown)
