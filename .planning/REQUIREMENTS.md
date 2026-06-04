# Requirements: Mycorrhizal Barcelona — Session 5 (CRISP-DM Phase 5: Evaluation)

**Defined:** 2026-06-04
**Core Value:** A capital-planning analyst can defensibly rank 400m cells for intervention, with every scoring and modeling choice traceable and stress-tested.

**Grading rubric:** Session 5 lecture (Evaluation). Lecture > skill when they conflict (locked).
**Project type:** HYBRID — Track A (linear regression model = supporting evidence) + Track B (priority ranking / composite = the headline conclusion). Both get evaluated.
**Source of truth for pre-registered tests:** `phase-4/test-design.md`. Every pre-registered test MUST run and report — including unfriendly results. No UI this session (lecture: do not build the decision-facing UI yet).

## v1 Requirements

Requirements for this milestone (Session 5 = Evaluation). Each maps to a roadmap phase.

### Return to the Brief

- [ ] **BRIEF-01**: Recover and restate the original brief from Phase-1 docs — the decision being made, who acts on it and how, what "good enough" means, and the cost of being wrong — and classify the project as Track A / Track B / hybrid with justification

### Robustness & Sensitivity

- [ ] **ROB-01**: Compute the full 24-spec sensitivity grid (3 normalizations × 4 weightings × 2 aggregations) over `scored_grid.parquet`, writing per-cell composite + rank-tier per spec to `outputs/phase-4/sensitivity-grid.csv`
- [ ] **ROB-02**: Add per-cell rank-stability count (specs matching the default Scenario-B tier out of 24) and tag each cell ROBUST (≥22/24) or FRAGILE (<18/24)
- [ ] **ROB-03**: Compute Cronbach's alpha across the 4 sub-scores within Scenario B (internal consistency)
- [ ] **ROB-04**: Produce a rank-stability distribution figure under `outputs/`
- [ ] **ROB-05**: Jackknife refit dropping each of the 3 train clusters; report per-feature coefficient mean ± std
- [ ] **ROB-06**: Inject Gaussian noise (σ=0.02) into all features, refit, report test-R² delta vs the locked model
- [ ] **ROB-07**: Re-run the spatial split under 3 alternative k-means seeds; report the test-R² distribution
- [ ] **ROB-08**: Defensible alternative-cut test (e.g. alternative `mean_sealed` threshold / drop one district) — does the headline verdict hold or does the sign flip? (lecture: "remove a year, weekdays only, alt definition")

### Construct Validity & Threats to Validity

- [ ] **VAL-01**: Convergent check — Pearson correlation between predicted score and `mean_sealed` (expect strong positive)
- [ ] **VAL-02**: Discriminant check — Pearson correlation between predicted score and `species_richness` (expect weak)
- [ ] **VAL-03**: Jaccard overlap of top-15 predicted vs Phase-3 `top15_flag`; flag if below 0.5
- [ ] **VAL-04**: OOD probe — residual distribution by district on the test cluster; flag any district with mean |residual| > 0.10
- [ ] **VAL-05**: Name and rule out the 4 threats to validity — confounding (e.g. sealed ↔ heat ↔ density), selection bias (tree inventory logs only managed street/park trees), spurious correlation, cherry-picking — each with specific evidence

### External Validation (does the data carry mycorrhizal signal?)

