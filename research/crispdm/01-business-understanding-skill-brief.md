---
name: business-understanding
description: Use at the very start of any data-pipeline or data-product project — before any data has been touched — to produce the twelve Phase-1 artifacts the project depends on (decision statement, decision unit, output specification, success criteria, risk register, glossary, cancellation criterion, intended use, product card draft, project plan). Triggers on phrases like "new project", "kick off", "Phase 1", "business understanding", "scope this", "frame this project", "what should we build", "where do we start", "we want to do something with X data", and any sentence whose subject is a technology or a dataset rather than a decision. Domain-agnostic by design — works for any pipeline project that produces a dataset, map, dashboard, or report consumed by a named human decision-maker. Hands off cleanly to the `earn-the-data` skill (Phase 2 — Data Understanding) once exit criteria are met. Refuse to invoke `earn-the-data` until the decision statement, decision unit, output specification, intended use, and cancellation criterion are all on disk.
trigger_phrases:
  - "new project"
  - "kick off a project"
  - "Phase 1"
  - "business understanding"
  - "frame this project"
  - "scope this"
  - "where do we start"
  - "what should we build"
  - "we want to do something with X"
  - "the brief is …"
  - "I want to use [technology] to [vague verb]"
  - "what's the problem we're solving"
---

# Business Understanding — Phase 1 of CRISP-DM

The principle is in the name: a data project that does not start by understanding the *business* — the decision, the decision-maker, the difference success would make — produces artifacts that look professional and fail the moment a stakeholder asks "what do we actually do with this?" This skill exists to block that failure mode by forcing twelve specific artifacts onto disk before any data is touched.

This is the upstream of `earn-the-data`. That skill insists: "anyone can find data; this skill is about earning the right to use it." This one insists: "anyone can build a data pipeline; this skill is about earning the right to build one."

## The anti-pattern this skill exists to prevent

> Open the dataset → run a notebook → produce a chart → invent the decision the chart supports → present.

This produces work that is technically defensible in isolation and strategically useless in context. Every step below exists to block it.

## Inputs required from the user

The skill cannot start without these five. If any is missing, the first action is to elicit it — not to proceed.

1. **A problem statement in the user's own words** (one to three sentences is fine — the looser, the more important Phase 1 becomes).
2. **A candidate decision-maker** — a named role at a named organisation that will use the output. ("Stakeholders" or "the team" is not an answer.)
3. **A candidate decision** — the action the decision-maker will take differently if the project succeeds.
4. **A rough domain** — what kind of data product (dataset, map, dashboard, report) and what subject area (urban, environmental, biodiversity, mobility, etc.).
5. **A timebox and resource constraint** — how long the project has, how many people, what the budget is (zero is a valid answer).

If the user supplies a technology ("we want to use LLMs / GIS / satellite imagery to …") in slot 1 instead of a problem, treat this as the solutionism anti-pattern and respond with: *"That's a technology, not a problem. What decision does someone need to make better?"*

## Sequential steps the skill walks the user through

The skill runs as a single pass. Steps may iterate internally but the pass does not stop partway. Each step produces named artifacts in a `phase-1/` directory at the project root.

### Step 1 — Frame the decision

Goal: collapse the user's problem statement into a single, unambiguous decision sentence.

Action: ask the user to complete this sentence and write it to `phase-1/decision-statement.md`:

> *"This data product will help [decision-maker role] at [organisation] decide [decision] at [cadence] by [mechanism]."*

Socratic questions:
- Who is the named individual or role? Not "stakeholders." A name.
- What is the specific decision? Not "understand" or "explore" — what action gets taken?
- At what cadence? (Annual budget cycle, weekly meeting, on-demand?)
- What is the current mechanism? (Intuition? Spreadsheet? Existing tool?)

If the user cannot fill all four slots, do not proceed. The slot they cannot fill is the artifact-quality problem the entire skill exists to surface.

Output: `phase-1/decision-statement.md` (one sentence + 3-4 sentences of context).

### Step 2 — Run the Heilmeier catechism

Goal: stress-test the framing in plain language.

Action: pose the eight Heilmeier questions to the user, one at a time, and write the answers to `phase-1/heilmeier.md`. The eight: (1) What are you trying to do, in plain words, no jargon? (2) How is it done today, what are the limits? (3) What is new in your approach, why will it succeed? (4) Who cares — what difference will it make? (5) What are the risks? (6) How much will it cost? (7) How long will it take? (8) What are the mid-term and final exams for success?

If any answer is "I don't know," that becomes a Phase-1 task — either elicit it from the sponsor, or surface it as a Phase-1 risk.

Output: `phase-1/heilmeier.md` (eight Q&A blocks).

### Step 3 — Apply Five Whys to the surface request

Goal: distinguish symptom from decision.

