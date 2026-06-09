# Grain Recommendation: Decide at 400 m, Execute at the Section

> Formal resolution of the project's central tension, triggered by the multi-agent planner
> evaluation (`planner-evaluation.md`). All four reviewers independently reached the same conclusion.

## The problem in one paragraph

The product exists at two spatial grains and they disagree. At the **400 m grid** the headline claim
holds — people-weighting materially re-orders priorities versus the naive plane-density rule (T1:
Spearman 0.89, top-15 Jaccard 0.30; burden margin +4.6/+9.3 points). At the **census-section grain**
the operational unit a planner acts on the same claim **fails** its pre-registered test: priority is
~97% collinear with raw plane density (T1 Spearman **0.97**), the re-ordering survives only 1 of 3
sensitivity arms (T4), and the two grains agree at only **Spearman 0.47** (C1). The cause is MAUP: at
fine grain a few park-like sections with huge mature-plane clusters (rank-1 = Montjuïc) dominate, and
population can no longer move the top.

## The recommendation

**Make the priority *claim* at the 400 m grain; use the census section only as the *execution* unit.**

| Question | Grain | Why |
|---|---|---|
| *Which areas relieve the most exposure per cut?* (the analytical claim) | **400 m grid** | This is where people-weighting demonstrably beats the density rule; the claim survives its tests here. |
| *Where exactly do crews work, and which streets?* (the operational packet) | **census section → street worklist** | Sections are real administrative/operational units; streets come from the inventory. But this is *execution*, not a fresh priority claim. |

Concretely: a 400 m cell's priority should drive *which part of the city* to target; the section(s)
overlapping that cell, and their street worklists, are how that target is turned into a crew schedule.
The section ranking must **not** be presented as an independent "who is most important" claim — at that
grain it is essentially "where the most mature planes are."

## Why not just ship one grain?

- **400 m only:** not actionable — a planner cannot work a 400 m square (the original deployment gap).
- **Section only:** not defensible — it fails T1/T4; the people-weighting that justifies the whole
  product washes out. Shipping it as *the* priority would be the same over-claim the project exists to
  avoid.
- **Both, with this division of labour:** honest and useful — each grain does the job it can defend.

## How the tool reflects this

- A **persistent caveat strip** states it on the map (shipped): *"At section grain the ranking ≈ plane
  density (MAUP) — use sections to execute, claim priority at the 400 m grain."*
- The **400 m layer** is a first-class toggle, framed as the *evidence/claim* view.
- Section views and street worklists are framed as the *execution* packet, not a ranking (the street
  CSV carries this disclaimer).

## Bottom line

This is not a defect we are conceding; it is a measured property of zonal data that the project
surfaced in its own output and now handles explicitly. The division — **claim at 400 m, execute at the
section** — is the honest way to be both defensible and actionable at once.
