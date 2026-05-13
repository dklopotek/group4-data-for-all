# Storytelling Guidance — Mycorrhizal Barcelona for Planners

**Audience:** Capital-planning analysts at Ajuntament Espais Verds i Biodiversitat.
**Constraint:** They are not ecologists. They open QGIS, read budgets, sign off on Eix Verd allocations.
**Author:** Visual Storyteller, 2026-05-10

---

## 1. The 90-second story

**Beginning (15s) — The hook the planner already feels.**
Barcelona's street trees are dying under heat stress in predictable places. Replacing them is expensive, and the same blocks keep losing the same trees. The planner already knows this — they sign the replacement orders. The question they have not yet been handed a defensible answer to is not "where should we plant" but "where will what we plant actually root and live past year three."

**Middle (45s) — The leverage claim, with proof.**
The same 400m grid cells keep coming up across every weighting scheme we tried. Fifteen zones, mostly in Sants–Montjuïc and Sant Andreu, share three barriers in common: sealed ground, surface heat anomaly above 5°C, and thin canopy. These are the zones where a euro of de-paving, planting, or cooling spend has the highest expected leverage — not because the model is clever, but because the barriers are physically stacked there. We are not predicting fungi. We are mapping where the conditions are most hostile to anything below the surface working, and naming which intervention budget line addresses each barrier.

**End (30s) — The decision in front of them.**
The next Eixos Verds capital cycle has to route de-paving, cooling, and planting euros somewhere. This map gives a defensible shortlist with the intervention type pre-matched to the budget line. It does not claim to recover fungal networks. It claims that these fifteen zones are where the budget will do the most measurable work in the planner's own metrics: surface coolness, canopy gain, infiltration.

**Lead with this sentence:** *"Mature trees cost less than dead saplings. Here are fifteen places where the next ones will live."*

---

## 2. The three things to show, in order

**FIRST — the shortlist as a map.** Open with `priority_map.html`, zoomed to show the 15 numbered zones colour-coded by intervention type (de-paving / cooling / planting). One glance, one question answered: *where.* No legend gymnastics, no science yet. The planner sees a budget memo waiting to be written.

**SECOND — the proof layer.** `sensitivity_comparison.png`. The Jaccard = 1.0 result is the single most defensible thing in this whole project. Frame it plainly: *"We tried three different weighting philosophies. The same fifteen zones came up every time. The ranking is not a knob we tuned to get the answer we wanted."* This is what makes a council defence survive cross-examination.

**THIRD — the action layer.** The per-zone table from `priority_zones.html`, but reframed as a **memo template**: zone ID, district, intervention type, the one-line rationale, the budget line it maps to, the limitations footer. The planner copies this into a Word doc and it is already 80% of their submission.

Order matters because planners trust geography first, methods second, and instructions third. Reversing this loses them at the methods slide.

---

## 3. The "underground network" frame — without the wellness vibe

**Drop the mycelium language for this audience.** Reserve it for the academic appendix. To a planner, "mycorrhizal network health" reads as either jargon or yoga. Neither helps. The motto — *"an ecosystem that supports mycelium health is an ecosystem that supports the health of all beings"* — is true, but it is a *team-motivation* line, not a *planner-facing* line. Use it on the project poster, not in the budget memo.

**Translate the motto into infrastructure language. The metaphor that works: soil life is municipal plumbing.** Invisible, easy to break with surface work, expensive to replace, and the reason new tenants do or do not survive their first summer. The city's street trees are renters in that building — they cannot stay if the floor is sealed, the rooms are too hot, and the neighbouring rooms (other host trees) have emptied out.

That metaphor lets a planner translate the science into a sentence they would say out loud: *"If we don't fix the sealed surface and the heat, the trees we plant won't make it past year three, and we will be replanting forever."*

**The concrete outcome the planner cares about — in priority order:**

1. **Sapling survival rate at 5 years.** This is the metric that hits their budget directly. Replanting a failed sapling costs roughly 3–5× the original planting cost when you account for removal, soil repair, and re-establishment.
2. **Summer surface temperature reduction in pedestrian corridors.** Linked to the cooling-strategy KPI the Ajuntament already reports.
3. **Heritage tree survival under climate stress.** *Platanus x acerifolia* on Passeig de Gràcia is non-negotiable politically. Anything that protects the existing canopy is a winning frame.

Carbon is fourth, not first. Planners hear "carbon" so often it has stopped landing. Sapling survival is harder to dismiss because it is a line item.

---

## 4. The one image that wins the argument

**`sensitivity_comparison.png` — the weight-robustness chart.**

Counterintuitive choice. The pretty map is `priority_map.html`. But the planner has seen pretty maps before, and they have learned to distrust them because every consultant produces one. What they have *not* seen is a chart that proves the analyst tried three different weighting philosophies and got the same answer every time.