Action: take the user's initial request (slot 1) and ask "why?" five times in succession, each time on the previous answer. Write the chain to `phase-1/five-whys.md`. If the fifth answer surfaces a different decision than the one in `decision-statement.md`, update the decision statement.

Socratic prompt: *"You said you want X. Why? … And why does that matter? … And why does that matter?"*

Output: `phase-1/five-whys.md` (five-step chain + revised decision statement if needed).

### Step 4 — Determine the decision unit

Goal: produce the single most load-bearing handoff artifact to Phase 2.

Action: ask the user to specify the *smallest spatial, temporal, and spectral unit at which claims will be made*. Examples:
- Spatial: city block (~100 m), neighbourhood (~500 m), municipality, region
- Temporal: hourly, daily, seasonal, annual
- Spectral / thematic: a specific quantity (heat, NDVI, species presence, modal share)

The decision unit is *not* what data the project has — it is what the decision requires. The 2× resolution rule in `earn-the-data` will be applied against this number.

Output: `phase-1/decision-unit.md` (spatial unit + temporal unit + spectral / thematic unit, each with a 1-sentence justification).

### Step 5 — Specify the output

Goal: replace the missing "model specification" with a "data product specification."

Action: ask the user to write the schema and properties of the artifact the project will publish. Write to `phase-1/output-spec.md`:
- Format (GeoJSON, CSV, PDF report, interactive dashboard, etc.)
- Schema (fields, types, units, coordinate reference system if spatial)
- Resolution (spatial / temporal / thematic) — must be at least as fine as the decision unit
- Coverage (extent in space and time)
- Refresh cadence
- Distribution mechanism (where it lives, how it is accessed)
- Licence (CC-BY, internal-only, etc.)

Socratic question: *"If a stranger downloaded this file in two years, what would they need to know to use it correctly?"* — the answer becomes the product card draft (Step 9).

Output: `phase-1/output-spec.md`.

### Step 6 — Define success criteria (binary, numerical, dated)

Goal: replace adjectives with numbers.

Action: produce two tables in `phase-1/success-criteria.md`:

| Business Success Criterion | Numerical Threshold | Deadline | Owner |
|---|---|---|---|
| (e.g. shortlist used in budget decision) | (used in ≥ 1 cycle) | (next FY) | (named sponsor) |

| Data-Product Success Criterion | Numerical Threshold | Verification Method |
|---|---|---|
| Coverage | ≥ 95% of decision units have non-null values | spatial coverage check |
| Freshness | input data ≤ N months old at publication | metadata audit |
| Reproducibility | each output value reproducible from published code | re-run on clean clone |

Refuse adjectives. *"Useful," "actionable," and "insightful" are not success criteria.* Each row must be a number with a deadline and an owner.

Output: `phase-1/success-criteria.md`.

### Step 7 — Inventory resources, constraints, assumptions

Goal: surface what the project has and what it does not.

Action: produce four short sections in `phase-1/situation.md`:
- **Resources**: people (named, with time commitments), data (named primary sources), compute, software, budget.
- **Requirements**: schedule, comprehensibility, legal, ethical (intended use / intended user / prohibited uses), security, deployment environment.
- **Assumptions**: things being taken on faith that, if wrong, would invalidate the project (e.g. *"we assume the planner reviews shortlists at all"*).
- **Constraints**: hard limits (e.g. *"no frontend deliverable, per teacher constraint"*; *"output must be reproducible from open code"*).

Output: `phase-1/situation.md`.

### Step 8 — Build the risk register and define the cancellation criterion

Goal: name what could kill the project and the rule that would stop it.

Action: produce a risk register in `phase-1/risks.md` with at least five rows:

| Risk | Likelihood (L/M/H) | Impact (L/M/H) | Owner | Mitigation | Triggers cancellation? |
|---|---|---|---|---|---|

At least one row must have *"Triggers cancellation? = Yes"* — the explicit condition under which the project should be stopped rather than continued. Per CRISP-ML(Q), the absence of a cancellation criterion is itself a Phase-1 defect.

Optional Socratic add-on: *pre-mortem*. Ask the user: *"Imagine it is six months from now and the project has clearly failed. What happened?"* Fold the answers into the register.

Output: `phase-1/risks.md` including a clearly marked "Cancellation criterion" section.

### Step 9 — Draft the terminology glossary and the product card

Goal: defuse the two silent-failure modes (vocabulary collisions, misuse of the published artifact).

Action A — glossary: produce `phase-1/glossary.md`, two columns: term, meaning. Include every term that the sponsor and the data team have used differently, even informally. Cross-reference where the same concept has multiple names (e.g. "block" vs. "Superilla" vs. "Manzana").

