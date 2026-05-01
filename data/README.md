# `data/` — How to reproduce the profiling notebook

Raw CSVs for the Ajuntament tree inventory are gitignored (~57 MB combined).
To re-run `notebooks/01-data-profiling.ipynb` from a fresh clone:

```bash
mkdir -p data
curl -L -o data/arbrat-viari.csv \
  "https://opendata-ajuntament.barcelona.cat/data/dataset/27b3f8a7-e536-4eea-b025-ce094817b2bd/resource/23124fd5-521f-40f8-85b8-efb1e71c2ec8/download"
curl -L -o data/arbrat-zona.csv \
  "https://opendata-ajuntament.barcelona.cat/data/dataset/9b525e1d-13b8-48f1-abf6-f5cd03baa1dd/resource/29cd5c1f-11b1-404b-b3a5-ae29940b8c55/download"
```

License: CC-BY 4.0 (Open Data BCN). Attribution: *Ajuntament de Barcelona,
Open Data BCN — Arbrat Viari + Arbrat de Zona.*

---

## Files in this folder (committed)

- `profile-summary.json` — machine-readable profiling output, diffable across snapshots. Real numbers from the notebook execution.

## Files NOT committed (regenerated)

- `arbrat-viari.csv` (~43 MB) — street-tree inventory
- `arbrat-zona.csv` (~14 MB) — park-tree inventory

These are auto-excluded by the repo's root `.gitignore` (`*.csv`).
Re-download via the curl commands above.

---

## Re-running the profiling notebook

```bash
# from repo root
pip install --user pandas numpy matplotlib seaborn nbformat nbconvert ipykernel
python build_notebook.py     # rebuilds + executes notebooks/01-data-profiling.ipynb
```

Or open `notebooks/01-data-profiling.ipynb` in Jupyter and run all cells.
