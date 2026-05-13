# Prompt Templates — Three Visual Registers

Each template is a structured Flux prompt. Replace `{variables}` with
content extracted from the markdown spec in Stage 1.

---

## How to extract variables from the markdown

Before filling templates, extract these fields from the spec:

| Variable | Where to find it | Example |
|---|---|---|
| `{subject}` | Title or one-sentence description | "Barcelona barrier-reduction priority zones" |
| `{layout}` | Layout section (top/center/panel/footer description) | "header top, large map center, data table right, footer" |
| `{key_elements}` | Named visual objects | "choropleth map, 400m grid cells, color-coded zones, legend, inset map" |
| `{color_palette}` | Any colors mentioned | "orange, red, green, blue zone fills on light basemap" |
| `{domain}` | Project domain | "urban planning, ecology, Barcelona" |
| `{data_type}` | Type of data shown | "spatial priority ranking, tabular sub-scores" |

---

## Register 1 — Technical / Cartographic

**Goal:** Clean, municipal planning aesthetic. Looks like it came out of a
GIS-literate planning department. Neutral palette, precise gridlines,
legible labels, no decoration.

```
A technical planning document layout for {subject}. {layout_description}.
Cartographic style: clean white background, light gray grid lines,
muted choropleth color fills ({color_palette}), sans-serif labels,
numbered zone markers, compact legend panel. No decorative elements.
Style references: urban planning report, ESRI layout template,
municipal GIS output. High information density, print-ready,
A3 landscape orientation. Flat design, no shadows or gradients.
```

**Image parameters:**
```json
{
  "image_size": "landscape_4_3",
  "num_inference_steps": 35,
  "guidance_scale": 7.5,
  "num_images": 1
}
```

---

## Register 2 — Editorial / Magazine

**Goal:** Data-journalism aesthetic. Rich, atmospheric, the kind of visual
you'd see in Bloomberg CityLab or Der Spiegel's data team. Dramatic use
of color and typography, strong visual hierarchy.

```
An editorial data visualization spread for {subject}. {layout_description}.
Magazine data-journalism style: deep dark background (#1a1a2e or similar),
vivid saturated accent colors for {key_elements}, large bold headline
typography, generous white space between sections, cinematic crop.
Style references: Bloomberg Graphics, NYT Upshot, Pudding.cool,
National Geographic data stories. Dramatic lighting on the map element,
richly textured basemap, annotation callouts with leader lines.
Full bleed, editorial magazine double-page spread.
```

**Image parameters:**
```json
{
  "image_size": "landscape_16_9",
  "num_inference_steps": 40,
  "guidance_scale": 8.0,
  "num_images": 1
}
```

---

## Register 3 — Architectural Diagram

**Goal:** Technical drawing aesthetic, IAAC/AA-flavored. Axonometric
or plan-oblique projection where applicable. Precise, analytical,
the kind of visual produced by architects doing research.

```
An architectural analytical diagram of {subject}. {layout_description}.
Style: axonometric technical drawing, architectural presentation board,
thin precise linework on white or off-white background, isometric grid,
bold primary accent color with 80% desaturated field colors,
hand-lettered or Helvetica Neue annotation style, section cuts and
exploded views where relevant, scale bar and north arrow if spatial.
Style references: SANAA drawings, MVRDV diagrams, AA School thesis boards,
IAAC research presentations, OMA analytical drawings.
Precise, minimal, intellectually rigorous. No photorealism.
```

**Image parameters:**
```json
{
  "image_size": "square_hd",
  "num_inference_steps": 38,
  "guidance_scale": 7.0,
  "num_images": 1
}
```

---

## Prompt assembly pattern

For each register, assemble the final prompt as:

```
[register_template]

Content specifics: The layout shows {layout}. Key visual elements include
{key_elements}. Color palette: {color_palette}. Domain: {domain}.
Data represented: {data_type}.

Do not include: photographic textures unrelated to the domain, human figures,
logos, watermarks, illegible text, non-relevant decorative elements.
```

Keep total prompt under 400 tokens. If the spec is complex, prioritize
spatial layout + key elements + style reference over exhaustive detail.

---

## Notes on Flux behavior

- Flux handles **spatial layout descriptions** well when phrased as
  "X occupies the top 10%, Y occupies the center 55%"
- Flux **cannot render legible text** — do not ask it to render specific
  labels, numbers, or table content. Describe text as "annotation labels"
  or "tabular data panel" without specifying content.
- Flux **handles color palettes** well when given hex codes or strong
  named colors. Avoid vague terms like "muted" without a reference color.
- For the architectural register, adding "no photorealism" and "linework"
  strongly steers away from Flux's default photographic tendencies.
