# Strategic Decision: Static Output vs. Interactive Tool

**Author:** Alex (Product Manager)
**Date:** 2026-05-10
**Status:** Recommendation
**Decision needed by:** Session 3 kickoff (defines remaining 5 sessions of build scope)
**Audience:** Group 4 team + seminar instructor

---

## TL;DR

**Recommendation: Tier 2 (Interactive Static).** Polish what we already have — a Folium-based HTML map plus companion documents — and stop there. Do not build Tier 3.

The planner audience does not need a configurable scenario engine. They need a defensible, weight-robust shortlist they can paste into a budget memo. We already have the substrate for that. The remaining work is fixing three known data bugs, sharpening the legend and footnotes, and producing a one-page printable companion. Estimated effort to ship Tier 2 well: **5–7 person-days of focused work**, which fits inside the seminar runway. Building Tier 3 would consume 25+ person-days, require infrastructure the team has not committed to operating, and produce a worse seminar artefact because the methods story would be drowned out by app plumbing.

The rest of this doc walks through the reasoning so the team can disagree with specifics.

---

## 1. What would make this a TOOL rather than a static output?

A static output is **read once, decision made, file archived.** A tool is **opened repeatedly, state changes between sessions, decisions are conditional on inputs the user controls.**

The minimum capability that flips this project from "report" to "tool" is **persistent, user-controlled state that changes the output.** Concretely, the smallest version of "tool" for this audience would be:

> A planner opens the app, **adjusts the weight on sealed-surface vs. heat vs. canopy**, sees the top-15 list update live, **filters to a single district** (e.g. Sant Andreu), and **exports the resulting shortlist as a PDF memo with their name and the timestamp** that they can attach to a budget submission.

That is the floor. Anything less than re-rankable, filterable, exportable is just an interactive viewer (Tier 2). Anything more — saved scenarios across sessions, multi-user comparison, vintage history, login — is a stateful application (Tier 3).

**The single feature that defines the tier boundary:** does the user's input change the output that other users see, across sessions, with version history? If yes → tool. If no → static (interactive or otherwise).

---

## 2. What is the planner actually doing with this?

I want to push back hard on solutioning before we map this. Let me write it out as concrete user actions, grounded in what `docs/output-sketch-v0.md` says the planner already knows and doesn't know.

### Action 1: "Where should the next de-paving line go?"

- **Input:** Planner opens the map. Wants to know which 3–5 zones in Sant Martí are the strongest de-paving candidates because that's the budget line they're allocating this cycle.
- **Output they need:** Filtered view of Sant Martí cells, ranked, with sealed-surface sub-score visible per cell, intervention type pill, and the limitations footer.
- **Decision:** "I'll route this cycle's de-paving budget toward zones 3, 7, and 11 because they have highest sealed-surface barrier in our district."
- **Tier required:** Tier 2 handles this. The planner clicks district boundaries, sees the cells, reads popups. No re-weighting needed.

### Action 2: "Defend rank #4 to a district council that asked why their neighborhood scored lower."

- **Input:** Planner pulls up zone #4's record.
- **Output they need:** Per-zone sub-scores, the assumption list, a one-line plain-language rationale, and the explicit "what this map cannot claim" caveat.
- **Decision:** "I can show the council the four sub-scores and explain why this zone outranks theirs, without hiding behind a black box."
- **Tier required:** Tier 1 or Tier 2 — this is just transparent record-keeping. We already have the data.

### Action 3: "Stress-test the ranking before I commit."

- **Input:** Planner is suspicious that the ranking is just an artefact of one weight choice.
- **Output they need:** Side-by-side comparison of three weighting scenarios (equal, sealed-dominant, heat-dominant) showing whether the same zones surface.
- **Decision:** "The ranking is robust across scenarios — I'm comfortable defending it."
- **Tier required:** **We already produced this** — `outputs/sensitivity_comparison.png` shows Jaccard = 1.0 across scenarios. Tier 2 surfaces it. Tier 3 would let them compute a *new* scenario, which is overkill given the result is already weight-robust.

### Action 4: "Cross-reference with the existing Eixos Verds plan."

- **Input:** Planner overlays our priority zones against published Eix Verd alignments (Consell de Cent, Pi i Margall) to see if our shortlist agrees with established corridors.
- **Output they need:** Map with both our priority zones and the planned Eixos Verds layer toggleable.
- **Decision:** "Three of our top-15 fall on planned Eix Verd corridors — that's a sanity check that our method isn't producing arbitrary geography."
- **Tier required:** Tier 2 with a layer toggle. This is a *very* high-value polish that we don't currently have.

