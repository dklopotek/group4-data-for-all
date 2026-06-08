# Validity Audit — Platanus Pollen-Allergen Priority (Cycle B) · TRACK B

> **Track B** (we built a conclusion/recommendation on existing data, no trained predictor).
> This is the threat analysis for the shipped product's central claim. Track A's equivalent is
> `docs/failure-gallery.md`. Every number is reproduced in `notebooks/05-evaluation.ipynb`
> (Cells B1–B4).

- **Analysis:** allergen-exposure priority = source_std × exposure_std (v1); × deprivation_std (v3)
- **Maintainer:** Group 4 (Rafik El Khoury)
- **Last updated:** 2026-06-09

---

## The claim under evaluation (one falsifiable sentence)

> *Ranking Barcelona's 400 m cells by (mature-plane-pollen source × residential exposure)
> re-orders the city's plane-removal sequence relative to the naive "remove where planes are
> densest" rule, captures more modeled allergen-exposure relief per removal, and that
> re-ordering survives reasonable perturbation.*

- **The decision it serves:** Espais Verds sequences the already-decided plane reduction
  (Pla Director 2017–2037) by modeled exposure relief.
- **The exact evidence:** `data/processed/allergen_layers.parquet` (494 cells); tests T1–T4.

---

## The four threats

| Threat | Present? | Ruled out by | Residual risk |
|---|---|---|---|
| **Confounding** — does sealed surface (or density) secretly drive both layers? | partial | T2: corr(source, exposure) = **0.30** — the two layers are nearly independent, so neither is a disguise of the other. The Cycle-A failure (composite ≈ sealed) is *structurally excluded* here: exposure is residential population, not a surface variable. | residential population ≠ daytime exposure; a commuter-heavy axis could rank high on residents who aren't the daytime receptors (L2). |
| **Selection bias** — who/what is missing from the receptor data? | yes (declared) | named explicitly: non-residents and commuters are absent from the residential layer; the **0.9%** of population clipped at the municipal edge; anyone below 400 m granularity. The exposure layer is *residential*, by construction. | a mobility/footfall receptor layer would close it; none open. |
| **Spurious correlation** — did we fish for a result? | no | the question and the pass thresholds (T1 J15<0.70 & ρ<0.90; T2 cross-corr<0.8) were **pre-registered** in `phase-6/allergen-validation-design.md` *before* the build. The product is a deterministic composite, not a fitted model, so there is no hyperparameter to tune toward a result. | — |
| **Cherry-picking** — did we report only the cuts that worked? | no | three candidate layers were built or specified, tested, and **rejected in writing**: age-prevalence (Spearman vs population **0.999**, redundant), sex (women 1.62× antihistamine use but sex-ratio ~constant spatially), bike-exposure (no cyclist-volume data). A layer that cannot re-order is reported as a finding, not buried. | — |

---

## Robustness — does the finding survive a different cut?

**T4 — the re-order verdict (T1) under three perturbations** (NB Cell B3):

| Perturbation | Re-orders vs density? |
|---|---|
| Uniform maturity (drop the maturity weighting) | **holds** |
| Rank-normalized layers (instead of min-max) | **holds** |
| Min-aggregation (conjunctive, instead of product) | **holds** |

→ 3/3. The headline does not depend on the specific normalization or aggregation choice.

**Equity variant (v3) sensitivity** (NB Cell B4 / `outputs/phase-6/equity_results.md`):
the deprivation re-weight is decorrelated from both layers (corr −0.008 / 0.17), so it carries
genuine new information. Under a floored weight the top-15 set is 0.875 Jaccard-stable vs v1;
under a rank-based weight, 0.5 — i.e. the *strength* of the equity tilt is a value dial, and we
report both v1 (efficiency) and v3 (equity) so the planner chooses the objective. The
**trade-off is quantified, not hidden:** v3 lifts the most-deprived-tercile share of the top-15
from **40% → 60%** at a cost of **~0.5 pp** of total exposure relief (0.180 → 0.175 burden captured).

---

## The Track-B "test set" — and its honest absence

Track B's out-of-sample analog is a slice we did **not** use while forming the conclusion.

- **For Cycle A** we had one and it was decisive: the external GBIF target falsified the
  ecological claim (`docs/failure-gallery.md` Case 1).
- **For Cycle B there is no true out-of-sample validation**, and we will not pretend there is.
  The one dataset that would test the SOURCE layer — a measured Barcelona Platanus-pollen series
  — does not exist openly. This is criterion 7 in the evaluation report, marked **un-evaluable**.
  T4 (perturbation robustness) and the rejected-layer audit are *internal* robustness, not
  external validation. Saying so is the point of this audit: the claim is **internally robust and
  externally un-validated**, and the product's NOT-list (#1) carries that boundary.

---

## Causal-language audit

The claim is associational and is worded that way: the product ranks *exposure potential*, never
asserts that a removal *causes* a measured drop in allergy outcomes. No causal design was run; no
causal language is used. (NOT-list #2: not a health-outcome predictor.)

---

## Verdict from the audit

The central claim survives all four threats *for what it claims* — a transparent re-ordering of
exposure relief — and is honest about the one thing it cannot do: validate its source layer
against measured pollen. **Internally robust, externally un-validated, act-on-able as a
sequencing aid with its caveats attached.**

- **Audited by:** Group 4 (Rafik El Khoury)
- **Reviewed by another team:** pending (Session-5 cross-team review)
