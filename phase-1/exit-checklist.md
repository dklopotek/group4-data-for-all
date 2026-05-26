# Phase 1 Exit Checklist

Binary exit criteria. All must pass before handoff to Phase 2.

## Checklist

- [x] **Decision statement** — one sentence, all four slots filled (role, decision, cadence, mechanism).
  - *Status:* `phase-1/decision-statement.md` — Barcelona Regional / Ajuntament Espais Verds, barrier-reduction capital allocation, annual budget cycle, ranked priority map.
- [x] **Named decision-maker** — named role at a named organisation, not "stakeholders."
  - *Status:* Urban planning analysts and landscape architects at Barcelona Regional + Ajuntament de Barcelona Espais Verds i Biodiversitat.
- [x] **Decision unit** — spatial, temporal, and thematic units written as numbers.
  - *Status:* `phase-1/decision-unit.md` — 400m × 400m grid, annual snapshot, four barrier sub-scores + composite + intervention type.
- [x] **Output specification** — schema exists; units, CRS (EPSG:4326), refresh cadence specified.
  - *Status:* `phase-1/output-spec.md` — 14-field GeoJSON schema fully specified with types, units, and CRS.
- [x] **Numerical success criteria** — every criterion is a number with a deadline and an owner.
  - *Status:* `phase-1/success-criteria.md` — 4 business criteria + 8 data-product criteria, all numerical with verification methods.
- [x] **Intended use and intended user** — both written in the product card draft.
  - *Status:* `phase-1/product-card-draft.md` §2–3 — intended use (green-infrastructure capital allocation), intended user (Barcelona Regional + Ajuntament Espais Verds).
- [x] **Out-of-scope uses** — at least two named in the product card draft.
  - *Status:* `phase-1/product-card-draft.md` §4 — four out-of-scope uses: regulatory compliance, property-level decisions, substitute for site surveys, belowground network claims.
- [x] **Risk register** — at least five risks, each with likelihood, impact, owner, mitigation.
  - *Status:* `phase-1/risks.md` — 7 risks documented with full L/M/H ratings, owners, mitigations.
- [x] **Cancellation criterion** — at least one risk marked "Triggers cancellation = Yes" with a clear condition.
  - *Status:* `phase-1/risks.md` — "If more than two of four barrier sub-scores cannot be computed at 400m for ≥50% of cells, rescope or cancel."
- [x] **Glossary** — every contested term covered.
  - *Status:* `phase-1/glossary.md` — planning↔technical cross-reference + contested terms section covering "priority," "connectivity," "recovery," "grid."
- [x] **Resources inventory** — every resource named (no "the team," no "the data").
  - *Status:* `phase-1/situation.md` — named people (Rafik, Dominika, Juan), 9 named data sources with providers, named compute/software stack.
- [x] **Constraints** — hard limits named, including explicit out-of-scope items.
  - *Status:* `phase-1/situation.md` — 8 explicit out-of-scope items including no frontend, no predictive model, no belowground claims, no AM-DNA validation, no real-time data.

## Handoff readiness

**All 12 boxes ticked.** Phase 1 is complete. Ready to hand off to Phase 2 (`earn-the-data` / `crispdm-2-companion`).

**Handoff payload:**
1. `phase-1/decision-statement.md`
2. `phase-1/decision-unit.md`
3. `phase-1/output-spec.md`
4. `phase-1/product-card-draft.md`
5. `phase-1/risks.md`

**Date:** 2026-05-26
**Committed by:** Rafik (with Claude Code / DeepSeek v4 Pro)
