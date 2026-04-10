#!/usr/bin/env python3
"""
Cutout - Transparent Asset Generator
=====================================
Create transparent assets by generating images with Gemini and removing backgrounds.

Two modes:
1. Generate mode: Prompt → Gemini generates with white bg → rembg removes → transparent asset
2. Process mode: Existing image → rembg removes background → transparent asset

Requires:
- GOOGLE_API_KEY environment variable (for generation)
- rembg package: pip install "rembg[cpu,cli]"
- Pillow: pip install Pillow  (for WebP conversion)

Usage:
    python3 cutout.py "prompt" [options]       # Generate new cutout
    python3 cutout.py --input image.png        # Remove bg from existing image
    python3 cutout.py --folder ~/Downloads/photos  # Batch process a folder

Arguments:
    prompt          The image generation prompt (for generate mode)

Options:
    --input         Path to existing image (process mode, skips generation)
    --folder        Process all images in a directory (batch mode)
    --aspect        Aspect ratio for generation (default: 1:1)
    --reference     Path to reference image for character consistency
    --me            Use your default reference image
    --output        Output directory (default: same directory / ~/Downloads)
    --name          Filename prefix (default: cutout)
    --model         rembg model (default: birefnet-general)
    --format        Output format: png (default) or webp
    --sizes         Output at multiple sizes (e.g., 1x,2x,3x or 512,1024,2048)

Example:
    python3 cutout.py "minimalist lighthouse icon" --aspect 1:1 --name logo
    python3 cutout.py --input ~/Downloads/photo.png --name photo-cutout
    python3 cutout.py "a person giving a thumbs up" --me --name thumbs
    python3 cutout.py "logo icon" --format webp --name logo
    python3 cutout.py "app icon" --name icon --sizes 1x,2x,3x
    python3 cutout.py --input photo.png --name hero --sizes 512,1024,2048
    python3 cutout.py --folder ~/Downloads/photos --format webp
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
import warnings
from pathlib import Path
from datetime import datetime

from PIL import Image

warnings.filterwarnings("ignore")

# Default reference image location
DEFAULT_REFERENCE = Path(__file__).parent.parent / "assets" / "my-reference.jpeg"

# rembg binary location (in skill's venv)
REMBG_BIN = Path(__file__).parent.parent / ".venv" / "bin" / "rembg"

# Supported aspect ratios
VALID_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]

# rembg model options (in order of recommendation for cutouts)
REMBG_MODELS = [
    "birefnet-general",      # High accuracy, best for logos/graphics
    "birefnet-general-lite", # Faster, slightly less accurate
    "isnet-general-use",     # Fast general-purpose
    "u2net",                 # Classic, reliable
]

DEFAULT_MODEL = "birefnet-general"
FALLBACK_MODEL = "u2net"


def check_rembg_installed() -> bool:
    """Check if rembg is installed and accessible."""
    return REMBG_BIN.exists()


def convert_to_webp(png_path: Path, webp_path: Path, quality: int = 90) -> bool:
    """Convert a PNG to WebP format using Pillow."""
    try:
        img = Image.open(png_path)
        img.save(str(webp_path), format="WEBP", quality=quality)
        return True
    except Exception as e:
        print(f"Error converting to WebP: {e}", file=sys.stderr)
        return False


def parse_sizes(sizes_str: str) -> list[dict]:
    """
    Parse --sizes argument into a list of size specs.

    Supports two formats:
    - Multiplier: "1x,2x,3x" — scale relative to original
    - Pixel: "512,1024,2048" — longest edge in pixels

    Returns:
        list of dicts with keys: label, type ("multiplier" or "pixel"), value (int or float)
    """
    specs = []
    for part in sizes_str.split(","):
        part = part.strip()
        if not part:
            continue
        if part.lower().endswith("x"):
            try:
                multiplier = float(part[:-1])
                if multiplier <= 0:
                    print(f"Warning: Skipping invalid multiplier '{part}'", file=sys.stderr)
                    continue
                specs.append({"label": part.lower(), "type": "multiplier", "value": multiplier})
            except ValueError:
                print(f"Warning: Skipping invalid size '{part}'", file=sys.stderr)
        else:
            try:
                pixels = int(part)
                if pixels <= 0:
                    print(f"Warning: Skipping invalid pixel size '{part}'", file=sys.stderr)
                    continue
                specs.append({"label": f"{pixels}px", "type": "pixel", "value": pixels})
            except ValueError:
                print(f"Warning: Skipping invalid size '{part}'", file=sys.stderr)
    return specs


def resize_cutout(input_path: Path, target_size: dict, output_path: Path) -> dict:
    """
    Resize a cutout image to a target size.

    Args:
        input_path: Path to the original cutout image
        target_size: dict with keys: label, type ("multiplier" or "pixel"), value
        output_path: Where to save the resized image

    Returns:
        dict with success status, path, dimensions, and whether it was skipped
    """
    try:
        img = Image.open(input_path)
        orig_w, orig_h = img.size
        longest_edge = max(orig_w, orig_h)

        if target_size["type"] == "multiplier":
            scale = target_size["value"]
            target_w = int(orig_w * scale)
            target_h = int(orig_h * scale)

            # Don't upscale — skip if target is larger than original
            if scale > 1.0:
                if target_w > orig_w or target_h > orig_h:
                    print(
                        f"Warning: Skipping {target_size['label']} — would upscale "
                        f"({orig_w}x{orig_h} → {target_w}x{target_h})",
                        file=sys.stderr
                    )
                    return {
                        "success": False,
                        "skipped": True,
                        "label": target_size["label"],
                        "reason": f"Would upscale from {orig_w}x{orig_h}"
                    }

            # 1x means original — just copy
            if scale == 1.0:
                shutil.copy2(input_path, output_path)
                return {
                    "success": True,
                    "path": str(output_path),
                    "label": target_size["label"],
                    "width": orig_w,
                    "height": orig_h
                }

        else:  # pixel
            target_px = target_size["value"]
            if target_px >= longest_edge:
                print(
                    f"Warning: Skipping {target_size['label']} — would upscale "
                    f"(longest edge {longest_edge}px → {target_px}px)",
                    file=sys.stderr
                )
                return {
                    "success": False,
                    "skipped": True,
                    "label": target_size["label"],
                    "reason": f"Would upscale from {longest_edge}px"
                }

            ratio = target_px / longest_edge
            target_w = int(orig_w * ratio)
            target_h = int(orig_h * ratio)

        resized = img.resize((target_w, target_h), Image.LANCZOS)
        resized.save(str(output_path))
        print(f"Resized {target_size['label']}: {target_w}x{target_h} → {output_path.name}", file=sys.stderr)

        return {
            "success": True,
            "path": str(output_path),
            "label": target_size["label"],
            "width": target_w,
            "height": target_h
        }

    except Exception as e:
        return {
            "success": False,
            "skipped": False,
            "label": target_size["label"],
            "error": str(e)[:200]
        }


def remove_background(
    input_path: Path,
    output_path: Path,
    model: str = "birefnet-general",
    user_specified_model: bool = False,
    output_format: str = "png"
) -> dict:
    """
    Remove background from image using rembg.

    If the default model fails and the user didn't explicitly choose a model,
    automatically retries with u2net as a fallback.

    Args:
        input_path: Path to input image
        output_path: Path for output image
        model: rembg model to use
        user_specified_model: True if user passed --model explicitly (disables fallback)
        output_format: "png" or "webp"

    Returns:
        dict with success status and path
    """
    if not check_rembg_installed():
        return {
            "success": False,
            "error": "rembg not installed. Run: pip install 'rembg[cpu,cli]'"
        }

    if not input_path.exists():
        return {
            "success": False,
            "error": f"Input file not found: {input_path}"
        }

    # rembg always outputs PNG; we convert to WebP afterward if needed
    if output_format == "webp":
        rembg_output = output_path.with_suffix(".png")
    else:
        rembg_output = output_path

    # Build rembg command
    cmd = [str(REMBG_BIN), "i", "-m", model, str(input_path), str(rembg_output)]

    print(f"Removing background with model: {model}...", file=sys.stderr)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout for large images
        )

        if result.returncode != 0:
            # Try fallback if default model failed and user didn't specify a model
            if not user_specified_model and model != FALLBACK_MODEL:
                print(f"Warning: {model} failed, retrying with {FALLBACK_MODEL}...", file=sys.stderr)
                fallback_cmd = [str(REMBG_BIN), "i", "-m", FALLBACK_MODEL, str(input_path), str(rembg_output)]
                fallback_result = subprocess.run(
                    fallback_cmd, capture_output=True, text=True, timeout=120
                )
                if fallback_result.returncode == 0 and rembg_output.exists():
                    if output_format == "webp":
                        if convert_to_webp(rembg_output, output_path):
                            rembg_output.unlink()
                        else:
                            return {"success": False, "error": "WebP conversion failed after fallback"}
                    print(f"Transparent {output_format.upper()} saved (fallback {FALLBACK_MODEL}): {output_path}", file=sys.stderr)
                    return {
                        "success": True,
                        "path": str(output_path),
                        "format": output_format,
                        "model": FALLBACK_MODEL
                    }
                return {
                    "success": False,
                    "error": f"Fallback model '{FALLBACK_MODEL}' also failed: {fallback_result.stderr[:200]}"
                }

            return {
                "success": False,
                "error": f"rembg failed: {result.stderr[:200]}"
            }

        if rembg_output.exists():
            if output_format == "webp":
                if convert_to_webp(rembg_output, output_path):
                    rembg_output.unlink()
                else:
                    return {"success": False, "error": "WebP conversion failed"}
            print(f"Transparent {output_format.upper()} saved: {output_path}", file=sys.stderr)
            return {
                "success": True,
                "path": str(output_path),
                "format": output_format,
                "model": model
            }
        else:
            return {
                "success": False,
                "error": "rembg completed but output file not found"
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Background removal timed out (>2 minutes)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)[:200]
        }


def load_reference_image(path: Path) -> bytes:
    """Load reference image as bytes."""
    with open(path, "rb") as f:
        return f.read()


def generate_with_white_bg(
    prompt: str,
    aspect_ratio: str = "1:1",
    reference_image_path: Path = None,
    output_path: Path = None
) -> dict:
    """
    Generate image with white background using Gemini API.
    Modifies prompt to request clean white background for easier cutout.

    Args:
        prompt: The image generation prompt
        aspect_ratio: Output aspect ratio
        reference_image_path: Optional reference image
        output_path: Where to save the generated image

    Returns:
        dict with success status and path to generated image
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

    # Validate aspect ratio
    if aspect_ratio not in VALID_RATIOS:
        print(f"Warning: Invalid aspect ratio '{aspect_ratio}', defaulting to 1:1", file=sys.stderr)
        aspect_ratio = "1:1"

    # Modify prompt for cutout-friendly generation
    cutout_prompt = f"{prompt}, isolated on pure white background, clean edges, no shadows, studio lighting, product photography style"

    client = genai.Client(api_key=api_key)

    # Build content - include reference image if provided
    contents = []
    if reference_image_path and reference_image_path.exists():
        ref_image = types.Part.from_bytes(
            data=load_reference_image(reference_image_path),
            mime_type="image/jpeg"
        )
        contents.append(ref_image)
        cutout_prompt = f"Using the person from the reference image: {cutout_prompt}"
        print(f"Using reference image: {reference_image_path.name}", file=sys.stderr)

    contents.append(cutout_prompt)

    print(f"Generating image at {aspect_ratio}...", file=sys.stderr)

    try:
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
                print(f"Generated: {output_path}", file=sys.stderr)
                return {
                    "success": True,
                    "path": str(output_path),
                    "aspect_ratio": aspect_ratio
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


def create_cutout(
    prompt: str = None,
    input_path: Path = None,
    aspect_ratio: str = "1:1",
    reference_image_path: Path = None,
    output_dir: Path = None,
    name: str = "cutout",
    model: str = "birefnet-general",
    user_specified_model: bool = False,
    output_format: str = "png",
    sizes: str = None
) -> dict:
    """
    Create a transparent cutout asset.

    Either generates a new image and removes background, or processes an existing image.

    Args:
        prompt: Image generation prompt (for generate mode)
        input_path: Path to existing image (for process mode)
        aspect_ratio: Aspect ratio for generation
        reference_image_path: Reference image for character consistency
        output_dir: Output directory
        name: Filename prefix
        model: rembg model to use
        user_specified_model: True if user passed --model explicitly
        output_format: "png" or "webp"
        sizes: Comma-separated size specs (e.g., "1x,2x,3x" or "512,1024")

    Returns:
        dict with success status, paths, and metadata
    """
    # Validate inputs
    if not prompt and not input_path:
        return {
            "success": False,
            "error": "Either prompt (for generation) or --input (for existing image) is required"
        }

    # Set output directory
    if output_dir is None:
        output_dir = Path.home() / "Downloads"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate timestamp for unique filenames
    timestamp = datetime.now().strftime("%H%M%S")

    # Determine input image path
    if input_path:
        # Process mode - use existing image
        source_path = Path(input_path)
        if not source_path.exists():
            return {
                "success": False,
                "error": f"Input file not found: {input_path}"
            }
        print(f"Processing existing image: {source_path}", file=sys.stderr)
    else:
        # Generate mode - create new image first
        source_path = output_dir / f"{name}-source-{timestamp}.png"

        gen_result = generate_with_white_bg(
            prompt=prompt,
            aspect_ratio=aspect_ratio,
            reference_image_path=reference_image_path,
            output_path=source_path
        )

        if not gen_result.get("success"):
            return gen_result

    # Now remove background
    final_path = output_dir / f"{name}-{timestamp}.{output_format}"

    bg_result = remove_background(
        input_path=source_path,
        output_path=final_path,
        model=model,
        user_specified_model=user_specified_model,
        output_format=output_format
    )

    if not bg_result.get("success"):
        return bg_result

    # Clean up source image if we generated it (keep only final cutout)
    if prompt and source_path.exists() and source_path != Path(input_path or ""):
        source_path.unlink()
        print(f"Cleaned up intermediate file: {source_path.name}", file=sys.stderr)

    result = {
        "success": True,
        "path": str(final_path),
        "format": output_format,
        "mode": "process" if input_path else "generate",
        "aspect_ratio": aspect_ratio if not input_path else "original",
        "model": model,
        "cost_estimate": "$0.134" if not input_path else "$0.00"
    }

    # Handle multiple size outputs
    if sizes:
        size_specs = parse_sizes(sizes)
        if size_specs:
            size_results = []
            for spec in size_specs:
                # Build output path: name-timestamp-label.format
                size_filename = f"{name}-{timestamp}-{spec['label']}.{output_format}"
                size_path = output_dir / size_filename

                # For 1x multiplier, the original IS the 1x — just copy it
                if spec["type"] == "multiplier" and spec["value"] == 1.0:
                    shutil.copy2(final_path, size_path)
                    img = Image.open(final_path)
                    w, h = img.size
                    size_results.append({
                        "success": True,
                        "path": str(size_path),
                        "label": spec["label"],
                        "width": w,
                        "height": h
                    })
                    print(f"Copied {spec['label']}: {w}x{h} → {size_path.name}", file=sys.stderr)
                else:
                    size_result = resize_cutout(final_path, spec, size_path)
                    size_results.append(size_result)

            result["sizes"] = size_results

    return result


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def process_folder(
    folder_path: Path,
    output_dir: Path = None,
    model: str = "birefnet-general",
    user_specified_model: bool = False,
    output_format: str = "png",
) -> dict:
    """
    Process all images in a folder through background removal.

    Args:
        folder_path: Path to folder containing images
        output_dir: Output directory (default: same as folder_path)
        model: rembg model to use
        user_specified_model: True if user explicitly chose the model
        output_format: "png" or "webp"

    Returns:
        dict with processed, skipped, failed counts and failure details
    """
    if not folder_path.is_dir():
        print(f"Error: Not a directory: {folder_path}", file=sys.stderr)
        return {"success": False, "error": f"Not a directory: {folder_path}"}

    if output_dir is None:
        output_dir = folder_path
    output_dir.mkdir(parents=True, exist_ok=True)

    # Collect image files, skip any with "-cutout" in the name
    image_files = sorted(
        f for f in folder_path.iterdir()
        if f.is_file()
        and f.suffix.lower() in IMAGE_EXTENSIONS
        and "-cutout" not in f.stem
    )

    if not image_files:
        print("No images found in folder.", file=sys.stderr)
        return {
            "success": True,
            "processed": 0,
            "skipped": 0,
            "failed": 0,
            "total": 0,
            "message": "No images found"
        }

    total = len(image_files)
    processed = 0
    failed = 0
    failures = []

    for i, img_file in enumerate(image_files, 1):
        print(f"Processing {i}/{total}: {img_file.name}...", file=sys.stderr)

        output_name = f"{img_file.stem}-cutout.{output_format}"
        output_path = output_dir / output_name

        result = remove_background(
            input_path=img_file,
            output_path=output_path,
            model=model,
            user_specified_model=user_specified_model,
            output_format=output_format
        )

        if result.get("success"):
            processed += 1
        else:
            failed += 1
            failures.append({
                "file": img_file.name,
                "error": result.get("error", "Unknown error")
            })

    print(f"\nProcessed {processed}/{total} images. {failed} failures.", file=sys.stderr)

    return {
        "success": True,
        "processed": processed,
        "skipped": 0,
        "failed": failed,
        "total": total,
        "output_dir": str(output_dir),
        "format": output_format,
        "failures": failures
    }


def main():
    parser = argparse.ArgumentParser(
        description="Create transparent PNG cutouts from prompts or existing images"
    )
    parser.add_argument("prompt", nargs="?", help="Image generation prompt (for generate mode)")
    parser.add_argument("--input", help="Path to existing image (process mode, skips generation)")
    parser.add_argument("--folder", help="Process all images in a directory (batch mode)")
    parser.add_argument("--aspect", default="1:1", help="Aspect ratio for generation (default: 1:1)")
    parser.add_argument("--reference", help="Path to reference image")
    parser.add_argument("--me", action="store_true", help="Use your default reference image")
    parser.add_argument("--output", help="Output directory (default: ~/Downloads)")
    parser.add_argument("--name", default="cutout", help="Filename prefix (default: cutout)")
    parser.add_argument("--model", default="birefnet-general",
                       choices=REMBG_MODELS,
                       help="rembg model (default: birefnet-general)")
    parser.add_argument("--format", default="png", choices=["png", "webp"],
                       help="Output format: png (default) or webp")
    parser.add_argument("--sizes",
                       help="Output at multiple sizes (e.g., 1x,2x,3x or 512,1024,2048)")

    args = parser.parse_args()

    # Validate mutual exclusivity
    if args.folder and args.prompt:
        parser.error("--folder and prompt are mutually exclusive")
    if args.folder and args.input:
        parser.error("--folder and --input are mutually exclusive")

    # Folder mode
    if args.folder:
        folder_path = Path(args.folder).expanduser().resolve()
        output_dir = Path(args.output).expanduser().resolve() if args.output else None

        result = process_folder(
            folder_path=folder_path,
            output_dir=output_dir,
            model=args.model,
            user_specified_model=(args.model != "birefnet-general"),
            output_format=args.format,
        )

        print(json.dumps(result, indent=2))
        if not result.get("success") or result.get("failed", 0) > 0:
            sys.exit(1)
        return

    # Validate: need either prompt or input
    if not args.prompt and not args.input:
        parser.error("Either a prompt (for generation), --input (for existing image), or --folder (for batch) is required")
        return

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

    # Create the cutout
    output_dir = Path(args.output).expanduser().resolve() if args.output else None
    input_path = Path(args.input).expanduser().resolve() if args.input else None

    result = create_cutout(
        prompt=args.prompt,
        input_path=input_path,
        aspect_ratio=args.aspect,
        reference_image_path=reference_path,
        output_dir=output_dir,
        name=args.name,
        model=args.model,
        user_specified_model=(args.model != "birefnet-general"),
        output_format=args.format,
        sizes=args.sizes
    )

    # Output result as JSON
    print(json.dumps(result, indent=2))

    # Exit with error if failed
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    main()
