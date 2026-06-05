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

## v2 addendum — at-risk (allergy-prevalence) layer (pre-registered 2026-06-05, before build)

**Motivation:** replace the flat population EXPOSURE layer with an *at-risk* layer = population reweighted by allergic-rhinitis (AR) prevalence, so cells with more allergy-susceptible residents rank higher. Spatial variation comes from local AGE STRUCTURE (AR prevalence is strongly age-dependent), since no sub-city AR data exists (only city-wide; see below).

**Data:** `data/raw/2026_pad_mdbas_edat-q.csv` (population by 5-year age band per census section, Open Data BCN). No sex split used (kept as a v3 sensitivity). Empirical sub-city AR data does NOT exist; the finest open signal is the city-wide CatSalut antihistamine age×sex profile (`data/raw/catsalut_receptes_bcnciutat_respiratori.csv`), used only for city-wide curve calibration, not spatial join.

**AR prevalence weights by age (literature-anchored):** 0-4: 0.04; 5-9: 0.089 (GAN 6-7yr); 10-14: 0.146 (GAN 13-14yr); 15-44: 0.22 (Bauchau & Durham 2004 ~23% EU adult; ESCA); 45-64: 0.18; 65-69: 0.10; 70+: 0.05-0.08 (decline with age). Platanus-sensitized share 0.37 (Puiggros 2015, Barcelona) is a CONSTANT multiplier — affects scale/interpretation, not ranking. `at_risk_section = sum_band(pop_band x prev_band)`, areal-interpolated to cells.

**Tests (criteria fixed before running):**
- **V2-1 (does prevalence re-order vs plain population?):** Spearman(at_risk_cell, population_cell) and Jaccard of top-15 priority_v2 (source x at_risk) vs priority_v1 (source x population). Pre-registered call: prevalence MATERIALLY re-orders iff top-15 Jaccard < 0.70 AND Spearman(at_risk, population) < 0.95. If not, the honest conclusion is "age-weighting is redundant with population at this resolution — not worth adding; keep v1."
- **V2-2 (city-wide calibration, honesty check):** correlate the literature age-prevalence curve with the empirical antihistamine prescriptions-per-capita-by-age profile. Report the correlation and any divergence (prescriptions skew older than prevalence — chronic medication use; report, do not force agreement).

**Reporting:** `outputs/phase-6/atrisk_results.{md,json}`. Verdict reported either way. No measured-AR spatial claim.

## v3 addendum — equity (deprivation) weighting (pre-registered 2026-06-05, before build)

**Motivation:** age/sex weighting was redundant because they barely vary in space. Income/deprivation is one of Barcelona's most spatially variable features and is likely decorrelated from the plane-lined boulevards, so it CAN reorder. But equity weighting changes the OBJECTIVE — from "max exposure relieved" (efficiency) to "max exposure relieved among the worst-off" (equity). It is a value choice, so v1 is kept and v3 is presented alongside it, not as a replacement.

**Data:** `data/raw/atles_renda_bruta_persona.csv` (INE Atlas gross income per person, by census section, 2023; 1,068 sections). Key = `Codi_Districte.zfill(2) + Seccio_Censal.zfill(3)`. Missing-income sections imputed with city median (count reported). `deprivation_std = minmax(max_income - income)` per cell after areal-weighted interpolation (poorest cell = 1, richest = 0).

**Layers:** v1 efficiency `priority_v1 = source_std x exposure_std`; v3 equity `priority_v3 = source_std x exposure_std x deprivation_std` (aggressive). A floored variant `deprivation_w = 0.5 + 0.5*deprivation_std` is run as sensitivity.

**Honesty note fixed before running:** aggressive equity weighting multiplies by a high-variance, decorrelated factor, so reordering is EXPECTED and is not itself the finding. The reportable, decision-relevant quantities are the tradeoff and the decorrelation, below.

**Pre-registered tests / quantities (fixed before running):**
- **V3-1 (decorrelation — the precondition):** corr(deprivation_std, source_std) and corr(deprivation_std, exposure_std). For deprivation to add genuine new information it must be decorrelated from both (|r| < 0.7). If it is strongly correlated, it adds little (report honestly).
- **V3-2 (reorder, expected):** Spearman(priority_v3, priority_v1), Jaccard top-15/50. Reported, but framed as expected given V3-1.
- **V3-3 (equity-efficiency tradeoff — THE finding):**
  - *Efficiency cost:* total exposure burden = Σ(source_std x exposure_std). Report the share captured by the top-15/50 cells of the EQUITY ranking vs the EFFICIENCY ranking. The gap = exposure relief sacrificed for equity.
  - *Equity gain:* share of top-15/50 cells falling in the most-deprived income TERCILE under v1 vs v3. The increase = the equity the reweighting buys.
- **Sensitivity:** floored deprivation weight [0.5,1]; rank-based deprivation. The direction of the tradeoff must hold.

**Reporting:** `outputs/phase-6/equity_results.{md,json}` + an equity priority table `outputs/phase-6/priority_zones_equity.csv`. Both maps (efficiency + equity) reported; the planner chooses the objective. No claim that one is "correct".

## Results

**VERDICT: exposure earns its place (materially re-orders + non-redundant).** T1: Spearman 0.8909, top-15 Jaccard 0.3043 -> re-orders=True. T3 burden margin over density-only (top-15): 0.0464. Full: `outputs/phase-6/allergen_priority_results.md`.
