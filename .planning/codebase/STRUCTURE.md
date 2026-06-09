# Directory Structure

_Mapped: 2026-06-04_

---

## Top-Level Layout

```
group4-data-for-all/
├── .claude/                          # Claude Code workspace config + skills directory
├── .git/                             # Git repository metadata
├── .planning/                        # Planning & architecture docs (you are here)
│   └── codebase/                     # Codebase maps (ARCHITECTURE.md, STRUCTURE.md)
├── .vscode/                          # VS Code workspace settings
├── assets/                           # Static images, logos, visual references
├── data/                             # Data lake (ETL hub) — see subsection below
├── docs/                             # Reference documentation (problem brief, audits, inventories)
├── notebooks/                        # Jupyter exploration (01-profiling → 05-visualisation)
├── outputs/                          # Final exports (maps, metrics, model artifacts)
├── phase-1/                          # CRISP-DM Phase 1: Business Understanding
├── phase-2/                          # CRISP-DM Phase 2: Data Understanding
├── phase-3/                          # CRISP-DM Phase 3: Data Preparation
├── phase-4/                          # CRISP-DM Phase 4: Modeling (Core A/B, ADRs)
├── research/                         # Literature, precedents, background studies
├── scripts/                          # Standalone downloaders (data ingestion helpers)
├── src/                              # Core ETL/ML pipeline modules (deterministic Python)
├── session-3/                        # Session 3 closure artifacts (presentation, logs)
├── MaAI01 25-26 - T03S13_Data -- DOCUMENTS/  # Seminar materials (sessions 1–4)
├── my-video/                         # Video editing workspace (unrelated)
├── HANDOFF.md                        # Current session handoff (state, open questions, next steps)
├── README.md                         # Project brief + structure
└── Seek_Deep_CHINA.md                # [untracked; git status shows as modified]
```

---

## Key Locations

### Where to Find...

| Item | Path | Format | Notes |
|------|------|--------|-------|
| **Raw tree inventory** | `data/arbrat-viari.csv`, `data/arbrat-zona.csv` | CSV | ~189k trees; Ajuntament BCN; combined in 01-data-profiling.ipynb |
| **Processed scored grid** | `data/processed/scored_grid.parquet` | Parquet | 442 cells × 80+ cols; source of truth for phase 3–4 |
| **Train/eval/test splits** | `data/splits/{train,eval,test}.parquet` | Parquet | Phase 4 modeling splits (spatial cluster-based) |
| **Cluster assignments** | `data/splits/cluster_assignments.parquet` | Parquet | cell_id → cluster_id → split mapping |
| **Satellite data** | `data/{landsat,sentinel2,urban-atlas}/` | GeoTIFF, Parquet | Raster/vector coverages for zonal stats |
| **Phase 1 decisions** | `phase-1/{situation,decision-statement,heilmeier,risks}.md` | Markdown | Business context, user persona, success criteria |
| **Phase 2 inventory** | `phase-2/data-inventory.md`, `phase-2/data-sheets/` | Markdown + CSV | Dataset catalogs per Bender et al. (2021) |
| **Phase 3 data contract** | `phase-3/data-contract.yaml` | YAML | Output schema for scored_grid |
| **Phase 3 ADRs** | `phase-3/adrs/` | Markdown | Architectural decisions (species priority, AM-only) |
| **Phase 4 test design** | `phase-4/test-design.md` | Markdown | Pre-registered split, baselines, metrics, sensitivity grid |
| **Phase 4 analytical question** | `phase-4/analytical-question.md` | Markdown | Canonical question, decision-maker, success criterion |
| **Phase 4 model card** | `outputs/model-card-v1.md` | Markdown | Mitchell template; metrics, limitations, reviewers |
| **Model artifact** | `outputs/phase-4/model_artifact.joblib` | Joblib | Fitted sklearn Pipeline (Imputer + LinearRegression) |
| **Model metrics** | `outputs/phase-4/metrics.csv` | CSV | R², MAE, RMSE per estimator × split |
| **Predictions** | `outputs/phase-4/predictions.parquet` | Parquet | cell_id, split, y_true, y_pred for all estimators |
| **Priority map** | `outputs/priority_map.html` | Folium HTML | Interactive map; top-15 cells; district-ranked |
| **Priority zones** | `outputs/priority_zones.csv` | CSV | Ranked cells for decision-maker export |
| **Grid + trees** | `outputs/grid_trees.geojson` | GeoJSON | 400m grid + tree counts + richness (preview) |
| **Mycorrhizal network** | `outputs/network_{nodes,edges,islands}.geojson` | GeoJSON | Fungal→tree topology for connectivity analysis |
| **Session handoff** | `HANDOFF.md` | Markdown | Current state, commits, what changed, open questions, next steps |

