# Handoff — Session 4 closed · CRISP-DM Phase 4 Core B shipped · ready for Session 5

**Created:** 2026-05-26 by Claude Code session (Opus 4.7, 1M ctx)
**Branch:** main
**Last commit (Phase 3):** 859bda9 — Session 3 closeout: ship CRISP-DM Phase 3 pipeline + PRPI v1.2
**Phase 4 commit:** pending (this commit)

## Goal
Build a barrier-reduction priority map for urban mycorrhizal fungi across Barcelona's 400m grid that a capital-planning analyst at Ajuntament Espais Verds / Barcelona Regional can use to allocate Eixos Verds / Superilla budget. CRISP-DM Phases 1–4 are complete. Session 4 turns the `scored_grid.parquet` into a predictive-model validation artifact with proper spatial splits, baselines, and a defensible model card.

## Current state — Phase 4 Core B (predictive validation) DONE

**Predictive model trained.** Linear regression over 10 raw features (no leakage from Phase 3 sub-scores) predicts `composite_score_B` on held-out spatial clusters. End-to-end runs via `python src/clean_data.py && python src/split_data.py && python src/train_model.py`.

**Headline metrics (test cluster, n = 88 cells in Sarrià-Sant Gervasi + Les Corts):**

| Estimator | R² | MAE | RMSE |
|---|---|---|---|
| **LinearRegression** | **0.877** | **0.0106** | **0.0509** |
| BaselineSpatialNearest | -0.290 | 0.130 | 0.165 |
| BaselineMean | -0.616 | 0.142 | 0.185 |
| BaselineDomainHeuristic | -0.622 | 0.143 | 0.185 |

Pre-registered pass criterion (beat all three baselines on test R² AND test MAE) **PASS**.

**Substantive finding.** Eval R² 0.999 → test R² 0.877. The 6× MAE gap (0.0017 → 0.0106) is the honest spatial generalization cost — `composite_score_B` is approximately linear in raw raster inputs within similar geography but degrades on out-of-sample geography. Implication: the Phase 3 composite carries little information beyond a linear re-skin of `mean_sealed` and friends, AND its absolute calibration depends on the geographic mix of training cells.

**Pipeline / build status:** all three Phase 4 scripts run from a clean checkout against the Phase 3 parquet. `python src/train_model.py` exits 0 and writes 4 artefacts under `outputs/phase-4/` plus 4 parquets under `data/splits/`. No formal pytest yet (carried over from Session 3).

## Files in flight
None at this commit. All Phase 4 artefacts are committed and on disk.

## What changed this session

1. **Lecture > skill priority established.** When the Session 4 lecture rubric and the `crispdm-4-modeling` skill conflict, lecture wins (the lecture is the grading rubric). Saved as `~/.claude/projects/.../memory/feedback-lecture-priority.md`.
2. **Recommend-don't-ask feedback recorded.** User wants me to drive Phase decisions with rationale, not Socratic Q&A. Saved as `feedback-recommend-dont-ask.md`.
3. **Whisper transcription wired up.** Local whisper.exe at hermes venv now used to auto-transcribe Telegram voice messages. Saved as `reference-whisper-local.md`.
4. **phase-4/analytical-question.md** — canonical one-sentence question, decision-maker, success criterion, leakage check, routing.
5. **phase-4/test-design.md** — pre-registered split / baselines / model / sensitivity grid / construct validity protocol. Results appended post-build.
6. **src/split_data.py** — k-means spatial cluster split (k=5, seed 42) on cell centroids in EPSG:25831. Writes `data/splits/cluster_assignments.parquet` + `train.parquet` / `eval.parquet` / `test.parquet`. Test cluster frozen at split time.
7. **src/baselines.py** — three sklearn-style baselines: `BaselineMean`, `BaselineSpatialNearest` (cKDTree on centroids), `BaselineDomainHeuristic` (sealed > 0.7 → 90th percentile, else mean).
8. **src/train_model.py** — fits the three baselines + tunes `fit_intercept` on eval for `LinearRegression`. Writes `metrics.csv`, `per_district.csv`, `predictions.parquet`, `model_artifact.joblib`. Single tuned model per Lecture 4 line 415.
9. **outputs/model-card-v1.md** — Mitchell et al. (2019) template with 5 NOTs (lecture demands ≥ 3), per-segment metrics, robustness statement, interpretability statement, MAUP / edge-effects / equity / snapshot limitations, versioning, reviewers.
10. **requirements.txt** — added `scikit-learn>=1.5,<2.0` for Phase 4.

