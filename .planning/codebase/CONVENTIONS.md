# Conventions

_Mapped: 2026-06-04_

---

## Code Style

**Function structure:** Single-responsibility functions with descriptive docstrings. Each function in `clean_data.py` (e.g., `load_tree_inventory`, `build_grid`, `spatial_join_trees_to_grid`) performs exactly one transform stage. Docstrings follow NumPy format with Parameters, Returns, and Example sections.

**Type hints:** Full type annotations using `from __future__ import annotations`. All function signatures declare input and return types (e.g., `def load_fungalroot_lookup(fungalroot_path: Path, ...) -> dict[str, str]`). Collections use generic syntax: `dict[str, float]`, `list[str]`, `pd.DataFrame`, `gpd.GeoDataFrame`.

**Line length:** Soft limit ~88 chars (observed in function signatures and docstrings; hard edges respected). No apparent linter config, so discipline is manual.

**Imports:** Organized into blocks:
  1. `__future__` (e.g., `from __future__ import annotations`)
  2. Standard library (e.g., `json`, `math`, `pathlib`)
  3. Third-party data (e.g., `pandas`, `geopandas`, `scipy`, `rasterio`)
  4. Local modules (e.g., `from baselines import ...`)

Example from `clean_data.py` lines 40–54: warnings suppressed explicitly (`warnings.filterwarnings`), rasterio import wrapped in try/except with graceful fallback flag.

**Docstring discipline:** Every public function has a multi-line docstring (e.g., `clean_data.py` lines 278–324). Docstrings explain the "why", not just the "what". Examples: `_normalise_myco` (lines 472–487), `compute_myco_statistics` (lines 751–825).

---

## Naming

**Files:** Lowercase with underscores (`clean_data.py`, `split_data.py`, `train_model.py`, `baselines.py`). One dataset / stage per file.

**Functions:** Lowercase with underscores, action-oriented verbs: `load_`, `build_`, `compute_`, `assign_`, `normalize_`, `write_`. Private functions prefixed with `_` (e.g., `_normalise_myco`, `_modal`, `_young_pct`, `_species_list_json`).

**Variables:**
  - Boolean flags: `RASTERIO_AVAILABLE`, `em_gbif_nearby`, `s4_shift_ceiling_reached`
  - Percentages (0–100 scale): `am_pct`, `em_pct`, `platanus_pct`, `trees_young_pct`
  - Scores (0–1 scale): `s1_sealed`, `s2_lst_anomaly`, `s3_inverted_ndvi`, `s4_mismatch`, `prpi`, `cell_vpa_score`
  - Counts: `n_AM`, `n_EM`, `n_unknown`, `n_platanus`, `tree_count`, `gbif_records`
  - Centroids / positions: `x`, `y` (in EPSG:25831); `lon`, `lat` (WGS-84 input)
  - Intermediate aggregates: `am_dom`, `em_dom`, `known` (in boolean masks)

**Data artifacts:**
  - Grid cells: `cell_id` (string, e.g., `"C016_011"`; deterministic from grid_size and snapping)
  - District/neighbourhood: `district` or `nom_districte` (Catalan names preserved from inventory)
  - Species: `species_name` (lowercased, normalized), `cat_nom_cientific` (original inventory column)
  - Mycorrhizal types: `myco_type` ∈ `{"AM", "EM", "NM"}`

**Constants:** UPPERCASE, grouped by logical section (e.g., "PATH CONSTANTS" lines 66–87, "CLEANING CONSTANTS" lines 92–136). CRS identifiers explicit: `CRS_PROJ = "EPSG:25831"`, `CRS_GEO = "EPSG:4326"`.

**CRS handling:** Always named and tracked. Input data in `EPSG:4326` (WGS-84, lon/lat), work in `EPSG:25831` (ETRS89 / UTM Zone 31N, metres). Raster inputs reprojected on read. Geometry column preserved for round-trip fidelity.

---

## Script Patterns

**No argparse; all configuration via constants at file top.** `clean_data.py` defines `GRID_SIZE = 400`, `REFERENCE_DATE`, all path roots, thresholds, and weights at module level (lines 66–256). This makes parameters auditable without re-running: grep for `GRID_SIZE` finds all usages.

**Pathlib throughout.** `Path(__file__).resolve().parent` to find project root relative to script location (lines 72–73 in `clean_data.py`). All data paths derived from `PROJECT_ROOT` as `Path` objects, never string concatenation or `os.path.join`.

