# Limitations Register

Each limitation with the condition under which it becomes a real failure. Mirrors paper §10; this is
the standalone deployment copy.

| # | Limitation | Becomes critical when |
|---|---|---|
| 1 | **Not validated against measured pollen.** Source layer is a literature-anchored emission proxy (Gabarra 2002; Maya-Manzano 2017). No open Barcelona *Platanus*-pollen series exists. | An open measured series appears and contradicts the proxy. |
| 2 | **Not a health/allergy predictor.** Models exposure potential, not clinical outcomes. | It is cited as health evidence. |
| 3 | **Not a decision on whether to remove planes.** Only sequences an existing policy. | Read as a removal mandate. |
| 4 | **Residential exposure misses daytime receptors** (schools, workplaces, commuters). | A commuter-heavy axis is under-ranked and that matters for the use case. |
| 5 | **MAUP — measured and load-bearing.** Re-running at census-section grain broke the exposure re-ordering result the 400 m grid supported (rollup Spearman 0.47; T1 fails, T4 1/3). | The section ranking is used as if it carried the same people-weighting evidence as the 400 m grid. |
| 6 | **Maturity is a coarse proxy.** Cell: young-tree share; section/street: categorical size class (A1 assumption). Neither is trunk diameter or measured emission. | A diameter/emission dataset shows the size classes mis-rank pollen output. June 2026 hunt: no continuous DBH/size data exists in BCN open portal (only ordinals). |
| 7 | **Pollarding cycle not per-tree.** Pruning reduces emission for ~2 years; city-wide cycle is 5 years but the *fitxa* is internal-only. | Real pruning dates become open and show a spatial bias that contradicts the uniform prior. |
| 8 | **Potency lens is modeled, not measured.** CALIOPE NO2 (25 m) is an allergenicity proxy, not a health outcome. | Validated ordinally (gate collinearity 0.22, var share 9%), but absolute values not calibrated to clinical response. |
| 9 | **Not validated against measured pollen.** XAC data exists but is request-only (CC-BY-NC); 1 trap integrates a ~15–30 km catchment. | Trap data is released and shows the spatial proxy mis-ranks the city at the catchment scale. |
| 10 | **Address parsing is free-text.** 100% street-match here, but a future inventory with dirtier `adreca` could drop coverage. | Coverage falls and unmatched planes are silently excluded. |

None is fatal to the deliberately modest analytical claim: a transparent, sensitivity-robust ranking
that, at the 400 m evidence grain, beats the city's implicit density rule on its own objective.
