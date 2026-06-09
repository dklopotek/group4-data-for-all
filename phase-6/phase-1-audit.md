# Phase 1 (Business Understanding) — Skill Audit & Gap-Fill (Pivot Product)

**Date:** 2026-06-05
**Skill applied:** `crispdm-1-business-understanding` (12-artifact reference model, Chapman et al. 2000 + CRISP-ML(Q) Studer et al. 2021).
**Scope note:** the pivot reused a condensed Phase-1 (`business-understanding.md`) rather than re-spawning Cycle A's 12 granular `phase-1/` files. This audit maps the 12 required artifacts to where each lives for the *pivot* and closes the genuine gaps inline. Lecture > skill: the seminar grades the reasoning, not the file count, so gaps are filled, not bureaucratically duplicated.

## Coverage of the 12 Phase-1 artifacts

| # | Required artifact | Pivot coverage | Location |
|---|---|---|---|
| 1 | Decision statement | ✅ | `phase-6/business-understanding.md` |
| 2 | Heilmeier catechism | ✅ (filled below) | this doc §A |
| 3 | Five-whys / decision-back | ✅ (the falsification chain) | `docs/failure-and-pivot.md` §4 |
| 4 | Decision unit | ✅ | `business-understanding.md` ("census section / street axis") |
| 5 | Output specification | ✅ | `phase-6/data-preparation.md` (contract) + model card |
| 6 | Success criteria (numeric) | ✅ (filled below) | this doc §B |
| 7 | Situation (resources/assumptions/constraints) | ✅ | design doc §7 + this doc §C |
| 8 | Risk register + cancellation | ✅ | this doc §C + `business-understanding.md` (cancellation) |
| 9 | Glossary (pivot terms) | ✅ (filled below) | this doc §D |
| 10 | Product card | ✅ | `outputs/model-card-allergen-v1.md` |
| 11 | Project plan | ✅ | design doc §6 + `docs/crispdm-summary.md` |
| 12 | Exit checklist | ✅ (filled below) | this doc §E |

## §A — Heilmeier catechism (was implicit; made explicit)

1. **What are you trying to do?** Tell Barcelona's tree planners which neighbourhoods to cut plane trees from *first*, so the people who breathe the most plane pollen get relief soonest.
2. **How is it done today, limits?** The implicit rule is "replace where plane trees are densest." Limit: it ignores how many people live there — a dense-but-empty boulevard outranks a moderately-planted dense-residential block.
3. **What's new, why will it succeed?** Multiply a pollen-source layer by a residential-exposure layer. It succeeds where the last project failed because both layers demonstrably move the ranking (not one variable in a costume) and it is tested against a question whose answer was unknown.
4. **Who cares?** Ajuntament Espais Verds (street-tree program) and urban public-health planners executing the Pla Director de l'Arbrat 2017–2037; ultimately ~46%-of-annual-pollen-exposed residents.
5. **Risks?** No measured pollen to validate the source layer; MAUP; exposure ≠ clinical harm. All declared.
6. **Cost?** Zero marginal — built on open data + held inventory, on existing compute.
7. **How long?** Built and evaluated within one session; Phase 6 deployment deferred to next week.
8. **Mid-term / final exams?** Mid: exposure must re-order vs density (T1) and be non-redundant (T2). Final: beat density-only on burden captured (T3), survive sensitivity (T4). All passed (`phase-6/evaluation-report.md`).

## §B — Success criteria (numeric, dated, owned) — GAP CLOSED

The original list (business-understanding.md) was partly adjectival. Restated as numbers:

| Success criterion | Threshold | Verification | Result |
|---|---|---|---|
| Exposure re-orders vs naive density | top-15 Jaccard < 0.70 AND Spearman < 0.90 | T1 | **0.30 / 0.89 — PASS** |
| Both layers material (not one in a costume) | \|corr(pri,src)\|≥0.3 AND \|corr(pri,expo)\|≥0.3, inputs \|r\|<0.8 | T2 | **0.80 / 0.64 / 0.30 — PASS** |
| Beat density-only on burden captured | margin > 0 at top-15 | T3 | **+4.6 pts — PASS** |
| Verdict survives perturbation | T1 holds under 3 perturbations | T4 | **3/3 — PASS** |
| Failure-and-pivot documented | exists on disk | file check | **PASS** (`docs/failure-and-pivot.md`) |
| Equity precondition (v3) | deprivation decorrelated from both, \|r\|<0.7 | V3-1 | **−0.008 / 0.17 — PASS** |

