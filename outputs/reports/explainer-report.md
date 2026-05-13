# Explainer Report — Mycorrhizal Barcelona

**Deliverable:** `outputs/explainer.html` — single-file interactive explainer for Ajuntament Espais Verds capital-planning analysts.
**Date:** 2026-05-10
**Author:** Frontend Developer

---

## How to view it

Open `outputs/explainer.html` in any modern browser (Chrome, Firefox, Edge, Safari). No build step, no server required.

- **Double-click** the file in Explorer/Finder, or drag it onto a browser window.
- **Optional but recommended:** serve the `outputs/` directory over a local HTTP server so `fetch('priority_zones.csv')` succeeds and the table reads live data:
  ```
  cd outputs
  python -m http.server 8000
  # then open http://localhost:8000/explainer.html
  ```
- Without a server (`file://`), the page detects the protocol, skips the fetch, and silently uses the **hardcoded fallback** dataset that mirrors `priority_zones.csv` row-for-row. The user-visible result is identical.
- The two embedded Folium maps (`priority_map.html`, `network_neighborhoods.html`) load via `<iframe>` and work identically under both protocols because they are sibling files.

---

## Narrative structure (follows storytelling-guidance.md)

The page is a single-column scrollytelling layout in nine sections, each with an `id` for sticky-nav anchor links:

| # | Section | id        | What it does                                                                  |
|---|---------|-----------|-------------------------------------------------------------------------------|
| 1 | Hero    | `#hero`   | Lead sentence: *"Mature trees cost less than dead saplings."* + sub-lede.    |
| 2 | Problem | `#problem`| Cost framing (3–5× replacement cost). Soil-as-municipal-plumbing metaphor.   |
| 3 | Barriers| `#barriers`| Four icon cards: sealed, heat, low canopy, host-mismatch (flagged honest).  |
| 4 | Map     | `#map`    | Embedded `priority_map.html` iframe + caption explaining colour = intervention.|
| 5 | Zones   | `#zones`  | Sortable table of all 15 zones with horizontal composite-barrier bars.       |
| 6 | Robust  | `#robust` | `sensitivity_comparison.png` + caption with honesty note re Jaccard artefact.|
| 7 | Network | `#network`| Embedded `network_neighborhoods.html` + 500m-not-2030-forecast caveat.        |
| 8 | Limits  | `#limits` | Five sober bullet points distilled from `limitations.md`. Dark-on-forest.    |
| 9 | Next    | `#next`   | Four budget-line crosswalk cards + explicit Seam-3 TODO note.                |

Order follows the Visual Storyteller's "geography first, methods second, instructions third" rule. The robustness chart and the limitations section are deliberately *prominent*, not buried — they are the trust artefacts that win the council defence.

---

## Design decisions

### Palette
- `--paper #f4efe6` — off-white background, slightly warm, reads as paper not screen.
- `--forest #1f3a2c` — dark forest green for headings, footer, limitations panel, table headers.
- `--copper #b6753a` — amber/copper for accents, eyebrow labels, the rule beside captions, "colonisation uncertain" flag, and the "honest" barrier card.
- Alternating section backgrounds (`paper` / `paper-2`) give the page rhythm without being noisy.

### Typography
- **Headers:** Cormorant Garamond (serif, italic on hero h1) — the planner's office reads PDFs and reports; serifs signal "document," not "startup."
- **Body:** Inter — clean sans-serif at 17px / 1.65 line-height for comfortable reading at the 840px content width.
- One Google Fonts import (the only external dependency; everything else is inline).

### Layout
- Single-column. Text content capped at `--content: 840px`; maps and the sensitivity figure break out wider to `--wide: 1180px`.
- Sticky top nav with eight anchor links. Smooth scroll. Backdrop-blur for legibility.
- Iframes at 640px desktop / 460px mobile, with `loading="lazy"` so the heavier Folium map only loads when scrolled to.

### Interaction (per "interactivity is for trust, not engagement")
- **Sortable zones table** — click any column header to sort asc/desc. Keyboard-accessible (`tabindex`, Enter/Space). Sort arrows in the header indicate state.
- **Horizontal bar chart inside the composite-barrier column** — value-bar combo so a planner can scan magnitudes without reading every decimal.
- **Colonisation-uncertain flag** as a coppered pill on the relevant barri rows.
- **Iframes pass through** Folium's native pan/zoom/popup interactions — no rebuild.
- **Subtle fade-in on scroll** (IntersectionObserver, 0.7s ease) — a single soft motion, gated by `prefers-reduced-motion`. No autoplay, no popups, no analytics, no cookies.

