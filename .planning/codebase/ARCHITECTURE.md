# Architecture

_Mapped: 2026-06-04_

## Overall Pattern

Batch geospatial ETL pipeline producing a priority map for urban mycorrhizal fungi across Barcelona's 400m grid. The pipeline follows CRISP-DM phases 1–4 as project scaffolding, runs as numbered Jupyter notebooks (01–05) backed by reusable Python scripts in `src/`, with data flowing through a lake structure (`data/raw/` → `data/processed/` → `data/splits/`) and outputs to `outputs/`.

This is **notebook-driven exploratory analysis** for phases 1–3, transitioning to **script-driven deterministic reproducibility** for phase 4 onward (predictive validation).

---

## Pipeline Stages / Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ 01. Data Profiling                                                  │
│     Input:  arbrat-viari.csv, arbrat-zona.csv (Ajuntament BCN)      │
│     Output: profile-summary.json, data-quality-audit.md             │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 02. Data Cleaning (& 02b. Grid + Trees)                             │
│     Script: src/clean_data.py                                       │
│     Inputs: tree inventory (combined), GBIF fungi, FungalRoot v2.0, │
│             satellite rasters (Landsat LST, Sentinel NDVI),         │
│             Urban Atlas, BCN boundary/districts                     │
│     Steps:                                                           │
│       - Normalize species names, join FungalRoot lookup             │
│       - Assign mycorrhizal type (AM/EM/NM) per tree                 │
│       - Build 400m grid on Barcelona boundary (EPSG:25831)          │
│       - Spatial join: trees → grid cells                            │
│       - Zonal stats: sealed surface, LST, NDVI per cell             │
│       - Tree stats: counts, fractions, richness, Platanus pct       │
│     Output: data/processed/scored_grid.parquet (.geojson preview)   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 03. Scoring & Composites (Phase 3)                                  │
│     Part of src/clean_data.py                                       │
│     Steps:                                                           │
│       - Compute 4 sub-scores (S1–S4) from base features             │
│       - Compute PRPI (Platanus Replacement Priority Index) v1.1     │
│       - Compute VPA allergenicity + species preference (v1.2)       │
│       - Compute 3 composite scenarios (A, B, C) — 5-term weighting  │
│       - Flag top-15 priority cells (Scenario B, district-constrained)│
│       - Classify intervention type + replacement flag               │
│     Output: scored_grid (with all scoring columns)                  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 04. Spatial Split (Phase 4 Core A prep)                             │
│     Script: src/split_data.py                                       │
│     Input:  data/processed/scored_grid.parquet                      │
│     Method: K-means clustering (k=5) on cell centroids (x,y)        │
│            in EPSG:25831, sorted by cluster size (deterministic)    │
│     Mapping:                                                         │
│       clusters 0,1,2 → train  (~60%)                                │
│       cluster 3      → eval   (~20%)                                │
│       cluster 4      → test   (~20%, FROZEN)                        │
│     Outputs: data/splits/                                           │
│       - cluster_assignments.parquet                                 │
│       - train.parquet, eval.parquet, test.parquet                   │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 05. Model Training (Phase 4 Core B)                                 │
│     Script: src/train_model.py                                      │
│     Inputs: data/splits/{train,eval,test}.parquet                   │
│     Models:                                                          │
│       - LinearRegression (fit_intercept tuned on eval)              │
│       - 3 baselines: Mean, SpatialNearest (cKDTree), DomainHeuristic│
│     Target: composite_score_B (from Phase 3)                        │
│     Features (10 raw): mean_sealed, mean_ndvi, lst_anomaly,         │
│              am_pct, em_pct, platanus_pct, cell_vpa_score,          │
│              species_richness, total_trees, trees_young_pct         │
│     Outputs: outputs/phase-4/                                       │
│       - metrics.csv (R², MAE, RMSE per estimator × split)           │
│       - predictions.parquet (cell_id, split, y_true, y_pred)       │
│       - model_artifact.joblib (fitted pipeline)                     │
│       - per_district.csv (test residuals by district)               │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 06. Visualization & Outputs (Phase 3, ongoing)                      │
│     Notebooks: 04-connectivity.ipynb, 05-visualisation.ipynb        │
│     Outputs: outputs/                                               │
│       - priority_map.html (interactive Folium map, Scenario B)       │
│       - priority_zones.csv / .html (district-ranked cells)          │
│       - network_nodes/edges/islands.geojson (mycorrhizal network)   │
│       - sensitivity_comparison.png (scoring sensitivity audit)      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Layers / Abstractions

