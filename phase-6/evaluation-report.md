# Pivot Product — Evaluation Report & Planner Verdict (CRISP-DM Phase 5)

**Date:** 2026-06-05
**Pre-registered design:** `phase-6/allergen-validation-design.md` (written before any result — binding).
**Raw results:** `outputs/phase-6/allergen_priority_results.{md,json}`, `equity_results.{md,json}`, `atrisk_results.md`, `sex_atrisk.md`.
**Companion:** `outputs/model-card-allergen-v1.md`.

This is the readable verdict that folds every pre-registered test — including the unfriendly ones — into one decision. Per the project's binding rule, every pre-registered test ran and every result is reported.

---

> **Orienting note (Chapman et al. 2000, pp. 28/30):** Phase 4 asked *did the model work?*; Phase 5 asks *did the pipeline answer the planner's actual question, in a form they can act on, with defensible caveats?* This report is the analytical Phase-5 evaluation. The skill-disciplined Go/Iterate/Kill memo, deploy-gate audit, and reconciled verdict live in `phase-6/phase-5-audit.md`.

## Verdict

**SHIP-READY (analytically), DEPLOY-PENDING (stakeholder validation).** The Platanus allergen-exposure priority passes every pre-registered test at **v1 (efficiency)** with **v3 (equity)** as a co-reported variant; analytical confidence ≈ **75%**, bounded by the one limitation we cannot close: the SOURCE layer is a literature-anchored emission proxy, **not validated against measured pollen** (no open data exists). The product is honest about that boundary and claims *exposure*, not clinical outcome. **Deployment is gated** on the unmet stakeholder Monday-test + independent reproduction (`phase-6/phase-5-audit.md` §3, §8) — that gate is the Phase 6 work, deferred to next week with the class. Read "SHIP ~75%" as *ship-grade analysis, deploy-pending*, not *deployed*.

This is the opposite outcome to Cycle A — and for a structural reason: here the two layers **both** demonstrably move the ranking, the test question's answer was genuinely unknown, and the un-validatable element is disclosed rather than dressed up.

## The pre-registered scorecard (v1)

| Test | Question | Result | Pre-registered call | Pass |
|---|---|---|---|---|
| **T1** | Does exposure re-order vs naive density? | Spearman 0.89; top-15 Jaccard **0.30**, top-50 0.39 | re-orders iff J15<0.70 AND ρ<0.90 | **YES** |
| **T2** | Two layers or one in a costume? | corr(pri,src)=0.80, corr(pri,expo)=0.64, corr(src,expo)=0.30 | both \|r\|≥0.3, inputs \|r\|<0.8 | **YES** |
| **T3** | Burden captured vs baselines (top-15 / top-50) | priority 0.18/0.45 vs density 0.13/0.35 vs random 0.03/0.10 | margin over density is the prize | **+4.6 / +9.3 pts** |
| **T4** | Does the T1 verdict survive perturbation? | holds under uniform maturity, rank-normalization, min-aggregation | verdict must hold | **YES** |

**Reading:** accounting for *people* changes ~70% of the top-15 priorities versus the city's density-only rule, and captures meaningfully more modeled allergen-exposure burden per tree removed. The exposure layer earns its place.

**Worked example (why it matters):** a **Nou Barris** cell with 251 planes and **13,400 residents** outranks a **Sant Martí** cell with **485 planes** but 6,500 residents (`outputs/phase-6/priority_zones.csv`, ranks 1 vs 2). Density-only would have inverted them.

## Equity variant (v3) — the near-free win

| Quantity | v1 efficiency | v3 equity | Read |
|---|---|---|---|
| **Precondition — decorrelation** | — | corr(deprivation,source)=**−0.008**, corr(deprivation,exposure)=0.17 | income carries genuine new info (decorrelated from both) |
| **Top-15 burden captured** | 0.180 | 0.175 | sacrifice **0.5 pp** (~3% relative) of exposure relief |
| **Deprived-tercile share of top-15** | 40% | **60%** | +20 pts of priority into the poorest third |

Deprivation is the one weight that *can* re-order (income is Barcelona's most spatially variable feature and is decorrelated from the plane-lined boulevards). v3 redirects priority toward the most-deprived tercile for almost no efficiency cost. **It is a value choice, not a correctness choice:** v1 (maximise total relief) and v3 (relieve the worst-off first) are both valid objectives — both are reported and **the planner chooses the objective.**

## What we tested and rejected (honest negatives)

- **Age-prevalence at-risk layer (v2):** built, then **rejected** — redundant with plain population (Spearman 0.999, top-15 Jaccard 0.875). Barcelona's age structure is spatially flat, so it cannot re-order. `outputs/phase-6/atrisk_results.md`.
- **Sex weighting:** real epidemiology (women receive **1.62×** the per-capita antihistamines of men) but the sex ratio is near-constant across neighbourhoods → no mappable layer. `outputs/phase-6/sex_atrisk.md`.
- **Bike-lane exposure layer:** killed at design (karpathy critique) — ~2–3% travel-mode receptor, no cyclist-volume data, no validation path.

Reporting these is the point: a layer that doesn't move the ranking is a finding, not a failure to hide.

## What this product does NOT claim (the NOT list)

1. **NOT validated against measured pollen** — literature-anchored emission proxy; central limitation, stated plainly.
2. **NOT a health/allergy predictor** — models exposure potential, not clinical outcomes.
3. **NOT a decision on whether to remove plane trees** — policy already decides that; this only sequences it.
4. **NOT valid below 400 m** nor for within-cell siting (MAUP on grid + areal population).
5. **NOT equity-adjusted in v1** (all residents equal); equity is the explicit v3 variant.
6. **Maturity is a coarse proxy** (cell-level young-share, not per-tree diameter).

## Deploy / iterate / stop

**Deploy (ship), with the limitation bound.** The product beats the city's current implicit rule on its own objective, survives every sensitivity perturbation, is built from inspectable data, and is honest about the one thing it cannot validate. The iterate path is clear if data appears: a measured Platanus pollen series (would upgrade SOURCE from proxy to validated) or sub-city allergy data (would let an at-risk layer re-order). Neither exists openly today.

## Handoff to Phase 6 (Deployment) — next week, with the class

Phase 5 is complete. **Phase 6 is intentionally not started** (lecture: no decision-facing UI this session). Ready inputs for deployment: the two priority tables (`priority_zones.csv` efficiency, `priority_zones_equity.csv` equity), the model card, and this verdict. Open deployment decisions to settle with the class: street-axis/census-section aggregation for the Eixos Verds procurement unit; whether the floored-equity weight becomes the shipped default; and the planner-facing format (table vs map).
