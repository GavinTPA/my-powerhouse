#!/usr/bin/env python3
"""
Model Cleanup - Manage downloaded rembg models
===============================================
List, inspect, and remove rembg models stored in ~/.u2net/.

Usage:
    python3 model_cleanup.py --list
    python3 model_cleanup.py --remove MODEL_NAME
    python3 model_cleanup.py --remove-all [--keep MODEL_NAME]

Options:
    --list              List all downloaded models with file sizes
    --remove MODEL      Remove a specific model's files
    --remove-all        Remove all downloaded models (prompts for confirmation)
    --keep MODEL        When used with --remove-all, keep specific models (repeatable)

Example:
    python3 model_cleanup.py --list
    python3 model_cleanup.py --remove isnet-general-use
    python3 model_cleanup.py --remove-all --keep birefnet-general
"""

import sys
import json
import shutil
import argparse
from pathlib import Path


MODELS_DIR = Path.home() / ".u2net"


def format_size(size_bytes: int) -> str:
    """Format byte count as human-readable string."""
    if size_bytes >= 1_073_741_824:
        return f"{size_bytes / 1_073_741_824:.2f} GB"
    elif size_bytes >= 1_048_576:
        return f"{size_bytes / 1_048_576:.1f} MB"
    elif size_bytes >= 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes} B"


def get_model_size(path: Path) -> int:
    """Get total size of a model entry (file or directory)."""
    if path.is_file():
        return path.stat().st_size
    elif path.is_dir():
        return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
    return 0


def list_models() -> dict:
    """List all downloaded models with sizes."""
    if not MODELS_DIR.exists():
        print("No models directory found (~/.u2net/ does not exist)", file=sys.stderr)
        return {"models": [], "total_size": "0 B", "total_bytes": 0}

    models = []
    total_bytes = 0

    for entry in sorted(MODELS_DIR.iterdir()):
        # Skip hidden files
        if entry.name.startswith("."):
            continue

        size = get_model_size(entry)
        total_bytes += size

        model_info = {
            "name": entry.name,
            "size": format_size(size),
            "size_bytes": size,
            "type": "directory" if entry.is_dir() else "file",
            "path": str(entry)
        }
        models.append(model_info)
        print(f"  {entry.name:<30} {format_size(size):>10}  ({model_info['type']})", file=sys.stderr)

    if not models:
        print("No models found in ~/.u2net/", file=sys.stderr)
    else:
        print(f"\n  Total: {len(models)} model(s), {format_size(total_bytes)}", file=sys.stderr)

    return {
        "models": models,
        "total_size": format_size(total_bytes),
        "total_bytes": total_bytes
    }


def remove_model(model_name: str) -> dict:
    """Remove a specific model's files."""
    if not MODELS_DIR.exists():
        print(f"Models directory not found (~/.u2net/)", file=sys.stderr)
        return {"success": False, "error": "Models directory does not exist"}

    model_path = MODELS_DIR / model_name
    if not model_path.exists():
        print(f"Model not found: {model_name}", file=sys.stderr)
        available = [e.name for e in MODELS_DIR.iterdir() if not e.name.startswith(".")]
        return {
            "success": False,
            "error": f"Model '{model_name}' not found",
            "available": available
        }

    size = get_model_size(model_path)
    size_str = format_size(size)

    if model_path.is_dir():
        shutil.rmtree(model_path)
    else:
        model_path.unlink()

    print(f"Removed: {model_name} ({size_str})", file=sys.stderr)
    return {
        "success": True,
        "removed": model_name,
        "freed": size_str,
        "freed_bytes": size
    }


def remove_all(keep: list[str] = None) -> dict:
    """Remove all downloaded models, optionally keeping some."""
    keep = keep or []

    if not MODELS_DIR.exists():
        print("Models directory not found (~/.u2net/)", file=sys.stderr)
        return {"success": False, "error": "Models directory does not exist"}

    entries = [e for e in MODELS_DIR.iterdir() if not e.name.startswith(".")]
    if not entries:
        print("No models to remove", file=sys.stderr)
        return {"success": True, "removed": [], "kept": [], "freed": "0 B", "freed_bytes": 0}

    to_remove = [e for e in entries if e.name not in keep]
    to_keep = [e for e in entries if e.name in keep]

    if not to_remove:
        print("All models are in the keep list — nothing to remove", file=sys.stderr)
        return {"success": True, "removed": [], "kept": [e.name for e in to_keep], "freed": "0 B", "freed_bytes": 0}

    # Confirmation prompt to stderr
    print(f"\nAbout to remove {len(to_remove)} model(s):", file=sys.stderr)
    for entry in to_remove:
        print(f"  - {entry.name} ({format_size(get_model_size(entry))})", file=sys.stderr)
    if to_keep:
        print(f"Keeping: {', '.join(e.name for e in to_keep)}", file=sys.stderr)

    print("\nConfirm removal? [y/N] ", end="", file=sys.stderr, flush=True)
    try:
        answer = input().strip().lower()
    except EOFError:
        answer = ""

    if answer not in ("y", "yes"):
        print("Cancelled", file=sys.stderr)
        return {"success": False, "error": "Cancelled by user"}

    removed = []
    total_freed = 0
    for entry in to_remove:
        size = get_model_size(entry)
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()
        removed.append(entry.name)
        total_freed += size
        print(f"Removed: {entry.name} ({format_size(size)})", file=sys.stderr)

    print(f"\nFreed {format_size(total_freed)} total", file=sys.stderr)
    return {
        "success": True,
        "removed": removed,
        "kept": [e.name for e in to_keep],
        "freed": format_size(total_freed),
        "freed_bytes": total_freed
    }


def main():
    parser = argparse.ArgumentParser(
        description="Manage downloaded rembg models in ~/.u2net/"
    )
    parser.add_argument("--list", action="store_true",
                       help="List all downloaded models with file sizes")
    parser.add_argument("--remove",
                       help="Remove a specific model by name")
    parser.add_argument("--remove-all", action="store_true",
                       help="Remove all downloaded models (with confirmation)")
    parser.add_argument("--keep", action="append", default=[],
                       help="When used with --remove-all, keep specific models (repeatable)")

    args = parser.parse_args()

    if not any([args.list, args.remove, args.remove_all]):
        parser.error("One of --list, --remove, or --remove-all is required")

    if args.list:
        result = list_models()
    elif args.remove:
        result = remove_model(args.remove)
    elif args.remove_all:
        result = remove_all(keep=args.keep)

    print(json.dumps(result, indent=2))

    if not result.get("success", True):
        sys.exit(1)


if __name__ == "__main__":
    main()
