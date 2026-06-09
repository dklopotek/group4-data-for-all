# Equity (Deprivation) Weighting Results (Phase 6 v3)

Income missing sections imputed with city median: 0.

## V3-1 decorrelation (precondition)
corr(deprivation, source) = -0.0077; corr(deprivation, exposure) = 0.1733.
-> decorrelated from both (genuine new info): **True**.

## V3-2 reorder (expected given V3-1)
Spearman(v3, v1) = 0.9623; top-15 Jaccard = 0.6667, top-50 Jaccard = 0.7241.

## V3-3 equity-efficiency TRADEOFF (the finding)
| k | efficiency map burden captured | equity map burden captured | relief sacrificed | deprived-tercile share (efficiency -> equity) |
|---|---|---|---|---|
| 15 | 0.1801 | 0.1748 | 0.0052 | 0.4 -> 0.6 |
| 50 | 0.4458 | 0.4371 | 0.0087 | 0.28 -> 0.36 |

Reading: the equity map directs more of the top cells into the most-deprived income tercile, at the cost of capturing less total exposure burden. Both numbers are the decision.

## Sensitivity (top-15 Jaccard vs v1)
{
  "floored_weight": 0.875,
  "rank_based": 0.5
}

## Verdict
deprivation is a genuine, decorrelated layer; equity weighting redirects priority toward the most-deprived tercile at a measured exposure-relief cost (see V3_3). Efficiency (v1) and equity (v3) are both valid objectives; the planner chooses.
