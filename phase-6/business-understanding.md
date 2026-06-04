# Pivot Product — Business Understanding (CRISP-DM Phase 1, re-run)

**Date:** 2026-06-04
**Product:** Platanus pollen-allergen exposure priority for Barcelona
**Prior project:** "Mycorrhizal Barcelona" — thesis falsified (`docs/failure-and-pivot.md`)

## The decision

Barcelona's *Pla Director de l'Arbrat 2017–2037* commits the city to reducing plane trees (*Platanus × acerifolia*) from ~27% to <12% of the street-tree stock. That reduction will happen over years, tree by tree, on a finite annual budget. **The decision this product supports: in what spatial order should the city sequence plane removals/replacements so that each removal delivers the most pollen-allergen-exposure relief to people?**

## Who acts, and how

- **Actor:** Ajuntament Espais Verds (street-tree program) together with urban-public-health planners.
- **Action:** sequence the multi-year replacement program — choose which axes / census sections to treat first.
- **Granularity:** census section / street axis (the unit the city procures against), aggregated from the analysis grid.

## What "good enough" means

A ranking is good enough if it (a) reduces modeled population allergen exposure **more than the city's current implicit rule** (replace where plane density is highest) and more than random, and (b) rests on a pollen-source layer that is **validated against independent measured pollen**, not against itself. A precise score that does not change the sequencing, or that merely re-expresses one variable, is not good enough — that is the exact failure we just documented.

## Cost of being wrong

- **Moderate, and asymmetric.** Mis-sequencing wastes program budget and delays relief for the most-exposed residents, but does not cause direct harm — plane removal proceeds either way under policy. Over-claiming health benefit we cannot support would damage credibility (the lesson from the mycorrhizal failure). The product therefore claims *exposure*, not clinical outcome, and states that boundary explicitly.

## Why this is defensible where the last one was not

| Failure mode (old project) | How the pivot avoids it |
|---|---|
| Validated an index against its own ingredients | Source layer validated against external aerobiology pollen data (or a stated emission-factor fallback) |
| Ecological signal weighted to ~0 (one variable in costume) | Two transparent layers (source, exposure); redundancy diagnostic confirms both move the ranking |
| Mechanism was assumption (FungalRoot trait proxy) | Mechanism is measured: plane inventory is direct; *Platanus* allergenicity is well-established |
| Data could not carry the claim | Plane locations, density, allergenicity, and pollen seasonality are all real and available |

## Intended use / NOT-for (drafted; finalized in the model card)

- **For:** prioritising the *sequence* of an already-decided plane-reduction program by modeled allergen-exposure relief.
- **NOT for:** predicting individual allergy/health outcomes; claiming clinical benefit; deciding *whether* to remove plane trees (policy already decides that); fine-grained within-cell siting.

## Success criteria (carried into evaluation)

1. SOURCE layer externally correlates with measured Platanus pollen at a pre-registered bar (or fallback limitation documented).
2. Priority beats density-only and random baselines on modeled exposure reduction per tree removed.
3. Redundancy diagnostic: source AND exposure both materially move the ranking.
4. Every layer reported separately; sensitivity pass; explicit non-claims.
5. The failure-and-pivot story is documented (done: `docs/failure-and-pivot.md`).

## Cancellation criterion

If the SOURCE layer fails external validation *and* no defensible emission-factor calibration exists, the pollen-source claim is downgraded to "plane-density proxy" and the product is reframed as a transparent plane-density × population exposure prioritisation with that limitation stated — we do not invent validation, just as we did not invent it for the fungal thesis.
