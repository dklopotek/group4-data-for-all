"""Dry-run: show what extract_layout_intent + build_prompt produce, without calling fal."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(".claude/skills/sketch-to-image/scripts").resolve()))
from run_pipeline import extract_layout_intent, extract_mermaid_blocks, build_prompt, REGISTERS

specs = [Path("docs/system-sketch-v0.md"), Path("docs/output-sketch-v0.md")]

for spec_path in specs:
    if not spec_path.exists():
        print(f"!! missing: {spec_path}")
        continue
    text = spec_path.read_text(encoding="utf-8")
    intent = extract_layout_intent(text, spec_path)
    mermaid = extract_mermaid_blocks(text)

    print("=" * 72)
    print(f"SPEC: {spec_path}")
    print("=" * 72)
    print(f"Mermaid blocks found: {len(mermaid)}")
    print("\n--- extracted intent ---")
    for k, v in intent.items():
        print(f"  {k:10s}: {v}")
    print("\n--- prompts that would be sent ---")
    for register in REGISTERS:
        prompt = build_prompt(register, intent)
        print(f"\n[{register}] ({len(prompt)} chars)")
        print(prompt)
    print()
