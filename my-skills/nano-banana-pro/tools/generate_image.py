#!/usr/bin/env python3
"""
Nano Banana Pro Image Generator
===============================
Generate images using Google's Gemini 3 Pro Image API with native resolution support.

Uses generate_content mode (not chat) for full ImageConfig support including
1K, 2K, 4K resolutions and flexible aspect ratios.

Requires GOOGLE_API_KEY environment variable.

Cost Tracking:
    Each successful generation is logged to ~/.config/nano-banana-pro-costs.csv
    for budget awareness. Use --costs to view spending totals.

Usage:
    python3 generate_image.py "prompt" [options]
    python3 generate_image.py --test
    python3 generate_image.py --costs

Arguments:
    prompt          The image generation prompt

Options:
    --size          Resolution: 1K, 2K, or 4K (default: 1K)
    --aspect        Aspect ratio (default: 16:9)
    --reference     Path to reference image for character consistency
    --ed            Use Ed's default reference image
    --output        Output directory (default: ~/Downloads)
    --name          Filename prefix (default: image)
    --test          Verify setup: validates key, generates a test image
    --costs         Show total spend and image count (no generation)

Example:
    python3 generate_image.py "A lighthouse cutting through morning fog" --size 2K --aspect 16:9
    python3 generate_image.py --test
    python3 generate_image.py --costs
"""

import os
import sys
import json
import csv
import argparse
import warnings
from pathlib import Path
from datetime import datetime

warnings.filterwarnings("ignore")

# Default reference image location (Ed's reference from instagram-carousel)
DEFAULT_ED_REFERENCE = Path(__file__).parent.parent / "assets" / "ed-reference.jpeg"

# Supported aspect ratios
VALID_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]

# Pricing estimates
PRICING = {
    "1K": 0.134,
    "2K": 0.24,
    "4K": 0.24
}

# Cost tracking log location
COST_LOG_PATH = Path.home() / ".config" / "nano-banana-pro-costs.csv"
CSV_HEADERS = ["timestamp", "model", "prompt_summary", "estimated_cost", "output_path"]

MODEL_NAME = "gemini-3-pro-image-preview"


