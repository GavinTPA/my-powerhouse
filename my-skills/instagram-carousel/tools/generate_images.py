#!/usr/bin/env python3
"""
Instagram Image Generator
=========================
Generates character-consistent images using Google's Gemini 3 Pro Image API.

Uses chat mode to maintain character consistency across all slides.
Supports both carousel (4:5) and reel (9:16) aspect ratios.
Requires GOOGLE_API_KEY environment variable.

Usage:
    python3 generate_images.py <prompts_json> <output_dir> [options]

Arguments:
    prompts_json    Path to JSON file containing list of prompt strings
    output_dir      Directory to save generated images (created if doesn't exist)

Options:
    --reference     Path to reference image for character consistency
    --name          Base name for file naming (default: "Slide")
    --me            Use your default reference image
    --aspect        "carousel" (1080x1350) or "reel" (1080x1920)
    --logo          Path to brand logo image (included in all slides)

Examples:
    # Carousel images (4:5 ratio)
    python3 generate_images.py prompts.json ~/Downloads/carousel --me --name Bonsai

    # Reel images (9:16 ratio)
    python3 generate_images.py prompts.json ~/Downloads/reel --me --name Decision --aspect reel
"""

import os
import sys
import json
import argparse
import warnings
from pathlib import Path
from datetime import datetime

warnings.filterwarnings("ignore")

# Instagram dimensions by format
# Note: Chat mode doesn't support ImageConfig, so we resize after generation
ASPECT_RATIOS = {
    "carousel": (1080, 1350),   # 4:5 aspect ratio - Instagram carousel/feed
    "reel": (1080, 1920),       # 9:16 aspect ratio - Instagram Reels/Stories
}

# Default for backwards compatibility
INSTAGRAM_WIDTH = 1080
INSTAGRAM_HEIGHT = 1350

# Default reference image location
DEFAULT_REFERENCE = Path(__file__).parent.parent / "assets" / "my-reference.jpeg"


def load_reference_image(path: Path) -> bytes:
    """Load reference image as bytes."""
    with open(path, "rb") as f:
        return f.read()


def resize_for_instagram(image_path: Path, aspect: str = "carousel") -> None:
    """
    Resize image to Instagram-optimal dimensions.

    Args:
        image_path: Path to the image file
        aspect: "carousel" (1080x1350, 4:5) or "reel" (1080x1920, 9:16)

    Uses smart cropping to maintain composition.
    """
    from PIL import Image

    width, height = ASPECT_RATIOS.get(aspect, ASPECT_RATIOS["carousel"])

    with Image.open(image_path) as img:
        # Calculate target dimensions maintaining aspect ratio
        target_ratio = width / height
        current_ratio = img.width / img.height

        if current_ratio > target_ratio:
            # Image is wider - crop sides
            new_width = int(img.height * target_ratio)
            left = (img.width - new_width) // 2
            img = img.crop((left, 0, left + new_width, img.height))
        elif current_ratio < target_ratio:
            # Image is taller - crop top/bottom
            new_height = int(img.width / target_ratio)
            top = (img.height - new_height) // 2
            img = img.crop((0, top, img.width, top + new_height))

        # Resize to exact dimensions
        img = img.resize((width, height), Image.Resampling.LANCZOS)

        # Save back (convert to RGB if needed for JPEG compatibility)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        img.save(image_path, quality=95)


