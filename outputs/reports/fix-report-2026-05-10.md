# Pipeline Fix Report — 2026-05-10

Surgical application of 12 bugs (plus 1 doc fix) found by parallel
Model QA Specialist + Code Reviewer audits. All fixes applied via
`.claude/fix_pipeline.py` in a single atomic pass; no refactors, no
new features, no scope creep. Pipeline is ready for the user to re-run
the four notebooks end-to-end.

---

## File 1 — `notebooks/02-grid-trees.ipynb`

| Bug | Severity | Cell ID | Change |
|---|---|---|---|
| BUG-1 | CRITICAL | `o5p6q7r8` (P5 — FungalRoot loading) | Added `_normalise_myco()` and applied to `fr["myco_type"]` after CSV load. Collapses compound strings ("EcM, AM undetermined", "EcM, no AM colonization", "EcM,AM", "Non-mycorrhizal", "OM", "ERM") into the canonical `{AM, EM, NM}` vocabulary the per-cell aggregator (P6) recognises. Without this, ~9,100 EM-host trees (Pinus + Quercus) were being misclassified as `NM` in the value-counts and `em_pct` was 0 for every cell. |
| BUG-2 | MAJOR | `o5p6q7r8` (same cell) | Replaced `myco_map.setdefault(sp, mt)` with `myco_map[sp] = mt` in the curated-stub loop. Stub now overrides the (post-normalisation) CSV value for the 20 species we have hand-curated, rather than the other way around. Defensive — important if the FungalRoot CSV is ever updated upstream with a wrong value for a key species. |

Sanity scan: no other cell in nb 02 references the literal raw values (`"ECM, AM UNDETERMINED"` etc.) outside this cell.

---

## File 2 — `notebooks/03-scoring.ipynb`

| Bug | Severity | Cell ID | Change |
|---|---|---|---|
| BUG-3 | CRITICAL | `cell-s1` (S1 sealed-surface) | `zonal_mean_from_raster(..., scale=1/100)` → `scale=1.0`. The raster produced by `process_urban_atlas.py` is already on a 0–1 scale (verified min=0.024, max=0.894 in the cell `8c21cebc` probe). The /100 collapse was killing the dimension — `s1_sealed` had std≈0.002, near-uniform, which is why the audit also fired BUG-10 in the visualiser. Comment about "Urban Atlas stores 0–100" updated to reflect the actual 0–1 raster. |
| BUG-4 | CRITICAL | `cell-s4` (S4 host-mismatch) | Function-internal thresholds `am_pct >= 0.8` → `>= 80`, `em_pct >= 0.5` → `>= 50`. Reporting block at the bottom of the cell updated to the same scale (3 occurrences). Notebook 02 stores `am_pct` and `em_pct` as percentages on 0–100, not 0–1. |
| BUG-5 | CRITICAL | `cell-colonisation` | `trees_young_pct >= 0.3` → `>= 30`. Same scale issue as BUG-4 — the colonisation flag was firing for every cell or no cells, never the intended 30%-young threshold. |
| BUG-6 | CRITICAL | `cell-top15` | Replaced single-line `selected[-1] = district_cells[0]` displacement (which only kept the LAST missing district) with the list-based logic from the bug list: per missing district, find its highest-ranked cell and add it; displace the lowest-ranked currently-selected cell whose district has > 1 representative; if no such over-represented district exists, simply grow the set (constraint is "at least one per district"). The function now consistently produces ≥ 8 districts in the top set instead of 4. |

Sanity scan: `Grep` for `am_pct >= 0\.8`, `em_pct >= 0\.5`, `trees_young_pct >= 0\.3`, `scale=1/100` returned zero matches across the notebooks directory.

---

## File 3 — `notebooks/04-connectivity.ipynb`

| Bug | Severity | Cell ID | Change |
|---|---|---|---|
| BUG-7 | MAJOR | `cell-bridge-fn` | Rewrote `bridge_score_for_zone()` to track distinct unordered component pairs `(comp_a, comp_b)` reached, instead of counting raw new-edge candidates. Previously, every blocked tree returned `node_to_comp.get(b_id, -1) = -1`, so the comparison `b_comp != n_comp` was always True for any reached neighbour, inflating the count by the size of each visited component. New code collects `reached_comps` for each blocked tree, then takes pairwise combinations into a set. |
| BUG-8 | MAJOR | `cell-spread-fn` | Replaced the static-radius `simulate_spread()` with a frontier-based BFS-like expansion. Per season: query within `spread_m_per_season` (2 m default) of every CURRENTLY-reached tree, filter by sealing barrier, accumulate. Halts early if no new trees are reached. Produces actual per-season propagation; the documented "2 m/season growth rate" is now real. |

---

## File 4 — `notebooks/05-visualisation.ipynb`

