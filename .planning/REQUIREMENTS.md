# Requirements: Mycorrhizal Barcelona — Session 5 (Phase 4 Core A close-out)

**Defined:** 2026-06-04
**Core Value:** A capital-planning analyst can defensibly rank 400m cells for intervention, with every scoring and modeling choice traceable and stress-tested.

**Source of truth:** `phase-4/test-design.md` (pre-registered before build). Every requirement below corresponds to a pre-registered test that MUST run and report — including unfriendly results.

## v1 Requirements

Requirements for this milestone. Each maps to a roadmap phase.

### Sensitivity (Core A — PRPI composite)

- [ ] **SENS-01**: Compute the full 24-spec sensitivity grid (3 normalizations × 4 weightings × 2 aggregations) over `scored_grid.parquet`, writing per-cell composite + rank-tier for each spec to `outputs/phase-4/sensitivity-grid.csv`
- [ ] **SENS-02**: Add a per-cell rank-stability count (specs matching the default Scenario-B tier out of 24) and tag each cell ROBUST (≥22/24) or FRAGILE (<18/24)
- [ ] **SENS-03**: Compute Cronbach's alpha across the 4 sub-scores within Scenario B and report it as the internal-consistency statistic
- [ ] **SENS-04**: Produce a sensitivity figure (rank-stability distribution) saved under `outputs/`

### Stability (Core B — regression)

- [ ] **STAB-01**: Jackknife refit dropping each of the 3 train clusters in turn; report per-feature coefficient mean ± std across refits
- [ ] **STAB-02**: Inject Gaussian noise (σ=0.02) into all features, refit, and report the test-R² delta vs the locked model
- [ ] **STAB-03**: Re-run the spatial split under 3 alternative k-means seeds and report the resulting test-R² distribution (test-cluster representativeness)

### Construct Validity (both cores)

- [ ] **CVAL-01**: Convergent check — Pearson correlation between predicted score and `mean_sealed` (expect strong positive)
- [ ] **CVAL-02**: Discriminant check — Pearson correlation between predicted score and `species_richness` (expect weak)
- [ ] **CVAL-03**: Jaccard overlap of top-15 predicted cells vs Phase-3 `top15_flag`; flag if below 0.5
- [ ] **CVAL-04**: OOD probe — residual distribution by district on the test cluster; flag any district with mean |residual| > 0.10

### Reporting (model cards + pre-registration close-out)

- [ ] **CARD-01**: Write `outputs/model-card-prpi-v1.md` — Mitchell et al. (2019) card for the PRPI composite itself (≥3 NOT statements; robustness drawn from SENS-01/02)
- [ ] **CARD-02**: Append a `## Results` section to `phase-4/test-design.md` covering §4 sensitivity, §5 construct validity, and §6 stability — negative results included, no edits to the pre-registered design except dated addenda
- [ ] **CARD-03**: Update `outputs/model-card-v1.md` §7/§9 to close the previously-flagged sensitivity/stability gaps now that the tests have run

## v2 Requirements

Deferred to a later milestone (out of this roadmap).

### Evaluation & Deployment

- **EVAL-01**: CRISP-DM Phase 5 evaluation + 8-artifact handoff packet
- **DEPL-01**: CRISP-DM Phase 6 deployment / instructor-demo packaging
- **XVAL-01**: Cross-data validation + peri-urban OOD patch (Collserola/Garraf/El Prat)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Frontend / UI / web app | Teacher reviews pipeline strategy, not UI (locked project constraint) |
| Re-deriving Phases 1-3 | `scored_grid.parquet` is the frozen single source of truth |
| Deep learning / regularization sweeps | Lecture caps tuning at one hyperparameter; linear model is the interpretability gate |
| New raster/data ingestion | Snapshot data frozen; Session 5 is analysis-only over existing artifacts |

## Traceability

Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SENS-01 | TBD | Pending |
| SENS-02 | TBD | Pending |
| SENS-03 | TBD | Pending |
| SENS-04 | TBD | Pending |
| STAB-01 | TBD | Pending |
| STAB-02 | TBD | Pending |
| STAB-03 | TBD | Pending |
| CVAL-01 | TBD | Pending |
| CVAL-02 | TBD | Pending |
| CVAL-03 | TBD | Pending |
| CVAL-04 | TBD | Pending |
| CARD-01 | TBD | Pending |
| CARD-02 | TBD | Pending |
| CARD-03 | TBD | Pending |

**Coverage:**
- v1 requirements: 14 total
- Mapped to phases: 0 (roadmap pending)
- Unmapped: 14 ⚠️

---
*Requirements defined: 2026-06-04*
*Last updated: 2026-06-04 after initial definition*
