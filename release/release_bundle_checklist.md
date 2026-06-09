# Release Bundle Checklist — v1.0.0 — 2026-06-09

ENVIRONMENT
- [x] requirements-lock.txt present (pinned exact versions)
- [~] Dockerfile — specified in publication_plan; not built on this Windows host (honest: untested)
- [x] Python interpreter pinned (3.11.15, documented in manifest + how_to_rerun)

CODE
- [x] Pipeline scripts run top-to-bottom deterministically (seed 42)
- [x] section_priority.py / street_actions.py have docstrings + __main__ guard
- [x] CITATION.cff at repo root
- [x] LICENSE (code) present at repo root  [verify: MIT]
- [x] README points to the final report + the deployment map

DATA
- [x] manifest.json lists every input with snapshot + SHA-256 + licence
- [x] manifest.json lists every output with version + SHA-256
- [x] Datasheet for the section product (outputs/phase-6/datasheet_section_priority.md)
- [x] CRS explicitly stated (EPSG:25831 internal, 4326 web)
- [x] Field-level data dictionary (in the datasheet)

DOCUMENTATION
- [x] Final report (outputs/reports/crispdm-phase-1-to-6-paper.md)
- [x] intended_use.md (who, what decisions, what NOT)
- [x] limitations.md
- [x] how_to_rerun.md (one page)
- [x] how_to_extend.md
- [x] decision_log.md
- [x] retrospective.md

FAIR
- [x] fair_checklist.md complete; no fail; 4 partials all DOI-dependent

PUBLICATION
- [x] publication_plan.md identifies all channels
- [~] Zenodo DOI (code) — PENDING (needs team account)
- [~] Zenodo DOI (data) — PENDING
- [~] DOIs recorded in report/CITATION — PENDING the mint

MAINTENANCE
- [x] monitoring_plan.md names maintainer (Group 4 / R. El Khoury; then unmaintained-fork-freely)
- [x] re-run cadence set (annual / on-trigger)
- [x] deprecation policy set

QUALITY GATES
- [x] Reproducibility: section_priority prints C1 PASSED; numbers match the report
- [x] Honesty gate: street file carries no priority/score column (grep-verified)
- [~] Stranger test / citability / maintainability: not externally run (seminar)

NEGATIVE CHECKS (should be FALSE / none shipped)
- [x] No maintained frontend/hosted service (the map is a one-off local aid; flagged)
- [x] No live model-serving endpoint
- [x] No "TBD" maintainer (explicit unmaintained-after-seminar statement)
- [x] No notebook with out-of-order cells (canonical code is src/*.py)

SIGN-OFF
Maintainer: Group 4 (Rafik El Khoury)
Date: 2026-06-09
Release tag: v1.0.0 (to be pushed)
