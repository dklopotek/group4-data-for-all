# How to extend — the soft parts of the pipeline

Three things you can change without touching the rest. Each is a deliberate, documented knob.

## 1. Swap the demand layer (which input)
Today exposure = **residential** population (`2026_pad_mdbas.csv`, joined in `src/section_priority.py`
`load_pop()`). To weight by **daytime** exposure instead (schools, workplaces, commuters), replace the
population join with a daytime-population or footfall table keyed on the same census-section code
(`DISTRICTE.zfill(2)+SEC_CENS.zfill(3)`). Nothing else changes. This is limitation #4 in the paper and
the most valuable extension.

## 2. Change the maturity / source definition (which scoring weight)
`src/section_priority.py` defines `MATURE = {"EXEMPLAR","PRIMERA"}` (assumption A1). Broaden to include
`SEGONA`, or replace categorical maturity with a trunk-diameter emission estimate if a diameter field
becomes available. The script already runs `broad_mature` and `uniform_maturity` as T4 sensitivity arms,
so you can see the effect immediately in the printed verdicts.

## 3. Change the removal target (policy input)
`src/street_actions.py` derives the target from the *Pla Director* policy **rate**, not a fixed count:
`REMOVAL_RATE = 1 − PCT_TARGET_2037/PCT_NOW` (12/27.45 → 0.563), applied to the street plane stock
(→ ~22,757). To use the city's actual annual or programme figure, either edit `PCT_NOW`/`PCT_TARGET_2037`
or set `target_remove` directly in `main()`. The `largest_remainder` apportionment and per-street caps
handle the rest. This is a **policy input, not a finding** — changing it never changes a priority, only
the `suggested_remove` annotation. (Sourced figures: 43,722 planes = 27.45% of total urban trees → 12%
by 2037; city rationale is biodiversity, not allergy — see paper §8.3.)

## Adding a whole new layer (a new sub-pipeline)
Follow the layer-audition gate (paper §7.3): a new layer earns inclusion only if it (a) re-orders the
output AND (b) is non-redundant with existing layers. Build it as a new `minmax`-standardised column,
multiply it in, and re-run T1–T4. If it doesn't pass the gate, report the rejection (we rejected three).

## What you should NOT do
Do not add a priority or score column at street grain (ecological fallacy — see the honesty gate in
`section-street-design.md`). Do not re-weight the spec until a failing test passes (that's the Cycle-A
sin). Do not relabel exposure as a health/clinical outcome.
