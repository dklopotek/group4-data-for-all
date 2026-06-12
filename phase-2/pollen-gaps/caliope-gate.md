# CALIOPE-Urban NO2 — pre-wiring gate (collinearity + variance decomposition)

> Run before deciding whether to wire CALIOPE NO2 into the planner, to test the "resolution
> illusion" risk (a real 25 m NO2 surface multiplied against a coarse assumption-driven emission
> layer could render an allergenicity-weighted *traffic* map that merely looks authoritative).
> Source: BSC CALIOPE-Urban, Zenodo 16737066, `Dataset2A` (annual mean NO2 per census tract,
> mean of 2019-2024). Licence cc-by-4.0 (Zenodo metadata). Reproduce: download Dataset2A, join on
> `ID_census` last-5 = section `key`.

## Crosswalk
`ID_census` (e.g. 8019301005) last-5 digits == our section `key` (e.g. 01005). **Match rate 1.000;
1,068 / 1,068 sections joined; 0 missing.** No fallback needed.

## Collinearity (is NO2 just the emission corridors restated?)
| pair | Pearson | Spearman |
|---|---|---|
| source_std (emission) vs NO2 | **+0.22** | +0.35 |
| priority (exposure) vs NO2 | +0.14 | +0.35 |
| mature_count vs NO2 | +0.22 | +0.35 |
| exposure_pop vs NO2 | +0.06 | +0.11 |
| (planes-only) source vs NO2 | +0.16 | — |

Weak positive. The dense-plane corridors are only mildly the high-NO2 arterials — NO2 carries
**largely independent** spatial information, not a restatement of the emission layer.

## Variance decomposition of the allergenicity-weighted exposure
`weighted = priority x minmax(NO2)` (NO2 as a multiplicative per-grain potency modifier on exposure).
| share | R2 |
|---|---|
| Var(weighted) explained by **priority** | **0.87** |
| Var(weighted) explained by **NO2** | **0.09** |
| Var(weighted) explained by source | 0.75 |

The weighted map is **dominated by our existing priority (87%)**, not by NO2 (9%). The
resolution-illusion failure mode (NO2 field showing through as fake section contrasts) **does NOT
occur** for this multiplication.

## Re-ordering
- Spearman(weighted, priority) = **0.983** — global order ~preserved.
- top-15 Jaccard(weighted vs priority) = 0.667; top-50 = 0.449 — NO2 **does** re-shuffle membership
  meaningfully (a third of the top-15, half of the top-50) without overturning the ranking.

## VERDICT: PASS — wire it as an ordinal, non-dominating potency lens.
NO2 is independent (collinearity 0.22), additive (re-shuffles the top), and **non-dominating**
(9% of variance; rank preserved 0.98). It will not masquerade as a traffic map. These exact numbers
are the required disclosure.

## Conditions on wiring (carry forward)
1. Use the **March-April mean** from `Dataset2B` (daily per-tract; average the `<yr>0301..<yr>0430`
   columns) for the final layer — NOT the annual mean used for this gate. The gate's collinearity
   verdict holds (NO2 spatial pattern is traffic-driven, ~stable annual-vs-April), but the shipped
   values should be season-matched.
2. NO2 enters **only** as a multiplicative potency modifier on **exposure**, never folded into
   emission (mechanism = membrane damage -> Pla a 3 release, not more grains).
3. Treat NO2 as **ordinal** (it can rank, not "2.3x worse") — no dose-response is available.
4. Relabel the product a **cycle-averaged climatological** exposure surface (the pollarding prior is
   uniform and spatially smoothed, so the map is not an April-2026 prediction).
5. Outstanding (minor, because we use NO2 ordinally): validate modeled NO2 against the 9 XVPCA
   stations' measured annual means before trusting absolute values.
6. Disclose these gate numbers wherever the NO2 lens appears; teach them to Vera.