That chart is the proof of honest method. It says: *"We did not work backward from a preferred answer."*

Caveat: this image only wins if the team fixes the `sealed_pct` raster bug first (per `output-quality-report.md`, Fix 1). Right now Jaccard = 1.0 is partially an artefact of a constant sealed-surface input. Once the raster is repaired, expected Jaccard is 0.7–0.9 — which is *still* a winning argument and an *honest* one. Lock in the fix before the chart goes on a cover.

For the cover, `priority_map.html` rendered as a static PNG with the 15 zones numbered is the right second choice. Use it if the sensitivity chart cannot be made presentation-ready in time.

---

## 5. Tool game versus interaction — Alex is right, but for a deeper reason

**Hard no on gamification. Cautious yes on interaction.**

A planner reviewing a €4M budget allocation will not click through a tutorial level. The instant the artefact feels playful, the planner's risk-assessment frame engages and credibility collapses. Municipal planners read PDFs, not games. This is not a generational opinion. It is procurement reality.

But Alex's recommendation in `2026-05-10-tool-vs-static.md` already handles this correctly: Tier 2 is interactive *without* being a game. Layer toggles, popup detail, district filtering, Eixos Verds overlay — these are *transparency features*, not *play features*. They let the planner verify the shortlist against their own knowledge of the city. That is not gamification; that is decision support.

The reframe to use internally: **"Interactivity is for trust, not engagement."** Every click in our HTML should answer a question the planner is about to ask, not invite them to explore for fun.

The one gamification-adjacent idea that *does* survive: the "click any zone and see the one-line rationale" pattern. That is not a game. That is a courtroom defence rehearsal. Keep it.

---

## 6. The Remotion 60-second video

The user has a Remotion project ready at `C:\Users\Rafik\Documents\GitHub\group4-data-for-all\my-video`. The current composition (`src/Composition.tsx`, `AmanitaScene`) is a 4-second 1080×1080 mushroom-growth animation — a beautiful asset, but as it stands it is a *loading screen aesthetic*, not a planner pitch. Reuse the visual register (square format, calm green palette, organic easing) but rebuild the script entirely. Treat the video as the **opener for any presentation to the Ajuntament** — it earns thirty seconds of attention before the slides.

The Amanita motif itself should appear only once, briefly: a single mushroom rising at the moment the soil composite emerges in Scene 3 — a five-frame visual seasoning, not a centrepiece. Anything more reads as wellness content and undermines the budget-memo register.

**Six scenes, ten seconds each:**

**Scene 1 (0–10s) — The cost framing.**
Black screen. White text fades in: *"Barcelona plants thousands of street trees a year. In the hottest, most sealed zones, the same blocks keep losing them."* Slow zoom into a single grid cell drawn over an aerial of Barcelona. (Do not invent specific cost figures; keep the language qualitative until the team verifies actual Ajuntament replacement costs.)

**Scene 2 (10–20s) — The barrier reveal.**
The Barcelona basemap fades up. Three layers animate in sequence over the city: sealed surface (grey wash), heat anomaly (red glow), thin canopy (yellow stippling). Each layer takes ~3 seconds. Text caption per layer: *"Sealed. Hot. Bare."*

**Scene 3 (20–30s) — The stacking.**
All three layers compose into a single composite. Fifteen zones light up in white as the composite emerges. Caption: *"Fifteen zones stack all three barriers. This is where the next euro does the most work."*

**Scene 4 (30–40s) — The robustness proof.**
Cut to a clean animated version of `sensitivity_comparison.png`. Three columns animate in. The same fifteen zones glow green across all three. Caption: *"Three weightings. Same fifteen zones. Every time."*

**Scene 5 (40–50s) — The intervention match.**
The fifteen zones recolour from white to their intervention type — de-paving (blue), cooling (red), planting (green). Caption: *"Each zone matched to a budget line that already exists."*

**Scene 6 (50–60s) — The honest limit.**
Hold on the final map. Text overlay: *"This map does not predict ecological recovery. It identifies where capital spending faces the fewest barriers. The rest is the work."* Fade to project title and group attribution.

**No voiceover.** Music: low, ambient, no rhythm. Subtitles only. A planner watching this on their phone with sound off in a meeting room must still get every beat.

**Typography:** sans-serif, single weight, generous whitespace. Avoid any visual move that could read as "campaign video." This is municipal evidence, not advocacy.

---

## Closing principle

The single biggest storytelling failure mode for this project is **letting the underground-network mystique do the talking.** It makes the team feel clever and makes the planner feel sold-to. Strip it out of the user-facing materials. Keep it for the academic appendix where it belongs. The planner-facing story is short, geographic, and budget-anchored: *fifteen zones, three barriers, four intervention budget lines, same answer across three weightings.* That is the whole pitch.

If the planner can repeat that sentence after sixty seconds, the visuals worked.