## What we tried that didn't work
- **Unicode "─" in `print()` statement in `src/train_model.py`.** Same Windows cp1252 trap as Session 3. Replaced with `--`. Do not re-introduce Unicode in console output without setting `PYTHONIOENCODING=utf-8`.
- **`py -3.12 -c "import sklearn"`.** Fails — only 3.11 (Astral) and 3.13 are installed. Phase 4 was run on the hermes-agent 3.11 venv (`C:\Users\Rafik\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`) which already had geopandas. `pip install scikit-learn` added to that venv. Future sessions: confirm interpreter before `pip install`.
- **Raw bash `cd src && python train_model.py` from the agent shell.** Works, but `git diff HANDOFF.md` then fails with "unknown revision" because the agent shell pwd has changed. Use `git -C <project-root>` to keep git calls path-stable, OR avoid `cd` and use absolute script paths.
- **Asking the user 4 multi-choice questions on Telegram for Phase 4 routing.** User explicitly pushed back via voice ("you would have to help me answer these"). New default: recommend with rationale, ask only for veto. See `feedback-recommend-dont-ask.md`.
- **Asking the user to type out a Telegram voice note.** Transcription is wired up via local whisper. Do NOT ask the user to type a voice they already recorded — transcribe it.

## Open questions / decisions pending
1. **Core A (PRPI composite finalization) not yet built.** Sensitivity grid (24 specs: 3 normalizations × 4 weight schemes × 2 aggregations) and jackknife / noise stability are pre-registered in `phase-4/test-design.md §4–§6` but deferred from Session 4 to keep Core B closeout shippable. Next session, run them and produce a second model card `outputs/model-card-prpi-v1.md`.
2. **Sensitivity coverage of Core B.** Pre-registered jackknife (drop-one train cluster) and Gaussian-noise injection were not executed this session. Flagged as a gap in `outputs/model-card-v1.md §7`. Quick to add — one short script.
3. **Test-cluster representativeness.** k-means seed 42 produced a wealthy NW test cluster. A different seed gives a different cluster; consider running 3 alternative seeds as a meta-sensitivity check and reporting the test-R² distribution.
4. **Notebook 06-modeling.ipynb (optional).** Could be a narrative walk-through of the Phase 4 pipeline for the instructor demo, parallel to the `src/*.py` canonical implementation. Not on the critical path.
5. **Peri-urban OOD test patch (carryover from Session 2 agenda).** Collserola / Garraf / El Prat cells not in pipeline. Worth pulling in for Session 5 as an out-of-distribution probe.
6. **Push to GitHub for instructor + Salvador review** — done this session per Lecture 4 action items.

## Next steps
1. **Run pre-registered Core A sensitivity grid** (`phase-4/test-design.md §4`). Output: `outputs/phase-4/sensitivity-grid.csv` + per-cell rank-stability column.
2. **Run pre-registered Core B stability checks** (`phase-4/test-design.md §6`): jackknife on train clusters + Gaussian noise injection. Output: append `## Stability` section to `phase-4/test-design.md`.
3. **Write `outputs/model-card-prpi-v1.md`** — Mitchell card for the PRPI composite itself, distinct from the Core B regression model card.
4. **Construct-validity probes** (`phase-4/test-design.md §5`): convergent / discriminant correlations + Jaccard overlap of top-15 predicted vs Phase 3 `top15_flag`.
5. **Phase 5 (Evaluation) handoff packet.** Per skill §11, the 8 exit artefacts must cross from Phase 4 to Phase 5 BEFORE the review. Inventory what's done vs what's pending; close gaps before Session 5.

## How to resume
Paste into the new Claude Code session:
> Read `HANDOFF.md` at the project root and continue from "Next steps" item 1. Lecture > skill priority is locked. Do not re-explore territory listed under "What we tried that didn't work" unless the listed condition is met.
