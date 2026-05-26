# Data Source Inventory — Mycorrhizal Network Mapping, Barcelona

> 10 candidate datasets surveyed across the 6 seminar categories
> (remote-sensing-optical, remote-sensing-thermal, climate-reanalysis, in-situ-sensors,
> biodiversity, built-environment). Decision unit: **Superilla / 400m × 400m grid**.
> Rubric: adopt only if total ≥ 10/14, with no fatal axis. Source-of-truth brief:
> `docs/problem-brief.md` (v1, copied from `C:\Users\Rafik\Downloads\problem-brief_1.md`).

## How this file is organised

Each candidate has: provider, access method, category, rubric scoring (0–2 per axis,
total /14), one-paragraph plain-English description, and a verdict (Adopt / Reject /
Investigate further). Summary at the bottom lists adopted / rejected / under-investigation
datasets and flags coverage gaps.

## The Dataset Assessment Rubric

| Axis | 0 | 1 | 2 |
|---|---|---|---|
| **Provenance** | Source unclear | Source documented | Documented + cited in peer-reviewed work |
| **Resolution match** | Coarser than decision unit | Roughly matches | ≥2× finer than decision unit |
| **Coverage** | Major gaps over our place/time | Minor gaps | Full coverage |
| **License** | Unclear / restrictive | Permissive with attribution | Public domain / CC0 |
| **Access reliability** | Manual scraping, fragile | API but rate-limited or unstable | Stable API or stable bulk download |
| **Bias clarity** | Unknown biases | Some documented | Biases fully documented + quantified |
| **Maintenance** | Stale, no updates | Updated irregularly | Actively maintained, contact available |

**The 2× rule applied to our 400m decision unit:** native spatial resolution must be
≤200m to score 2 on resolution match.

---

## 1. GBIF — Global Biodiversity Information Facility (fungal occurrences, Barcelona / Catalonia, 2015–2024)

- **Provider:** GBIF Secretariat (intergovernmental, hosted in Copenhagen)
- **Access method:** REST API (`api.gbif.org/v1/occurrence/search`) + bulk download (DOI-stamped DwC-A archive)
- **Category:** biodiversity

### Rubric scoring (0–2 per axis)

| Axis | Score | Justification |
|---|---|---|
| Provenance | 2 | GBIF is the canonical biodiversity occurrence aggregator; cited in thousands of peer-reviewed studies; each record carries a citable DOI |
| Resolution match | 2 | Point-level lat/lon (when reported with coordinate uncertainty ≤100m, which is the majority for Catalan records); finer than 400m grid |
| Coverage | 1 | Full Catalonia coverage but density varies wildly; record counts for Barcelona municipality 2015–2024 to be confirmed in profiling (estimated 200–800 records depending on filter strictness) |
| License | 2 | CC0 / CC-BY / CC-BY-NC per-record (filter to CC0 + CC-BY for redistribution); attribution string per record |
| Access reliability | 2 | Stable REST API + bulk download; GBIF Hosted Portals are well-monitored |
| Bias clarity | 1 | Major biases documented but not quantified for our area: (i) fruiting-body bias (AM fungi essentially invisible), (ii) citizen-science geographic skew toward accessible high-foot-traffic areas, (iii) seasonal bias (autumn-heavy) — all noted in published GBIF metadata but not numerically corrected |
| Maintenance | 2 | Active aggregation, ~1B occurrences globally, daily ingestion |
| **TOTAL** | **12/14** | |

### One-paragraph description

GBIF aggregates georeferenced biodiversity occurrence records (specimen collections,
citizen-science observations, surveys) from ~2,000 publishing institutions worldwide.
An instance is a single occurrence record with taxon, lat/lon (with coordinate
uncertainty), date, basis-of-record (e.g. HUMAN_OBSERVATION, PRESERVED_SPECIMEN), and
provenance back to the source dataset. For Barcelona, the fungal subset is dominated
by iNaturalist research-grade observations (which mirror to GBIF, so we do not
inventory iNat as a separate source) plus museum and survey records. Useful for: the
**observed-fungi layer** of the host-vs-observed gap analysis. Cannot tell us about
hyphal network presence, AM colonisation, or anything not visible aboveground.

