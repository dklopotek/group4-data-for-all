# CLAUDE.md — Mycorrhizal Barcelona

Project instruction file for AI agents working in this repo. Managed alongside GSD planning in `.planning/`.

## Project

Mycorrhizal Barcelona — a batch geospatial pipeline that ranks Barcelona's 400m grid cells for urban mycorrhizal-fungi barrier reduction, for a capital-planning analyst at Ajuntament Espais Verds / Barcelona Regional. CRISP-DM seminar project (MaAI01 25-26). See `.planning/PROJECT.md` for full context.

**Current milestone:** Session 5 = CRISP-DM **Phase 5 (Evaluation)**. Roadmap in `.planning/ROADMAP.md`, requirements in `.planning/REQUIREMENTS.md`. Hybrid Track A (linear model = evidence) + Track B (priority ranking = headline conclusion).

## Locked project rules

- **Lecture > skill.** When the seminar lecture and any CRISP-DM skill conflict, the lecture wins — it is the grading rubric. Phase 4 anchor: `Session 4/Lecture_4.md`; Phase 5 (Evaluation) is the current rubric.
- **Recommend, don't ask.** Drive decisions with rationale; ask only for a veto. No multi-question Socratic prompts.
- **Pre-registration is binding.** `phase-4/test-design.md` was written before the build. Every pre-registered test must run and every result must be reported — including unfriendly ones. Silently dropping a pre-registered test is the cardinal Phase 4 sin.
- **No decision-facing UI this session.** Lecture is explicit: evaluation first, UI deferred to Phase 6.
- **Frozen data.** `data/processed/scored_grid.parquet`, `model_artifact.joblib`, and the splits are the single source of truth. No new data ingestion, no re-deriving Phases 1-3, this session.
- **Be brutally honest.** A defensible verdict (deploy / iterate / stop, with stated confidence) beats polished results. Document every failure as a limit; do not bias toward making the system look like it works.

## Tech & environment

- Python 3.11 on the **hermes-agent venv** (`C:\Users\Rafik\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe`) — has geopandas + scikit-learn. Confirm the interpreter before any `pip install`. `py -3.12` is NOT available.
- Stack: geopandas, scikit-learn, rasterio, shapely, pandas, numpy, joblib. Full list in `.planning/codebase/STACK.md`.
- **Windows cp1252 console** — no Unicode (─, ×, etc.) in `print()` without `PYTHONIOENCODING=utf-8`. Use ASCII (`--`, `x`) in console output.
- Determinism: all randomness seeded (k-means seed 42); test cluster frozen at split time, never inspected until final assessment.

## Pipeline entry points

```bash
python src/clean_data.py     # Phases 1-3 ETL → data/processed/scored_grid.parquet
python src/split_data.py      # spatial cluster split → data/splits/
python src/train_model.py     # baselines + linear model → outputs/phase-4/
```

Notebooks (`notebooks/01..05`) are narrative/exploration only; `src/*.py` is canonical.

## GSD workflow

This project uses GSD planning. Phase artifacts live in `.planning/`. Next: `/gsd-plan-phase 1`.
Run `/gsd-progress` to see status. Codebase map: `.planning/codebase/`.
