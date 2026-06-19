# REPO MAP — what's what

> Lost? Read this first, then the one file that explains the whole project:
> **`outputs/reports/crispdm-phase-1-to-6-paper.md`** — the canonical narrative (the "bible", all 6 phases).

## What this project is

One project, one story. We built a spatial priority map for Barcelona's 400 m grid.

1. **Original thesis (Sessions 1–4):** rank cells for *mycorrhizal-fungi* recovery, using plane-tree (*Platanus*) replacement as the lever.
2. **The twist (Session 5, Evaluation):** we **falsified our own thesis** — the index turned out to rank cells by *sealed (paved) surface*, an external test returned a flat null, and the literature didn't support the lever.
3. **The pivot (Session 6):** kept the same data, changed the question → **where to sequence Barcelona's committed plane-tree removal so each cut relieves the most pollen-allergen exposure.**

The falsification *is* the headline result. The shipped product is the pollen-allergen priority map.

## The real pipeline (inputs → outputs)

Canonical pipeline = `src/*.py` (Python). Notebooks = narrative/exploration only (CLAUDE.md rule).

```
data/ (raw geo layers)
   │  src/clean_data.py      ETL + scoring
   ▼
data/processed/scored_grid.parquet   <-- SINGLE SOURCE OF TRUTH
   │  src/split_data.py      spatial cluster split
   ▼
data/splits/{train,eval,test}.parquet
   │  src/train_model.py     baselines + linear model
   ▼
outputs/phase-4/   metrics, model_artifact.joblib, predictions
   │  src/external_validation.py + phase5_robustness.py   (Phase 5 falsification)
   ▼
outputs/phase-5/   external_validation_results  (the null that killed the thesis)
   │  src/allergen_*.py, exposure_layer.py, equity_layer.py  (the pivot)
   ▼
outputs/phase-6/   allergen_priority_results + maps   <-- SHIPPED PRODUCT
```

## Top-level directories

| Dir | What it is | Keep / note |
|-----|-----------|-------------|
| `src/` | **Canonical pipeline** — 12 Python scripts, Phases 1→6 | the real code |
| `data/` | Raw + processed geo layers (large files gitignored) | inputs |
| `data/processed/` | Pipeline outputs; `scored_grid.parquet` is canonical | source of truth |
| `data/splits/` | Train/eval/test spatial split | frozen |
| `outputs/phase-4/` | Modeling results (linear model, metrics) | |
| `outputs/phase-5/` | Evaluation — the external-validation null | the falsification |
| `outputs/phase-6/` | **Shipped product** — allergen priority + maps | headline |
| `outputs/reports/` | Write-ups; **the canonical paper lives here** | read the paper |
| `outputs/maps/`, `outputs/figures/` | Rendered HTML maps + PNG figures | render artifacts |
| `outputs/model-card-*.md` | Model cards (mycorrhizal v1 + allergen v1) | |
| `notebooks/` | `01..05` narrative exploration only — **NOT canonical** | mirror of src/ logic |
| `scripts/` | One-off helpers (download, fixes, regenerate, viz) | not part of pipeline |
| `phase-1/ … phase-6/` | CRISP-DM phase deliverables (decisions, contracts, audits) | graded artifacts |
| `docs/` | Briefs, datasheets, cleaning logs, plans | project docs |
| `research/crispdm/` | Background academic notes per CRISP-DM phase | reference |
| `.planning/` | GSD planning (PROJECT, ROADMAP, REQUIREMENTS, codebase maps) | process meta |
| `my-video/` | Remotion video explainer (separate Node project) | self-contained; `build/` now gitignored |
| `session-3/` | One session's briefing + task ownership | snapshot |
| `assets/` | Course PDF | reference |

## Phase 2 data-understanding artifacts (Rafik)

Rafik's Phase 2 work lives in `phase-2/` and covers all data-understanding deliverables.
See `phase-2/ingestion-log.md` for the SHA-256-stamped retrieval record of every raw file.