### Verdict

**Adopt** — secondary dataset, full datasheet required. This is the observed-fungi
side of the host-vs-observed gap analysis; the brief depends on it.

---

## 2. FungalRoot v2.0 (Soudzilovskaia et al. 2022, *New Phytologist*)

- **Provider:** Soudzilovskaia lab consortium; published as supplementary data with the *New Phytologist* paper (doi:10.1111/nph.18207)
- **Access method:** Static download from journal supplementary materials + Zenodo mirror; also redistributed by FunFun and other mycology databases
- **Category:** biodiversity (lookup / trait database)

### Rubric scoring (0–2 per axis)

| Axis | Score | Justification |
|---|---|---|
| Provenance | 2 | Published in *New Phytologist*; canonical reference for plant-mycorrhizal-type lookup |
| Resolution match | 2 | Categorical lookup at species level — exact match for the question we are asking it (host taxon → mycorrhizal type). Spatial resolution N/A (it is a join table, not a spatial dataset) |
| Coverage | 2 | ~14,870 plant species; expected to cover all major BCN street/park tree genera (*Platanus*, *Tilia*, *Celtis*, *Citrus*, *Cupressus*, *Pinus*, *Quercus*, etc.) |
| License | 2 | Open under journal supplementary terms, redistribution permitted with citation |
| Access reliability | 2 | Static published file; Zenodo mirror is permanent |
| Bias clarity | 1 | Returns mycorrhizal *type* (AM, EcM, ErM, NM, mixed) only — not colonisation intensity, viability, or partner identity. Limit is documented in the paper but not quantified per our use case |
| Maintenance | 1 | v2.0 published 2022; no v3 announced. Effectively static — versioned but not actively updated |
| **TOTAL** | **12/14** | |

### One-paragraph description

FungalRoot v2.0 is a global empirical database of plant mycorrhizal traits compiled
from ~36,000 source records. An instance is a plant species with its assigned
mycorrhizal type and a reference to the source observations. We use it as the **join
table** that converts our tree-species inventory into expected-mycorrhizal-type at
each green node. It is not a spatial or observational dataset on its own; it is the
host-side inference layer that makes the brief's analysis possible. Cannot tell us
which fungal *species* partner with which tree, only which *type* of mycorrhiza is
expected.

### Verdict

**Adopt** — auxiliary (join table), no full datasheet required (datasheet template
is shaped for observational/spatial datasets; we cite the paper inline in the
methodology section instead).

---

## 3. GlobalAMFungi (Větrovský et al. 2023, *New Phytologist*)

- **Provider:** Věrovský / Czech Academy of Sciences consortium
- **Access method:** `globalamfungi.com` web portal (download per study); some data also on ENA/SRA (raw reads)
- **Category:** biodiversity

### Rubric scoring (0–2 per axis)

| Axis | Score | Justification |
|---|---|---|
| Provenance | 2 | Published in *New Phytologist* (doi:10.1111/nph.19283); peer-reviewed methodology |
| Resolution match | 2 | Point-georeferenced sample locations at meter precision when reported |
| Coverage | 0 | **Sparse in Iberia.** 8,486 samples globally but Mediterranean / Iberian density is low; brief flags this as an open question. Sample count for the Barcelona region is expected to be near zero |
| License | 2 | Open access per journal terms |
| Access reliability | 1 | Web portal is functional but less stable than GBIF; per-study downloads, no unified API |
| Bias clarity | 2 | Aggregated metabarcoding studies with documented sampling design per source study |
| Maintenance | 1 | v1 2023, no clear update cadence published |
| **TOTAL** | **10/14** | (resolution match is fine, but **coverage = 0 is a fatal axis** for our use case) |

### One-paragraph description

GlobalAMFungi is a global database of arbuscular mycorrhizal fungal occurrences from
high-throughput sequencing (DNA metabarcoding) studies. An instance is a soil sample
with georeferenced location, sample date, host vegetation context, and inferred AMF
community composition. This would be the *gold-standard* observed-fungi layer for AM
fungi specifically — exactly the fungi citizen-science misses — except that it is
sparse in Iberia. To be confirmed in profiling: are there any samples within or
adjacent to Barcelona? Even one sample within 50km would let us cite this as a
reference distribution.

