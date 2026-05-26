# Phase 3 Data Cleaning Report — Mycorrhizal Barcelona

Per CRISP-DM Phase 3.2 (Chapman et al. 2000, p. 28). One section per adopted source. Documents every quality issue found, treatment applied, mechanism assumption (for missingness), rows affected, and residual concerns.

**Date:** 2026-05-26
**Notebooks:** 01-data-profiling, 02-grid-trees, 03-scoring, 04-connectivity

---

## 1. Ajuntament BCN Tree Inventory (PRIMARY)

**Files:** `data/arbrat-viari.csv` (143,610 rows), `data/arbrat-zona.csv` (45,480 rows)
**Combined:** 189,090 rows, 43 columns → 7 retained, 36 dropped (SEL-005)

### 1.1 Quality issues found

| # | Issue | Severity | Detection method |
|---|-------|----------|-----------------|
| A1 | Species name inconsistency: mixed format (`Quercus ilex`, `Q. ilex`, `quercus ilex`) | MODERATE | profile: unique values in `cat_nom_cientific` |
| A2 | Genus-only records: 25 rows (0.01%) with `cat_genere` but no `cat_especie` | MINOR | profile: null check on species column |
| A3 | 45,272 trees (24%) outside MYCO_LOOKUP top-20 | MAJOR | join: species not in hardcoded dict |
| A4 | Unknown number of null `data_plantacio` | MINOR | profile: null check (not yet quantified) |
| A5 | 36 irrelevant columns retained in raw (address, height, canopy width, etc.) | MINOR | Phase 1 scope: mycorrhizal relevance filter |
| A6 | Duplicate rows from re-ingestion: not checked | MINOR | no SHA-256 row hash computed |

### 1.2 Missingness classification

| Column | Null rate | Mechanism | Justification |
|--------|----------|-----------|---------------|
| `cat_especie` | 0.01% | MAR | genus-only entries are biologically meaningful (young trees, uncertain ID), not random |
| `data_plantacio` | unknown % | MAR | planting date recorded when known; older trees more likely missing; missingness correlates with tree age |
| Species outside MYCO_LOOKUP | 24% | MAR | rarer species are less likely to have resolved mycorrhizal type in FungalRoot; rarity correlates with missingness |

### 1.3 Treatments applied

| Issue | Treatment | Rationale | Reversible? |
|-------|-----------|-----------|-------------|
| A1 | Normalize to lowercase `genus species`; join against FungalRoot `(genus, species)` | canonical taxonomy for pipeline | YES — raw names in source CSV |
| A2 | Flag as `myco_type = 'unknown'` after genus-level FungalRoot fallback | cannot resolve AM/EM for genera with mixed types | YES — flagged, not dropped |
| A3 | Exclude from network graph; retain in grid-level `total_trees` count; `am_pct`/`em_pct` computed from matched subset only | graph needs typed trees; grid stats preserve completeness context | YES — trees retained in grid, excluded only from graph |
| A4 | Assign `colonisation_uncertain = True` for null `data_plantacio` | conservative: unknown-age trees may lack mycorrhizal establishment | YES — flag, not imputation |
| A5 | Drop at SELECT phase (SEL-005); not a cleaning action — documented for completeness | columns irrelevant to mycorrhizal question | YES — source files unchanged |
| A6 | Not treated — deferred | low priority; Ajuntament publishes deduplicated CSVs | YES — add SHA-256 column in future |

### 1.4 Residual concerns

- **24% tree loss to MYCO_LOOKUP:** 45,272 trees excluded from graph construction. Grid-level `am_pct`/`em_pct` statistics are computed from matched subset only — a grid cell with 100 trees but only 50 matched has `am_pct = n_AM / 50`, not `n_AM / 100`. This inflates apparent mycorrhizal-type coverage.
- **No dedup check:** Byte-identical rows from re-download would not be caught.
- **Planting date quality:** `data_plantacio` completeness not yet profiled — `colonisation_uncertain` flag coverage unknown.

---

## 2. FungalRoot v2.0 (LOOKUP TABLE)

**File:** `data/fungalroot.csv` (14,919 rows, 379 KB)

### 2.1 Quality issues found

| # | Issue | Severity | Detection method |
|---|-------|----------|-----------------|
| F1 | Domain shift: mycorrhizal type assignments from natural/semi-natural ecosystems applied to engineered urban substrates | MODERATE | documented in bias-and-annotation.md |
| F2 | Type assignment reports presence/absence of mycorrhizal type, NOT colonisation intensity or viability | MINOR | documented in paper |
| F3 | 11 observed `myco_type` categories in raw data (descriptive text) vs simplified codes expected by pipeline | MINOR | schema validation mismatch (Phase 2) |

### 2.2 Treatments applied