### Action 5: "Paste the shortlist into a budget memo."

- **Input:** Planner needs to attach the priority list to an internal Ajuntament budget submission.
- **Output they need:** A printable, citable, one-page PDF with the top-15 table, the map, the citation block, and the limitations footer.
- **Decision:** "I attach this to my memo. If anyone questions it, the methodology is in the companion doc."
- **Tier required:** Tier 1 or Tier 2 — this is a static printable. The PDF *is* the deliverable for the budget cycle.

### What the planner is NOT doing

I want to name what we should *not* assume the planner does, because every assumption here drives scope.

- **They are not iterating on weights weekly.** They run a budget cycle every 12+ months. The output is consulted at decision time, not continuously.
- **They are not multi-user collaborating in real time** on the scoring. Internal review happens by emailing PDFs, not by shared dashboards.
- **They are not versioning scenarios across cycles.** The next cycle they want a *new* analysis with refreshed data — not the same app with saved old scenarios.
- **They are not training new analysts on the tool.** Onboarding a tool-based workflow into a municipal team takes years and is out of scope for a seminar deliverable.

This last point is the most important. The fantasy version of Tier 3 — "the Ajuntament adopts our app and uses it for years" — is not how municipal procurement, IT security, or data-governance actually works. A seminar project does not become production municipal infrastructure. Pretending it might leads to over-engineering.

---

## 3. The 3 architectural implications of going Tier 3 (Live Tool)

Spelling these out concretely so the team understands what "we go full tool" actually entails.

### Implication 1: A backend service with a persistent compute layer

We would need a server (FastAPI or Flask) that re-runs the scoring pipeline on user-supplied weights *because* the planner-supplied weights need to compute a new composite per zone across all 495 grid cells, and that computation is too heavy to run client-side in a useful time. Today, the pipeline runs in notebooks; for a tool, it has to run on demand behind an API.

- **Specific component needed:** a `POST /score` endpoint that accepts `{w_sealed, w_lst, w_ndvi, w_mismatch, district_filter}` and returns a re-ranked GeoJSON.
- **Why:** because Action 1 (filter by district) and the hypothetical Action 6 (re-weight) both require server-side recomputation across the full grid, not just a client-side filter on a precomputed top-15.
- **Hidden cost:** someone has to host this. Render free tier sleeps, Heroku free tier is gone, and the team has not committed to operating a cloud account.

### Implication 2: A persistence layer for saved scenarios and exports

If saving scenarios is part of "tool," we need a database — even a tiny one — to associate a scenario name + weights + timestamp + creator with a persistent record that survives a server restart.

- **Specific component needed:** a SQLite or Postgres table with `(scenario_id, name, weights_json, created_at, created_by)` plus a blob store for generated PDF memos.
- **Why:** because Action 5 (export memo) becomes meaningful only if the memo persists with a stable URL. Otherwise the planner downloads a PDF and the "tool" is just a one-shot generator wrapped in a UI — at which point it isn't really a tool.
- **Hidden cost:** auth. As soon as we have saved state, we have "whose state is it" — which means user accounts, password hashing, session management, and the security review that comes with any of that.

### Implication 3: A versioning model for the underlying data vintage

The scoring depends on Urban Atlas (2018/2021), Sentinel-2 (2024 composite), Landsat (2024 composite), Ajuntament tree inventory (2024-Q4). When any of these refresh, scenarios saved against the old vintage become incomparable to scenarios saved against the new one — silently and dangerously.

- **Specific component needed:** a `data_vintage_id` foreign key on every saved scenario, plus an explicit UI badge "computed against vintage 2026-Q1" so a planner doesn't compare old and new scenarios as if they were equivalent.
- **Why:** because the *whole point* of a tool over a static output is repeated use — and repeated use across data refreshes without versioning produces wrong answers. This is the failure mode that would actually embarrass us in front of the Ajuntament.
- **Hidden cost:** data pipeline orchestration. Tier 3 isn't done when the app works; it's done when the data refresh process is documented, automated, and version-tagged.

**These three implications aren't optional add-ons.** Skip any one of them and Tier 3 becomes a liability rather than an asset. That is exactly why I don't recommend going there with this team and timeline.