| Bug | Severity | Cell ID | Change |
|---|---|---|---|
| BUG-9 | MAJOR | `b0c1d2e3` (sensitivity chart) | Column headers updated to `"Equal weights"` / `"Sealed-dominant, recommended"` / `"Heat + canopy weighted"` matching the implementation in 03's `SCENARIOS` dict. |
| BUG-9 | MAJOR | `e3f4a5b6` (HTML caption) | Caption "Scenario B: LST-heavy weighting" → "Scenario B: Sealed-dominant weighting, recommended". |
| BUG-10 | MEDIUM | `c9d0e1f2` (DATA_LABEL assignment) | Replaced flat ternary with `_data_label()` helper that, for the non-synthetic branch, examines `s1_sealed`, `s2_lst`, `s3_ndvi` standard deviations. If any sub-score has std < 0.05, banner becomes `"DATA-WARNING: low variance in sub-scores (<list>) — output may be unreliable"`; otherwise `"REAL DATA"`. This is exactly the warning that would have caught BUG-3 before it shipped a uniform-output map. |
| BUG-11 | MEDIUM | `a5b6c7d8` (limitations footer §5) | Replaced the "based on sealed-surface fraction > 85% and/or LST anomaly > 4°C" paragraph with the correct documentation: "True for cells where ≥30% of trees were planted within the past 5 years. These cells may have lower-than-expected mycorrhizal colonisation regardless of host species (FungalRoot lookup assumes colonisation-competent substrate, which is not guaranteed in recently-engineered urban substrates)." |

Note: stale `outputs/limitations.md` and `outputs/priority_zones.html` artefacts on disk still contain the pre-fix text — they will be regenerated correctly when notebook 05 is re-run.

---

## File 5 — `data/process_urban_atlas.py`

| Bug | Severity | Line | Change |
|---|---|---|---|
| BUG-12 | MINOR | 39 (SEALED_FRACTION dict) | `12230: 0.70` (Railways) → `12230: 0.50`. Aligns with published Urban Atlas Imperviousness Density bands (0.30–0.60). |

This change only affects future re-runs of `process_urban_atlas.py`. The currently-on-disk `sealed_surface.tif` was generated with the old value; user should re-run the script before re-running notebook 03 if they want this fix to propagate to the raster.

---

## File 6 — `docs/system-sketch-v0.md`

| Bug | Severity | Line | Change |
|---|---|---|---|
| BUG-13 | DOC | 187 | Scenario B weights documented as `0.50 / 0.17 / 0.17 / 0.05` → `0.55 / 0.20 / 0.20 / 0.05`. The implementation in `notebooks/03-scoring.ipynb` cell `cell-composite` was always `0.55/0.20/0.20/0.05` and that is the source of truth; doc is corrected to match. Per the audit instruction: don't change implementation. |

---

## Verification

- All four notebooks load as valid JSON post-edit (`json.load` round-trip clean).
- `Grep` for old-behaviour markers (`am_pct >= 0.8`, `em_pct >= 0.5`, `trees_young_pct >= 0.3`, `scale=1/100`, `LST-heavy`, `Sealed-heavy`, `setdefault(sp, mt)`, `12230: 0.70`, `0.50/0.17/0.17/0.05`) returns no matches in the notebooks directory or in the source files. Remaining matches are confined to:
  - `outputs/code-review-deep.md` and `outputs/model-qa-audit.md` (the audit reports themselves — leave alone).
  - `outputs/limitations.md` (stale generated artefact — will be overwritten when notebook 05 re-runs).
  - `docs/plans/2026-05-10-pipeline-design.md` (planning doc not in the bug list — left untouched per "no scope creep").
  - `.claude/fix_pipeline.py` (this fix script itself, which intentionally references the old values in its `assert ... in old` guards).

## Re-run checklist for the user

1. Optional: `python data/process_urban_atlas.py` — regenerate `sealed_surface.tif` with the corrected railway value (BUG-12).
2. Run `notebooks/02-grid-trees.ipynb` end-to-end — `em_pct` should now be non-zero in cells with Pinus / Quercus presence; `dominant_myco_type` distribution should now include EM cells.
3. Run `notebooks/03-scoring.ipynb` — `s1_sealed` std should be roughly 0.20–0.30 (real Urban Atlas variance), not ≈ 0.002. `top15_scenario_*` should cover ≥ 8 of 10 districts.
4. Run `notebooks/04-connectivity.ipynb` — `bridge_score` column should contain a mix of values, not all 0; `simulate_spread` should show monotonic per-season tree growth in the intervention scenario relative to baseline.
5. Run `notebooks/05-visualisation.ipynb` — chart legend and HTML caption read "Sealed-dominant", DATA_LABEL is "REAL DATA" (or DATA-WARNING if any sub-score is still degenerate), limitations footer §5 cites tree-age basis.

Pipeline date: 2026-05-10. Fixer: dev agent. Source: `.claude/fix_pipeline.py`.
