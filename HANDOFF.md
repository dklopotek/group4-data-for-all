# Handoff -- Session 3 Closed · PRPI v1.2 Shipped · Ready for Session 4

**Last updated:** 2026-05-26 by Claude Code session
**Branch:** main
**Status:** Session 3 deliverables complete. Pipeline is at v1.2 with deep-research-informed operational scenario.

## Goal (DONE)
Add a "Platanus Replacement Priority Index" (PRPI) stage to the mycorrhizal barrier pipeline. **Shipped in two iterations:**
- **v1.1** (initial): EM-optimistic scenario, 5-term composite, `replacement_priority` strict gate, `s4_shift_ceiling_reached` honesty flag. 47 columns, 495 cells.
- **v1.2** (after deep-research pivot): refreshed `arbrat-viari` 2026_1T snapshot, peer-reviewed VPA allergenicity (Cariñanos & Marinangeli 2021), operational scenario `prpi_operational` anchored to Barcelona's Espais Verds Zelkova/Pistacia pilot palette, re-scoped public-health docstrings (Osborne et al. 2017 null asthma result; Scala et al. 2017 Pla a 3 food-allergy framing), `s4_shift_potential` reframed as upper-bound hypothesis. **51 columns, 494 cells.**

## Current state

**Pipeline works end-to-end.** `src/clean_data.py` runs in 6.9s, produces 495 cells, 40 columns, deterministic output. Both `scored_grid.geojson` (0.9 MB) and `scored_grid.parquet` (0.2 MB) verified.

**All 9 Session 3 course deliverables built**, plus Phase 1-4 documentation. NONE committed yet. Everything is uncommitted in working tree.

**Key Platanus findings from this session's research:**

