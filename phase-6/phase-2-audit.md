# Phase 2 (Data Understanding) — Companion Close-Out (Pivot Datasets)

**Date:** 2026-06-05
**Skill applied:** `crispdm-2-companion` (G1–G8 close-out: ingestion log, observed description, Wang & Strong cross-check, executable schema, MAUP/edge, annotation-noise, Croissant, versioning).
**Scope:** the 4 datasets the pivot *added* (population, boundaries, income, prescriptions) + the pollen NEGATIVE. The shared street-tree inventory is already closed out in Cycle A's `phase-2/`. Source of truth for acquisition: `data/raw/SOURCES.md`.
**Altitude:** seminar scope, lecture > skill. Load-bearing artifacts filled here; full per-source Croissant JSON-LD and standalone schema files are **deferred with reason** (E7/E-schema) — see §G7. This is an explicit `deferred`, not a silent skip.

## Coverage vs the 8 gaps

| Gap | Artifact | Pivot status | Where |
|---|---|---|---|
| G1 | Ingestion log | ✅ | §G1 (formalized from SOURCES.md) |
| G2 | Ingested-data description (observed) | ✅ | §G2 |
| G3 | Wang & Strong / ISO 25012 cross-check | ✅ | §G3 |
| G4 | Executable schema | ⚠️ inline spec; standalone files deferred | §G4 |
| G5 | MAUP + edge declaration (binding) | ✅ | §G5 |
| G6 | Annotation/label-noise estimate | ✅ | §G6 |
| G7 | Croissant JSON-LD sidecar | ⏸ deferred w/ reason | §G7 |
| G8 | Versioning policy | ✅ | §G8 |

## §G1 — Ingestion log

| source | retrieved (UTC) | url / api | dest | sha256 | rows | encoding | reproducible |
|---|---|---|---|---|---|---|---|
| Population (Padró 2026) | 2026-06-04 | opendata-ajuntament `pad_mdbas` resource c7fca94d… | `data/raw/2026_pad_mdbas.csv` | not recorded at ingest | 1068 | utf-8 | yes (resource id pinned in SOURCES.md) |
| Census-section boundaries | 2026-06-04 | Open Data BCN `808daafa…` (served as zip) | `data/raw/Unitats_Administratives_BCN_geojson/…POLIGONS.json` | not recorded | 1501 feat → 1068 SEC_CENS | utf-8 | yes (unzip step documented) |
| Income (INE Atlas 2023) | 2026-06-04 | INE Atlas gross income per person | `data/raw/atles_renda_bruta_persona.csv` | not recorded | 1068 | utf-8 | yes |
| Prescriptions (CatSalut) | 2026-06-05 | Socrata `thrd-jj3r.json`, region 79 | `data/raw/catsalut_receptes_bcnciutat_respiratori.csv` | `023a70a7…7ce06` | 288 | utf-8 | yes (SODA query documented) |
| **Platanus pollen** | 2026-06-04 | XAC / PIA portal; EAN | — | — | **0 (none open)** | — | **n/a — no machine-readable series exists** |

**Remediation note (E2):** SHA-256 was captured at ingest only for prescriptions. The other three are marked reproducible via pinned resource IDs/queries in `data/raw/SOURCES.md`; hashes can be backfilled by re-running the documented pulls. Flagged honestly rather than fabricated.

## §G2 — Ingested-data description (observed at the bytes)

- **Population** `2026_pad_mdbas.csv`: 1068 rows. Cols: `Data_Referencia, Codi_Districte, Nom_Districte, Codi_Barri, Nom_Barri, AEB, Seccio_Censal, Valor`. `Valor` (residents) sums to **1,729,963**; `Seccio_Censal` NOT zero-padded (1001…10141). Ref date 2026-01-01.
- **Boundaries** POLIGONS.json: 1501 features; filter `TIPUS_UA=="SEC_CENS"` → **1068** polygons. CRS **EPSG:25831** declared in file. Key = `DISTRICTE(2) + SEC_CENS(3)`.
- **Income** `atles_renda_bruta_persona.csv`: 1068 rows. Income col `Import_Renda*` (€/person, numeric after coercion); key = `Codi_Districte.zfill(2)+Seccio_Censal.zfill(3)`. Some sections NaN → median-imputed at prep (count reported by `equity_layer.py`).
- **Prescriptions** `catsalut_receptes_bcnciutat_respiratori.csv`: 288 rows. Cols: `any, grup_edat, sexe, codi_atc_2, atc_2, receptes, envasos`. Region 79 only; ATC2 ∈ {R01,R03,R06}; years 2020–25. R06 2024 ≈ 636,417 rx.
- **Observed-vs-asserted disagreement:** none material. Population total matches SOURCES.md assertion; join verified 1068/1068.

## §G3 — Wang & Strong cross-check (key dimensions)

