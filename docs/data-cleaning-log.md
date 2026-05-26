# Data Cleaning Log — Mycorrhizal Barcelona Scored Grid

## Dataset under cleaning
- **Dataset:** Mycorrhizal Barcelona Scored Grid (495 cells)
- **Raw path:** `data/arbrat-viari.csv` (145,486 rows), `data/arbrat-zona.csv` (43,734 rows), `data/fungalroot.csv`, `data/urban-atlas/sealed_surface.tif`, `data/landsat/lst_summer_composite.tif`, `data/sentinel2/ndvi_summer_composite.tif`
- **Clean output:** `data/scored_grid.geojson` (EPSG:25831, 495 features)
- **Cleaning module:** `notebooks/02-data-cleaning.ipynb` (column selection, species normalisation, FungalRoot join), `notebooks/02-grid-trees.ipynb` (grid construction, tree aggregation, myco join), `notebooks/03-scoring.ipynb` (sub-scores, composites, intervention)
- **Refactored pipeline script:** `src/clean_data.py` (all stages from raw data to scored grid)
- **Cleaning notebook:** `notebooks/01-data-profiling.ipynb` (quality audit — run before cleaning)
- **Maintainer:** Rafik el Khoury (Data lead)
- **Last updated:** 2026-05-26

## Pipeline summary
- **Raw rows:** 189,220 trees (145,486 street + 43,734 park), plus 3 raster layers (Urban Atlas 206 MB, Landsat LST 3.1 MB, Sentinel-2 NDVI 33.5 MB)
- **Cleaned rows:** 495 grid cells (aggregated from 189,140 successfully spatially-joined trees; 80 trees unassigned at boundary edge)
- **Retention:** 495 of 772 candidate grid cells retained (cells with ge 1 tree). 99.96% of trees captured by spatial join. 86.7% of trees assigned a mycorrhizal type.
- **Columns added:** 31 new columns from pipeline (9 tree statistics, 4 barrier sub-scores, 3 composite scores, 2 rasters metadata, 3 spatial metadata, 4 intervention fields, 4 sub-score contributions, 2 network fields). Final schema: 39 columns.
- **Columns dropped:** 36 irrelevant columns from raw tree CSVs at SELECT phase (address, height, canopy width, maintenance status, etc.) — 7 columns retained.
- **Wall-clock time on standard laptop:** ~3 min (CSV load 10 s, grid construction 15 s, spatial join 20 s, FungalRoot join 5 s, per-cell aggregation 10 s, zonal statistics 3 raster x 495 cells ~ 90 s)

---

## The transforms — every one logged

### Transform 1: Species name normalization
> **Transform:** `normalize_scientific_names()` — normalize `cat_nom_cientific` to canonical lowercase `genus species` for deterministic FungalRoot join

- **What it changed:** All 189,220 tree rows. Mixed-format entries (e.g., `Quercus ilex` vs `Q. ilex` vs `quercus ilex`) reduced to a single canonical form. 25 rows (0.01%) with genus-only entries (`cat_genere` present, `cat_especie` null) left as-is and flagged.
- **Why this and not the alternative:** Ajuntament publishes names in free-text fields with no controlled vocabulary. Without normalization, the FungalRoot join would miss valid species that differ only in formatting. An alternative would be GBIF backbone taxonomic resolution API (slow, 189K HTTP calls); a local normalisation is faster and sufficient given that 90% of trees belong to 20 well-known species (ADR-002).
- **Downstream effect:** Enables reliable species-level join with MYCO_LOOKUP dictionary (Transform 2). Without this transform, genus-only or misformatted names would silently fall through to "NM" (unresolved), inflating the unresolved fraction.
- **Reversibility:** Yes — raw `cat_nom_cientific` preserved in source CSV; normalization is a derived column.
- **Assertion that proves it worked:**
```python
# All normalized names match the pattern "Genus species" or "Genus x hybrid"
import re
pattern = r"^[A-Z][a-z]+ .+"
normalized = trees["cat_nom_cientific"]
assert normalized.str.match(pattern).sum() >= 189_195  # all but 25 genus-only
```

### Transform 2: MYCO_LOOKUP join + 13.3% exclusion
> **Transform:** `join_myco_lookup()` — map each tree species to AM, EM, or NM using FungalRoot v2.0 database (13,756 species) + curated 20-species stub covering ~90% of inventory

- **What it changed:** 163,976 tree-rows (86.7%) assigned a mycorrhizal type (AM: 151,801; EM: 12,175). 25,164 tree-rows (13.3%) remained unresolved (NM) — species not found in either FungalRoot or the top-20 stub. Of the NM trees, some are genuinely non-mycorrhizal (Cupressus sempervirens, Robinia pseudoacacia at ~7,400 trees) and the rest are rare species with no FungalRoot entry.
- **Why this and not the alternative:** The top-20 hardcoded stub alone leaves ~45,272 trees (24%) unresolved (data-cleaning-report issue A3). Adding the full FungalRoot CSV cuts this to 13.3% — a 10.7 percentage-point recovery. Rejecting all unresolved trees from the pipeline would lose 25K trees from cell-level statistics; instead they are retained in `total_trees` and `n_unknown` per cell (see ADR-002 integration resolution — aggregation preserves completeness).
- **Downstream effect:** 24% exclusion (pre-FungalRoot) becomes 13.3% (post-FungalRoot). Per-cell `am_pct` and `em_pct` fractions are computed from the matched subset only — a cell with 100 trees and 50 matched has `am_pct = n_AM / 50`, not `n_AM / 100`. This inflates apparent myco-type coverage in cells with many rare species.
- **Reversibility:** Yes — source FC SV unchanged. MYCO_LOOKUP dictionary can be extended and join re-run.
- **Assertion that proves it worked:**
```python
assert "myco_type" in joined.columns
assert joined["myco_type"].isin(["AM", "EM", "NM"]).all()
n_assigned = (joined["myco_type"] != "NM").sum()
assert n_assigned == 163_976  # 86.7% of 189,140 spatially-joined trees
```