def generate_carousel_images(
    prompts: list[str],
    output_dir: Path,
    reference_image_path: Path = None,
    logo_image_path: Path = None,
    carousel_name: str = "Slide",
    aspect: str = "carousel"
) -> dict:
    """
    Generate images with character consistency using chat mode.

    Args:
        prompts: List of image prompts (one per slide)
        output_dir: Directory to save generated images
        reference_image_path: Path to character reference image (optional)
        logo_image_path: Path to brand logo image (optional, included in all slides)
        carousel_name: Base name for output files (e.g., "Bonsai" -> Bonsai01.png)
        aspect: "carousel" (1080x1350, 4:5) or "reel" (1080x1920, 9:16)

    Returns:
        dict with 'generated' (list of paths) and 'failed' (list of slide numbers)
    """
    from google import genai
    from google.genai import types

    # Configure API
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_API_KEY environment variable not set")

    client = genai.Client(api_key=api_key)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load reference image if provided
    ref_image = None
    if reference_image_path and reference_image_path.exists():
        ref_image = types.Part.from_bytes(
            data=load_reference_image(reference_image_path),
            mime_type="image/jpeg"
        )
        print(f"Reference image: {reference_image_path.name}", file=sys.stderr)

    # Load logo image if provided
    logo_image = None
    if logo_image_path and logo_image_path.exists():
        logo_mime = "image/png" if logo_image_path.suffix.lower() == ".png" else "image/jpeg"
        logo_image = types.Part.from_bytes(
            data=load_reference_image(logo_image_path),
            mime_type=logo_mime
        )
        print(f"Logo image: {logo_image_path.name}", file=sys.stderr)

    # Create chat session for character consistency
    # Note: ImageConfig not supported in chat mode, so we resize after generation
    chat = client.chats.create(model="gemini-3-pro-image-preview")

    generated = []
    failed = []

    for i, prompt in enumerate(prompts, 1):
        slide_name = f"{carousel_name}{i:02d}"
        print(f"Generating {slide_name}...", file=sys.stderr)

        try:
            if i == 1:
                # First slide - send all reference images for chat context
                parts = []
                intro = ""
                if ref_image:
                    parts.append(ref_image)
                    intro += "This is my reference photo. Use this exact person's appearance throughout all images. "
                if logo_image:
                    parts.append(logo_image)
                    intro += "This is the brand logo. Include this logo in every image as specified in the prompt's BRANDING instructions. Reproduce the logo faithfully. "
                parts.append(intro + prompt)
                response = chat.send_message(parts)
            else:
                # Subsequent slides - chat maintains character + logo context
                response = chat.send_message(prompt)

            # Extract and save image (new SDK uses response.parts)
            saved = False
            for part in response.parts:
                if part.inline_data:
                    output_path = output_dir / f"{slide_name}.png"
                    # Use as_image().save() for cleaner handling
                    image = part.as_image()
                    image.save(str(output_path))

                    # Resize to target dimensions
                    resize_for_instagram(output_path, aspect)

                    width, height = ASPECT_RATIOS[aspect]
                    generated.append(str(output_path))
                    print(f"  Saved: {slide_name}.png (resized to {width}x{height})", file=sys.stderr)
                    saved = True
                    break

            if not saved:
                failed.append(i)
                print(f"  Warning: No image in response for slide {i}", file=sys.stderr)

        except Exception as e:
            failed.append(i)
            print(f"  Error on slide {i}: {str(e)[:60]}", file=sys.stderr)

    return {
        "generated": generated,
        "failed": failed,
        "total": len(prompts),
        "output_dir": str(output_dir)
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate character-consistent images using Gemini API"
    )
    parser.add_argument("prompts_json", help="Path to JSON file with list of prompts")
    parser.add_argument("output_dir", help="Directory to save generated images")
    parser.add_argument("--reference", help="Path to reference image for character consistency")
    parser.add_argument("--logo", help="Path to brand logo image (included in all slides)")
    parser.add_argument("--name", default="Slide", help="Base name for file naming")
    parser.add_argument("--me", action="store_true", help="Use your default reference image")
    parser.add_argument("--aspect", choices=["carousel", "reel"], default="carousel",
                        help="Aspect ratio: carousel (1080x1350, 4:5) or reel (1080x1920, 9:16)")

    args = parser.parse_args()

    # Load prompts
    prompts_path = Path(args.prompts_json)
    if not prompts_path.exists():
        print(f"Error: Prompts file not found: {prompts_path}", file=sys.stderr)
        sys.exit(1)

    with open(prompts_path) as f:
        prompts = json.load(f)

    if not isinstance(prompts, list):
        print("Error: Prompts JSON must be a list of strings", file=sys.stderr)
        sys.exit(1)

    # Determine reference image
    reference_path = None
    if args.me:
        reference_path = DEFAULT_REFERENCE
        if not reference_path.exists():
            print(f"Warning: Reference image not found at {reference_path}", file=sys.stderr)
            print("Run 'set up instagram carousel' to add your reference photo.", file=sys.stderr)
            reference_path = None
    elif args.reference:
        reference_path = Path(args.reference)
        if not reference_path.exists():
            print(f"Warning: Reference image not found: {reference_path}", file=sys.stderr)
            reference_path = None

    # Determine logo image
    logo_path = None
    if args.logo:
        logo_path = Path(args.logo)
        if not logo_path.exists():
            print(f"Warning: Logo image not found: {logo_path}", file=sys.stderr)
            logo_path = None

    # Generate images
    output_dir = Path(args.output_dir)
    width, height = ASPECT_RATIOS[args.aspect]
    print(f"Aspect: {args.aspect} ({width}x{height})", file=sys.stderr)

    result = generate_carousel_images(
        prompts=prompts,
        output_dir=output_dir,
        reference_image_path=reference_path,
        logo_image_path=logo_path,
        carousel_name=args.name,
        aspect=args.aspect
    )

    # Output result as JSON (for parsing by caller)
    print(json.dumps(result, indent=2))

    # Exit with error if any failed
    if result["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
