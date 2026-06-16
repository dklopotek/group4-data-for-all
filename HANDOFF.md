# Handoff — Session 6 (FINAL): full CRISP-DM cycle closed

**Created:** 2026-06-05 · **Updated:** 2026-06-16 (final session)
**Branch:** main
**Status:** COMPLETE — all 6 CRISP-DM phases closed; presentation + delivery package ready.

## Summary
Full six-phase CRISP-DM cycle delivered. Mycorrhizal thesis falsified on three independent lines (Session 5), pivoted to Platanus pollen-allergen exposure priority (Cycle B). Product shipped as v1 (efficiency) + v3 (equity variant). Final delivery HTML presentation and updated README added this session.

## Final deliverables
- `outputs/presentation-final.html` — 5-minute tutor presentation (open in browser)
- `outputs/reports/crispdm-phase-1-to-6-paper.md` — full canonical paper
- `outputs/phase-6/maps/deployment_map.html` — interactive priority map
- `outputs/phase-6/street_removal_actions.csv` — per-street worklist (top-60 sections)

## Current state
- **GSD planning** initialized in `.planning/` (PROJECT.md, REQUIREMENTS.md, ROADMAP.md, config.json, STATE.md). Roadmap is framed as Session-5 = CRISP-DM Phase 5 Evaluation; the pivot product lives under `phase-6/` + `outputs/phase-6/`.
- **Two falsification results, fully documented:** mycorrhizal composite is ~91% sealed surface (internal); external GBIF test FAIL (`outputs/phase-5/external_validation_results.md`); 44-source lit-review (`outputs/reports/lit-review-mycorrhizal-prioritization.md`). Failure narrative: `docs/failure-and-pivot.md`.
- **Pivot product (Platanus allergen priority), all scripts run exit-0 on the hermes venv:**
  - v1 priority = SOURCE (plane density x maturity) x EXPOSURE (residential population). Exposure EARNS its place (re-orders vs naive density, top-15 Jaccard 0.30; both layers non-redundant). `outputs/phase-6/allergen_priority_results.md`.
  - v3 equity variant = v1 x deprivation (income). Near-free equity win: deprived-tercile share of top-15 40%->60% for only ~0.5pp (~3% relative) exposure-relief cost. `outputs/phase-6/equity_results.md`.
  - Model card: `outputs/model-card-allergen-v1.md` (6 NOTs, equity trade documented).
- **Build/test status:** no pytest exists (carried over from earlier sessions). All `src/*.py` pipeline scripts were run this session and exited 0. Numbers in the result `.md`/`.json` files match what the scripts printed.
- Working tree clean except 3 pre-existing modified files unrelated to this work (Seek_Deep_CHINA.md, notebooks/01, notebooks/02) and the untracked `data/processed/allergen_layers.parquet` (gitignored, regenerable).

## Files in flight
None incomplete. Everything is committed. Key files the next session will read:
- `docs/failure-and-pivot.md` — the honest failure record (REQUIRED reading; user explicitly wanted failure documented).
- `docs/plans/2026-06-04-platanus-allergen-priority-design.md` — pivot design.
- `phase-6/business-understanding.md` — CRISP-DM Phase 1 (re-run for pivot).
- `phase-6/allergen-validation-design.md` — pre-registered evaluation incl. v2 (at-risk) and v3 (equity) addenda + appended results.
- `src/allergen_source.py`, `src/exposure_layer.py`, `src/allergen_priority.py`, `src/atrisk_layer.py`, `src/equity_layer.py`, `src/sex_atrisk.py` — the pivot pipeline.
- `outputs/phase-6/*.md|json` — all results. `outputs/model-card-allergen-v1.md` — the card.

## What changed this session
1. Initialized GSD project scaffolding (`.planning/`), reframed Session 5 = CRISP-DM Phase 5 Evaluation per the lecture (lecture > skill, locked).
2. Evaluated and FALSIFIED the mycorrhizal thesis on 3 independent lines (lit-review, internal redundancy, pre-registered external GBIF test = FAIL).
3. Ran the deferred ROB/VAL pack (sensitivity grid 321/97/76 ROBUST/MOD/FRAGILE, jackknife/noise/seed stability, construct validity) — commit 37d9a82.
4. Pivoted (brainstorming skill -> approved design) to the Platanus allergen-priority product; built it CRISP-DM-style and documented the failure.
5. Layer selection, each tested with the same honesty check (does it re-order / add info?): EXPOSURE adopted; AGE-prevalence rejected (redundant, Jaccard 0.875); SEX no mappable signal (women 1.6x antihistamines but ratio flat in space); BIKE LANES killed at design via karpathy critique; DEPRIVATION adopted as equity variant v3 (decorrelated r=-0.008, near-free equity win).

## What we tried that didn't work
- **The whole mycorrhizal thesis.** Falsified. Do NOT revive AM->EM host-mismatch as a predictor — external GBIF test p=0.99. (Carry only as a stated hypothesis.)
- **Age-prevalence at-risk layer.** Redundant with population (Spearman 0.999). Do not re-add as a spatial weight; age structure is spatially flat in Barcelona.
- **Sex weighting.** Real epidemiological signal (women 1.6x) but sex ratio ~constant across cells -> no mappable layer.
- **Bike-lane exposure layer.** Rejected at design under karpathy review: ~2-3% travel-mode receptor, no cyclist-volume data, no validation path. Do not build unless cyclist flow-count data appears.
- **External pollen validation.** No open machine-readable Barcelona Platanus pollen series exists (XAC gives only 0-4 forecast; EAN access-controlled). Source layer is a literature-anchored emission proxy, NOT measured-pollen-validated. Do not claim measured validation.
- **Windows cp1252 console:** keep ASCII-only in all `print()` (no unicode). Use the hermes venv python: `C:\Users\Rafik\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` (3.11; has geopandas/sklearn). `py -3.12` is NOT installed.

## Open questions / decisions pending
1. How to present CRISP-DM phases for the pivoted product — do we renumber (the old Phases 1-4 were the mycorrhizal build; phase-6/ holds the pivot) or write a unifying CRISP-DM doc that frames the failure as the Phase-5 evaluation outcome and the pivot as a new Phase-1-through-5 cycle? (User wants to decide this next session.)
2. Whether to ship a Phase-6 deployment/UI later (lecture said not this session).
3. Optional v2/v3 extensions: street-axis aggregation for Eixos Verds; equity floored-weight as default.

## Next steps
1. **Decide the CRISP-DM documentation structure** for the pivot (see Open Question 1) — likely a single `docs/crispdm-summary.md` mapping each of the 6 phases to what was actually done across the mycorrhizal cycle (Phases 1-4 + the Phase-5 falsification) and the pivot cycle (allergen Phase 1 business-understanding -> Phase 5 evaluation), with the failure as the hinge.
2. Fill any thin CRISP-DM phases for the pivot product: Phase 2 (data understanding — the allergen data inventory: tree inventory, population, income, the no-pollen-data finding) and Phase 3 (data preparation — the layer-build steps) are currently implicit in scripts/results; formalize them into short phase docs if the rubric wants them.
3. Write the one-page planner verdict / evaluation report that folds v1 (efficiency) + v3 (equity) + the trade into a single readable deliverable (was offered, user deferred).
4. Optional: socioeconomic equity floored-weight as the shipped default; street-axis aggregation.

## How to resume
Paste into the new Claude Code session:
> Read `HANDOFF.md` at the project root and continue from "Next steps" item 1. Lecture > skill is locked; recommend-don't-ask is locked. Do not re-explore territory listed under "What we tried that didn't work" unless the listed condition is met.
