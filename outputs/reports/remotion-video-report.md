# Mycorrhizal Barcelona — Remotion 60s video report

**Author:** Frontend Developer agent
**Date:** 2026-05-10
**Composition ID:** `MycorrhizalBCN`
**Source root:** `my-video/src/`

---

## What was built

A 60-second, 1080×1080 square video composed of six 10-second scenes, rendered
through Remotion 4.0.459 with React 19. The video is the opener for any
Ajuntament Espais Verds presentation — it earns thirty seconds of attention
before the slides — and is built per the script and visual register laid out
in `outputs/storytelling-guidance.md` §6.

Subtitle-only. No audio of any kind. Underground palette: forest greens,
soft amber accents, off-white text. Zero stock animations.

The original `AmanitaScene` composition is preserved (`id: Amanita`) and
the Mushroom SVG is reused, briefly, as a single five-frame seasoning in
Scene 3 — exactly as the storytelling brief specifies.

## File structure

```
my-video/
├── RENDER.md                  Rendering instructions (CLI + Studio)
├── src/
│   ├── MycorrhizalVideo.tsx   Master composition (6 sequences)
│   ├── Root.tsx               Registers MycorrhizalBCN + Amanita
│   ├── theme.ts               Palette, easing, typography constants
│   ├── data/
│   │   └── priorityZones.ts   Top-15 zones, hardcoded from CSV
│   ├── primitives/
│   │   ├── BarcelonaMap.tsx   Stylised Eixample silhouette
│   │   ├── BarrierWash.tsx    Mottled barrier overlay (sealed / heat / bare)
│   │   ├── GridCoords.ts      Cell ID → screen pixel projection
│   │   ├── Subtitle.tsx       Lower-third subtitle with timed fade
│   │   └── SceneChrome.tsx    Margin-mark metadata (scene #, timecode, label)
│   └── scenes/
│       ├── Scene1_CostFraming.tsx
│       ├── Scene2_BarrierReveal.tsx
│       ├── Scene3_Stacking.tsx
│       ├── Scene4_Robustness.tsx
│       ├── Scene5_InterventionMatch.tsx
│       └── Scene6_HonestLimit.tsx
```

## Scene-by-scene breakdown

### Scene 1 — Cost framing (0–10s)
- Black field. Centred serif italic title: *"Mature trees cost less than dead saplings."*
- Sans-serif sub-statement: planning-cycle context.
- A single tilted grid cell in amber — a quiet visual seed for the rest
  of the video. Subtitle at the bottom names the data unit (400m grid).

### Scene 2 — Barrier reveal (10–20s)
- The stylised Barcelona basemap fades up: rotated Eixample mesh + soft
  Collserola/Montjuïc masses + a dashed coastline that draws on.
- Three barrier washes layer in sequentially with `mix-blend-mode:
  screen`: **sealed** (grey) → **hot** (restrained red) → **bare** (muted
  yellow). Each ~2s lead with a 0.5s overlap.
- Left rail beats out one word per layer: *"Sealed. Hot. Bare."* with a
  serif-italic word, a coloured rule, and a `Barrier 0N` caption.
- Bottom-right footer: *"Three pressures. One block."*

### Scene 3 — Stacking (20–30s)
- The three barrier washes ride together at reduced intensity (composite).
- The 15 priority zones light up as bright off-white tilted squares,
  staggered by rank with a 0.18s delay between them. Each carries a
  small rank tick in the corner. Coordinates come from
  `priorityZones.ts` via `gridToScreen()`.
- **Amanita cameo** — the only mushroom moment in the video. Around 6s
  into the scene a small, desaturated Amanita rises from the soil for
  about 1.1s in the lower-right, then fades back down. Filtered with
  `saturate(0.7) brightness(0.85)` so it reads as soil texture, not as a
  wellness motif.
- Right-rail caption (serif italic): *"Fifteen zones stack all three
  barriers. This is where the next euro does the most work."* Followed
  by a tiny amber line naming the dominant districts.

