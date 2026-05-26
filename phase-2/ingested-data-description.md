# Ingested-Data Description — Observed Properties

Per CRISP-DM Phase 2 Task 2 (Describe Data). Values below are **observed from bytes on disk**, not asserted from documentation. When observation disagrees with the data sheet, that disagreement is surfaced as a finding. Closes **G2**.

**Observation date:** 2026-05-26 (companion close-out), except where noted from profiling notebook execution (2026-05-01).

---

## 1. Ajuntament BCN — Street Tree Inventory (Arbrat Viari)

| Property | Observed Value |
|----------|---------------|
| File format | CSV (UTF-8) |
| On-disk size | 43,173,450 bytes |
| Row count | 145,478 |
| Column count | 23 (as loaded by pandas; source CSV has additional columns merged from park inventory) |
| Detected encoding | UTF-8 |
| Observation source | `notebooks/01-data-profiling.ipynb` Cell 3 |

### Column list with inferred dtypes

| Column | Inferred dtype | Non-null % | Observed min | Observed max | Cardinality |
|--------|---------------|-----------|-------------|-------------|------------|
| `codi` | object (str) | 100% | — | — | 145,478 unique |
| `x_etrs89` | float64 | 100% | — | — | — |
| `y_etrs89` | float64 | 100% | — | — | — |
| `latitud` | float64 | 100% | 41.344797 | 41.467776 | — |
| `longitud` | float64 | 100% | 2.088837 | 2.225044 | — |
| `tipus_element` | object (str) | 100% | — | — | 4 unique |
| `espai_verd` | object (str) | ~39.6% | — | — | — |
| `adreca` | object (str) | ~100% | — | — | — |
| `cat_especie_id` | int64 | 100% | — | — | 383 unique |
| `cat_nom_cientific` | object (str) | 100% | — | — | 381 unique |
| `cat_nom_castella` | object (str) | ~98% | — | — | — |
| `cat_nom_catala` | object (str) | ~97.8% | — | — | — |
| `categoria_arbrat` | object (str) | ~100% | — | — | 4 unique |
| `data_plantacio` | object (str) | ~19% | 0013-04-22 (anomaly) | 2026-09-30 (future) | — |
| `tipus_aigua` | object (str) | ~6% | — | — | 3 unique |
| `tipus_reg` | object (str) | ~100% | — | — | 8 unique |
| `catalogacio` | object (str) | ~0.5% | — | — | — |
| `codi_barri` | float64 | ~100% | — | — | — |
| `nom_barri` | object (str) | ~100% | — | — | — |
| `codi_districte` | float64 | ~100% | — | — | 10 unique |
| `nom_districte` | object (str) | ~100% | — | — | 10 unique |
| `source` | object (str) | 100% | — | — | 1 unique ("street") |

### Top-5 species (observed)

| Rank | Species | Count |
|------|---------|-------|
| 1 | *Platanus × acerifolia* | 42,828 |
| 2 | *Celtis australis* | 21,304 |
| 3 | *Tipuana tipu* | 10,748 |
| 4 | *Styphnolobium japonicum* | 9,931 |
| 5 | *Melia azedarach* | 7,248 |

### Disagreements with data sheet

