# Group 4 — Platanus Pollen-Allergen Priority, Barcelona

**MaAI01 25–26 · Data for All · CRISP-DM seminar project**

A batch geospatial pipeline that ranks Barcelona's 400 m grid cells to sequence the
city's committed plane-tree (*Platanus*) removal so each cut relieves the most
**pollen-allergen exposure** for the people who live there.

We started on a *mycorrhizal-fungi* recovery thesis, **falsified it ourselves** at the
Evaluation phase (three independent lines of evidence), and pivoted to the allergen
question the same data could honestly answer. The documented falsification is the
project's strongest result — a pre-registered hypothesis death is the clearest
demonstration of the CRISP-DM iteration loop.

## Start here

- **`outputs/presentation-final.html`** — 5-minute final-delivery presentation (open in browser). Press `T` to start the countdown timer, arrow keys to advance slides.
- **`outputs/reports/crispdm-phase-1-to-6-paper.md`** — the canonical narrative (all 6 CRISP-DM phases, both cycles).
- **`outputs/phase-6/maps/deployment_map.html`** — interactive priority map (section ↔ 400m toggle, street worklists).
- **`REPO-MAP.md`** — what every directory is + the real pipeline flow.

## Run the pipeline

Canonical pipeline is `src/*.py` (notebooks are narrative only). Uses the hermes-agent
venv (geopandas + scikit-learn) — see `CLAUDE.md` for the interpreter path.

```bash
python src/clean_data.py          # Phases 1-3 ETL -> data/processed/scored_grid.parquet
python src/split_data.py          # spatial cluster split -> data/splits/
python src/train_model.py         # baselines + linear model -> outputs/phase-4/
python src/external_validation.py # Phase 5 external test (the falsification)
python src/allergen_priority.py   # Phase 5 pivot product -> outputs/phase-6/ (cell grain)
python src/section_priority.py    # Phase 6 deploy: census-section grain + T1-T4 re-run
python src/street_actions.py      # Phase 6 deploy: per-street removal worklist
python scripts/build_deploy_map.py # interactive map -> outputs/phase-6/maps/deployment_map.html
```

## Repository layout

```
src/                canonical pipeline (Phases 1-6)
data/               raw + processed geo layers  (large files gitignored)
  processed/        scored_grid.parquet  <- single source of truth
  splits/           train/eval/test
outputs/
  phase-4/          modeling results + model artifact
  phase-5/          evaluation (external-validation null)
  phase-6/          SHIPPED product: allergen priority + maps
  reports/          write-ups (the canonical paper)
notebooks/          01..05 narrative exploration (NOT canonical)
scripts/            one-off helpers
phase-1/ … phase-6/ CRISP-DM graded deliverables
docs/               briefs, datasheets, logs, plans
research/crispdm/   background academic notes
.planning/          GSD planning + codebase maps
my-video/           Remotion video explainer (separate Node project)
```

See `REPO-MAP.md` for the full table and known gotchas (e.g. the two `scored_grid.geojson`
files belonging to two different toolchains).

## Working agreement

- Branch + PR for everything; no direct pushes to `main`.
- `src/*.py` is canonical — when notebooks disagree, the scripts win.
- Be brutally honest: a defensible verdict beats a flattering one (see `CLAUDE.md`).