The keystone test (lit-review §9 #4): predict an EXTERNAL fungal outcome the composite never used, and ask whether the biotic/host layers add signal beyond the abiotic null. Pre-registered in `phase-5/external-validation-design.md`; implemented in `src/external_validation.py`.

- [ ] **EXT-01**: Build the external GBIF fungal target — spatial-join the 1,024 geo-located GBIF occurrences to grid cells (EPSG:25831), compute per-cell observed fungal richness, presence, and effort to `data/processed/gbif_external_target.parquet`; confirm via leakage check that none of these feed the composite or the Core-B features
- [ ] **EXT-02**: Fit the pre-registered nested models (M0 abiotic null = sealed + ndvi + effort; M1 + biotic/host) on the observed subset; report ΔAdjusted-R², partial-F and p, and VIF against the pre-registered PASS criterion (ΔAdj-R² ≥ 0.05 AND partial-F p < 0.05); state the PASS/FAIL verdict and what it means for defend/rebuild/reframe
- [ ] **EXT-03**: Run the pre-registered confound + robustness pass — presence/absence logistic with 5-fold CV-AUC + LR test over all cells, effort-controlled and drop-effort variants, log-richness variant, and Moran's I on residuals; the PASS/FAIL verdict must survive (or be flagged as fragile)

### Failure & Stress (Track A)

- [ ] **FAIL-01**: Failure gallery — 4-5 worst test-cell predictions, each with input, what made it hard, predicted vs actual, and one-off vs systematic diagnosis
- [ ] **STRESS-01**: Stress test under shifted / extreme / missing-feature inputs; report whether error stays under tolerance (graceful degradation) or collapses

### Process & Reproducibility Audit

- [ ] **AUDIT-01**: CRISP-DM process walk-back + error audit — did Phase-3 cleaning decisions shape results? was removed data anomalous or crucial? name the weakest link, where rigor was traded for time, and untested assumptions taken on faith
- [ ] **REPRO-01**: Reproducibility check — fresh-clone / fresh-env run reproduces the report numbers (document command + match); plus a peer-review handoff packet for another group

### Verdict & Documentation

- [ ] **DOC-01**: Fill the Track A model-card evaluation section in `outputs/model-card-v1.md` — metrics table, failure gallery, stress results, segment differentials (confirmed by analysis, not guessed)
- [ ] **DOC-02**: Write the PRPI composite model card `outputs/model-card-prpi-v1.md` (Mitchell template, ≥3 NOT statements; robustness from ROB-01/02)
- [ ] **DOC-03**: Write the Track B conclusion brief — falsifiable claim + evidence + threats ruled out + explicit "what we are NOT claiming"
- [ ] **DOC-04**: Append a `## Results` section to `phase-4/test-design.md` covering §4 sensitivity, §5 construct validity, §6 stability — negatives retained, dated addenda only
- [ ] **VERDICT-01**: Write the evaluation report a planner can read without opening notebooks — brief + success criteria + evidence + where it failed + deploy/iterate/stop recommendation with a stated confidence level

## v2 Requirements

Deferred to a later milestone (out of this roadmap).

### Deployment & Cross-validation

- **DEPL-01**: CRISP-DM Phase 6 deployment / decision-facing UI (lecture: not this session)
- **XVAL-01**: Cross-data validation + peri-urban OOD patch (Collserola/Garraf/El Prat)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Decision-facing UI / dashboard | Lecture: do not build the UI this session — evaluation first |
| Re-deriving Phases 1-3 | `scored_grid.parquet` is the frozen single source of truth |
| Collecting new data | Lecture: no new data unless looping back to an earlier phase |
| Deep learning / regularization sweeps | Lecture caps tuning at one hyperparameter; linear model is the interpretability gate |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| BRIEF-01 | Phase 1 | Pending |
| ROB-01 | Phase 1 | Pending |
| ROB-02 | Phase 1 | Pending |
| ROB-03 | Phase 1 | Pending |
| ROB-04 | Phase 1 | Pending |
| ROB-05 | Phase 1 | Pending |
| ROB-06 | Phase 1 | Pending |
| ROB-07 | Phase 1 | Pending |
| ROB-08 | Phase 1 | Pending |
| VAL-01 | Phase 1 | Pending |
| VAL-02 | Phase 1 | Pending |
| VAL-03 | Phase 1 | Pending |
| VAL-04 | Phase 1 | Pending |
| EXT-01 | Phase 1 | Pending |
| EXT-02 | Phase 1 | Pending |
| EXT-03 | Phase 1 | Pending |
| VAL-05 | Phase 2 | Pending |
| FAIL-01 | Phase 2 | Pending |
| STRESS-01 | Phase 2 | Pending |
| AUDIT-01 | Phase 2 | Pending |
| REPRO-01 | Phase 2 | Pending |
| DOC-01 | Phase 3 | Pending |
| DOC-02 | Phase 3 | Pending |
| DOC-03 | Phase 3 | Pending |
| DOC-04 | Phase 3 | Pending |
| VERDICT-01 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 26 total
- Mapped to phases: 26 ✓
- Unmapped: 0

**By phase:**
- Phase 1 — Return to Brief & Quantitative Robustness: 16 (BRIEF-01, ROB-01..08, VAL-01..04, EXT-01..03)
- Phase 2 — Adversarial Evaluation: 5 (VAL-05, FAIL-01, STRESS-01, AUDIT-01, REPRO-01)
- Phase 3 — Verdict & Documentation: 5 (DOC-01..04, VERDICT-01)

---
*Requirements defined: 2026-06-04*
*Last updated: 2026-06-04 — added EXT-01..03 (GBIF external validation) to Phase 1; pre-registered in phase-5/external-validation-design.md*
