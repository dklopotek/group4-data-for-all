# Phase 6 — Pre-registered Evaluation: Platanus Allergen-Exposure Priority

**Date written:** 2026-06-04 (BEFORE computing the priority or any result)
**Anchors:** `docs/plans/2026-06-04-platanus-allergen-priority-design.md`; the team's binding pre-registration discipline (design + method committed before results).

---

## 0. External pollen validation — declared INFEASIBLE (cancellation clause invoked)

The design (Sec 4) pre-committed to validate the SOURCE layer against measured aerobiology Platanus-pollen data, with a fallback if such data was unavailable. **It is unavailable.** A best-effort acquisition (Open Data BCN + XAC/PIA + UAB aerobiology + EAN) found **no openly downloadable, machine-readable, station-level Platanus pollen time-series with coordinates**: the Catalan network publishes only a current 0–4 forecast level per station, and EAN is access-controlled (`data/raw/SOURCES.md`).

**Consequence (honest downgrade, per the design's cancellation criterion):** the SOURCE layer is NOT validated against measured pollen. It is a **literature-anchored plane-pollen emission proxy**, defensible on three established facts but explicitly un-validated spatially:
- *Platanus* is the single largest contributor to Barcelona's airborne pollen — ~46% of the annual pollen index, season mid-March–April (Gabarra, Belmonte & Canela, 2002, *Aerobiologia*, https://doi.org/10.1023/A:1021370724043).
- Per-inflorescence emission is ~3–10 × 10⁶ grains; clinical symptom threshold ~50 grains/m³ (Maya-Manzano et al., 2017, *Urban Forestry & Urban Greening*, https://doi.org/10.1016/j.ufug.2017.09.009).
- Emission scales with the number and maturity of plane trees — the inventory quantities we hold directly.

We do **not** invent validation. This limitation is carried into the model card exactly as the fungal-thesis limitation was.

## 1. The question we CAN test (answer unknown before running)

Given that external validation is off the table, the substantive, non-tautological question is:

> **Does accounting for residential population (exposure) materially re-order replacement priorities versus the city's implicit "replace where plane density is highest" rule — or are the most-planted cells already the most-exposed, making exposure redundant?**

This is the same class of question the fungal test asked (does a second layer add anything), and its answer is genuinely unknown. If exposure barely re-orders, that is an honest finding (the naive rule is near-optimal); if it re-orders substantially, the two-layer product earns its complexity.

## 2. Layers (transparent, no opaque composite)

- SOURCE `source_std` = min-max of (plane_count × maturity). (`src/allergen_source.py`)
- EXPOSURE `exposure_std` = min-max of areal-interpolated residential population. (`src/exposure_layer.py`)
- FEASIBILITY `feasibility` = 1 − sealed (annotation/gate, not a score).
- **PRIORITY** `priority = source_std × exposure_std` (product of two transparent layers).

## 3. Pre-registered tests and criteria (fixed before running)

**T1 — Does exposure re-order vs the naive density rule?**
Compare PRIORITY ranking to a SOURCE-only (density×maturity) ranking.
- Report Spearman rank correlation and Jaccard overlap of the top-15 and top-50 cells.
- **Pre-registered call:** exposure MATERIALLY re-orders iff top-15 Jaccard < 0.70 AND Spearman < 0.90. If both exceed those, exposure is largely redundant with density (honest limitation, reported as such).

**T2 — Redundancy diagnostic (not one layer in a costume).**
Report corr(priority, source_std), corr(priority, exposure_std), corr(source_std, exposure_std). Both layers must correlate materially (|r| ≥ 0.3) with priority, and the two input layers must not be near-identical (|corr(source,exposure)| < 0.8). If priority collapses onto a single layer, say so — this is the exact failure mode we are guarding against.

**T3 — Burden-capture vs baselines (with an honesty caveat).**
Define total allergen-exposure burden = Σ over cells of (source_std × exposure_std). For top-k cells (k = 15, 50) under three strategies — PRIORITY, DENSITY-ONLY, RANDOM (seed 42, 200 draws, report mean) — report the share of total burden captured.
- Caveat stated up front: burden is the priority's own objective, so PRIORITY leading is partly by construction. The reportable, non-trivial quantity is the **margin over density-only** — how much extra burden the city captures by accounting for people. RANDOM is the floor.

**T4 — Sensitivity (verdict must survive).**
Re-run T1's re-ordering verdict under: (a) uniform maturity (priority = density×exposure), (b) rank-normalized instead of min-max layers, (c) geometric mean instead of product. The T1 verdict (material re-ordering: yes/no) must hold across these.

## 4. Reporting contract

Write `outputs/phase-6/allergen_priority_results.md` + `.json` with: layer summaries, T1–T4 results, the burden-capture margin over density-only, and a one-line verdict on whether exposure earns its place. A planner-readable priority table (`outputs/phase-6/priority_zones.csv`, top cells with district, planes, population, priority, feasibility). Negative/limiting results retained. No measured-pollen claim anywhere.

---

## Results

_(pending — `src/allergen_priority.py`)_
