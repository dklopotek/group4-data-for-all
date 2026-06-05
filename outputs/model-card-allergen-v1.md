# Model Card — Platanus Pollen-Allergen Exposure Priority (v1)

Mitchell et al. (2019) card, adapted for a non-ML analytical product. Companion to `docs/failure-and-pivot.md`, `phase-6/business-understanding.md`, and `phase-6/allergen-validation-design.md`.

## Planner TL;DR

A transparent, two-layer map that ranks Barcelona cells for **where to sequence the city's plane-tree (*Platanus*) reduction so each removal relieves the most pollen-allergen exposure for residents.** It multiplies a **pollen-source** layer (how many mature plane trees) by an **exposure** layer (how many people live there). Accounting for people **changes ~70% of the top-15 priorities** versus the city's naive "replace where planes are densest" rule — e.g. a Nou Barris cell with 251 planes and 13,400 residents outranks a Sant Martí cell with 485 planes but 6,500 residents. **It is not validated against measured pollen** (no open data exists) and **does not predict health outcomes** — it ranks exposure, transparently.

## Model details

- **Type:** deterministic analytical product (no learned model). `priority = source_std × exposure_std`, two transparent min-max layers; feasibility (`1 − sealed`) annotated, not scored.
- **Source layer:** `plane_count × maturity` per 400 m cell, from the Barcelona street-tree inventory. Maturity = `1 − trees_young_pct/100`.
- **Exposure layer:** areal-weighted residential population (Padró 2026; 1.71M residents allocated, 99.1% of city) interpolated to cells.
- **Version:** v1, 2026-06-04. **Built with:** Claude Code (Opus 4.8). Code: `src/allergen_source.py`, `src/exposure_layer.py`, `src/allergen_priority.py`. Deterministic (seed 42).

## Intended use

- **Primary:** help Ajuntament Espais Verds / urban-health planners **sequence** an already-decided, multi-year plane-reduction program (Pla Director de l'Arbrat 2017–2037, 27%→<12%) by modeled allergen-exposure relief, at census-section / axis scale.
- **Users:** municipal green-infrastructure and public-health planners.

## Metrics (pre-registered, `phase-6/allergen-validation-design.md`)

- **T1 — exposure re-orders vs naive density:** Spearman 0.89, top-15 Jaccard 0.30 → **yes** (criterion J15<0.70 & ρ<0.90).
- **T2 — redundancy:** corr(priority,source)=0.80, corr(priority,exposure)=0.64, corr(source,exposure)=0.30 → both layers material, inputs not collinear (**not one variable in a costume**).
- **T3 — burden capture (top-15 / top-50):** priority 0.18 / 0.45 vs density-only 0.13 / 0.35 vs random 0.03 / 0.10 → **margin over the naive rule +4.6 / +9.3 points**.
- **T4 — sensitivity:** the re-ordering verdict holds under uniform maturity, rank-normalization, and min-aggregation.

## Factors

- Geographic: 400 m grid; results reported by district / census section. Sant Martí and Eixample dominate the high-priority set (high plane density × dense residential population).
- The two levers behave differently: dense-but-low-population industrial-edge cells rank lower than moderately-planted dense-residential cells — the intended effect.

## Evaluation & training data

- Street-tree inventory (Open Data BCN, `arbrat`), 230k trees → 494-cell grid.
- Population: Padró Municipal 2026 by census section (1,068 sections), areal-joined.
- No labelled training set; this is an indicator, not a learned model.

## Ethical considerations

- **Equity / at-risk weighting (tested two ways):**
  - *Age-prevalence (rejected):* reweighting population by age-band allergic-rhinitis prevalence (`src/atrisk_layer.py`) was **redundant with plain population** (Spearman 0.999, top-15 Jaccard 0.875) — Barcelona's age structure barely varies in space, so it cannot re-order. Not worth adding (`outputs/phase-6/atrisk_results.md`).
  - *Sex:* women receive ~1.6× the per-capita antihistamine prescriptions of men (`outputs/phase-6/sex_atrisk.md`), but the sex ratio is near-constant across neighbourhoods, so it also adds no mappable signal.
  - *Deprivation / income (adopted as an equity variant, v3):* income is decorrelated from plane density (r = −0.008; `src/equity_layer.py`), so it carries genuine new information. An **equity-weighted variant** lifts the most-deprived-tercile share of the top-15 from **40% → 60% while sacrificing only ~0.5 pp (~3% relative) of total exposure relief** (`outputs/phase-6/equity_results.md`). This is a value choice: v1 (efficiency, max relief) and v3 (equity, relief for the worst-off) are **both reported; the planner chooses**. No sub-city allergy data exists (privacy); all at-risk layers are modeled, not measured.
- **Exposure ≠ harm:** the product ranks *potential exposure*, not diagnosed allergy or clinical impact.

## Caveats and limitations (the NOT list — ≥3 required, 6 given)

1. **NOT validated against measured pollen.** No open machine-readable Barcelona Platanus-pollen series exists; the source layer is a *literature-anchored emission proxy* (Gabarra et al., 2002 — *Platanus* ≈ 46% of Barcelona's annual pollen; Maya-Manzano et al., 2017 — emission factors), spatially un-validated. This is the central limitation, stated plainly.
2. **NOT a health/allergy predictor.** It models exposure potential, not clinical outcomes.
3. **NOT a decision on whether to remove plane trees** — city policy already decides that; this only sequences it.
4. **NOT valid below 400 m** nor for within-cell siting; the grid and the areal population interpolation both carry the Modifiable Areal Unit Problem (results are conditional on cell size and partition).
5. **NOT equity-adjusted** in v1 (all residents equal).
6. **Maturity is a coarse proxy** (cell-level young-tree share, not per-tree trunk diameter); a diameter-based emission estimate would refine the source layer.

## How this product differs from the failed predecessor

The mycorrhizal composite collapsed to a single variable (sealed surface) with its ecological components at effective weight ≈ 0, and was validated against its own ingredients. This product is the structural opposite: **two layers that demonstrably both move the ranking (T2), tested against an external question whose answer was unknown (T1), with its un-validatable element disclosed rather than dressed up.** The lesson from the failure (`docs/failure-and-pivot.md`) is built into the design.

## Reproducibility

`python src/allergen_source.py && python src/exposure_layer.py && python src/allergen_priority.py` from the committed `scored_grid.parquet` + raw population/boundary files. Outputs under `outputs/phase-6/`.
