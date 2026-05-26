# Datasheet: `scored_grid.geojson` — Barcelona Mycorrhizal Barrier-Reduction Priority Map

Per Gebru et al. (2021): "Datasheets for Datasets." 8 sections. Documents the Phase 3 output dataset for Phase 4 consumption.

**Dataset:** `data/scored_grid.geojson`
**Version:** 1.0.0
**Date:** 2026-05-26

---

## 1. Motivation

**For what purpose was the dataset created?**
To identify 400m × 400m grid cells in Barcelona where physical and ecological barriers most severely limit mycorrhizal fungal network connectivity, and to recommend intervention types (de-paving, cooling, planting) per priority cell.

**Who created the dataset?**
Rafik El Khoury, graduate seminar project (Universitat de Barcelona / Institut de Ciències del Mar). Pipeline implemented in Python (pandas, GeoPandas, rasterstats, NetworkX) across 5 Jupyter notebooks (01–05). Decision audit by Claude (Anthropic).

**Who funded the creation?**
Graduate seminar — no external funding.

**Any other comments?**
This is the v2 (barrier-reduction) deliverable. The v1 (fragmentation) brief was retired after Phase 1 because AM-blindness makes fragmentation unmeasurable with available data. The dataset answers "where should we de-pave to reduce mycorrhizal barriers?" — NOT "how connected is Barcelona's fungal network?"

---

## 2. Composition

**What do the instances represent?**
Each instance is a 400m × 400m grid cell covering Barcelona municipality (EPSG:25831, UTM zone 31N). 495 cells total.

**How many instances?**
495 features (GeoJSON Polygon geometry).

**What data does each instance consist of?**
39 columns (see `phase-3/data-contract.yaml` for full schema):
- **Identifiers:** cell_id, district, barri
- **Geometry:** Polygon in EPSG:25831
- **Tree statistics:** total_trees, n_AM, n_EM, n_unknown, am_pct, em_pct, trees_young_pct, species_richness, expected_myco_type
- **Sub-scores (0-1):** s1_sealed, s2_lst_anomaly, s3_inverted_ndvi, s4_mismatch
- **Composite scores:** composite_score_A, composite_score_B (primary), composite_score_C
- **Intervention:** top15_flag, intervention_type, intervention_profile, colonisation_uncertain
- **Contributions:** s1-s4_contribution_pct
- **Raster values:** mean_sealed, mean_lst_celsius, lst_anomaly, mean_ndvi
- **GBIF:** gbif_records
- **Network:** component_id, component_size
- **Metadata:** cell_bbox_*

**Does the dataset contain all possible instances?**
Yes — 495 cells cover the full Barcelona municipal area within the bounding box. No sampling.

**Is there a label or target?**
No supervised target. The composite score is a constructed index, not a ground-truth label. Phase 4 may derive binary/ordinal targets from the composite score for classification.

