# Problem Brief — Mapping Barrier-Reduction Priority for Belowground Ecological Recovery in Barcelona

> This is the working brief, **revised after Session 2 (Data Understanding)**.
> Original v1 framed the question around mapping "mycorrhizal network
> fragmentation." Data realities forced a revision toward what the data can
> actually support: a **barrier-reduction priority map**, identifying where
> interventions targeting known, measurable barriers to belowground
> ecological recovery deliver highest leverage per capital euro spent. See
> `problem-brief-v2.md` for the changelog explaining *why*.

---

## The Environmental Question

For each Superilla-scale zone (~400m × 400m) in Barcelona, **where do known
barriers to belowground ecological recovery — sealed surface, heat anomaly,
low canopy, and host–mycorrhizal mismatch — concentrate, such that
barrier-reduction interventions (de-paving, urban cooling, new planting,
mycorrhizally-compatible species selection) deliver the highest expected
leverage per € of capital spend?**

**Why this framing, not the v1 framing:**

The v1 brief asked "where is the belowground fungal community most
fragmented?" That question implicitly requires *measuring* the fungal
community — which the available data cannot support in dense urban
Barcelona. AM fungi (the dominant partners for *Platanus*, *Tilia*, *Celtis*
and other common BCN street trees) are invisible to citizen science, and
DNA-based metabarcoding reference data is essentially absent in Iberia.

The revised framing asserts a tighter, more honest claim: **belowground
ecological recovery requires the absence of certain known barriers (compacted
sealed surfaces, extreme heat, missing host canopy, host–partner mismatch)
— and we can directly map those barriers per zone, rank intervention
leverage, and tie each intervention type to an existing Ajuntament budget
line.** The output does not claim to map a network or predict recovery
outcomes; it claims to identify where capital spending on barrier-reduction
has highest expected leverage.

This framing preserves the project's underlying motivation — that
belowground ecology matters for urban resilience — while only making claims
the data can support.

---

## The Design Decision This Supports

Barcelona is iterating on its green-infrastructure strategy through the
**Superilla (Superblock)** and **Eixos Verds** programmes — both of which
include capital lines for:

- **De-paving** of selected streets and block interiors
- **Structural-soil** intervention beneath new plantings
- **New tree plantings** (species selection)
- **Urban cooling** (canopy + green-axis prioritisation)

The project produces a spatially explicit, ranked priority map of zones
where the combined barrier index is highest, **with an intervention-type
recommendation per zone** (de-paving / planting / species selection /
combined). This lets planners route capital toward the zones where each
specific budget line delivers most leverage.

---

## The Intended User

Urban planning analysts and landscape architects at **Barcelona Regional**
(the municipal urban-development agency that absorbed the former Agència
d'Ecologia Urbana de Barcelona when it was dissolved in 2020) and the
**Ajuntament de Barcelona's Espais Verds i Biodiversitat** team. These users
work with GIS and municipal spatial data but are not mycologists or soil
ecologists. The output must read as a priority map with a one-page scoring
rationale, an intervention-type recommendation per zone, and an explicit
list of what the map cannot claim.

---

## Sub-questions

1. **Per zone, what mycorrhizal type does the host tree composition lead us
   to expect (AM / EM / mixed)?** *(tree inventory + FungalRoot v2.0 lookup)*
   → Informs **species-selection** intervention.

2. **Per zone, what is the sealed-surface fraction?** *(Urban Atlas 10m)*
   → Informs **de-paving** intervention.

3. **Per zone, what is the heat anomaly relative to the city baseline?**
   *(Landsat 8/9 LST)*
   → Informs **urban cooling / canopy** intervention.

4. **Per zone, what is the canopy / NDVI?** *(Sentinel-2 L2A)*
   → Informs **new-planting** intervention.

5. **Per zone, is there host–mycorrhizal mismatch — i.e. existing host trees
   without spatially-adjacent citizen-science confirmation, or zones where
   the host composition is mycorrhizally inconsistent (mixed AM/EM where
   neither dominates)?**
   → Informs **species-selection** intervention.

6. **Combined: which zones rank highest on the multi-barrier composite, and
   which intervention type is the top per-zone recommendation?**

7. *(Methodological anchor)* **How does the peri-urban reference patch's
   barrier index compare to urban core?** Establishes a "what low-barrier
   looks like" baseline for the urban map.

---

## Adopted Data Sources

(Survey and rubric scoring in `docs/data-source-inventory.md`. Two adopted
datasets get full datasheets; auxiliary sources are referenced inline.)

| Dataset | Role | Datasheet |
|---|---|---|
| Ajuntament BCN Arbrat Viari + park-tree inventory | **Primary** — host-side input for expected mycorrhizal type & host-mismatch | `datasheets/ajuntament-trees.md` |
| GBIF fungal occurrences (Catalonia, 2015–2024) | **Secondary** — observation context (used carefully given AM-blindness) | `datasheets/gbif-fungi.md` |
| FungalRoot v2.0 (Soudzilovskaia et al. 2022) | Auxiliary — host-to-mycorrhizal-type lookup | inline citation |
| OSM + BCN open data | Auxiliary — geographic framework, district boundaries | inline citation |
| Copernicus Urban Atlas 2018/2021 | Auxiliary — sealed-surface fraction (de-paving leverage) | inline citation |
| Sentinel-2 L2A | Auxiliary — NDVI canopy proxy (new-planting leverage) | inline citation |
| Landsat 8/9 thermal | Auxiliary — LST heat anomaly (cooling leverage) | inline citation |

Rejected after rubric scoring: ERA5-Land (resolution mismatch fatal at 9km),
AEMET XEMA station network (sparse station density). GlobalAMFungi pending
profiling-time check on Iberian sample density.

---

## Measurable Success Criteria

1. The pipeline (ingestion → barrier scoring → priority map +
   intervention-type recommendations) is reproducible from the repository in
   under 30 minutes after the one-off data download, with no manual steps.

2. Every Barcelona district (10 total) has at least one scored zone — no
   district is silently excluded by data gaps. Any deliberate exclusion is
   stated.

3. Output is a shortlist of **≤15 priority zones**, each with: priority
   rank, expected mycorrhizal type, four sub-scores (sealed surface, heat,
   NDVI, host mismatch), the **top-recommended intervention type**, and the
   assumptions it depends on.

4. A non-ecologist planner can read the one-page methods summary and
   correctly state at least three things the map *cannot* claim.

5. Output is sanity-checked against at least one named existing green axis
   in Barcelona's current planning documents (e.g. an Eix Verd along
   Consell de Cent or Pi i Margall) to confirm the ranking is not arbitrary.

