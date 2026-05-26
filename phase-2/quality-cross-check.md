# Quality Cross-Check — Wang & Strong (1996) 15 Dimensions

Per CRISP-DM Phase 2 Task 2. One row per adopted source × one column per Wang & Strong quality dimension. This cross-check makes explicit which dimensions the earn-the-data 5-axis rubric (Provenance, Resolution, Coverage, Licensing, Bias) covers and which it leaves unassessed. Closes **G3**.

## Dimension framework: Wang & Strong (1996) four categories

### Intrinsic DQ (data quality in its own right)
- **DQ1. Accuracy** — correctness of values
- **DQ2. Objectivity** — freedom from bias
- **DQ3. Believability** — regarded as true and credible
- **DQ4. Reputation** — trusted in terms of source or content

### Contextual DQ (quality within the context of the task)
- **DQ5. Value-added** — beneficial for the task
- **DQ6. Relevancy** — applicable for the task
- **DQ7. Timeliness** — sufficiently up-to-date
- **DQ8. Completeness** — not missing; of sufficient breadth and depth
- **DQ9. Appropriate amount of data** — quantity matches task needs

### Representational DQ (quality of the format and meaning)
- **DQ10. Interpretability** — in appropriate language, symbols, units
- **DQ11. Ease of understanding** — clear, simple
- **DQ12. Representational consistency** — same format, compatible with prior data
- **DQ13. Concise representation** — compactly represented

### Accessibility DQ (quality of access)
- **DQ14. Accessibility** — available, retrievable
- **DQ15. Access security** — access controlled appropriately

---

## Cross-check matrix

### Ajuntament BCN Tree Inventory (PRIMARY, 13/14 rubric)

| Dimension | Assessment |
|-----------|-----------|
| DQ1 Accuracy | **assessed:** High — municipal field surveys with trained operators; GPS coordinates verified within BCN bbox (0 OOB records). 6 records have invalid district codes (0.003%). Species ID: 0.01% genus-only. |
| DQ2 Objectivity | **assessed:** Municipal asset register — not an ecological survey. Objectivity is high for what it measures (tree presence/location); low for what it doesn't (tree health, root extent). The bias toward public-realm trees is documented. |
| DQ3 Believability | **assessed:** High. Used in peer-reviewed urban ecology studies. Quarterly publication cadence with correction mechanism. |
| DQ4 Reputation | **assessed:** High. Ajuntament de Barcelona is the canonical source for municipal data within its jurisdiction. CC-BY 4.0 license signals institutional commitment to openness. |
| DQ5 Value-added | **assessed:** Load-bearing. Without this dataset the project does not exist. The expected-mycorrhizal-type layer and host–mismatch sub-score depend on it. |
| DQ6 Relevancy | **assessed:** Directly relevant. The 7 sub-questions all route through this dataset either as primary input (SQ1, SQ5) or as spatial framework (SQ2–SQ4, SQ6–SQ7). |
| DQ7 Timeliness | **assessed:** Adequate. Snapshot vintage 2024-11-12 (~6 months old at analysis time). Quarterly cadence means a newer snapshot is available if needed. Planting dates are 81% missing, limiting temporal depth. |
| DQ8 Completeness | **assessed:** High for public-realm trees (near-census). Structurally incomplete for private-realm trees (gardens, courtyards). Documented in data sheet §8. |
| DQ9 Appropriate amount | **assessed:** More than sufficient. 189,090 records across 10 districts, 381 species. Minimum density ~600 trees/400m cell in the sparsest district. |
| DQ10 Interpretability | **assessed:** Adequate. Field names in Catalan with English glosses provided in data sheet §2. Species names use scientific nomenclature. `tipus_reg`, `categoria_arbrat` values in Catalan — cross-reference needed. |
| DQ11 Ease of understanding | **assessed:** Moderate. CSV format is universally readable. Catalan field names and coded values (e.g. `GOTEIG AVARIAT`) require domain knowledge. Data sheet provides translations. |
| DQ12 Repres. consistency | **assessed:** High. Same schema across street + park files. Coordinates in both WGS84 (lat/lon) and ETRS89/UTM31N. Quarterly snapshots maintain schema stability. |
| DQ13 Concise representation | **assessed:** Adequate. 23 columns, 189k rows, 57MB combined CSV. Redundant columns (Catalan + Castilian common names, lat/lon + UTM coords) add bulk but not ambiguity. |
| DQ14 Accessibility | **assessed:** High. Open Data BCN portal provides CSV/GeoJSON/Shapefile/KML + CKAN API. No authentication required. Stable URLs. |
| DQ15 Access security | **n/a:** Public open data — no access control. |

