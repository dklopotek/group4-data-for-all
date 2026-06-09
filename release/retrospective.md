# Project Retrospective — Mycorrhizal Barcelona → Platanus Allergen Priority

> CRISP-DM Phase 6, "Review Project" task. Written 2026-06-09 at the close of the full six-phase
> cycle. Honest by mandate (CLAUDE.md): a retrospective that only lists wins is theatre.

## What worked / what didn't / what next

| What worked | What didn't | What next |
|---|---|---|
| Pre-registration (test designs committed before results) — it's what made the falsification credible | We validated a composite against its own ingredients in Cycle A and didn't catch it until Phase 5 | Always run an *external* check before celebrating a high in-distribution number |
| Spatial-cluster split (no autocorrelation leakage) | Nominal weights hid that one component (sealed surface) drove the whole ranking | Inspect *effective* weights empirically, not just declared ones |
| Killing the thesis instead of relabeling it | The mycorrhizal mechanism was assumption (genus-level trait table), never measured | Don't encode a mechanism the available data can't test |
| Multiplicative aggregation in the pivot (non-compensatory, no hidden weights) | The pollen source layer is still un-validated (no open measured-pollen series) | Acquire/derive a measured-pollen series; calibrate or refute the proxy |
| Phase-6 move to native section grain (dropped an interpolation crutch) | At section grain the people-weighting result broke (MAUP) — we only learned this at deployment | Test multiple grains *early*, treat MAUP as a first-class design variable not a footnote |
| Reusing helper code across cell + section products (no re-implementation) | Single 400 m grain was treated as settled through Phases 3–5 | Carry 2+ grains through evaluation so MAUP surfaces before deployment |

## Lessons-learned register (numbered, phase-tagged, severity-tagged)

1. **[Phase 4, CRITICAL]** An index tested against its own inputs returns arithmetic, not evidence. The 0.877 R² was tautological. *Mitigation now standard:* external, pre-registered validation gate.
2. **[Phase 4, MAJOR]** Compensatory (additive) aggregation lets a high-variance component capture effective control. *Mitigation:* multiplicative/conjunctive aggregation when every dimension must count.
3. **[Phase 2, MAJOR]** Absence of validation data is a finding, not a blocker — but it must be declared and bound the claim. The cancellation criterion firing (no pollen series → proxy downgrade) is the model working as designed.
4. **[Phase 6, MAJOR]** Re-ordering power is grain-dependent. The same `source × exposure` product re-orders at 400 m and collapses onto source at section grain because the mature-plane distribution is heavy-tailed. MAUP is load-bearing here, not cosmetic.
5. **[Phase 1, MINOR]** "Recommend, don't ask" plus a written cancellation criterion kept the pivot decisive rather than a drift. Worth keeping.
6. **[Phase 3, MINOR]** Raw-immutable + new-column-per-transform discipline made the section-grain recompute cheap (no re-derivation of Phases 1–3 needed).

## Reverse pre-mortem — which risks materialized, which were avoided

- **Materialized:** "the index just measures sealed surface" (Cycle A) — caught and acted on.
- **Materialized:** "no measured-pollen data exists" — anticipated by the cancellation criterion, downgraded honestly.
- **Materialized (late):** "MAUP changes the answer" — only surfaced at Phase 6; should have been tested earlier.
- **Avoided:** shipping a relabeled sealed-surface map; inventing validation; cherry-picking layers (3 rejections reported); causal language (product says *exposure*, never *causes*).

## Contribution accounting (CRediT)

Group 4 members: Conceptualization, Methodology, Software, Validation, Formal analysis, Data curation,
Writing, Visualization. Seminar instructor: Supervision, Review. AI agent (Claude, Opus 4.8): code
implementation, documentation drafting, methodological auditing against CRISP-DM skills — all analytical
decisions and the pre-registered designs approved by the human authors. *(Individual member names to be
filled by the team before circulation.)*

## End-of-cycle triggers — what would start a new CRISP-DM iteration

1. An open measured *Platanus*-pollen series appears → validate/refute the source proxy (would be a major version bump).
2. The *Pla Director* removal target changes → re-run the allocation in `street_actions.py`.
3. A refreshed tree inventory or population register (Padró) is published → re-run the pipeline.
4. A stakeholder asks for daytime/commuter exposure (schools, workplaces) → new exposure layer, new Phase 1.
5. A request for a maintained interactive tool → a *separate* frontend project with its own CRISP-DM cycle (the `deployment_map.html` here is a one-off presentation aid, not a maintained service).