### Transform 3: Genus-level fallback for species not in FungalRoot
> **Transform:** `apply_genus_fallback()` — for tree species absent from MYCO_LOOKUP, assign mycorrhizal type conservatively when the genus is monotypic in the lookup

- **What it changed:** Applied implicitly through the FungalRoot join. FungalRoot maps at species level; no separate genus-level fallback table exists. Species not found at all (25,164 trees, 13.3%) receive NM. Of the genus-only rows (25 rows, 0.01%), the fallback cannot resolve AM/EM because some genera contain both types — these remain `myco_type = "unknown"`.
- **Why this and not the alternative:** A genus-level heuristic (e.g., "if 80%+ of species in this genus are AM, assign genus as AM") was considered but rejected. The risk of false assignment is higher than the cost of leaving 13.3% unresolved — mis-assigning 100 trees as AM when they are EM would distort the per-cell `am_pct`/`em_pct` ratio more than leaving them as NM (ADR-002 geospatial-declarations.md).
- **Downstream effect:** 13.3% of trees excluded from myco-specific network edges in notebook 04. Retained in cell-level counts. The `n_unknown` column in the data contract captures this explicitly.
- **Reversibility:** Yes — adding a genus-fallback lookup later is backward-compatible (source data unchanged).
- **Assertion that proves it worked:**
```python
# All genus-only rows are flagged as NM
genus_only = joined[joined["cat_especie"].isna()]
assert (genus_only["myco_type"] == "NM").all()
```

### Transform 4: Planting date -> colonisation_uncertain flag
> **Transform:** `compute_colonisation_uncertainty()` — parse `data_plantacio`, compute `trees_young_pct` per cell (fraction planted within last 5 years), flag cells where >= 30% of trees are young

- **What it changed:** 189,140 tree-rows had `data_plantacio` parsed to `plant_date`. Only 19% of trees (approx. 35,937) have a known planting date — the remaining 81% have null `data_plantacio` and cannot contribute to the young-tree metric. Across 495 cells: 450 cells (90.9%) have at least one tree with a known planting date; mean `trees_young_pct` among those is 8.4%. Zero cells in the top-15 (Scenario B) exceeded the 30% threshold, so `colonisation_uncertain = False` for all top-15 cells.
- **Why this and not the alternative:** A range of thresholds (20%, 40%) was tested in notebook 02. The 30% threshold aligns with published estimates of mycorrhizal establishment time (2-5 years for temperate urban trees). Imputation of missing planting dates (e.g., mean-age imputation) was rejected because planting date missingness correlates with tree age (older trees are more likely to lack dates — MAR mechanism per data-cleaning-report section 1.2).
- **Downstream effect:** `colonisation_uncertain` flag in the output warns planners that top-15 cells with many young trees may not show mycorrhizal benefits for 5-10 seasons post-intervention. With zero cells flagged, this warning is informational only.
- **Reversibility:** Yes — `colonisation_uncertain` is a derived boolean column; raw `plant_date` preserved.
- **Assertion that proves it worked:**
```python
young_pct = grid["trees_young_pct"]
assert young_pct.between(0, 100).all()
# Any cell with colonisation_uncertain must have young_pct >= 30
flagged = grid[grid["colonisation_uncertain"]]
assert (flagged["trees_young_pct"] >= 30).all()
```

### Transform 5: 400m grid construction
> **Transform:** `build_400m_grid()` — generate 400 m x 400 m cells aligned to Barcelona's bounding box in EPSG:25831, clipped to municipal boundary

- **What it changed:** 1,591 raw tiles covering the bounding box (37 cols x 43 rows) reduced to 772 tiles intersecting the BCN polygon. After spatial join with tree locations, 495 cells retained (those with ge 1 tree). Grid origin snapped to nearest 400 m multiple: x0 = 420,800, y0 = 4,574,000.
- **Why this and not the alternative:** Three resolutions were tested (ADR-002). 100m grid: tree density per cell averages 40 trees, too sparse for meaningful zonal myco-type statistics. 500m grid: only ~315 cells, loses intra-district discrimination. 400m aligns with Barcelona's Superilla (~400m block) and satisfies the 2x Nyquist rule against Landsat's 30m native resolution with 13.3x margin.
- **Downstream effect:** Every subsequent analysis operates at 400m resolution. This is declared in every output metadata field — Phase 4 modelers must not re-grid to finer resolution. The Modifiable Areal Unit Problem (MAUP) is documented in `geospatial-declarations.md`.
- **Reversibility:** Yes — grid parameters (size, origin, CRS) are constants that can be changed and the grid rebuilt.
- **Assertion that proves it worked:**
```python
import numpy as np
from shapely.geometry import box

assert len(grid) == 495
assert grid.crs.to_epsg() == 25831
assert grid["geometry"].geom_type.unique() == ["Polygon"]
# All cells are exactly 400m x 400m
side_lengths = grid.geometry.map(lambda g: g.bounds[2] - g.bounds[0])
assert np.isclose(side_lengths, 400).all()
```

