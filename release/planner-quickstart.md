# Planner's Quickstart — how to actually use this

> For the Espais Verds capital-planning analyst. Five minutes, repeatable each budget cycle.
> This tool does **not** decide *whether* to remove planes (policy already does). It tells you
> **the order** to sequence the cuts so each one relieves the most pollen exposure for the most people.

## The three files (and what each is FOR)

| File | Role | When you touch it |
|---|---|---|
| `outputs/phase-6/section_priority.csv` | **The queue** — sections ranked, top-down | Step 1: pick where |
| `outputs/phase-6/street_removal_actions.csv` | **The worklist** — streets + mature-plane counts per top section | Step 2: pick what |
| `outputs/phase-6/maps/deployment_map.html` | **The pitch** — show councillors the heat | Step 5: get buy-in |

It is a **worklist generator**, not a map to stare at. The map is for communication.

## The 5-step loop

1. **Open the queue** (`section_priority.csv`). Read from rank 1 down.
2. **Apply the honesty filter.** Skip/flag park-dominated sections with few residents — e.g. rank 1
   = **Montjuïc** (1,840 planes but ~2,000 residents; it's the Olympic park). Huge plane count,
   little residential exposure. The next ranks (Sant Martí, Eixample) are dense-residential — start there.
3. **Pull the streets.** Filter `street_removal_actions.csv` to your chosen section. You get the exact
   streets and how many **mature** planes each holds (e.g. Sant Martí → C/ Maresme 32, Rbla Prim 17).
   `suggested_remove` is an illustrative policy allocation, not an order — use `n_mature` as your menu.
4. **Cross-reference the works calendar.** Where a street is already being dug up (tram, pavement,
   utilities — e.g. the Diagonal tram works), piggyback the removal/replacement. Near-zero marginal
   cost. This matches the city's own opportunistic rollout.
5. **Schedule down the queue** until this cycle's budget is spent. Then open the **map** in the
   council meeting: *"we sequence where the most residents breathe the most pollen — here's why."*

## Two things to remember (the honest caveats)

- **Concentration is the point.** The top 15 sections hold ~28% of the city's total priority, the top
  50 hold ~44%. You capture most of the benefit from a short list — don't try to work all 827
  planted sections.
- **Grain matters (MAUP).** At this fine section grain the ranking leans toward "biggest mature-plane
  clusters." For the *people-weighting evidence* (population genuinely re-ordering priorities), use the
  **400 m view** in the map (toggle top-right). Use sections to *act*, the 400 m view to *justify the
  method*. Read them together — see the model card and paper §8.

## What it is NOT for
Not health/allergy evidence. Not a reason to remove planes (policy decides that; this only sequences).
Not street-level ranking (streets are a worklist, not a priority score). Not valid below section grain.
