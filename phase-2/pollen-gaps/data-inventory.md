# Phase-2 Data Inventory — closing the pollen-model gaps

> Produced by the `earn-the-data` discipline (primary-source verified, June 2026) in response to a
> scientific critique of the source layer (allometry / pollarding / dispersion / allergenicity).
> Every candidate below was verified at its primary source; secondhand numbers were discarded
> (one — "the legacy tree inventory carries trunk perimeter" — was checked against the real CSV and
> found FALSE, a summary hallucination). This is a NEW, user-authorised data hunt; it sits alongside,
> and does not replace, the original Phase-2 inventory.

## Decision unit

- **Spatial:** census section (1,068 units) — the operational grain the planner acts on; plus a 400 m grid for the evidence/claim layer. A supporting source must vary at ~few-hundred-metre scale (2x rule wants <= ~200 m).
- **Per-tree:** the source layer is built from individual street trees (40,444 Platanus), so a size/emission signal is wanted per tree.
- **Temporal:** Platanus season is March–April; the product is a static annual-scale priority, not hourly.

## The four gaps and what the hunt found

| Gap | Best candidate | Obtainable? | Verdict |
|---|---|---|---|
| **Per-tree size (DBH/canopy)** for Katz allometry | Open Data BCN `arbrat-viari/zona/parcs` | **No continuous measure** — only ordinal `categoria_arbrat`; legacy `ALCADA` also a class | Cannot instantiate allometry per tree. Fallback: declared per-class size weights. |
| **Pollarding (esporga) regime** | Parcs i Jardins per-tree `fitxa` (pruning dates) | **Exists internally, NOT open**; city-wide avg **~5-yr** cycle IS documented | Per-tree correction impossible with open data → declared limitation + optional uniform prior. |
| **NO2 allergenicity surface** | **BSC CALIOPE-Urban (Zenodo 16737066)** | **YES — open, 25 m, pre-aggregated to the 1,068 census tracts** | **Recommended: wire it in.** The one genuine new layer. |
| **Measured Platanus pollen** | XAC / PIA (UAB-ICTA, Belmonte) | **Published outputs freely accessible** (calendar PDF, 30-yr chart, Fitxa Botànica, real-time forecast); raw daily series CC-BY-NC request-only; 1 trap, ~15–30 km catchment | Temporal + species validation adopted in Phase 5. Cannot validate spatial ranking. Full documentation: `phase-5/aerobiological-validation-sources.md`. |

## Candidate scorecard (5-dimension rubric, 0–3 each)

| Candidate | Prov | Res | Cov | Lic | Bias | Total | Decision |
|---|---|---|---|---|---|---|---|
| **CALIOPE-Urban NO2** (Zenodo 16737066, BSC) | 3 | 3 | 3 | 2 | 2 | **13** | **RECOMMEND — wire in (NO2 allergenicity-context layer)** |
| Ajuntament/ASPB *Mapes d'immissió* NO2 (street-segment) | 3 | 2 | 3 | 3 | 2 | 13 | Cross-check / official corroborant |
| XVPCA hourly stations (9 pts) | 3 | 0 | 2 | 3 | 2 | 10 | Ground-truth points only (fails 2x as a surface) |
| BCN tree inventory — as a SIZE source | 3 | 0 | 3 | 3 | 2 | 11 | Insufficient for allometry (no DBH); already used for location/source |
| XAC Platanus pollen series | 3 | 1* | 3 | 1 | 2 | 10 | **UPDATED 2026-06-14**: Published outputs (pollen calendar PDF, 30-year aggregate chart, Fitxa Botànica SCAIC/PIA 2022, real-time weekly forecast) are freely accessible — no request needed. Raw daily time-series still request-gated (CC-BY-NC). Published outputs adopted as external validation evidence in Phase 5. See `phase-5/aerobiological-validation-sources.md`. |
| Pollarding / esporga (per-tree) | — | — | — | — | — | — | **No open dataset exists** → declared limitation |
| CAMS NO2 (~10 km) | 3 | 0 | 3 | 3 | 2 | 11 | EXCLUDED — one pixel ~ whole city |
| EEA interpolated NO2 (1 km) | 3 | 1 | 3 | 3 | 2 | 12 | EXCLUDED for intra-city (fails 2x by 5–10x) |
| Sentinel-5P/TROPOMI NO2 | 3 | 0 | 3 | 3 | 1 | 10 | EXCLUDED — ~3.5 km AND column not ground-level |

\* XAC resolution: temporal 3 / spatial 0 — one trap integrates a ~15–30 km catchment; it cannot resolve neighbourhoods (documented 18–34 % divergence at 1 m–1.5 km). Scored 1 to reflect that only the temporal axis is usable.

## Why the shape of the CALIOPE score matters

13/15 with **Resolution = 3** and **Provenance = 3** is the right shape: it clears the 2x rule comfortably (25 m vs a few-hundred-metre unit; the publisher even pre-aggregated it to our exact 1,068-tract geometry) and it is peer-reviewed (Nature *Scientific Data* 2026) and fused with the 9 official XVPCA monitors. The two points lost are **Licensing** (Zenodo says CC-BY-4.0 but the readme adds a non-commercial/research caveat — must confirm with BSC before any non-academic deployment) and **Bias** (it is modeled R-LINE + land-use regression, not measured — validate against the XVPCA points before trusting it). Neither blocks use as an annual allergenicity-context layer at section grain.

## Primary-source URLs (recorded for reproducibility)

- CALIOPE-Urban open dataset — https://zenodo.org/records/16737066 ; data paper https://www.nature.com/articles/s41597-026-06592-x ; forecast portal https://caliope.bsc.es/
- Ajuntament *Mapes d'immissió* — https://opendata-ajuntament.barcelona.cat/data/en/dataset/mapes-immissio-qualitat-aire
- XVPCA hourly — https://opendata-ajuntament.barcelona.cat/data/en/dataset/qualitat-aire-detall-bcn
- Tree inventory — https://opendata-ajuntament.barcelona.cat/data/en/dataset/arbrat-viari (and `-zona`, `-parcs`)
- XAC / PIA — https://lap.uab.cat/aerobiologia/ ; EAN data policy https://ean.polleninfo.eu/Ean/datausepolicy
- Pla Director de l'Arbrat 2017-2037 — https://bcnroc.ajuntament.barcelona.cat/jspui/handle/11703/101548
- Pollarding cycle (~5-yr, official) — Ajuntament press release, temporada de poda 2024 (barcelona.cat)