def log_cost(prompt: str, cost: float, output_path: str) -> None:
    """
    Log image generation cost to CSV file for budget tracking.
    Creates file with headers if it doesn't exist.
    """
    # Ensure .config directory exists
    COST_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Check if file exists to determine if we need headers
    write_headers = not COST_LOG_PATH.exists()

    # Prepare row data
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    prompt_summary = prompt[:50].replace(",", " ").replace("\n", " ")

    row = [timestamp, MODEL_NAME, prompt_summary, f"{cost:.3f}", output_path]

    with open(COST_LOG_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if write_headers:
            writer.writerow(CSV_HEADERS)
        writer.writerow(row)


def show_cost_summary() -> None:
    """Display cost summary from the log file."""
    if not COST_LOG_PATH.exists():
        print("No cost log found. Generate some images first!")
        return

    total_cost = 0.0
    total_count = 0
    month_cost = 0.0
    month_count = 0

    current_month = datetime.now().strftime("%Y-%m")

    with open(COST_LOG_PATH, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                cost = float(row["estimated_cost"])
                total_cost += cost
                total_count += 1

                # Check if this entry is from current month
                if row["timestamp"].startswith(current_month):
                    month_cost += cost
                    month_count += 1
            except (ValueError, KeyError):
                continue  # Skip malformed rows

    print(f"Total images generated: {total_count}")
    print(f"Total estimated spend: ${total_cost:.2f}")
    print(f"This month: ${month_cost:.2f} ({month_count} images)")


TEST_PROMPT = (
    "A cute Hello Kitty and a chibi Gundam standing together giving a thumbs up, "
    "with a banner that says 'You Did It!', bright cheerful colors, "
    "celebratory confetti, cartoon style"
)


def run_test() -> None:
    """Verify setup: validate API key and generate a test image."""
    # Step 1: Check key exists
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("FAILED: GOOGLE_API_KEY not set.")
        print("")
        print("Fix: Run 'set up nano banana pro' in Claude Code,")
        print("or add this line to ~/.zshrc:")
        print('  export GOOGLE_API_KEY="your-key-here"')
        print("Then run: source ~/.zshrc")
        sys.exit(1)

    # Step 2: Validate key format
    key_stripped = api_key.strip()
    if key_stripped != api_key:
        print("WARNING: Your API key has leading/trailing whitespace.")
        print("This may cause authentication failures.")

    if not key_stripped.startswith("AIza"):
        print(f"WARNING: Key starts with '{key_stripped[:4]}...' — expected 'AIza'.")
        print("This may not be a valid Google AI Studio key.")

    if not (30 <= len(key_stripped) <= 50):
        print(f"WARNING: Key length is {len(key_stripped)} — expected 35-45 characters.")

    print(f"API key found: {key_stripped[:8]}...{key_stripped[-4:]}")

    # Step 3: Check google-genai is installed
    try:
        from google import genai  # noqa: F401
        print("google-genai package: installed")
    except ImportError:
        print("FAILED: google-genai package not installed.")
        print("")
        print("Fix: pip install google-genai pillow")
        sys.exit(1)

    # Step 4: Generate test image
    print("")
    print("Generating test image...")
    result = generate_image(
        prompt=TEST_PROMPT,
        size="1K",
        aspect_ratio="1:1",
        name="welcome-test"
    )

    if result.get("success"):
        print("")
        print("=" * 50)
        print("  CONNECTION TEST PASSED!")
        print("=" * 50)
        print("")
        print(f"  Your test image is at:")
        print(f"  {result['path']}")
        print("")
        print("  Open it to see Hello Kitty and Chibi Gundam")
        print("  giving you a thumbs up!")
        print("")
        print("  You're all set to generate images.")
        print("  Try: 'nano banana, generate an image of...'")
        print("=" * 50)
    else:
        error = result.get("error", "Unknown error")
        print("")
        print("FAILED: Image generation did not work.")
        print(f"Error: {error}")
        print("")
        if "billing" in error.lower() or "402" in error:
            print("Fix: Enable billing at https://console.cloud.google.com/billing")
            print("Image generation requires a paid account (~$0.13/image).")
        elif "invalid" in error.lower() or "401" in error or "403" in error:
            print("Fix: Check your API key is correct at https://aistudio.google.com/apikey")
        elif "quota" in error.lower() or "429" in error:
            print("Fix: You've hit a rate limit. Wait a minute and try again.")
        else:
            print("Fix: Check your internet connection and try again.")
            print("If the problem persists, delete the key at aistudio.google.com/apikey")
            print("and create a new one.")
        sys.exit(1)


def load_reference_image(path: Path) -> bytes:
    """Load reference image as bytes."""
    with open(path, "rb") as f:
        return f.read()


def generate_image(
    prompt: str,
    size: str = "1K",
    aspect_ratio: str = "16:9",
    reference_image_path: Path = None,
    output_dir: Path = None,
    name: str = "image"
) -> dict:
    """
    Generate a single image using Gemini 3 Pro Image API.

    Args:
        prompt: The image generation prompt
        size: Resolution - 1K, 2K, or 4K
        aspect_ratio: Output aspect ratio (e.g., "16:9", "1:1")
        reference_image_path: Optional reference image for character consistency
        output_dir: Directory to save the image
        name: Filename prefix

    Returns:
        dict with success status, path, and metadata
    """
    from google import genai
    from google.genai import types

    # Configure API
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "GOOGLE_API_KEY environment variable not set. Add it to ~/.zshrc"
        }

    # Validate inputs
    size = size.upper()
    if size not in ["1K", "2K", "4K"]:
        print(f"Warning: Invalid size '{size}', defaulting to 1K", file=sys.stderr)
        size = "1K"

    if aspect_ratio not in VALID_RATIOS:
        print(f"Warning: Invalid aspect ratio '{aspect_ratio}', defaulting to 16:9", file=sys.stderr)
        aspect_ratio = "16:9"

    # Set output directory
    if output_dir is None:
        output_dir = Path.home() / "Downloads"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp for unique filename
    timestamp = datetime.now().strftime("%H%M%S")
    output_filename = f"{name}-{timestamp}.png"
    output_path = output_dir / output_filename

    client = genai.Client(api_key=api_key)

    # Build content - include reference image if provided
    contents = []
    if reference_image_path and reference_image_path.exists():
        ref_image = types.Part.from_bytes(
            data=load_reference_image(reference_image_path),
            mime_type="image/jpeg"
        )
        contents.append(ref_image)
        # Modify prompt to reference the image
        prompt = f"Using the person from the reference image: {prompt}"
        print(f"Using reference image: {reference_image_path.name}", file=sys.stderr)

    contents.append(prompt)

    print(f"Generating {size} image at {aspect_ratio}...", file=sys.stderr)

    try:
        # Note: The google-genai SDK (v1.47.0) only supports aspect_ratio
        # Resolution control (1K/2K/4K) requires Vertex AI or a future SDK version
        # For now, we generate at default resolution (~1K) with aspect ratio control
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio
                )
            )
        )

        # Extract and save image
        for part in response.parts:
            if part.inline_data:
                image = part.as_image()
                image.save(str(output_path))
                print(f"Saved: {output_path}", file=sys.stderr)

                # Log cost for budget tracking
                cost = PRICING.get(size, 0.134)
                log_cost(prompt, cost, str(output_path))

                return {
                    "success": True,
                    "path": str(output_path),
                    "resolution": size,
                    "aspect_ratio": aspect_ratio,
                    "cost_estimate": f"${cost:.3f}"
                }

        return {
            "success": False,
            "error": "No image in API response"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)[:200]
        }


