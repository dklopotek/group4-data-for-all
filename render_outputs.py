"""Render output-sketch-v0 in 3 visual registers via fal.ai Flux.

Hand-crafted prompts grounded in docs/output-sketch-v0.md's layout section.
Bypasses the skill's brittle parser; calls generate.py directly per register.
"""
import os
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PROMPTS = {
    "technical": (
        "A flat cartographic municipal planning document at A3 landscape "
        "orientation, depicting an annotated map of Barcelona, Spain showing "
        "barrier-reduction priority zones. Top 10% of the page: a clean header "
        "band with title-text typography (visual structure, not legible specific "
        "text). Center 55%: a flat top-down basemap of the city of Barcelona "
        "with its 10 administrative districts faintly outlined in light gray, "
        "the Mediterranean coastline visible to the southeast, a faint 400m grid "
        "overlay, and 15 small filled-square priority cells distributed across "
        "the urban fabric — color-coded in four distinct saturated categories: "
        "orange, red, green, and blue. Each priority cell carries a small white "
        "circular numeric badge from 1 to 15. A tiny inset map showing a single "
        "1km square peri-urban reference patch in the lower-left corner. Right "
        "side 25%: a vertical panel containing a clean rectangular tabular data "
        "layout with row dividers and column headers, color-coded intervention-"
        "type pills in each row, no specific text legible. Bottom 10%: a footer "
        "band with caption-style annotation text and a citation block. Style: "
        "ESRI ArcGIS Layout aesthetic, QGIS print composer output, Ajuntament "
        "de Barcelona municipal report, clean white background with light gray "
        "gridlines, Helvetica Neue sans-serif typography, no decorative "
        "elements, flat design, no shadows, no gradients, print-ready, high "
        "information density."
    ),
    "editorial": (
        "An editorial data-journalism magazine spread depicting Barcelona's "
        "barrier-reduction priority zones for belowground ecological recovery, "
        "full-bleed double-page spread aesthetic. Deep dark navy background "
        "(#0d1b2a). Bold sans-serif headline typography across the top with "
        "strong visual hierarchy (visual structure, not legible specific text). "
        "Center hero: a dramatic richly-textured atmospheric basemap of "
        "Barcelona with its 10 districts subtly delineated, 15 priority zones "
        "glowing as vivid saturated cells in four intervention colors — "
        "luminous orange, fiery red, electric green, and ultraviolet blue — "
        "each zone numbered 1 to 15 with thin elegant leader-lines pointing to "
        "small annotation labels. The Mediterranean coastline catches dramatic "
        "side-lighting. Right-side editorial panel: clean tabular data "
        "presentation in white-on-dark, color-coded intervention pills, "
        "generous whitespace between rows. Tiny Collserola peri-urban "
        "reference-patch inset in the lower margin as a callout. Bottom: a "
        "thin annotated band with caption-style footnotes. Style: Bloomberg "
        "Graphics, NYT Upshot, Pudding.cool, National Geographic data stories, "
        "MIT SENSEable City Lab — cinematic, atmospheric, intellectually "
        "rigorous, print-magazine-quality."
    ),
    "architectural": (
        "An architectural analytical research presentation board depicting "
        "Barcelona's top 15 barrier-reduction priority zones at Superilla "
        "scale, in axonometric plan-oblique projection. Off-white paper "
        "background. Thin precise black linework throughout. The Barcelona "
        "urban fabric drawn in light hairline strokes showing the 10 districts "
        "and the Cerdà grid, with the 15 priority cells extruded slightly "
        "upward from the plane as colored prisms — bold but desaturated muted "
        "accent colors: terracotta, brick red, sage green, slate blue. Each "
        "priority cell carries a small Helvetica Neue numeric label and a thin "
        "leader-line to a zone-record annotation block in a margin. Right "
        "margin: a clean analytical scoring matrix with sub-score bars per "
        "zone, drawn as architectural diagram — small rectangles, hairline "
        "grids. Lower-left corner: a tiny axonometric exploded inset of the "
        "peri-urban Collserola reference patch as methodological anchor. Scale "
        "bar and north arrow in lower right. Top margin: project title block "
        "in tiny analytical lettering. Bottom margin: a methodological footer "
        "in small caps. Style: SANAA drawings, MVRDV diagrams, AA School "
        "thesis boards, IAAC research presentations, OMA analytical drawings — "
        "precise, minimal, intellectually rigorous, no photorealism, "
        "hand-drafted feel with computational precision."
    ),
}

NEGATIVES = (
    " Do not include: photographic satellite imagery, human figures, logos, "
    "watermarks, illegible scribbles, decorative ornaments, AI artifacts."
)


def call_generate(register: str, prompt: str) -> tuple[str, int, str]:
    out_png = Path("outputs") / f"output-sketch-v0_{register}.png"
    cmd = [
        sys.executable,
        ".claude/skills/sketch-to-image/scripts/generate.py",
        "--prompt", prompt + NEGATIVES,
        "--register", register,
        "--output", str(out_png),
        "--retry",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, env=os.environ.copy())
    return register, result.returncode, (result.stdout + result.stderr).strip()


def main():
    if not os.environ.get("FAL_KEY"):
        print("ERROR: FAL_KEY not set", file=sys.stderr)
        sys.exit(1)

    Path("outputs").mkdir(exist_ok=True)

    print(f"Firing {len(PROMPTS)} parallel Flux requests...")
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [pool.submit(call_generate, r, p) for r, p in PROMPTS.items()]
        for fut in as_completed(futures):
            register, code, output = fut.result()
            status = "OK" if code == 0 else "FAIL"
            print(f"\n[{status}] {register}")
            print(output)


if __name__ == "__main__":
    main()
