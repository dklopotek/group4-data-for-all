# Mycorrhizal Barcelona — Data Report

*How every dataset is sourced, processed, and turned into the final priority map.*

A standalone walkthrough for a reader who has never seen this repo. Read top to bottom:
**(1)** what the project does, **(2)** every dataset and where it comes from, **(3)** how the
raw data is cleaned and scored, **(4)** exactly how each input feeds each output.

---

## 1. The one-paragraph story

We built a spatial priority map over Barcelona on a **400 m × 400 m grid**. Original question
(Sessions 1–4): *rank cells for mycorrhizal-fungi recovery, using plane-tree (Platanus)
replacement as the lever.* During evaluation (Session 5) we **falsified our own thesis** — the
index turned out to mostly rank cells by how paved they were, an external biodiversity test came
back a flat null, and the literature didn't support the lever. So in Session 6 we **kept all the
same data and changed the question**: *where should Barcelona sequence its already-committed
plane-tree removals so each cut relieves the most pollen-allergen exposure?* The falsification is
the honest headline; the **shipped product is the pollen-allergen priority map** (`outputs/phase-6/`).

This matters for reading the data: **every dataset below is used twice** — once in the original
mycorrhizal scoring (Phases 1–4), and again, mostly unchanged, in the allergen pivot (Phase 6).

---

## 2. Every dataset (sourced, scored, adopted/rejected)

All candidates were scored on a **7-axis rubric (0–2 each, /14)**: provenance, resolution match,
coverage, license, access reliability, bias clarity, maintenance. Rule: **adopt only if ≥10/14
with no fatal axis**. The "2× rule" means native resolution must be ≤200 m to fully match the
400 m grid. Full survey: `phase-2/data-inventory.md`.

### 2a. Adopted datasets (the ones that drive outputs)

| # | Dataset | Source / provider | Resolution | Score | Role in pipeline | Files |
|---|---------|-------------------|-----------|-------|------------------|-------|
| 1 | **Ajuntament tree inventory** (Arbrat Viari street + Arbrat Zona park) | Open Data BCN (CKAN API), CC-BY 4.0 | per-tree point (~m) | **13/14 PRIMARY** | The load-bearing layer. Every tree → species → grid cell. | `data/arbrat-viari.csv`, `data/arbrat-zona.csv` |
| 2 | **FungalRoot v2.0** | Soudzilovskaia et al. 2022, *New Phytologist* (doi:10.1111/nph.18207) | species-level lookup | 12/14 join table | Converts each tree species → mycorrhizal **type** (AM / EM / NM). Not spatial — a join table. | `data/fungalroot.csv` |
| 3 | **GBIF fungal occurrences** | GBIF Secretariat, CC0/CC-BY | point lat/lon | 12/14 SECONDARY | The "observed fungi" layer — counted per cell. Used as the falsification target in Phase 5. | `data/gbif-fungi.json`, `gbif-fungi-all.json` |
| 4 | **Copernicus Urban Atlas 2018** (sealed surface) | Copernicus Land Monitoring Service (EEA/ESA), free | 10 m raster | **14/14** | Sealed (paved) surface fraction per cell — the dominant barrier-severity input. | `data/urban-atlas/sealed_surface.tif`, `sealed_per_cell.csv` |
| 5 | **Sentinel-2 L2A** (NDVI) | ESA / Copernicus, free | 10 m | **14/14** | Vegetation greenness per cell — a sanity-check / vigour proxy. | `data/sentinel2/ndvi_summer_composite.tif` (from `B04_red`, `B08_nir`) |
| 6 | **Landsat 8/9 thermal** (LST) | USGS / NASA, public domain | 100 m | **14/14** | Land-surface temperature per cell — heat-stress proxy. | `data/landsat/lst_summer_composite.tif` (from `ST_B10_raw`) |
| 7 | **OSM + BCN boundaries/sections** | OSM (ODbL) + Open Data BCN (CC-BY) | sub-m vector | 12/14 | Spatial framework: municipal boundary, district polygons, the grid clip, census-section geometry. | `data/bcn-boundary.geojson`, `bcn-districts.geojson`, `data/raw/Unitats_Administratives_BCN*` |

### 2b. Added for the Phase-6 allergen pivot

