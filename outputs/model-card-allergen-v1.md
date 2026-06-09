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

## Deployment grain (Phase 6) — and a grain-dependence finding

The 400 m grain above is the **evidence** grain. For deployment the product was recomputed at the
city's **native census-section grain** (1,068 sections; `src/section_priority.py`) — finer than the
494 cells and the native unit of the population data, so the areal-interpolation step is dropped — and
a per-street removal **worklist** (`src/street_actions.py`, `outputs/phase-6/street_removal_actions.csv`)
was emitted for the top sections. **Honest finding:** at section grain the exposure layer **fails** the
pre-registered re-ordering test it passes at 400 m — Spearman(priority, source) 0.97 (>0.90), T4 holds
in only 1 of 3 arms, and the cell ranking rolls up to the section ranking at only Spearman 0.47. A few
park-like sections with very large mature-plane clusters (rank-1 = **Montjuïc**, 594 mature planes,
~2,000 residents) dominate, so people-weighting washes out at the top. This is the **Modifiable Areal
Unit Problem measured in our own product**: the 400 m map carries the people-weighting evidence; the
section map is the operational unit, where priority is closer to "largest mature clusters first." Both
are shipped with this caveat. **The street worklist is an action/inventory layer only — it carries no
priority or score column (ecological fallacy gate); `suggested_remove` is an illustrative, swappable
policy allocation, not a finding.** Policy anchor (sourced, Pla Director 2017–2037): 43,722 planes =
27.45% of *total urban trees* → 12% by 2037 (~56% cut); we apply that rate (0.563) to the street stock
(→ ~22,757). **The city's stated primary rationale is biodiversity / monoculture disease-risk, not
allergy** — this product optimizes exposure relief as a *co-benefit* of a removal programme run for
other reasons. (The Sant Jordi 2026 nuisance was the plane *fruit*, distinct from the spring *pollen*
modelled here.) See paper §8, §2.4 and `phase-6/section-street-design.md`.

## Trained-model probe (Phase 4, pre-registered) -- why the shipped core is still a composite

We tested whether a trained ML model should join Phase 4 (`phase-6/modeling-ml-design.md`;
deep-research `research/crispdm/04-modeling-ml-options.md`). Three pre-registered models, all reported:
- **#1 Source estimator (supervised):** predict observed mature-plane density from urban-form features
  (no plane-derived inputs). Random-CV R2 0.41/0.44 (Ridge/RF) collapsed to **spatial-CV R2
  -0.25/-0.37** -- urban form does NOT predict historical plane placement. Honest negative; re-enacts
  the Cycle-A leakage trap, this time caught by spatial cross-validation (Roberts 2017, Ploton 2020).
  Confirms the inventory is irreplaceable.
- **#2 Typologies (clustering):** k=4 archetypes (silhouette 0.32, ARI 1.0). **No high-source/high-pop
  archetype exists** -> independently confirms the source-vs-population tension behind the MAUP finding.
- **#3 Hotspots (Gi*/LISA):** 100 significant priority hot-spots, 76 High-High clusters -> defensible
  clusters instead of an arbitrary top-N.

Net: a trained model earns its place only with an observed, independent target AND an honest
generalization test; here the supervised probe failed spatial validation and the unsupervised methods
reinforced the composite. The shipped priority stays a transparent composite. See paper sec 6.5.

## How this product differs from the failed predecessor

The mycorrhizal composite collapsed to a single variable (sealed surface) with its ecological components at effective weight ≈ 0, and was validated against its own ingredients. This product is the structural opposite: **two layers that demonstrably both move the ranking (T2), tested against an external question whose answer was unknown (T1), with its un-validatable element disclosed rather than dressed up.** The lesson from the failure (`docs/failure-and-pivot.md`) is built into the design.

## Reproducibility

`python src/allergen_source.py && python src/exposure_layer.py && python src/allergen_priority.py` from the committed `scored_grid.parquet` + raw population/boundary files. For the deployment grain add `python src/section_priority.py && python src/street_actions.py && python scripts/build_deploy_map.py`. Outputs under `outputs/phase-6/`. Deterministic (seed 42).