- **Tree count:** Data sheet says "~150,000 street trees"; observed 145,478. Within expected range for quarterly snapshot variation.
- **Species count:** Data sheet says "species-level taxonomy may default to genus." Observed: only 25 records (0.01%) are genus-only (*Washingtonia sp*). Species-level join is feasible — this is a *positive* disagreement (data is better than the data sheet's cautious estimate).

---

## 2. Ajuntament BCN — Park Tree Inventory (Arbrat Zona)

| Property | Observed Value |
|----------|---------------|
| File format | CSV (UTF-8) |
| On-disk size | 14,010,218 bytes |
| Row count | 43,612 |
| Column count | 23 (same schema as street trees, minus `source` column added at concat) |
| Detected encoding | UTF-8 |
| Observation source | `notebooks/01-data-profiling.ipynb` Cell 3 |

### Disagreements with data sheet

- **Tree count:** Data sheet says "~30,000 park trees"; observed 43,612. Significant positive disagreement — park inventory is larger than the data sheet's estimate. Likely reflects recent park-tree planting programmes.

---

## 3. FungalRoot v2.0

| Property | Observed Value |
|----------|---------------|
| File format | CSV |
| On-disk size | 379,211 bytes |
| Row count | Not profiled in notebook (deferred to Session 3 pipeline) |
| Detected encoding | UTF-8 |
| Observation source | `data/fungalroot.csv` on disk; `file` command reports "SPEC" (special/scientific format) |

### Findings

- **Deferred profiling.** FungalRoot was not independently profiled in `01-data-profiling.ipynb`. The join coverage against the tree inventory (381 unique species) should be verified in Session 3 notebook 03. The data sheet asserts ~14,870 plant species coverage — this is asserted, not observed.

---

## 4. GBIF — Fungal Occurrences (Barcelona subset)

| Property | Observed Value |
|----------|---------------|
| File format | JSON (GBIF Occurrence API response) |
| On-disk size | 3,165,654 bytes |
| Record count | 1,023 (per spot-check in `docs/data-quality-audit.md`) |
| Detected encoding | UTF-8 |
| Observation source | `docs/data-quality-audit.md` GBIF spot-check section |

### basisOfRecord breakdown (observed)

| basisOfRecord | Count | % |
|---------------|-------|---|
| HUMAN_OBSERVATION | 1,006 | 98.3% |
| PRESERVED_SPECIMEN | 16 | 1.6% |
| MATERIAL_SAMPLE | 0 | 0.0% |

### Findings

- **Zero DNA-based records.** Confirms the AM-blindness confound: no molecular (DNA metabarcoding) fungal records exist for Barcelona in GBIF.
- **Sample size is workable** (>500 threshold from v1 brief) but citizen-science dominance is total.

---

## 5. Copernicus Urban Atlas 2018

| Property | Observed Value |
|----------|---------------|
| File format | FlatGeobuf (.fgb) |
| On-disk size | 205,988,280 bytes |
| Native CRS | EPSG:3035 (ETRS89-extended / LAEA Europe) — assumed from product spec |
| Observation source | File on disk; not yet loaded in a profiling notebook |

### Findings

- **Not profiled.** The Urban Atlas file exists on disk but was not loaded in `01-data-profiling.ipynb`. Sealed-surface fraction extraction is deferred to Session 3 notebook 02 (grid generation). The data sheet asserts 10m resolution for the sealed-surface layer — this is asserted, not observed.

---

## 6. Landsat 8/9 LST (Summer 2023)

| Property | Observed Value |
|----------|---------------|
| File format | GeoTIFF |
| On-disk size | 3,101,906 bytes (3 files) |
| Native CRS | EPSG:32631 (WGS 84 / UTM zone 31N) — assumed |
| Observation source | Files on disk; not yet loaded in a profiling notebook |

### Findings

- **Not profiled.** LST rasters exist on disk but were not loaded in `01-data-profiling.ipynb`. The data sheet asserts 100m native resolution resampled to 30m — this is asserted, not observed. Valid temperature range and cloud-cover fraction should be verified in Session 3 notebook 02.

---

## 7. Sentinel-2 L2A (Summer 2023)

| Property | Observed Value |
|----------|---------------|
| File format | GeoTIFF |
| On-disk size | 33,453,984 bytes (4 files) |
| Native CRS | EPSG:32631 (WGS 84 / UTM zone 31N) — assumed |
| Observation source | Files on disk; not yet loaded in a profiling notebook |

### Findings

- **Not profiled.** NDVI rasters exist on disk but were not loaded in `01-data-profiling.ipynb`. The data sheet asserts 10m resolution — this is asserted, not observed. Valid NDVI range [-1, 1] and cloud-mask coverage should be verified in Session 3 notebook 02.

---

## 8. BCN Administrative Boundaries

| Property | Observed Value |
|----------|---------------|
| File format | GeoJSON |
| On-disk size | 168,240 bytes (boundary) + 579,935 bytes (districts) |
| Native CRS | EPSG:4326 (WGS 84) — observed in GeoJSON coordinates |
| Observation source | Files on disk |

---

## Cross-reference: data sheet vs. observation disagreements

| Dataset | Data Sheet Claim | Observed | Action |
|---------|-----------------|----------|--------|
| Ajuntament Trees (street) | ~150,000 records | 145,478 | Within quarterly snapshot variation — no action |
| Ajuntament Trees (park) | ~30,000 records | 43,612 | Update data sheet estimate; reflects recent planting |
| Ajuntament Trees (species) | "genus may be the realistic join key" | 0.01% genus-only | Resolved: species-level join is feasible |
| GBIF Fungi | "estimated 200–800 records" | 1,023 records | Above upper estimate — update data sheet |
| FungalRoot | "~14,870 plant species" | Not verified | Deferred to Session 3 |
| Urban Atlas | "10m sealed-surface" | Not verified | Deferred to Session 3 |
| Landsat LST | "100m native, resampled 30m" | Not verified | Deferred to Session 3 |
| Sentinel-2 | "10m resolution" | Not verified | Deferred to Session 3 |

**Date:** 2026-05-26
**Described by:** Rafik (Phase 2 companion close-out)