---

## data/ Subtree (The Data Lake)

```
data/
├── raw/                              # Minimal preprocessing only
│   └── vpa-mediterranean-species.csv # VPA allergenicity reference (Cariñanos & Marinangeli 2021)
│
├── processed/                        # Phase 3 output; single source of truth
│   ├── scored_grid.parquet          # 442 cells × 80+ cols (geometry, trees, scores, all composites)
│   └── scored_grid.geojson          # GeoJSON preview of same
│
├── splits/                           # Phase 4 spatial cluster splits
│   ├── cluster_assignments.parquet  # cell_id → cluster_id → split mapping (k=5, seed=42)
│   ├── train.parquet                # clusters 0,1,2 (~60% of cells)
│   ├── eval.parquet                 # cluster 3 (~20% of cells)
│   └── test.parquet                 # cluster 4 (~20% of cells, FROZEN)
│
├── landsat/                          # Landsat 8/9 Surface Temperature (pre-computed zonal stats)
│   └── [GeoTIFF/Parquet tiles]      # Downloaded via Planetary Computer; zonal stats extracted to scored_grid
│
├── sentinel2/                        # Sentinel-2 L2A NDVI (pre-computed zonal stats)
│   └── [GeoTIFF/Parquet tiles]      # Downloaded via Planetary Computer; zonal stats extracted to scored_grid
│
├── urban-atlas/                      # Copernicus Urban Atlas (land-cover classification)
│   └── [GeoTIFF/Shapefile]          # Sealed surface % per cell computed as zonal stat
│
├── [CSV/JSON root files]             # Ingested source datasets (static snapshots)
│   ├── arbrat-viari.csv             # Street trees (145k rows) — Ajuntament BCN
│   ├── arbrat-zona.csv              # Park trees (43k rows) — Ajuntament BCN
│   ├── arbrat-viari-prev-snapshot.csv # Archive snapshot for change detection (not used)
│   ├── fungalroot.csv               # FungalRoot v2.0 lookup (species → mycorrhizal type)
│   ├── gbif-fungi.json              # GBIF fungal occurrences (observations within BCN)
│   ├── gbif-fungi-all.json          # Backup copy (larger)
│   ├── bcn-boundary.geojson         # Municipal boundary (1 polygon)
│   ├── bcn-districts.geojson        # District boundaries (10 polygons)
│   ├── intervention_costs.json      # Cost assumptions (tree replacement, planting)
│   ├── profile-summary.json         # Profiling output (01-data-profiling.ipynb)
│   └── README.md                    # Data lake overview + Zenodo / OpenData BCN URLs
```

### Data Provenance

| Dataset | Source | Format | Vintage | Size | Usage |
|---------|--------|--------|---------|------|-------|
| **Tree inventory (viari)** | Ajuntament BCN (Open Data) | CSV | 2024-Q4 / 2026-Q1 | 41 MB | Spatial join → grid tree stats |
| **Tree inventory (zona)** | Ajuntament BCN (Open Data) | CSV | 2024-Q4 / 2026-Q1 | 13 MB | Spatial join → grid tree stats |
| **FungalRoot v2.0** | Zenodo (10.5281/zenodo.xxx) | CSV | 2023 | ~1 MB | Species → AM/EM/NM lookup |
| **GBIF fungi** | Global Biodiversity Information Facility | JSON | 2024 | 3–9 MB | Fungal occurrence count per cell |
| **Sentinel-2 NDVI** | Planetary Computer (no login) | GeoTIFF | 2023–2024 | Tiled | Zonal stat → mean_ndvi per cell |
| **Landsat LST** | Planetary Computer (no login) | GeoTIFF | 2023–2024 | Tiled | Zonal stat → lst_anomaly per cell |
| **Urban Atlas** | Copernicus (free registration) | GeoTIFF | 2018 | ~200 MB | Zonal stat → sealed % per cell |
| **BCN boundary + districts** | IDESCAT / Ajuntament | GeoJSON | ~2020 | 1 MB | Grid clipping + district labeling |

---

## outputs/ Subtree (Final Artifacts)

