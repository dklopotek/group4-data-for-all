# Problem Brief v2 — Mycorrhizal Barcelona project

> Phase-1 loopback artifact. After Session 2's data understanding work, the
> v1 brief's "where is the network most fragmented?" framing was forced into
> revision because the data cannot support that claim at the resolution we
> need. The full revised brief lives in `docs/problem-brief.md`. This file
> (`problem-brief-v2.md`) is the changelog explaining *why* it changed.

---

## Was v1 revised? (yes / no)

**Yes** — substantially. Two-step revision during Session 2:

1. **Step 1 (intermediate, not adopted):** v1's "fragmentation map" was
   first reframed as an "uncertainty + stress diagnostic" — output a map
   of *where to investigate further*. Defensible but indirect: the
   policy chain required a separate research step before any spending
   decision.

2. **Step 2 (adopted):** Pushed one further to a **barrier-reduction
   priority map** — output identifies where intervention on
   directly-measurable barriers (sealed surface, heat, low canopy,
   host–mycorrhizal mismatch) delivers highest leverage per €, with an
   intervention-type recommendation per zone. Same data, same defensibility,
   single-step policy chain.

The decision unit (Superilla / 400m grid), user, geography, and most
out-of-scope statements are preserved.

---

## What did the data reveal?

1. **AM fungi are invisible to citizen science — and AM-host dominance
   in BCN's inventory is empirically confirmed.** Profiling shows the
   top six species (*Platanus × acerifolia* 42,828, *Celtis australis*
   21,304, *Tipuana tipu* 10,748, *Styphnolobium japonicum* 9,931,
   *Melia azedarach* 7,248, *Brachychiton populneus* 6,323) are all AM
   hosts. EM-host taxa appear at meaningful counts (*Pinus pinea*,
   *Pinus halepensis*, *Quercus ilex*, ~9k trees combined) so the
   observation layer can do useful work for the EM-dominant subset, but
   the dominant signal is AM and therefore not citizen-sci-visible. The
   AM-blindness limit is foundational, not a footnote.

2. **GBIF density for Barcelona is workable — and confirms the
   citizen-sci bias.** Profiling-time spot-check returned 1,023 fungal
   records in BCN bbox 2015–2024 (above the v1 brief's "above 500" upper
   estimate). 98.3% are HUMAN_OBSERVATION (citizen science), 1.6%
   PRESERVED_SPECIMEN, 0% MATERIAL_SAMPLE — i.e. zero DNA-based ground
   truth. Sample size is workable for the observation-context layer but
   the basis-of-record breakdown confirms the AM-blindness limit is real.

3. **GlobalAMFungi DNA reference data is not verifiable from this
   profiling session.** Both the project portal (JS-rendered) and the
   *New Phytologist* paper (paywalled) blocked programmatic verification.
   The dataset is retained as INVESTIGATE pending manual portal access;
   the v2 framing already does not depend on this source.

4. **ERA5-Land at 9km cannot differentiate Superilla zones.** A single
   ERA5-Land grid cell covers roughly half of Barcelona — useless for
   any per-zone score. Soil moisture, the single most important driver
   of mycorrhizal community composition, has no Superilla-scale source.
   Mitigated by using Sentinel-2 NDVI + Landsat LST as joint surface
   proxies.

5. **Sealed-surface fraction has a defensible 10m source.** Copernicus
   Urban Atlas 2018/2021 covers Barcelona's Functional Urban Area at 10m
   resolution and was unscored in v1; adopting it makes the de-paving
   leverage layer robust at our decision unit.

6. **The Ajuntament tree inventory is bigger than estimated and
   species-level taxonomy is consistent.** 189,090 records (145,478
   street + 43,612 park) across 10 districts and ~73 barris, with 381
   unique species. Only 25 records (0.01%) are genus-only, all
   *Washingtonia sp* — the v1 brief's worry about a genus-only fallback
   is resolved: species-level FungalRoot join is feasible.

7. **The barriers we *can* measure are exactly the levers planners
   already control.** Sealed-surface, heat, canopy, and host-species
   composition each map to a documented Ajuntament budget line (Eixos
   Verds, Superilla soil, planting programme, cooling strategy). This
   collapsed the v1 indirection: instead of mapping an unmeasurable
   target and recommending soil sampling, we can map the measurable
   barriers and recommend specific intervention types.