### GBIF Fungal Occurrences (SECONDARY, 12/14 rubric)

| Dimension | Assessment |
|-----------|-----------|
| DQ1 Accuracy | **assessed:** Variable. Coordinate uncertainty ≤100m for Catalan records (our filter). Taxonomic accuracy depends on observer expertise (citizen-sci) or collection metadata (specimens). iNaturalist research-grade filter adds community verification. |
| DQ2 Objectivity | **assessed:** Low. Documented biases: fruiting-body bias (AM invisible), geographic skew (foot-traffic confound), seasonal skew (autumn-heavy), taxonomic skew (enthusiast taxa). These are structural, not correctable at our scope. |
| DQ3 Believability | **assessed:** Moderate. GBIF is the canonical biodiversity aggregator. Individual records are as credible as their source datasets. The basisOfRecord breakdown (98.3% citizen-science) is a credibility qualifier, not a disqualifier. |
| DQ4 Reputation | **assessed:** High. GBIF is the intergovernmental standard for biodiversity occurrence data. Cited in thousands of peer-reviewed studies. |
| DQ5 Value-added | **assessed:** Contextual. GBIF provides the observation-context layer and enables the peri-urban reference patch comparison. NOT used as a barrier sub-score input — this is a deliberate scope decision. |
| DQ6 Relevancy | **assessed:** Partial. Relevant for host–mismatch context (SQ5). Irrelevant for sealed surface (SQ2), heat (SQ3), NDVI (SQ4). The AM-blindness limit constrains relevance for the dominant AM-host tree subset. |
| DQ7 Timeliness | **assessed:** Adequate. Records span 2015–2024. Aggregation across the full decade window washes out seasonal variation at the analysis level. |
| DQ8 Completeness | **assessed:** Structurally incomplete. No AM-fungal records (invisible to citizen science). No DNA-based records in Barcelona (0 MATERIAL_SAMPLE). This is a known, documented, load-bearing gap. |
| DQ9 Appropriate amount | **assessed:** Workable but thin. 1,023 records across ~100 km² over 10 years = ~2–8 records/km²/decade. Sample size is above the v1 brief's minimum threshold (>500) but too sparse for per-cell statistical inference. |
| DQ10 Interpretability | **assessed:** High. Darwin Core standard is well-documented. GBIF API returns structured JSON with explicit field definitions. |
| DQ11 Ease of understanding | **assessed:** Moderate. Darwin Core is verbose and domain-specific. The data sheet translates key fields for our use case. |
| DQ12 Repres. consistency | **assessed:** High. Darwin Core is a stable, versioned standard. All records share the same JSON structure. |
| DQ13 Concise representation | **assessed:** Adequate. 3.2MB JSON for 1,023 records. Darwin Core is verbose (many fields per record) but well-structured. |
| DQ14 Accessibility | **assessed:** High. Stable REST API + bulk download with citable DOI. No authentication required for public data. Rate limits are documented. |
| DQ15 Access security | **n/a:** Public open data — no access control beyond API rate limiting. |

### FungalRoot v2.0 (AUXILIARY, 12/14 rubric)