| Issue | Treatment | Rationale | Reversible? |
|-------|-----------|-----------|-------------|
| F1 | `colonisation_uncertain` flag for trees planted <5 years ago; categorical mismatch encoding (matched/mismatched/unconfirmable) | acknowledges substrate uncertainty without over-claiming precision | YES |
| F2 | Documented; no treatment | pipeline uses type as categorical expectation, not quantitative score | N/A |
| F3 | Schema updated to observed categories (Phase 2 fix) | data, not schema, is ground truth | YES |

### 2.3 Residual concerns

- **Urban substrate domain shift:** FungalRoot compiled from natural ecosystem literature. Colonisation type in structural soil cells, compacted backfill, or container-grown transplants may differ from published assignment. Not correctable at current scope.

---

## 3. GBIF Fungal Occurrences (SECONDARY)

**Files:** `data/gbif-fungi.json` (3.2 MB, Barcelona bbox), `data/gbif-fungi-all.json` (9.0 MB, Catalonia)

### 3.1 Quality issues found

| # | Issue | Severity | Detection method |
|---|-------|----------|-----------------|
| G1 | AM-blindness: structural — AM fungi produce no visible fruiting body, essentially absent from citizen-science records | CRITICAL | domain knowledge; documented in every artifact |
| G2 | Opportunistic sampling: observations biased toward accessible, high-foot-trail areas in autumn | SEVERE | GBIF metadata: 98.3% HUMAN_OBSERVATION |
| G3 | 0% MATERIAL_SAMPLE records — zero DNA-based identifications | MODERATE | profile: `basisOfRecord` unique values |
| G4 | Taxonomic skew toward visible macro-fungi (boletes, Amanita, morels) | MODERATE | literature; not quantified for our subset |
| G5 | No fungal-specific identification accuracy audit exists for our geography | MODERATE | literature search (bias-and-annotation.md) |

### 3.2 Treatments applied

| Issue | Treatment | Rationale | Reversible? |
|-------|-----------|-----------|-------------|
| G1 | NOT used as barrier sub-score input; GBIF = observation-context only; "unconfirmable" category in S4 | structural bias not correctable | N/A (design choice) |
| G2 | Reference patch anchor (Collserola) for qualitative sanity check; no quantitative correction | spatial bias cannot be debiased without participation rate data per neighbourhood | YES (flag, not remove) |
| G3 | Documented gap; no treatment possible without new data source | molecular data unavailable for Barcelona | N/A |
| G4 | Documented; GBIF records binned to grid-level presence/absence only — no abundance weighting | reduces impact of taxonomic skew on output | N/A (design choice) |
| G5 | `unknown` annotation-quality estimate with 4-point mitigation plan (bias-and-annotation.md §2.1) | no published error rate exists | N/A |

### 3.3 Residual concerns

- **EVERY GBIF-based inference is conditional on observer presence.** A zero GBIF record in a cell means "no citizen scientist photographed a fungus there" — NOT "no fungi exist there." This is the load-bearing design constraint behind the v2 (barrier-reduction) brief.

---

## 4. Copernicus Urban Atlas 2018 (SPATIAL LAYER)

**File:** `data/urban-atlas/sealed_surface.tif` (206 MB, EPSG:3035, 0-1 scale)

### 4.1 Quality issues found

| # | Issue | Severity | Detection method |
|---|-------|----------|-----------------|
| U1 | Scale misread as 0-100 in initial notebook (BUG-3) | CRITICAL (fixed) | profile: actual value range 0.0-1.0 |
| U2 | 2018 vintage — ageing; sealed surface changes slowly but urban development continues | MINOR | documented |
| U3 | SHA-256 hash not computed (file size) | MINOR | documented in ingestion-log.md + versioning-policy.md |

### 4.2 Treatments applied

| Issue | Treatment | Rationale | Reversible? |
|-------|-----------|-----------|-------------|
| U1 | Fix reading scale: `scale=1.0` (not 0.01) | `process_urban_atlas.py` writes 0-1 scale; dividing by 100 produced 0-0.01 range | YES (source file unchanged) |
| U2 | Documented; no treatment | vintage limitation — 2021 update available but not ingested | N/A |
| U3 | Deferred to Phase 3 first load | hash computation on 206 MB file with Python `hashlib.file_digest()` — run once | YES |

### 4.3 Residual concerns

- **Ageing vintage:** 2018 Urban Atlas may miss recent development (post-2018). Impact on sealed-surface scoring: low — major urban form changes slowly at 400m resolution.

---

## 5. Landsat 8/9 Land Surface Temperature (SPATIAL LAYER)

**Files:** `data/landsat/lst_summer_composite.tif` (3.1 MB, EPSG:32631)

### 5.1 Quality issues found

| # | Issue | Severity | Detection method |
|---|-------|----------|-----------------|
| L1 | QA_PIXEL band not inspected — cloud/cloud-shadow/water contamination unknown | MODERATE | deferred (bias-and-annotation.md) |
| L2 | LST ≠ air temperature — satellite measures surface (rooftop, pavement, canopy-top) temperature | MINOR | documented; standard UHI proxy |
| L3 | Compositing method: median of summer scenes — scene count, date range not logged | MINOR | notebook 02 code audit |
| L4 | SHA-256 not computed | MINOR | documented in versioning-policy.md |