### Accessibility
- Semantic HTML: one `<h1>` (hero), `<h2>` per section, `<nav>`, `<main>`, `<section>` with `aria-labelledby`, `<footer>`.
- Iframes have `title` attributes. The bar-chart cells have `aria-label` exposing the numeric value to screen readers.
- Sortable headers have `role="button"` and `tabindex="0"`; Enter/Space trigger sort.
- Reduced-motion query disables fade-ins and smooth scroll for users who request it.
- Sufficient contrast: forest green on off-white (~12:1), copper on off-white meets AA for non-body text.

### Honesty as a feature
Following the storytelling guidance, the page does *not* hide the limitations. The "What this map cannot claim" section is a dark-forest panel — the most visually weighted block on the page after the hero — with five plain-language bullets. The sensitivity caption explicitly flags the Jaccard=1.0 artefact and the 0.7–0.9 expected range post-fix. The connectivity caveat names what the map is *not* (a 2030 forecast). The Next-Steps section ends with an explicit Seam-3 TODO box.

---

## Data flow

1. On page load, JS attempts `fetch('priority_zones.csv')` if the protocol is HTTP(S).
2. CSV is parsed with a small in-file parser that handles quoted fields containing commas (e.g. *"SANT PERE, SANTA CATERINA I LA RIBERA"*).
3. Rows are mapped to a clean `{rank, district, barri, composite, intervention, uncertain, profile}` object array.
4. If fetch fails, errors, or runs under `file://`, the JS silently falls back to a hardcoded `FALLBACK` array that mirrors the CSV.
5. The table is rendered using safe DOM methods (`createElement` + `textContent`) — no `innerHTML` for any data field.

---

## Constraints honoured

| Requirement                                           | Status |
|-------------------------------------------------------|--------|
| Single self-contained HTML file                       | done   |
| All CSS inline / in `<style>`                         | done   |
| All JS inline                                         | done   |
| No external CDN except one Google Fonts import        | done   |
| Embeds existing Folium maps via iframe (not rebuilt)  | done   |
| Loads CSV at runtime via fetch + hardcoded fallback   | done   |
| No SPA framework                                      | done — vanilla JS only |
| No "Buy now" / "Subscribe" CTAs                       | done   |
| No stock photography (SVG geometric only)             | done — hyphae motif as inline SVG data-URI |
| Mobile-friendly (single column collapses)             | done — breakpoints at 720px and 700px     |
| Semantic HTML with single h1, h2 per section          | done — 1 h1, 8 h2 |
| Smooth scroll + sticky top nav                        | done   |
| Subtle fade-ins, no game animations                   | done — IntersectionObserver only |
| Respects `prefers-reduced-motion`                     | done   |
| No autoplay / popups / analytics / cookies            | done   |

---

## File map

```
outputs/
├── explainer.html              ← THIS deliverable (40 KB)
├── explainer-report.md         ← THIS report
├── priority_map.html           ← embedded as iframe in §4 Map
├── network_neighborhoods.html  ← embedded as iframe in §7 Connectivity
├── priority_zones.csv          ← fetched at runtime in §5 Zones table
├── sensitivity_comparison.png  ← <img> in §6 Robustness
└── limitations.md              ← source for §8 Limits bullets
```

---

## Validation

Tag balance, counts, and feature presence verified:
- 1 `<h1>`, 8 `<h2>` (one per narrative section)
- 9 `<section>` blocks (hero + 8 narrative)
- 2 `<iframe>` embeds (priority map, connectivity map)
- 1 `<img>` (sensitivity chart)
- `fetch()` and `FALLBACK` array both present
- File size: 40 KB (well under the 100 KB target for a single-file artefact)

The user should open the file in a browser and confirm that the iframe maps, the sensitivity image, and the sortable table all render correctly. If the table appears but shows the hardcoded fallback rather than fresh CSV, that is expected behaviour under `file://` — serve the directory over `python -m http.server` to verify the fetch path.
