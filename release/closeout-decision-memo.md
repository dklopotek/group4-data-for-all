# CRISP-DM Closeout & Decision Memo

**Project:** Mycorrhizal Barcelona → Platanus Pollen-Allergen Exposure Priority
**Team:** Group 4 (MaAI01 25-26)
**Date:** 2026-06-09 · **Version:** 1.0 (full cycle closed)
**Decision authority:** Group 4, for the seminar. Real-world deployment authority: Ajuntament de
Barcelona, Espais Verds (not yet engaged — see open gates).

> The capstone document. States, on one page, that all six CRISP-DM phases are complete, and records
> the formal Go / Iterate / Kill decision for each cycle with stated confidence. Backed by
> `outputs/reports/crispdm-phase-1-to-6-paper.md` (the full narrative) and the artifacts below.

---

## 1. Phase completion (all six, with evidence)

| Phase | Status | Evidence |
|---|---|---|
| 1 — Business Understanding | ✅ Complete (both cycles) | `phase-6/business-understanding.md`, paper §1, §5, §6.1; decision statement + cancellation criterion on disk |
| 2 — Data Understanding | ✅ Complete | `phase-6/data-understanding.md`, `docs/data-source-inventory.md`; central negative (no measured-pollen series) recorded |
| 3 — Data Preparation | ✅ Complete | `phase-6/data-preparation.md`, `phase-6/allergen-data-contract.yaml`, `docs/data-cleaning-log.md`; raw-immutable, reversible |
| 4 — Modeling | ✅ Complete (both cycles) | `phase-6/modeling.md`, `outputs/phase-4/`; linear model (Cycle A) + multiplicative composite (Cycle B) |
| 5 — Evaluation | ✅ Complete | `docs/evaluation-report.md`, `evaluation-log.md`, `failure-gallery.md`, `validity-audit.md`, `notebooks/05-evaluation.ipynb`; pre-registered, external falsification |
| 6 — Deployment | ✅ Complete | `src/section_priority.py`, `src/street_actions.py`, `outputs/phase-6/maps/deployment_map.html`, full `release/` bundle, paper §8 |

**The framework is closed.** Every phase has a graded artifact; every number reproduces on a fresh run
(seed 42); two honest negatives are documented, not hidden.

---

## 2. The decision

### Cycle A — Mycorrhizal Barcelona → **KILL / STOP**
- **Verdict:** Stop the mycorrhizal claim. The composite was 91% sealed surface; the external GBIF test
  returned a flat null (partial-F p = 0.99); the literature lever was weak-to-unsupported.
- **Confidence:** **High** (~80%) — triangulated across three independent lines, robust under every
  alternative specification.
- **Disposition:** retained as a falsified hypothesis for a future project with measured soil data.

### Cycle B — Platanus Allergen-Exposure Priority → **ITERATE → conditional GO (deploy-pending)**
- **Verdict:** **Analytically ship-ready** at the 400 m evidence grain (passes all pre-registered tests,
  survives sensitivity). Deploy as a **sequencing co-benefit aid** for an already-committed removal
  programme — *not* as health evidence and *not* as a justification to remove.
- **Confidence:** **~75%**, bounded by the un-validatable source proxy (no open measured-pollen series).
- **Grain caveat (binding):** at the operational census-section grain the people-weighting result does
  not hold (MAUP; paper §8.2). Use the 400 m map as the people-weighting *evidence* and the section map
  as the *operational unit*; read them together.

---

## 3. Conditions for deployment / non-use (summary; full lists in `release/`)
- **Deploy when:** a real Espais Verds analyst signs off after a walkthrough, AND an independent party
  reproduces the numbers on a clean machine. Both are **organizational gates, currently OPEN.**
- **Do NOT use** as health/allergy evidence, below census-section grain, for street-level prioritisation,
  or as a basis to decide *whether* to remove planes. (`release/intended_use.md`, `limitations.md`.)

---

## 4. Open items (not analytical — cannot be faked here)
1. Stakeholder sign-off (Espais Verds analyst) — organizational.
2. Independent reproduction on a clean machine — organizational.
3. Zenodo DOI mint for code + data — needs the team's institutional/GitHub account
   (`release/publication_plan.md`, 4 steps).

These do not block the *seminar* deliverable; they are the real-world deployment readiness gates, named
honestly.

---

## 5. End-of-cycle trigger
If an open measured *Platanus*-pollen series appears, re-open at Phase 1 to validate (or refute) the
source proxy — a new CRISP-DM cycle citing this v1 as input. (Full trigger list: `release/retrospective.md`.)

---

## Sign-off

| Role | Name | Date |
|---|---|---|
| Author / maintainer | Group 4 — Rafik El Khoury | 2026-06-09 |
| Team members | _(to be co-signed)_ | |
| Instructor (supervision/review) | _(seminar)_ | |

**CRISP-DM 1→6: COMPLETE.**
