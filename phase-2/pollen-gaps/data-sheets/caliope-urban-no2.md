# Data Sheet — CALIOPE-Urban NO2 (Barcelona, street-resolution)

Following Gebru et al. (2021) + a Limitations section. The recommended new source from the pollen-gap hunt.

## 1. Motivation
Created by the **Barcelona Supercomputing Center (BSC)** Earth Sciences dept to provide street-resolution air-quality (NO2) for Barcelona, fusing a dispersion model with the official monitoring network. Published as an open dataset (Zenodo) accompanying a Nature *Scientific Data* (2026) paper. For us: it supplies the **pollution dimension** the pollen critique flagged — NO2/O3 damage Platanus pollen and modulate the Pla a 3 allergen, so allergenicity per grain is higher on high-NO2 corridors. It lets us add an **allergenicity-context layer** at our exact decision unit.

## 2. Composition
- Modeled annual and daily mean **NO2** (µg/m³) over Barcelona municipality (+250 m buffer).
- Native grid **25 m × 25 m** (~250,000 cells). Method: **R-LINE Gaussian dispersion + microscale land-use regression**, data-fused with the XVPCA monitoring network.
- Crucially, the publisher provides a **pre-aggregation to the 1,068 Barcelona census tracts** (their "Dataset2") — i.e. the section-grain join we need is already done.
- **NO2 only** in the fine product; O3 at street scale is NOT included.

## 3. Collection
Not field-measured per cell — it is a **physics+statistics model** (R-LINE dispersion over a road-emissions inventory + LUR), anchored to the **9 XVPCA stations**. Years covered: **2019–2024**. Provenance: BSC on MareNostrum 5; operational street forecast launched May 2025.

## 4. Pre-processing (steps WE must perform before use)
- **CRS:** dataset is **EPSG:4326 (WGS84)**; our pipeline is EPSG:25831. Reproject before any spatial join (or use the pre-aggregated census-tract table and join on the tract key directly — preferred, avoids reprojection).
- **Key join:** confirm the dataset's census-tract identifier matches our section `key` (district 2-digit + section 3-digit). If it uses INE `CUSEC` codes, build a crosswalk.
- **Temporal aggregation:** use the **annual mean** (our product is annual-scale). Do NOT use hourly — the open grid is annual/daily only.
- **Units:** µg/m³ (no conversion); min-max normalise only at the modelling layer, like the other std layers.
- **Validation:** before trusting it, cross-check the modeled values at the 9 XVPCA station locations against their measured annual means.

## 5. Uses
**Should be used for:** an **annual NO2 allergenicity-context layer** at census-section grain — an optional lens that flags sections where the *same* pollen grain is likely more allergenic, and a guardrail for interpretation. As a *secondary* weight or a displayed context layer, NOT as a replacement for the source proxy.
**Should NOT be used for:** claiming measured pollen or measured allergy; hour-of-day pollen-spike coupling (open grid is annual/daily, not hourly); O3 effects (not in the fine product); any commercial/redistributive use until the licence caveat is cleared with BSC.

## 6. Distribution
Open download from **Zenodo (record 16737066)** — Shapefile + **GeoTIFF** + CSV, plus the census-tract CSV. DOI-citable.

## 7. Maintenance
Actively maintained by BSC; operational forecast ongoing. The historical archive (2019–2024) is the stable, citable product. Re-pull on a new Zenodo version.

## 8. Limitations
- **Modeled, not measured** (R-LINE + LUR). Validate against XVPCA; treat as a strong estimate, not ground truth.
- **Licence ambiguity:** Zenodo metadata = CC-BY-4.0, but the readme adds a non-commercial/research-attribution caveat. **Confirm exact terms with BSC** before any non-academic municipal deployment. (Scored Licensing = 2 for this reason.)
- **NO2 only**, annual/daily only — no O3, no hourly, from the open product.
- **Near-road structure is the signal AND a bias:** LUR/R-LINE emphasise road proximity; canyon effects may over- or under-state concentrations on specific street geometries. Cross-check with the Ajuntament *Mapes d'immissió* street-segment map as an independent official corroborant.
- **It does not fix the source proxy** — it adds an allergenicity *context*, not measured pollen. The pollen source remains an unvalidated proxy; this layer changes interpretation of grains, not the grain count.
