# Phase 5 (Evaluation) — Skill Audit, Reconciled Verdict & Go/Iterate/Kill Memo (Pivot)

**Date:** 2026-06-05
**Skill applied:** `crispdm-5-evaluation` (default verdict NEEDS WORK; SHIP requires real decision-maker Monday-test + independent reproduction + signed registers).
**LOCKED CONSTRAINT:** lecture > skill — the seminar lecture is the Phase-5 grading rubric, not this skill. The skill's industry-deployment gate is heavier than a seminar evaluation; where they diverge, the lecture wins, but the skill's honesty discipline is adopted because "be brutally honest" is also a locked project rule.

> **Orienting sentence (Chapman et al. 2000, pp. 28, 30, verbatim discipline):** Phase 4 asks *did the model work?* Phase 5 asks *did the pipeline answer the question the decision-maker actually has, in a form they can act on, with caveats they can defend?*

## The headline conflict (flagged, not hidden)

`phase-6/evaluation-report.md` records **"SHIP, ~75%."** Under the skill's strict gate, **SHIP is not earned**: there is no real Ajuntament decision-maker in the room, no stakeholder walkthrough, and no independent second-operator reproduction on a clean machine. This is a seminar; the decision-maker (Espais Verds capital-planning analyst) is hypothetical.

**Reconciled verdict (honest):** the product is **methodologically ship-ready** — it passes every pre-registered technical test (T1–T4), survives sensitivity, and is honest about its one un-closable limitation — but **deployment is GATED on stakeholder validation**, which is unperformed. Read "SHIP ~75%" as *"technically ship-grade; deploy-pending the stakeholder Monday-test."* That Monday-test **is the Phase 6 work deferred to next week with the class** — so the gap is by design, not an oversight.

## Cycle A as the worked example of Phase 5 doing its job

The skill's anti-pattern #7 ("treating 'no' as failure") and its insistence that *a clean no-go is a successful Phase 5* are already demonstrated by **Cycle A**: the mycorrhizal thesis was evaluated and KILLED (internal redundancy + external GBIF FAIL p=0.99 + 44-source lit-review), documented in `outputs/phase-5/` and `docs/failure-and-pivot.md`. That is a model Phase-5 kill decision. The pivot's Phase 5 is the *go* counterpart, with the deploy gate honestly marked open.

## Step-by-step coverage

| Skill step | Status | Where / gap |
|---|---|---|
| 0 Gate (Phase-1 criteria + cancellation criterion exist) | ✅ | `phase-6/phase-1-audit.md` §B (numeric criteria), §C (cancellation, invoked) |
| 1 Phase4/5 distinction at top of report | ✅ now | this doc header + cross-ref added to evaluation-report.md |
| 2 Close loop on Phase-1 criteria (verbatim + evidence) | ✅ | §1 below |
| 3 Fitness-for-purpose 6-item checklist | ✅ now | §2 |
| 4 Stakeholder walkthrough + Monday test | ❌ **UNMET** | §3 — no real decision-maker (Phase 6 work) |
| 5 Ethics/bias review | ✅ | §4 |
| 6 Process review + pre-mortem | ✅ now | §5 |
| 7 Limitations register (owner+trigger) | ✅ now | §6 |
| 8 Intended-use + PROHIBITED uses | ✅ now | §7 |
| 9 Conditions deployment / non-use | ✅ now | §8 |
| 10 Go/Iterate/Kill memo | ✅ | §9 |

## §1 — Phase-1 business criteria, closed loop

| Criterion (from phase-1-audit §B) | Status | Evidence |
|---|---|---|
| Exposure re-orders vs naive density (J15<0.70 & ρ<0.90) | **met** | `outputs/phase-6/allergen_priority_results.md` T1: 0.30 / 0.89 |
| Both layers material, inputs not collinear | **met** | T2: 0.80 / 0.64 / 0.30 |
| Beat density-only on burden captured | **met** | T3: +4.6 pts (top-15) |
| Verdict survives perturbation | **met** | T4: 3/3 |
| Equity precondition (decorrelation) | **met** | V3-1: −0.008 / 0.17 |
| SOURCE validated vs measured pollen | **unmet (un-evaluable)** | no open data — cancellation clause invoked, honest downgrade to literature-anchored proxy |
| Failure-and-pivot documented | **met** | `docs/failure-and-pivot.md` |

