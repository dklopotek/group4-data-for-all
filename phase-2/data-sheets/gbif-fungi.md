# Dataset Datasheet — GBIF Fungal Occurrence Records (Catalonia / Barcelona, 2015–2024)

> Secondary dataset for the Mycorrhizal Barcelona project (Session 2,
> CRISP-DM Phase 2). Based on Gebru et al. 2021, "Datasheets for Datasets."

---

## 0. Quick reference

- **Dataset name:** GBIF occurrence records — Kingdom *Fungi*, geographic filter Catalonia (with Barcelona municipal subset), eventDate 2015-01-01 to 2024-12-31
- **Version / vintage:** GBIF download DOI to be generated at profiling time (DOI is per-download); index version date stamped on the download
- **Source URL:** `https://www.gbif.org/occurrence/search?country=ES&taxon_key=5&...` (filterable web search) and `https://api.gbif.org/v1/occurrence/search` (REST API for programmatic queries); bulk Darwin Core Archive available per download
- **License:** Per-record license; we filter to CC0 + CC-BY (excluding CC-BY-NC where redistribution is needed)
- **Spatial coverage:** Catalonia for the contextual query; Barcelona municipal boundary for the analytical subset; ~50–100km buffer used for the peri-urban reference patch
- **Temporal coverage:** 2015-01-01 to 2024-12-31 inclusive
- **Native resolution (spatial / temporal):** Point lat/lon at meter precision *when reported with low coordinate uncertainty*; precision varies per record (`coordinateUncertaintyInMeters` field). Temporal: per-event `eventDate`
- **Format:** Darwin Core Archive (TSV/CSV) for bulk download; JSON via REST API for ad-hoc queries
- **Size:** Estimated 200–800 records for Barcelona municipal subset 2015–2024 (to be confirmed in profiling); ~5,000–20,000 for Catalonia-wide
- **Datasheet last updated:** 2026-05-01 by [name]

---

## 1. Motivation

- **Why was the dataset created?**
  GBIF (the Global Biodiversity Information Facility) was created as the
  international biodiversity-data infrastructure to make species-occurrence
  data findable, accessible, interoperable, and reusable across natural
  history collections, citizen-science platforms, surveys, and research
  outputs. It does not collect data itself; it aggregates and standardises.

- **Who created the dataset (individuals, organizations)?**
  GBIF Secretariat (intergovernmental, hosted in Copenhagen) operates the
  index. ~2,000 publishing institutions contribute the underlying records.
  For our subset, the dominant contributors are: iNaturalist
  research-grade observations (citizen science), national / regional
  herbaria and natural-history museums (specimen collections), and
  university / research-group survey datasets.

- **Who funded the creation of the dataset?**
  GBIF is funded by member-country contributions. Underlying record
  collection is funded by each publishing institution independently.

- **For what tasks was the dataset originally intended?**
  Biodiversity research, conservation policy, species-distribution
  modelling, taxonomic and biogeographic studies, ecology research broadly.

---

## 2. Composition

- **What does an instance represent?**
  A single occurrence record — one observation or specimen of an organism
  at one georeferenced location at one time, with provenance back to the
  publishing dataset.

- **How many instances are there in total?**
  Whole index: ~2 billion globally. Our planned subset (Kingdom Fungi,
  Barcelona municipality, 2015–2024) is estimated at 200–800 records and
  is the load-bearing unknown for our profiling — this is one of the
  v2-brief's open questions.

- **What features / fields does each instance have?** *(Darwin Core
  standard, selected fields)*

| Field | Type | Description | Required? |
|---|---|---|---|
| `gbifID` | string | Unique GBIF identifier | Yes |
| `scientificName` | string | Full scientific name (taxon) | Yes |
| `kingdom`, `phylum`, `class`, `order`, `family`, `genus`, `specificEpithet` | string | Taxonomic hierarchy | Mostly |
| `decimalLatitude`, `decimalLongitude` | float | WGS-84 coordinates | Mostly (but some records lack them) |
| `coordinateUncertaintyInMeters` | float | Reported coordinate uncertainty | Variable |
| `eventDate` | date / datetime | Observation date / time | Mostly |
| `basisOfRecord` | enum | HUMAN_OBSERVATION / PRESERVED_SPECIMEN / MATERIAL_SAMPLE / etc. | Yes |
| `recordedBy` | string | Observer / collector | Variable |
| `datasetKey` | string | UUID linking to publishing dataset | Yes |
| `license` | enum | CC0 / CC-BY / CC-BY-NC | Yes |
| `occurrenceStatus` | enum | PRESENT / ABSENT (almost always PRESENT for fungi citizen-sci) | Yes |
| `establishmentMeans` | enum | NATIVE / INTRODUCED / etc. (when reported) | Variable |
| `taxonRank` | enum | SPECIES / GENUS / FAMILY (etc.) — granularity of identification | Yes |

- **Are there labels or targets associated with each instance?**
  No labels in the ML sense. The taxon is the primary attribute.

