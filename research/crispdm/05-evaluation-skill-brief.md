# Skill Brief — `crispdm-phase5-evaluate-pipeline`

*A skill that walks a graduate student through CRISP-DM Phase 5 Evaluation of a data pipeline and produces a defensible go / iterate / kill decision. Domain: AEC, urban, environmental data pipelines. Companion to `05-evaluation-academic.md`.*

---

## name
`crispdm-phase5-evaluate-pipeline`

## description
Runs the user through a structured Phase 5 — Evaluation — of a CRISP-DM data pipeline. Produces an Evaluation Report, a Limitations Register, an Intended-Use Statement, Conditions for Deployment, Conditions for Non-Use, and a signed Go / Iterate / Kill memo. Forces the user to close the loop back to the Phase-1 business success criteria, evaluate the *whole pipeline* (not just any model inside it) against the decision-maker's actual decision, and surface the assumptions, biases, and limitations that distinguish a shippable pipeline from a publishable one.

The skill is for pipeline projects where the audience is a real decision-maker (urban planner, scientist, policymaker, operations team) and the deliverable is a pipeline rather than a model in isolation.

## triggers
Activate this skill when the user says any of:
- "evaluate the pipeline", "phase 5", "phase five", "CRISP-DM evaluation"
- "is the pipeline ready", "should we ship", "go no-go", "ready for deployment"
- "is this fit for purpose", "did we answer the question"
- "review the data project", "post-mortem the pipeline"
- "is the mycorrhizal pipeline good enough"
- "do we deploy / iterate / kill"

Do **NOT** activate this skill if the user is asking about model metrics in isolation (AUC, RMSE, F1, accuracy, train/test, hyperparameter tuning). That is **Phase 4 Modeling-stage assessment**, not Phase 5 Evaluation. Route them to a Phase-4 skill or tell them the distinction (see Anti-Patterns).

## inputs (required — refuse to proceed if missing)

1. **The original Phase-1 business success criteria, verbatim.** If the user cannot produce these, **refuse to start the evaluation**. Tell them: *"Phase 5 evaluates against the Phase-1 business success criteria. Without those criteria written down, this is theatre. Go produce them — return when you can paste them in."* This is a hard gate; do not proceed without it.
2. The Phase-1 business question (one sentence — the decision the pipeline is meant to inform).
3. The intended decision-maker (named institution and role).
4. A pinned, runnable version of the pipeline (commit hash, environment file, raw-input manifest).
5. A list of the pipeline's outputs (raster, table, ranked list, alert, etc.) and where they live.
6. Access (live or via summary) to at least one named representative of the intended decision-maker for the stakeholder walkthrough.

## optional inputs
- Phase-4 model-assessment outputs (technical metrics).
- Any prior data documentation: datasheets for datasets, data lineage docs.
- Sensitivity-analysis outputs.
- Reproducibility-test outputs (a second run by an independent operator).

## sequential steps

### Step 0 — Gate check
Verify all required inputs. If any are missing, stop and produce a list of exactly what is missing. Do not proceed.