Six of seven **met**; the seventh is **un-evaluable by absence of data** — itself a reported Phase-5 outcome, not an escape hatch.

## §2 — Fitness-for-purpose (Hamilton et al. 2022, 6 items)

| Item | Verdict | Note |
|---|---|---|
| Answers the ORIGINAL Phase-1 question (not a convenient one)? | **yes** | sequences plane removal by exposure relief — exactly the framed decision |
| Resolution matched to decision unit? | **partial** | 400 m cell; planner procures at section/axis — aggregation to axis is Phase-6 work |
| Stated confidence honest (real uncertainty, not goodness-of-fit)? | **yes** | claims exposure not outcome; proxy limitation stated; no fake validation |
| Timeliness adequate? | **yes** | one-shot indicator for a multi-year program |
| Licences / ethics / re-use compatible? | **yes** | all open data, CC-BY-compatible |
| Reproducible end-to-end by independent operator on clean machine? | **partial — UNVERIFIED** | one-command rebuild documented (data contract) but not independently re-run; a SHIP precondition, open |

## §3 — Stakeholder walkthrough (THE unmet gate)

**Not performed — no real decision-maker exists for a seminar project.** The Monday test — *"Would the Espais Verds analyst act on this output on Monday, in front of colleagues, without further work?"* — **cannot be answered on the record.** This is the load-bearing gap the skill exists to surface, and it is precisely what Phase 6 (next week, with the class) is for: present the two maps + the equity trade to a stakeholder proxy and capture the verbatim answer. Until then, the verdict is deploy-pending, not deployed.

## §4 — Ethics & bias review

- **Who benefits?** Plane-pollen-exposed residents in high-priority cells; the city's public-health and green-infrastructure planners.
- **Who is missed?** Non-residents (workers/commuters not in the residential receptor layer); the 0.9% of population clipped at the municipal edge; anyone below 400 m granularity.
- **Failure-cost asymmetry:** mis-sequencing wastes budget and delays relief for the most-exposed — moderate, non-harmful (removal proceeds under policy regardless). Over-claiming health benefit would damage credibility — guarded by the exposure-not-outcome framing.
- **Edge behaviour:** cells with no residential overlap → exposure 0 (structural); signalled in the layer table.
- **Contestability:** transparent per-cell inputs (count × maturity × people) let any party reconstruct and challenge a score.
- **Dominant bias is sampling/representation** (residential ≠ daytime exposure; no sub-city allergy data), not classical demographic fairness — mechanism stated, not labelled.

## §5 — Process review + pre-mortem (pivot)

**Shortcuts / unvalidated assumptions:** maturity = young-share proxy (no per-tree diameter); residential population as exposure proxy (no daytime/mobility data); 400 m cell size not varied (MAUP untested at alternative resolutions); income vintage 2023 vs population 2026.

**Pre-mortem** (*"6 months live, an auditor shows the planner a serious failure — what happened?"*):
1. A journalist notes the "pollen" map was never validated against measured pollen → **mitigated**: NOT-list #1 states this plainly; map is labelled an emission proxy.
2. A removal in a top cell relieves little real exposure because commuters, not residents, dominate that street → **open**: residential-only exposure is a declared limitation; mobility data would close it.
3. Equity variant accused of "reverse discrimination" in cell selection → **mitigated**: v3 is a co-reported *option*, planner chooses; v1 efficiency always shown alongside.
4. Re-run by another team yields different top-15 → **open**: independent reproduction unverified (see §2 item 6).

## §6 — Limitations register (owner + trigger)

