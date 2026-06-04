# External Validation Results

**Verdict: FAIL** (pre-registered criterion in `phase-5/external-validation-design.md` Sec 4)

LEAKAGE WARNING: ['prpi', 's4_mismatch'] are composite inputs

Cells: 99 with >=1 GBIF record / 494 total.

## Richness (primary, observed subset, OLS)
| Model | Adj-R2 |
|---|---|
| M0 abiotic null (sealed + ndvi + effort) | 0.6972 |
| M1 + biotic/host | 0.6777 |
| **Delta Adj-R2** | **-0.0195** |

partial-F = 0.178, p = 0.98917 -> biotic block **adds NO signal**

## Presence (secondary, all cells, logistic, 5-fold CV)
M0 AUC 1.0 -> M1 AUC 1.0 (Delta 0.0); LR p 0.99996 -> FAIL

## Robustness
- log-richness OLS: dAdjR2 -0.0009, partial-F p 0.5675
- drop effort: dAdjR2 -0.0104, partial-F p 0.5445
- Moran's I on M1 residuals: I=-0.04743565357805596, p=0.214

## VIF (collinearity)
{
  "mean_sealed": 165.74,
  "mean_ndvi": 92.22,
  "log_effort": 1.22,
  "am_pct": Infinity,
  "em_pct": Infinity,
  "platanus_pct": 698.93,
  "s4_mismatch": 1.22,
  "prpi": 627.91,
  "species_richness": 3.8,
  "total_trees": 5.19
}

## M1 standardized coefficients
{
  "intercept": 3.4848,
  "mean_sealed": -3.0048,
  "mean_ndvi": -2.9642,
  "log_effort": 6.9445,
  "am_pct": 0.1209,
  "em_pct": -0.1209,
  "platanus_pct": 6.8825,
  "s4_mismatch": -0.0602,
  "prpi": -6.7994,
  "species_richness": -0.5412,
  "total_trees": 0.2067
}

## Interpretation and caveats (honest reading)

**Headline (richness, the valid test).** Across the 99 cells with at least one independent GBIF fungal record, the abiotic null (sealed + NDVI + sampling effort) explains adjusted-R² = 0.70 — and that is dominated by `log_effort` (standardized coef +6.94): you record more species where more people looked. Adding the full biotic/host block (am/em/platanus/mismatch/PRPI/richness/trees) moves adjusted-R² *down* by 0.0195 and is non-significant (partial-F p = 0.989). The block adds **no** information about real external fungal occurrence beyond effort and the abiotic surface. This holds under both robustness variants: log-richness (p = 0.57) and drop-effort (p = 0.54). Moran's I on residuals is not significant (I = −0.047, p = 0.21), so the FAIL is not a spatial-autocorrelation artifact.

**Caveat 1 — the presence model is circular and must be discounted.** `gbif_present` was defined as `effort ≥ 1` and `log_effort` was a covariate, so effort predicts presence by construction; AUC = 1.0 for both M0 and M1 is mechanical, not evidence. The presence row is uninformative. The richness model on the observed subset carries the verdict. (Logged as a dated addendum in the design doc — not silently re-run after seeing results.)

**Caveat 2 — severe multicollinearity in the biotic block.** VIF is ∞ for `am_pct`/`em_pct` (they plus `n_unknown` sum to a constant) and 600–700 for `platanus_pct` and `prpi`. The individual M1 coefficients (e.g. platanus +6.88 cancelling prpi −6.80) are therefore uninterpretable. This does **not** rescue the biotic claim: the *block* partial-F is valid regardless of within-block collinearity, and the block explains no new variance. If anything, the collinearity is itself a finding — the "five components" are not five independent signals.

**Caveat 3 — the leakage warning is benign.** The run flagged `prpi` and `s4_mismatch` as composite inputs. That is expected: they define `composite_score_B`, but here they are used as *predictors of an external GBIF target the composite never saw*. PRPI never had access to GBIF occurrence, so there is no leakage into this test's target. The warning confirms the guard works; it is not a violation.

**What this means.** Three independent lines now converge: (a) the literature finds the AM→EM host lever weak-to-unsupported; (b) the internal diagnostic shows `composite_score_B` ≈ sealed surface; (c) this external test shows the biotic/host layers carry no detectable signal about real fungal occurrence. The mycorrhizal thesis does not survive contact with independent data **in this dataset, at this resolution, with these proxies.** The defensible Session-5 verdict is **reframe**: deliver an urban cooling / depaving prioritization (the abiotic signal is real and decision-relevant for the Eixos Verds) and carry the mycorrhizal claim as an explicit, here-falsified hypothesis. This is a clean, defensible result — exactly the "uncomfortable truth" the brief and the instructor asked for.