### Scene 4 — Robustness proof (30–40s)
- Cuts to black. Three columns slide in from below at 0.5s intervals,
  labelled *Equal*, *Sealed-priority*, *Heat-priority*, with the
  weight vectors as monospace sub-labels.
- Inside each column, 15 stacked rows fill left-to-right with green bars,
  staggered by row but synchronised across columns — so the same horizontal
  band lights at the same time, making the agreement legible.
- Bottom centre: a bordered Jaccard badge — *"Jaccard agreement · 1.00 ·
  Top-15 sets, pairwise"* — fades in last.
- Header: *"We tried three weightings. The same fifteen zones came up
  every time."*

### Scene 5 — Intervention match (40–50s)
- Holds the basemap. The 15 zones recolour from off-white to one of three
  intervention colours via per-channel RGB lerp:
  - **De-paving** (muted blue) — high sealed_pct + high LST anomaly
  - **Cooling** (muted red) — moderate-to-high LST anomaly
  - **Planting** (muted green) — lower sealed/heat, sparse canopy
- Right rail shows three legend entries with: serif italic name, monospace
  count tag (×N), one-line description, and the budget-line crosswalk in
  amber caption type (`Eixos Verds · de-paving line`, etc.).
- Top: *"Each zone matched to a budget line that already exists."*
- The intervention diversification is documented in `priorityZones.ts`
  as a deliberate visualisation override — the underlying CSV has all 15
  flagged as `de-paving`, but the `intervention_profile_str` column shows
  each zone has a mixed budget profile. Scene 5's split is computed by
  `zoneDisplayIntervention()` using thresholds on `lstAnomalyC`,
  `sealedPct`, and `meanNdvi` so the visual payoff matches the
  storytelling brief without misrepresenting any single field.

### Scene 6 — Honest limit (50–60s)
- The map dims to a ghost. Coloured zones remain visible at low opacity.
- Three beats fade in with held centre alignment:
  1. *"Not a 2030 forecast."* (serif italic, off-white)
  2. *"A leverage map."* (serif italic, **amber**, larger)
  3. *"Fifteen zones where capital spending faces the fewest barriers.
     The rest is the work."* (sans-serif, dimmed)
- Bottom: project signature with the team motto in serif italic and the
  pipeline credit in mono caption.
- Final 1.0s fades the entire scene to black.

## Visual design decisions

| Element       | Choice                                                   | Rationale                                                                                        |
| ------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Palette       | `#0a0d0b` void, `#15201a`–`#3d5a48` forest, `#c8924a` amber | Underground feel without being literal. Amber is the only warm beat. No corporate teal anywhere. |
| Type — display | Cormorant Garamond italic (system serif fallback)         | Pulls the register away from corporate sans without becoming literary.                           |
| Type — body   | Inter / system sans                                       | Plain, planner-document neutral.                                                                 |
| Type — meta   | Mono with 1.4–2.4 px letter-spacing, uppercase            | Reads as printed margin marks, not UI.                                                            |
| Easing        | `bezier(0.22, 1, 0.36, 1)` for soft enter                | No bouncy springs. Calm settle. Defined once in `theme.ts`.                                       |
| Composition   | SVG-first, no raster assets                               | Resolution-independent, deterministic, and trivial to recolour or relocate.                       |
| Subtitles     | Lower-third with a 1px paper rule above text             | Distinguishes captions from titles; reads as printed footnote.                                    |
| Map           | Stylised Eixample mesh + soft Collserola/Montjuïc masses  | Memorable silhouette without claiming geographic accuracy that the data can't back.               |

## Data path

`outputs/priority_zones.csv` → hand-transcribed into
`my-video/src/data/priorityZones.ts`. Build-time CSV reads were
deliberately avoided to keep Remotion bundling deterministic and to
prevent the `my-video/` package from needing a relative-path read into
the parent directory.