---

## 4. The Three Tiers — gain, loss, effort

### Tier 1 — Static (PDF map + companion docs)

- **What it is:** Printable PDF with the top-15 map, the per-zone scoring table, citation block, limitations footer. Read once, attached to a memo, archived.
- **Gained:**
  - Zero infrastructure. No hosting, no auth, no maintenance.
  - Forces the team to write the methods story tightly because there's no UI to hide behind.
  - Matches actual municipal-procurement reality — PDFs travel through email and intranets without IT review.
- **Lost:**
  - No layer toggling, no popup detail, no district-filtering UX.
  - The 2,165 network islands and the bridge layer become hard to render meaningfully on a printed page.
  - Loses much of what we already built — the Folium map currently exists and works.
- **Effort:** 2–3 person-days. Mostly polish, layout, and PDF export of existing data.

### Tier 2 — Interactive Static (HTML with Folium-style interactivity)

- **What it is:** What we have now (`outputs/priority_map.html`, `outputs/priority_zones.html`, `outputs/sensitivity_comparison.png`, `outputs/network_spread.html`, `outputs/limitations.md`), plus a printable PDF companion for the budget-memo use case. Layer toggles, popups, search-by-district, click-to-detail. **No server. No state. The page is a single HTML file.**
- **Gained:**
  - All five planner actions in §2 are supported, except for arbitrary re-weighting (which we explicitly don't need — Jaccard = 1.0 across scenarios already shows the ranking is weight-robust).
  - The HTML map is shareable as a single file, runs in any browser, no install.
  - Methodology and interactivity coexist — the planner can both browse and read.
  - Reuses the existing Folium pipeline; no rebuild required.
- **Lost:**
  - No saved scenarios. Each visit starts fresh.
  - No multi-user comparison. No vintage history.
  - The "scenario builder" fantasy — but again, the data shows we don't need it.
- **Effort:** **5–7 person-days.** Breakdown:
  - Fix the three blocking data bugs from `output-quality-report.md`: sealed_pct raster repair, bridge_score recomputation, colonisation_uncertain threshold. **~3 days.**
  - Add Eixos Verds overlay layer (Action 4 above) — high-leverage, low-effort polish. **~1 day.**
  - Generate one-page printable PDF companion from the same data (Action 5). **~1 day.**
  - Polish legend, footnotes, the "rank 15 anomaly" explanation noted in the quality report, and the AM-uniformity tooltip. **~1 day.**
  - Buffer for review and revision. **~1 day.**

### Tier 3 — Live Tool (stateful application)

- **What it is:** Backend API + frontend SPA + database + auth + data-vintage versioning + scenario save/load + memo export with stable URLs. Real product engineering.
- **Gained:**
  - Adjustable weights, saved scenarios, multi-user, comparable analyses across vintages, exportable memos with traceable IDs.
  - A genuinely impressive seminar demo.
- **Lost:**
  - Methods focus. The seminar is about *data understanding and pipeline reasoning*, not Flask routing and React state.
  - 4–8 weeks of team capacity into infrastructure that nobody will operate after the seminar ends.
  - The team's energy. Mixed-skill team + first-time backend work + tight deadline = high probability of a half-finished app that demos badly.
- **Effort:** **25–40 person-days minimum.** And that's optimistic. Breakdown:
  - Backend API (FastAPI, scoring endpoint, district filter, auth scaffolding): 8–10 days.
  - Frontend SPA (React or Vue, map component, weight sliders, scenario save UX): 8–12 days.
  - Database + persistence + scenario versioning: 3–5 days.
  - Auth (even basic token auth): 2–3 days.
  - Hosting, CI, env management: 2–3 days.
  - Data vintage versioning + safety badges: 2–4 days.
  - Bug-fixing, integration, polish: 5–8 days minimum on top.
  - **And** we still have to fix the same three data bugs as Tier 2.

---

## 5. Recommendation: Tier 2

**Build Tier 2. Polish what exists. Do not build Tier 3.**

### Why Tier 2 over Tier 1

Because we already have the Folium map running and it's the single highest-value artefact for the planner — they can click a zone, read its sub-scores, defend the rank to a council, and toggle the network-island layer to see the bridge logic. Throwing that away to print a PDF is a regression. Tier 1 is the right floor only if the team is exhausted and we need the smallest possible thing that ships; we are not in that situation.

That said, **Tier 2 should produce a Tier-1-style printable PDF as one of its companion outputs.** The planner's Action 5 — "paste the shortlist into a budget memo" — is genuinely served best by a printable. So Tier 2 = Tier 1 + Folium, not Tier 2 *instead of* Tier 1.

### Why not Tier 3

Three reasons, in order of weight.

1. **The seminar audience is grading methods, not infrastructure.** Spending 4 weeks on a backend that nobody operates after the deliverable is misallocated team capacity. The seminar artefact is stronger if the team can defend every line of the scoring logic, not if they can demo a slick app whose pipeline they half-understand.

2. **The planner audience does not need scenario configurability.** The data already shows Jaccard = 1.0 across three weighting scenarios — the ranking is weight-robust. Building a weight slider for a planner who doesn't need to slide weights is solving an imagined problem. The features the planner *actually* uses (district filter, popup detail, sensitivity comparison, printable export) are all Tier 2 features.

3. **The team is 4 students with mixed skills.** A live tool requires backend Python, frontend JS, hosting ops, auth handling, and data ops — five distinct skill bands. If even one of those is shaky, the project ships a broken app instead of a polished static. The probability-weighted outcome of attempting Tier 3 is *worse* than the probability-weighted outcome of Tier 2, regardless of upside ceiling.

### What I'd say no to, explicitly

To make this concrete, here is the "what we are NOT building" list:

| Request | Reason for deferral | What would change my mind |
|---|---|---|
| Weight-adjustment sliders | Jaccard = 1.0 across scenarios; ranking is weight-robust. Sliders solve a problem the data doesn't have. | If post-bug-fix Jaccard drops below 0.7, weight choice becomes a real decision and sliders become useful. |
| Saved scenarios / login | The planner is on a 12-month budget cycle, not a daily session. State across sessions is overhead, not value. | If the Ajuntament formally adopts and asks for it. They won't, in a seminar window. |
| Live data refresh | Snapshot is documented in problem brief as the scope. Live refresh is a different project. | Out of scope for v1. Revisit as a "future work" line in the seminar deck. |
| Multi-user comparison | The user is a single planner producing a memo, not a workshop facilitator. | Not unless we get user-research signal that two planners are comparing in real time. We don't have that. |
| Mobile responsive | Planners use desktop GIS. Mobile usage is near-zero for this workflow. | Out of scope. Document as a "v2" note. |

### The one thing this analysis depends on

**Confidence: ~75%.** The biggest uncertainty is whether the seminar instructor or the imagined Ajuntament audience would in fact be more impressed by a Tier 3 demo than a Tier 2 polished artefact. I'm assuming they grade *methodological clarity and audience fit*, not *production-app polish*. If the instructor's rubric explicitly rewards interactivity beyond what Tier 2 offers, that would shift the recommendation. Worth a 10-minute conversation to confirm before locking scope.

I'm at 95%+ confidence that Tier 3 is the wrong call regardless. The 25% uncertainty sits between Tier 1 and Tier 2 — and even there, I think Tier 2 is the stronger artefact.

---

## 6. Next steps if Tier 2 is approved

1. **Today / Session 3:** Lock scope. Team agrees on Tier 2 + companion PDF. No further "should we add X" mid-build.
2. **Days 1–3:** Fix the three blocking data bugs (`sealed_pct`, `bridge_score`, `colonisation_uncertain` threshold).
3. **Day 4:** Add Eixos Verds overlay layer to the Folium map.
4. **Day 5:** Generate one-page printable PDF companion.
5. **Day 6:** Polish — legend, footnotes, AM-uniformity tooltip, district-guarantee footnote.
6. **Day 7:** Internal review, dry-run presentation, final fixes.
7. **Session 7:** Lock the deliverable. Ship.

If at Day 3 we are not on track to finish, scope cuts — in this order — are: skip the Eixos Verds overlay (Day 4), then skip the printable PDF (Day 5). Never cut the data-bug fixes.

---

## Appendix: Documents reviewed

- `docs/problem-brief.md` — establishes audience, decision being supported, success criteria.
- `docs/output-sketch-v0.md` — current static output design and explicit "top 3 actions" the output enables.
- `outputs/limitations.md` — what the current output cannot claim; relevant for scope of any tool.
- `outputs/output-quality-report.md` — three blocking data bugs that any tier must fix.