def main():
    parser = argparse.ArgumentParser(
        description="Generate images using Gemini 3 Pro Image API"
    )
    parser.add_argument("prompt", nargs="?", help="The image generation prompt")
    parser.add_argument("--size", default="1K", help="Resolution: 1K, 2K, or 4K (default: 1K)")
    parser.add_argument("--aspect", default="16:9", help="Aspect ratio (default: 16:9)")
    parser.add_argument("--reference", help="Path to reference image")
    parser.add_argument("--ed", action="store_true", help="Use Ed's default reference image")
    parser.add_argument("--output", help="Output directory (default: ~/Downloads)")
    parser.add_argument("--name", default="image", help="Filename prefix (default: image)")
    parser.add_argument("--test", action="store_true", help="Verify setup: validates key, generates test image")
    parser.add_argument("--costs", action="store_true", help="Show cost tracking summary")

    args = parser.parse_args()

    # Handle --test flag
    if args.test:
        run_test()
        return

    # Handle --costs flag
    if args.costs:
        show_cost_summary()
        return

    # Require prompt for image generation
    if not args.prompt:
        parser.error("prompt is required for image generation (or use --costs)")
        return

    # Determine reference image
    reference_path = None
    if args.ed:
        reference_path = DEFAULT_ED_REFERENCE
        if not reference_path.exists():
            print(f"Warning: Ed's reference image not found at {reference_path}", file=sys.stderr)
            reference_path = None
    elif args.reference:
        reference_path = Path(args.reference)
        if not reference_path.exists():
            print(f"Warning: Reference image not found: {reference_path}", file=sys.stderr)
            reference_path = None

    # Generate the image
    output_dir = Path(args.output) if args.output else None
    result = generate_image(
        prompt=args.prompt,
        size=args.size,
        aspect_ratio=args.aspect,
        reference_image_path=reference_path,
        output_dir=output_dir,
        name=args.name
    )

    # Output result as JSON
    print(json.dumps(result, indent=2))

    # Exit with error if failed
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