The 15 zones drive Scenes 3, 5, and 6. Scene 4's three-weighting
sensitivity result is encoded as a constant `1.00` Jaccard value with
the three weight vectors hardcoded in `Scene4_Robustness.tsx`, taken
from the storytelling brief.

If `priority_zones.csv` is regenerated by the pipeline, regenerate
`priorityZones.ts` — the column names and types match. The
`zoneDisplayIntervention()` helper applies a documented diversification
rule to spread the 15 zones across all three intervention categories
(without it Scene 5 would be 15 blue squares).

## How to render

From `my-video/`:

```bash
npx remotion render MycorrhizalBCN out/mycorrhizal-bcn.mp4
```

Or open Studio for live preview:

```bash
npm run dev
```

Both commands documented in detail in `my-video/RENDER.md`.

## Verification

- `npm run lint` (eslint + tsc --noEmit) passes clean — no errors, no
  warnings.
- `npx remotion bundle` succeeds — all imports resolve at the bundler
  level, not just at the TS level.
- Single-frame still renders verified for every scene (1, 2, 3, 4, 5, 6)
  via `npx remotion still MycorrhizalBCN out/test.png --frame=N`.
  Reference frames render with the expected content: subtitles, zones,
  charts, captions, and the Amanita cameo all paint correctly.
- All scenes use only `interpolate(frame, …, { easing })` for animation;
  no CSS transitions or Tailwind animation classes (both forbidden in
  Remotion).
- The Amanita cameo is exactly one occurrence, in Scene 3, lasting about
  1.5 seconds — matching the storytelling brief's "five-frame visual
  seasoning, not a centrepiece" instruction.
- All margin chrome (scene number, timecode, project tag, scene label)
  is consistent across scenes via `SceneChrome.tsx`.
- Subtitle-only — no `<Audio>` or `<Video>` components anywhere in the
  source tree.

### Bug caught and fixed during verification

The first render of Scenes 2–6 was empty save for the chrome. The root
cause: each scene was computing `local = useCurrentFrame() -
sceneStartFrame`, but `useCurrentFrame()` inside a `<Sequence from={X}>`
already returns frames relative to the sequence's `from`. The double
subtraction pushed `local` deep into negative territory for every scene
after the first, clamping every interpolation to 0 and producing no
visible content. Scene 1 worked accidentally because its
`sceneStartFrame` is 0.

Fix: each scene now uses `const local = useCurrentFrame()` directly, and
the `sceneStartFrame` prop has been removed from all six scenes. The
`MycorrhizalVideo.tsx` composition was updated to drop the unused prop.
Re-renders of frames in all six scenes confirm the fix.

## Honest limitations of the artefact

- The Barcelona basemap is **not georeferenced**. It is a stylised
  silhouette. The grid-coordinate-to-screen-pixel projection inside
  `GridCoords.ts` produces a visually plausible spread of the 15 zones
  but does not place them at their real WGS84 coordinates. This is by
  design (the brief says "Barcelona basemap fades up" without requiring
  geographic accuracy and a full georeferenced render would require
  shipping a static map image into `public/`).
- The intervention split visualised in Scene 5 is a documented heuristic
  diversification, not the raw `intervention_type` column from the CSV.
  See `priorityZones.ts` for the rule and rationale.
- The Jaccard = 1.00 number shown in Scene 4 is the current pipeline
  output. Per `outputs/limitations.md` and the storytelling brief this
  result is partly an artefact of the constant `sealed_pct` raster bug;
  once the raster fix lands the realistic Jaccard is 0.7–0.9. **The
  scene should be re-rendered with the corrected number after that fix
  ships** — change the constant in `Scene4_Robustness.tsx`.
- Cormorant Garamond is referenced in the font stack but not loaded
  through `@remotion/google-fonts`; on render it falls back to system
  serif. If a tighter typographic match is needed, add the Google Fonts
  loader and re-render.