---

## What changed in the brief

### Decision

- **Was (v1):** "Rank zones by fragmentation severity using sealed-surface
  fraction, urban density, and inter-node distance."
- **Now:** "Rank zones by **combined barrier index** (sealed surface, heat,
  low canopy, host–mycorrhizal mismatch) and recommend the **top
  intervention type** per zone, tied to an existing Ajuntament budget
  line."

The decision unit (Superilla / 400m grid) is unchanged. What changed is
*what we measure* per zone — directly-measurable known barriers — and the
*output form*: not just a rank but an intervention-type recommendation.

### User

- **Was:** Ajuntament Espais Verds i Biodiversitat + Barcelona Regional.
- **Now:** Same.
   We considered pivoting to Collserola (peri-urban) but rejected because
   that would change the user (Diputació de Barcelona / AMB / Generalitat)
   and the planning context (no analogue to Eixos Verds / Superilla
   capital lines exists peri-urban). The peri-urban reference patch is
   retained methodologically but the project's user, decision-maker, and
   geography are all municipal.

### Success criteria

- **Was (v1 wording):** "Output is a shortlist of ≤15 priority zones, each
  with its score, the inputs that produced it, and the assumptions it
  depends on."
- **Now:** Same shortlist size, but each zone now carries: expected
  mycorrhizal type, four sub-scores (sealed surface / heat / canopy /
  host mismatch), and the **top-recommended intervention type**. Plus
  two new criteria: (i) a peri-urban reference patch as low-barrier
  anchor, (ii) every intervention type maps to a documented Ajuntament
  budget line.

### Sub-questions

- **Was (v1):** Sub-questions were implicit. The v1 brief had "open
  questions for Session 3" but these were data-availability questions, not
  analytical sub-questions.
- **Now:** Seven explicit sub-questions, each mapped to a data source in
  `data-to-decision-map.md`, and each tied to an intervention type. (See
  `problem-brief.md` for the full list.)

### Out of scope

*New additions, given data limits and scope discipline:*

- **No claim that barrier-reduction will produce mycorrhizal network
  formation, recovery, or strengthening.** The output identifies *leverage*,
  not *outcome*. Soil microbial community recovery timescales are
  5–20+ years; the map cannot promise within-cycle results.
- **No claim of belowground network state, connectivity, or
  "fragmentation."** This is not a connectivity map.
- **The peri-urban reference patch is a methodological anchor only** —
  not a target zone, not subject to priority ranking, not used to make
  quantitative claims about what "should" exist in Barcelona.
- No specific tree-species recommendations — only the mycorrhizal-type
  expectation layer that supports planners' species selection within their
  existing protocols.

---

## What we still don't know

**Resolved by Session 2 profiling:**

- ~~Actual GBIF fungal record count for the Barcelona municipal boundary,
  2015–2024.~~ → **Resolved at 1,023 records** (98% citizen-sci, 0%
  DNA-based). See `data-quality-audit.md` GBIF spot-check.
- ~~Does the Ajuntament tree inventory carry consistent species-level
  taxonomy or is genus the realistic join key against FungalRoot?~~ →
  **Resolved YES — species-level is consistent**, only 25 records
  (0.01%) are genus-only.

**Still open for Session 3:**

- Whether any GlobalAMFungi sample exists within 100km of Barcelona.
  Profiling-session attempts at programmatic verification blocked by
  JS-rendered portal and paywalled paper. Requires manual portal
  inspection. Retained as INVESTIGATE; v2 framing does not depend on it.
- The peri-urban reference patch's barrier index relative to urban core
  median. Computed during Session 3 once Urban Atlas + Landsat LST are
  ingested for the reference patch.
- For each of the four intervention types, the specific Ajuntament /
  Barcelona Regional budget line, decision cycle, and current-cycle
  spending allocations. Required for criterion 7. Best filled in via a
  brief desk review of the most recent Eixos Verds / Superilla planning
  documents.

---

## Sign-off

The full revised brief lives in `docs/problem-brief.md` (overwritten on
revision). This file (`problem-brief-v2.md`) is the changelog explaining
*why* the revision was made — and explicitly notes the two-step revision
path during Session 2 (intermediate diagnostic shape considered and
rejected in favor of the action-oriented barrier-reduction shape).

**Team:** [names]
**Committed by:** [name]
**Date:** 2026-05-01
