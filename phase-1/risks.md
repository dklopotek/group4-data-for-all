# Risk Register

## Risk Table

| # | Risk | Likelihood | Impact | Owner | Mitigation | Triggers Cancellation? |
|---|---|---|---|---|---|---|
| R1 | **AM-blindness confound:** AM fungi are invisible to citizen science, making the host–mismatch sub-score structurally unconfirmable for AM-dominant zones (~85% of BCN trees) | H (certain — it is a structural limit, not a probability) | M (reduces confidence in mismatch sub-score; does not invalidate the other three sub-scores) | Rafik | Flag categorically as "unconfirmable" rather than faking a quantitative score. Document prominently in product card and all outputs. The peri-urban reference patch provides a qualitative anchor. | No — this is a documented limitation, not a project-killer. The barrier-reduction framing was specifically chosen to be defensible even with this confound. |
| R2 | **Intervention heuristic too simple:** The "highest sub-score → intervention type" mapping may misroute capital in zones where barriers are balanced | M (heuristic is simple by design but may miss interactions) | L (output is a recommendation, not an automated allocation; planners apply judgment) | Rafik | Document as a heuristic, not an optimizer. Recommend "combined" intervention when top two sub-scores are within 10% of each other. | No |
| R3 | **Cloud occlusion in satellite data:** Persistent cloud cover over Barcelona during the target summer window could leave gaps in LST or NDVI layers | L (Barcelona has a Mediterranean climate; summer cloud cover is low) | M (missing data in key zones would create gaps in the priority ranking) | Rafik | Use multi-scene summer composites (June–August). Fall back to adjacent-year data if current year is incomplete. Document any gaps explicitly. | No |
| R4 | **GlobalAMFungi zero samples in Iberia:** If the DNA metabarcoding reference database has no samples within 100km of Barcelona, there is zero AM-fungal ground truth | M (preliminary assessment suggests sparse coverage) | L (v2 framing already does not depend on this source) | Rafik | Retain as "INVESTIGATE" — query the portal manually during Session 3. If zero samples, reject with documented rationale. Framing stands without it. | No |
| R5 | **Teacher rejects CRISP-DM retrofitting as insufficient:** The process documentation in notebooks (before/after counts, design decisions, bounds assertions) may not meet the grading standard | M (first attempt at formal CRISP-DM documentation) | H (core grading criterion) | Rafik | Follow the session-3/tasks.md specifications exactly. Validate each notebook against the P1–P5 requirements before submission. Review against the academic CRISP-DM reference model. | No — but triggers a rework cycle before Session 4. |
| R6 | **Pipeline not reproducible from clean clone:** Dependency drift, hardcoded paths, or missing data downloads prevent a reviewer from re-running | M (common in notebook-based projects) | H (reproducibility is a core CRISP-DM requirement) | Rafik | Use relative paths. Document all data download URLs in a setup script. Pin Python dependency versions. Test a clean-clone re-run if time permits. | No |
| R7 | **Peri-urban reference patch selection is arbitrary:** Choosing Collserola vs. Garraf vs. another patch changes the baseline, and there is no objective criterion for the choice | M | L (the patch is a qualitative anchor, not a statistical comparator) | Rafik | Document the selection criteria: (1) within 15km of Barcelona center, (2) protected natural area status, (3) minimal sealed surface, (4) known EM-host tree presence. Justify the choice in the methodology. | No |

## Cancellation Criterion

**The project should be cancelled or fundamentally rescoped if:**

> After completing Session 3 data preparation, **more than two of the four barrier sub-scores cannot be computed at the 400m decision unit for ≥ 50% of Barcelona's grid cells.** This would mean the core barrier-reduction concept — combining four measurable barriers into a composite score — is not feasible with the available data, and the output would be too sparse to support a planning decision.

*Rationale:* The project's value proposition is the *combination* of barriers. If the majority of zones have data for only one or two barriers, the composite index collapses to a single-barrier map, which already exists in other forms. The cancellation threshold is set at 2 of 4 barriers because (a) sealed surface and NDVI are near-certain to be computable (both have verified 10m sources), (b) LST at 100m is highly likely, and (c) the mismatch sub-score is the one most at risk. If LST also fails (e.g., due to cloud occlusion), only 2 of 4 barriers remain — at which point the composite is too thin to justify.

## Pre-Mortem

*"Imagine it is June 2026 and the project has clearly failed. What happened?"*

1. **The AM-blindness confound was not documented prominently enough.** A reviewer noticed that the majority of BCN zones had an "unconfirmable" mismatch flag, asked "so what does this map actually tell us that a simple NDVI map doesn't?", and the project could not articulate the value-add of the composite over a single-layer map.
2. **The notebooks ran but the process was invisible.** The teacher opened notebook 03, saw a sequence of code cells with no design-justification markdown, and concluded the team had done data work without data thinking.
3. **Scope creep into frontend.** Someone spent Session 4 building a beautiful interactive map instead of hardening the pipeline logic, and the teacher ignored it because "no frontend" was stated in the briefing.

*Pre-mortem mitigations baked into the risk register and the session-3 task list: R1 documentation requirement, P1–P5 notebook retrofitting specs, and the explicit "no frontend" constraint in the situation assessment.*
