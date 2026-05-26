# ADR-005: Spread Simulation — Deprecated, Replaced by Static Buffer

**Status:** ACCEPTED
**Date:** 2026-05-26
**Deciders:** Rafik, Claude (Phase 3 connectivity audit)

## Context

Notebook 04 (`04-connectivity.ipynb`) originally contained a `simulate_spread()` function intended to model fungal network expansion over multiple seasons via BFS propagation. The function was:

1. **BUG-8 (original):** Implemented as a static 500m buffer, not propagation — ignored graph structure entirely.
2. **BUG-8 (fix):** Rewritten as frontier-based BFS with `spread_m_per_season` parameter, 5-season simulation.
3. **After fix:** 180 source trees reachable, zero growth over 5 seasons — the function never produced a non-trivial result.
4. **Design flaw discovered:** The function accepted a NetworkX graph `G` but built its own KDTree from `trees_gdf`, bypassing the AM/EM edge thresholds encoded in the graph.

## Decision

**The spread simulation is deprecated. Replaced by a static 500m connectivity neighbourhood buffer around connected components.**

## Rationale

1. **Function never worked:** Zero growth over 5 seasons with any reasonable parameter set. The 15m/35m edge thresholds are too conservative to support multi-season spread.
2. **Bypassed graph structure:** Building a fresh KDTree from all trees ignored the AM/EM distinction, the barrier-cell filtering, and the edge thresholds that were the entire point of the graph construction.
3. **Static buffer is honest:** A 500m buffer around each fungal network island answers "what area is within walking-dispersal range of this existing fungal community?" — a static, descriptive question that doesn't pretend to model temporal dynamics.
4. **No data to calibrate:** A dynamic spread model requires colonisation rate data (probability of establishment per unit time per unit distance) across urban substrates. No such data exists for Barcelona.

## Consequences

- Output renamed: `network_spread.html` → `network_neighborhoods.html`.
- Visualisation relabeled: "2030 projected spread" → "500m connectivity neighbourhood".
- `simulate_spread()` remains in notebook 04 for reproducibility but is wrapped in a deprecation warning.
- Phase 4 must not use the deprecated function for any inference.

## Rejected alternatives

- **Remove function entirely:** Breaks reproducibility of notebook 04. Deprecation preserves the development history.
- **Calibrate from literature:** Fungal colonisation rates in urban substrates are essentially unstudied — literature calibration would be speculative.
- **Replace with circuit theory (Circuitscape):** Methodologically valid but requires resistance surfaces calibrated to mycorrhizal dispersal — beyond graduate seminar scope.