**Are there recommended data splits?**
Not yet. Phase 4 must define a spatial cross-validation strategy — random train/test splitting violates spatial autocorrelation (Tobler's Law). Recommended: block k-fold (k=5) on the 400m grid, stratified by district.

**Is there any missing data?**
- `district`/`barri`: null for cells with no tree coverage (edge cells).
- `am_pct`/`em_pct`: null for cells with no matched trees.
- `mean_lst_celsius`/`lst_anomaly`/`mean_ndvi`: null for cells with no valid satellite pixels.
- `component_id`/`component_size`: null for cells with no trees in the network graph.

**Are there any errors, noise, or sources of redundancy?**
See `phase-3/data-cleaning-report.md` and `phase-2/bias-and-annotation.md` for full error inventory:
- S4 mismatch sub-score is 0.5 for 53.1% of cells (AM-dominant) — informationally null.
- 24% of trees excluded from myco_type assignment.
- Cloud mask and QA band not verified for satellite rasters.
- Urban Atlas 2018 vintage may miss post-2018 development.

**Is the dataset self-contained?**
Partially. The GeoJSON contains all scored attributes. Raw tree-level data, satellite rasters, and GBIF records are in `data/`. Network graph outputs are separate files (`network_nodes.geojson`, etc.).

**How was the data collected?**
See Phase 2 artifacts: `data-inventory.md`, `ingestion-log.md` for per-source provenance. All sources are public/open-access.

---

## 3. Collection Process

**How was each instance acquired?**
1. 400m grid generated from BCN bounding box in EPSG:25831 (`notebooks/02-grid-trees.ipynb`).
2. Trees assigned to cells via spatial join (`ST_Within`).
3. Per-cell tree statistics aggregated from tree-level data.
4. Raster zonal statistics extracted via `rasterstats.zonal_stats(cells, raster, stats=['mean'])`.
5. Sub-scores computed per cell (see `phase-3/decisions.md` CON-001 through CON-004).
6. Composite scores computed as weighted sums (CON-005 through CON-008).
7. Top-15 extraction, intervention classification, and output serialisation (`notebooks/03-scoring.ipynb`).

**Who was involved in data collection?**
Tree data: Ajuntament de Barcelona (municipal contractor field surveys). GBIF: citizen scientists (iNaturalist). Satellite: ESA (Sentinel-2), NASA/USGS (Landsat). Urban Atlas: Copernicus / EEA.

**Over what timeframe?**
Tree inventory: snapshot date unknown (Ajuntament publishes quarterly updates). GBIF: records through 2024. Urban Atlas: 2018 reference year. Landsat/Sentinel-2: summer composite (June-August, year unspecified — logged in notebook 02).

**Was any preprocessing/cleaning/labeling done?**
Yes. Full cleaning report: `phase-3/data-cleaning-report.md`. Major steps:
- Species names normalised against FungalRoot.
- 45,272 trees with unresolved myco_type excluded from graph (retained in grid stats).
- Sealed surface scale bug fixed (0-1, not 0-100).
- am_pct/em_pct threshold bug fixed (≥80, not ≥0.8).
- District constraint bug fixed (one cell per missing district).
- Bridge score double-counting bug fixed (distinct component pairs).

---

## 4. Uses

**Has the dataset been used for any tasks already?**
Yes — the Phase 3 pipeline uses it as the primary output. Notebook 05 visualises it in interactive HTML maps.

**What (other) tasks could the dataset be used for?**
- Urban green infrastructure planning (where to de-pave).
- Urban heat island analysis (LST anomaly layer).
- Tree species diversity mapping (species_richness per cell).
- Mycorrhizal host distribution mapping (am_pct, em_pct).
- Zonal statistics baseline for any spatial analysis at Superilla scale.

**Is there anything about the composition or collection that might impact future uses?**
- **AM-blindness:** The S4 mismatch sub-score is structurally limited — AM fungi are invisible to citizen science. Any use of S4 must acknowledge this.
- **AM graph limitation:** Network-derived columns (component_id, component_size) reflect AM connectivity in SANT MARTÍ only, not the full city.
- **No temporal dimension:** Single snapshot. Cannot be used for change-over-time analysis.
- **400m resolution:** Fine enough for Superilla-scale planning, too coarse for street-level or individual-tree intervention design.

**Are there tasks the dataset should NOT be used for?**
- **Mycorrhizal network state assessment** — the dataset measures barriers to connectivity, not actual fungal network presence/absence.
- **Individual tree health diagnosis** — tree-level data is aggregated to grid; individual tree attributes are in raw CSVs.
- **Fragmentation measurement** — the v1 brief was retired for a reason. Do not use this data to claim "Barcelona's fungal network is X% fragmented."
- **Biodiversity assessment** — the dataset maps host-tree expectation, not soil fungal diversity.

---

## 5. Distribution

**How will the dataset be distributed?**
As a GeoJSON file in the project repository (`data/scored_grid.geojson`). Not published to an external repository (graduate seminar scope).

**When will it be distributed?**
Available immediately within the project. No external distribution planned.

**Copyright / License?**
Derived from public/open-access sources:
- Ajuntament BCN OpenData: CC-BY 4.0
- GBIF: CC-BY 4.0 / CC0 (per-record basis)
- FungalRoot: CC-BY 4.0
- Copernicus Urban Atlas: full, free, open access (EU Copernicus regulation)
- Landsat: USGS public domain
- Sentinel-2: ESA free, full, open access

Derived dataset inherits CC-BY 4.0 with attribution to upstream sources.

**Any fees?**
None.

---

## 6. Maintenance

**Who is maintaining the dataset?**
Rafik El Khoury (project author). No institutional maintenance commitment (graduate seminar).

**Will the dataset be updated?**
One-shot snapshot per `phase-2/versioning-policy.md`. No periodic re-ingest planned. On-demand re-ingest possible for GBIF if records are stale.

**Will older versions be supported?**
No versioning beyond git history. Retirement ceremony defined in `versioning-policy.md` §5 if any source is deprecated.

**How can others contribute?**
Not applicable — individual graduate seminar project.

**Is there an erratum mechanism?**
Contact the author. Corrections will be documented in `phase-3/decisions.md` as new SEL/CLN entries.

---

## 7. Legal & Ethical

** Lawyer-readable disclaimer:**
This dataset is a graduate seminar output. It is NOT a professional urban planning tool. Do not base municipal decisions, budget allocations, or environmental impact assessments on this dataset without independent validation.

**Does the dataset contain information that might be considered sensitive?**
No. All data is aggregated to 400m grid cells. No individual tree locations, no personal data, no private property information.

**Does the dataset contain information that might be considered inappropriate?**
No.

**Does the dataset relate to people?**
No. Tree and environmental data only.

**Were any ethical review processes conducted?**
Not applicable — no human subjects, no sensitive data. Graduate seminar project.

**How were ethical concerns around citizen-science data handled?**
GBIF data is public, CC-licensed, and aggregated to grid-cell presence/absence — no individual observer information is exposed. The socioeconomic equity concern (citizen-science participation uneven across neighbourhoods) is documented in `bias-and-annotation.md` and encoded in the pipeline's refusal to use GBIF as a barrier sub-score input.

---

## 8. Caveats & Recommendations

**Caveats for Phase 4 modelers:**

1. **Spatial autocorrelation:** Grid cells are not independent observations. Phase 4 must use spatial cross-validation, not random train/test splits.
2. **Composite score is a constructed index:** No ground-truth "barrier" label exists. Treat composite scores as ordinal rankings, not cardinal measurements.
3. **S4 (mismatch) is information gap, not ecological score:** Weight Scenario B assigns it 5% — any model that elevates S4 as a primary predictor must justify the AM-blindness assumption.
4. **Bridge scores are zero:** The network model produces no inter-component bridging. Barrier reduction is hypothetical — the dataset identifies WHERE intervention would help, not WHETHER it would.
5. **Colonisation uncertainty not triggered:** 0 cells flagged in top-15. The 30% young-tree threshold may be too strict; Phase 4 should test sensitivity to this threshold.
6. **LST anomaly is relative, not absolute:** z-score normalised to city mean. A cell with high LST anomaly may still be cooler than an inland reference — the anomaly is relative to Barcelona, not absolute temperature stress.

**Recommended Phase 4 approaches:**
- Ordinal regression on composite score quintiles (not raw score).
- Spatial block cross-validation (k=5, stratified by district).
- Sensitivity analysis: run all analyses on all three weight scenarios (A/B/C) — report Jaccard stability of top-N priority lists.
- Feature importance: SHAP values with spatial dependence correction.
- Null model: random cell ranking vs Scenario B ranking — test whether the composite score outperforms random.