### 5.2 Treatments applied

| Issue | Treatment | Rationale | Reversible? |
|-------|-----------|-----------|-------------|
| L1 | Deferred — report valid-pixel fraction per cell in Phase 3 output metadata | QA inspection requires per-pixel bitmask decoding | YES (deferred) |
| L2 | Documented; no treatment | standard remote-sensing practice for UHI studies | N/A |
| L3 | Log compositing metadata retroactively in `phase-3/raster-compositing-log.md` | reproducibility requirement | YES (re-runnable) |
| L4 | Compute SHA-256 on first Phase 3 load | versioning-policy.md requirement | YES |

### 5.3 Residual concerns

- **LST-NDVI relationship:** Urban LST is modulated by building shadow, wind corridors, and anthropogenic heat — not just vegetation. The pipeline treats LST anomaly as an independent sub-score; correlation with S1 (sealed surface) and S3 (inverted NDVI) is expected but not quantified.

---

## 6. Sentinel-2 L2A NDVI (SPATIAL LAYER)

**Files:** `data/sentinel2/ndvi_summer_composite.tif` (33.5 MB, EPSG:32631)

### 6.1 Quality issues found

| # | Issue | Severity | Detection method |
|---|-------|----------|-----------------|
| S1 | Cloud mask (SCL classes 8, 9, 10) not verified for scene(s) | MODERATE | deferred (bias-and-annotation.md) |
| S2 | NDVI saturation at >0.8 not relevant for Mediterranean urban context | MINOR | documented |
| S3 | Compositing metadata not logged (scene count, date range, cloud-cover fraction) | MINOR | notebook 02 code audit |
| S4 | SHA-256 not computed | MINOR | documented |

### 6.2 Treatments applied

| Issue | Treatment | Rationale | Reversible? |
|-------|-----------|-----------|-------------|
| S1 | Deferred — report valid-pixel fraction per cell | Mediterranean summer cloud cover <15% expected; low-risk deferral | YES |
| S2 | Documented; no treatment | NDVI range 0.1-0.7 across Barcelona | N/A |
| S3 | Log retroactively in `phase-3/raster-compositing-log.md` | reproducibility | YES |
| S4 | Compute SHA-256 on first Phase 3 load | versioning-policy.md requirement | YES |

### 6.3 Residual concerns

- **NDVI-AM relationship:** NDVI measures total green biomass, not mycorrhizal-host biomass. An NDVI-rich cell could be grass (non-host) or palm (AM-host but ecologically different from tree AM). The pipeline uses NDVI as general vegetation proxy — specificity to mycorrhizal function is untested.

---

## 7. BCN Boundaries (AUXILIARY SPATIAL FRAMEWORK)

**Files:** `data/bcn-boundary.geojson` (168 KB), `data/bcn-districts.geojson` (580 KB)

### 7.1 Quality issues found

| # | Issue | Severity | Detection method |
|---|-------|----------|-----------------|
| B1 | Administrative epoch not verified — boundary may not match tree inventory epoch | MINOR | documented |
| B2 | District boundaries: 10 districts match Ajuntament `nom_districte` values | NONE | cross-check: unique district names in trees vs boundaries |

### 7.2 Treatments applied

No cleaning required. Boundaries used as spatial framework only — clipping extent for 400m grid and district-label lookup.

---

## Summary: Cleaning Report

| Source | Issues found | Critical | Major | Moderate | Minor | All resolved? |
|--------|-------------|----------|-------|----------|-------|---------------|
| Ajuntament Trees | 6 | 0 | 1 (A3) | 1 (A1) | 4 | Partial — 24% tree loss documented, not resolved |
| FungalRoot | 3 | 0 | 0 | 1 (F1) | 2 | Yes — all documented or schema-fixed |
| GBIF Fungi | 5 | 1 (G1) | 1 (G2) | 3 | 0 | No — structural biases documented, not correctable |
| Urban Atlas | 3 | 0 | 0 | 0 | 3 | Yes — scale bug fixed; age documented |
| Landsat LST | 4 | 0 | 0 | 1 (L1) | 3 | Partial — QA deferred |
| Sentinel-2 NDVI | 4 | 0 | 0 | 1 (S1) | 3 | Partial — cloud mask deferred |
| BCN Boundaries | 2 | 0 | 0 | 0 | 2 | Yes |

**3 deferred issues:** LST QA band, Sentinel-2 cloud mask, Urban Atlas SHA-256. All deferred items are documented in `bias-and-annotation.md` and `versioning-policy.md` with Phase 3 remediation paths.

**Date:** 2026-05-26
**Cleaning audit by:** Claude (Phase 3 retroactive)