| Sub-path | What it is |
|---|---|
| `phase-2/data-sheets/ajuntament-trees.md` | Full "Datasheets for Datasets" (Gebru et al. 2021) for the **primary** dataset — Barcelona municipal tree inventory (Arbrat Viari + Arbrat Zona) |
| `phase-2/data-sheets/gbif-fungi.md` | Full datasheet for the **secondary** dataset — GBIF fungal occurrences (Catalonia / Barcelona, 2015–2024) |
| `phase-2/schemas/ajuntament-trees.py` | Pandera schema validator for `data/arbrat-viari.csv` + `data/arbrat-zona.csv` |
| `phase-2/schemas/fungalroot.py` | Pandera schema validator for `data/fungalroot.csv` |
| `phase-2/schemas/gbif-fungi.py` | Pandera schema validator for `data/gbif-fungi.json` |
| `phase-2/schemas/spatial-layers.yaml` | CRS + bounds + nodata contracts for rasters/vectors: Urban Atlas FlatGeobuf, Landsat LST GeoTIFFs, Sentinel-2 NDVI GeoTIFFs, BCN boundary GeoJSONs |
| `phase-2/croissant/ajuntament-trees.jsonld` | Croissant ML JSON-LD metadata record — Ajuntament tree inventory |
| `phase-2/croissant/fungalroot.jsonld` | Croissant ML JSON-LD — FungalRoot v2.0 |
| `phase-2/croissant/gbif-fungi.jsonld` | Croissant ML JSON-LD — GBIF fungal occurrences |
| `phase-2/croissant/landsat-lst.jsonld` | Croissant ML JSON-LD — Landsat 8/9 LST summer composite |
| `phase-2/croissant/sentinel2-ndvi.jsonld` | Croissant ML JSON-LD — Sentinel-2 NDVI summer composite |
| `phase-2/croissant/urban-atlas.jsonld` | Croissant ML JSON-LD — Copernicus Urban Atlas 2018 |
| `phase-2/pollen-gaps/data-inventory.md` | Phase 2 extension (June 2026): data hunt for allergen-model gaps — per-tree size, pollarding regime, NO2 surface. CALIOPE-Urban NO2 adopted; others documented as open gaps. |
| `phase-2/pollen-gaps/caliope-gate.md` | Pre-wiring gate for CALIOPE-Urban NO2 (Zenodo 16737066): collinearity (Pearson 0.22) + variance decomposition (9% of weighted-map variance) — verdict PASS, non-dominating ordinal potency lens |
| `phase-2/pollen-gaps/data-sheets/caliope-urban-no2.md` | Full datasheet for CALIOPE-Urban NO2 |
| `phase-2/ingestion-log.md` | SHA-256-stamped retrieval log for all 9 raw data files (Ajuntament trees, FungalRoot, GBIF, BCN boundaries, Urban Atlas, Landsat LST, Sentinel-2) |

## Known confusions (read before you trip on them)

- **Two `scored_grid.geojson` files, both live, different toolchains:**
  - `data/processed/scored_grid.geojson` — written by `src/clean_data.py` (canonical pipeline).
  - `data/scored_grid.geojson` — read/written by notebooks `03/04/05` and `scripts/regenerate_priority_csv.py`.
  - They are **not** copies; deleting either breaks one toolchain. Treat `data/processed/` as authoritative; the root one is the notebook mirror.
- **CRISP-DM artifacts live in several homes by purpose, not duplication:** `phase-N/` = graded deliverables, `docs/` = working briefs, `research/crispdm/` = background reading, `.planning/` = GSD process. Not redundant — different audiences.
- **`.claude/fix_pipeline.py`** is a documented 13-bug-fix patch script referenced by name in `.planning/codebase/CONCERNS.md` and `outputs/reports/`. It lives at that path on purpose — don't move it.
- **Notebooks vs `src/`:** when they disagree, `src/*.py` wins (CLAUDE.md). Notebooks are for narrative.

## Recent cleanup (this commit)

- Untracked `my-video/build/` (35 generated webpack bundles) → added to `my-video/.gitignore`.
- Removed stray `Seek_Deep_CHINA.md` (an unrelated DeepSeek API config note).
- Moved one-off scripts `generate_briefing.py`, `analyze_pipeline.py`, `generate_session3_pptx.py` → `scripts/`.
- Removed 4 stale render duplicates from `outputs/maps/` and `outputs/figures/` (superseded by newer copies in `outputs/`; recoverable from git history).
