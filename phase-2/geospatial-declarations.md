# Geospatial Declarations — CRS, MAUP, Edge-Buffer Policy

Per CRISP-DM Phase 2 companion Step F. Binds the analysis CRS, areal unit, reprojection methods, and edge-treatment policy for all spatial layers in the Mycorrhizal Barcelona project. Closes **G5**.

**Date:** 2026-05-26

---

## 1. Native CRS per source

| Source | Format | Native CRS | EPSG | Notes |
|--------|--------|-----------|------|-------|
| Ajuntament Trees (lat/lon) | CSV | WGS 84 | EPSG:4326 | Geographic; per-tree point |
| Ajuntament Trees (ETRS89) | CSV | ETRS89 / UTM zone 31N | EPSG:25831 | Projected; x_etrs89, y_etrs89 columns |
| GBIF Fungi | JSON | WGS 84 | EPSG:4326 | Geographic; per-record point |
| BCN Municipal Boundary | GeoJSON | WGS 84 | EPSG:4326 | Geographic; polygon |
| BCN Districts | GeoJSON | WGS 84 | EPSG:4326 | Geographic; 10 MultiPolygons |
| Copernicus Urban Atlas 2018 | FlatGeobuf | ETRS89-extended / LAEA Europe | EPSG:3035 | Projected; Lambert azimuthal equal-area |
| Landsat 8/9 LST | GeoTIFF | WGS 84 / UTM zone 31N | EPSG:32631 | Projected; path 198, row 031 |
| Sentinel-2 L2A | GeoTIFF | WGS 84 / UTM zone 31N | EPSG:32631 | Projected; tile T31TDF |

---

## 2. Chosen analysis CRS

**EPSG:25831 — ETRS89 / UTM zone 31N**

*Justification:*
- ETRS89 is the official European reference frame; UTM31N covers Catalonia.
- The Ajuntament de Barcelona itself uses ETRS89/UTM31N for its spatial data products.
- EPSG:32631 (WGS84/UTM31N) differs from EPSG:25831 by <1m in Barcelona — negligible at 400m decision unit. Landsat and Sentinel-2 data arrive in EPSG:32631; reprojection to EPSG:25831 is a datum shift only (same UTM zone), not a resampling.
- EPSG:3035 (Urban Atlas) covers all of Europe in an equal-area projection — suitable for area calculations but not standard for Barcelona municipal work. Reprojection to EPSG:25831 via bilinear resampling.
- All distance-based calculations (grid generation, buffer operations) use metres in EPSG:25831.

---

## 3. Reprojection methods

| Source | From | To | Method | Rationale |
|--------|------|----|--------|-----------|
| Ajuntament Trees (lat/lon) | EPSG:4326 | EPSG:25831 | Coordinate transform (no resampling) | Vector point data; exact transform |
| GBIF Fungi | EPSG:4326 | EPSG:25831 | Coordinate transform (no resampling) | Vector point data |
| BCN Boundaries | EPSG:4326 | EPSG:25831 | Coordinate transform (no resampling) | Vector polygon data |
| Urban Atlas (sealed surface) | EPSG:3035 | EPSG:25831 | **Bilinear** | Continuous fraction (0–100%); bilinear preserves gradient |
| Landsat LST | EPSG:32631 | EPSG:25831 | **Bilinear** | Continuous temperature field |
| Sentinel-2 NDVI | EPSG:32631 | EPSG:25831 | **Bilinear** | Continuous vegetation index |

**Reprojection tool:** `rasterio.warp.reproject` with `Resampling.bilinear` for rasters; `GeoPandas.to_crs()` for vectors.

**CRS cross-check (deferred to Session 3 notebook 02):** After reprojection, verify all layers align to the same 400m grid origin (xmin, ymin) in EPSG:25831. Pixel-level misalignment >0.5m between layers is a finding.

---

## 4. Areal unit — 400m grid

**Chosen unit:** 400m × 400m grid cells, aligned to the ETRS89/UTM31N (EPSG:25831) origin.