| Dimension | Assessment |
|-----------|-----------|
| DQ1 Accuracy | **assessed:** High for mycorrhizal type assignment at species level. Published in *New Phytologist*, compiled from ~36,000 source records with documented methodology. |
| DQ2 Objectivity | **deferred:** The database reports mycorrhizal *type* (AM/EM/ErM/NM/mixed), not colonisation intensity or viability. This limit is documented in the paper. |
| DQ3 Believability | **assessed:** High. Peer-reviewed publication. Canonical reference for plant-mycorrhizal-type lookup in the mycorrhizal ecology literature. |
| DQ4 Reputation | **assessed:** High. Soudzilovskaia et al. (2022) is widely cited. FungalRoot is the standard lookup for this type of analysis. |
| DQ5 Value-added | **assessed:** Essential. The join table that converts tree species → expected mycorrhizal type. Without it, the host–mismatch sub-score cannot be computed. |
| DQ6 Relevancy | **assessed:** Directly relevant. Maps 1:1 to sub-questions 1 and 5 (expected mycorrhizal type, host–mismatch). |
| DQ7 Timeliness | **assessed:** Adequate. v2.0 published 2022. Plant-mycorrhizal type assignments are stable at species level — no annual update needed. |
| DQ8 Completeness | **assessed:** Expected to cover all major BCN tree genera. Coverage against the 381-species inventory to be verified in Session 3 (deferred profiling). |
| DQ9 Appropriate amount | **assessed:** More than sufficient. ~14,870 species — far more than the ~381 species in our inventory. |
| DQ10 Interpretability | **assessed:** High. Simple CSV with species name + mycorrhizal type + source reference. |
| DQ11 Ease of understanding | **assessed:** High. Two-column join structure (species → type). Minimal domain knowledge required. |
| DQ12 Repres. consistency | **assessed:** High. Static CSV. Versioned (v2.0). |
| DQ13 Concise representation | **assessed:** High. 379KB CSV. Compact. |
| DQ14 Accessibility | **assessed:** High. Zenodo mirror is permanent. Journal supplementary materials are open access. |
| DQ15 Access security | **n/a:** Public open access. |

### Copernicus Urban Atlas 2018 (AUXILIARY, 14/14 rubric)

| Dimension | Assessment |
|-----------|-----------|
| DQ1 Accuracy | **assessed:** High. Pan-European harmonised product with published accuracy assessment per vintage. 10m sealed-surface fraction derived from VHR satellite imagery. |
| DQ2 Objectivity | **assessed:** High. Standardised methodology applied uniformly across all European FUAs. |
| DQ3 Believability | **assessed:** High. Used in dozens of urban-ecology and connectivity peer-reviewed studies. |
| DQ4 Reputation | **assessed:** High. Copernicus Land Monitoring Service is an EU operational programme. |
| DQ5 Value-added | **assessed:** High. Provides the sealed-surface fraction input to the composite barrier index. One of four barrier sub-scores. |
| DQ6 Relevancy | **assessed:** Directly relevant for SQ2 (sealed-surface fraction per zone). |
| DQ7 Timeliness | **assessed:** Adequate but ageing. 2018 vintage with 2021 update available. Sealed-surface fraction changes slowly at city scale — 2018 is acceptable for a 2026 snapshot analysis. |
| DQ8 Completeness | **assessed:** Full coverage of Barcelona Functional Urban Area. |
| DQ9 Appropriate amount | **assessed:** More than sufficient. 10m resolution = 40× finer than 400m decision unit. |
| DQ10 Interpretability | **assessed:** Moderate. FlatGeobuf format requires GDAL/GeoPandas. Product documentation is comprehensive. |
| DQ11 Ease of understanding | **assessed:** Moderate. Land-use/land-cover classification requires domain knowledge. Sealed-surface fraction is straightforward (0–100%). |
| DQ12 Repres. consistency | **assessed:** High. Consistent across Copernicus vintages. |
| DQ13 Concise representation | **assessed:** Adequate. 206MB FlatGeobuf. Binary format, not human-readable. |
| DQ14 Accessibility | **assessed:** High. Free download from Copernicus LMS portal. Registration required (light). |
| DQ15 Access security | **n/a:** Public open data — registration gate only. |

### Landsat 8/9 LST (AUXILIARY, 14/14 rubric)

