# Pivot Product — Modeling (CRISP-DM Phase 4)

**Date:** 2026-06-05 (formalized from `src/allergen_priority.py` + `src/equity_layer.py`)
**Technique family:** **composite indicator** (OECD/JRC 2008), NOT a learned model. The analytical core of this pipeline is a transparent product of standardized layers — judged on interpretability, robustness, and defensibility, not held-out accuracy.

## Why a composite indicator, not ML

The decision is a **ranking** over cells from variables we trust and can inspect, with no labelled outcome to learn from (and, deliberately, no measured-pollen target — see Phase 2). The crispdm-4 decision tree routes "rank cells by a transparent multi-criteria objective" to a composite indicator, not a regression. Phase-4 success is *does the indicator change the planner's decision in a way that survives sensitivity*, not R².

## The model

```
priority_v1 (efficiency) = source_std × exposure_std
priority_v3 (equity)     = source_std × exposure_std × deprivation_std
feasibility              = 1 − sealed        (annotated, never multiplied in)
```

- **Aggregation = product (conjunctive AND), not weighted sum.** This is the explicit fix for the Cycle-A failure. A weighted sum lets one high-variance component dominate the ranking while its declared weight hides that fact (sealed surface drove `composite_score_B` at effective weight ≈ 1). A product demands a cell score on **both** levers: a 485-plane cell with few residents and a high-pollen-but-empty cell both fall, by construction. There are no hidden weights to mis-set — each layer enters once, standardized to [0,1].
- **No opaque composite, no learned parameters.** Every term is one of the Phase-3 contract columns; the output is fully reproducible from the layers.

## Baselines the ranking must beat (defined before evaluation)

1. **DENSITY-ONLY** — sequence by `plane_density` (the city's implicit "replace where planes are densest" rule). This is the bar that matters: the product only earns its complexity if accounting for *people* beats it.
2. **RANDOM** — mean over 200 seed-42 draws of k cells. The floor.

## The anti-tautology commitment

Cycle A validated an index against its own ingredients. Phase 4 here pre-commits (in `phase-6/allergen-validation-design.md`, written before any result) to test the indicator against an **external** question whose answer was unknown: *does adding exposure materially re-order priorities versus the naive density rule, or are the most-planted cells already the most-exposed (making exposure redundant)?* If exposure barely re-orders, that is an honest finding (the naive rule is near-optimal) — not something to paper over.

## Determinism & reproducibility

- Seed 42; the only randomness is the RANDOM baseline. All standardization is min-max over the fixed cell set.
- Run: `python src/allergen_priority.py` (writes priority, runs T1–T4, emits the planner table). Equity variant: `python src/equity_layer.py`.

## What Phase 4 hands to Phase 5

`priority` and `priority_std` columns on `allergen_layers.parquet`, a top-30 planner table (`outputs/phase-6/priority_zones.csv`), and the pre-registered tests T1 (re-ordering), T2 (redundancy), T3 (burden-capture vs baselines), T4 (sensitivity) ready to run — plus the v3 equity tradeoff (V3-1 decorrelation, V3-2 reorder, V3-3 tradeoff). Modeling makes no claim of validity on its own; the verdict is Phase 5's to render.
