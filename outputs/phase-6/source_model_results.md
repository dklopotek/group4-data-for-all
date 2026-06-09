# Source-Estimator Results (Cycle-B Phase-4 Model #1)

Predicts observed **mature-plane density** from urban-form/demographic features (no plane-derived
inputs). Headline = **spatial-CV R2** (random-CV shown only to expose spatial-autocorrelation leakage,
the Cycle-A 0.999 trap; Roberts 2017, Ploton 2020).

**VERDICT: HONEST NEGATIVE: best spatial-CV R2 -0.2543 < 0.3 -- urban form does not predict historical plane placement (planting is path-dependent). Inventory irreplaceable.**

| model | random-CV R2 | spatial-CV R2 | random MAE | spatial MAE | leakage gap (R2) |
|---|---|---|---|---|---|
| Ridge | 0.4111 | **-0.2543** | 150.14 | 208.67 | 0.6654 |
| RandomForest | 0.4388 | **-0.3678** | 143.37 | 210.68 | 0.8066 |

Criterion (pre-registered): useful drift proxy iff spatial-CV R2 >= 0.3.

**Top RF features:** district_lbl_Eixample (0.2773), mean_ndvi (0.123), pop_density (0.0908), dist_to_centre_km (0.0808), mean_lst_celsius (0.0805), mean_sealed (0.0804).

The random-vs-spatial gap is the audit: a large gap = the same leakage that inflated Cycle A. We report
the spatial number as the truth.
