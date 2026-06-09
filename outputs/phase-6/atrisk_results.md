# At-Risk (Allergy-Prevalence) Layer Results (Phase 6 v2)

**Layer:** literature-weighted demographic (age-band x AR prevalence x Platanus share 0.37 constant)
**Spatial AR data:** none below health-region; layer is modeled, not measured

**VERDICT: age-weighting largely redundant with population at this resolution -- honest: keep v1 (population), report at-risk as a minor refinement**

## V2-1 -- does prevalence re-order vs plain population?
Spearman(at_risk, population) = 0.999; Spearman(priority_v2, priority_v1) = 0.9997; top-15 Jaccard = 0.875, top-50 Jaccard = 0.9231.
-> prevalence materially re-orders: **False** (criterion: jaccard_top15 < 0.70 AND spearman_atrisk_vs_population < 0.95).

## V2-2 -- city-wide calibration (honesty note)
{
  "R06_total": 566817,
  "top_age_bands_by_prescriptions": {
    "60-64 anys": 46700,
    "50-54 anys": 46495,
    "65-69 anys": 46444,
    "55-59 anys": 45228,
    "45-49 anys": 44422
  },
  "note": "prescriptions peak in middle/older age (chronic medication use), while AR PREVALENCE peaks younger -- prescriptions are a use proxy, not a prevalence map; divergence reported, not forced to agree."
}
