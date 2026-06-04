# Allergen-Priority Results (Phase 6)

**Pollen validation:** INFEASIBLE - source is literature-anchored proxy, not measured-pollen-validated (see design Sec 0)

**VERDICT: exposure earns its place (materially re-orders + non-redundant)**

## T1 - does exposure re-order vs naive plane-density?
Spearman(priority, source) = 0.8909; top-15 Jaccard = 0.3043, top-50 Jaccard = 0.3889.
-> exposure materially re-orders: **True** (criterion: J15<0.70 AND Spearman<0.90).

## T2 - redundancy (not one layer in a costume)
corr(priority, source) = 0.803; corr(priority, exposure) = 0.6361; corr(source, exposure) = 0.2975.
Both layers material: True; inputs not redundant: True.

## T3 - allergen-exposure burden captured by top-k (priority's own objective; read the MARGIN)
| k | priority | density-only | random | margin (priority - density) |
|---|---|---|---|---|
| 15 | 0.1801 | 0.1337 | 0.0296 | 0.0464 |
| 50 | 0.4458 | 0.3524 | 0.1015 | 0.0934 |

## T4 - sensitivity (T1 re-order verdict must hold)
{
  "uniform_maturity": true,
  "rank_normalized": true,
  "min_aggregation": true
}

## Top priority cells
See `outputs/phase-6/priority_zones.csv` (top 30: cell, district, planes, population, priority, feasibility).
