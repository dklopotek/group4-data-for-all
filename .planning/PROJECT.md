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

<!-- This milestone: Session 5 = close CRISP-DM Phase 4 (Core A wrap-up). -->

- [ ] Run pre-registered Core A sensitivity grid (24 specs) with per-cell rank-stability + ROBUST/FRAGILE tags + Cronbach's alpha
- [ ] Run Core B stability checks (jackknife on 3 train clusters, Gaussian-noise injection) + 3-seed meta-sensitivity on the spatial split
- [ ] Run construct-validity probes (convergent, discriminant, Jaccard vs Phase-3 top-15, OOD residual-by-district)
- [ ] Write PRPI model card (`outputs/model-card-prpi-v1.md`), distinct from the Core B regression card
- [ ] Append all results to the pre-registered `phase-4/test-design.md` (negative results included) and update model-card-v1 §7/§9 gaps

### Out of Scope

- CRISP-DM Phase 5 (Evaluation) and Phase 6 (Deployment) — deferred to a later milestone; this milestone closes Phase 4 only
- Cross-data / parallel-dataset validation and peri-urban OOD patch (Collserola/Garraf/El Prat) — no dataset in pipeline; logged in model-card limitations
- Any frontend / UI / web app — teacher will not review UI; pipeline strategy is what's graded (locked project constraint)
- Re-running or re-deriving Phases 1-3 — outputs are the frozen single source of truth (`scored_grid.parquet`)
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
| GSD roadmap scopes Session 5 only (close Phase 4), defer Phase 5/6 | Keep the milestone shippable; Phases 1-4 already exist as code/docs | — Pending |
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