- **Is any information missing from instances?**
  - Some records lack coordinates entirely (record may have only a verbal
    locality).
  - `coordinateUncertaintyInMeters` is often missing — when it is, treat
    cautiously; we will filter to records with explicit uncertainty
    ≤100m for the priority-map analysis.
  - Identification rank varies; many citizen-sci records are genus-only.
  - Phenological state (fruiting body vs vegetative) is rarely recorded
    for fungi but is *crucial* — we treat all visible fungal records as
    fruiting-body observations by basis-of-record convention.

- **Are there relationships between individual instances?**
  Records sharing a `datasetKey` come from the same publishing dataset
  (e.g. one museum's specimen collection). Records from the same
  observer (`recordedBy`) may cluster spatially / temporally.

- **Are there recommended data splits (train/val/test)?**
  N/A.

---

## 3. Collection process

- **How was the data acquired?**
  Aggregated from publishing datasets — most are *not* primary collection
  by GBIF. For our subset, the dominant collection modes are: (i)
  citizen-science observation via iNaturalist (smartphone photo,
  community ID, automatic mirror to GBIF when "research grade"), (ii)
  herbaria / museum specimen records (often historical, georeferenced
  retrospectively), (iii) targeted ecological survey datasets.

- **What instruments / sensors / software were used?**
  Smartphone cameras + iNaturalist app for citizen-sci; field collection
  + lab identification for specimens; varies for surveys.

- **Who was involved in the data collection process?**
  For Barcelona: predominantly iNaturalist users and some Catalan / Spanish
  mycology associations. Specimen records trace back to natural-history
  collection curators.

- **Over what time period was the data collected?**
  We filter to `eventDate` 2015-01-01 to 2024-12-31. Underlying records
  may have collection dates outside this window if they are specimens
  later digitised; we filter on event date, not digitisation date.

- **What was the sampling strategy?**
  **Opportunistic** — citizen-science observations occur where humans go,
  during seasons when fruiting bodies are visible (autumn-heavy), and
  conditional on phone-camera-and-app technology adoption. This is
  emphatically *not* probabilistic sampling. Specimen records reflect
  historical collection priorities of the institutions involved.

- **Is the sample representative of the larger population it claims to
  describe?**
  **No.** Multiple severe biases are documented in the literature:
  - **Geographic skew toward accessible / high-foot-traffic areas.**
  - **Phenological skew toward fruiting-body season** (typically autumn
    in Mediterranean climate).
  - **Taxonomic skew toward visible, identifiable groups** —
    ectomycorrhizal and saprotrophic fungi over-represented;
    arbuscular mycorrhizal fungi essentially absent (no visible fruiting
    body to photograph).
  - **Observer skew** toward enthusiast taxa (boletes, *Amanita*,
    morels) over inconspicuous taxa.
  These are not minor caveats; they are foundational characteristics of
  the dataset for our project.

- **Were any ethical review processes conducted?**
  Per-publishing-dataset; iNaturalist users consent to data publication
  on platform sign-up. No human-subjects concerns.

---

## 4. Preprocessing & cleaning

- **What preprocessing was done by the dataset creators?**
  GBIF normalises Darwin Core records, runs taxonomic name matching
  against the GBIF Backbone Taxonomy, performs basic coordinate validity
  checks (in-water flags, equator-prime-meridian outliers, etc.), and
  applies country/admin-boundary cross-checks. iNaturalist applies
  community-vote "research grade" verification before mirroring records
  to GBIF.

- **Is the raw data also available?**
  Per-publishing-dataset — depends on each publisher. iNaturalist data
  remains accessible on iNaturalist itself with photos.

- **What preprocessing did WE do before adopting the dataset?**
  *(Detailed in `notebooks/01-data-profiling.ipynb`.)* Planned:
  (i) filter to Kingdom *Fungi*, Catalonia (then Barcelona subset),
  eventDate 2015–2024;
  (ii) keep only records with `decimalLatitude/Longitude` present and
  `coordinateUncertaintyInMeters` either missing or ≤100m;
  (iii) deduplicate against `gbifID`;
  (iv) classify by `basisOfRecord` (HUMAN_OBSERVATION vs PRESERVED_SPECIMEN
  vs others) for downstream weighting / filtering;
  (v) compute observation-density per 400m grid cell (urban target) and
  for the peri-urban reference patch.

- **Where is the preprocessing software / code available?**
  `notebooks/01-data-profiling.ipynb` (this repo). The GBIF download DOI
  is recorded for citation.

---

## 5. Uses

- **What tasks has the dataset been used for?**
  Biodiversity assessment, species-distribution modelling, climate-shift
  ecology, conservation prioritisation, taxonomic studies. GBIF underlies
  thousands of peer-reviewed papers per year; the citation list is
  generated automatically per dataset DOI.

- **Is there a repository linking to papers / systems that use this
  dataset?**
  Yes — GBIF tracks citations per download DOI. Each download is citable.

- **What other tasks could this dataset be used for?**
  Citizen-science engagement metrics; phenology trend studies (with care);
  invasive-species early warning; macro-ecological pattern analysis.

- **What tasks should this dataset NOT be used for?**

  1. **Inferring presence or absence of arbuscular mycorrhizal (AM)
     fungi at any location.** AM fungi do not produce visible fruiting
     bodies and are essentially absent from the citizen-science portion
     of GBIF. A *zero* fungal record at a location does not mean *no
     fungi* — it means *no visible fruiting body was observed by a
     citizen scientist*.
  2. **Quantitative comparison of fungal abundance between
     observation-rich and observation-poor neighborhoods without
     correcting for observation effort.** Apparent abundance differences
     are confounded by foot traffic, urbanity, and observer-population
     density. Correction requires either a reference/control area (which
     this project uses via the peri-urban reference patch) or an
     explicit observer-effort model.
  3. **Phenology claims at fine temporal resolution in low-record-count
     areas.** Sample size for Barcelona-municipal Fungi 2015–2024 is
     too small to support per-month or per-week phenological inferences.

- **Are there any considerations about discrimination, bias, or harm
  that could result from use of this dataset?**
  The geographic-skew bias intersects with socioeconomic geography:
  citizen-science participation is uneven across neighborhoods and may
  correlate with income, age, and access to outdoor green space. Using
  this dataset to allocate any kind of public investment without
  correcting for the skew would systematically disadvantage areas with
  lower observer participation — an equity concern relevant to our
  project's barrier-reduction-priority framing. Mitigation: the project
  does *not* use GBIF density as a barrier sub-score input. GBIF is used
  as observation-context only, with the peri-urban reference patch as
  the anchor.

---

## 6. Distribution & licensing

- **Under what license is the dataset distributed?**
  Per-record. CC0, CC-BY 4.0, and CC-BY-NC 4.0 are the dominant licenses
  in the index. Our query filters records to redistributable licenses
  (CC0 + CC-BY) for downstream redistribution; CC-BY-NC records can be
  *consulted* but should not be re-shared in derived datasets without
  per-record review.

- **Are there any restrictions on use, redistribution, attribution, or
  modification?**
  CC-BY records require attribution; CC0 has no restrictions. We
  generate the GBIF citation string per download DOI and reproduce it in
  the priority-map output.

- **What's the required attribution string?**
  > GBIF Occurrence Download DOI: [generated at download time]. Cite
  > as: GBIF.org (YYYY) GBIF Occurrence Download
  > https://doi.org/[DOI-from-download]
  Plus per-record dataset attribution where licensed CC-BY.

- **Are there fees for access?**
  No.

- **Are there export controls or regulatory restrictions?**
  No.

---

## 7. Maintenance

- **Who supports / hosts / maintains the dataset?**
  GBIF Secretariat (Copenhagen) for the index; ~2,000 publishing
  institutions for individual records.

- **How can the maintainer be contacted?**
  GBIF helpdesk via gbif.org; per-dataset contact via each publisher.

- **Is there an erratum?**
  Per-dataset corrections appear when publishers re-issue. The GBIF
  Backbone Taxonomy receives corrections that re-map names.

- **Will the dataset be updated?**
  Yes — daily aggregation; new records constantly added.

- **How often is the dataset updated?**
  Continuously; the index reflects the publishing-dataset state with
  some lag.

- **Are older versions of the dataset still available?**
  Each download DOI freezes a specific snapshot — those snapshots remain
  citable indefinitely. This is critical for reproducibility: we cite
  the DOI of *our* download, not a moving "GBIF as of today" reference.

---

## 8. Limitations relative to OUR project

*The most important section for the seminar. How does this dataset's
character intersect with our problem brief?*

- **Resolution mismatch with our decision unit?**
  None at the spatial axis — point coordinates are far finer than 400m
  grid. **But the *effective* resolution is sample-size-limited:** with
  ~200–800 records across 100+ km² of Barcelona over a decade, density
  is ~2–8 records/km²/decade, which is sparse at the 400m grid.

- **Geographic gaps that matter for us?**
  Citizen-science geographic skew. Areas with low observer activity
  produce few records *regardless* of underlying ecology. This is the
  primary reason GBIF density is *not* a barrier sub-score input in the
  Shape-C framing — the reference patch is the methodological response.

- **Temporal gaps that matter for us?**
  Citizen-sci is autumn-heavy in Mediterranean climates. We aggregate
  across the full 2015–2024 window so the seasonal pattern washes out at
  the analysis level, but it remains relevant for any sub-claim about
  fungal dynamics.

- **Biases that could distort our conclusions?**
  - **AM-blindness** (no visible fruiting bodies) — load-bearing limit.
  - **Geographic skew** (foot-traffic and observer-density confound).
  - **Taxonomic skew** toward enthusiast taxa.
  These are why the Shape-C framing does *not* use GBIF as a primary
  signal; it is observation context with a reference-patch anchor.

- **What additional sources would compensate for these limits?**
  - **GlobalAMFungi** would compensate for AM-blindness — if Iberian
    samples exist (pending profiling). If not, this gap is total and
    documented.
  - The peri-urban reference patch addresses the geographic skew
    qualitatively.
  - There is no good fix for taxonomic skew at our scope.

- **Verdict for our project:**
  **SECONDARY** — used for observation-context, peri-urban reference
  comparison, and to validate the methodological framing's "AM-blindness"
  claim with concrete numbers from profiling. **Not** an input to any
  barrier sub-score.
