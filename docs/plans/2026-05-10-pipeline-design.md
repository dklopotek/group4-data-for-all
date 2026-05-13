# Pipeline Design — Mycorrhizal Barcelona
**Date:** 2026-05-10
**Mode:** NEXUS-Micro
**Status:** Approved — ready for implementation

---

## What We're Building

Two-layer pipeline producing:
1. **Barrier composite scoring pipeline (Phase B)** — ranks Barcelona's 400m Superilla-scale grid cells by 4 sub-scores, outputs top-15 priority zones with intervention-type recommendations
2. **Mycorrhizal network connectivity model (Phase C)** — builds a tree-to-tree hyphal reach graph, identifies existing network islands and bridge interventions, simulates network spread from source patches

**Motto:** An ecosystem that supports mycelium health is an ecosystem that supports health of all beings.

---

## Architecture

### Format
- Jupyter notebooks for exploration (one per stage)
- `src/pipeline.py` for the clean, end-to-end runnable script

### Notebook stages
```
notebooks/
  01-data-profiling.ipynb       ✅ complete (real data)
  02-grid-trees.ipynb           → data/grid_trees.geojson
  03-scoring.ipynb              → data/scored_grid.geojson
  04-connectivity.ipynb         → data/network.geojson
  05-visualisation.ipynb        → outputs/priority_map.html
src/
  pipeline.py                   → end-to-end runner
```

### Intermediate data contracts
Each notebook writes a clean GeoJSON/CSV to `data/` that the next reads — stages are independently re-runnable.

---

## Data Stack

| Source | Role | Status | Location |
|---|---|---|---|
| Ajuntament tree inventory (street + park) | PRIMARY — host-species composition | Re-download via curl | data/ |
| FungalRoot v2.0 | JOIN TABLE — species → mycorrhizal type | Download from Zenodo | data/ |
| Copernicus Urban Atlas 2018/2021 | sub-score 1 — sealed surface | Manual download (Copernicus portal) | data/ |
| Landsat 8/9 thermal | sub-score 2 — LST heat anomaly | Google Earth Engine / USGS | data/ |
| Sentinel-2 L2A | sub-score 3 — NDVI canopy | Copernicus Data Space | data/ |
| GBIF fungal occurrences | sub-score 4 — confirmation gap context | GBIF API | data/ |
| OSM + BCN open data | spatial framework | Overpass API / BCN portal | data/ |

**Python environment:** Python 3.13. Install: `pip install geopandas networkx rasterio folium pandas numpy`

---

## Phase B: Scoring Pipeline (P1–P11)

**P1** — Build 400m grid over BCN municipal boundary (GeoPandas + OSM district frame)
**P2** — Spatial join tree inventory → grid cells
**P3** — FungalRoot join: species → mycorrhizal type (AM/EM/mixed/NM) per tree
**P4** — Compute expected mycorrhizal type per cell (modal type + composition fractions)
**P5** — GBIF proximity query: fungal records within 200m of each cell centroid
**P6** — Compute confirmation gap + AM-blindness flag per cell
**P7** — Zonal statistics: Urban Atlas sealed-surface % per cell
**P8** — Zonal statistics: Landsat LST anomaly vs city median per cell
**P9** — Zonal statistics: Sentinel-2 mean NDVI per cell
**P10** — Composite score: normalise sub-scores to [0,1], test 3 weight scenarios:
  - Scenario A: equal (0.25/0.25/0.25/0.25)
  - Scenario B: sealed-surface dominant (0.50/0.17/0.17/0.05 — host-mismatch downweighted per critical finding)
  - Scenario C: heat+canopy dominant (0.17/0.30/0.30/0.23)
**P11** — Intervention-type label per cell (highest sub-score → de-paving / cooling / planting / species-selection)
**P12** — Rank cells, take top-15 (with ≥1 zone per district constraint)
**P13** — Peri-urban reference patch barrier index (Collserola / Garraf ~1km²)

---

## Phase C: Connectivity Model (P14–P16)

**P14** — Build tree-to-tree graph (NetworkX):
  - Nodes = trees (with lat/lon, species, mycorrhizal type)
  - Edges = trees within hyphal reach (AM: 15m, EM: 35m) through connected soil
  - Edge removal: edges crossing >50% sealed surface (Urban Atlas) are cut
**P15** — Find connected components (existing mycorrhizal "islands")
**P16** — Bridge analysis: which single de-paving intervention connects the two largest currently-isolated islands?
**P17** — Spread simulation: starting from source patches (Collserola, Ciutadella, Montjuïc), propagate network growth at published AM growth rates (~2m/season), show network extent by 2030 under priority-zone intervention scenarios

---

## Output

**Priority map:** Interactive HTML map (Folium/Kepler) — 400m grid, top-15 zones colour-coded by intervention type, peri-urban reference patch inset
**Per-zone table:** Rank, district/barri, expected mycorrhizal type, 4 sub-scores (3 weight scenarios), barrier composite, intervention type, AM-blindness flag, colonisation-uncertainty flag
**Network map:** Connected island overlay, bridge intervention highlighted, 2030 spread projection
**Limitations sheet:** "What this map cannot claim" — embedded in map footer and as standalone MD

---

## Quality Gates (NEXUS-Micro)

- Dev↔QA loop on every notebook: build → test → PASS / FAIL (max 3 retries)
- Reality Checker approval required before any output is committed
- Evidence required: intermediate GeoJSON files with real record counts, not assertions
- Sensitivity test must be run before top-15 list is finalised (Jaccard similarity across 3 scenarios)

---

## Team

| Agent | Responsibility |
|---|---|
| Agents Orchestrator | Pipeline control, quality gates, handoffs |
| Data Engineer | Data download, CRS standardisation, data/ folder setup |
| Backend Architect | Grid construction, spatial joins, zonal statistics (P1-P9) |
| AI Engineer | Composite scoring, sensitivity test, NetworkX connectivity model (P10-P17) |
| Analytics Reporter | Visualisation, output design, limitations sheet |
| Reality Checker | Evidence-based approval at each quality gate |
