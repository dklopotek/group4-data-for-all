# How to re-run (one page)

Reproduces every Phase-6 number from raw data on disk. Deterministic (seed 42) — outputs match
the SHA-256 hashes in `release/manifest.json`.

## 1. Environment
```bash
# Windows (the project's interpreter):
#   C:\Users\<you>\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe
# or a fresh env:
conda create -n bcn python=3.11 -c conda-forge geopandas=1.0.1 scikit-learn=1.8.0 -y
conda activate bcn
pip install -r release/requirements-lock.txt
```

## 2. Inputs (already in the repo)
- `data/arbrat-viari.csv` — street-tree inventory
- `data/raw/2026_pad_mdbas.csv` — population by census section
- `data/raw/Unitats_Administratives_BCN_geojson/0301100100_UNITATS_ADM_POLIGONS.json` — section polygons
- `data/processed/allergen_layers.parquet` — Phase-5 cell product (for the MAUP rollup check)

## 3. Run (Windows console needs UTF-8 for any non-ASCII)
```bash
set PYTHONIOENCODING=utf-8          # Windows; or export on *nix
python src/section_priority.py      # -> outputs/phase-6/section_priority.{parquet,csv,md,json}
python src/street_actions.py        # -> outputs/phase-6/street_removal_actions.csv + points.geojson
python scripts/build_deploy_map.py  # -> outputs/phase-6/maps/deployment_map.html
```

## 4. Verify
- `section_priority.py` prints `C1 assertions PASSED` (1,068 sections, ~1.73M pop).
- `street_actions.py` prints `HONESTY GATE ... PASS` and `street-match coverage: 100.0%`.
- Open `outputs/phase-6/maps/deployment_map.html` in any browser (needs internet for basemap tiles only).
- Numbers reproduce the paper §8 and `phase-6/section-street-design.md` Results.

The earlier phases (1–5) rebuild via `src/clean_data.py → split_data.py → train_model.py →
external_validation.py → allergen_source.py → exposure_layer.py → allergen_priority.py` (see README).