| # | Dataset | Source | Resolution | Role | Files |
|---|---------|--------|-----------|------|-------|
| 8 | **Padró population by census section** | Open Data BCN `pad_mdbas`, ref date 2026-01-01, 1.73M residents over 1068 sections | census section | **Exposure layer** — areal-weighted onto the grid to give residents-per-cell. | `data/raw/2026_pad_mdbas.csv` (+ `_sexe`, `_edat-q` breakdowns) |
| 9 | **CatSalut respiratory prescriptions** | Dades Obertes Catalunya `thrd-jj3r`, region 79 = Barcelona Ciutat, 2020–25 | health region (city-wide only) | Age/sex **relative burden** weight for allergic-rhinitis (R06 antihistamines etc.). City-wide only — used as a weight, not a per-cell signal. | `data/raw/catsalut_receptes_bcnciutat_respiratori.csv` |
| 10 | **VPA allergenicity** (Cariñanos & Marinangeli 2021) | published index | species-level | Down-weights high-pollen-allergen species in the replacement palette. | `data/raw/vpa-mediterranean-species.csv` |
| 11 | **Platanus pollen calibration** | Gabarra et al. 2002; Maya-Manzano et al. 2017 (literature) | — | Anchors the pollen-source emission factor. **No open machine-readable pollen series exists** (XAC/EAN are closed), so this is a literature-anchored proxy, not measured pollen. | cited in `data/raw/SOURCES.md` |
| 12 | **Atles de renda** (income per person) | Open Data BCN | census section | Equity layer (Phase-6 equity check). | `data/raw/atles_renda_bruta_persona.csv` |

### 2c. Rejected (documented on purpose — shows the rubric was used)

