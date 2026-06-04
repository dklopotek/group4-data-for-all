# Concerns & Technical Debt
**Mapped: 2026-06-04**

## Summary
The Mycorrhizal Barcelona CRISP-DM Phase 4 pipeline ships a linear regression model (R² 0.877, MAE 0.011 on test cluster) that predicts barrier-severity scores from raw geospatial features. Phase 3 processing is mature (13 bug fixes documented and applied via `.claude/fix_pipeline.py`). Phase 4 Core B is complete; Core A (PRPI composite sensitivity grid, 24 specs) is deferred. Five scientific-defensibility findings from earlier deep research remain partially unaddressed in code/data: asthma-claim scope, Quercus ilex hypothesis, AM→EM substrate hypothesis, Barcelona species-palette mismatch, and stale inventory vintage. Code fragility is moderate: notebook-to-Python migration is complete for Phase 4, but three Core A sensitivity checks remain unimplemented.

---

## Scientific / Methodological Risks (HIGHEST PRIORITY)

| Concern | Severity | Evidence / Location | Impact |
|---------|----------|-------------------|--------|
| **Asthma claim not empirically supported** | CRITICAL | PRPI docs claim barrier-reduction targets asthma burden; Osborne et al. (2017) found no significant association Platanus↔asthma in 8.2M London cohort. Real burden is rhinoconjunctivitis + food-allergy cross-reactivity (Scala 2017, Cariñanos & Marinangeli 2021). `src/clean_data.py` lines 9–11, 31–32 mention "allergenicity"; `outputs/model-card-v1.md` §2.2 docstring claims "public-health advice" re: pollen without asthma precision. | Public-health claims are inflated. Ajuntament stakeholders may make intervention decisions believing a larger health burden exists than evidence supports. Decision-maker harm: medium. |
| **Barcelona deployed Zelkova/Pistacia, not Quercus ilex** | MAJOR | Project-prior designs PRPI around EM hosts (Quercus ilex, Pinus). Espais Verds official doc (*Trees and Climate Change*) names Zelkova serrata + Pistacia chinensis as the pilot palette; both are AM hosts. Cariñanos scores Q. ilex VPA IV–V (same allergy class as Platanus — shifts but does not reduce allergenic burden). `src/clean_data.py` lines 26–27 hardcode "EM-optimistic scenario" but the city has moved. | PRPI design assumes substitution with EM trees; actual intervention palette is AM. Predicted composite scores may not align with realized intervention outcomes post-2026. Model validation gap: ranking of cells by predicted score may diverge from actual post-intervention mycorrhizal-network outcomes. |
| **AM→EM substrate effect framed as outcome, not hypothesis** | MAJOR | PRPI v1.1 assumes engineered (EM-favorable) substrate will shift mycorrhizal colonization from AM to EM. Verbeek et al. (2025, *Plants People Planet*) and Gaimaro et al. (2025, *npj Urban Sustainability*) show urban AM communities shift *composition* (not collapse) and substrate acts *jointly* with host identity—not sufficiently. `src/clean_data.py` line 31 says "EM-optimistic scenario"; `outputs/model-card-v1.md` §2.1 target is `composite_score_B` (Scenario B sealed-dominant, which subsumes PRPI v1.2). | Phase 3 composite is anchored to a substrate assumption that is structurally sound as an upper bound but empirically underspecified. No sensitivity check for substrate assumption in Phase 4 Core A pre-registered tests. Test-design gap: `phase-4/test-design.md` §4 sensitivity grid (24 specs) does not vary substrate regime. |
| **Inventory snapshot drift unaddressed** | MAJOR | Pipeline pulls arbrat-viari 2026_1T (snapshot 2026-05-01); municipal canon reports ~43,722 trees / 27.5% Platanus as of 2026-Q2 (vs. pipeline 42,828 / 22.6%). Data file `data/arbrat-viari-prev-snapshot.csv` (dated 2026-05-10) suggests prior awareness of drift. No snapshot-to-snapshot diff documented; `data/README.md` download instructions are static. | Model trained on one-point-in-time inventory; Eixos Verds rollout during 2015–2024 actively changes tree population. Any claim about "where new plantings happened" requires two snapshots. Current pipeline is single-snapshot only — acknowledged in `outputs/model-card-v1.md` §2.5 but not tracked for future re-runs. Reproducibility risk: if user re-downloads arbrat-viari in Session 5, input data drifts without warning. |
| **Top-15 ranking divergence unexplored** | MAJOR | Phase 3 `top15_flag` derived from `composite_score_B` via district-constrained threshold (≥ 80th pct within district). Phase 4 test-set Jaccard overlap between predicted vs. Phase 3 `top15_flag` is not yet reported. `phase-4/test-design.md` §5 pre-registers "face validation" (expert top-15 comparison); deferred post-build. | If predicted top-15 differs substantially from Phase 3 top-15, the decision-maker signal changes without explanation. Risk mitigation exists (pre-registered test) but is incomplete. |

