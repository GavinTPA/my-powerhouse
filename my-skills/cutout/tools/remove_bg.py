#!/usr/bin/env python3
"""
Remove Background - Standalone Background Removal
=================================================
Simple wrapper around rembg for removing backgrounds from existing images.

For generation + background removal, use cutout.py instead.

Requires:
- rembg package: pip install "rembg[cpu,cli]"
- Pillow: pip install Pillow  (for WebP conversion)

Usage:
    python3 remove_bg.py input.png output.png [--model MODEL] [--format FORMAT]
    python3 remove_bg.py --folder ~/Downloads/photos [--format webp] [--force]

Arguments:
    input           Path to input image (single file mode)
    output          Path for output image (single file mode)

Options:
    --model         rembg model (default: birefnet-general)
                    Options: birefnet-general, birefnet-general-lite,
                             isnet-general-use, u2net
    --format        Output format: png (default) or webp
    --folder        Process all images in a folder (batch mode)
    --force         Re-process files that already have cutouts

Example:
    python3 remove_bg.py ~/Downloads/photo.png ~/Downloads/photo-transparent.png
    python3 remove_bg.py photo.jpg cutout.png --model u2net
    python3 remove_bg.py photo.jpg cutout.webp --format webp
    python3 remove_bg.py --folder ~/Downloads/photos --format webp
"""

import sys
import argparse
import subprocess
from pathlib import Path
from PIL import Image

# rembg binary location (in skill's venv)
REMBG_BIN = Path(__file__).parent.parent / ".venv" / "bin" / "rembg"

# rembg model options
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


def remove_background(
    input_path: Path,
    output_path: Path,
    model: str = "birefnet-general",
    user_specified_model: bool = False,
    output_format: str = "png"
) -> bool:
    """
    Remove background from image using rembg.

    If the default model fails and the user didn't explicitly choose a model,
    automatically retries with u2net as a fallback.

    Args:
        input_path: Path to input image
        output_path: Path for output image (extension adjusted by output_format)
        model: rembg model to use
        user_specified_model: True if user passed --model explicitly (disables fallback)
        output_format: "png" or "webp"

    Returns:
        True if successful, False otherwise
    """
    if not check_rembg_installed():
        print("Error: rembg not installed.", file=sys.stderr)
        print("Install with: pip install 'rembg[cpu,cli]'", file=sys.stderr)
        return False

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return False

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

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
                            print(f"Success (fallback {FALLBACK_MODEL}): {output_path}", file=sys.stderr)
                            return True
                        return False
                    print(f"Success (fallback {FALLBACK_MODEL}): {output_path}", file=sys.stderr)
                    return True
                print(f"Error: Fallback model '{FALLBACK_MODEL}' also failed: {fallback_result.stderr}", file=sys.stderr)
                return False

            print(f"Error: rembg failed: {result.stderr}", file=sys.stderr)
            return False

        if rembg_output.exists():
            if output_format == "webp":
                if convert_to_webp(rembg_output, output_path):
                    rembg_output.unlink()
                    print(f"Success: {output_path}", file=sys.stderr)
                    return True
                return False
            print(f"Success: {output_path}", file=sys.stderr)
            return True
        else:
            print("Error: rembg completed but output file not found", file=sys.stderr)
            return False

    except subprocess.TimeoutExpired:
        print("Error: Background removal timed out (>2 minutes)", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def process_folder(
    folder_path: Path,
    model: str = "birefnet-general",
    user_specified_model: bool = False,
    output_format: str = "png",
    force: bool = False
) -> dict:
    """
    Process all images in a folder, outputting cutouts to a cutouts/ subfolder.

    Args:
        folder_path: Path to folder containing images
        model: rembg model to use
        user_specified_model: True if user explicitly chose the model
        output_format: "png" or "webp"
        force: Re-process files that already have cutouts

    Returns:
        dict with processed, skipped, failed counts
    """
    if not folder_path.is_dir():
        print(f"Error: Not a directory: {folder_path}", file=sys.stderr)
        return {"processed": 0, "skipped": 0, "failed": 0}

    # Collect image files
    image_files = sorted(
        f for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
    )

    if not image_files:
        print(f"No image files found in {folder_path}", file=sys.stderr)
        return {"processed": 0, "skipped": 0, "failed": 0}

    # Create output subfolder
    output_dir = folder_path / "cutouts"
    output_dir.mkdir(exist_ok=True)

    total = len(image_files)
    processed = 0
    skipped = 0
    failed = 0

    for i, img_file in enumerate(image_files, 1):
        output_name = img_file.stem + f".{output_format}"
        output_path = output_dir / output_name

        # Skip if cutout already exists (unless --force)
        if output_path.exists() and not force:
            print(f"Skipping {i}/{total}: {img_file.name} (cutout exists)", file=sys.stderr)
            skipped += 1
            continue

        print(f"Processing {i}/{total}: {img_file.name}", file=sys.stderr)

        success = remove_background(
            input_path=img_file,
            output_path=output_path,
            model=model,
            user_specified_model=user_specified_model,
            output_format=output_format
        )

        if success:
            processed += 1
        else:
            failed += 1

    summary = {"processed": processed, "skipped": skipped, "failed": failed}
    print(f"\nProcessed {processed} files, skipped {skipped}, failed {failed}", file=sys.stderr)
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Remove background from an image or batch of images"
    )
    parser.add_argument("input", nargs="?", help="Path to input image (single file mode)")
    parser.add_argument("output", nargs="?", help="Path for output image (single file mode)")
    parser.add_argument("--model", default="birefnet-general",
                       choices=REMBG_MODELS,
                       help="rembg model (default: birefnet-general)")
    parser.add_argument("--format", default="png", choices=["png", "webp"],
                       help="Output format: png (default) or webp")
    parser.add_argument("--folder", help="Process all images in a folder (batch mode)")
    parser.add_argument("--force", action="store_true",
                       help="Re-process files that already have cutouts (folder mode)")

    args = parser.parse_args()

    user_specified_model = (args.model != "birefnet-general")

    # Folder mode
    if args.folder:
        folder_path = Path(args.folder).expanduser().resolve()
        summary = process_folder(
            folder_path=folder_path,
            model=args.model,
            user_specified_model=user_specified_model,
            output_format=args.format,
            force=args.force
        )
        import json
        print(json.dumps(summary, indent=2))
        total = summary["processed"] + summary["failed"]
        sys.exit(0 if summary["failed"] == 0 and total > 0 else 1 if summary["failed"] > 0 else 0)

    # Single file mode
    if not args.input or not args.output:
        parser.error("In single file mode, both input and output are required. Use --folder for batch mode.")

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    # Adjust output extension to match format
    expected_ext = f".{args.format}"
    if output_path.suffix.lower() != expected_ext:
        output_path = output_path.with_suffix(expected_ext)
        print(f"Output adjusted to: {output_path}", file=sys.stderr)

    success = remove_background(
        input_path=input_path,
        output_path=output_path,
        model=args.model,
        user_specified_model=user_specified_model,
        output_format=args.format
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