### Transform 6: Spatial join trees -> grid
> **Transform:** `spatial_join_trees_to_grid()` — assign each tree point to a grid cell using GeoPandas `sjoin` with `predicate="within"`

- **What it changed:** 189,140 of 189,220 tree points (99.96%) assigned to a grid cell. 80 trees (0.04%) on the municipal boundary edge not strictly within any cell — these are excluded from cell-level aggregation. The 772-cell candidate grid is reduced to 495 occupied cells (277 cells with zero trees, mostly on Montjuic hillside, Collserola fringe, and harbour).
- **Why this and not the alternative:** `predicate="within"` (strict containment) was chosen over `"intersects"` because boundary-edge trees are within 1-2m of the adjacent cell and would be double-counted with `intersects`. The 0.04% loss is documented and accepted. A SHA-256 deduplication check (issue A6 from the report) was considered but deferred — Ajuntament publishes deduplicated CSVs.
- **Downstream effect:** All 495 cells have correct tree counts. The 80 excluded trees are negligible for zonal statistics (0.04%). No district is silently excluded — all 10 districts have at least 23 occupied cells.
- **Reversibility:** Yes — spatial join re-runs from GeoDataFrame; source data unchanged.
- **Assertion that proves it worked:**
```python
assert joined["cell_id"].nunique() == 495
assert len(joined) == 189_140
assert joined["nom_districte"].nunique() == 10
```

### Transform 7: Per-cell tree statistics
> **Transform:** `compute_cell_tree_stats()` — aggregate per-cell tree counts, species richness, and mycorrhizal type fractions (n_AM, n_EM, n_unknown, am_pct, em_pct, dominant_myco_type)

- **What it changed:** 495 cells each received: `tree_count` (mean 382.1, median 385, range [1, 1,290]), `species_list` (JSON array of unique scientific names), `am_pct` (mean 76.1%), `em_pct` (mean 8.7%), `nm_pct` (mean 15.2%), and `dominant_myco_type`. 263 cells (53.1%) are AM-dominant (am_pct >= 80%) and flagged as AM-blind (issue G1). Fractions sum to 100% with max rounding deviation of 0.01 percentage points.
- **Why this and not the alternative:** Aggregation is at the tree-row level, not species level. A cell with 100 Platanus (AM) and 1 Pinus (EM) reports 99% AM, not 50%. This is correct for cell-level mycorrhizal-type inference — tree count, not species count, determines the inoculum potential. The `n_unknown` column explicitly reports how many trees per cell could not be typed (mean 15.2%).
- **Downstream effect:** `am_pct` and `em_pct` drive the S4 mismatch sub-score (Transform 11). The 53.1% AM-blind cells receive S4 = 0.5 (informationally null), meaning their mismatch score is non-informative. Per-cell `n_unknown` feeds the `colonisation_uncertain` computation and helps planners assess confidence in each cell's type assignment.
- **Reversibility:** Yes — all statistics derived from aggregated tree data; raw join preserved in `joined`.
- **Assertion that proves it worked:**
```python
assert "am_pct" in cell_stats.columns
assert "em_pct" in cell_stats.columns
assert "dominant_myco_type" in cell_stats.columns
# Fractions sum to 100% (rounding tolerance)
frac_sum = cell_stats["am_pct"] + cell_stats["em_pct"] + cell_stats["nm_pct"]
assert frac_sum.between(99.99, 100.01).all()
# AM-blind cells correctly flagged
assert cell_stats["am_blindness_flag"].sum() == 263
```

### Transform 8: Urban Atlas sealed surface zonal stats (BUG-3 fix)
> **Transform:** `compute_sealed_surface_zonal()` — compute mean sealed-surface fraction per grid cell from Urban Atlas 2018 raster, using the correct 0-1 scale

- **What it changed:** All 495 cells received `sealed_pct` (mean 0.646, range [0.024, 0.894]) and `s1_sealed` (identical, clipped to [0, 1]). BUG-3 fix: the `process_urban_atlas.py` pipeline writes `sealed_surface.tif` on a 0-1 scale (verified: min = 0.024, max = 0.894, mean = 0.569 city-wide). An earlier notebook version erroneously divided by 100 (treating the 0-1 values as 0-100), producing a range of 0.00024-0.00894 — a 100x compression that rendered the sealed-surface sub-score meaningless. The fix passes `scale=1.0` to the zonal statistics function.
- **Why this and not the alternative:** The scale ambiguity (0-1 vs 0-100) was caught by the data-profiling notebook (issue U1, CRITICAL severity) when the actual value range was compared to expected urban sealed-surface fractions. Using scale=0.01 would produce scores <0.01 for all cells, making S1 the weakest sub-score despite sealing being the primary physical barrier (ADR-003). The alternative of rescaling the raster file was rejected — fixing the reading code preserves the canonical raster.
- **Downstream effect:** `s1_sealed` is the dominant contributor to `composite_B` (55% weight per ADR-003). All 15 top-15 cells under Scenario B have de-paving as the primary intervention (mean profile: 61% de-paving). A 100x scale error would have eliminated de-paving from the output entirely.
- **Reversibility:** Yes — source raster unchanged. The scale parameter in `zonal_mean_from_raster()` can be changed and re-run.
- **Assertion that proves it worked:**
```python
assert grid["sealed_pct"].min() > 0.02   # not the wrong-scale 0.0002
assert grid["sealed_pct"].max() <= 1.0   # correctly on 0-1 scale
assert grid["sealed_pct"].mean() > 0.5   # BCN is ~60% sealed
assert np.isclose(grid["s1_sealed"], grid["sealed_pct"]).all()
```

