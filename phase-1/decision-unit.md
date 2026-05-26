# Decision Unit

## Spatial unit

**400m × 400m grid cell (Superilla scale)**

*Justification:* The Superilla programme — Barcelona's primary green-infrastructure delivery mechanism — operates at approximately 400m × 400m blocks. A finer unit (e.g., 100m) would produce recommendations at a scale below what the planning process can act on. A coarser unit (e.g., 1km) would aggregate across heterogeneous urban fabrics, washing out the barrier signal. The 400m unit maps directly to the decision-maker's operational unit of intervention planning.

## Temporal unit

**Annual snapshot (single planning cycle)**

*Justification:* The Ajuntament's green-infrastructure budget is allocated on an annual cycle. The output is a static priority ranking for the current planning year, not a time series. Input data vintages will be documented per source; the product card will state "valid for [budget cycle year]; re-run with updated inputs for subsequent cycles."

## Thematic / spectral unit

**Four barrier sub-scores per zone, plus one composite intervention recommendation:**

1. **Sealed-surface fraction** (0–100%) — from Copernicus Urban Atlas 10m
2. **Heat anomaly** (°C above city baseline) — from Landsat 8/9 LST
3. **Canopy / NDVI** (unitless, −1 to 1) — from Sentinel-2 L2A
4. **Host–mycorrhizal mismatch** (categorical: matched / mismatched / unconfirmable) — from Ajuntament tree inventory + FungalRoot v2.0 + GBIF
5. **Composite barrier index** (0–1) + **intervention-type recommendation** (de-paving / planting / species-selection / combined)

*Justification:* Each barrier maps to a specific, documented Ajuntament budget line. Keeping sub-scores separate lets planners weight barriers according to current-cycle priorities while still providing a default composite ranking. The categorical mismatch flag (rather than a pseudo-quantitative score) is deliberate — AM fungi are invisible to citizen science, and faking a continuous score for the AM-dominant majority of BCN zones would be dishonest.