### Data Layer (`data/`)
- **raw/**: Minimal preprocessing (VPA species list)
- **processed/**: scored_grid output from clean_data.py; definitive single source of truth for phases 3–4
- **splits/**: Train/eval/test parquets and cluster assignments (phase 4)
- **{landsat, sentinel2, urban-atlas}/**: Raster and vector coverages (satellite/land-cover data)

### Script Layer (`src/`)
Reusable, deterministic Python modules:
- **clean_data.py**: All-in-one phase 1–3 ETL (189k trees → 400m grid scoring)
- **split_data.py**: Spatial clustering and train/eval/test assignment
- **baselines.py**: Three sklearn-compatible baseline estimators
- **train_model.py**: Model training, evaluation, and artifact export

### Notebook Layer (`notebooks/`)
Interactive exploration + narrative:
- **01-data-profiling.ipynb**: 189k tree inventory shape, distributions, anomalies
- **02-data-cleaning.ipynb**: Species name normalization, FungalRoot join (archived; logic moved to src)
- **02-grid-trees.ipynb**: 400m grid construction, spatial tree joins
- **03-scoring.ipynb**: PRPI computation, composite indices, intervention classification
- **04-connectivity.ipynb**: Mycorrhizal network topology (edge/island analysis)
- **05-visualisation.ipynb**: Interactive map generation, sensitivity plots

### Documentation Layer (`phase-*`, `docs/`)
- **phase-1/**: Business understanding (Heilmeier, decision unit, risks, glossary)
- **phase-2/**: Data inventory, ingestion log, quality audit, data sheets, schemas
- **phase-3/**: Data cleaning report, data contract (YAML schema), ADRs, session verification
- **phase-4/**: Analytical question, test design (pre-registered), modeling guidelines, ADRs
- **docs/**: Pipeline architecture, data source inventory, problem brief

---

## Entry Points

### Full Reproducibility (Clean Checkout)
```bash
# Download all raw datasets (trees, GBIF, FungalRoot, satellite, Urban Atlas)
python scripts/download_all.py

# Run the deterministic pipeline (phases 1–3 logic encapsulated)
python src/clean_data.py

# Phase 4: spatial split + modeling
python src/split_data.py
python src/train_model.py
```

No notebooks need to be run by a user; they are for exploration and narrative. The **canonical implementation** is in `src/*.py`.

### Interactive Exploration
Run notebooks in sequence (01 → 05) to see analysis flow and interpretations, but note that phases 1–3 logic has been extracted to `src/clean_data.py` for reproducibility.

### Key Outputs (What Does Success Look Like?)
- **scored_grid.parquet** (data/processed/): 442 cells × 80+ columns; one row per 400m grid cell with trees, species richness, mycorrhizal composition, raster features, all sub-scores and composites, intervention type, priority flag.
- **Model card + metrics** (outputs/phase-4/): R² 0.877 (test), MAE 0.0106 on linear regression over 10 raw features, beats all three baselines.
- **Priority map** (outputs/): Folium HTML showing top-15 cells, ranked by composite_score_B, color-coded by intervention type.

---

## Key Artifacts (The "Models" / Outputs)

### Data Artifacts
| File | Format | Source | Purpose | Size |
|------|--------|--------|---------|------|
| **scored_grid.parquet** | Parquet | src/clean_data.py | Single source of truth; all cell-level features + scores | ~228 KB |
| **scored_grid.geojson** | GeoJSON | src/clean_data.py | Preview of scored_grid with geometry | ~1.2 MB |
| **train.parquet** | Parquet | src/split_data.py | Training split (clusters 0–2) | ~168 KB |
| **eval.parquet** | Parquet | src/split_data.py | Validation split (cluster 3) | ~89 KB |
| **test.parquet** | Parquet | src/split_data.py | Test split (cluster 4), FROZEN | ~84 KB |
| **cluster_assignments.parquet** | Parquet | src/split_data.py | cell_id → cluster_id → split mapping | ~5 KB |

### Model Artifacts (Phase 4)
| File | Format | Content |
|------|--------|---------|
| **model_artifact.joblib** | Joblib | Fitted sklearn Pipeline: SimpleImputer + LinearRegression |
| **metrics.csv** | CSV | R², MAE, RMSE for each estimator × split (train/eval/test) |
| **predictions.parquet** | Parquet | cell_id, split, composite_score_B (y_true), all y_pred columns |
| **per_district.csv** | CSV | Residuals (y_true − y_pred) by district (test set only) |

### Visualization Outputs
| File | Format | Content | Audience |
|------|--------|---------|----------|
| **priority_map.html** | Folium | Interactive map of top-15 cells + network | Ajuntament / analyst |
| **priority_zones.csv** | CSV | Ranked cells: cell_id, rank, district, composite_score_B | Decision-maker export |
| **grid_trees.geojson** | GeoJSON | Grid cells + tree counts + species richness | QA + mapping |
| **network_nodes.geojson** | GeoJSON | Mycorrhizal network nodes (fungi + trees) | Research / interpretation |
| **network_edges.geojson** | GeoJSON | Network edges (fungal→tree links) | Research / interpretation |
| **sensitivity_comparison.png** | PNG | Heatmap of 24 scoring scenarios vs baseline | Robustness audit |

---

## Phase Structure (CRISP-DM Scaffolding)

**Phase 1: Business Understanding** (`phase-1/`)
- Decision unit: Superilla / 400m grid for capital allocation (Eixos Verds budget)
- User: analyst at Ajuntament Espais Verds / Barcelona Regional
- Success: defensible priority ranking for urban mycorrhizal fungi

**Phase 2: Data Understanding** (`phase-2/`)
- Inventory: tree taxonomy, GBIF fungi, satellite/land-cover, costs
- Quality audit: completeness, consistency, representativeness
- Data sheets: each source (Bender et al. 2021 template)

**Phase 3: Data Preparation** (`phase-3/`)
- Cleaned tree inventory (189k → 442 grid cells)
- Scoring sub-components (S1–S4) + PRPI v1.1 + VPA v1.2
- Three composite scenarios (A, B, C); top-15 flagging; intervention classification
- Data contract (YAML schema); ADRs on species priority, AM-only assumption

**Phase 4: Modeling** (`phase-4/`)
- Core A (deferred): PRPI sensitivity grid (24 specs: 3 normalizations × 4 weighting × 2 aggregations)
- Core B (complete): Linear regression on 10 raw features; spatial cluster split (k=5); model card with ≥3 NOT statements

---

## Summary Callouts

- **No APIs or real-time processing.** All data is static snapshots (2024–Q1 2026 vintage).
- **No ML model serving.** Output is a scored grid CSV + priority map HTML; the linear model is validation artifact, not production.
- **CRISP-DM is the roadmap.** Phases 1–3 are exploratory (notebooks), phase 4 begins systematic validation (scripts).
- **Windows + Python 3.11.** Hermes agent venv; requires `geopandas`, `scikit-learn`, `joblib`, `pandas`, `numpy`, `requests`.
