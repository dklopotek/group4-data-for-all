# ADR-004: AM Graph — Demonstration District Only

**Status:** ACCEPTED (with remediation path)
**Date:** 2026-05-26
**Deciders:** Rafik, Claude (Phase 3 connectivity audit)

## Context

The fungal connectivity graph (notebook 04) constructs a network where:
- Nodes = trees with known mycorrhizal type (AM or EM)
- Edges = spatial proximity within myco-type-specific thresholds (AM ≤15m, EM ≤35m)
- Barrier = grid cells with sealed_pct ≥ 0.7 block edge construction

After MYCO_LOOKUP filtering, 143,948 trees have known myco_type:
- 134,809 AM trees (93.7%)
- 9,139 EM trees (6.3%)

The full AM graph (134,809 nodes) has `n×(n-1)/2` = ~9.1 billion potential edges. A cKDTree radius query at 15m across the full city requires a tree of ~134K points — the query itself is `O(n log n)` but the edge count scales with tree density per 15m disk, which is high in dense urban areas (~50-200 trees per 15m radius). Memory and runtime blow up.

## Decision

**The AM graph is limited to a single demonstration district: SANT MARTÍ.**

EM graph runs city-wide (9,139 nodes — feasible).
Combined graph = AM (SANT MARTÍ only) + EM (all districts) = 35,177 nodes, 54,357 edges.

## Rationale

1. **SANT MARTÍ as demonstration:** Sant Martí is Barcelona's most populous district, covers the 22@ innovation district (active urban transformation), and has a representative mix of street trees, park trees, and sealed surfaces.
2. **Computational constraint is real:** Full-city AM graph is not achievable in a pandas/GeoPandas notebook pipeline without spatial indexing and edge-limiting heuristics beyond the current implementation.
3. **Network structure is illustrative, not operational:** The connectivity analysis demonstrates method feasibility, not city-wide inference. Bridge scores are zero city-wide anyway — the network model needs parameter tuning before full deployment.
4. **EM graph is small:** Only 9,139 EM trees exist — EM graph runs city-wide trivially. The limitation is AM-specific.

## Consequences

- `network_nodes.geojson` contains AM trees from SANT MARTÍ only + EM trees from all districts.
- `network_islands.geojson` underrepresents AM-connected components in non-Sant Martí districts.
- Connected component statistics (25,508 components, largest island = 552 trees) are valid for the combined graph but the AM component reflects only SANT MARTÍ.
- Network visualisation labels must disclose the district limitation.

## Remediation path

1. **Partition AM graph by district** — compute AM connectivity per district independently (10 sub-graphs). District boundaries are natural AM dispersal barriers (wide roads, sealed plazas). This is ecologically defensible.
2. **Spatial indexing with STRtree** — GeoPandas `sindex` for pre-filtering before cKDTree radius query. Reduces candidate pairs from `n²` to `n × local_density`.
3. **Edge cap per node** — limit each tree to its k=20 nearest neighbours within the 15m threshold. Ecological justification: a tree root system cannot sustain unlimited mycorrhizal connections.
4. **Re-run AM graph city-wide** using the district-partitioned + edge-capped approach. Target: <500K edges total.

## Rejected alternatives

- **Ignore limitation, present as city-wide:** Dishonest. The 04-connectivity notebook already correctly labels the AM graph as demonstration-only.
- **Drop AM graph entirely:** Loses the network dimension of the analysis. EM-only graph misses 93.7% of trees.
- **Increase AM threshold to reduce edge count:** 15m is already conservative (literature range 1-50m). Raising it would dilute the ecological signal.