```
outputs/
├── phase-4/                          # Phase 4 modeling outputs (Core B complete, Core A pending)
│   ├── metrics.csv                  # R², MAE, RMSE for each estimator × split (train/eval/test)
│   ├── per_district.csv             # Residuals by district (test set)
│   ├── predictions.parquet          # cell_id, split, y_true, y_pred* for all estimators
│   └── model_artifact.joblib        # Fitted sklearn Pipeline (SimpleImputer + LinearRegression)
│
├── figures/                          # Supporting plots + diagrams
│   └── [PNG/SVG]                    # EDA plots, architecture sketches, etc.
│
├── maps/                             # Raster map exports
│   └── [PNG/GeoTIFF]                # Static priority map rasters (for presentation)
│
├── reports/                          # Analysis reports
│   └── [Markdown/PDF]               # Data quality, limitations, interpretation
│
├── [Top-level exports]               # Main deliverables
│   ├── priority_map.html            # Interactive Folium map (top-15 cells, Scenario B)
│   ├── priority_zones.csv           # Ranked cells for analyst export (rank, district, score)
│   ├── priority_zones.html          # Ranked cells as interactive table
│   ├── grid_trees.geojson           # 400m grid + tree counts + species richness (QA)
│   ├── grid_trees_map.png           # PNG preview of grid_trees geometry
│   ├── network_nodes.geojson        # Mycorrhizal network nodes (fungi + trees)
│   ├── network_edges.geojson        # Network edges (fungal→tree links)
│   ├── network_islands.geojson      # Connected components (fungal islands)
│   ├── sensitivity_comparison.png   # Heatmap: 24 scoring scenarios vs baseline
│   ├── limitations.md               # Phase 3 limitations (AM-blindness, snapshot, MAUP)
│   ├── model-card-v1.md             # Mitchell template; leakage check; ≥3 NOTs
│   ├── pipeline-results-interpretation.md  # Narrative interpretation
│   └── [Session 3 presentation + analysis Python]  # Presentation, analysis scripts
```

---

## Naming Conventions

### Notebooks
```
NN-name.ipynb           where NN ∈ {01, 02, 03, 04, 05}
Example: 01-data-profiling.ipynb, 02-grid-trees.ipynb
```

### Data Files
```
kebab-case.{csv,parquet,geojson}
Example: scored-grid.parquet, arbrat-viari.csv, bcn-boundary.geojson
```

### Phase Directories
```
phase-N/                where N ∈ {1, 2, 3, 4}
Contents:
  - decision documents (decision-statement.md, analytical-question.md)
  - design documents (test-design.md, data-contract.yaml)
  - architectural decision records (adrs/)
  - exit checklists (exit-audit.md, exit-checklist.md)
  - session-specific artifacts (data-cleaning-report.md, modeling-guidelines.md)
```

### ADR (Architectural Decision Records)
```
phase-N/adrs/NNNN-slug.md
Example: phase-3/adrs/0001-platanus-only.md, phase-4/adrs/0003-spatial-cluster-split.md
Format: Title, Status, Context, Decision, Consequences, References
```

### Script Files
```
camel_case.py           (Python modules in src/)
kebab-case.py           (Standalone scripts in scripts/)
Example: src/clean_data.py, scripts/download_all.py
```

### Output Artifacts
```
artifact_name.{format}
Examples:
  - priority_map.html
  - scored_grid.geojson
  - model_artifact.joblib
  - metrics.csv
```

---

## Key Relationships (Data Flow)

```
[Tree inventory CSVs]
       ↓ (01-data-profiling.ipynb)
[Profile summary + anomaly audit]
       ↓
[02-data-cleaning.ipynb + src/clean_data.py]
       ↓ (joins FungalRoot, GBIF, zonal stats)
[scored_grid.parquet] ← source of truth for phases 3–4
       ↓
[03-scoring.ipynb + src/clean_data.py]
       ↓ (computes composites A/B/C, top-15 flag, intervention type)
[scored_grid + all scoring columns]
       ↓
[src/split_data.py]
       ↓ (k-means spatial clustering, deterministic split assignment)
[train.parquet, eval.parquet, test.parquet, cluster_assignments.parquet]
       ↓
[src/train_model.py]
       ↓ (fits LinearRegression + 3 baselines, writes metrics + artifact)
[model_artifact.joblib, metrics.csv, predictions.parquet, per_district.csv]
       ↓
[04-connectivity.ipynb, 05-visualisation.ipynb]
       ↓ (generates network topology, priority maps)
[network_{nodes,edges,islands}.geojson, priority_map.html, priority_zones.csv]
```

---

## Summary Callouts

- **Single source of truth:** `data/processed/scored_grid.parquet` (442 cells, all 80+ features + scores)
- **Frozen test set:** `data/splits/test.parquet` (cluster 4, k=5 split, seed=42)
- **No code in data/:** data/ is for data only; all logic lives in src/ and notebooks/
- **Phase structure:** each phase-N/ has decisions, designs, ADRs, and an exit audit — read the exit docs to understand what was locked
- **Outputs are for presentation:** tables/CSVs for analysts, maps for decision-makers, metrics for validation, not for re-ingestion