### Step 1 — Name the Phase 4 / Phase 5 distinction out loud
Before any evaluation, write into the report: *"This is Phase 5. We are evaluating the pipeline against the Phase-1 business success criteria, not the Phase-4 technical metrics. Phase-4 metrics may appear as evidence but they are not the criteria."* This sentence is the orienting move that prevents the most common failure (Section 11 anti-pattern #1 in the academic brief).

### Step 2 — Closing the loop
For each Phase-1 business success criterion, produce a row:

| Criterion (verbatim) | Status (met / partial / unmet) | Evidence | Residual risk |

If a criterion cannot be evaluated, mark it `un-evaluable` and flag why — this is itself a Phase-5 finding.

### Step 3 — Fitness-for-purpose checklist
Produce yes / no / partial / NA answers for each:

- Does the output answer the *original* Phase-1 question, or a question the pipeline made convenient?
- Is the spatial / temporal / categorical resolution matched to the decision unit?
- Is the stated confidence honest (real uncertainty propagation, not goodness-of-fit only)?
- Is timeliness adequate for the decision?
- Are data licences, ethical clearances, and re-use rights compatible with intended use?
- Is the pipeline reproducible end-to-end by an independent operator on a clean machine?

For each "no" or "partial", write a one-line consequence.

### Step 4 — Stakeholder walkthrough
Run the walkthrough script in the appendix below. Capture verbatim hesitations, missing-context requests, and invented caveats from the decision-maker. Score the closing "Monday test" (would you act on this output on Monday?).

### Step 5 — Ethical and bias review (pipeline level)
Answer in plain language:
- Who benefits from the pipeline's output? (Name specific people / institutions.)
- Who is missed? (Whose phenomena, geographies, or populations are under-represented in the inputs?)
- What is the failure-cost asymmetry between false-positive and false-negative outputs?
- What does the pipeline do at the edges of its coverage, and how is that signalled?
- Is there a route for affected parties to contest or correct an output?

### Step 6 — Review process (meta-review)
Produce a four-column register of:
- Shortcuts taken.
- Assumptions not validated.
- Inputs with thin provenance.
- Steps that should be re-run before deployment.

Run a **pre-mortem**: *"Imagine this pipeline has been live for six months and a journalist or auditor has just shown a serious failure to the decision-maker. Write the post-mortem now."* Add the failure modes that surface here to the register.

### Step 7 — Limitations Register
Convert the findings of Steps 2 – 6 into a line-item file:

| ID | Limitation | Source phase | Severity (L/M/H) | Trigger condition | Mitigation | Owner |

This file must live in the repository, not in slides.

### Step 8 — Intended-Use Statement
Following Mitchell et al. (2019), write:
- Pipeline name + version (commit hash).
- Primary intended uses.
- Primary intended users (named institutions / roles).
- Out-of-scope uses (named).
- **Prohibited uses (named) — required for pipelines that could be misused for enforcement or punitive decisions.**
- Performance characteristics across coverage tiers.
- Date of next required re-evaluation.

### Step 9 — Conditions for Deployment / Conditions for Non-Use
Two short lists. Conditions for Deployment are preconditions that must be true for release (e.g. "second-team reproduction succeeds and hash-matches"). Conditions for Non-Use are contexts where the pipeline must explicitly *not* be applied (e.g. "must not be used as sole evidence in planning appeals"). Both lists feed directly into Phase 6.

### Step 10 — Go / Iterate / Kill decision
Produce a one-page memo:
- Recommendation (ship / iterate / kill).
- Recommender (name).
- Dissenting opinions (named).
- Rationale, tied to specific Phase-1 criteria and walkthrough findings.
- If "iterate": the written hypothesis for what will change and which phase to loop back to.
- If "kill": explicit acknowledgement that sunk costs do not justify continuing.

### Step 11 — Phase 6 handoff bundle
Confirm the existence of: Evaluation Report (Step 2), Fitness-for-purpose checklist (Step 3), Bias & ethics review (Step 5), Process-review register (Step 6), Limitations Register (Step 7), Intended-Use Statement (Step 8), Conditions for Deployment / Non-Use (Step 9), Go/Iterate/Kill memo (Step 10), Reproducibility bundle (pinned env, input manifest with hashes, run script, expected-output hashes). Without these, do not pass to Phase 6.

## deliverables

The skill must produce (or update) these files in `evaluation/<pipeline-name>/`:

1. `evaluation-report.md` — structured by Phase-1 criteria, with the orienting Phase-4/5 distinction at the top.
2. `limitations-register.md` (or `.csv`) — versioned, line-item.
3. `intended-use-statement.md` — model-card-style.
4. `conditions-deployment.md` — bullet list of preconditions for release.
5. `conditions-non-use.md` — bullet list of contexts where the pipeline must not be used.
6. `go-no-go-memo.md` — one page, signed (named).
7. `walkthrough-notes.md` — verbatim notes from the stakeholder walkthrough.
8. `process-review.md` — pre-mortem + register of shortcuts and unchecked assumptions.

## quality checks
Before declaring Phase 5 complete, verify each:

- [ ] The Phase 4 / Phase 5 distinction is stated explicitly at the top of the evaluation report.
- [ ] Every Phase-1 business success criterion appears verbatim and has a status + evidence.
- [ ] A real decision-maker (not just the pipeline team) participated in the walkthrough; their name is recorded.
- [ ] The "Monday test" answer is recorded verbatim, not paraphrased.
- [ ] The Limitations Register has at least one line per Phase-1 criterion marked `partial` or `unmet`.
- [ ] An Intended-Use Statement names prohibited uses, not only intended uses.
- [ ] The Go/Iterate/Kill memo names dissenting opinions if any existed (or states explicitly "no dissenting opinions").
- [ ] If recommendation is "iterate", a written hypothesis exists for what will change.
- [ ] If recommendation is "ship", an independent operator has re-run the pipeline end-to-end on a clean machine.
- [ ] No Phase-4 technical metric (AUC, RMSE, accuracy) appears alone as evidence for a Phase-1 criterion without an explicit translation step.

## anti-patterns (auto-detect and stop)

The skill must detect and refuse to proceed when any of these are happening:

1. **The assessment-vs-evaluation conflation.** If the user offers AUC / RMSE / accuracy as the evaluation, stop and explain: *"That is Phase-4 Assess Model. Phase 5 evaluates against the Phase-1 business success criteria. Show me those."* Cite Chapman et al. (2000, pp. 28, 30).
2. **No decision-maker in the room.** If the team is evaluating the pipeline against criteria the team invented and presenting it to itself, stop and require a named representative of the decision-maker for the walkthrough. (Madaio et al., 2020.)
3. **Evaluating in isolation from intended use.** If the evaluation is happening at the team's desk only, stop and require the decision-rehearsal session in the intended-use context. (Voinov et al., 2018.)
4. **Confirmation bias.** The team built the pipeline; they will find it acceptable by default. Require the pre-mortem (Step 6) and treat its outputs as evidence, not as speculation. (Kahneman, 2011.)
5. **Vanishing limitations.** If limitations are surfaced verbally and not committed to `limitations-register.md` in the repo, treat the evaluation as incomplete.
6. **Skipping Review Process.** Treating Evaluate Results as the whole of Phase 5 and omitting the Review Process meta-review. The CRISP-DM 1.0 guide marks these as distinct tasks with distinct outputs (Chapman et al., 2000, pp. 30–31).
7. **Treating "no" as failure.** A clean no-go with a defensible evaluation is a successful Phase 5. Do not push the user toward "ship" to avoid the appearance of failure.
8. **Vague Phase-1 criteria.** "Provide useful insight to planners" is not a falsifiable criterion. Force the user to operationalise it before evaluating against it.

## handoff to Phase 6

When recommendation is **ship**, hand the following bundle to Phase 6 (Deployment):

- All eight deliverables above.
- A reproducibility bundle: pinned environment (lockfile), raw-input manifest with file hashes, single run script, expected-output hashes.
- A named owner for monitoring and a re-evaluation cadence (calendar date).

When recommendation is **iterate**, hand back to the named phase with the written hypothesis. Do *not* loop back without one — that is sunk-cost defence dressed as iteration.

When recommendation is **kill**, archive all eight deliverables alongside the kill-rationale. A clean kill is documentation that future related projects must read; do not delete it.

---

## Appendix A — Stakeholder Walkthrough Script

Use this script in Step 4. Run with the named decision-maker in the room (or on a call). Record verbatim where possible.

**Setup (2 min)**
> "We are running Phase 5 of CRISP-DM on the [PIPELINE NAME]. The goal of today is to find out whether this pipeline answers the question you originally asked, in a form you can act on. There are no wrong answers; we want you to be hard on it. We will not change the pipeline during this session — we will just record what you say."

**Anchoring (3 min)**
> "Could you state, in your own words, the decision you would use this pipeline to inform?"

Record verbatim. Compare to the Phase-1 business question. If the two differ materially, flag it as a Phase-5 finding (the team and the decision-maker have drifted apart).

**Stage-by-stage walkthrough (15 min)**
Walk the decision-maker through every stage of the pipeline, in order. At each stage, ask three questions:

1. *"Do you trust this input? What would you want to know about it that you don't?"*
2. *"Do you understand what is happening to the data at this step?"*
3. *"Is there an assumption being made here that you would push back on?"*

Note any "I don't know" answers — those are documentation gaps to add to the Limitations Register.

**Decision rehearsal (8 min)**
Hand the decision-maker the pipeline's output (the map, the ranked list). Ask:
> "If you had to make a real intervention decision right now from this output, what would you decide, and why?"

Watch and note:
- Where did they hesitate?
- What context did they ask for that the output did not give them?
- What caveats did they invent in their own head to make the output usable?

Each of those is a Phase-5 finding.

**The Monday test (2 min)**
Close with the single most diagnostic question in the script:
> "Would you act on this output on Monday morning, in front of your colleagues, without further work?"

Possible answers and what to do with each:
- *"Yes, as-is."* — Strong positive Phase-5 signal. Record verbatim.
- *"Yes, with these caveats..."* — Capture caveats; they become entries in the Intended-Use Statement and Conditions for Non-Use.
- *"No, not yet, because..."* — Capture the "because". It dictates the iteration target.
- *"No, never; the pipeline answers the wrong question."* — Phase-5 kill signal. Record verbatim.

**Close (1 min)**
> "Thank you. We will write up what you said and send it back to you for verification before any decision is made. Nothing leaves this room as a recommendation until you have seen the write-up."

---

## Appendix B — One-Sentence Memorability

If the student forgets everything else, they should remember:

> **Phase 4 asks: did the model work? Phase 5 asks: did the pipeline answer the question the decision-maker actually has, in a form they can act on, with caveats they can defend? Phase 5 starts only after the Phase-1 business success criteria are on the table, and ends only after a named decision-maker has said, on the record, whether they would use the output on Monday.**

---

## References (skill brief)

Chapman, P., Clinton, J., Kerber, R., Khabaza, T., Reinartz, T., Shearer, C., & Wirth, R. (2000). *CRISP-DM 1.0: Step-by-step data mining guide* (esp. pp. 28–31). https://www.kde.cs.uni-kassel.de/lehre/ws2012-13/kdd/files/CRISPWP-0800.pdf

Kahneman, D. (2011). *Thinking, fast and slow.* Farrar, Straus and Giroux.

Madaio, M. A., Stark, L., Wortman Vaughan, J., & Wallach, H. (2020). Co-designing checklists to understand organizational challenges and opportunities around fairness in AI. *CHI '20.* https://doi.org/10.1145/3313831.3376445

Mitchell, M., Wu, S., Zaldivar, A., Barnes, P., Vasserman, L., Hutchinson, B., Spitzer, E., Raji, I. D., & Gebru, T. (2019). Model cards for model reporting. *FAT\* '19.* https://doi.org/10.1145/3287560.3287596

Pineau, J. et al. (2021). Improving reproducibility in machine learning research. *JMLR, 22.* https://www.jmlr.org/papers/v22/20-303.html

Raji, I. D. et al. (2020). Closing the AI accountability gap: Defining an end-to-end framework for internal algorithmic auditing. *FAT\* '20.* https://doi.org/10.1145/3351095.3372873

Sambasivan, N. et al. (2021). "Everyone wants to do the model work, not the data work": Data cascades in high-stakes AI. *CHI '21.* https://doi.org/10.1145/3411764.3445518

Sculley, D. et al. (2015). Hidden technical debt in machine learning systems. *NIPS 2015.* https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems

Studer, S. et al. (2021). Towards CRISP-ML(Q). *Machine Learning and Knowledge Extraction, 3*(2), 392–413. https://doi.org/10.3390/make3020020

Voinov, A. & Bousquet, F. (2010). Modelling with stakeholders. *Environmental Modelling & Software, 25*(11).

Voinov, A. et al. (2018). Tools and methods in participatory modeling. *Environmental Modelling & Software, 109.* https://doi.org/10.1016/j.envsoft.2018.08.028

Hamilton, S. H. et al. (2022). Fit-for-purpose environmental modeling. *Environmental Modelling & Software.* https://www.sciencedirect.com/science/article/abs/pii/S1364815221003200
