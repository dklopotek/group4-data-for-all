# ADR-002: Integration Resolution — 400m × 400m Grid

**Status:** ACCEPTED
**Date:** 2026-05-26
**Deciders:** Rafik, Claude (Phase 2 data-inventory)

## Context

The project's decision unit, declared in `phase-2/data-inventory.md`, is a 400m × 400m grid over Barcelona. This was chosen as Superilla-compatible: Barcelona's Superilla (superblock) units are approximately 400m × 400m, making the grid directly relevant to urban planning policy.

The coarsest input layer is Urban Atlas at 10m native resolution. The finest is Landsat LST at 30m (resampled from 100m thermal band).

The 2× resolution rule (crispdm-3-data-preparation skill anti-pattern #6) requires that the integration resolution be at least 2× the coarsest input resolution: 2 × 30m = 60m. The 400m grid satisfies this with 6.7× margin.

## Decision

**All analysis is performed at 400m × 400m grid cell resolution, aligned to BCN's bounding box in EPSG:25831.**

Grid origin: `(xmin, ymin)` of BCN boundary in EPSG:25831.
Grid dimensions: derived from `(xmax - xmin) / 400` and `(ymax - ymin) / 400`.
Total cells: 495 covering the Barcelona municipal area.

## Rationale

1. **Superilla alignment:** Barcelona's flagship urban planning intervention operates at ~400m scale. A grid matching this scale produces directly actionable policy recommendations.
2. **2× rule satisfied:** Coarsest input (Landsat 30m) → 400m = 13.3× margin. No scale-mismatch claim vulnerability.
3. **Vector-raster integration:** 400m is large enough to capture meaningful zonal statistics (mean sealed surface, mean LST, mean NDVI) without excessive within-cell variance, and small enough to resolve intra-district variation.
4. **Computational feasibility:** 495 cells is tractable for all operations (cKDTree spatial queries, NetworkX graph construction, Folium rendering).
5. **Modifiable Areal Unit Problem (MAUP):** Sensitivity to grid origin and cell size is documented in `geospatial-declarations.md`. The grid is aligned to the BCN bounding box, not an arbitrary national grid origin — this is a documented choice, not an oversight.

## Consequences

- All vector-to-grid aggregation uses `gdf.sjoin(grid, how='left')` with `ST_Within` predicate.
- All raster-to-grid zonal statistics use `rasterstats.zonal_stats(cells, raster, stats=['mean'])`.
- Output GeoJSONs carry one feature per cell (495 features).
- The 400m resolution is declared in every output metadata field — Phase 4 modelers must not re-grid to finer resolution.

## Rejected alternatives

- **100m grid:** Higher resolution but outputs false precision — Landsat thermal band is 100m native; tree density per 100m cell is sparse (average ~40 trees/cell vs ~382 at 400m).
- **500m grid:** Too coarse — only ~315 cells cover Barcelona, losing intra-district discrimination.
- **Vector-native (per-tree):** Individual-tree analysis is spurious for mycorrhizal networks — fungi operate at soil-patch, not individual-tree scale.