**`__main__` guard enforced.** Every executable script ends with:
```python
if __name__ == "__main__":
    main()
```
(e.g., `split_data.py` lines 133–134, `train_model.py` lines 230–231). Allows safe imports for testing / reuse.

**Single `main()` function orchestrates the pipeline.** `clean_data.py` main (lines ~5400+) calls the 16 stages in sequence, printing progress checkpoints. `train_model.py` main (lines 159–227) orchestrates baselines, tuning, metrics, and artifact export.

**Graceful fallbacks for missing data:**
  - `RASTERIO_AVAILABLE` flag (lines 57–64) used throughout; missing rasters trigger synthetic Beta/Normal values with explicit warnings (e.g., lines 977–983, 1027–1030).
  - `FungalRoot` CSV absent → hardcoded top-20 stub (lines 435–442).
  - Boundary GeoJSON absent → hardcoded BCN bounding box (lines 562–567).
  - GBIF JSON absent → empty GeoDataFrame (lines 848–853).

All fallbacks are logged so the user knows data provenance.

---

## Data Handling Discipline

**Raw-immutable principle observed:**
  - Input CSVs (`arbrat-viari.csv`, `arbrat-zona.csv`, `fungalroot.csv`, GBIF JSON) read once, never modified in place.
  - Outputs written to `data/processed/` (GeoJSON), `data/splits/` (parquet), `outputs/phase-4/` (metrics CSV, joblib artifacts).
  - No in-place mutations of DataFrames; `.copy()` used liberally (e.g., lines 359, 391, 519, 624, 1012, 1207).

**Rejected rows partitioned with reason_code, not `dropna()`:**
  - Trees with null coordinates: kept in counts, filtered into separate GeoDataFrame via `coord_mask` (lines 625–628 in `build_tree_geodataframe`). No silent drop.
  - Boundary-edge trees not within any cell: counted and logged (lines 669–673).
  - Raster pixels outside cell: caught in exception handler (line 322), cell gets `NaN`, later filled strategically (e.g., line 976: `np.where(np.isnan(sealed_raw), 0.0, sealed_raw)`).

**Decision logs baked into code:**
  - Top-20 hardcoded override (lines 223–247): comment explains "BUG-2 fix", applied AFTER CSV join for safety.
  - `S4_SHIFT_ASSUMPTION = "EM"` (line 177): documented as upper-bound hypothesis, flagged in output column docstring (lines 1189–1196).
  - Species preference weights (lines 195–221): sourced from deep-research (2026-05-26), Cariñanos & Marinangeli (2021), and Barcelona's pilot palette.
  - Composite weights (lines 144–148): per ADR-003, rebalanced to sum to 1.0 across three scenarios (A/B/C).

**Reversible transforms:**
  - Normalizations track raw values: `mean_sealed` stored alongside `s1_sealed`; `mean_lst_celsius`, `lst_anomaly` stored alongside `s2_lst_anomaly`; `mean_ndvi` stored alongside `s3_inverted_ndvi`.
  - PRPI intermediate columns (`platanus_pct`, `s4_shift_potential`, `s4_shift_ceiling_reached`) preserved in output so post-hoc analysis can reweight or recompute.
  - Scores clipped but not transformed: min-max normalisation (lines 1032–1041) uses observed min/max, not assumed bounds. If raster absent, synthetic fallback is explicit.

---

## Error Handling & Logging

**Assertions for critical invariants:**
  - Non-empty outputs: `assert len(out) > 0, "Tree inventory is empty after loading"` (line 363).
  - Null checks: `assert out["myco_type"].notna().all(), "Some trees have null myco_type"` (line 521).
  - Schema conformance: `assert (out["prpi"].between(0, 1)).all(), "PRPI out of [0, 1] range"` (line 1249).
  - Weight sums: `assert abs(sum(w.values()) - 1.0) < 1e-6, f"PRPI_WEIGHTS sum to ..."` (line 1246–1248).

Assertions are **not** used for user-facing validation (e.g., missing file). Instead, graceful fallback or explicit warning.

**Print statements for progress; no logging module.** Each function prints a status line with its name in brackets:
```python
print(f"  [load_fungalroot_lookup] Loaded {len(out):,} species mappings")
print(f"  [spatial_join] {total - matched:,} trees not within any cell")
```
This makes pipeline checkpoints visible in stdout. Main orchestrator (`clean_data.py` main) calls stages and indents output.

**No try/catch for user errors.** File not found → `FileNotFoundError` propagates (users will see it). This is intentional: it forces downstream attention to missing data rather than silent degradation.

