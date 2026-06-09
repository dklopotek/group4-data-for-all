# Pivot Product — Data Understanding (CRISP-DM Phase 2)

**Date:** 2026-06-05 (formalized post-build from the acquisition record `data/raw/SOURCES.md`; no new ingestion)
**Product:** Platanus pollen-allergen exposure priority for Barcelona
**Decision unit:** a 400 m analysis cell (≈494-cell grid), reported up to census section / street axis — the unit the city procures against.

## What the decision needs from data

To sequence plane removals by allergen-exposure relief, the product needs three things per cell: **how much plane-pollen a cell emits** (source), **how many people are there to breathe it** (exposure), and **whether the cell is plantable** (feasibility). The equity variant additionally needs **how deprived** the cell's residents are. The honest, decision-shaping question Phase 2 must answer is: *can the available data carry each of these — and what can it NOT carry?*

## Datasets

| # | Dataset | Source / file | Unit | Status | Used for |
|---|---|---|---|---|---|
| 1 | Street-tree inventory (carried from Cycle A) | Open Data BCN `arbrat` → `data/processed/scored_grid.parquet` (`n_platanus`, `platanus_pct`, `trees_young_pct`, `mean_sealed`) | 400 m cell | held, immutable | SOURCE + FEASIBILITY |
| 2 | Residential population | `2026_pad_mdbas.csv` (Padró Municipal, ref. 2026-01-01) | census section (1,068) | acquired | EXPOSURE |
| 3 | Census-section boundaries | `Unitats_Administratives_BCN_geojson/...POLIGONS.json`, EPSG:25831 | 1,068 SEC_CENS polygons | acquired | areal join |
| 4 | Gross income per person | `atles_renda_bruta_persona.csv` (INE Atlas, 2023) | census section (1,068) | acquired | DEPRIVATION (v3) |
| 5 | Antihistamine / respiratory prescriptions | `catsalut_receptes_bcnciutat_respiratori.csv` (CatSalut, ATC R01/R03/R06, 2020–25) | **health region only** (region 79 = Barcelona Ciutat) | acquired | city-wide age/sex calibration only |
| 6 | **Platanus airborne pollen** | XAC / Punt d'Informació Aerobiològica; EAN | station | **NOT AVAILABLE (open, machine-readable)** | would have been external validation |

### Key quantities (verified at source)
- Population total **1,729,963** across 1,068 sections; **99.1%** allocates onto the grid after areal interpolation (`src/exposure_layer.py`).
- Join key = `Codi_Districte.zfill(2) + 3-digit section` → 5-digit string; **1,068/1,068 exact match**, zero unmatched (`data/raw/SOURCES.md`).
- Income: 1,068 sections; missing-income sections imputed with city median (count reported by `src/equity_layer.py` → 0 this run).
- Antihistamines (R06) Barcelona Ciutat 2024 ≈ 636,417 prescriptions; clear female-skew (W:M 1.62) and mid-age peak (45–69).

## The central negative finding (decision-shaping)

**No openly downloadable, machine-readable, station-level Platanus pollen time-series with coordinates exists.** The Catalan aerobiology network (XAC) publishes only a current 0–4 forecast *level* per station; EAN is access-controlled. This is the same discipline as Cycle A: we record what we could not get rather than inventing it. **Consequence:** the SOURCE layer cannot be validated against measured pollen and is declared a *literature-anchored emission proxy* (Gabarra et al. 2002 — *Platanus* ≈ 46% of Barcelona's annual pollen; Maya-Manzano et al. 2017 — per-inflorescence emission ~3–10×10⁶ grains, symptom threshold ~50 grains/m³). This is carried into Phase 5 as the cancellation clause and into the model card as NOT-claim #1.

**Second negative finding:** no allergy/asthma/prescription signal exists below the health-region level (ESCA and CatSalut are city-/region-wide only; privacy). So any "at-risk" weighting must be *modeled from demographics*, never measured — which is exactly why the age-prevalence and sex layers were later rejected as non-mappable (Phase 5).

## Fitness for purpose (quality cross-check)

- **Provenance:** all open municipal/statistical sources (Open Data BCN, INE, CatSalut), CC-BY-compatible. High.
- **Resolution:** population/income at census section (irregular, varying area) → 400 m cell requires **areal-weighted interpolation** (population is a count, not a density). Adequate for sequencing at section/axis scale; not below 400 m.
- **Coverage:** 99.1% of city population allocated; full census-section coverage for income.
- **Currency:** population ref. 2026; income 2023; inventory as held from Cycle A.
- **The gap:** measured pollen and sub-city allergy — both absent, both declared, neither faked.

## MAUP and edge effects (declared)

Results are conditional on the 400 m cell size and the census-section partition. Areal interpolation assumes population is uniformly distributed within each section. The Modifiable Areal Unit Problem applies to every population- and income-derived layer and is restated in the model card limitations.

## Phase-2 conclusion → Phase 3

The data **can** carry a transparent SOURCE × EXPOSURE priority and a decorrelated DEPRIVATION equity layer. It **cannot** carry measured-pollen validation or a measured sub-city allergy signal. Phase 3 therefore builds two transparent layers (plus deprivation for v3), each independently inspectable, with the un-validatable element labelled — not bundled into an opaque composite, which is the Cycle-A failure mode. Handoff target: `data/processed/allergen_layers.parquet`.
