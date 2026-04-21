# Problem Brief — Mapping Mycorrhizal Network Fragmentation for Habitat Corridor Design in Barcelona

> This document is the project's **purpose document.**
> Every other deliverable in the seminar references this.

---

## The Environmental Question

How fragmented is Barcelona's belowground mycorrhizal network across its full green infrastructure
(parks and street trees), and which urban zones show the greatest disconnect between where
mycorrhizal networks *should* exist (inferred from host tree distribution) and where fungal
activity is actually *observed* — indicating the highest priority locations for habitat corridor
intervention?

This question uses mycorrhizal fungi as a diagnostic proxy for belowground ecosystem health.
A corridor that looks connected above ground may be functionally severed underground if the
fungal network that sustains its trees has collapsed due to urban fragmentation, soil sealing,
heavy metal stress, or edge effects. Standard corridor planning does not currently account for this.

---

## The Design Decision This Supports

Barcelona's urban planning office is continuously updating its green infrastructure strategy,
including the ongoing Superblock (Superilla) programme which redesigns street-level space
and introduces new planting zones across the city. Planners need to decide *where* to
prioritise new corridor plantings and soil remediation efforts to maximise ecological
connectivity — not just visual greenness.

This project gives planners a spatially explicit, ranked map of zones where mycorrhizal
network fragmentation is most severe, so that new corridor placements restore actual
biological infrastructure rather than just adding isolated green patches that remain
functionally disconnected at the soil level.

---

## The Intended User

Urban planning analysts and landscape architects at the **Barcelona Urban Ecology Agency
(Agència d'Ecologia Urbana de Barcelona)** and the **Ajuntament de Barcelona's Espais Verds
department**. These users are familiar with GIS, municipal spatial data, and green
infrastructure planning. They are not mycologists or soil ecologists. The output must be
readable as a spatial priority map with a clear scoring rationale they can defend to
district-level decision makers and justify in capital planning documents.

---

## Candidate Data Sources

| Dataset | What it provides | Access |
|---|---|---|
| **Barcelona Biodiversity Atlas** (Ajuntament BCN) | 200,000+ georeferenced trees, 400+ species, NDVI, habitat classifications | Public, open |
| **GBIF occurrence records** — fungi, filtered to Barcelona / Catalonia | Direct fungal observation points, 2015–2024 | Free API |
| **iNaturalist research-grade observations** — fungi, Barcelona | Citizen science fungal sightings with coordinates | Via GBIF or direct API |
| **FungalRoot database** (Soudzilovskaia et al., 2020, via GBIF) | Plant-to-mycorrhizal-type lookup for 14,870 plant species — the inference bridge layer | Open, GBIF-hosted |
| **GlobalAMFungi database** (Větrovský et al., 2023) | ~50M AM fungal DNA sequences from 8,500 georeferenced samples | Open access |
| **OpenStreetMap / Barcelona open data** | Street network, building footprints, sealed surface mapping | Public |

**Methodology note:** Direct fungal occurrence records in Barcelona will be sparse.
The core analytical strategy is therefore:

1. Use the Barcelona tree database + FungalRoot to infer *expected* mycorrhizal network
   presence at each green node (park or street tree cluster)
2. Overlay with actual GBIF/iNaturalist fungal observations to identify where
   observations fall significantly below expectation
3. Score each zone by fragmentation severity using urban density, sealed surfaces,
   and distance between green nodes as additional variables
4. Rank zones and output as a priority corridor map

---

## Measurable Success Criteria

1. The full pipeline (data ingestion → fragmentation scoring → map output) is reproducible
   from the repository by a non-author in under 15 minutes with no manual steps
2. Every Barcelona district (10 total) has at least one scored zone in the output — no
   district is missing from the analysis due to data gaps
3. The ranked map produces a shortlist of ≤15 priority corridor zones with explicit
   fragmentation scores, each traceable back to the input data
4. The methodology can be clearly explained to a non-ecologist in a single page —
   a planner must be able to state what the map can and cannot claim
5. Output is validated against at least one existing known ecological corridor or
   green axis in Barcelona (e.g. Collserola–Ciutadella axis) to confirm the model
   is not producing nonsense rankings

---

## Risks and Open Questions

**Risks:**

- Fungal occurrence data for Barcelona in GBIF/iNaturalist may be too sparse in certain
  districts to distinguish genuine absence from observation gaps — the model could
  flag data deserts as fragmentation hotspots
- FungalRoot provides mycorrhizal *type* per plant species but not intensity or
  viability — the inference layer is probabilistic, not empirical
- Barcelona's urban soils are heavily modified (compaction, contamination, irrigation);
  the relationship between tree presence and functional mycorrhizal networks may be
  weaker than in less disturbed cities
- The Superblock programme is ongoing — green infrastructure is actively changing
  during the 2015–2024 window, which introduces temporal inconsistency in the tree data

**Open questions for next session (Data Understanding):**

- What is the actual record count for fungi in GBIF filtered to Barcelona municipality
  boundary, 2015–2024? Is it above 500 records? Below 100?
- Does the Barcelona Biodiversity Atlas tree data include species-level taxonomy
  consistently enough to join against FungalRoot at species level, or only genus level?
- Is GlobalAMFungi data geographically represented in the Iberian Peninsula / Mediterranean
  biome at sufficient density to be useful as a reference, or is it biased toward
  Northern Europe?
- Does the Ajuntament publish soil sealing / impervious surface data at a resolution
  useful for corridor gap analysis?

---

## Out of Scope

- No soil sampling or field data collection — this is a desk-based spatial analysis only
- No modelling of specific fungal species distributions — we are working at the
  network/functional level, not species level
- No analysis outside the Barcelona municipal boundary
- No recommendations for species to plant — only *where* to prioritise corridors,
  not *what* to put in them
- No real-time or live data feeds — snapshot analysis of 2015–2024 archived data only

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