| Dataset | Score | Why rejected |
|---------|-------|--------------|
| **ERA5-Land** climate reanalysis | 10/14 | **Fatal**: 9 km grid is ~22× coarser than 400 m. One cell covers half the city. Kept only as a city-wide context sentence. |
| **AEMET / Meteo.cat XEMA** stations | 9/14 | Below threshold — only ~5–10 stations in the metro area, too sparse to differentiate zones. |
| **GlobalAMFungi** (AM-fungal DNA) | 10/14 | **Fatal coverage**: near-zero samples in Iberia. Means there is *no* DNA ground-truth for AM fungi in our area — a key limitation. |
| **iNaturalist** | — | Not separately counted: research-grade obs mirror into GBIF (#3), so adopting both would double-count. |

**Known coverage gaps** (documented, not hidden): no soil-moisture/soil-temperature at this scale,
no DNA-confirmed AM-fungal ground truth, no per-tree health/vitality. These are exactly why the
mycorrhizal thesis couldn't be confirmed.

---

## 3. How the raw data is processed

Canonical code is `src/*.py` (notebooks are narrative only). The whole chain:

```
data/ (raw geo layers + CSVs)
   │  src/clean_data.py        ETL + scoring  (17 stages)
   ▼
data/processed/scored_grid.parquet      <-- SINGLE SOURCE OF TRUTH (one row per 400m cell)
   │  src/split_data.py        spatial cluster split (k-means, seed 42)
   ▼
data/splits/{train,eval,test}.parquet
   │  src/train_model.py       baselines + linear model
   ▼
outputs/phase-4/   metrics, model_artifact.joblib, predictions
   │  src/external_validation.py + phase5_robustness.py   (Phase 5 FALSIFICATION)
   ▼
outputs/phase-5/   external_validation_results   (the null that killed the thesis)
   │  src/exposure_layer.py, allergen_*.py, equity_layer.py   (the PIVOT)
   ▼
outputs/phase-6/   allergen_priority_results + priority_zones.csv + maps   <-- SHIPPED PRODUCT
```

### 3a. `clean_data.py` — the 17-stage ETL (where each raw input enters)

1–4. **Tree inventory** (#1): load street + park CSVs, normalise species names, join **FungalRoot**
(#2) to label each tree AM / EM / NM (with a hardcoded top-20 species override for reliability).
5–6. **Build the 400 m grid** clipped to the **BCN boundary** (#7), then spatial-join every tree
into its cell.
7. **Per-cell tree stats**: counts, species richness, AM/EM fractions, **Platanus count**.
8. **GBIF fungi** (#3): count observed occurrences per cell.
9. **Zonal statistics from 3 rasters** — **sealed surface** (#4), **LST** (#6), **NDVI** (#5) —
averaged into each cell. (If `rasterio` is missing the code falls back to synthetic values, flagged.)
10. **Four sub-scores S1–S4** computed per cell (sealed barrier, heat, vegetation deficit, host-fungus mismatch).
11–13. **PRPI** (Platanus Replacement Priority Index) + VPA allergenicity + species-preference palette.
14. **Three composite scenarios A/B/C** (different weightings, below).
15–17. Flag top-15 priority cells, classify intervention type per cell, assert invariants, write output.

The result, `data/processed/scored_grid.parquet`, has **one row per grid cell** with all inputs and
scores side by side. Everything downstream reads only this file — it is frozen and authoritative.

### 3b. Key processing decisions worth knowing

- **CRS**: everything is reprojected to **EPSG:25831** (UTM 31N, metres) so the 400 m grid is true metres.
- **Areal weighting**: population is a *count*, not a density, so census-section population is split into
  grid cells by **overlap area** (handles the Modifiable Areal Unit Problem; declared in the model card).
- **Determinism**: every random step is seeded (k-means seed 42); the test cluster is frozen at split
  time and never inspected until the final assessment.
- **Rejected rows are partitioned, never silently dropped** (Phase-3 cleaning discipline).

---

## 4. How each input maps to each output (the formulas)

### 4a. Original mycorrhizal score (Phases 1–4)

Four sub-scores feed three composite **scenarios** (weights all sum to 1.0):

| Term | Source dataset | Meaning |
|------|----------------|---------|
| `sealed` | Urban Atlas (#4) | paved-surface fraction (barrier severity) |
| `lst` | Landsat (#6) | heat stress |
| `ndvi` | Sentinel-2 (#5) | vegetation deficit (inverted) |
| `mismatch` | Trees + FungalRoot + GBIF (#1,2,3) | host-vs-observed fungal mismatch |
| `prpi` | Trees (Platanus count) + NDVI + feasibility | plane-tree replacement priority |

```
Scenario A (equal):          0.20 each term
Scenario B (PRIMARY, sealed-dominant):  sealed .45 | lst .20 | ndvi .15 | mismatch .05 | prpi .15
Scenario C (eco-dominant):   sealed .15 | lst .25 | ndvi .25 | mismatch .20 | prpi .15
```

**PRPI** itself = `0.40·platanus_density + 0.20·ndvi + 0.20·s4_shift + 0.20·feasibility`, where
feasibility = `1 − sealed` and only cells with sealed < 0.7 are plantable.

**This is where the thesis broke**: Scenario B (the primary one) puts 0.45 weight on `sealed`, so the
"mycorrhizal priority" map was essentially a **paved-surface map** wearing a biodiversity costume —
confirmed in Phase 5.

### 4b. The Phase-5 falsification (what each output proved)

- `src/external_validation.py` → `outputs/phase-5/external_validation_results.*`: tested the score
  against an **independent GBIF target** (`data/processed/gbif_external_target.parquet`). Result: a
  **flat null** — the index did not predict observed fungi. Thesis falsified.
- `src/phase5_robustness.py`: showed the ranking was driven by the `sealed` term, not biology.

### 4c. The shipped allergen product (Phase 6)

Deliberately **simple and transparent — two layers multiplied**:

```
priority = source_std  ×  exposure_std
```

| Layer | Built from | Code |
|-------|-----------|------|
| **source_std** | Plane-tree density per cell × tree maturity (`categoria_maturity`) × VPA allergenicity (#10), min-max standardised | `src/allergen_source.py`, `categoria_maturity.py` |
| **exposure_std** | Residents per cell — Padró population (#8) areal-weighted onto the grid, min-max standardised | `src/exposure_layer.py` |
| feasibility (annotated, not multiplied) | sealed surface (#4) | `src/allergen_priority.py` |

CatSalut prescriptions (#9) supply the **age/sex burden weighting**; income (#12) feeds a separate
**equity check** (`src/equity_layer.py` → `equity_results`). Pollen calibration (#11) anchors the
emission factor but **cannot validate** the product — there is no open measured-pollen series, so the
source layer is honestly labelled a *literature-anchored proxy*.

**Final output** `outputs/phase-6/priority_zones.csv` — one row per priority cell:
```
rank, cell_id, district, plane_density, maturity, exposure_pop, source_std, exposure_std, priority, feasibility
1,    C025_033, NOU BARRIS, 251,        0.9452,   13435.7,      0.512,      0.957,        0.490,    0.234
```

The product was **pre-registered and tested** (`allergen_priority_results.md`): T1 exposure
materially re-orders vs naive plane-density (Spearman 0.89, low top-15 overlap), T2 the two layers
are non-redundant (corr source↔exposure only 0.30), T3 the top-50 cells capture more allergen burden
than density-only or random, T4 the re-ordering holds under sensitivity perturbations.

---

## 5. Where to find everything

| You want… | Read |
|-----------|------|
| Full project narrative (the "bible") | `outputs/reports/crispdm-phase-1-to-6-paper.md` |
| Every dataset scored | `phase-2/data-inventory.md` |
| Exact source URLs / provenance / hashes | `data/raw/SOURCES.md`, `phase-2/ingestion-log.md` |
| The canonical pipeline | `src/clean_data.py` → `split_data.py` → `train_model.py` → `allergen_priority.py` |
| The single source-of-truth table | `data/processed/scored_grid.parquet` |
| The falsification | `outputs/phase-5/external_validation_results.md` |
| The shipped product | `outputs/phase-6/priority_zones.csv` + `outputs/maps/*.html` |
| Honest limitations | `outputs/limitations.md`, model cards `outputs/model-card-*.md` |

**One-line summary for your friend:** *12 public datasets (trees, fungi, satellite greenness, heat,
paved surface, population, health, income) get fused onto a 400 m Barcelona grid; the original
"fungi-recovery" score collapsed under its own validation into a paved-surface proxy, so we honestly
pivoted to a two-layer (plane-tree allergen source × resident exposure) map that says where removing
plane trees relieves the most pollen allergy.*
