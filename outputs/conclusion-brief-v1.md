# Conclusion Brief — "Mycorrhizal Barcelona" (Track B)

**Project:** Group 4 — barrier-reduction priority map for Barcelona's 400 m grid
**Phase:** CRISP-DM Phase 5 (Evaluation) · Session 5
**Audience:** capital-planning analyst, Ajuntament Espais Verds / Barcelona Regional
**Date:** 2026-06-04
**Read time:** 5 minutes. No notebook required.

---

## If you read nothing else

We set out to map where supporting soil **mycorrhizal fungi** would do most good, so the city could prioritise intervention. After evaluating our own work against independent data, we found the mycorrhizal signal is not in our number. Our headline index ranks cells by how **sealed and hot** they are — a valid and useful signal for **cooling and depaving** priority, but not a measure of fungi. We are therefore **reframing the deliverable** to what it actually measures (an urban cooling / depaving prioritisation aligned with the Eixos Verds), and reporting the mycorrhizal question as an **honestly falsified hypothesis** rather than a delivered result.

This is a deliberate, evidence-based downgrade of our own claim. We think that is the right call, and below is exactly why.

---

## 1. The decision this was built to serve

- **Decision:** where to direct Eixos Verds / Superilla intervention budget across the city.
- **Who acts, and how:** a capital-planning analyst ranks candidate locations and allocates to the top priorities, at the scale the city actually works — the **green axis / square**, translated from our grid.
- **"Good enough":** a ranking that beats the status-quo intuition *and* is honest about what it measures. A precise number for a quantity nobody can act on is not good enough.
- **Cost of being wrong:** misallocated greening budget and a false ecological story told to the public. The reframe **lowers** this cost by claiming only what the data support.

## 2. The claims, stated so they can be proven wrong

**Claim A — SUPPORTED (the reframed product).**
*Within Barcelona's built fabric, priority for street-level cooling and depaving is reliably identified by impervious (sealed) surface and surface temperature; the 400 m index ranks the most-sealed, hottest cells consistently.*
This would be false if sealing/heat did not rank cells in line with thermal exposure. It does. The signal is real and rests on validated physics (impervious surface is the dominant driver of urban land-surface temperature).

**Claim B — FALSIFIED (the original mycorrhizal thesis).**
*Host-tree mycorrhizal composition and AM→EM "mismatch" identify where supporting fungal networks matters most.*
This would be true if the biotic/host layers predicted real fungal occurrence beyond the abiotic surface. They do not. Tested against 1,024 independent GBIF fungal records the index never used, the biotic/host block added **no** explanatory power once sealing, greenness, and sampling effort were accounted for (ΔAdjusted-R² = −0.02; partial-F p = 0.99; robust under every alternative we tried). We report this as a clean null.

## 3. The evidence — three independent lines, one answer

1. **Literature.** A critical review of 44 sources finds the AM→EM host lever weak-to-unsupported in cities, the *Platanus*-is-impoverished premise specifically undercut (Amsterdam plane-tree fungal diversity *rose* with urbanisation), and a sealed-surface/greenness null that explains ~86% of arbuscular-mycorrhizal richness variance in a comparable European city. (`outputs/reports/lit-review-mycorrhizal-prioritization.md`)
2. **Internal redundancy diagnostic.** Our headline `composite_score_B` is 91% explained by sealed surface alone; the two components that encode the ecological thesis correlate −0.015 (mismatch) and +0.18 (PRPI) with the output. The five-component index is, to first order, the sealed-surface raster.
3. **External validation (pre-registered).** Against independent GBIF fungal occurrence, the biotic/host layers add nothing beyond the abiotic null. (`phase-5/external-validation-design.md`, `outputs/phase-5/external_validation_results.md`)

Independent methods, same conclusion. That is the strongest form the evidence could take.

## 4. Threats to validity — named and ruled out

| Threat | Why it does not explain away the result |
|---|---|
| **Confounding** (sealed ↔ heat ↔ density are collinear) | We do not claim to separate them — Claim A is about the abiotic *bundle*. The mycorrhizal increment (Claim B) was tested over-and-above that bundle and was null. |
| **Selection bias** (GBIF logs only where people looked) | Sampling effort was a covariate in every model; tested on the observed subset and as presence/absence; the null held under both, and with effort dropped. |
| **Spurious correlation** (test enough cuts, one lines up) | The biotic block was tested as a *block* against a single pre-registered criterion — no per-variable fishing. |
| **Cherry-picking** | The pass criterion was fixed and committed *before* the result was seen; every result, including the unflattering ones and our own design flaws, is reported. |

We also disclose our own test's limits: the presence model was circular and was discounted; the biotic layers are severely collinear (so their individual coefficients are uninterpretable, though the block test remains valid); one robustness model was deferred for a missing library and substituted with a defensible alternative. None change the verdict.

## 5. What we are explicitly NOT claiming

- NOT a map of fungal diversity, mycorrhizal network health, or soil biology.
- NOT that planting ectomycorrhizal trees restores fungal networks.
- NOT a biodiversity index — greenness is not biodiversity.
- NOT valid for individual cells flagged FRAGILE, nor below the 400 m resolution (the result is conditional on cell size — a known spatial-aggregation effect).
- NOT a substitute for soil sampling, and NOT regulatory or public-health advice.

## 6. Verdict and confidence

**ITERATE — reframe, do not deploy as-is, do not abandon.** Confidence ≈ **75–80%**.

- **Stop** presenting the deliverable as a mycorrhizal / biodiversity map. The claim is falsified in this dataset.
- **Iterate** toward the defensible product: an urban cooling / depaving prioritisation for the Eixos Verds, re-expressed at the axis/square scale the city procures against, and re-validated against a cooling-relevant external outcome (e.g. heat exposure / vulnerability) before any deployment.
- **Carry forward** the mycorrhizal ambition as a stated hypothesis, testable later with *measured* local soil-fungal data (which Barcelona's inventory does not currently hold) rather than trait-table proxies.

Why 75–80% and not higher: the result is robust and triangulated, but it is bounded by data we did not have — opportunistic GBIF occurrence at 400 m is a coarse probe of fungal reality, and a finer, sampled dataset could surface signal this one cannot. We are confident in the *direction* (reframe), less so in the *ceiling* of what a better fungal dataset might show. That uncertainty is itself a reason to reframe honestly now rather than over-claim.

---

*Companion artifacts: `outputs/reports/lit-review-mycorrhizal-prioritization.md` (literature), `outputs/phase-5/external_validation_results.md` (external test), `phase-5/external-validation-design.md` (pre-registration). Model cards: `outputs/model-card-v1.md` (Track A regression), `outputs/model-card-prpi-v1.md` (PRPI composite, pending).*