### Verdict

**Investigate further** — query the database for samples within 100km of Barcelona
during profiling. If ≥3 samples in Catalonia, retain as **contextual reference**.
If zero, **reject** with a documented note that no AM-fungal DNA-based ground truth
exists for our area.

---

## 4. Ajuntament de Barcelona — Arbrat Viari + park-tree inventory

- **Provider:** Ajuntament de Barcelona (open data portal)
- **Access method:** Open Data BCN portal (`opendata-ajuntament.barcelona.cat`) — CSV / GeoJSON / Shapefile; quarterly snapshots; also queryable via CKAN API
- **Category:** built-environment

### Rubric scoring (0–2 per axis)

| Axis | Score | Justification |
|---|---|---|
| Provenance | 2 | Municipal data, used in multiple peer-reviewed BCN urban-ecology studies (e.g. Padullés Cubino et al. on tree diversity), well-documented metadata |
| Resolution match | 2 | Per-tree point data at meter precision — far finer than 400m |
| Coverage | 2 | Full city, 2015–present, quarterly updates; both street trees (~150,000) and park-tree inventory (separate dataset) |
| License | 2 | CC-BY 4.0 per BCN open-data terms |
| Access reliability | 2 | Stable open-data portal, multiple format exports, CKAN API |
| Bias clarity | 1 | Known: street-tree dataset only initially; park-tree inventory added later with possible coverage gaps in older park records; species-level taxonomy may default to genus for some entries (flagged as v1 brief open question) |
| Maintenance | 2 | Active; quarterly publication cadence |
| **TOTAL** | **13/14** | |

### One-paragraph description

The Ajuntament tree inventory is the canonical municipal record of every street tree
and park tree in Barcelona. An instance is a single tree with location (lat/lon),
species (when typed), genus, common name, planting date (variable completeness),
trunk diameter category, and address/park reference. Combined with FungalRoot v2.0,
it produces the *expected mycorrhizal type* layer that drives the brief's host-side
inference. Cannot tell us about tree health, root system extent, or whether the tree
has been replaced since the snapshot date.

### Verdict

**Adopt as PRIMARY** — full datasheet required. This is the load-bearing dataset for
the entire analysis.

---

## 5. OpenStreetMap + BCN open data (street network, building footprints)

- **Provider:** OSM Foundation (OSM); Ajuntament de Barcelona (BCN open data)
- **Access method:** Overpass API + Geofabrik regional extracts (OSM); BCN open-data portal (footprints, district / barrio boundaries, statistical sections)
- **Category:** built-environment

### Rubric scoring (0–2 per axis)

| Axis | Score | Justification |
|---|---|---|
| Provenance | 2 | OSM widely used in peer-reviewed urban-form studies; BCN open data municipal-source |
| Resolution match | 2 | Sub-meter vector data |
| Coverage | 2 | Full BCN, dense urban areas have very high OSM completeness |
| License | 1 | OSM under ODbL (share-alike — restrictive for derived databases distributed publicly); BCN under CC-BY. Mixed → 1 |
| Access reliability | 2 | Overpass + Geofabrik stable; BCN portal stable |
| Bias clarity | 1 | OSM completeness biases known (urban core dense, peri-urban sparser) but not quantified for BCN specifically |
| Maintenance | 2 | Both actively maintained |
| **TOTAL** | **12/14** | |

### One-paragraph description

OSM and BCN open-data layers provide the spatial framework on which everything else
sits — district boundaries, barri (neighborhood) polygons, statistical-section grids,
street network for inter-node distance calculations, building footprints for
proximity analysis. An instance is a vector feature (polygon for parcel/footprint,
linestring for road, point for amenity) with tagged attributes. Auxiliary throughout
the pipeline; not a primary observational dataset on its own.

### Verdict

**Adopt** — auxiliary / contextual, no separate datasheet (will be referenced inline
in system-sketch and methodology).

---

## 6. Copernicus Urban Atlas 2018 / 2021

