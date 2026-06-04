# Failure and Pivot — the honest record

**Project:** Group 4 · CRISP-DM seminar · Barcelona
**Written:** 2026-06-04 (Session 5, Evaluation)
**Status:** the original thesis was tested and failed; the project pivoted. This document is the record of that, kept deliberately and in full.

> We are documenting a failure on purpose. The Session-5 brief asks for a defensible verdict, not a flattering one. What follows is what we set out to do, what we built, how we found out it did not work, why it did not work, and what we did about it.

---

## 1. What we set out to do

**"Mycorrhizal Barcelona."** Build a priority map over Barcelona's 400 m grid identifying where intervention would best support the regeneration of soil **mycorrhizal-fungal networks** — the belowground symbioses that connect trees and condition urban soil. The intended user was a capital-planning analyst at Ajuntament Espais Verds allocating Eixos Verds / Superilla budget.

The thesis had a specific mechanism: street trees differ in mycorrhizal type (arbuscular **AM** vs ectomycorrhizal **EM**), and replacing AM-associating trees — above all the dominant plane tree (*Platanus × acerifolia*) — with EM hosts would reduce a "host–fungal mismatch" and help networks recover. We encoded that as sub-scores (`s4_mismatch`, a Platanus Replacement Priority Index `prpi`) inside a five-component composite, `composite_score_B`.

## 2. What we built (and built well)

Through CRISP-DM Phases 1–4 we shipped a genuinely rigorous pipeline:

- A deterministic ETL turning a 189k-tree inventory into a 442-cell scored grid with mycorrhizal composition, species richness, and satellite features.
- The five-component composite, three weighting scenarios, a top-15 priority flag.
- A **pre-registered** Phase-4 test design (written before the build), a spatial-cluster train/eval/test split, three baselines, one tuned hyperparameter, and a linear model reaching test R² = 0.877 that beat all baselines and reproduced end-to-end.

The instructor review called this "the most methodologically mature Phase 4 in the cohort." The craft was real. **The craft is not what failed.**

## 3. How we found out it failed (Session 5 evaluation)

Three independent lines of evidence, each documented and committed:

**(a) Internal redundancy — the index is sealed surface in a costume.**
Checking our own committed data: `composite_score_B` is 91% explained by impervious (sealed) surface *alone* (R² 0.91, r 0.95), and 99.9% by a linear combination of its raw inputs. The two components carrying the actual ecological thesis contribute almost nothing to the ranking: correlation with host/fungal mismatch (`s4`) = **−0.015**, with PRPI = **+0.18**, versus **+0.95** for sealed surface. A planner ranking cells by our headline was ranking them by *how grey the cell is.*

**(b) External falsification — pre-registered test against independent data.**
We asked the question Phase 4 should have asked: against an external fungal outcome the composite never used (1,024 geo-located GBIF fungal occurrences), do the biotic/host layers add any signal beyond the abiotic null (sealing + greenness + sampling effort)? Pre-registered design and code committed *before* results (`phase-5/external-validation-design.md`, `src/external_validation.py`). Verdict: **FAIL.** The biotic/host block added nothing — richness ΔAdjusted-R² = −0.02, partial-F p = 0.99, robust under every alternative we tried. (Full result, including our own design flaws disclosed: `outputs/phase-5/external_validation_results.md`.)

**(c) Literature — the lever was never well-supported.**
A 44-source critical review (`outputs/reports/lit-review-mycorrhizal-prioritization.md`) found the AM→EM host lever weak-to-unsupported in cities; a sealed-surface/greenness axis that explains ~86% of arbuscular-mycorrhizal richness variance in a comparable European city; and direct counter-evidence to our premise — in Amsterdam, plane-tree fungal diversity *increased* with urbanization.

Three methods, one conclusion: **the mycorrhizal signal is not in our number, and the data we have cannot put it there.**

## 4. Why it failed (root cause)

- **We validated a tautology.** Phase 4 tested whether raw features predict a composite *built from those features.* The answer (R² ≈ 1 in-distribution) was arithmetic, not evidence. The one non-trivial number — the test-set gap — turned out to measure how stable our Phase-3 normalization constants are across space, not anything about Barcelona's fungi.
- **The ecological signal was weighted into irrelevance.** The mycorrhizal components had near-zero *effective* weight (composite-indicator theory: nominal weights are not effective weights; one dominant, high-variance component — sealed surface — decides the ranking regardless of the weights we declared).
- **The mechanism was assumption, not measurement.** Mycorrhizal types came from a trait-table genus-level fallback (FungalRoot), not local soil sampling. The AM→EM "improvement" direction was never demonstrated and is contradicted by the best urban evidence.
- **The data could not carry the claim.** Opportunistic GBIF occurrence at 400 m is a coarse probe; we had no measured local soil-fungal outcome layer. The honest thing the data supports is an abiotic surface, not a biotic one.

## 5. What we decided (deploy / iterate / stop)

Per the Session-5 verdict structure, the options were deploy, iterate, or stop. We chose to **stop the mycorrhizal claim and iterate to a new question** — confidence ≈ 75–80% (bounded by the coarse external data; a finer fungal dataset could surface signal this one cannot). The reasoning and the full conclusion are in `outputs/conclusion-brief-v1.md`.

We did **not** quietly relabel and move on. We:
1. wrote the redundancy finding as the headline, not a footnote;
2. ran and reported the external falsification, negative result and all;
3. dropped the "analyst ranks by predicted score" use case (it was just the composite, worse);
4. pivoted to a question the data *can* answer.

## 6. What we pivoted to — and why it is defensible

**Platanus pollen-allergen exposure priority** (design: `docs/plans/2026-06-04-platanus-allergen-priority-design.md`).

The pivot keeps what was real and drops what was not. Plane trees are still central — but for a property the data and the literature actually support: ***Platanus* is a major Barcelona spring aeroallergen,** and the city already has a standing policy to cut it from ~27% to <12% of street trees by 2037. The new decision is *where to sequence that reduction so each removal buys the most allergen-exposure relief for people.* It is:

- **decision-relevant** — tied to an actual Ajuntament policy and a real public-health outcome;
- **plane-tree central** — the species we already inventoried in detail;
- **buildable and honest** — three transparent layers (pollen source, population exposure, feasibility), each inspectable, with the source layer **validated against independent aerobiology pollen data**, not against itself.

The fungal/regeneration ambition is not deleted — it is carried forward as a *stated, here-falsified hypothesis*: where plane trees are removed, replacement could be designed to support soil recovery, a claim for a future project with measured soil data.

## 7. What we kept

The process. Pre-registration before building, spatial splits, honest baselines, negative results retained, every design flaw disclosed (including, in the external test, a circular presence model we caught and discounted ourselves). The pivot is not a retreat from rigour — it is rigour applied to its own conclusion. The same discipline now governs the new product.

## 8. Lessons (for us, and on the record)

1. **Never validate an index against its own ingredients.** Pick an external outcome whose answer you do not already know.
2. **Nominal weights are not effective weights.** Check which component actually drives the ranking before claiming the index is multidimensional.
3. **A proxy must be relabelled as the proxy it is** unless validated against the thing it claims to measure.
4. **A falsified hypothesis, reported honestly, is a result** — and a stronger one than a flattering number that means nothing.

---

*Companion artifacts: `outputs/reports/lit-review-mycorrhizal-prioritization.md` · `phase-5/external-validation-design.md` · `outputs/phase-5/external_validation_results.md` · `outputs/conclusion-brief-v1.md` · `phase-4/test-design.md` (Results).*
