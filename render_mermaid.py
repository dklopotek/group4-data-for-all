"""Render the mermaid block from system-sketch-v0.md to a styled SVG."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".claude/skills/sketch-to-image/scripts").resolve()))
from run_pipeline import extract_mermaid_blocks, render_mermaid

spec = Path("docs/system-sketch-v0.md")
out_dir = Path("outputs")
out_dir.mkdir(exist_ok=True)

text = spec.read_text(encoding="utf-8")
blocks = extract_mermaid_blocks(text)
print(f"Found {len(blocks)} mermaid block(s) in {spec.name}")

for i, block in enumerate(blocks):
    suffix = f"_diagram_{i}" if len(blocks) > 1 else "_diagram"
    out = out_dir / f"{spec.stem}{suffix}.svg"
    ok = render_mermaid(block, out)
    print(f"  {'OK' if ok else 'FAIL'} -> {out}")