---

## Data Risks

| Concern | Evidence / Location | Mitigation Status |
|---------|-------------------|------------------|
| **Missing planting dates (~81% of inventory)** | `docs/data-quality-audit.md` §2.1: "planting date is missing for ~81% of records (153,176 of 189,090)." Prevents tree-age cohort analysis. | ACCEPTED. Documented in audit; design explicitly snapshot-state only. Not a bug, a design choice. |
| **Sealed-surface raster at 10m, grid at 400m (potential MAUP)** | Urban Atlas provides 10m pixels; Phase 3 aggregates to 400m grid via zonal mean. `src/clean_data.py` uses rasterio zonal stats; resolution mismatch noted but not sensitivity-tested. `phase-4/modeling-guidelines.md` §3.2 pre-registers MAUP check (200m / 800m grids) but deferred to Core A. | Deferred. Pre-registered in test design; not yet executed. Medium risk — MAUP is well-known; aggregation function (mean) is defensible. |
| **GBIF fungi coverage gaps in central Barcelona** | `docs/datasheets/gbif-fungi.md` notes sparse central coverage; `outputs/model-card-v1.md` §2.4 flags out-of-scope regulatory use because calibration uncertainty not propagated. | ACCEPTED & DOCUMENTED. Known limitation cited in model card. GBIF as auxiliary signal only, not authoritative. |
| **Median imputation on 10 features during train/eval/test** | `src/train_model.py` lines 84–107: "Median imputer fit on train only; same imputer reused on eval + test." Feature missingness concentrated in `lst_anomaly` (raster edge cases) and `am_pct` (no matched trees). No imputation variance analysis. | DOCUMENTED in model card §5; defensible given lecture constraint (one hyperparameter tune only). No holdout for imputation stability checks. Minor risk. |
| **Manual top-20 species override in FungalRoot join** | `.claude/fix_pipeline.py` lines 45–60 hard-code TOP20_MYCO stub (Platanus AM, Pinus pinea EM, etc.). Rationale documented (90% of inventory) but curated values override CSV. If FungalRoot updated, override persists silently. | DOCUMENTED in fix-pipeline script + `src/clean_data.py` lines 17–18; BUG-1 in handoff. Known patch. No auto-check for FungalRoot version drift. Low risk but brittle. |

---

## Code Fragility

