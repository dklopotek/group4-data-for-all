#!/usr/bin/env python3
"""
generate.py — fal.ai Flux image generation for sketch-to-image skill

Usage:
    python scripts/generate.py \
        --prompt "your prompt here" \
        --register technical|editorial|architectural \
        --output path/to/output.png

Requires: FAL_KEY environment variable
"""

import argparse
import os
import sys
import json
import urllib.request
import urllib.error
import base64
from pathlib import Path

# Register-specific Flux parameters
REGISTER_PARAMS = {
    "technical": {
        "image_size": "landscape_4_3",
        "num_inference_steps": 35,
        "guidance_scale": 7.5,
    },
    "editorial": {
        "image_size": "landscape_16_9",
        "num_inference_steps": 40,
        "guidance_scale": 8.0,
    },
    "architectural": {
        "image_size": "square_hd",
        "num_inference_steps": 38,
        "guidance_scale": 7.0,
    },
}

FAL_ENDPOINT = "https://fal.run/fal-ai/flux/dev"


def build_payload(prompt: str, register: str) -> dict:
    params = REGISTER_PARAMS[register]
    return {
        "prompt": prompt,
        "image_size": params["image_size"],
        "num_inference_steps": params["num_inference_steps"],
        "guidance_scale": params["guidance_scale"],
        "num_images": 1,
        "enable_safety_checker": True,
        "output_format": "png",
    }


def call_fal(payload: dict, fal_key: str) -> str:
    """Call fal.ai API, return image URL."""
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        FAL_ENDPOINT,
        data=body,
        headers={
            "Authorization": f"Key {fal_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"ERROR: fal.ai API returned {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Network error calling fal.ai: {e.reason}", file=sys.stderr)
        sys.exit(1)

    # Extract image URL from response
    images = result.get("images", [])
    if not images:
        print(f"ERROR: No images in fal.ai response: {result}", file=sys.stderr)
        sys.exit(1)

    return images[0]["url"]


def download_image(url: str, output_path: str) -> None:
    """Download image from URL to local path."""
    req = urllib.request.Request(url, headers={"User-Agent": "sketch-to-image/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(data)


def main():
    parser = argparse.ArgumentParser(description="Generate image via fal.ai Flux")
    parser.add_argument("--prompt", required=True, help="Flux prompt string")
    parser.add_argument(
        "--register",
        required=True,
        choices=["technical", "editorial", "architectural"],
        help="Visual register",
    )
    parser.add_argument("--output", required=True, help="Output PNG path")
    parser.add_argument(
        "--retry", action="store_true", help="Retry once on failure with shorter prompt"
    )
    args = parser.parse_args()

    # Check FAL_KEY
    fal_key = os.environ.get("FAL_KEY")
    if not fal_key:
        print(
            "ERROR: FAL_KEY environment variable not set.\n"
            "Export it: export FAL_KEY=your_key_here",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"[sketch-to-image] Generating {args.register} image...")
    print(f"[sketch-to-image] Prompt length: {len(args.prompt)} chars")

    payload = build_payload(args.prompt, args.register)

    try:
        image_url = call_fal(payload, fal_key)
    except SystemExit:
        if args.retry:
            # Truncate prompt to first 300 chars and retry
            short_prompt = args.prompt[:300] + " [concise rendering]"
            print(
                f"[sketch-to-image] Retrying with shorter prompt ({len(short_prompt)} chars)...",
                file=sys.stderr,
            )
            payload = build_payload(short_prompt, args.register)
            image_url = call_fal(payload, fal_key)
        else:
            raise

    print(f"[sketch-to-image] Downloading from: {image_url}")
    download_image(image_url, args.output)
    print(f"[sketch-to-image] Saved: {args.output}")


if __name__ == "__main__":
    main()