6. **A peri-urban reference patch** (Collserola or Garraf, ~1km², similar
   habitat) is included as a qualitative anchor — its barrier index
   establishes what "low-barrier" looks like for the urban map.

7. Each of the four intervention types maps to a documented Ajuntament /
   Barcelona Regional budget line (Eixos Verds / Superilla / planting
   programme / cooling strategy). If a barrier has no corresponding budget
   line, the gap is explicitly flagged in the output.

---

## Risks and Open Questions

**Risks:**

- AM fungi are essentially invisible to citizen science. The host-mismatch
  sub-score is therefore an *expectation* metric, not an *observation*
  metric: it asks "do the host trees here have known partners that *should*
  be present somewhere," not "are those partners actually present." This
  is documented as a limit; the brief deliberately does not claim
  observation of AM communities.

- FungalRoot returns mycorrhizal *type*, not colonisation intensity,
  viability, or partner identity. The expected-type layer is a categorical
  proxy.

- Urban Barcelona soils are heavily modified (compaction, contamination,
  irrigation regime), weakening any tree-presence-to-functional-mycorrhiza
  link relative to less disturbed systems. The barrier-reduction framing
  works *with* this fact, not against it: we are explicitly mapping where
  modification is most severe.

- **Intervention efficacy is not validated within a planning cycle.** Soil
  microbial community recovery timescales are 5–20+ years; this map
  identifies *where leverage is highest*, not *where outcomes are
  guaranteed*. Documented as a limit; output explicitly states this.

- The Superilla / Eixos Verds rollout changes the green network during the
  2015–2024 window, introducing temporal inconsistency in the tree data.

- Districts with lower human foot traffic will have lower citizen-science
  fungal records for reasons unrelated to ecology. Mitigated by the
  peri-urban reference patch and by treating the GBIF layer as
  observation-density context, not as a barrier sub-score input.

**Open questions for next session (Data Preparation):**

- Actual GBIF fungal record count for the Barcelona municipal boundary,
  2015–2024 — above 500, or below 100?
- Does Ajuntament tree data carry consistent species-level taxonomy, or is
  genus the realistic join key against FungalRoot?
- Does any GlobalAMFungi sample exist within 100km of Barcelona that could
  serve as a contextual reference?
- What is the peri-urban reference patch's barrier index relative to the
  urban core's median?
- For each intervention type, what is the documented Ajuntament budget line
  and decision cycle? (Required for criterion 7.)

---

## Out of Scope

- **No claim that barrier-reduction will produce mycorrhizal network
  formation, recovery, or strengthening.** The output identifies leverage,
  not outcome.
- **No claim of belowground network state, connectivity, or
  "fragmentation."** This is not a connectivity map.
- No soil sampling or field collection — desk-based spatial analysis only.
- No species-level fungal distribution modelling — we work at
  mycorrhizal-type and zonal level, not species level.
- No analysis outside the Barcelona municipal boundary, *except* the single
  named peri-urban reference patch used as a qualitative low-barrier
  anchor.
- No specific tree-species recommendations are produced — only the
  mycorrhizal-type expectation layer that supports planners' species
  selection within their existing protocols.
- No real-time data feeds — snapshot of 2015–2024 archived data.

---

## Key References

- Soudzilovskaia, N.A. et al. (2022). FungalRoot v.2.0 — an empirical database of plant mycorrhizal traits. *New Phytologist*. doi:10.1111/nph.18207
- Steidinger, B.S. et al. (2019). Climatic controls of decomposition drive the global biogeography of forest-tree symbioses. *Nature* 569, 404–408. doi:10.1038/s41586-019-1128-0
- Tedersoo, L. et al. (2014). Global diversity and geography of soil fungi. *Science* 346, 1256688. doi:10.1126/science.1256688
- Větrovský, T. et al. (2023). GlobalAMFungi: a global database of arbuscular mycorrhizal fungal occurrences from high-throughput sequencing metabarcoding studies. *New Phytologist*. doi:10.1111/nph.19283

---

## Team

| Name | Role on this project |
|---|---|
| [ ] | Decomposition lead — breaks goal into analytical components |
| [ ] | Data lead — locates, audits, and prepares data sources |
| [ ] | Prompt lead — directs and iterates with the AI engineer |
| [ ] | Verification lead — challenges outputs and validates logic |

> Roles are loose — they help divide work, not lock anyone in.
> Everyone reads everyone's code. Everyone defends every line.
