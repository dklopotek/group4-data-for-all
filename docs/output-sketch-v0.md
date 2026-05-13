# Output Sketch v0

> One-page sketch of what the planner sees at the end of Session 7.
> This is a sketch, not a product spec. Decision unit: Superilla / 400m
> grid. Sketch will iterate; Session 7 has the locked version.

---

## What is the final output?

- [x] **Annotated map / report** *(static, designed to be read)*

The output is a single-page-equivalent document combining (a) a map of
Barcelona showing the priority zones, color-coded by recommended
intervention type, and (b) a tabular per-zone record listing rank,
expected mycorrhizal type, four sub-scores, intervention type, and
the assumptions the score depends on. A printable PDF with an
optional interactive web-map version sharing the same underlying GeoJSON.

**One-sentence description of the output:**

> A printable annotated map of Barcelona's top 15 barrier-reduction
> priority zones at Superilla scale, color-coded by recommended
> intervention type and paired with a per-zone scoring rationale + an
> explicit list of what the map cannot claim.

---

## Who is the user?

> **A capital-planning analyst at Barcelona Regional or at the
> Ajuntament's Espais Verds i Biodiversitat unit, on a Tuesday morning,
> deciding which 5–8 streets or block-interiors get priority allocation
> in the next Eixos Verds + Superilla soil-intervention budget cycle.**

### What does the user already know?

- BCN's existing planning programmes (Eixos Verds, Superilla, the
  cooling strategy, the Pla del Verd i de la Biodiversitat 2020–2030)
- GIS tools — QGIS or ArcGIS — and reading basic spatial datasets
- Their own municipal districts, neighborhoods, and budget cycles
- That trees + soil + cooling are intertwined ecologically, even if
  they're not specialists in mycorrhizal ecology

### What does the user NOT know?

- Where, at Superilla scale, the *combined* barrier index is highest
- Which intervention type (de-paving / cooling / planting /
  species-selection) maps best to each priority zone
- Whether observation deserts in citizen-science fungal records reflect
  ecology or just observer geography (the peri-urban reference patch
  answers this contextually)
- The mycorrhizal expectation map of the public-realm tree population
  (this is genuinely new information for municipal planning)

---

## The top 3 actions this output enables

1. **Allocate next-cycle Eixos Verds capital** to the 3–5 highest-ranked
   zones whose top recommended intervention type matches the available
   budget line (e.g. de-paving line → top zones with sealed-surface as
   dominant sub-score).

2. **Identify priority de-paving + structural-soil sites within the
   Superilla rollout**, by selecting from the shortlist the zones already
   inside designated Superilla intervention areas — with the barrier
   composite acting as the tiebreaker between competing candidate sites.

3. **Brief stakeholders** (district councils, citizen platforms, the
   Comissió de Govern) with a one-page defensible scoring rationale per
   zone, including the explicit "what this map cannot claim" footer.

---

## Sketch

*Image to be added; for now, description-based wireframe.*

> Layout (described top → bottom):
>
> - **Header (top, ~10% of page):** Title — "Barcelona Barrier-Reduction
>   Priority Zones for Belowground Ecological Recovery v0.1." Decision
>   unit. Snapshot date. Scoring vintage.
>
> - **Center (~55%):** Barcelona basemap with 10 districts faintly
>   outlined, the 400m grid lightly drawn. The top 15 priority zones
>   highlighted as filled cells, color-coded by recommended intervention
>   type:
>     - 🟧 De-paving (sealed-surface dominant)
>     - 🟥 Cooling / canopy (heat-anomaly dominant)
>     - 🟩 New planting (NDVI-low dominant)
>     - 🟦 Species selection (host-mismatch dominant)
>   Numbered 1–15. Reference-patch in Collserola shown as a tiny inset
>   below the legend.
>
> - **Right side panel (~25%):** Tabular per-zone record. For each zone:
>   rank, district / barri, expected mycorrhizal type, four sub-scores
>   (sealed %, LST anomaly, NDVI, host-mismatch flag), intervention type
>   pill, and a one-line assumption note. Sortable in the web version.
>
> - **Footer (~10%):** "What this map *cannot* claim:"
>     - It is *not* a map of belowground network state or fragmentation
>     - It does *not* predict that intervention will produce mycorrhizal
>       community recovery within a planning cycle
>     - It does *not* reflect private-realm vegetation or tree health
>     Plus the citation block for adopted datasources.

---

## What this output is NOT

- **Not a fungal-network map.** The map shows where intervention has
  highest leverage given measurable barriers — it does not depict any
  underground network, partnership, or connectivity.
- **Not a forecast of intervention success.** Soil-microbial recovery
  timescales are long; the map is a planning-decision aid, not a
  guaranteed outcome predictor.
- **Not a guarantee that the highest-scoring zones will produce the
  fastest mycorrhizal recovery.** Urban restoration ecology supports
  non-linear response curves — zones with moderate barrier levels and
  some residual soil biological capital (spore banks, residual hyphal
  networks) may recover faster from the same intervention than severely
  degraded zones. Highest composite score ≠ highest intervention return
  per euro. Zones with `colonisation_uncertain=True` in the per-zone
  record warrant additional site assessment before committing capital.

---

## What would make a user trust this output?

- **Per-zone transparent rationale.** Every priority zone has its
  numerical sub-scores and the assumption-list visible; nothing is a
  black box. The planner can defend any specific ranking call to a
  district council without consulting the analyst.

---

## How does this connect to the rest of the work?

| Seminar artifact | How it feeds into this output |
|---|---|
| Problem brief (v2) | The decision this output supports — barrier-reduction priority for Eixos Verds + Superilla allocation |
| Datasheets (Ajuntament + GBIF) | Provenance shown in the footer (citation, source, license) |
| Quality audit | Limitations shown in the footer's "what this map cannot claim" block |
| Decision map | The seven sub-questions this output answers |
| System sketch | The pipeline that produces this output |
| (Future) Model card | Per-sub-score description, weights, sensitivity, AM-blindness limit |
| (Future) Failure gallery | Known failure modes (e.g. zones flagged as observation deserts) |

---

## Sign-off

**Team:** [names]
**Sketched by:** [name]
**Last updated:** 2026-05-01