| ID | Limitation | Sev | Trigger condition | Mitigation | Owner |
|---|---|---|---|---|---|
| L1 | Not validated vs measured pollen | H | open Platanus pollen series appears | upgrade SOURCE proxy→validated | Group 4 |
| L2 | Residential ≠ daytime exposure | M | commuter-heavy axis ranks high | add mobility receptor layer | Group 4 |
| L3 | MAUP (400 m, fixed partition) | M | decision needs sub-400 m siting | re-grid + re-run; declared not-for | Group 4 |
| L4 | Independent reproduction unverified | M | before any real deployment | second operator clean-machine run | Group 4 |
| L5 | No stakeholder Monday-test | H | before deployment | Phase 6 walkthrough w/ class | Group 4 |
| L6 | Equity is a value choice, not correctness | L | planner treats v3 as "the answer" | co-report v1+v3; planner chooses | Group 4 |

## §7 — Intended-use statement (incl. PROHIBITED uses)

- **Pipeline:** allergen_layers v1 + v3 (deterministic, seed 42).
- **Intended users:** Espais Verds / urban-health planners.
- **Intended use:** sequence the already-decided plane-reduction by modeled allergen-exposure relief, at section/axis scale.
- **Out-of-scope:** within-cell siting; sub-400 m claims; deciding *whether* to remove planes.
- **PROHIBITED (named):** must NOT be cited as measured-pollen or clinical/health evidence; must NOT be used as sole evidence in a planning appeal or any punitive/enforcement action; must NOT be applied outside the Barcelona municipal boundary; must NOT be presented without its NOT-list.
- **Next re-evaluation:** on appearance of measured pollen or mobility data, or annually with population refresh.

## §8 — Conditions

**For deployment (must hold before release):** (1) stakeholder Monday-test answered yes/yes-with-caveats; (2) independent second-operator reproduction hash-matches or differences explained; (3) aggregation to the procurement unit (section/axis) done; (4) NOT-list shipped with every map.

**For non-use:** outside Barcelona; below 400 m; as health/clinical evidence; as appeal/enforcement evidence; after population/inventory goes stale without re-run.

## §9 — Go / Iterate / Kill memo

- **Recommendation:** **ITERATE → (conditional) SHIP.** Technically ship-grade; deployment gated on §8. In the skill's strict terms this is **NEEDS WORK on the deploy gate**; in the lecture's seminar terms the *analytical evaluation is complete and positive*.
- **Recommender:** Group 4.
- **Dissent:** none recorded (single team). The skeptical position is represented internally by the unmet stakeholder gate (L5) and unverified reproduction (L4), both held open rather than waved through.
- **Rationale:** six of seven Phase-1 criteria met with file-backed evidence; the seventh honestly un-evaluable; robust under sensitivity; equity win near-free. The two open items (L4, L5) are **not analytical defects** — they are deployment-readiness checks that belong to Phase 6.
- **Iterate hypothesis (what Phase 6 changes):** running the stakeholder walkthrough + independent reproduction will either flip the gate to full SHIP or surface a concrete usability defect; aggregation to section/axis will match the output to the procurement unit.

## Exit checklist (skill's 10 items)

1. ✅ Phase4/5 distinction stated (header) · 2. ✅ criteria verbatim + evidence (§1) · 3. ❌ real decision-maker (§3 — open, Phase 6) · 4. ❌ Monday-test verbatim (§3 — open) · 5. ✅ limitations register w/ owners (§6) · 6. ✅ prohibited uses (§7) · 7. ✅ dissent line (§9) · 8. ✅ iterate hypothesis (§9) · 9. ❌ independent repro (§2 — open) · 10. ✅ no bare Phase-4 metric stands as business evidence (each T-test translated to the decision in §1).

**Three items (3, 4, 9) are open BY DESIGN — they are the Phase 6 deploy gate, deferred to class.** Analytical Phase 5 is complete; deployment-readiness Phase 5 is honestly marked incomplete. That is the correct, non-inflated state of the project.