- **Provider:** Copernicus Land Monitoring Service (European Environment Agency, ESA, EC)
- **Access method:** Copernicus Land Monitoring Service portal (`land.copernicus.eu`); free download after light registration; vector + 10m raster
- **Category:** built-environment (also flagged as land-use / earth-observation derived)

### Rubric scoring (0–2 per axis)

| Axis | Score | Justification |
|---|---|---|
| Provenance | 2 | Pan-European harmonised product; methodology peer-reviewed; used in dozens of urban-ecology and connectivity studies |
| Resolution match | 2 | 10m raster (sealed-surface fraction); ~minimum mapping unit 0.25 ha for change layer — finer than 400m grid |
| Coverage | 2 | Covers Barcelona Functional Urban Area for 2018 + 2021 vintages |
| License | 2 | Free for any use (commercial, research) per Copernicus terms |
| Access reliability | 2 | Stable downloads; new vintages every ~3 years |
| Bias clarity | 2 | Methodology + accuracy assessment published per vintage |
| Maintenance | 2 | Active CLMS programme |
| **TOTAL** | **14/14** | |

### One-paragraph description

Urban Atlas provides harmonised land-use / land-cover and sealed-surface fraction
across all European Functional Urban Areas. An instance is a polygon in the LU/LC
classification (residential continuous dense, urban green, sport+leisure, etc.) or
a 10m raster pixel of impervious-surface percentage. This is the canonical source
for our **sealed-surface input** to the fragmentation severity score; it also gives
us a categorical land-use layer for context. Cannot tell us about soil compaction,
contamination, or sub-pixel heterogeneity.

### Verdict

**Adopt** — auxiliary (could be promoted to secondary if we want a built-environment
datasheet alongside the biodiversity one). Sealed-surface fraction layer is critical
for the brief's scoring formula.

---

## 7. Sentinel-2 L2A (optical, 10m)

- **Provider:** ESA / Copernicus
- **Access method:** Copernicus Data Space Ecosystem (`dataspace.copernicus.eu`); also AWS Open Data, Google Earth Engine, Planetary Computer
- **Category:** remote-sensing-optical

### Rubric scoring (0–2 per axis)

| Axis | Score | Justification |
|---|---|---|
| Provenance | 2 | ESA mission, extensively peer-reviewed since 2015 |
| Resolution match | 2 | 10m visible/NIR — 40× finer than 400m |
| Coverage | 2 | 5-day revisit since 2017 (S-2A + S-2B); BCN covered by tile T31TDF |
| License | 2 | Free, no restrictions on use |
| Access reliability | 2 | Multiple stable redistributors (Copernicus, AWS, GEE, Planetary Computer) |
| Bias clarity | 2 | Cloud-cover documented per scene; atmospheric correction (L2A vs L1C) well-characterised; known issue: cloud-shadow false-positives in dense urban |
| Maintenance | 2 | Active mission, S-2C launched Sep 2024 |
| **TOTAL** | **14/14** | |

### One-paragraph description

Sentinel-2 L2A delivers atmospherically corrected surface reflectance imagery at 10m
visible/NIR resolution every 5 days. An instance is a multi-band scene tile. Used
here for **NDVI / EVI** as a vegetation-presence and condition proxy that
sanity-checks the tree inventory (catches cases where listed trees are missing,
dead, or where ungazetted vegetation is thriving). Cannot replace the tree inventory
because it cannot resolve species or distinguish street tree from understory.

### Verdict

**Adopt** — auxiliary (vegetation sanity-check layer); no separate datasheet
required unless we want to elevate it during profiling.

---

## 8. Landsat 8 / 9 thermal (LST)

- **Provider:** USGS / NASA
- **Access method:** USGS Earth Explorer, AWS Open Data, Google Earth Engine
- **Category:** remote-sensing-thermal

### Rubric scoring (0–2 per axis)

