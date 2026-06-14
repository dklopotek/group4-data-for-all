# Validity Audit — Platanus Pollen-Allergen Priority (Cycle B) · TRACK B

> **Track B** (we built a conclusion/recommendation on existing data, no trained predictor).
> This is the threat analysis for the shipped product's central claim. Track A's equivalent is
> `docs/failure-gallery.md`. Every number is reproduced in `notebooks/05-evaluation.ipynb`
> (Cells B1–B4).

- **Analysis:** allergen-exposure priority = source_std × exposure_std (v1); × deprivation_std (v3)
- **The claim under audit:** *Ranking Barcelona's 400 m cells by (mature-plane-pollen source ×
  residential exposure) re-orders the city's removal sequence relative to the naive
  "remove where planes are densest" rule, captures more modelled allergen-exposure relief per
  removal, and that re-ordering survives reasonable perturbation.*
- **Data drawn from:** Barcelona street-tree inventory (`arbrat`, 2026_1T); Padró Municipal 2026
  residential population by census section; INE Atlas gross income 2023; Gabarra et al. 2002
  emission factors. All existing, open or held. No trained predictor.
- **Maintainer:** Group 4 (Rafik El Khoury / Dominika Klopotek)
- **Last updated:** 2026-06-14

---

## The four threats

### 1 · Confounding — a third thing drives both

> Does sealed surface, or plane density itself, secretly explain the re-ordering?

- **Present?** Partial — a real risk. Cells with many planes are also often dense and
  heavily sealed, which could drive *both* the source layer and the exposure layer, making
  the product a disguised sealed-surface map (exactly the Cycle-A failure mode).
- **Test:** `05-evaluation.ipynb` Cell B2 (T2). Computed corr(source, exposure) directly.
  If a hidden third variable drove both, the two layers would be highly correlated.
  Result: corr(source, exposure) = **0.30** — the two inputs are nearly independent.
  The Cycle-A collapse is structurally excluded: exposure is residential population, not
  a surface variable. We also checked corr(priority, source) = 0.80 and
  corr(priority, exposure) = 0.64 — both layers move the ranking, neither dominates.
- **Verdict:** Partially controlled. The two layers are demonstrably near-independent, so
  the product is not a single-variable re-skin. **Residual risk:** residential population ≠
  daytime exposure; a commuter-heavy axis could rank high on residents who are not the
  daytime receptors (L2 in conclusions brief).

---

### 2 · Selection bias — your data isn't who you think

> The existing system recorded residents. What's missing, and does the gap shift the ranking?

- **Present?** Yes — declared explicitly.
- **Test:** Coverage audit at ingestion (Phase 2). The Padró layer covers census sections
  for permanent residents only. Missing: (a) non-residents and commuters; (b) **0.9%** of
  population clipped at the municipal edge; (c) anyone below 400 m granularity. No open
  footfall or mobility data exists at this spatial resolution.
- **Verdict:** Residual risk, declared and bounded. The residential choice is explicit in the
  product spec; the 0.9% clip is negligible; the MAUP floor is in the NOT-list. A
  mobility/footfall receptor layer would close the commuter gap — none open at 400 m.

---

### 3 · Spurious correlation — something lined up by chance

> Did we fish for a threshold that passed, or run enough comparisons that one was bound to?

- **Present?** No.
- **Test:** Question and pass thresholds (T1: J15 < 0.70 AND ρ < 0.90; T2 cross-corr < 0.8)
  were **pre-registered** in `phase-6/allergen-validation-design.md` *before* the build.
  The product is a deterministic composite (no hyperparameter to tune toward a result).
  We ran four pre-registered tests (T1–T4), not an exploratory sweep.
- **Verdict:** Ruled out. Pre-registration is binding; thresholds were not adjusted after
  seeing results.

---

### 4 · Cherry-picking — the story chose the data

> Did we report only the cuts that supported the claim?

- **Present?** No.
- **Cuts that did not support it:**
  - **Age-prevalence layer:** Spearman(at\_risk, population) = **0.999** — redundant with
    plain population; top-15 Jaccard vs v1 = 0.875; cannot re-order at this resolution.
    Built, tested, rejected, reported (`05-evaluation.ipynb` Cell B4, Test 19).
  - **Sex weighting:** women receive **1.62×** the per-capita antihistamines of men — real
    epidemiology, but the sex ratio is ~constant across neighbourhoods → no mappable spatial
    signal. Answered, not mapped. Test 20.
  - **Bike-exposure layer:** ~2–3% travel-mode receptor, no open cyclist-volume data, no
    validation path. Rejected at design (Test 21).
  - **T4 rank-based equity weight:** top-15 Jaccard vs v1 = 0.50 — the strength of the
    equity tilt is sensitive to weighting choice. Reported alongside the floored-weight
    result (0.875), not hidden.