**Exception handling only for optional features:**
  - Rasterio import (lines 57–64): caught if not installed; functionality degrades gracefully.
  - Raster read (lines 315–323): try/except per-cell to skip nodata / out-of-bounds; cells get `NaN`.

---

## Geospatial Conventions

**CRS declared explicitly at every stage:**
  - Input: `CRS_GEO = "EPSG:4326"` (lines 97–98) when loading CSV with lon/lat.
  - Work: `CRS_PROJ = "EPSG:25831"` (line 96) for all geometric operations (grid, spatial join, distance).
  - Raster: on read, check `src.crs` and reproject input GeoDataFrame if mismatch (lines 312–313).
  - Output: `crs=crs` parameter passed to `GeoDataFrame()` constructor (e.g., line 594, 628, 875).

**Grid design locked:**
  - Size: `GRID_SIZE = 400` metres (line 95), matches Barcelona's Superilla block width.
  - Snapping: cells aligned to multiples of `grid_size` from origin (lines 570–573), so grid is deterministic across runs.
  - Cell naming: `f"C{x_index:03d}_{y_index:03d}"` (lines 585–587), reproducible from (xi, yi) origin.

**Centroid vs. bounding-box:**
  - Grid cells stored as Polygons (full 400m² extent).
  - Spatial indexing uses `geometry` (polygon intersection, "within" predicate).
  - Baseline uses cell bounding-box midpoint as centroid (lines 74–76 in `baselines.py`), not geometry.centroid.

**Resolution conventions:** Raster inputs assumed to be summer composites (Landsat LST, Sentinel-2 NDVI) at standard Planetary Computer resolution (~30m). Zonal mean aggregates to cell level (lines 278–324). No resampling; "illustrative" fallback is raw synthetic value at cell level.

---

## Documentation Conventions

**Markdown discipline in notebooks:** Phase 3 notebooks (`notebooks/01-*.ipynb` through `05-*.ipynb`) follow markdown-first structure: each section has a header, narrative text, then code cells. Markdown cells explain the "why"; code cells implement specifics.

**Phase ADRs:**
  - `phase-3/adrs/` : architectural decisions (e.g., species normalization, grid design, FungalRoot override logic).
  - `phase-3/decisions.md` : end-to-end log of all data-cleaning and encoding choices.
  - `phase-3/data-contract.yaml` : formal schema for scored_grid output (columns, types, nullability, ranges, rationale).
  - `phase-4/analytical-question.md` : feature engineering rationale, leakage check, target definition.
  - `phase-4/test-design.md` : pre-registered test plan (split, baselines, metrics, pass/fail criteria, sensitivity grid).

**Comments in code:** Reserved for WHY, not WHAT. Example: lines 217–220 in `compute_platanus_replacement_priority` explain the assumption trade-off (EM vs. AM swap). Comments avoid duplicating docstrings.

**README structure (implicit, see project root):** User runs `python src/clean_data.py` to stage Phase 3 → Phase 4. Then `python src/split_data.py` to stage Phase 4 train/eval/test. Then `python src/train_model.py` to build model. Each script prints progress; no CLI args.

**README.md should document:**
  - Data provenance (Ajuntament Open Data snapshot date, FungalRoot version, GBIF query bounds).
  - Running the pipeline (step-by-step command examples).
  - Output files (where they live, what columns they have).
  - Phase-3 / Phase-4 design decisions (cross-link to ADRs).

---

## Summary Table

| Aspect | Practice |
|--------|----------|
| **Function structure** | Single responsibility; NumPy docstrings; type hints everywhere |
| **Naming** | Lowercase with underscores; action verbs for functions; UPPERCASE for constants; percentages (0-100), scores (0-1) |
| **Configuration** | All constants at module top; no argparse |
| **Paths** | Pathlib; relative to PROJECT_ROOT derived from `__file__` |
| **Data immutability** | Read once; `.copy()` before mutation; rejected rows logged, not dropped |
| **Reversibility** | Raw values stored alongside normalized; all transforms trackable |
| **Assertions** | Invariants only (non-empty, non-null, range checks); not user-facing validation |
| **Logging** | Print with function name in brackets; no `logging` module |
| **Errors** | Fail fast for user errors; graceful fallback for optional features |
| **CRS** | Always named; input EPSG:4326, work EPSG:25831, checked on read/write |
| **Grid** | 400m × 400m, snapped to origin, deterministic cell IDs |
| **Markdown** | Section headers + narrative + code; ADRs document decisions; data contract formalizes schema |