Action B — product card draft: produce `phase-1/product-card-draft.md` with these sections (adapted from Gebru et al. 2021 datasheet template plus Mitchell et al. 2019 model card template):
1. What is this artifact?
2. Intended use (what decisions it supports)
3. Intended user (named role)
4. Out-of-scope uses (what it must not be used for)
5. Known limitations (initial set; expanded by `earn-the-data`)
6. Provenance summary (inputs, transformations — filled in by later phases)
7. Versioning and contact

This is the draft. Phase 2 (`earn-the-data`) will extend it with data-source-specific limitations. Phase 6 (Deployment) finalises it.

Outputs: `phase-1/glossary.md`, `phase-1/product-card-draft.md`.

### Step 10 — Produce the project plan and exit-criteria checklist

Goal: define what done looks like for Phase 1 and the rough shape of subsequent phases.

Action: produce `phase-1/project-plan.md` with the phases (Phase 2 through Phase 6 of CRISP-DM, plus any phase-0 acquisition work), expected duration of each, decision gates between them, and the initial tool / technique posture (e.g. *"Python + GeoPandas + DuckDB; no commercial tools"*).

Then produce `phase-1/exit-checklist.md` — a copy of the binary exit-criteria checklist below. Each must be ticked before the skill hands off to `earn-the-data`.

Outputs: `phase-1/project-plan.md`, `phase-1/exit-checklist.md`.

## Deliverables produced

After a clean pass, the `phase-1/` directory at the project root contains:

```
phase-1/
├── decision-statement.md        # Step 1 — one-sentence decision + context
├── heilmeier.md                 # Step 2 — eight-question stress test
├── five-whys.md                 # Step 3 — symptom-to-decision chain
├── decision-unit.md             # Step 4 — spatial / temporal / spectral unit
├── output-spec.md               # Step 5 — what the project publishes
├── success-criteria.md          # Step 6 — business + data-product, numerical
├── situation.md                 # Step 7 — resources, requirements, assumptions, constraints
├── risks.md                     # Step 8 — risk register + cancellation criterion
├── glossary.md                  # Step 9a — terminology
├── product-card-draft.md        # Step 9b — datasheet/model-card hybrid for the output
├── project-plan.md              # Step 10a — phases, gates, tool posture
└── exit-checklist.md            # Step 10b — binary exit criteria, all ticked
```

The skill must also surface a 1-page summary of the twelve artifacts inline, with the decision statement, the decision unit, and the cancellation criterion as the headline.

## Quality checks / exit criteria (binary — all must pass)

The skill refuses to hand off to `earn-the-data` until every box is ticked. Each is binary.

- [ ] **Decision statement** — can you state the decision in one sentence with all four slots filled (role, decision, cadence, mechanism)?
- [ ] **Named decision-maker** — is there a named individual or role at a named organisation, not "stakeholders"?
- [ ] **Decision unit** — are the spatial, temporal, and thematic units written down as numbers, not adjectives?
- [ ] **Output specification** — does the schema exist? Are units, CRS (if spatial), and refresh cadence specified?
- [ ] **Numerical success criteria** — is every success criterion a number with a deadline? No adjectives?
- [ ] **Intended use and intended user** — are both written in the product card draft?
- [ ] **Out-of-scope uses** — are at least two named in the product card draft? (If none, the team has not thought about misuse.)
- [ ] **Risk register** — at least five risks, each with likelihood, impact, owner, mitigation?
- [ ] **Cancellation criterion** — is there at least one risk marked "Triggers cancellation = Yes" with a clear condition?
- [ ] **Glossary** — does it contain every term the sponsor and the data team used differently?
- [ ] **Resources inventory** — is every resource named (no "the team," no "the data")?
- [ ] **Constraints** — are hard limits named, including what is *not* in scope?

If any box is unticked, do not proceed. Return to the relevant step.

## Anti-patterns to block (refuse to proceed past)

The skill should detect these patterns in the user's input or in its own draft artifacts and refuse to advance until they are corrected.

**Solutionism.** Subject of the project is a technology, not a decision. Diagnostic: the sentence "we want to use X" appears in slot 1 of the inputs. Block: respond *"X is a tool, not a problem. What decision does someone need to make better with it?"*

**Missing decision-maker.** Decision statement names "stakeholders," "users," or "the team." Block: refuse to write `decision-statement.md` until a named role at a named organisation is supplied.

**Adjective success criteria.** A success criterion uses any of: useful, actionable, insightful, better, more accurate, novel, interesting. Block: respond *"That is not a success criterion. What number, by when?"*

**Pre-emptive data hunting.** User wants to start with "let me show you the data we have." Block: respond *"Phase 1 is not done. We have not defined the decision. Data comes later."* (Note: this is the exact handoff condition for `earn-the-data` — it is enforced from both sides.)

**Vocabulary drift.** The same term is used with two different meanings inside the Phase-1 artifacts. Block: stop and add both meanings to the glossary, then choose one.