| Axis | Score | Justification |
|---|---|---|
| Provenance | 2 | NASA / USGS mission; standard reference for urban heat island studies |
| Resolution match | 2 | 100m native thermal (resampled to 30m in standard products) — 4× finer than 400m grid |
| Coverage | 2 | 16-day revisit since Landsat-8 (2013) + Landsat-9 (2021) combined effective ~8 days; BCN scene path/row 198/031 |
| License | 2 | USGS — public domain |
| Access reliability | 2 | Multiple stable redistributors |
| Bias clarity | 2 | Atmospheric correction + emissivity assumptions well-documented in product spec; known limitation: cloud occlusion |
| Maintenance | 2 | Active NASA mission |
| **TOTAL** | **14/14** | |

### One-paragraph description

Landsat 8/9 thermal infrared bands deliver land surface temperature retrievals at
100m native resolution. An instance is an LST raster scene. Used here as a **heat
stress proxy** — Mediterranean urban heat is well-documented as a soil-microbiome
stressor, and the v1 brief names it as a risk factor without quantifying it.
Combining Landsat LST with Sentinel-2 NDVI gives us defensible heat-vegetation
context per 400m grid cell. Cannot give us soil temperature directly — only land
surface temperature, which is a proxy with documented offsets.

### Verdict

**Adopt** — auxiliary (heat-stress context layer); no separate datasheet unless
elevated to a scored input in the priority formula.

---

## 9. ERA5-Land (Copernicus Climate Change Service)

- **Provider:** ECMWF / Copernicus C3S
- **Access method:** Climate Data Store API (`cds.climate.copernicus.eu`)
- **Category:** climate-reanalysis

### Rubric scoring (0–2 per axis)

| Axis | Score | Justification |
|---|---|---|
| Provenance | 2 | ECMWF reanalysis, peer-reviewed extensively |
| Resolution match | 0 | **9km native grid → ~22× COARSER than 400m decision unit. Fails the 2× rule by ~50×.** A single grid cell covers roughly half of Barcelona |
| Coverage | 2 | 1981–present, hourly, global |
| License | 2 | Copernicus terms, free for any use |
| Access reliability | 2 | CDS API stable |
| Bias clarity | 2 | Reanalysis methodology and known urban-scale biases (no explicit urban canopy modelling) documented in literature |
| Maintenance | 2 | Operational, daily updates with ~5-day latency |
| **TOTAL** | **10/14** | (10 is the rubric threshold but **resolution match = 0 is a fatal axis** for our per-zone scoring use case) |

### One-paragraph description

