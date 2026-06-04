# Roadmap: Mycorrhizal Barcelona — Session 5 (CRISP-DM Phase 5: Evaluation)

## Overview

This milestone is **CRISP-DM Phase 5: Evaluation**, scoped by the Session 5 lecture rubric (lecture > skill, locked). It does NOT close Phase 4 as a build — it evaluates the FROZEN deliverables of Phases 1-4 against the original brief. This is a HYBRID project: **Track A** is the linear regression model (supporting evidence) and **Track B** is the priority ranking / PRPI composite (the headline conclusion). The lecture requires BOTH be evaluated.

All work is analysis and reporting over frozen inputs — `data/processed/scored_grid.parquet`, `outputs/phase-4/model_artifact.joblib`, the existing splits, and predictions. No new data, no re-derivation of Phases 1-3, and **no decision-facing UI** (the lecture is explicit: evaluation comes first, UI is deferred to Phase 6).

The grade rewards **rigor and honesty, not predictive accuracy**. Documented negative results, named-and-ruled-out threats, and an honest deploy/iterate/stop verdict are the success conditions. Pre-registration is binding: every test in `phase-4/test-design.md` must run and report — including unfriendly results.

Three coarse phases, run goal-backward from the verdict:
1. **Return to Brief & Quantitative Robustness** — recover the brief, then build the quantitative evidence layer (sensitivity grid, stability refits, construct-validity probes).
2. **Adversarial Evaluation** — try to break the conclusion: name threats, gallery the worst failures, stress-test, audit the process, and prove someone else can reproduce it.
3. **Verdict & Documentation** — consume Phases 1-2 into the two model cards, the Track B conclusion brief, the pre-registered Results append, and a planner-readable deploy/iterate/stop report.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Return to Brief & Quantitative Robustness** - Recover the brief and classify Track A/B, then build the quantitative evidence layer: 24-spec sensitivity grid, jackknife/noise/seed stability, alternative-cut test, and convergent/discriminant/Jaccard/OOD construct-validity probes
- [ ] **Phase 2: Adversarial Evaluation** - Try to break the conclusion: name and rule out the 4 threats to validity, gallery the worst predictions, stress-test for graceful degradation, audit the CRISP-DM process, and prove a fresh-clone reproduction plus peer-review handoff
- [ ] **Phase 3: Verdict & Documentation** - Consume Phases 1-2 into the Track A model card, the PRPI composite card, the Track B conclusion brief, the pre-registered test-design Results append, and a planner-readable deploy/iterate/stop evaluation report with stated confidence

## Phase Details

### Phase 1: Return to Brief & Quantitative Robustness
**Goal**: The original brief is recovered and the project classified as a hybrid; the headline ranking and the supporting model both carry quantitative robustness, stability, and construct-validity evidence — so an evaluator can see exactly which cells are trustworthy and whether the verdict holds under defensible alternative choices.
**Depends on**: Nothing (runs over frozen `scored_grid.parquet`, `model_artifact.joblib`, splits, predictions)
**Requirements**: BRIEF-01, ROB-01, ROB-02, ROB-03, ROB-04, ROB-05, ROB-06, ROB-07, ROB-08, VAL-01, VAL-02, VAL-03, VAL-04
**Success Criteria** (what must be TRUE):
  1. A brief-recovery section exists (decision, actor + how they act, "good enough" bar, cost of being wrong) and explicitly classifies the project as Track A / Track B / hybrid with justification (BRIEF-01)
  2. `outputs/phase-4/sensitivity-grid.csv` exists with one row per cell, a composite + rank-tier column for each of the 24 specs (3 normalizations × 4 weightings × 2 aggregations), a per-cell `rank_stability` count (out of 24 vs default Scenario B), and a `robustness_tag` column tagging ROBUST (≥22/24) or FRAGILE (<18/24); a rank-stability distribution figure is saved under `outputs/` (ROB-01, ROB-02, ROB-04)
  3. Cronbach's alpha across the 4 sub-scores within Scenario B is computed and reported as the internal-consistency statistic (ROB-03)
  4. A stability artifact under `outputs/phase-4/` reports per-feature jackknife coefficient mean ± std across the 3 train-cluster refits, the test-R² delta under σ=0.02 Gaussian noise, the test-R² distribution across 3 alternative k-means seeds, and an alternative-cut test result stating whether the headline verdict holds or the sign flips (ROB-05, ROB-06, ROB-07, ROB-08)
  5. A construct-validity artifact under `outputs/phase-4/` reports convergent Pearson r (predicted vs `mean_sealed`), discriminant Pearson r (vs `species_richness`), Jaccard overlap of top-15 predicted vs Phase-3 `top15_flag` (flagged if < 0.5), and an OOD residual-by-district table flagging any district with mean |residual| > 0.10 (VAL-01, VAL-02, VAL-03, VAL-04)