**Missing cancellation criterion.** The risk register has no row marked "Triggers cancellation = Yes." Block: require at least one. Per Studer et al. (2021), the absence is a Phase-1 defect.

**No out-of-scope uses.** Product card draft lists zero out-of-scope uses. Block: require at least two. (Examples: "not for individual-property-level decisions"; "not for regulatory or legal use.")

**Scope creep through ambiguity.** Constraints section names what is in scope but not what is out. Block: require an explicit out-of-scope list.

**Hand-off mentality.** The sponsor was not in the room (or in the loop) for any of Steps 1, 3, 5, 6, 8. Block: flag explicitly that the artifacts will need sponsor sign-off before Phase 2 begins.

## Handoff to next phase (Phase 2 — Data Understanding via `earn-the-data`)

Once all exit-checklist boxes are ticked, hand off to `earn-the-data` with the following state passed forward:

**Mandatory handoff payload** (read by `earn-the-data` at its Step 1 and Step 10):
- `phase-1/decision-statement.md` — used to frame the brief revisit at `earn-the-data` Step 10.
- `phase-1/decision-unit.md` — used to apply the 2× resolution rule at `earn-the-data` Step 4.
- `phase-1/output-spec.md` — used to score Resolution and Coverage on the `earn-the-data` rubric at Step 5.
- `phase-1/product-card-draft.md` — used to fill the Uses sections of the data sheets at `earn-the-data` Step 6.

**Recommended handoff payload** (strengthens Phase 2 but not strictly required):
- `phase-1/situation.md` — informs the inventory of resources.
- `phase-1/risks.md` — informs candidate-dataset risk scoring.
- `phase-1/glossary.md` — disambiguates field semantics.

**Invocation instruction.** After confirming the exit checklist passes, invoke `earn-the-data` with: *"Phase 1 artifacts are in `phase-1/`. Decision unit is in `phase-1/decision-unit.md`. Begin Phase 2."*

If `earn-the-data` returns at its Step 10 with a "No — question cannot be answered" finding, the appropriate response is to *return to this skill's Step 1* and reframe the decision against what the data can actually support. This is the iterative property CRISP-DM is built around; it is not a failure.

## Out of scope for this skill

- Choosing or evaluating specific datasets — that is `earn-the-data`.
- Profiling data — that is `earn-the-data` Step 9 plus the user's notebooks.
- Building the pipeline — that is later phases.
- Frontend / UI design — out of scope per project direction.
- Writing the project plan in tool-specific detail (Gantt, Jira) — produce the phased plan, not the ticket breakdown.

## Why the discipline matters

Empirical evidence is consistent: between 60% and 87% of data-science / analytics projects fail to deliver business outcomes, and the modal failure is not technical but definitional (Gartner 2017 in Data Science PM 2024; VentureBeat 2019; NewVantage Partners surveys). The cost of a misframed problem grows monotonically through CRISP-DM's six phases; correcting it in Phase 6 is roughly an order of magnitude more expensive than catching it in Phase 1. The twelve artifacts above exist because each catches a specific failure mode that the literature has documented at scale. Skipping any of them does not save time; it defers the work to a phase where it costs more.

## References (short list)

- Chapman et al. (2000). *CRISP-DM 1.0: Step-by-step data mining guide.* — original definitions of the four tasks and twelve outputs.
- Studer et al. (2021). Towards CRISP-ML(Q). *Machine Learning and Knowledge Extraction* 3(2), 392–413. — quality-assurance overlay; cancellation-criterion requirement.
- Martínez-Plumed et al. (2021). CRISP-DM twenty years later. *IEEE TKDE* 33(8), 3048–3061. — exploratory-vs-goal-directed trajectories.
- Schröer, Kruse & Gómez (2021). A systematic literature review on applying CRISP-DM. *Procedia CS* 181, 526–534. — empirical record on Phase-1 under-specification.
- Saltz (2021). CRISP-DM for data science: Strengths, weaknesses, next steps. — Phase-1 weakness analysis.
- Taylor (2017). Four problems in using CRISP-DM. *KDnuggets*. — four failure modes (clarity, rework, hand-off, iteration).
- Hoerl, Kuonen & Redman (2022). Framing data science problems the right way. *MIT Sloan Management Review*. — decision-back framing.
- Gebru et al. (2021). Datasheets for datasets. *CACM* 64(12). — product card structure.
- Mitchell et al. (2019). Model cards for model reporting. *FAccT*. — model card structure (adapted for data products).
- Wilkinson et al. (2016). FAIR Guiding Principles. *Scientific Data* 3. — Phase-1 publishing posture.
- DARPA. *The Heilmeier Catechism.* — eight-question elicitation tool.
- Ulwick / Strategyn. *Jobs-to-be-Done framework.* — stakeholder-need elicitation.
- IBM (2021). *SPSS Modeler CRISP-DM Guide.* — operational expansion of original artifacts.