| Concern | File / Location | Impact |
|---------|-----------------|--------|
| **Notebook-only stages (Phase 3) still not fully extracted to src/** | `notebooks/02-data-cleaning.ipynb`, `03-scoring.ipynb`, `04-connectivity.ipynb`, `05-visualisation.ipynb` exist in parallel to Python src scripts. `build_notebook.py` (if it exists) rebuilds notebooks but is not mentioned in HANDOFF.md. | HANDOFF.md states Phase 3 is "done," but visualization + connectivity (bridge score, spread simulation) remain notebook-based. Phase 4 only canonicalized the data prep (clean_data.py) and modeling (train_model.py). If someone re-runs 04-connectivity, they are reading stale code. Medium fragility. |
| **13 documented bugs fixed via patch script, not integrated** | `.claude/fix_pipeline.py` applies 13 cell-level fixes (BUG-1 through BUG-13: FungalRoot stub, scale conversions, scenario labels, railways weight, etc.). Script runs post-cleanup but is not part of the main pipeline. If notebooks are re-executed from scratch, fixes are lost. | Patch is committed to `.claude/` but not documented in the main pipeline README. Fragile: user might re-run `02-grid-trees.ipynb` cell o5p6q7r8 and lose BUG-1 fix. Mitigation: handoff.md mentions it; integration into src/clean_data.py would be safer. Medium fragility. |
| **No test suite (pytest / unittest)** | `HANDOFF.md` §2 says "No formal pytest yet (carried over from Session 3)." No `tests/` directory. `phase-4/test-design.md` is a pre-registered design, not automated checks. | Phase 4 code (`src/train_model.py`, baselines.py) has no automated regression tests. Manual execution only. If someone edits `src/baselines.py` to add a new baseline, there is no test to catch breakage. Low-medium risk for a seminar project, but fragile for team hand-offs. |
| **Hardcoded file paths relative to project root** | `src/clean_data.py` lines 72–86: `PROJECT_ROOT = _HERE.parent`; paths assume execution from project root. `src/train_model.py` lines 68–71 same. Works but brittle if user runs from subdirectory. | Works as documented (README says "run from project root"). Not a blocker, but non-portable. Low risk. |
| **No requirements-lock (only requirements.txt with version ranges)** | `requirements.txt` specifies `scikit-learn>=1.5,<2.0`, `pandas==3.0.3`, etc. Some pinned (pandas, numpy), some ranged (scikit-learn). No `poetry.lock` or `pip-freeze` output committed. | Reproducibility risk: if run 6 months from now, different minor versions of scikit-learn might have different behavior. Medium risk for a graded seminar. Mitigation: HANDOFF.md says "run on hermes-agent 3.11 venv"; if user loses that venv, they re-pip-install and get different versions. |
| **Manual dependency on GBIF/Urban Atlas/Landsat/Sentinel2 external data** | `src/clean_data.py` tries-except on rasterio (lines 57–64); graceful fallback to synthetic values if rasters absent. Downloads via `data/README.md` curl commands (not automated). If URLs change or PDFs expire, pipeline breaks silently (synthetic fallback). | Acknowledged in code. Fallback is defensive but obscures the failure. Medium fragility: pipeline runs with garbage data if rasters are missing. |

---

## Reproducibility Risks

| Concern | Evidence | Mitigation |
|---------|----------|-----------|
| **Large data files not in repo; re-download required** | `data/arbrat-viari.csv` (~43 MB) and `data/arbrat-zona.csv` (~14 MB) are gitignored. Users must manually run curl commands from `data/README.md`. | EXPECTED FOR SEMINAR. Documented. Low risk if README is read. Mitigated by `.gitignore` + explicit instructions. |
| **External portals (Open Data BCN, GBIF, Planetary Computer STAC) may change** | GBIF API, Planetary Computer availability, Open Data BCN URL structure are external dependencies. If endpoints retire or API changes, re-runs fail. | RISK FLAGGED in model card §2.5 ("forecasting future barrier scores"). No fallback. Medium risk for 2026–2027 re-runs. Mitigation: snapshot the downloaded CSVs in `data/raw/` and version them. |
| **Test cluster frozen at split time; never re-shuffled** | `phase-4/test-design.md` §1.2 & HANDOFF.md state test cluster is frozen. But k-means seed 42 produces a geographically-clustered NW test set (Sarrià-Sant Gervasi + Les Corts). Alternative seeds yield different clusters. Meta-risk: reported metrics may be seed-dependent. | FLAGGED IN HANDOFF.md open question #3: "Test-cluster representativeness. k-means seed 42 produced a wealthy NW test cluster. A different seed gives a different cluster; consider running 3 alternative seeds as a meta-sensitivity check." Not yet executed. Medium risk for generalization claims. |
| **No snapshot versioning / lineage tracking** | Pipeline reads `arbrat-viari.csv` and `arbrat-zona.csv` without recording download timestamp or source URL hash. If user re-pulls in Session 5, there is no way to know if data changed. `ARBRAT_VIARI_SNAPSHOT = "2026_1T"` (line 90 of clean_data.py) is a label, not a hash. | MITIGATED BY DESIGN: HANDOFF.md & model card acknowledge snapshot-state-only framing. But for future sessions, a versioning scheme (e.g., commit hash of downloaded data) would help. Medium-term risk. |

---

## TODO / FIXME Inventory

**Grep for TODO|FIXME|HACK|XXX|BUG:** Found 62 matches across `src/clean_data.py` and `.claude/fix_pipeline.py`. All are docstring annotations of the 13 bug fixes (BUG-1 through BUG-13), not open TODOs. No unresolved TODOs remain in the main pipeline.

Examples from `src/clean_data.py`:
- Line 224: `# Applied AFTER the FungalRoot CSV join for safety (BUG-2 fix).`
- Line 464: `# Top-20 override: curated values trump the CSV (BUG-2 fix)`
- Line 954: `# BUG-3 fix: When the raster is absent, draws synthetic`
- Line 1099: `# BUG-4 fix: am_pct and em_pct are 0–100, not 0–1`
- Line 1665: `# trees_young_pct is on a 0–100 scale (BUG-5 fix)`

All bugs are *fixed* and *documented*, not outstanding. Status: **CLEAN**.

---

## Security / Secrets

**No leaked credentials found.** Project uses public datasets only (Open Data BCN, GBIF, Urban Atlas, Landsat, Sentinel-2). No `.env` files, API keys, or private credentials in committed code or docs. Model file `outputs/phase-4/model_artifact.joblib` is a pickled sklearn pipeline (safe). Status: **CLEAN**.

---

## Prioritized Recommendations

### 1. **BLOCKING (before Session 5 completion)**
**Reconcile Barcelona species palette with PRPI design.** Decision-maker is allocating Eixos Verds budget based on a PRPI composite anchored to EM-host substitution (Q. ilex, Pinus), but Espais Verds is planting Zelkova + Pistacia (both AM). 
- **Action:** Update `src/clean_data.py` lines 26–27 PRPI docstring to name the *actual* palette (Zelkova, Pistacia, Sophora, Melia, jacarandas, Celtis) and re-run Phase 3 scoring with `SPECIES_PREFERENCE = "Barcelona_operational"` as a new scenario alongside the EM-optimistic prior. Write a one-paragraph rationale in the scoring module explaining the shift.
- **Effort:** ~1 hour (species list lookup + docstring update + re-run Phase 3).
- **Owner:** Rafik (or Salvador as domain expert).
- **Evidence:** `outputs/model-card-v1.md` §2.1, project-prpi-evidence-review.md finding #4.

### 2. **BLOCKING (before Session 5 completion)**
**Scope the asthma claim down to allergenic burden.** Remove all language claiming PRPI reduces asthma incidence; replace with "rhinoconjunctivitis + food-allergy cross-reactivity via Bet v 1 homolog and Pla a 3 interactions."
- **Action:** Edit `src/clean_data.py` lines 9–11, 31–32; update `outputs/model-card-v1.md` §1 purpose statement and §2.2 docstring. Add a literature citation (Osborne et al. 2017, Scala et al. 2017).
- **Effort:** ~30 minutes.
- **Owner:** Rafik.
- **Evidence:** project-prpi-evidence-review.md finding #1; Osborne et al. (2017) *Int J Biometeorol*.

### 3. **MEDIUM PRIORITY (Phase 4 Core A wrap-up)**
**Run pre-registered Core A sensitivity grid and stability checks.** HANDOFF.md open question #2 + #5.
- **Tests deferred:** `phase-4/test-design.md` §4 (24-spec rank-stability grid), §5 (Jaccard overlap top-15 predicted vs. Phase 3), §6 (jackknife on train clusters, Gaussian noise injection).
- **Action:** Create `src/sensitivity_grid.py` to enumerate 3×4×2=24 composite specs; compute per-cell rank stability; flag fragile cells < 18/24. Run jackknife + noise stability. Append results to `phase-4/test-design.md` §Results and write `outputs/model-card-prpi-v1.md` per Lecture 4 §8.
- **Effort:** ~4–6 hours.
- **Owner:** Rafik.
- **Evidence:** HANDOFF.md, phase-4/test-design.md.

### 4. **MEDIUM PRIORITY (model robustness)**
**Reconcile test-cluster seed dependency.** Run three alternative k-means seeds (e.g., 42, 123, 999) and report test-R² distribution. If R² varies by >0.05 across seeds, call out the sensitivity in the model card.
- **Action:** Add seed-sweep loop to `src/split_data.py`; write per-seed metrics to `outputs/phase-4/seed-sensitivity.csv`.
- **Effort:** ~1 hour.
- **Owner:** Rafik.
- **Evidence:** HANDOFF.md open question #3.

### 5. **LOW PRIORITY (defensive)**
**Commit a requirements-lock file.** Generate `requirements-lock.txt` via `pip freeze` on the hermes-agent 3.11 venv and commit it for reproducibility.
- **Action:** Run `pip freeze > requirements-lock.txt` on the confirmed working venv; commit.
- **Effort:** ~5 minutes.
- **Owner:** Any.
- **Evidence:** Reproducibility best practice.

### 6. **LOW PRIORITY (future-proofing)**
**Add snapshot versioning metadata.** In `src/clean_data.py`, record the download date and source URL of arbrat-viari.csv at load time (via file modification timestamp). Print it to the log. Future users will see if they're using a different snapshot.
- **Action:** Add `snapshot_mtime = os.path.getmtime(VIARI_PATH)` and log it.
- **Effort:** ~15 minutes.
- **Owner:** Any.
- **Evidence:** Reproducibility best practice.

### 7. **DOCUMENTATION (no code change)**
**Update Phase 3 → Phase 4 handoff packet.** Create a checklist in `HANDOFF.md` verifying that all 8 exit artifacts (skill §11) are complete and correct before Session 5 evaluation. Current HANDOFF.md is well-written but omits this checklist.
- **Action:** Add a §"Phase 5 Handoff Checklist" with 8 items (analytical question, test design, model card Core B, sensitivity grid pre-registered, baselines code, model artifact, per-district metrics, Notebook 06 optional).
- **Effort:** ~20 minutes.
- **Owner:** Rafik.
- **Evidence:** crispdm-4-modeling skill §11.

---

## Summary Table

| Category | Risk Level | Resolved? | Blocker? |
|----------|-----------|-----------|----------|
| Asthma claim scope | CRITICAL | Partial (flagged in memory, not yet in code) | YES |
| Species palette mismatch | MAJOR | No (code still references EM-optimistic) | YES |
| Substrate hypothesis framing | MAJOR | No (sensitivity grid deferred) | NO (deferred to Core A) |
| Inventory snapshot drift | MAJOR | Acknowledged, not tracked | NO (known limitation documented) |
| Top-15 ranking divergence | MAJOR | Pre-registered but not executed | NO (test design complete, execution deferred) |
| Notebook-to-Python migration incomplete | MEDIUM | Partial (Phase 4 done, Phase 3 visualizations notebook-only) | NO (documentation exists) |
| Bug-fix patch script not integrated | MEDIUM | No (script committed to .claude/ but separate) | NO (documented in handoff) |
| Test-cluster seed dependency | MEDIUM | No (single seed 42 only) | NO (flagged as open question) |
| No pytest suite | MEDIUM | No | NO (seminar scope acceptable) |
| Requirements-lock missing | LOW | No | NO |

