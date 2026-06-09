# Intended-Use Statement

## Who
A **capital-planning analyst at Ajuntament de Barcelona, Espais Verds** (municipal greenery),
working with urban public-health planners.

## What decision it informs
**The spatial order in which to sequence the city's already-committed plane-tree (*Platanus*)
reduction** (Pla Director de l'Arbrat 2017–2037: 43,722 planes = 27.45% of total urban trees → 12% by
2037, a ~56% cut, under a no-species-above-15% rule), so that each removal relieves the most
pollen-allergen exposure for residents. **The city's stated primary rationale is biodiversity and
monoculture disease-risk, not allergy** — this product supplies only the *sequencing* and treats
allergen-exposure relief as a co-benefit, never as the city's justification to remove. The product
delivers:
1. **Census sections ranked** by `source × exposure` priority (`section_priority.csv`) — the where.
2. A **per-street mature-plane worklist** for the top sections (`street_removal_actions.csv`) — the what.
3. An interactive map for exploration/presentation (`deployment_map.html`).

## How to act on it
Read sections top-down; within a chosen section, use the street worklist to find the mature planes to
schedule for removal/replacement under the existing programme. Use the equity variant (v3) if the
objective is relief for the worst-off rather than maximum total relief.

## What it must NOT be used for
1. **Not health evidence.** It models *exposure potential*, never diagnosed allergy or clinical outcome.
2. **Not a decision on whether to remove planes** — policy already decided that; this only sequences it.
3. **Not street-level prioritisation.** Street output is inventory + a feasibility allocation; ranking
   individual streets by section-level exposure is an ecological fallacy.
4. **Not valid below the census section** (and the 400 m evidence grain is coarser still); do not use for
   within-block siting.
5. **Not a pollen measurement.** The source layer is a literature-anchored proxy; no measured Barcelona
   *Platanus*-pollen series exists.
6. **Not punitive/enforcement input.** It is a planning aid, not a basis for fines, appeals, or
   property-level decisions.

## Confidence
Analytically ship-ready at the **400 m evidence grain** (passes all pre-registered tests). At the
**census-section deployment grain** the people-weighting result does not hold (MAUP, paper §8): treat
the section ranking as "largest mature-plane clusters, in populated areas" and consult both grains.
True deployment still pends a real analyst's sign-off and an independent reproduction.
