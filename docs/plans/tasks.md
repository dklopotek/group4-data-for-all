# Mycorrhizal Barcelona — Open Tasks

Generated 2026-05-10 after NEXUS-Micro pipeline build.
Status: [ ] = open, [x] = resolved, [~] = deferred

---

## A. Environment & Data Setup

- [x] T01: Install Python packages (`pip install -r requirements.txt`) — RAFIK
- [x] T02: Run `data/download_data.py` — tree CSVs, GBIF records, BCN boundaries — RAFIK
- [x] T03: Verify 2 URLs marked `# VERIFY` in download_data.py — RAFIK
- [x] T04: Download Urban Atlas 2018 manually (Copernicus portal, free registration) — RAFIK
- [x] T05: Download Sentinel-2 NDVI summer composite for BCN tile T31TDF — RAFIK
- [x] T06: Download Landsat 8/9 LST summer composite for BCN (path/row 197/031) — RAFIK

## B. Pipeline Execution

- [x] T07: Run notebooks 02→03→04→05 in sequence, verify intermediate GeoJSON outputs exist — RAFIK
- [x] T08: Check Jaccard sensitivity output — if any pair < 0.5, flag for team discussion — RAFIK

## C. Open Seams (from system-sketch-v0.md)

- [x] T09: Budget-line crosswalk — RAFIK uses firecrawl to scrape Ajuntament Eixos Verds + Superilla pages → docs/plans/budget-lines.md
- [x] T10: Reference patch — REFRAMED: use lowest-barrier within-city cells (Ciutadella, Montjuïc, Laberint) as reference baseline instead of peri-urban. Update sub-Q7 in docs accordingly.
- [ ] T11: GlobalAMFungi portal check — manually verify Iberian sample density at globalamfungi.com

## D. Documentation Fixes (from research findings 2026-05-10)

- [ ] T12: Add irrigation confound caveat to docs/data-quality-audit.md (cite Jumpponen & Egerton-Warburton 2010, Mycorrhiza)
- [ ] T13: Add FungalRoot engineered-substrate limitation to docs/datasheets/ajuntament-trees.md Section 8
- [ ] T14: Add "highest barrier ≠ fastest recovery" bullet to docs/output-sketch-v0.md "What this output is NOT"
- [ ] T15: Add irrigation confound caveat to docs/system-sketch-v0.md P7 description
- [ ] T16: Update docs/system-sketch-v0.md P9 to name the 3 weight scenarios (equal / sealed-dominant / heat+canopy)

## E. Final Output

- [ ] T17: Add team member names to datasheet sign-offs (ajuntament-trees.md + gbif-fungi.md + data-quality-audit.md)
- [ ] T18: Verify outputs/priority_map.html renders correctly in browser
- [ ] T19: Download full FungalRoot v2.0 CSV from Zenodo and place at data/fungalroot.csv

---

## Decisions

### T09 — Budget-line crosswalk — RESOLVED 2026-05-10
**Decision:** Rafik uses firecrawl scraping on Ajuntament Eixos Verds + Superilla programme pages to extract a 4-row budget-line table. Output saved to docs/plans/budget-lines.md.
**Reasoning:** Web scraping is faster and more reliable than reading planning PDFs manually. No language-specialist team member required.

### T10 — Reference patch — RESOLVED 2026-05-10
**Decision:** Replace peri-urban Collserola/Garraf patch with within-city lowest-barrier reference zones (5-10 cells with lowest composite score — Ciutadella interior, Montjuïc, Laberint d'Horta area).
**Reasoning:** Same data infrastructure, no schema crosswalk, more actionable for Ajuntament planners (within-city gradient is directly comparable). Sub-Q7 reframed: "what does the lowest-barrier end of the within-city distribution look like?"
**Deferred:** Full peri-urban comparison marked as stretch goal for future work.
