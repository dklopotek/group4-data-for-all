# Planner-Perspective Evaluation of the Tool

> Multi-agent evaluation (2026-06-09): four independent reviewers ran the tool against the real
> 48-scenario output (`planner_scenarios.md/json`) — an **efficiency planner**, an **equity/EJ officer**,
> a **quantitative analyst**, and a **skeptical reality-check auditor**. All figures are from the data
> files; none invented. They converged on one picture, summarized here.

## Headline verdict

**A useful sequencing aid that beats the city's status-quo rule by a real but modest margin — usable
with conditions, NOT yet a councillor-grade decision instrument.** The tool's honesty is its strength;
its weakness is that the caveats live in footnotes while the misleading defaults live in the buttons.

- **Efficiency planner:** *yes, with conditions* — use it Monday; skip-park always on; brief relief as a proxy.
- **Equity officer:** *yes, with conditions* — near-free equity tilt, but the equity instrument is too thin to anchor an EJ case alone.
- **Analyst:** *iterate, not ship-as-priority-tool* — ship the budget/equity/skip-park logic anchored on the 400 m grain; section priority is an execution unit, not an analytical claim.
- **Reality-check auditor:** *needs work* — strong as a Phase-5 evaluation artifact; not deployable until the grain, the proxy, and the honesty-vs-defaults gap are fixed.

## What works (quantified, skip-park ON, the realistic setting)

| Finding | Evidence |
|---|---|
| **Beats the city's "most-planes-first" rule** | efficiency vs density_naive burden captured: **+2.31 pp at budget 1000 (~+19% relative)**, +2.56 pp at 2000 |
| **Equity tilt is near-free (sometimes free-or-better)** | +11.2 pp deprived-tercile share at budget 500 for **−0.06 pp** burden; at budget 2000 equity captures *equal-or-more* burden than efficiency while +4.9 pp deprived |
| **Strong concentration** | top-15 sections = 27.6% of city priority; first 2,000 mature planes (~64% of removable stock) capture **22.4%** of burden |
| **Sweet spot budget ≈ 1,000–2,000** | marginal relief/1,000 planes falls 28→8 pp by budget 2,000, then craters to ~2 pp toward the 3,146-mature ceiling |

## The big caveat (all four agreed)

**At the census-section grain the tool ships in, "priority" is ~97% the same as "where the most mature
planes are"** (`section_priority.md`: T1 Spearman 0.97, T4 holds 1/3, agreement with the 400 m product
only 0.47). The people-weighting that justifies the tool is real at the **400 m grain** but washes out
at section grain (MAUP). **Use sections as the operational/execution unit (the crew's work packet +
street list); make the priority *claim* at the 400 m grain.** The honest margin over the naive rule at
section grain is ~+3–5 points (T3), not the +4.6/+9.3 headline (which is the 400 m number).

## Other consensus findings

- **Skip-park is a correctness requirement, not an option.** With it off, small budgets spend ~59% of a
  1,000-tree year on one Montjuïc parkland section (594 mature planes, ~2,000 residents) — felling trees
  where almost nobody is exposed. The UI defaults it on (correct), but lets a user flip it off with no warning.
- **At the operational ceiling (budget 5,000) all four objectives converge** to an identical answer
  (28.57% burden, 398 sections) — you run out of removable mature planes (3,146). Strategy choice is real
  only in the 500–2,000 band.
- **The equity instrument is thin:** one income tercile, binary, no health/vulnerability data (children,
  elderly, diagnosed allergic-respiratory). A near-free *tie-breaker*, not a standalone EJ case.
- **Relief is a modeled proxy** (source × residents), not measured pollen or health outcome — the source
  layer is an unvalidated literature proxy.

## Tool fixes this evaluation triggered (honesty-vs-defaults gap)

Applied to `planner.html` (see commit):
1. **Persistent caveat strip** on the map (always visible, not just the dismissible modal): section
   ranking ≈ plane density at this grain; relief is a modeled proxy.
2. **Skip-park OFF warning** — a confirm prompt when a user unchecks it, naming the Montjuïc trap.
3. **CSV disclaimer row** — the exported worklist carries a first row stating `suggested` is a policy
   allocation, not a street ranking.

Deferred (recommended, larger): an objective selector with a marginal-relief curve; reconciling the two
grains (decide at 400 m, execute at section); a real vulnerability layer for the equity objective;
budget expressed in crews/euros/works-calendar slots.

## Bottom line for the presentation

The tool earns ~19% more exposure relief per tree than the city's current rule at the right budget, and
buys an almost-free equity tilt — but it is honest that, at the grain a crew works, its ranking is close
to "count the planes," and its relief number is a proxy. That candor is the deliverable: a sequencing
aid that tells you exactly how far to trust it.
