# Phase 2 Versioning Policy — Mycorrhizal Barcelona

This document defines how datasets are versioned, pinned, and updated throughout the "Mycorrhizal Barcelona" CRISP-DM pipeline.

## 1. Dataset Pinning

All datasets ingested into the pipeline are pinned by their source URL and a retrieval timestamp. If a source file is provided locally (e.g., LandSat/Sentinel-2 TIFs), it is pinned by its file modification time and path.

| Dataset | Version/Pin | Source |
| :--- | :--- | :--- |
| **Ajuntament Trees** | 2024-11-20 | Open Data BCN (GeoJSON) |
| **GBIF Fungi** | 2024-11-20 | GBIF.org (JSON) |
| **FungalRoot** | v1.0 | Soudzilovskaia et al. 2020 (CSV) |
| **Urban Atlas** | 2018 (V02) | Copernicus Land Monitoring Service |
| **Sentinel-2** | Summer 2023 | Copernicus Open Access Hub |
| **LandSat 8** | Summer 2023 | USGS EarthExplorer |

## 2. Snapshot Location

Snapshots of ingested data are stored in the `data/` directory.
- Raw ingested files: `data/[source]/raw/` (or directly in `data/` if single file)
- Processed/Cleaned versions: `data/[source]/processed/`

## 3. Re-ingest Cadence

As this is a seminar project, data ingestion is performed **once** at the start of the project. No automatic re-ingest is planned. If significant updates occur at the source, manual re-ingestion will be triggered and documented in the `phase-2/ingestion-log.md`.

## 4. Breaking-Change Detection

Any change in source data schema (e.g., column rename, unit change) is detected during the **Phase 2 Schema Validation** step. 
- Schema scripts in `phase-2/schemas/` will fail if data does not match constraints.
- Any failure requires a revision of the schema script and potentially downstream Phase 3 transformation code.

## 5. Retirement Policy

- **Intermediate files**: Deleted after the relevant pipeline step is verified.
- **Final outputs**: Retained in `outputs/` for the duration of the seminar.
- **Archive**: The entire `data/` folder should be archived upon project completion.
