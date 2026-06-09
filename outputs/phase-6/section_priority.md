# Section-Grain Priority Results (Phase 6 -- Deployment)

Recomputed at **census-section grain** (1068 sections, native demand grain --
NO areal interpolation). Source = mature Platanus count per section (assumption A1:
mature = ['EXEMPLAR', 'PRIMERA']). 40433 Platanus joined to sections
(11 unmatched).

**VERDICT: section-grain exposure largely redundant (honest limitation)**

## C1 -- grain sanity + agreement with the 400 m cell product
- sections: 1068 (expected ~1068); city pop joined:
  1,729,963 (0 sections missing pop).
- Spearman(section priority, rolled-up cell priority) = **0.4669**
  over 1068 sections -> REVIEW.

## T1 -- does exposure re-order vs naive plane-density?
Spearman(priority, source) = 0.9701; top-15 Jaccard =
0.5789, top-50 Jaccard = 0.5152.
-> exposure materially re-orders: **False** (criterion: J15<0.70 AND Spearman<0.90).

## T2 -- redundancy (two material layers, not one in a costume)
corr(priority,source) = 0.8685; corr(priority,exposure) = 0.3075;
corr(source,exposure) = 0.0866.
Both layers material: True; inputs not redundant: True.

## T3 -- allergen-exposure burden captured by top-k (read the MARGIN)
| k | priority | density-only | random | margin (priority - density) |
|---|---|---|---|---|
| 15 | 0.2764 | 0.2274 | 0.0135 | 0.049 |
| 50 | 0.4406 | 0.406 | 0.0454 | 0.0346 |

## T4 -- sensitivity (T1 re-order verdict must hold in >=2 of 3 arms)
{
  "broad_mature": false,
  "uniform_maturity": false,
  "rank_normalized": true
}
-> holds in majority: **False**.

## Top priority sections
See `outputs/phase-6/section_priority.csv` (top 50: key, district, planes, mature, population, priority).
Street-level action lists for the top sections: `outputs/phase-6/street_removal_actions.csv`.
