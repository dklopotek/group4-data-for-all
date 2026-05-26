# Output Specification

## Format

**GeoJSON** (RFC 7946), with an accompanying CSV for non-spatial consumers.

## Schema

### Geometry

| Field | Type | Description |
|---|---|---|
| `geometry` | Polygon | 400m × 400m grid cell in EPSG:4326 |

### Properties

| Field | Type | Unit | Description |
|---|---|---|---|
| `zone_id` | string | — | Unique grid cell identifier |
| `sealed_surface_pct` | float (0–100) | % | Sealed surface fraction from Urban Atlas 10m |
| `heat_anomaly_c` | float | °C | LST anomaly relative to city baseline |
| `ndvi_mean` | float (−1 to 1) | unitless | Mean NDVI from Sentinel-2 summer composite |
| `myco_type` | string | — | Expected mycorrhizal type: `AM`, `EM`, `mixed`, `unknown` |
| `mismatch_flag` | string | — | `matched` / `mismatched` / `unconfirmable` |
| `barrier_index` | float (0–1) | unitless | Weighted composite of four normalized sub-scores |
| `intervention_type` | string | — | `de-paving`, `planting`, `species-selection`, `combined` |
| `budget_line_ref` | string | — | Reference to documented Ajuntament budget line |
| `sub_score_sealed` | float (0–1) | unitless | Normalized sealed-surface sub-score |
| `sub_score_heat` | float (0–1) | unitless | Normalized heat anomaly sub-score |
| `sub_score_canopy` | float (0–1) | unitless | Normalized canopy/NDVI sub-score |
| `sub_score_mismatch` | float (0–1) | unitless | Normalized mismatch sub-score (categorical encoding) |

## Resolution

- Spatial: 400m × 400m grid cells
- Thematic: Per-zone scores at the grid cell level
- Input data resolution: 10m (Urban Atlas, Sentinel-2), 100m (Landsat LST), per-tree points (inventory), point occurrences (GBIF)

## Coverage

- **Spatial extent:** Barcelona municipal boundary (lat ~41.35–41.47°N, lon ~2.09–2.23°E)
- **Temporal extent:** Single planning-year snapshot. Input data vintages: Urban Atlas 2018/2021, Landsat summer 2023 composite, Sentinel-2 summer 2023 composite, Ajuntament tree inventory snapshot 2024-11-12, GBIF occurrences 2015–2024.

## Refresh cadence

Static output for the current seminar deliverable. Designed for annual re-run: update tree inventory snapshot, pull latest satellite composites, re-run pipeline.

## Distribution mechanism

- Git repository (this repo) for source code and pipeline
- `outputs/priority_zones.geojson` for the output file
- `outputs/maps/priority_map.html` for interactive web map
- `outputs/priority_zones.csv` for non-spatial consumers

## Licence

CC-BY 4.0 (matching the most restrictive input licence — Ajuntament Open Data BCN, ODbL for OSM-derived data)

## FAIR posture

- **Findable:** Output file in a known repository path. Recommended: deposit on Zenodo with DOI for the final version.
- **Accessible:** Git clone + open data inputs (all publicly downloadable).
- **Interoperable:** GeoJSON (RFC 7946) with documented schema. EPSG:4326 CRS.
- **Reusable:** CC-BY 4.0 licence. Product card documents intended use, out-of-scope uses, and known limitations.
