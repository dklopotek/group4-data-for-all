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
| 6 | **Maturity is a coarse proxy.** Cell: young-tree share; section/street: categorical size class (A1 assumption). Neither is trunk diameter or measured emission. | A diameter/emission dataset shows the size classes mis-rank pollen output. |
| 7 | **No stakeholder Monday-test, no independent reproduction.** Organizational deployment gates, open by design. | Treated as "deployed" without either. |
| 8 | **Address parsing is free-text.** 100% street-match here, but a future inventory with dirtier `adreca` could drop coverage. | Coverage falls and unmatched planes are silently excluded. |

None is fatal to the deliberately modest analytical claim: a transparent, sensitivity-robust ranking
that, at the 400 m evidence grain, beats the city's implicit density rule on its own objective.