*Public health:*
- 42,828 *Platanus × acerifolia* trees (22.6% of inventory, #1 species, all AM hosts)
- One tree = up to 143 billion pollen grains. Barcelona recorded 48,626 grains/m³ peak
- Sensitization rate: 5-59% of allergic population. Cross-reactivity with peach, apple, hazelnut, peanut, lettuce
- Peak pollination: March-May, coinciding with Sant Jordi (23 April) -- maximum outdoor exposure

*City policy:*
- Barcelona's Pla Director de l'Arbrat 2017-2037: reduce plane trees from 27% → <12% of street trees by 2037
- No single species may exceed 15% of total
- €9.4M/year budget. City replaces ~1,500 trees/year -- far below ~8,000/year pace needed
- Trialled replacement species: *Zelkova serrata*, *Pistacia chinensis* (mycorrhizal type: unknown, likely both AM)
- Native replacements on the table: *Quercus ilex* (EM), *Pinus halepensis* (EM)

*Disease:*
- Massaria disease (*Splanchnonema platani*) causes branch dieback, requiring aggressive pruning
- Monoculture risk: a single pathogen could devastate 27% of the canopy overnight
- Climate models show Platanus vulnerable to Barcelona's projected +2°C warming

*Pipeline integration opportunity:*
- 95.2% of cells classified "de-paving" -- Platanus replacement creates a second intervention axis
- 85.5% of cells are AM-dominant (S4=0.5, null) -- replacing Platanus (AM) with EM species could shift borderline cells (81-89% AM) below the 80% threshold, making S4 actionable
- The pipeline already normalizes species names and has per-cell tree aggregation -- only missing per-species counting

## What changed this session

**Prior session work (compacted):**
1. Read all Session 3 course templates from `MaAI01 25-26 - T03S13_Data -- DOCUMENTS/Session 3/`
2. Orchestrated 6 parallel agents to build 9 course deliverables: `src/clean_data.py`, `notebooks/02-data-cleaning.ipynb`, `docs/data-cleaning-log.md`, `docs/pipeline-architecture-v1.md`, `requirements.txt`, datasheet §4 updates, `data/processed/scored_grid.parquet` + `.geojson`
3. Cross-artifact verification pass with 4 blockers fixed (non-deterministic timestamp, enum mismatch, cross-references, LABEL_MAP keys)
4. Pipeline execution fixed (Python wheel downgrade 3.13→3.11, GBIF utf-8 encoding, Unicode console)
5. Results interpreted in `outputs/pipeline-results-interpretation.md`

**This conversation turn (new):**
6. Deep-researched Platanus problem: pollen allergy burden, Massaria disease, 2037 Master Plan targets, replacement species ecology
7. Researched mycorrhizal angle: Platanus is AM, replacing with EM species could break the AM-blind S4 null zone
8. Designed PRPI formula: `w1 × platanus_pct + w2 × S3_inverted_ndvi + w3 × s4_shift_potential + w4 × (1 − S1_sealed)`
9. Identified `s4_shift_potential` as the novel metric -- pre/post AM% delta per cell assuming EM replanting
10. Critiqued concept with 4 honest problems (AM not second-class, AM-blindness ceiling, city pace gap, unknown replacement myco types)
11. **NO CODE WRITTEN for this layer -- design only.**

## Files in flight

- `src/clean_data.py` -- 14-stage pipeline. `TOP20_MYCO` dict at line 141: `"Platanus × acerifolia": "AM"`. `normalize_species_names()` at ~line 284 lowercases species names. `compute_cell_tree_stats()` aggregates by myco_type, NOT by individual species. Needs: per-species counting, `compute_platanus_replacement_priority()` function, pipe chain insertion.
- `notebooks/02-data-cleaning.ipynb` -- 24 cells. No Platanus-specific analysis yet.
- `docs/data-cleaning-log.md` -- 305 lines, 14 transforms. No Platanus transform yet.
- `docs/pipeline-architecture-v1.md` -- 495 lines, 16 component specs. Needs PRPI component entry.
- `phase-3/data-contract.yaml` -- 311 lines. scored_grid schema has 40 columns. Needs `platanus_pct` and `prpi` entries.
- `phase-3/data-cleaning-report.md` -- 224 lines. No Platanus-specific issue yet.
- `outputs/pipeline-results-interpretation.md` -- 150 lines. Needs Platanus replacement zone recommendations.
- `notebooks/02-grid-trees.ipynb` -- per-cell tree stats. Currently aggregates by myco_type only.
- `data/raw/arbrat-viari.csv` + `arbrat-zona.csv` -- 189,090 tree rows. `cat_nom_cientific` column has species names. Platanus rows identifiable by `normalize_species_names()` matching `"platanus × acerifolia"`.

## What we tried that didn't work

Carried forward from prior session:
- **PDF rendering:** pdftoppm not available on Windows. Workaround: read markdown templates.
- **Python 3.13 venv:** C extensions for cp311, not cp313. Fixed: downgrade all packages to Python 3.11 wheels.
- **`pd.Timestamp.now()`:** Non-deterministic young-tree cutoff. Fixed: `REFERENCE_DATE = pd.Timestamp("2026-05-26")`.
- **`intervention_type` enum:** `"species-selection"` vs `"multi-strategy"`. Fixed: aligned to `"multi-strategy"`.
- **LABEL_MAP keys:** `s2_lst_anomaly` vs `s2_lst`. Fixed: aligned keys.
- **GBIF cp1252:** non-cp1252 characters. Fixed: `encoding='utf-8'`.

No new failures this turn (no code ran).

## Open questions / decisions pending

1. **Replacement myco type assumption.** If all replacement species are AM, `s4_shift_potential = 0` everywhere -- the layer is ecologically meaningless. Need user decision: assume EM replacement (optimistic, produces differentiated map), assume AM (conservative, produces flat map), or make it a user-configurable parameter? The research shows the city's current trial species (*Zelkova*, *Pistacia*) are likely AM, but native EM options (*Quercus ilex*, *Pinus halepensis*) are already in the approved palette.
2. **PRPI weight scenario.** Standalone parallel index with its own 4-weight scheme, or folded as a 5th sub-score into the existing composite? ADR-003 (weight scenario B) currently distributes 1.0 across 4 sub-scores. Adding a 5th requires a new weight scenario or a parallel index.
3. **Intervention classification.** Add `"species-replacement"` as a 5th enum value in `intervention_type`, or create a separate `replacement_priority` flag column? The data contract defines `intervention_type` as enum[de-paving, planting, cooling, multi-strategy]. New value requires contract update.
4. **Per-species data granularity.** Currently only `species_list` (JSON array) and `species_richness` (int count). Adding `n_platanus` opens the door to top-N per-species counts. Do we add just Platanus, or the top 5 species? The latter is 5 more columns but enables richer analysis.
5. **City plan alignment risk.** Referencing the 2037 Master Plan dates the output. If the plan changes (election, budget cut), the PRPI's policy grounding weakens. Trade-off: policy alignment makes output immediately useful to Barcelona Regional, but adds shelf-life risk.
6. **AM-blindness ceiling.** Even after removing ALL Platanus, cells at >90% AM remain AM-dominant. `s4_shift_potential` only matters for borderline cells (81-89% AM). For cells at 95%+, the replacement is ecologically neutral belowground. Should we flag this ceiling explicitly in the output (`s4_shift_ceiling_reached` boolean)?

## Next steps

1. **Add `n_platanus` counting to `compute_cell_tree_stats()`** in `src/clean_data.py`. Match normalized species name `"platanus × acerifolia"` against the species column post-normalization. Add `n_platanus` to the cell_stats dataframe before aggregation. ~5 lines.
2. **Implement `compute_platanus_replacement_priority()` function.** Full function with: docstring, Args/Returns, type hints, `out = df.copy()`, at least 1 assertion. Compute: `platanus_pct = n_platanus / total_trees * 100`, `s4_shift_potential` (pre/post AM% delta assuming Platanus removed and replanted with EM), PRPI = weighted sum. ~35 lines.
3. **Add to `.pipe()` chain** in the main composition function (currently `clean_temperature_dataset()` -- rename to `clean_mycorrhizal_dataset()`). Insert after `add_temperature_anomaly()` and before `df[FINAL_COLUMNS]`. ~3 lines.
4. **Add `"species-replacement"` intervention type.** Update `classify_intervention()` to check: if PRPI > 0.5 AND `s4_shift_potential > 0` AND `S1_sealed < 0.7` (feasibility gate), set to `"species-replacement"`. Update `data-contract.yaml` enum. ~10 lines.
5. **Add PRPI constants** to the top of `src/clean_data.py`: `PRPI_WEIGHTS` dict, `PRPI_THRESHOLD`, `S4_SHIFT_ASSUMPTION` (default `"EM"`). ~5 lines.
6. **Re-run pipeline:** `python src/clean_data.py`. Verify output has `platanus_pct` and `prpi` columns, no nulls in PRPI, `n_platanus` sum matches inventory (42,828).
7. **Add visualization** to `notebooks/05-visualisation.ipynb`: PRPI choropleth map, top-15 replacement priority cells, S4 shift potential histogram.
8. **Update documentation:** `docs/data-cleaning-log.md` (Transform 15 entry), `docs/pipeline-architecture-v1.md` (new component + Mermaid node), `phase-3/data-contract.yaml` (2 new columns), `outputs/pipeline-results-interpretation.md` (Platanus section).
9. **Commit.** All current uncommitted work + this new layer.

## How to resume
Paste into the new Claude Code session:
> Read `HANDOFF.md` at the project root and continue from "Next steps" item 1. Do not re-explore territory listed under "What we tried that didn't work" unless the listed condition is met.

---

## SESSION 3 CLOSE-OUT (2026-05-26)

**All Session 3 deliverables shipped. Pipeline runs at v1.2 in 5.2s, deterministic, 494 cells × 51 cols.**

**Session 3 deliverables in tree:**
- `src/clean_data.py` — 17-stage pipeline, v1.2
- `notebooks/02-data-cleaning.ipynb` — 24 cells (still v1.0-aligned; cosmetic refresh out of scope)
- `docs/data-cleaning-log.md` — 16 transforms (added T15 PRPI, T16 v1.2 pivot)
- `docs/pipeline-architecture-v1.md` — 17-component spec with PRPI mermaid node
- `phase-3/data-contract.yaml` — schema v1.2.0
- `requirements.txt` — Python 3.11 wheels
- `data/processed/scored_grid.geojson` + `.parquet` (1.1 MB + 0.2 MB)
- `outputs/pipeline-results-interpretation.md` — §1-§10 (§9 Platanus layer, §10 v1.2 pivot)
- `outputs/deep-research-platanus-prpi.md` — 5,800-word APA 7 report, 30+ refs, 5 critical contradictions surfaced
- `data/raw/vpa-mediterranean-species.csv` — 40-species peer-reviewed allergenicity table

**Inputs refreshed:**
- `data/arbrat-viari.csv` — 2026_1T Open Data BCN snapshot (188,991 trees, 42,815 Platanus)
- `data/arbrat-viari-prev-snapshot.csv` — preserved for rollback / diff

**Pipeline run on 2026-05-26:**
- 494 cells × 51 cols, all 17 stages, ~5.2s
- 42,815 Platanus matched (vs 42,828 inventory baseline — 13 lost to spatial-join boundary edge)
- `prpi` (EM-optimistic) range [0.151, 0.832]
- `prpi_operational` (Zelkova/Pistacia pilot) range [0.151, 0.728]
- 17 cells disagree between scenarios at `prpi > 0.5` action threshold
- 164 cells hit AM-blindness ceiling
- All invariants pass

**Next (Session 4):** Move to CRISP-DM Phase 4 (Modeling). Per `MaAI01 25-26 - T03S13_Data -- DOCUMENTS/Session 4/Lecture_4.md`: data splitting strategy (spatial/clustered recommended for 400m grid), baselining (dumb mean + domain heuristics + spatial nearest), model assessment, and model card with explicit "what it is NOT for" boundaries. The scored_grid.parquet is the modeling-ready input. Recommend Scenario B as the primary target column; both `prpi` and `prpi_operational` available as sensitivity scenarios.