Owner: Group 4 (seminar). Business-side owner (hypothetical deployment): Espais Verds capital-planning analyst. Deadline: pre-Phase-6 (this session) — met.

## §C — Situation: resources, assumptions, constraints, risk register — TIGHTENED

**Resources:** held street-tree inventory (`scored_grid.parquet`); open data (Padró 2026 population, INE Atlas income 2023, census-section boundaries, CatSalut prescriptions); hermes-agent venv (Python 3.11, geopandas/sklearn). Budget €0.

**Assumptions (if false, invalidate the claim):** (a) plane pollen emission scales with count × maturity; (b) residential population approximates daytime receptor exposure; (c) census-section population is ~uniform within section (areal interpolation).

**Constraints / out-of-scope (≥3):** no decision-facing UI this session (lecture); no measured-pollen validation (no open data); no within-cell siting; no clinical-outcome claim; Phase 6 deferred to class.

**Risk register (cancellation flagged):**

| Risk | L | I | Owner | Mitigation | Cancellation? |
|---|---|---|---|---|---|
| No measured pollen series | H | M | Group 4 | downgrade SOURCE to literature-anchored proxy, declare | **Yes — if no defensible emission-factor calibration existed, reframe to plane-density×pop with limitation stated** (clause invoked, design §0) |
| Exposure redundant with density | M | H | Group 4 | T1/T2 pre-registered; report either way | No (honest finding) |
| MAUP distorts ranking | M | M | Group 4 | declare; sensitivity T4 | No |
| Equity weight just decorrelated noise | M | M | Group 4 | V3-1 decorrelation precondition | No |
| Over-claim health benefit | L | H | Group 4 | claim exposure not outcome; NOT-list | No |

## §D — Glossary (pivot-specific terms) — GAP CLOSED

| Term | Meaning |
|---|---|
| SOURCE layer | per-cell plane-pollen emission proxy = `plane_density × maturity`, min-max standardized |
| EXPOSURE layer | per-cell residential population, areal-interpolated, standardized |
| FEASIBILITY | `1 − sealed`; plantability annotation/gate, never multiplied into priority |
| DEPRIVATION | `minmax(max_income − cell_income)`; poorest cell = 1 (v3 equity) |
| priority (v1) | `source_std × exposure_std` — efficiency objective |
| priority (v3) | `× deprivation_std` — equity objective |
| burden | `Σ(source_std × exposure_std)` — total modeled exposure relief available |
| maturity | `1 − trees_young_pct/100` — coarse per-cell emission proxy |
| density-only | baseline = rank by `plane_density` (the city's implicit rule) |
| at-risk (v2) | age×AR-prevalence-weighted population — built, rejected (redundant) |

## §E — Phase-1 exit checklist (skill's binary gate)

- [x] Decision statement — one sentence, four slots (role/decision/cadence/mechanism)
- [x] Named decision-maker — Espais Verds capital-planning analyst / urban-health planner
- [x] Decision unit — census section / street axis (from 400 m grid)
- [x] Output specification — schema/units/CRS in data-preparation.md + model card
- [x] Numerical success criteria — §B, every row a number with verification
- [x] Intended use + intended user — model card
- [x] Out-of-scope uses (≥2) — model card NOT-list (6)
- [x] Risk register (≥5) — §C
- [x] Cancellation criterion — §C row 1 (invoked: pollen validation infeasible → honest downgrade)
- [x] Glossary — §D
- [x] Resources inventory — §C
- [x] Constraints incl. out-of-scope — §C

**All boxes ticked. Phase 1 (pivot) passes the skill's gate.**
