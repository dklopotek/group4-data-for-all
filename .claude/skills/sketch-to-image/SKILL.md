---
name: sketch-to-image
description: >
  Converts textual wireframe sketches in markdown (.md files) into generated
  images using the fal.ai Flux API. Use this skill whenever a user has .md
  files containing layout descriptions, wireframes, or visual specs and wants
  them rendered as actual images. Triggers on: "generate images from my
  sketches", "render my wireframe", "visualise my spec", "turn this md into
  an image", or any request to produce visual output from markdown-described
  layouts. Produces THREE output images per sketch in different visual
  registers: (1) technical/cartographic, (2) editorial/magazine,
  (3) architectural diagram. Also renders any Mermaid diagrams found in the
  markdown as clean SVGs. Always use this skill when .md files describe
  visual layouts, maps, dashboards, or system diagrams.
---

# Sketch-to-Image Skill

Converts markdown wireframe specs into generated images via fal.ai Flux,
producing three visual registers per sketch plus SVG rendering of any
Mermaid diagrams.

---

## Pipeline Overview

```
.md file(s)
    │
    ├─► [Stage 1] Claude parses markdown → extracts layout intent
    │
    ├─► [Stage 2a] Mermaid blocks → SVG via mermaid-cli (deterministic)
    │
    └─► [Stage 2b] Layout descriptions → 3× Flux prompts → 3× PNG images
                   (technical / editorial / architectural)
```

---

## Step 1 — Parse the markdown

Read the input `.md` file(s). Extract:

- **Layout intent**: the spatial composition described (header/body/panel/footer, map area, table, etc.)
- **Key visual elements**: what objects appear (map, grid, color-coded zones, legend, table, inset)
- **Color palette hints**: any colors mentioned (🟧🟥🟩🟦 or hex codes or descriptions)
- **Title / subject**: what the output is about
- **Mermaid blocks**: any ` ```mermaid ``` ` fenced blocks → extract verbatim for SVG rendering

---

## Step 2a — Render Mermaid diagrams (deterministic)

If any Mermaid blocks were found:

```bash
# Install if not present
npm install -g @mermaid-js/mermaid-cli

# Render each block
echo "<mermaid_content>" > /tmp/diagram.mmd
mmdc -i /tmp/diagram.mmd -o outputs/diagram.svg -t default -b transparent
```

Style the SVG output with clean fonts and the color palette from the spec.
See `references/mermaid-style.md` for theme configuration.

---

## Step 3 — Build Flux prompts

For each visual register, construct a Flux prompt using the extracted layout
intent. Read `references/prompt-templates.md` for the exact prompt
structure per register.

**Three registers:**

| Register | Style goal | Flux model |
|---|---|---|
| `technical` | Clean municipal planning aesthetic, cartographic precision, neutral palette, gridded layout | `fal-ai/flux/dev` |
| `editorial` | Rich data-journalism feel, dramatic typography, atmospheric color, magazine spreads | `fal-ai/flux/dev` |
| `architectural` | Axonometric or exploded-view precision, technical drawing aesthetic, IAAC-flavored | `fal-ai/flux/dev` |

---

## Step 4 — Call fal.ai Flux API

Run `scripts/generate.py` once per register. Requires `FAL_KEY` in environment.

```bash
python scripts/generate.py \
  --prompt "<constructed_prompt>" \
  --register technical \
  --output outputs/<sketch_name>_technical.png

python scripts/generate.py \
  --prompt "<constructed_prompt>" \
  --register editorial \
  --output outputs/<sketch_name>_editorial.png

python scripts/generate.py \
  --prompt "<constructed_prompt>" \
  --register architectural \
  --output outputs/<sketch_name>_architectural.png
```

---

## Step 5 — Output

Deliver to `/mnt/user-data/outputs/`:
- `<sketch_name>_technical.png`
- `<sketch_name>_editorial.png`
- `<sketch_name>_architectural.png`
- `<sketch_name>_diagram.svg` (if Mermaid block present)

Present all files to the user with a one-line note per image on what
register choices were made and why.

---

## Error handling

- **No FAL_KEY**: fail immediately with clear message — do not proceed
- **Mermaid not installed**: skip SVG step, warn user, continue with PNGs
- **Flux API error**: log the prompt that failed, retry once with shorter prompt
- **No layout description found in .md**: report which file had no parseable layout and skip it

---

## Reference files

- `references/prompt-templates.md` — exact prompt structure for each register
- `references/mermaid-style.md` — Mermaid theme config and CSS overrides
- `scripts/generate.py` — fal.ai API call script