**Plans**: TBD

### Phase 2: Adversarial Evaluation
**Goal**: The conclusion has been actively attacked rather than merely reported — the four threats to validity are named and ruled out with specific evidence, the worst predictions are surfaced and diagnosed, the model's degradation behavior is characterized, the process's weakest link is admitted, and an outsider can reproduce the numbers — so the verdict survives hostile review.
**Depends on**: Phase 1 (threats and failures reference the robustness/validity evidence; can overlap with Phase 1's qualitative work)
**Requirements**: VAL-05, FAIL-01, STRESS-01, AUDIT-01, REPRO-01
**Success Criteria** (what must be TRUE):
  1. A threats-to-validity section names all four threats — confounding (e.g. sealed ↔ heat ↔ density), selection bias (inventory logs only managed street/park trees), spurious correlation, cherry-picking — and rules each out (or flags it as residual) with specific evidence (VAL-05)
  2. A failure gallery documents the 4-5 worst test-cell predictions, each with input, what made it hard, predicted vs actual, and a one-off vs systematic diagnosis (FAIL-01)
  3. A stress-test artifact reports model behavior under shifted / extreme / missing-feature inputs and states whether error stays under tolerance (graceful degradation) or collapses (STRESS-01)
  4. A process / error-audit section walks back the CRISP-DM phases (did Phase-3 cleaning shape results? was removed data anomalous or crucial?), names the weakest link, where rigor was traded for time, and untested assumptions taken on faith (AUDIT-01)
  5. A reproducibility artifact documents the fresh-clone / fresh-env command and confirms the report numbers match, plus a peer-review handoff packet for another group (REPRO-01)
**Plans**: TBD

### Phase 3: Verdict & Documentation
**Goal**: Every result from Phases 1-2 is consumed into evaluator-facing deliverables: both cores have completed model cards, the Track B headline carries a falsifiable conclusion brief, the pre-registered test-design carries all results (negatives retained), and a planner can read a single report ending in a deploy/iterate/stop recommendation with a stated confidence — without opening a notebook.
**Depends on**: Phase 1, Phase 2
**Requirements**: DOC-01, DOC-02, DOC-03, DOC-04, VERDICT-01
**Success Criteria** (what must be TRUE):
  1. `outputs/model-card-v1.md` has its Track A evaluation section filled — metrics table, failure gallery, stress results, and segment differentials — confirmed by the Phase 1-2 analysis, not guessed (DOC-01)
  2. `outputs/model-card-prpi-v1.md` exists — a Mitchell et al. (2019) card for the PRPI composite with ≥3 NOT statements and a robustness section sourced from the Phase 1 ROB-01/ROB-02 ROBUST/FRAGILE results (DOC-02)
  3. A Track B conclusion brief exists with a falsifiable claim, its evidence, the threats ruled out, and an explicit "what we are NOT claiming" list (DOC-03)
  4. `phase-4/test-design.md` has a `## Results` section covering §4 sensitivity, §5 construct validity, and §6 stability, with negative results retained and additions made only as dated addenda (DOC-04)
  5. A planner-readable evaluation report exists (no notebooks required to read) covering the brief, success criteria, evidence, where it failed, and a deploy / iterate / stop recommendation with a stated confidence level (VERDICT-01)
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3. Phase 1 (quantitative re-tests) and Phase 2 (qualitative audit + threats + reproducibility) are partly independent and may overlap during planning/execution; Phase 3 consumes both and runs last.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Return to Brief & Quantitative Robustness | 0/2 | Not started | - |
| 2. Adversarial Evaluation | 0/2 | Not started | - |
| 3. Verdict & Documentation | 0/2 | Not started | - |
