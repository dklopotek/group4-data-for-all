# Mycorrhizal Barcelona — Barrier-Reduction Priority Map

## What This Is

A batch geospatial pipeline that turns Barcelona's open tree inventory, GBIF fungi
records, FungalRoot trait data, and satellite/land-cover rasters into a defensible
priority ranking of 400m grid cells for urban mycorrhizal-fungi barrier reduction.
The intended user is a capital-planning analyst at Ajuntament Espais Verds /
Barcelona Regional allocating Eixos Verds / Superilla budget. It is a CRISP-DM
seminar project (MaAI01 25-26), graded against the course lecture rubric — **not a
production app and not a UI**.

## Core Value

A capital-planning analyst can defensibly rank 400m cells for intervention, with
every scoring and modeling choice traceable and stress-tested — robustness and
interpretability, not predictive accuracy, are what make the ranking usable.

## Requirements

### Validated

<!-- Shipped and confirmed (inferred from existing code, CRISP-DM Phases 1-4). -->

- ✓ Deterministic phase 1-3 ETL: 189k-tree inventory → 442-cell 400m grid with mycorrhizal composition, species richness, raster features (`src/clean_data.py`) — Phase 3
- ✓ PRPI v1.1 + VPA v1.2 scoring, 4 sub-scores (S1-S4), 3 composite scenarios (A/B/C), top-15 flagging, intervention classification — Phase 3
- ✓ YAML data contract + ADRs (species priority, AM-only assumption) — Phase 3
- ✓ Spatial cluster split: k-means (k=5, seed 42) on EPSG:25831 centroids, 60/20/20 train/eval/test, test frozen at write (`src/split_data.py`) — Phase 4 Core B
- ✓ Three pre-registered baselines (Mean, SpatialNearest, DomainHeuristic) — Phase 4 Core B
- ✓ Linear regression on 10 raw features (no Phase-3 leakage); test R² 0.877, MAE 0.011, beats all 3 baselines (pre-registered PASS) — Phase 4 Core B
- ✓ Model card v1 (Mitchell template, 5 NOT statements, per-segment metrics) — Phase 4 Core B
- ✓ Priority map (Folium HTML), priority-zones export, mycorrhizal connectivity network — Phase 3 outputs

### Active

<!-- This milestone: Session 5 = CRISP-DM Phase 5 (Evaluation), per the Session 5 lecture rubric. Hybrid Track A (model) + Track B (ranking conclusion). -->

- [ ] Return to the brief — restate decision, actor, "good enough" bar, cost of being wrong; classify Track A/B/hybrid
- [ ] Robustness & sensitivity — 24-spec composite grid + ROBUST/FRAGILE tags + Cronbach's alpha; jackknife, noise, 3-seed, alternative-cut tests
- [ ] Construct validity & threats — convergent/discriminant/Jaccard/OOD probes; name + rule out confounding, selection bias, spurious correlation, cherry-picking
- [ ] **External validation (keystone)** — predict external GBIF fungal occurrence (never used in the composite); test whether biotic/host layers add signal beyond the sealed+greenness null. PASS → re-weighted biotic claim earned; FAIL → reframe confirmed empirically
- [ ] Failure & stress (Track A) — failure gallery of 4-5 worst predictions; stress test for graceful degradation
- [ ] Process & reproducibility audit — CRISP-DM walk-back, weakest-link/error audit, fresh-clone reproduction, peer-review packet
- [ ] Verdict & docs — fill Track A model card, PRPI card, Track B conclusion brief, append test-design Results, write planner-readable evaluation report with deploy/iterate/stop + confidence

### Out of Scope

- Decision-facing UI / dashboard — lecture explicitly says do NOT build the UI this session; evaluation comes first (deferred to Phase 6)
- CRISP-DM Phase 6 (Deployment) — deferred to a later milestone
- Cross-data / parallel-dataset validation and peri-urban OOD patch (Collserola/Garraf/El Prat) — no dataset in pipeline; logged in model-card limitations
- Re-running or re-deriving Phases 1-3 — outputs are the frozen single source of truth (`scored_grid.parquet`)
- Collecting new data — lecture: no new data unless looping back to an earlier phase
- Deep-learning / regularization sweeps — lecture caps tuning at one hyperparameter; linear model is the interpretability gate

## Context

- **Lecture is the grading rubric.** When the seminar lecture and any CRISP-DM skill conflict, the lecture wins. Phase 4 anchors: `Session 4/Lecture_4.md` lines 273-415.
- **Recommend, don't ask.** Drive phase decisions with rationale; ask only for a veto. The user pushed back explicitly on multi-question Socratic prompts.
- **Pre-registration is binding.** `phase-4/test-design.md` was written before the build; every test in it must run and every result (including unfriendly) must be reported. Silently dropping a pre-registered test is the cardinal Phase 4 sin.
- **Substantive finding to defend:** eval R² 0.999 → test R² 0.877 is the honest spatial generalization cost; the composite is a locally near-linear re-skin of `mean_sealed` and friends whose calibration depends on the geographic mix of training cells.
- Brownfield codebase mapped 2026-06-04 → `.planning/codebase/`. Canonical implementation is `src/*.py`; notebooks are narrative only.

## Constraints

- **Tech stack**: Python 3.11 (hermes-agent venv), geopandas/scikit-learn/rasterio; Windows cp1252 console — no Unicode in `print()` without `PYTHONIOENCODING=utf-8`. No DB, no API serving, local file-based.
- **Reproducibility**: raw is immutable; pipeline reruns via `python src/clean_data.py && src/split_data.py && src/train_model.py`. Exact version pins except `scikit-learn>=1.5,<2.0`.
- **Determinism**: all randomness seeded (k-means seed 42); test cluster frozen at split time, never inspected until final assessment.
- **Timeline**: seminar session cadence; Session 5 closes Phase 4 to keep the milestone shippable for instructor + Salvador review.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| GSD roadmap = Session 5 = CRISP-DM Phase 5 Evaluation (lecture rubric), defer Phase 6 | Session 5 lecture defines this session as Evaluation; lecture > skill (locked). Phase 4 sensitivity/stability folds in as evidence | ✓ Good |
| **Pivot**: mycorrhizal thesis → Platanus pollen-allergen exposure priority | Mycorrhizal thesis falsified on 3 independent lines (`docs/failure-and-pivot.md`); allergen product is decision-relevant, plane-tree central, and the data carries signal | ✓ Good — v1 shipped, exposure earns its place (T1 re-orders, T2 non-redundant) |
| Skip 4-agent domain research | Domain exhaustively known (prior deep-research in memory); web backends unavailable in env | — Pending |
| Coarse granularity, YOLO mode | Small remaining scope; matches recommend-don't-ask | — Pending |
| Sensitivity grid = 24 specs (3 norm × 4 weight × 2 agg) | Pre-registered in test-design.md §4; skill demands sensitivity on every composite choice | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-04 after initialization*
