# ADR-001: Canonical Analysis CRS — EPSG:25831 (ETRS89 / UTM zone 31N)

**Status:** ACCEPTED
**Date:** 2026-05-26
**Deciders:** Rafik, Claude (Phase 2 geospatial review)

## Context

Seven adopted sources span four native CRSs:

| Source | Native CRS |
|--------|-----------|
| Ajuntament Trees | EPSG:4326 / EPSG:25831 |
| GBIF Fungi | EPSG:4326 |
| BCN Boundaries | EPSG:4326 |
| Urban Atlas 2018 | EPSG:3035 (ETRS89-LAEA) |
| Landsat 8/9 LST | EPSG:32631 (WGS84 / UTM31N) |
| Sentinel-2 L2A | EPSG:32631 (WGS84 / UTM31N) |

On-the-fly reprojection in QGIS or folium masks the underlying CRS heterogeneity. Every spatial operation (distance, area, buffer) must be performed in a projected CRS to avoid degree-based distortions.

## Decision

**All spatial layers are reprojected to EPSG:25831 at ingest.** This is the official Catalan cartographic reference system (ETRS89 datum, UTM zone 31N, metres).

## Rationale

1. **Metre-based:** Distance thresholds (AM ≤15m, EM ≤35m) are meaningless in degrees.
2. **Official:** EPSG:25831 is the coordinate system used by the Institut Cartogràfic i Geològic de Catalunya (ICGC) and the Ajuntament de Barcelona's own OpenData portal.
3. **Single reprojection:** Each source is reprojected once at ingest. No chain-reprojection that accumulates floating-point error (Atkinson & Curran 1997).
4. **Area-preserving for 400m grid:** UTM is conformal, not equal-area, but distortion at Barcelona's latitude (~41°N) is <0.1% over a 400m cell — negligible for our purpose.

## Consequences

- All GeoJSON outputs carry EPSG:25831 coordinates.
- Web maps (Folium) auto-reproject to EPSG:4326 for display — this is a view transform, not a data transform.
- EPSG:25831 → EPSG:4326 back-transform available via `gdf.to_crs('EPSG:4326')` if needed for external consumption.

## Rejected alternatives

- **EPSG:4326 (WGS84):** Degree-based — distance computations invalid.
- **EPSG:3857 (Web Mercator):** Area distortion at 41°N is ~30% — unacceptable for grid-based areal statistics.
- **EPSG:3035 (ETRS89-LAEA):** Equal-area but non-standard for Catalan municipal data; adds reprojection step for Ajuntament sources.