ERA5-Land is the high-resolution land-surface component of the ERA5 atmospheric
reanalysis, providing hourly fields of air temperature, precipitation, soil
moisture, evaporation, etc. on a 9km global grid. At the scale of Barcelona this is
~3 grid cells covering the entire municipality — useless for differentiating
Superilla zones. Useful only as a **city-wide context layer** (e.g. "summer 2023
was 1.8°C warmer than 1991–2020 baseline") to frame the v2 brief.

### Verdict

**Reject as primary or scored input** (resolution-match fatal). **Retain as
contextual only** — cite a single Barcelona-wide annual or summer-mean value in the
v2 brief's context paragraph; do not score per zone. This is exactly the kind of
documented rejection the rubric is designed to produce.

---

## 10. AEMET XEMA / Meteo.cat station network

- **Provider:** AEMET (Spanish meteorological agency); Meteo.cat / SMC (Catalan meteorological service)
- **Access method:** AEMET OpenData API (rate-limited, requires registration); Meteo.cat XEMA portal
- **Category:** in-situ-sensors

### Rubric scoring (0–2 per axis)

| Axis | Score | Justification |
|---|---|---|
| Provenance | 2 | National + regional meteorological agencies; quality-controlled observations |
| Resolution match | 0 | Point stations — ~5–10 stations within Barcelona metropolitan area. Effective interpolated resolution is much coarser than 400m given station density |
| Coverage | 1 | Good temporal coverage (sub-hourly); sparse spatial — not all districts have a station |
| License | 2 | AEMET data openly licensed (re-use permitted with attribution); Meteo.cat similar |
| Access reliability | 1 | AEMET API rate-limited; Meteo.cat XEMA download interface less standardised; no single unified bulk download |
| Bias clarity | 1 | Siting biases known (airports, official sites, parks) — documented but not quantified for BCN |
| Maintenance | 2 | Active operations, daily |
| **TOTAL** | **9/14** | |

### One-paragraph description

XEMA / AEMET station data give in-situ ground-truth meteorological observations at
sub-hourly cadence. An instance is a station × timestamp record (T, RH, precipitation,
wind, etc.). For our purposes the station density is too low to differentiate
Superilla zones — the network is built for regional weather, not intra-urban
microclimate. Useful only for ground-truthing satellite LST or ERA5 if we wanted to
go deep on heat; not a candidate for the scoring pipeline.

### Verdict

**Reject** — below 10/14 threshold; station density insufficient for our decision
unit.

---

## Summary

### Adopted (7)

| # | Source | Score | Role |
|---|---|---|---|
| 4 | Ajuntament BCN tree inventory | 13/14 | **PRIMARY** (full datasheet) |
| 1 | GBIF fungal occurrences | 12/14 | **SECONDARY** (full datasheet) |
| 2 | FungalRoot v2.0 | 12/14 | Auxiliary — host-fungus join table |
| 5 | OSM + BCN open data | 12/14 | Auxiliary — spatial framework |
| 6 | Copernicus Urban Atlas | 14/14 | Auxiliary — sealed-surface input |
| 7 | Sentinel-2 L2A | 14/14 | Auxiliary — vegetation sanity-check |
| 8 | Landsat 8/9 thermal | 14/14 | Auxiliary — heat stress context |

### Under investigation (1)

- **GlobalAMFungi (10/14)** — adopt as contextual reference *if* ≥3 samples exist
  within 100km of Barcelona; otherwise reject with a documented "no AM-fungal
  DNA ground truth exists for our area" note. To be confirmed in profiling.

### Rejected (2)

- **ERA5-Land (10/14)** — resolution match is fatal (9km vs 400m grid). 9km cell
  cannot differentiate Superilla zones. Retained only as a city-wide context line
  in the v2 brief.
- **AEMET XEMA (9/14)** — below threshold. Station density too sparse for our
  decision unit; retained only if we need to ground-truth satellite-derived
  thermal.

### Considered but not separately inventoried

- **iNaturalist research-grade fungi** — research-grade observations mirror to GBIF,
  so adopting both would double-count. Treated as a sub-stream of GBIF (#1) with
  a `basisOfRecord = HUMAN_OBSERVATION` filter when we need to isolate the
  citizen-science subset.

### Coverage gaps

Sub-questions / brief inputs that have *no* directly-adopted source:

- **Soil moisture / soil temperature at Superilla scale** — ERA5-Land rejected on
  resolution; no in-situ network at this density. Mitigation: use Sentinel-2 NDVI
  trend + Landsat LST as joint proxies; document the gap.
- **AM-fungal community composition (DNA-confirmed)** — GlobalAMFungi sparse in
  Iberia; pending profiling. If the gap is total, the brief is already revised
  (see `problem-brief-v2.md`) to *not claim network state* — the "observed" layer
  is treated as fruiting-body proxy, not network proxy.
- **Tree health / vitality** — neither tree inventory nor remote sensing
  reliably gives this at species precision. Not in current scope.

### Methodological note — peri-urban reference patch

The brief's revised framing (per `problem-brief-v2.md`) includes a single
**peri-urban reference patch** (~1km × 1km in Collserola or Garraf, similar
Mediterranean Quercus / Pinus habitat) used as a qualitative anchor for
observation-density contrast. This patch is **not a separate inventoried source**
— it reuses adopted data (GBIF fungal records + Urban Atlas land-use class)
applied to a different geography. The reference patch is explicitly N=1, used
qualitatively, not as a target zone. It addresses the citizen-science
geographic-skew confound documented in source #1's bias-clarity note.

---

## Sign-off

**Inventory survey covers all 6 seminar categories.** Adopted-source resolution
ranges from 10m (Sentinel-2, Urban Atlas) to per-tree point precision (Ajuntament
inventory) — all comfortably finer than the 400m decision unit. Two documented
rejections strengthen the artifact by showing the rubric was actually used to
discriminate.

**Last updated:** 2026-04-30
**Decision unit at time of scoring:** Superilla / 400m × 400m grid
