# Pivot Product — Data Preparation (CRISP-DM Phase 3)

**Date:** 2026-06-05 (formalized from the canonical scripts; raw data immutable, layers regenerable)
**Output:** `data/processed/allergen_layers.parquet` (one row per ≈494 analysis cells)
**Principle:** transparent layers, no opaque composite. Raw is never mutated; every layer is a new, inspectable column built by a deterministic script (seed 42, ASCII-only console).

Walked through the five canonical generic tasks (Select → Clean → Construct → Integrate → Format).

## SOURCE layer — plane-pollen emission proxy  (`src/allergen_source.py`)

- **Select:** from `scored_grid.parquet`, keep `cell_id, district, n_platanus, platanus_pct, total_trees, trees_young_pct, mean_sealed, geometry`.
- **Clean:** `trees_young_pct` missing → filled with column median; clipped to [0,1] after transform.
- **Construct:**
  - `maturity = (1 - trees_young_pct/100)` clipped [0,1] — older/larger planes emit more pollen; cell-level young-share is the only maturity proxy in the inventory (no per-tree trunk diameter; declared as a coarse-proxy limitation).
  - `source_raw = plane_density × maturity`, where `plane_density = n_platanus` (NaN→0).
  - `source_std = minmax(source_raw)`.
- **Retained baseline:** `plane_density` is kept as the **density-only** comparison the priority must beat in Phase 5.

## FEASIBILITY gate  (`src/allergen_source.py`)

- `feasibility = (1 - mean_sealed)` clipped [0,1], `mean_sealed` NaN→median. **Annotation/gate, not a score** — it is reported alongside the ranking, never multiplied into it (a sealed cell can still be a high priority; feasibility tells the planner *how hard* the swap is, not *whether* it matters).

## EXPOSURE layer — receptor population  (`src/exposure_layer.py`)

- **Select/Clean:** population `Valor` → int; key = `Codi_Districte.zfill(2)` + last-3 of `Seccio_Censal` → 5-digit string (leading zeros preserved — string join, never integer).
- **Integrate:** census-section polygons filtered `TIPUS_UA == "SEC_CENS"`, reprojected to **EPSG:25831** (projected metres), merged to population (assert 0 missing).
- **Construct (areal-weighted interpolation):** `gpd.overlay(grid, sections, intersection)`; weight `w = intersect_area / section_area`; `pop_alloc = section_pop × w`; sum per `cell_id`. Population is a **count, not a density**, so areal weighting is required (MAUP declared).
- `exposure_pop` NaN→0; `exposure_std = minmax(exposure_pop)`.
- **Check:** 1,729,963 city pop → **99.1% allocated** to grid; printed for audit.

## DEPRIVATION layer — equity (v3)  (`src/equity_layer.py`)

- **Clean:** income column `Import_Renda*` → numeric; key = `Codi_Districte.zfill(2) + Seccio_Censal.zfill(3)`; missing income → city median (count reported).
- **Integrate (population-weighted, not areal):** income is a **rate, not a count**, so each cell's income = `np.average(section_income, weights=allocated_pop)` over overlapping sections. Falls back to unweighted mean where no population overlaps.
- **Construct:** `deprivation_std = minmax(max_income - cell_income)` → poorest cell = 1, richest = 0.

## AT-RISK layer — built, then REJECTED (v2)  (`src/atrisk_layer.py`)

Built honestly and tested, not silently dropped. `at_risk_section = Σ_band(pop_band × AR_prevalence_band)` with literature-anchored age-prevalence weights (Platanus-sensitized share 0.37 as a constant multiplier → affects scale, not ranking), areal-interpolated to cells. **Phase 5 verdict: redundant with plain population** (Spearman 0.999) because Barcelona's age structure is spatially flat — not added to the shipped product. Recorded as an honest negative, not deleted.

## Integration & format

- All layers join on `cell_id` into a single `allergen_layers.parquet`. CRS forced to EPSG:25831 throughout; `set_crs` applied if absent.
- Determinism: no randomness in layer construction; the only seeded randomness is the RANDOM baseline in Phase 5 (seed 42, 200 draws).
- **Rebuild (one command chain):**
  ```bash
  python src/allergen_source.py && python src/exposure_layer.py && python src/equity_layer.py
  ```

## Data contract (handoff to Phase 4)

| Column | Meaning | Range | Built by |
|---|---|---|---|
| `source_std` | plane-pollen emission proxy, standardized | [0,1] | allergen_source.py |
| `exposure_std` | residential population, standardized | [0,1] | exposure_layer.py |
| `deprivation_std` | inverted income (poorest=1) | [0,1] | equity_layer.py |
| `feasibility` | 1 − sealed (annotation/gate) | [0,1] | allergen_source.py |
| `plane_density` | raw n_platanus (density-only baseline) | ≥0 | allergen_source.py |
| `exposure_pop`, `cell_income`, `maturity` | raw inspectable inputs | — | per script |

CRS EPSG:25831 · cell ≈ 400 m · units: counts (pop), €/person (income), fractions (std). Lineage: `scored_grid.parquet` (Cycle A) + `data/raw/` (population, boundaries, income). Sensitivity: results conditional on cell size and section partition (MAUP).
