# Publication Plan

What gets published where. DOI items are **pending** — they require the team's institutional/GitHub
accounts and are not fakeable here; the steps are specified so the team can execute in minutes.

| Artifact | Channel | Status |
|---|---|---|
| Code (pipeline + scripts) | Zenodo DOI via GitHub release integration | PENDING — enable Zenodo–GitHub, tag `v1.0.0`, mint |
| Data product (`section_priority.*`, `street_removal_actions.csv`) | Zenodo data upload | PENDING — upload bundle, mint data DOI |
| Final report | In-repo `outputs/reports/crispdm-phase-1-to-6-paper.md`; render PDF via Pandoc | Available in repo; PDF on demand |
| Source code | Public GitHub repo | Available |
| (Optional) source-code archival | Software Heritage | Optional |

## Steps to mint (when ready)
1. Repo → GitHub → enable Zenodo integration for the repo.
2. `git tag v1.0.0 && git push --tags` → create a GitHub Release → Zenodo auto-mints the **code DOI**.
3. Upload the data bundle (the five `outputs/phase-6/*` products + datasheet) to Zenodo → **data DOI**.
4. Write both DOIs into `release/manifest.json`, `CITATION.cff`, and the paper's Declarations.

## Licences (separate by artifact type)
- **Code:** MIT (`LICENSE`).
- **Data:** CC-BY-4.0 (`LICENSE-DATA`) — matches the Open Data BCN upstream licence.
- **Docs/report:** CC-BY-4.0 (`LICENSE-DOCS`).

No consumer-facing portal or hosted UI is published (course constraint). The `deployment_map.html` is a
local presentation aid, not a deployed service.