- **Verdict:** Ruled out. Three candidate layers were built or specified, found unhelpful,
  and reported. The cut that weakened the equity variant (rank-based weight) is also shown.

---

## Robustness / sensitivity table

> From `05-evaluation.ipynb` Cells B3–B4. Does the conclusion survive choices we could
> defensibly have made differently?

| Cut / choice | Effect on headline | Holds? | Note |
|---|---|---|---|
| Headline (T1): exposure vs density-only | top-15 Jaccard 0.30, burden margin +0.046 | — | baseline finding |
| Uniform maturity (drop maturity weighting) | re-order verdict holds | **holds** | removes one data-quality dependency |
| Rank-normalised layers (not min-max) | re-order verdict holds | **holds** | normalization-independent |
| Min-aggregation (conjunctive, not product) | re-order verdict holds | **holds** | aggregation-independent |
| Equity v3 (floored deprivation weight) | top-15 Jaccard vs v1 = 0.875 | **holds near** | deprived-tercile share 40%→60%, cost 0.5 pp |
| Equity v3 (rank-based deprivation weight) | top-15 Jaccard vs v1 = 0.50 | **weakens** | tilt strength is a value dial — reported, not hidden |
| Pollen source validated externally | **no open series** — un-testable | **un-evaluable** | the un-closable limitation; bounds confidence at ~75% |

**Reading:** the re-ordering claim holds under 3/3 pre-registered perturbations and is
near-stable under a modest equity tilt. It weakens when the equity tilt is maximised —
which is expected and disclosed. The claim cannot be externally validated for the source
layer; that is the single un-closable caveat.

---

## The Track-B "test set" — honest absence

Track B's out-of-sample analog is a slice we did **not** use while forming the conclusion.

- **For Cycle A** we had one and it was decisive: the external GBIF target falsified the
  ecological claim (`docs/failure-gallery.md` Case 1).
- **For Cycle B there is no true out-of-sample validation**, and we will not pretend there
  is. The one dataset that would test the SOURCE layer — a measured Barcelona
  *Platanus*-pollen series — does not exist openly (Test 22). T4 and the rejected-layer
  audit are *internal* robustness, not external validation. Saying so is the point of this
  audit.

---

## Causal-language audit

The claim is associational and is worded that way throughout: the product ranks *exposure
potential*, never asserts that a removal *causes* a measured drop in allergy outcomes. No
causal design was run; no causal language is used. (NOT-list #2 in `conclusions-brief.md`.)

---

## Summary — what the audit changes

- **Threats that remain:** selection bias (commuters absent from receptor layer, L2) and
  the un-validated source layer (no open pollen series). Both are declared in the NOT-list
  and bound the analytical confidence at ~75%.
- **Conditions the conclusion is restricted to:** 400 m grid, city-wide, Barcelona 2026
  residential population and tree inventory; valid as a *sequencing* aid only; not valid
  below 400 m, for within-cell siting, or as a health-outcome claim.
- **The verdict's "where it fails" row:** the source layer (mature-plane emission proxy)
  has never been compared to a measured pollen series. If the emission proxy is badly
  miscalibrated at the cell level, the ranking could mislead. This is un-closable with
  current open data; it is the reason the recommendation is SHIP (~75%), not DEPLOY.

---

## Sign-off

- **Audit by:** Group 4 (Rafik El Khoury / Dominika Klopotek)
- **Reviewed by another team:** _(reviewer team — to be filled during Session-5 block 03)_
- **Did they find a threat we missed?** _(yes / no — what)_

- [x] All four threats addressed (Confounding / Selection / Spurious / Cherry-picking).
- [x] At least one threat is **residual** (not fully ruled out) — confounding (L2) and
      source-layer validation both remain.
- [x] Robustness table includes at least one cut that **weakens** the finding
      (rank-based equity weight, Jaccard 0.50; pollen validation, un-evaluable).
- [x] Causal language audited — no causal claims in the product or this document.
- [ ] Cross-team review completed _(pending block 03)_.
