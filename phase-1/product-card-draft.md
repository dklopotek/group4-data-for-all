# Product Card — Mycorrhizal Barcelona: Barrier-Reduction Priority Map

*Adapted from Gebru et al. (2021) Datasheets for Datasets and Mitchell et al. (2019) Model Cards.*

---

## 1. What is this artifact?

A GeoJSON file containing ~200 grid cells (400m × 400m) covering the Barcelona municipal boundary. Each cell carries:
- Four barrier sub-scores (sealed surface, heat anomaly, canopy/NDVI, host–mycorrhizal mismatch)
- A composite barrier index (0–1)
- An intervention-type recommendation (de-paving / planting / species-selection / combined)
- A reference to a documented Ajuntament budget line

The top 15 zones by composite barrier index form the priority shortlist. A peri-urban reference patch (Collserola, 1km²) is included as a low-barrier qualitative anchor, excluded from the priority ranking.

## 2. Intended use

**Decision-support for municipal green-infrastructure capital allocation.** The map helps urban planning analysts at Barcelona Regional and Ajuntament Espais Verds i Biodiversitat answer: *"Given our current Superilla / Eixos Verds budget lines, which 400m zones should we prioritize for de-paving, planting, species-selection, or combined intervention this cycle?"*

## 3. Intended user

- **Primary:** Urban planning analysts and landscape architects at Barcelona Regional
- **Secondary:** Ajuntament de Barcelona, Espais Verds i Biodiversitat team
- **Tertiary (seminar context):** Graduate seminar instructor evaluating CRISP-DM process documentation

## 4. Out-of-scope uses (do NOT use for these)

1. **Regulatory compliance.** This map does not meet any regulatory standard for environmental impact assessment, zoning, or permitting. Do not cite it in legal or regulatory filings.
2. **Property-level decisions.** The 400m resolution is too coarse for parcel-scale, building-scale, or real-estate valuation decisions. A high score for a grid cell does not imply high risk or low value for any individual property within it.
3. **Substitute for site-specific surveys.** The map uses satellite-derived proxies and citizen-science observations. It cannot replace soil sampling, fungal DNA analysis, or on-site ecological assessment before ground-disturbing activities.
4. **Claim of belowground network state.** This map identifies *barriers* (measurable surface conditions). It does not map, measure, or predict the state of mycorrhizal fungal networks belowground.

## 5. Known limitations

1. **AM-blindness.** Arbuscular mycorrhizal fungi — the dominant partners of ~85% of Barcelona's street trees — do not produce visible aboveground fruiting bodies and are therefore invisible to citizen science. The host–mycorrhizal mismatch sub-score is a **categorical flag** ("unconfirmable") for AM-dominant zones, not a quantitative measurement.
2. **No ground-truth validation.** No DNA metabarcoding reference data exists for Barcelona at usable density. The GlobalAMFungi database (Větrovský et al. 2023) has sparse or zero coverage in Iberia. There is no way to verify that barrier reduction will produce mycorrhizal recovery.
3. **Intervention heuristic, not optimizer.** The intervention-type recommendation uses a simple rule ("highest sub-score → corresponding intervention type"). It does not optimize for cost-effectiveness, multi-objective trade-offs, or intervention interactions.
4. **Static snapshot.** Input data vintages vary (tree inventory: 2024-11-12; satellite: summer 2023 composites; Urban Atlas: 2018/2021). The output is valid for a single planning cycle and should be re-run with updated inputs annually.
5. **Peri-urban reference patch is N=1.** The Collserola reference patch is a single qualitative anchor. It cannot support statistical inference about what fungal communities "should" exist in urban Barcelona.
6. **No soil moisture data at decision-unit resolution.** Soil moisture — the single most important driver of mycorrhizal community composition — has no source at 400m or finer. Mitigated by using NDVI + LST as joint surface proxies.
7. **Citizen-science geographic bias.** GBIF fungal observations are concentrated in accessible, high-foot-traffic areas (parks, Collserola trails). Zones with fewer observations may have fewer people, not fewer fungi.

## 6. Provenance summary

| Input | Source | Vintage | Processing |
|---|---|---|---|
| Tree inventory | Open Data BCN (Ajuntament) | 2024-11-12 | Species → FungalRoot join → per-cell mycorrhizal type |
| FungalRoot v2.0 | Soudzilovskaia et al. (2022) | Published 2022 | Species-level lookup table |
| GBIF fungi | GBIF Secretariat | 2015–2024 | Spatial join to grid cells |
| Urban Atlas | Copernicus LMS | 2018/2021 | 10m sealed-surface fraction per cell |
| Landsat LST | USGS | Summer 2023 composite | 100m → resampled, per-cell mean anomaly |
| Sentinel-2 NDVI | Copernicus | Summer 2023 composite | 10m per-cell mean NDVI |
| Administrative boundaries | Open Data BCN | Current | Grid generation, spatial filtering |

Transformations: spatial joins, zonal statistics, min-max normalization, weighted composite scoring. Full pipeline in `notebooks/01–05`.

## 7. Versioning and contact

- **Version:** v1.0-draft (seminar deliverable)
- **Contact:** Project team (see repository)
- **Repository:** `group4-data-for-all`
- **Licence:** CC-BY 4.0
- **Recommended citation:** [Team names]. (2026). *Mycorrhizal Barcelona: Barrier-Reduction Priority Map* [Data product]. Graduate seminar, Data for AI.