| Dimension | Assessment |
|-----------|-----------|
| DQ1 Accuracy | **assessed:** High. NASA/USGS standard product. Atmospheric correction and emissivity methodology documented in product specification. Known urban canopy limitation (LST ≠ soil temperature). |
| DQ2 Objectivity | **assessed:** High. Instrument-derived measurement with documented algorithms. |
| DQ3 Believability | **assessed:** High. Standard reference for urban heat island studies. |
| DQ4 Reputation | **assessed:** High. NASA/USGS mission with 40+ year Landsat programme heritage. |
| DQ5 Value-added | **assessed:** High. Provides the heat-anomaly input to the composite barrier index. |
| DQ6 Relevancy | **assessed:** Directly relevant for SQ3 (LST anomaly per zone). |
| DQ7 Timeliness | **assessed:** Adequate. Summer 2023 composite — one season behind. Mediterranean summer LST patterns are stable year-to-year. |
| DQ8 Completeness | **assessed:** Full coverage of Barcelona scene (path 198, row 031). Cloud occlusion possible but low in Mediterranean summer. |
| DQ9 Appropriate amount | **assessed:** Adequate. 100m native resolution (4× finer than 400m grid). |
| DQ10 Interpretability | **assessed:** Moderate. GeoTIFF with Kelvin pixel values — unit conversion to °C required. |
| DQ11 Ease of understanding | **assessed:** Moderate. Requires raster processing knowledge (GDAL/rasterio). |
| DQ12 Repres. consistency | **assessed:** High. Landsat Collection 2 is a stable, versioned product. |
| DQ13 Concise representation | **assessed:** High. 3.1MB for 3 GeoTIFFs. Compact. |
| DQ14 Accessibility | **assessed:** High. USGS Earth Explorer + AWS Open Data + Google Earth Engine. |
| DQ15 Access security | **n/a:** USGS public domain data. |

### Sentinel-2 L2A (AUXILIARY, 14/14 rubric)

| Dimension | Assessment |
|-----------|-----------|
| DQ1 Accuracy | **assessed:** High. ESA standard product. Sen2Cor atmospheric correction validated. |
| DQ2 Objectivity | **assessed:** High. Instrument-derived measurement. NDVI is a well-characterised vegetation index. |
| DQ3 Believability | **assessed:** High. Extensively validated since 2015 mission start. |
| DQ4 Reputation | **assessed:** High. ESA/Copernicus flagship optical mission. |
| DQ5 Value-added | **assessed:** High. Provides the canopy/NDVI input to the composite barrier index. Also sanity-checks the tree inventory (catches missing/dead trees). |
| DQ6 Relevancy | **assessed:** Directly relevant for SQ4 (NDVI per zone). |
| DQ7 Timeliness | **assessed:** Adequate. Summer 2023 composite — one season behind. |
| DQ8 Completeness | **assessed:** Full coverage of Barcelona tile T31TDF. Cloud occlusion possible; multi-scene composite mitigates. |
| DQ9 Appropriate amount | **assessed:** More than sufficient. 10m resolution = 40× finer than 400m grid. |
| DQ10 Interpretability | **assessed:** Moderate. GeoTIFF with unitless NDVI values [-1, 1]. |
| DQ11 Ease of understanding | **assessed:** Moderate. Requires raster processing knowledge. |
| DQ12 Repres. consistency | **assessed:** High. Sentinel-2 L2A is a stable, versioned product. |
| DQ13 Concise representation | **assessed:** Adequate. 33MB for 4 GeoTIFFs. |
| DQ14 Accessibility | **assessed:** High. Copernicus Data Space Ecosystem + AWS + GEE + Planetary Computer. |
| DQ15 Access security | **n/a:** Public open data. |

---

## Coverage summary: rubric axes vs. Wang & Strong dimensions

| earn-the-data rubric axis | Wang & Strong dimensions covered | Dimensions NOT covered |
|---------------------------|----------------------------------|------------------------|
| Provenance | DQ3 Believability, DQ4 Reputation | DQ1 Accuracy, DQ2 Objectivity |
| Resolution match | DQ9 Appropriate amount (partial) | DQ8 Completeness (spatial) |
| Coverage | DQ8 Completeness (spatial/temporal) | DQ7 Timeliness |
| Licensing | DQ14 Accessibility (legal) | DQ15 Access security |
| Bias clarity | DQ2 Objectivity | — |

**Gap acknowledged:** The 5-axis rubric covers 8 of 15 Wang & Strong dimensions directly. The remaining 7 (DQ1 Accuracy, DQ7 Timeliness, DQ10–DQ13 representational, DQ15 security) are assessed above for the first time. No dimension is silently omitted.

**Date:** 2026-05-26
**Cross-checked by:** Rafik (Phase 2 companion close-out)