| dimension | population | income | prescriptions | boundaries |
|---|---|---|---|---|
| Accuracy | assessed: official register | assessed: INE statistical | deferred: dispensing≠patients (over-counts) | assessed: official cadastral |
| Completeness | assessed: 99.1% allocated | assessed: NaN imputed, count reported | assessed: full age×sex | assessed: 1068/1068 |
| Timeliness | assessed: 2026 | assessed: 2023 (3yr lag) | assessed: 2020–25 | assessed: current |
| Believability | assessed: high | assessed: high | deferred: utilization bias (female-skew partly care-seeking) | assessed: high |
| Interpretability | assessed: count | assessed: €/person | assessed: rx count | assessed: polygon |
| Consistency (rep.) | assessed: 5-digit key | assessed: 5-digit key | n/a: region-level, no spatial join | assessed: EPSG:25831 |
| Appropriate amount | assessed: section grain ok | assessed: section grain ok | **deferred: too coarse (region only) → city-wide calibration only, not a spatial layer** | assessed |

The one load-bearing limitation: prescriptions are region-level → usable only as a city-wide age/sex *relative* weight, never a sub-city layer. This drove the rejection of the at-risk and sex layers in Phase 5.

## §G4 — Executable schema (inline spec; standalone files deferred)

Load-bearing join is population/income ↔ boundaries. Schema expectation (Pandera-style, the project's stack):

```
population:  Codi_Districte:str(2)  Seccio_Censal:str  Valor:int>=0  key:str(5) unique  nullable=none
income:      key:str(5) unique  income:float>0 (nullable→median-impute, report count)
boundaries:  TIPUS_UA=="SEC_CENS"  DISTRICTE:str(2)  SEC_CENS:str(3)  geometry:Polygon  crs==EPSG:25831
join:        population.key == boundaries.key, 1:1, 1068/1068 (asserted in exposure_layer.py)
```

`src/exposure_layer.py` already enforces the binding constraint at runtime (`assert miss == 0`). Standalone `.yaml` schema files deferred (seminar; Cycle A `phase-2/schemas/` demonstrates the capability) — the runtime assert is the live validation gate.

## §G5 — MAUP & edge declaration (binding)

- **Native CRS:** boundaries EPSG:25831 (already projected metres); population/income are tabular, joined to boundaries.
- **Analysis CRS:** EPSG:25831 throughout (no reprojection of the analysis grid).
- **Aggregation unit:** 400 m grid cell; reported up to census section / street axis.
- **MAUP:** population/income → cell via areal- (pop) and population-weighted (income) interpolation. **Binding:** Phase 3+ must not silently re-grid or re-aggregate; cell size and section partition are fixed inputs and results are conditional on them. Alternative cell size NOT tested (seminar time) — declared as a limitation, not hidden.
- **Edge:** Barcelona municipal boundary is the study extent; no cross-border receptors modeled (residents outside the city not counted) — stated.

## §G6 — Annotation / label-noise

None of the 4 pivot datasets are crowd-sourced — all official administrative/statistical registers, so classic citizen-science label noise is **n/a**. The one quality caveat is **measurement/utilization bias** in prescriptions (dispensing counts ≠ rhinitis patients; antihistamines also treat urticaria; female care-seeking skew). Lifted verbatim from SOURCES.md and `sex_atrisk.md`; mitigation = used only as relative age/sex weight, then rejected as non-mappable. (Contrast: Cycle A's GBIF fungi *were* crowd-sourced and carry occurrence/sampling bias — closed in Cycle A `phase-2/bias-and-annotation.md`.)

## §G7 — Croissant sidecar (DEFERRED, with reason)

Full per-source Croissant JSON-LD sidecars are **deferred**. Reason: the pivot is a seminar deliverable, not a published dataset; the data sheets + this close-out are the source of truth; Cycle A's `phase-2/croissant/` already demonstrates the team can produce valid Croissant. If the product is ever published, sidecars inherit provenance from §G1–G2. Marked `deferred`, not skipped (skill anti-pattern compliance).

## §G8 — Versioning policy

- **Pinning:** Open Data BCN resource IDs + Socrata dataset id (`thrd-jj3r`) recorded in SOURCES.md; raw files committed under `data/raw/` (small CSVs).
- **Re-ingest cadence:** one-shot (seminar). Population updates annually; income annually; prescriptions annually — re-pull only if extending past this project.
- **Breaking-change detection:** re-run `exposure_layer.py` / `equity_layer.py`; the 1068/1068 join assert + min-max ranges are the diff signal.
- **Retirement:** drop if upstream resource id changes or license changes.

## Handoff gate → Phase 3

All load-bearing Phase-2 artifacts for the pivot exist and are non-empty (G1, G2, G3, G5, G6, G8 filled; G4 inline + runtime assert; G7 deferred-with-reason). The brief still holds (the decision the data can answer is exposure prioritization, not measured-pollen or sub-city allergy — both declared absent). **Phase 3 (data-preparation.md) may proceed** — and did.