**Justification:** Maps to the Superilla programme's operational intervention scale. The Ajuntament budget cycle allocates funds at roughly this spatial grain. Finer (100m) produces unactionable micro-recommendations; coarser (1km) washes out the barrier signal across heterogeneous urban fabrics.

**Grid generation method:** `numpy.meshgrid` or `rasterio.windows` with origin at `(xmin, ymin)` of the BCN municipal boundary bounding box + 400m buffer, snapped to 400m intervals. Each cell centroid becomes a row in the output GeoJSON (`grid_trees.geojson` + derived scored grid).

---

## 5. MAUP sensitivity statement

*Per Openshaw & Taylor (1979) — the Modifiable Areal Unit Problem.*

**Acknowledged.** The 400m grid is one of many possible aggregations of the same underlying point and raster data. Changing the grid origin, cell size, or shape (e.g., to administrative barris instead of a regular grid) will change the per-zone barrier scores and the resulting priority ranking.

**What was tested:** Nothing yet — the 400m grid is the only unit defined. The decision unit was chosen from the decision-maker's operational context (Superilla scale), not from data convenience.

**What SHOULD be tested (Phase 4 sensitivity):**
- **200m grid** — as a sanity check: do the top-15 priority zones at 400m remain in the top quartile at 200m? If not, the ranking is resolution-sensitive and the claim language must be softened.
- **Barri (neighbourhood) aggregation** — does the priority ranking by barri mean (area-weighted) correlate with the 400m grid ranking at ρ > 0.7? If not, the administrative unit is a confound.

**Minimum reporting standard:** The Phase 4 (Modeling) report must include at minimum one MAUP sensitivity check. If resources preclude a full 200m re-run, report the direction of expected bias (coarser units wash out small-area extremes — our 400m grid may under-detect barrier hotspots smaller than one cell).

---

## 6. Edge-buffer policy

**Problem:** Grid cells at the BCN municipal boundary are partially outside Barcelona. Observations near the edge may belong to a neighbouring municipality (Sant Adrià de Besòs, Santa Coloma de Gramenet, L'Hospitalet, Esplugues) and should not drive Barcelona-specific recommendations.

**Policy (three-tier):**

| Tier | Condition | Action |
|------|-----------|--------|
| **Core** | Cell centroid ≥ 400m inside BCN boundary | No flag. Full analysis. |
| **Edge** | Cell centroid < 400m inside BCN boundary | Flag `edge=True` in output. Report separately from core cells. Include in ranking but with a coverage note. |
| **Outside** | Cell centroid outside BCN boundary | Exclude from analysis. |

**Buffer extent:** 400m (one cell width) inside and outside the municipal boundary.

**Peri-urban reference patch:** The Collserola reference zone is fully inside Barcelona municipality (it IS the northern boundary) but should be flagged as `reference_patch=True`, not `edge=True`. It serves a different analytical role (qualitative anchor, not barrier-score target).

**Implementation:** `notebooks/02-grid-generation.ipynb` must compute the signed distance of each cell centroid from the BCN boundary polygon in EPSG:25831 and assign the tier column.

---

## 7. CRS note on EPSG:32631 vs EPSG:25831

EPSG:32631 (WGS84/UTM31N) and EPSG:25831 (ETRS89/UTM31N) are functionally identical at Barcelona's location — the datum shift between WGS84 and ETRS89 is <1m. Landsat and Sentinel-2 products are distributed in EPSG:32631; the Ajuntament uses EPSG:25831. Reprojecting from 32631→25831 changes the CRS metadata but not the pixel grid. The project standardises on EPSG:25831 for consistency with the municipal data ecosystem.

**EPSG:3035 (Urban Atlas)** is a different projection family (Lambert azimuthal equal-area, not UTM). Reprojection from 3035→25831 involves resampling the 10m grid. This is a genuine transformation — not a metadata-only change.

---

## 8. Declarations sign-off

All spatial layers have native CRS declared. Analysis CRS is EPSG:25831. Areal unit is 400m grid. MAUP is acknowledged and a sensitivity check is planned for Phase 4. Edge-buffer policy defines a three-tier treatment. No spatial layer is silently reprojected — every transformation is recorded above.

**Declared by:** Rafik (Phase 2 companion Step F)
