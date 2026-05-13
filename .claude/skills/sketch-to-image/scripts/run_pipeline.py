#!/usr/bin/env python3
"""
run_pipeline.py — Orchestrates the full sketch-to-image pipeline.

Usage:
    python scripts/run_pipeline.py --spec path/to/sketch.md [--spec path/to/other.md]
    python scripts/run_pipeline.py --spec-dir path/to/specs/
    python scripts/run_pipeline.py --spec output-sketch-v0.md system-sketch-v0.md

Outputs to: ./outputs/<spec_stem>_{technical,editorial,architectural}.png
            ./outputs/<spec_stem>_diagram.svg  (if Mermaid found)

Requires: FAL_KEY env var, Python 3.8+
Optional: mmdc (mermaid-cli) for SVG rendering — `npm install -g @mermaid-js/mermaid-cli`
"""

import argparse
import os
import re
import sys
import json
import subprocess
import tempfile
from pathlib import Path

REGISTERS = ["technical", "editorial", "architectural"]

# ── Prompt templates per register ────────────────────────────────────────────

TEMPLATES = {
    "technical": (
        "A technical planning document layout for {subject}. {layout}. "
        "Cartographic style: clean white background, light gray grid lines, "
        "muted choropleth color fills ({colors}), sans-serif labels, "
        "numbered zone markers, compact legend panel. No decorative elements. "
        "Style references: urban planning report, ESRI layout template, "
        "municipal GIS output. High information density, print-ready, "
        "A3 landscape orientation. Flat design, no shadows or gradients. "
        "Key elements: {elements}."
    ),
    "editorial": (
        "An editorial data visualization spread for {subject}. {layout}. "
        "Magazine data-journalism style: deep dark background, "
        "vivid saturated accent colors ({colors}), large bold headline "
        "typography, generous white space, cinematic crop. "
        "Style references: Bloomberg Graphics, NYT Upshot, Pudding.cool, "
        "National Geographic data stories. Dramatic lighting on map element, "
        "richly textured basemap, annotation callouts with leader lines. "
        "Full bleed editorial magazine double-page spread. "
        "Key elements: {elements}. No photorealism unrelated to domain."
    ),
    "architectural": (
        "An architectural analytical diagram of {subject}. {layout}. "
        "Style: axonometric technical drawing, architectural presentation board, "
        "thin precise linework on white background, isometric grid, "
        "bold primary accent color with desaturated fields ({colors}), "
        "Helvetica Neue annotation style, scale bar if spatial. "
        "Style references: SANAA drawings, MVRDV diagrams, AA School thesis boards, "
        "IAAC research presentations, OMA analytical drawings. "
        "Precise, minimal, intellectually rigorous. No photorealism. "
        "Key elements: {elements}."
    ),
}


# ── Markdown parsing ──────────────────────────────────────────────────────────

def extract_mermaid_blocks(text: str) -> list[str]:
    pattern = r"```mermaid\n(.*?)```"
    return re.findall(pattern, text, re.DOTALL)


def extract_layout_intent(text: str, filepath: Path) -> dict:
    """
    Extract visual intent from markdown spec.
    Returns dict with: subject, layout, elements, colors, domain, data_type
    """
    lines = text.splitlines()

    # Subject: first H1 or H2 title
    subject = filepath.stem.replace("-", " ").replace("_", " ")
    for line in lines:
        if line.startswith("# "):
            subject = line.lstrip("# ").strip()
            break
        if line.startswith("## What is"):
            # Look for the next non-empty line
            idx = lines.index(line)
            for l in lines[idx+1:idx+5]:
                if l.strip() and not l.startswith("#"):
                    subject = l.strip().lstrip("> ").lstrip("- ").strip()
                    break
            break

    # Layout: look for layout/sketch/wireframe section
    layout = ""
    in_layout = False
    layout_lines = []
    for line in lines:
        lower = line.lower()
        if any(kw in lower for kw in ["layout", "sketch", "wireframe", "header", "center", "footer"]):
            in_layout = True
        if in_layout and line.strip():
            layout_lines.append(line.strip().lstrip(">").lstrip("-").strip())
            if len(layout_lines) > 8:
                break

    layout = " ".join(layout_lines[:6]) if layout_lines else "structured document layout"

    # Elements: bullet points describing visual objects
    element_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("- ", "* ", "🟧", "🟥", "🟩", "🟦")):
            clean = re.sub(r"[🟧🟥🟩🟦\*\-]", "", stripped).strip()
            if clean and len(clean) > 5:
                element_lines.append(clean)
    elements = ", ".join(element_lines[:8]) if element_lines else "map, data table, legend, annotations"

    # Colors: extract any color mentions
    color_pattern = r"(#[0-9a-fA-F]{3,6}|orange|red|green|blue|amber|teal|purple|yellow|gray|grey|white|black|dark|light)"
    colors_found = re.findall(color_pattern, text, re.IGNORECASE)
    color_hints = ["orange", "red", "green", "blue"]  # defaults from the spec emoji
    if colors_found:
        color_hints = list(dict.fromkeys(c.lower() for c in colors_found))[:6]
    colors = ", ".join(color_hints)

    # Domain: infer from content
    domain = "urban planning, ecology, spatial analysis"
    if "barcelona" in text.lower():
        domain = "Barcelona urban planning, mycorrhizal ecology, spatial analysis"

    # Data type
    data_type = "spatial priority ranking with tabular sub-scores"

    return {
        "subject": subject[:120],
        "layout": layout[:300],
        "elements": elements[:200],
        "colors": colors[:100],
        "domain": domain,
        "data_type": data_type,
    }


