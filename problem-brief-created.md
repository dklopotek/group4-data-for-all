# Problem Brief — Mapping Mycorrhizal Network Fragmentation for Habitat Corridor Design in Barcelona

> This document is the project's **purpose document.**
> Every other deliverable in the seminar references this.

---

## The Environmental Question

How fragmented is Barcelona's belowground fungal community across its public green
infrastructure (parks and street trees), and which urban zones show the largest gap
between where mycorrhizal partners are *expected* (inferred from host tree species)
and where fungi are actually *recorded* — flagging candidate locations for soil-aware
corridor intervention?

We use mycorrhizal fungi as a partial proxy for soil ecosystem condition. A corridor
that looks connected aboveground can be functionally weaker belowground if soil sealing,
compaction, heavy-metal contamination, or edge effects have degraded the host-fungus
relationship. Standard corridor planning rarely uses this signal. We treat the proxy
as diagnostic-with-caveats, not as ground truth — see Risks.

---

## The Design Decision This Supports

Barcelona is iterating on its green-infrastructure strategy, including the ongoing
Superilla (Superblock) and Eixos Verds programmes that introduce new planting and
de-paved zones. Planners must decide *where* to prioritise corridor plantings and
soil-remediation spend to improve ecological connectivity, not just visual greenness.

The project produces a spatially explicit, ranked map of zones where the host-fungus
signal is weakest, paired with a written list of the assumptions behind each ranking,
so planners can defend the prioritisation in district-level decisions and capital
documents.

---

## The Intended User

Urban planning analysts and landscape architects at **Barcelona Regional** (the
municipal urban-development agency that absorbed the former Agència d'Ecologia Urbana
de Barcelona when it was dissolved in 2020) and the **Ajuntament de Barcelona's
Espais Verds i Biodiversitat** team. These users work with GIS and municipal spatial
data but are not mycologists or soil ecologists. The output must read as a priority
map with a one-page scoring rationale and an explicit list of what the map cannot
claim.

---

## Candidate Data Sources

| Dataset | What it provides | Access |
|---|---|---|
| **Ajuntament BCN Open Data — Arbrat Viari + park-tree inventory** | Street trees and park trees with species and location, quarterly updates 2015–present | Public, open |
| **GBIF fungal occurrences** (Barcelona / Catalonia, 2015–2024) | Aboveground fungal records — predominantly fruiting bodies | Free API |
| **iNaturalist research-grade fungi** (mirrored to GBIF) | Citizen-science sightings; visible mushrooms only, biased toward ectomycorrhizal taxa | Via GBIF |
| **FungalRoot v.2.0** (Soudzilovskaia et al., 2022, *New Phytologist*) | Plant-to-mycorrhizal-*type* lookup for ~14,870 species — type only, not colonisation intensity | Open |
| **GlobalAMFungi** (Větrovský et al., 2023) | AM-fungal DNA metabarcoding from 8,486 georeferenced samples; sparse in Iberia | globalamfungi.com |
| **OSM + Barcelona open data** | Street network, building footprints, sealed-surface mapping | Public |

**Methodology note:** Direct mycorrhizal-network observation in Barcelona is not
available, and existing fungal records are mostly aboveground fruiting bodies — which
arbuscular mycorrhizal fungi (the dominant partners for *Platanus*, *Tilia*, *Celtis*
and other common Barcelona street trees) do not produce visibly. The pipeline therefore
operates on a host-side inference:

1. Use the city's tree inventory + FungalRoot to infer the *expected* mycorrhizal
   type at each green node (park or street-tree cluster).
2. Overlay GBIF + iNaturalist records to identify zones that are *under-observed*
   relative to host expectation — explicitly noting this captures fruiting-body
   sparsity, not network collapse.
3. Score zones by fragmentation severity using sealed-surface fraction, urban density,
   and inter-node distance as additional variables.
4. Rank zones and output a priority candidate map, paired with a written limitations
   sheet.

---

## Measurable Success Criteria

1. The pipeline (ingestion → scoring → map) is reproducible from the repository in
   under 30 minutes after the one-off data download, with no manual steps.
2. Every Barcelona district (10 total) has at least one scored zone — no district is
   silently excluded by data gaps. Any deliberate exclusion is stated.
3. Output is a shortlist of ≤15 priority zones, each with its score, the inputs that
   produced it, and the assumptions it depends on.
4. A non-ecologist planner can read the one-page methods summary and correctly state
   at least three things the map *cannot* claim.
5. Output is sanity-checked against at least one named existing green axis in
   Barcelona's current planning documents (e.g. an Eix Verd along Consell de Cent or
   Pi i Margall) to confirm the ranking is not arbitrary.

---

## Risks and Open Questions

**Risks:**

- The "common mycorrhizal network" framing the project leans on is contested.
  Karst, Jones & Hoeksema (2023, *Nature Ecology & Evolution*) show much of the
  popular wood-wide-web evidence base is over-interpreted. Network-level claims
  must be hedged accordingly, not stated as established fact.
- iNaturalist and GBIF fungal records skew strongly toward visible fruiting bodies,
  i.e. ectomycorrhizal and saprotrophic taxa. AM fungi — the dominant partners
  for many of Barcelona's street-tree genera — are essentially invisible to
  citizen science, so the "observed" layer systematically undercounts the
  mycorrhizal type that matters most here.
- FungalRoot returns mycorrhizal *type*, not colonisation intensity, viability,
  or network connectivity. The expected layer is a categorical proxy.
- Urban Barcelona soils are heavily modified (compaction, contamination,
  irrigation regime), weakening the tree-presence-to-functional-mycorrhiza link
  relative to less disturbed systems.
- Districts with lower human foot traffic will under-record citizen-science fungi
  for reasons unrelated to ecology — the model could mistake observation deserts
  for fragmentation hotspots.
- The Superilla / Eixos Verds rollout changes the green network during the
  2015–2024 window, introducing temporal inconsistency in the tree data.

**Open questions for next session (Data Understanding):**

- Actual GBIF fungal record count for the Barcelona municipal boundary, 2015–2024
  — above 500, or below 100?
- Does Ajuntament tree data carry consistent species-level taxonomy, or is genus
  the realistic join key against FungalRoot?
- Is GlobalAMFungi sample density in the Iberian Peninsula sufficient to use as
  reference, or is it dominated by Northern / Central European samples?
- Does the Ajuntament publish soil sealing / impervious surface data at a
  resolution useful for sub-district corridor analysis?

---

## Out of Scope

- No soil sampling or field collection — desk-based spatial analysis only.
- No species-level fungal distribution modelling — we work at mycorrhizal-type
  and zonal level, not species level.
- No analysis outside the Barcelona municipal boundary.
- No species recommendations for new plantings — only zonal prioritisation.
- No real-time data feeds — snapshot of 2015–2024 archived data.

---

## Key References

- Karst, J., Jones, M.D. & Hoeksema, J.D. (2023). Positive citation bias and overinterpreted results lead to misinformation on common mycorrhizal networks in forests. *Nature Ecology & Evolution* 7, 501–511. doi:10.1038/s41559-023-01986-1
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
