# Phase-6 augmentation: Cross-Grain Corroboration + co-benefit + guardrails

> A deployment-layer augmentation of the planner web app, designed by reasoning from the
> project's own central finding. No new data ingestion (frozen-data rule): every new layer is
> a presentation derivation over Phase 1-4 outputs already on disk. Built by `src/section_enrich.py`
> (+ `src/rx_calibration.py` for the exploratory Rx finding); wired into `scripts/build_app_data.py`
> and `outputs/phase-6/app/planner.html`.

## Why (the motivation)

The product exists at two spatial grains that disagree (section vs 400 m; Spearman **0.467**).
Until now that fact lived in a caveat strip. A skeptical grader's standard attack on any
composite-indicator map is "did you test MAUP, and does your ranking survive it?" The augmentation
turns that liability into the headline feature: it makes the grain-disagreement a per-section,
actionable **trust verdict**, and adds the city's actual removal driver (biodiversity) plus a
do-no-harm thermal guardrail.

## 1. Flagship -- Cross-Grain Corroboration (the trust verdict)

For every census section, re-rank by the **400 m people-weighted product** (area-weighted rollup
of cell `source_std * exposure_std`) and compare to the section-grain priority rank. Stamp each
section (top-tercile membership in each grain):

| Verdict | Meaning | Planner action |
|---|---|---|
| **CORROBORATED** (187) | high at BOTH grains | trust -- act first |
| **ARTIFACT** (169) | high at section grain only; 400 m people-weighting demotes it | execution unit only -- do NOT claim priority |
| **UNDERRATED** (169) | low at section grain, high at 400 m | the upside of people-weighting the naive count misses |
| **minor** (543) | not high at either grain | lower tier |

**Correctness gate (enforced in code):** the #1 section (Montjuic, 03024 -- 594 mature planes,
2,031 residents) MUST classify **ARTIFACT** (`rank_400m` = 920), else the badge would lie. The
build asserts this and asserts grain Spearman < 0.9.

**Honesty scope:** corroboration compares two aggregations of the *same* unvalidated pollen
proxy. Agreement raises confidence in the spatial **allocation**; it does **not** validate the
proxy. It is a MAUP-robustness / internal-consistency check, not ground truth. The app states this
on the layer explainer, in the detail badge, and in the help modal.

In the app: a new **Corroboration map layer** (4-colour verdict), a **detail-panel badge** (section
rank vs 400 m rank + verdict sentence + the proxy caveat), a **filter** (isolate any class), and a
**plan-level KPI** -- "% of this plan's modeled relief that is corroborated vs from artifacts." The
KPI immediately flags, e.g., that the co-benefit objective leans ~86% on artifacts (review).

## 2. Co-benefit objective -- the city's ACTUAL driver (monoculture / biodiversity)

The city removes planes for **biodiversity / monoculture-risk** (Pla Director: no species >15%),
not allergy. We had only ever counted Platanus; we now use the **full 286-species inventory** to
compute per section:
- **Platanus share** = section Platanus / section total street trees (the policy-direct signal), and
- **Shannon diversity** H = -sum(p ln p) over all species, normalised (richness/evenness context;
  method inspired by the CoolSpend project's `species_diversity_score`, computed here on this
  project's own inventory).

New objective **co_benefit = priority_std x monoculture_std** -- surfaces sections that serve the
city mandate AND the health co-benefit at once. City plane-share check = 0.2787 (matches the known
~27.5%). Both metrics shown in the detail panel.

## 3. Thermal do-no-harm guardrail

`heat_risk = minmax(LST) * (1 - minmax(NDVI))` from `section_features` (already on disk); top
quartile (267 sections) gets a **Heat-island caution** badge: removing canopy where it is already
hot and bare worsens the urban heat island -- pair removal with immediate replacement, no gaps.
A guardrail, never a priority.

## 4. Exploratory finding -- literature allergy weights vs real Barcelona prescribing

`src/rx_calibration.py` (EXPLORATORY -- NOT a pre-registered T1-T4; reported per the honesty rule).
Compares the vulnerability layer's literature allergic-rhinitis age weights against **real CatSalut
respiratory prescriptions** (R01 nasal + R06 antihistamine), per-capita by broad age band.

**FINDING (reported either way): DIVERGES.** Real allergy-type prescribing per 1,000 rises
monotonically into old age (65+ = **747.8**, the peak), while the literature weight peaks at 20-44
(0.22) and decays to 0.07 at 65+ -- shape Spearman = **-0.40** (anti-correlated). Our vulnerability
layer under-weights older residents. Because that layer was already found REDUNDANT for *ranking*,
this does not move the headline -- but it shows the redundancy is because age structure is ~flat in
space, not because age is uninformative. Calibrating to local Rx would shift vulnerability toward
older neighborhoods, not flatten it.

**Limitation:** CatSalut data is city-wide by age x sex -- it recalibrates the AGE curve, not the
map. Rx is a demand signal (prevalence x severity x polypharmacy x care-seeking), not a prevalence
measurement; elderly polypharmacy inflates counts. R03 (asthma/COPD) reported separately.

## What was deliberately NOT built

- No revival of the failed source-estimator as a "predicted pollen" surface (it failed spatial CV;
  rendering it would re-commit the cardinal sin).
- No street-level ranking (ecological fallacy -- already disclaimed).
- No live pollen/air-quality API (new ingestion; pretends the proxy gap is solved).
- No arbitrary "uncertainty band" on the relief curve -- without a principled perturbation model it
  would be a dishonest decoration; deferred until a defensible width exists.

## Provenance

All inputs are public and already on disk: street inventory (Open Data BCN), census population &
age register (Padro 2026), section polygons (Ajuntament BCN), satellite NDVI/LST, CatSalut
respiratory prescriptions 2024-25. Cost figures are illustrative (CoolSpend; "verify locally").
The pollen source remains an unvalidated proxy -- the one limitation everything else is scoped
around. Deterministic (seed 42); `python src/section_enrich.py` reproduces every number and
re-runs the Montjuic correctness gate.