def build_prompt(register: str, intent: dict) -> str:
    template = TEMPLATES[register]
    prompt = template.format(**intent)
    # Append safety suffix
    prompt += (
        " Do not include: watermarks, logos, illegible scribbles, "
        "human figures unrelated to domain, non-relevant textures."
    )
    return prompt[:1500]  # Flux handles up to ~500 tokens but be safe


# ── Mermaid rendering ─────────────────────────────────────────────────────────

def render_mermaid(mermaid_content: str, output_path: Path) -> bool:
    """Render a Mermaid diagram to SVG. Returns True on success."""
    # Check mmdc is available
    check = subprocess.run(["mmdc", "--version"], capture_output=True)
    if check.returncode != 0:
        print(
            "WARNING: mmdc (mermaid-cli) not found. "
            "Install with: npm install -g @mermaid-js/mermaid-cli",
            file=sys.stderr,
        )
        return False

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
        f.write(mermaid_content)
        tmp_path = f.name

    config = {
        "theme": "base",
        "themeVariables": {
            "primaryColor": "#2d4a6b",
            "primaryTextColor": "#ffffff",
            "primaryBorderColor": "#1a3050",
            "lineColor": "#6b8caa",
            "secondaryColor": "#f0f4f8",
            "clusterBkg": "#f0f4f8",
            "fontFamily": "Helvetica Neue, Arial, sans-serif",
            "fontSize": "14px",
        }
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as cf:
        json.dump(config, cf)
        config_path = cf.name

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["mmdc", "-i", tmp_path, "-o", str(output_path),
         "--config", config_path,
         "--backgroundColor", "transparent",
         "--width", "1920", "--height", "1080"],
        capture_output=True, text=True
    )
    os.unlink(tmp_path)
    os.unlink(config_path)

    if result.returncode != 0:
        print(f"WARNING: mmdc failed: {result.stderr}", file=sys.stderr)
        return False

    print(f"[sketch-to-image] SVG diagram → {output_path}")
    return True


# ── Main pipeline ─────────────────────────────────────────────────────────────

def process_spec(spec_path: Path, output_dir: Path) -> list[Path]:
    """Process one .md spec file. Returns list of output paths created."""
    print(f"\n[sketch-to-image] Processing: {spec_path.name}")
    text = spec_path.read_text(encoding="utf-8")
    stem = spec_path.stem
    outputs = []

    # 1. Render any Mermaid diagrams
    mermaid_blocks = extract_mermaid_blocks(text)
    for i, block in enumerate(mermaid_blocks):
        suffix = f"_diagram_{i}" if len(mermaid_blocks) > 1 else "_diagram"
        svg_path = output_dir / f"{stem}{suffix}.svg"
        if render_mermaid(block, svg_path):
            outputs.append(svg_path)

    # 2. Extract layout intent
    intent = extract_layout_intent(text, spec_path)
    print(f"[sketch-to-image] Subject: {intent['subject']}")

    # 3. Generate 3 images
    script = Path(__file__).parent / "generate.py"
    for register in REGISTERS:
        prompt = build_prompt(register, intent)
        out_png = output_dir / f"{stem}_{register}.png"

        print(f"[sketch-to-image] → {register} ({len(prompt)} chars)")
        result = subprocess.run(
            [sys.executable, str(script),
             "--prompt", prompt,
             "--register", register,
             "--output", str(out_png),
             "--retry"],
            env=os.environ.copy()
        )
        if result.returncode == 0:
            outputs.append(out_png)
        else:
            print(f"ERROR: Failed to generate {register} image for {stem}", file=sys.stderr)

    return outputs


def main():
    parser = argparse.ArgumentParser(description="Sketch-to-image pipeline")
    parser.add_argument("--spec", nargs="+", help="Path(s) to .md spec file(s)")
    parser.add_argument("--spec-dir", help="Directory containing .md spec files")
    parser.add_argument("--output-dir", default="outputs", help="Output directory (default: ./outputs)")
    args = parser.parse_args()

    if not os.environ.get("FAL_KEY"):
        print("ERROR: FAL_KEY environment variable not set.", file=sys.stderr)
        print("Export it: export FAL_KEY=your_key_here", file=sys.stderr)
        sys.exit(1)

    specs = []
    if args.spec:
        specs = [Path(s) for s in args.spec]
    elif args.spec_dir:
        specs = list(Path(args.spec_dir).glob("*.md"))
    else:
        parser.print_help()
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_outputs = []
    for spec in specs:
        if not spec.exists():
            print(f"WARNING: {spec} not found, skipping.", file=sys.stderr)
            continue
        outputs = process_spec(spec, output_dir)
        all_outputs.extend(outputs)

    print(f"\n[sketch-to-image] Done. {len(all_outputs)} file(s) generated:")
    for p in all_outputs:
        print(f"  {p}")


if __name__ == "__main__":
    main()