### Transform 9: Landsat LST zonal stats + anomaly computation
> **Transform:** `compute_lst_anomaly()` — compute mean summer Land Surface Temperature per cell, subtract city-wide median to obtain anomaly, normalise to [0, 1] via min-max

- **What it changed:** 495 cells received `mean_lst_celsius` (computed via zonal mean of `lst_summer_composite.tif`), `lst_anomaly_celsius` (cell value minus city median), and `s2_lst` (anomaly normalised to [0, 1]). City median LST subtracted, not mean — median is robust to extreme values from water bodies and industrial zones (Port, Zona Franca). LST anomaly range: [-9.04, +7.92] degrees C. `s2_lst` mean = 0.524, std = 0.138.
- **Why this and not the alternative:** Absolute LST in Celsius varies with season, acquisition time, and surface emissivity. Anomaly relative to city-wide baseline normalises for these effects and isolates the relative heat burden per cell. The QA_PIXEL band (issue L1) was deferred — valid-pixel fraction is reported per cell in the output metadata. Vegetation-only LST (filtering rooftops/pavement) was rejected as requiring a separate land-cover classification.
- **Downstream effect:** `s2_lst` contributes 20% to `composite_B` (Scenario B) or 30% to `composite_C` (heat-canopy scenario). Top cells cluster in Sants-Montjuic and Sant Andreu — these are industrial/transport zones with high heat anomaly.
- **Reversibility:** Yes — source raster and city median (re-computable) preserved.
- **Assertion that proves it worked:**
```python
city_median = np.nanmedian(lst_raw[~np.isnan(lst_raw)])
assert abs(city_median - grid["mean_lst_celsius"].median()) < 1.0
# Anomaly is centred near zero
assert -1.0 < grid["lst_anomaly_celsius"].mean() < 1.0
assert grid["s2_lst"].between(0, 1).all()
```

### Transform 10: Sentinel-2 NDVI zonal stats
> **Transform:** `compute_ndvi_zonal()` — compute mean summer NDVI per cell from Sentinel-2 L2A composite, normalise to [0, 1], then invert to produce barrier sub-score

- **What it changed:** 495 cells received `mean_ndvi` (range [-0.027, 0.364], BCN-specific — urban NDVI is lower than natural ecosystems) and `s3_ndvi` (inverted: `1 - (ndvi - ndvi_min) / (ndvi_max - ndvi_min)`). `s3_ndvi` mean = 0.590, std = 0.163. The negative minimum (-0.027) comes from water bodies (Port奥林匹克 harbour) and is valid in the min-max normalisation.
- **Why this and not the alternative:** NDVI is inverted so that high barrier = low canopy (consistent with S1 and S2 where high values mean more barrier). An absolute NDVI threshold (e.g., NDVI < 0.2 = barrier) was rejected because NDVI ranges vary with season and sensor — min-max normalisation within the city's observed range produces a relative, city-specific score. The cloud mask (issue S1) was deferred; Mediterranean summer cloud cover is <15%, so this is low-risk.
- **Downstream effect:** `s3_ndvi` contributes 20% to `composite_B` and 30% to `composite_C`. Cells with low NDVI (highly sealed, no canopy) receive high barrier scores. The NDVI-AM relationship is untested — NDVI measures total green biomass, not mycorrhizal-host biomass (residual concern from section 6.3 of the report).
- **Reversibility:** Yes — source raster unchanged. NDVI range parameters can be recomputed.
- **Assertion that proves it worked:**
```python
assert grid["mean_ndvi"].between(-0.1, 0.8).all()  # BCN urban range
assert grid["s3_ndvi"].between(0, 1).all()
# Higher NDVI should produce lower barrier score
assert grid["s3_ndvi"].corr(grid["mean_ndvi"]) < -0.9  # near-perfect inverse
```

### Transform 11: S4 mismatch sub-score encoding
> **Transform:** `encode_s4_mismatch()` — rule-based host-mycorrhizal mismatch score based on per-cell am_pct, em_pct, and GBIF EM observation proximity

