#!/usr/bin/env python3
"""
GHL Media Library Upload
========================
Upload files (PDFs, images) to GoHighLevel Media Library and get back
a permanent storage URL.

Usage:
    python3 upload_media.py FILE_PATH
    python3 upload_media.py FILE_PATH --dry-run
    python3 upload_media.py FILE_PATH --raw

Examples:
    python3 upload_media.py ~/Downloads/Install-Your-First-Skill.pdf
    # → https://storage.googleapis.com/msgsndr/TAkJ8H3DfDYzhAfrhFFV/media/xxxxx.pdf

    python3 upload_media.py ~/Downloads/guide.pdf --dry-run
    # → File OK, 45.3 KB, application/pdf (would upload)

GHL v2 endpoint: POST /medias/upload-file
- Multipart form: file (bytes) + hosted = false
- 25 MB limit for standard files, 500 MB for video
- Returns a permanent storage.googleapis.com URL

Versioning: Each upload creates a new file with a unique URL.
Old URLs stay alive forever. Update your indexes to point to the new URL.
"""

import sys
import json
import argparse
import mimetypes
from pathlib import Path

# Add tools directory to path for ghl_client import
sys.path.insert(0, str(Path(__file__).parent))
from ghl_client import GHLClient

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500 MB

VIDEO_MIMES = {"video/mp4", "video/mpeg", "video/quicktime", "video/x-msvideo"}


def format_size(size_bytes: int) -> str:
    """Human-readable file size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def upload_file(file_path: str, dry_run: bool = False, raw: bool = False) -> str | None:
    """
    Upload a file to GHL Media Library.

    Args:
        file_path: Path to the local file
        dry_run: If True, validate only — don't upload
        raw: If True, print the full raw API response

    Returns:
        The GHL storage URL, or None on failure
    """
    path = Path(file_path).expanduser()

    if not path.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        return None

    if not path.is_file():
        print(f"Error: Not a file: {path}", file=sys.stderr)
        return None

    # Detect MIME type
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type is None:
        mime_type = "application/octet-stream"

    file_size = path.stat().st_size
    max_size = MAX_VIDEO_SIZE if mime_type in VIDEO_MIMES else MAX_FILE_SIZE

    if file_size > max_size:
        print(f"Error: File too large ({format_size(file_size)}). Max: {format_size(max_size)}", file=sys.stderr)
        return None

    if file_size == 0:
        print("Error: File is empty", file=sys.stderr)
        return None

    if dry_run:
        print(f"File OK, {format_size(file_size)}, {mime_type} (would upload)")
        print(f"  Path: {path}")
        print(f"  Name: {path.name}")
        return None

    # Upload
    client = GHLClient()

    with open(path, "rb") as f:
        file_bytes = f.read()

    files = {
        "file": (path.name, file_bytes, mime_type)
    }
    data = {
        "hosted": "false"
    }

    print(f"Uploading {path.name} ({format_size(file_size)})...")

    response = client.post_multipart("/medias/upload-file", files=files, data=data)

    if response.status_code not in (200, 201):
        print(f"Error: Upload failed with status {response.status_code}", file=sys.stderr)
        print(f"Response: {response.text[:500]}", file=sys.stderr)
        return None

    # Parse response
    try:
        result = response.json()
    except json.JSONDecodeError:
        print(f"Error: Could not parse response as JSON", file=sys.stderr)
        print(f"Raw response: {response.text[:500]}", file=sys.stderr)
        return None

    if raw:
        print("Raw API response:")
        print(json.dumps(result, indent=2))

    # Extract URL — GHL docs don't publish the response schema,
    # so we check several likely field names
    url = None
    for key in ("url", "fileUrl", "file_url", "mediaUrl", "media_url"):
        if key in result:
            url = result[key]
            break

    # Also check nested structures
    if url is None and isinstance(result, dict):
        for value in result.values():
            if isinstance(value, str) and "storage.googleapis.com" in value:
                url = value
                break

    if url:
        print(f"Uploaded: {url}")
        return url
    else:
        print("Upload succeeded but could not extract URL from response.")
        print("Raw response (save this — URL is in here somewhere):")
        print(json.dumps(result, indent=2))
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Upload files to GHL Media Library",
        epilog="Each upload creates a new file with a unique URL. Old URLs stay alive forever."
    )
    parser.add_argument("file", help="Path to the file to upload")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate file without uploading")
    parser.add_argument("--raw", action="store_true",
                        help="Print full raw API response (useful for debugging)")

    args = parser.parse_args()

    result = upload_file(args.file, dry_run=args.dry_run, raw=args.raw)

    if result:
        sys.exit(0)
    elif args.dry_run:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