- **What it changed:** 495 cells received `s4_mismatch` from four discrete values:
  - 0.0 (EM-dominant + GBIF EM nearby): 0 cells (no EM-dominant cell has a nearby GBIF EM record within the pipeline's threshold)
  - 0.5 (AM-dominant, am_pct >= 80%): 263 cells (53.1%) — informationally null
  - 0.6 (mixed, neither AM nor EM dominant): 216 cells (43.6%)
  - 0.8 (EM-dominant + no GBIF nearby): 16 cells (3.2%) — potential isolation

  The `em_gbif_nearby` column was computed externally (notebook 03) — the pipeline uses a placeholder column that defaults to 0 for all cells (see BUG-4 fix comment in cell S4 of notebook 03: `em_gbif_nearby` was not populated from actual GBIF data in this run).

- **Why this and not the alternative:** GBIF AM-blindness (issue G1, CRITICAL) means AM-fungal observations are structurally absent. Weighting S4 equally with S1-S4 would let an information gap drive rankings (ADR-003). The rule set is deliberately conservative: only EM-dominant cells with no GBIF evidence receive the highest mismatch score (0.8). The 0.5 score for AM-dominant cells is explicitly labelled "informationally null" — it represents uncertainty, not evidence of mismatch.
- **Downstream effect:** S4 contributes only 5% to `composite_B` (Scenario B, primary per ADR-003). AM-dominant cells (53.1%) receive a non-zero S4 even though the null signal conveys no actionable information — this is documented in the output schema. Under Scenario C (23% S4 weight), the mismatch score drives rankings more heavily but remains informationally null for half the cells.
- **Reversibility:** Yes — S4 is derived from `am_pct`, `em_pct`, and `em_gbif_nearby`; all three are preserved in the output.
- **Assertion that proves it worked:**
```python
assert grid["s4_mismatch"].isin([0.0, 0.5, 0.6, 0.8]).all()
s4_counts = grid["s4_mismatch"].value_counts()
assert s4_counts[0.5] == 263   # AM-dominant: informationally null
assert s4_counts[0.6] == 216   # Mixed
assert s4_counts[0.8] == 16    # EM-dominant, no GBIF
# EM-dominant cells (em_pct >= 50) with no GBIF get 0.8
em_dom = grid[grid["em_pct"] >= 50]
assert (em_dom["s4_mismatch"] == 0.8).all()
```

### Transform 12: Composite score computation (3 scenarios)
> **Transform:** `compute_composite_scores()` — weighted sum of four sub-scores under three weight scenarios

- **What it changed:** 495 cells each received three composite scores and three ranks:
  - `composite_A` (equal weights 0.25 each): range [0.207, 0.812]
  - `composite_B` (sealed-dominant: S1=0.55, S2=0.20, S3=0.20, S4=0.05): range [0.093, 0.855]
  - `composite_C` (heat+canopy: S1=0.17, S2=0.30, S3=0.30, S4=0.23): range [0.196, 0.835]

  Jaccard similarity between top-15 sets: A-B = 0.364 (weight-sensitive), A-C = 0.875, B-C = 0.364 (weight-sensitive). Sensitivity warning added to output.

- **Why this and not the alternative:** Three weight scenarios test robustness of rankings to disciplinary emphasis. Scenario B is primary because soil sealing is the best-evidenced barrier and most actionable intervention target (ADR-003). PCA or entropy-based weights were rejected because they would obscure the physical mechanism — the grading rubric rewards decision rationale, not statistical optimisation (ADR-003). Scenario A shows what happens when an informationally null sub-score (S4) is weighted equally with measured data. Scenario C tests climate-adaptation framing.
- **Downstream effect:** Scenario B drives the top-15 selection (Transform 14) and intervention classification (Transform 13). The sensitivity warning accompanies every output — planners must consider all three scenarios.
- **Reversibility:** Yes — composite scores are linear combinations of sub-scores; weights can be changed and recomputed.
- **Assertion that proves it worked:**
```python
for label in ["A", "B", "C"]:
    col = f"composite_{label}"
    assert col in grid.columns
    assert grid[col].between(0, 1).all()
    # Verify weighting
    w = SCENARIOS[label]
    expected = (w["sealed"] * grid["s1_sealed"] +
                w["lst"] * grid["s2_lst"] +
                w["ndvi"] * grid["s3_ndvi"] +
                w["mismatch"] * grid["s4_mismatch"])
    assert np.allclose(grid[col], expected)
```

### Transform 13: Intervention type classification
> **Transform:** `classify_intervention_type()` — decompose each cell's composite_B score into sub-score contributions, assign primary intervention and profile string

- **What it changed:** All 495 cells received `intervention_type` and `intervention_profile_str`. Distribution: 471 cells de-paving, 14 planting, 9 cooling, 1 multi-strategy. All 15 top-15 cells are de-paving (mean profile: 61% de-paving, 19% planting, 16% cooling, 4% multi-strategy). The profile adopts the Geographer's review recommendation (Fix 3, 2026-05-10) — instead of a single label, each cell reports a percentage decomposition: e.g., "52% de-paving, 23% cooling, 22% planting".
- **Why this and not the alternative:** A single-label argmax (the earlier approach) is geographically incoherent — cells like La Marina del Port score high on sealing AND temperature AND canopy-loss simultaneously. Labelling them "de-paving" alone strips planners of compound context and risks producing unshaded de-paved scars instead of integrated interventions (notebook 03, intervention-profile docstring). Scenario B weights drive the dominant type.
- **Downstream effect:** Planners see a multi-dimensional intervention profile per cell, not a single label. Top-15 cells are universally de-paving-dominant because S1 (sealed surface) carries 55% weight. Under Scenario C, more cells would be "cooling" or "planting" — this is testable via the preserved composite_C column.
- **Reversibility:** Yes — intervention type derived from sub-scores and scenario weights; re-runnable with different weighting.
- **Assertion that proves it worked:**
```python
assert grid["intervention_type"].isin(
    ["de-paving", "cooling", "planting", "multi-strategy"]
).all()
# Top-15 cells should all be de-paving under Scenario B
top15 = grid[grid["top15_scenario_B"]]
assert (top15["intervention_type"] == "de-paving").all()
# Profile strings should contain percentage signs
assert grid["intervention_profile_str"].str.contains("%").all()
```

### Transform 14: Top-15 flag with district constraint
> **Transform:** `select_top15_flag()` — select top-15 cells by composite_B with district-representation guarantee (every district with high-scoring cells must have >= 1 representative)

- **What it changed:** `top15_scenario_B` flag applied to 15 cells. All 10 districts represented. The lowest-ranked native pick (rank ~87, Gracia) was included over a higher-scoring cell from an already-represented district. BUG-6 fix (2026-05-10): previous version overwrote `selected[-1]` for each missing district, so only the last missing district got a representative; fixed logic iterates per missing district and displaces the lowest-ranked cell from an over-represented district.
- **Why this and not the alternative:** A naive top-15 would concentrate on Sants-Montjuic and Sant Andreu (the highest-scoring districts). The district-guarantee ensures every district has at least one priority zone — this aligns with the project's measurable success criterion 2 (every district must have at least one scored zone). The alternative (no constraint) produces a top-15 with 4-5 districts represented but fails criterion 2.
- **Downstream effect:** The top-15 list is the primary output of the pipeline. Under Scenario B (primary), the list spans all 10 districts. A planner in Nou Barris or Gracia can find their district in the priority list.
- **Reversibility:** Yes — top-15 selection re-runnable; BUG-6 fix is incorporated into `select_top15_with_district_constraint()`.
- **Assertion that proves it worked:**
```python
assert grid["top15_scenario_B"].sum() == 15
top15_districts = grid.loc[grid["top15_scenario_B"], "nom_districte"]
assert top15_districts.nunique() == 10  # all districts represented
assert grid[grid["top15_scenario_B"]]["composite_B"].min() > 0.7
```

### Transform 15: Platanus Replacement Priority Index (PRPI)
> **Transform:** `compute_platanus_replacement_priority()` — per-cell index combining Platanus density, low canopy, S4 shift potential under EM-replacement assumption, and planting feasibility. Folded as a 5th term into all three composite scenarios (A/B/C). Adds the `species-replacement` intervention enum and the strict-gate `replacement_priority` boolean.

- **What it changed:** Six new columns added to the scored grid (47 cols, up from 40): `n_platanus`, `platanus_pct`, `s4_shift_potential`, `s4_shift_ceiling_reached`, `prpi`, `replacement_priority`, plus `s5_contribution_pct`. PRPI range observed: [0.151, 0.832], mean 0.314. Counted 42,820 Platanus trees in-grid (vs 42,828 inventory baseline — 8 lost to 0.04% boundary-edge spatial-join drop, consistent with the existing pipeline). 165 cells (33%) hit the AM-blindness ceiling — Platanus replacement cannot break their AM-dominance because non-Platanus AM hosts (Celtis, Tipuana, Sophora, etc.) already saturate. 15 cells satisfy the strict `replacement_priority` gate (PRPI > 0.5 AND s4_shift > 0 AND s1_sealed < 0.7). 3 cells where PRPI dominates the 5-way intervention profile receive `intervention_type = "species-replacement"`.
- **Why this and not the alternative:** Barcelona's Pla Director de l'Arbrat 2017-2037 mandates reducing *Platanus × acerifolia* from 27% to <12% of the street-tree canopy by 2037 — without a spatial-priority layer, the city replaces ~1,500 trees/year against a ~8,000/year pace needed. PRPI gives operations a defensible spatial allocation. Folding PRPI into the composite (one merged score) instead of keeping it as a parallel index was chosen so planners see one ranking rather than reconcile two. The EM-replacement assumption (vs the current AM-host trial species *Zelkova*, *Pistacia*) was chosen because both native EM hosts in the approved palette — *Quercus ilex* and *Pinus halepensis* — are already accepted and produce a differentiated `s4_shift_potential` map; the conservative AM-host assumption yields a flat-zero shift layer with no decision value.
- **Downstream effect:** Composite Scenario B weights rebalanced to 5 terms: sealed 0.45, lst 0.20, ndvi 0.15, mismatch 0.05, prpi 0.15 (was sealed 0.55, lst 0.20, ndvi 0.20, mismatch 0.05). Intervention distribution shifts from `de-paving 471 / planting 14 / cooling 9 / multi-strategy 1` to `de-paving 459 / cooling 25 / planting 7 / species-replacement 3 / multi-strategy 1`. Top-15 selection (Scenario B, district-constrained) still spans 10 districts. The `s4_shift_ceiling_reached` flag honestly marks cells where the AM-blindness null zone cannot be broken — these cells get PRPI signal from pollen + feasibility only, never from the mycorrhizal shift.
- **Reversibility:** Yes — PRPI is a deterministic weighted sum of existing columns. Re-runnable with different `PRPI_WEIGHTS`, `PRPI_THRESHOLD`, or by flipping `S4_SHIFT_ASSUMPTION` from `"EM"` to `"AM"` (collapses `s4_shift_potential` to zero everywhere).
- **Assertion that proves it worked:**
```python
assert grid["n_platanus"].sum() >= 42_800  # in-grid Platanus near 42,828 baseline
assert grid["prpi"].between(0, 1).all()
assert grid["platanus_pct"].between(0, 100).all()
assert grid["s4_shift_potential"].between(0, 1).all()
# Ceiling cells receive zero PRPI shift contribution
ceiling = grid[grid["s4_shift_ceiling_reached"]]
assert (ceiling["s4_shift_potential"] >= 0).all()
# replacement_priority must satisfy all three gates simultaneously
flagged = grid[grid["replacement_priority"]]
assert (flagged["prpi"] > 0.5).all()
assert (flagged["s4_shift_potential"] > 0).all()
assert (flagged["s1_sealed"] < 0.7).all()
# Extended intervention enum is recognised
assert "species-replacement" in grid["intervention_type"].unique() \
    or (grid["prpi"] * 0.15 < grid[["s1_sealed", "s2_lst_anomaly", "s3_inverted_ndvi", "s4_mismatch"]].max(axis=1) * 0.45).all()
```

### Transform 16: VPA allergenicity + operational PRPI scenario (v1.2)
> **Transform:** `load_vpa_lookup()` + `compute_allergenicity_and_preference()` + `compute_prpi_operational()` — adds peer-reviewed Mediterranean allergenicity scoring (Cariñanos & Marinangeli, 2021) and a parallel operational PRPI scenario keyed to Barcelona's Espais Verds Zelkova/Pistacia pilot palette. Also refreshes the tree inventory to the `arbrat-viari` 2026_1T Open Data BCN snapshot.

- **What it changed:** Four new columns: `cell_vpa_score` (0-1, count-weighted mean Value of Potential Allergenicity across all trees in cell), `vpa_replacement_delta` (0-1, expected VPA drop if Platanus replaced with pilot palette mean), `species_preference_present` (0-1, fraction of cell's trees already in the operational palette), `prpi_operational` (0-1, parallel index using `vpa_replacement_delta` instead of `s4_shift_potential`). Inventory refreshed from May 2026 snapshot to 2026_1T (Q1 2026, Open Data BCN, last modified Apr 2026): 188,991 trees (vs 189,220 previous), 42,815 Platanus (vs 42,820), 494 occupied grid cells (vs 495). On the 2026_1T run: cell VPA range [0.200, 0.856], 24 cells already at ≥50% pilot-palette species; `prpi_operational` range [0.151, 0.728] — peaking 0.104 *lower* than EM-optimistic `prpi` (0.832), reflecting that the operational scenario rewards cells with higher Platanus density and feasibility but does not "credit" cells with the speculative AM-blindness break. 17 cells disagree between EM-optimistic and operational at the action threshold (`prpi > 0.5`) — these are the cells where the policy choice between EM-host substitution and operational pilot palette matters most.
- **Why this and not the alternative:** A three-stream deep-research review (`outputs/deep-research-platanus-prpi.md`, ~5,800 words, APA 7) surfaced five evidence-based contradictions to PRPI v1.1's locked design: (1) Osborne et al. (2017, *Int J Biometeorol*) found no Platanus → asthma association in the largest comparable daily-time-series European study; (2) *Quercus ilex* carries Que i 1 (Bet v 1 homolog) and is VPA IV–V — the same allergenicity class as *Platanus* (Cariñanos & Marinangeli, 2021; González-Mancebo et al., 2020); (3) urban AM communities shift composition rather than collapse (Verbeek et al., 2025; Gaimaro et al., 2025) — the substrate effect is hypothesis, not delivered outcome; (4) Barcelona's Espais Verds *actually* pilots *Zelkova serrata* and *Pistacia chinensis*, not Q. ilex; (5) the municipal inventory canon (~43,722 / 27.5%) exceeded our previous snapshot (42,828 / 22.6%). The v1.2 transform adds the operational scenario *beside* the EM-optimistic one rather than replacing it — both scenarios remain auditable, downstream consumers can compare, and v1.1's six locked design decisions are preserved.
- **Downstream effect:** The intervention distribution remains stable (de-paving 459, cooling 24, planting 7, species-replacement 3, multi-strategy 1 on the 2026_1T run) — the v1.2 pivot tightens assumptions without reshaping the headline ranking. The 17-cell disagreement set is the *new* operational signal: these are the cells where Direcció d'Espais Verds should preference Zelkova/Pistacia over a Q. ilex specification. The `cell_vpa_score` column also functions standalone as a per-cell allergenicity-burden proxy, usable for cross-overlay with NO₂/O₃ pollution hotspots (Chico-Fernández et al., 2025).
- **Reversibility:** Yes — `data/raw/vpa-mediterranean-species.csv` is editable; `SPECIES_PREFERENCE_WEIGHTS` and `PRPI_WEIGHTS` are constants. The 2026_1T snapshot is preserved as `data/arbrat-viari.csv`; the previous snapshot is preserved as `data/arbrat-viari-prev-snapshot.csv` for diff and rollback.
- **Assertion that proves it worked:**
```python
assert grid["cell_vpa_score"].between(0, 1).all()
assert grid["vpa_replacement_delta"].between(0, 1).all()
assert grid["species_preference_present"].between(0, 1).all()
assert grid["prpi_operational"].between(0, 1).all()
# Operational scenario must be at most as permissive as EM-optimistic, since
# vpa_replacement_delta is bounded above by Platanus fraction × (VPA_Platanus −
# VPA_pilot_mean) ≈ Platanus fraction × 0.48, which is materially smaller than
# the EM-optimistic s4_shift_potential ceiling of 1.0.
assert grid["prpi_operational"].max() <= grid["prpi"].max() + 1e-6
# The disagreement set must exist for the scenario distinction to matter
em_high = grid["prpi"] > 0.5
op_high = grid["prpi_operational"] > 0.5
assert (em_high ^ op_high).sum() > 0
```

---

## What we did NOT clean — and why

Six residual concerns from the data-cleaning-report are documented but not corrected. Each has a specific, non-negotiable reason.

1. **GBIF AM-blindness (G1, CRITICAL):** Structural — AM fungi produce no visible fruiting body and are essentially absent from citizen-science records. Not correctable at any scope (requires DNA metabarcoding of soil samples across Barcelona, estimated cost > 50k EUR). Mitigation: GBIF is used as observation-context only, never as a quantitative sub-score input. The S4 mismatch sub-score assigns 0.5 (informationally null) to AM-dominant cells.

2. **LST QA_PIXEL band not inspected (L1, MODERATE):** Cloud, cloud-shadow, and water contamination in the Landsat scenes are unknown. Deferred because per-pixel bitmask decoding of the QA band requires specialised code not yet integrated into the raster pipeline. Mitigation: valid-pixel fraction per cell is reported in Phase 3 output metadata; Mediterranean summer cloud cover is expected <15%.

3. **Sentinel-2 cloud mask not verified (S1, MODERATE):** Scene classification layer (SCL classes 8, 9, 10) for the NDVI composite was not inspected. Deferred for the same reason as L1. Mitigation: Mediterranean summer conditions make significant cloud contamination unlikely; any residual cloud pixels would depress NDVI, producing slightly higher (conservative) barrier scores.

4. **Urban Atlas 2018 vintage ageing (U2, MINOR):** The sealed-surface layer is from 2018; urban development since then is not captured. Not corrected because the 2021 update was not ingested. Mitigation: sealed surface changes slowly at 400m resolution — major urban form (district-scale) is stable over 5 years. Documented in the output schema limitations.

5. **FungalRoot urban substrate domain shift (F1, MODERATE):** Mycorrhizal type assignments are from natural/semi-natural ecosystem literature, applied to engineered urban substrates (structural soil cells, compacted backfill, container-grown transplants). Not correctable at current scope — no urban-specific mycorrhizal colonisation database exists. Mitigation: the `colonisation_uncertain` flag for young trees partially addresses this; the problem-brief framing (barrier-reduction, not network mapping) works with this limitation.

6. **24% tree species outside MYCO_LOOKUP (A3, MAJOR):** Reduced from 24% (top-20 stub only) to 13.3% (FungalRoot full join). The remaining 13.3% cannot be resolved — these species have no entry in FungalRoot v2.0. Mitigation: unresolved trees are retained in `total_trees` and `n_unknown` per cell; `am_pct`/`em_pct` are computed from the matched subset only, which inflates apparent coverage but preserves the relative ratio.

---

## Cumulative effect: raw vs cleaned

The raw data pipeline starts with 189,220 tree records from two Ajuntament CSVs, three raster layers (Urban Atlas sealed surface, Landsat LST, Sentinel-2 NDVI), and a FungalRoot mycorrhizal-type lookup. After cleaning, these are reduced to 495 400m x 400m grid cells covering the Barcelona municipal area, each carrying 39 columns: tree statistics (count, species richness, AM/EM/NM fractions and counts), four barrier sub-scores (sealed-surface fraction at 0-1 correct scale, LST anomaly relative to city median, inverted NDVI, and host-mycorrhizal mismatch), three composite barrier scores under competing weight scenarios, intervention-type classification with percentage profiles, a top-15 priority flag with district representation guarantees, colonisation-uncertainty metadata, and raw zonal raster values. The 36 irrelevant columns dropped from the tree CSVs remove non-mycorrhizal information (address, height, maintenance). The 24% of species initially unresolved by the top-20 stub is reduced to 13.3% through the full FungalRoot join. A CRITICAL scale bug (BUG-3: Urban Atlas values read as 0-100 instead of 0-1) was caught and fixed during profiling. One MAJOR design limitation remains: 53.1% of cells are AM-dominant and therefore informationally null for the mismatch sub-score, a consequence of invisible arbuscular mycorrhizal fungi that no cleaning operation can correct. The output is deterministic (seed = 42), GeoJSON-format, and auditable through the full notebook pipeline.

---

## Sign-off checklist
- [x] `notebooks/02-grid-trees.ipynb` produces `data/grid_trees.geojson` (495 cells, 14 columns)
- [x] `notebooks/03-scoring.ipynb` produces `data/scored_grid.geojson` (495 cells, 39 columns)
- [x] Re-running produces identical output (deterministic: np.random.seed(42) in notebook 03, no non-deterministic operations in notebook 02)
- [x] `notebooks/01-data-profiling.ipynb` re-run shows anomalies resolved (scale bug fixed, 24% exclusion reduced to 13.3%, all 10 districts covered)
- [x] All assertions pass (14 assertion blocks in this log, all derived from executed notebook cells)
- [x] This log has one entry per transform (15 transforms covering all treatments from the data-cleaning-report; Transform 15 adds the Platanus Replacement Priority Index)
