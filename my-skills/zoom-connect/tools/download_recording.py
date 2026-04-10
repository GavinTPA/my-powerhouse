#!/usr/bin/env python3
"""
Download Zoom Recording Files
===============================
Download specific recording files (transcript, chat, video) to local storage.

Usage:
    python3 download_recording.py --meeting-id <id> --type <TYPE>
    python3 download_recording.py --uuid <uuid> --type <TYPE>

Options:
    --meeting-id ID    Zoom meeting ID
    --uuid UUID        Meeting UUID (use for PMI / Personal Meeting Room sessions)
    --type TYPE        File type: MP4, M4A, CHAT, TRANSCRIPT, TIMELINE, CC
    --output DIR       Output directory (default: ~/Downloads/zoom-recordings/)
    --all              Download all available files for this meeting

Examples:
    python3 download_recording.py --meeting-id 12345678901 --type TRANSCRIPT
    python3 download_recording.py --uuid "abc123def==" --type CHAT
    python3 download_recording.py --meeting-id 12345678901 --all
    python3 download_recording.py --meeting-id 12345678901 --type MP4 --output ~/Downloads/
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from zoom_client import ZoomClient


# File extensions for each type
FILE_EXTENSIONS = {
    "MP4": ".mp4",
    "M4A": ".m4a",
    "CHAT": ".txt",
    "TRANSCRIPT": ".vtt",
    "TIMELINE": ".json",
    "CC": ".vtt"
}


def safe_filename(text: str) -> str:
    """Convert text to a safe filename."""
    # Replace unsafe chars with hyphens
    safe = ""
    for c in text:
        if c.isalnum() or c in "-_ ":
            safe += c
        else:
            safe += "-"
    # Collapse multiple hyphens/spaces
    while "  " in safe:
        safe = safe.replace("  ", " ")
    while "--" in safe:
        safe = safe.replace("--", "-")
    return safe.strip(" -")


def download_files(client: ZoomClient, meeting_id: str = None, uuid: str = None,
                   file_type: str = None, download_all: bool = False,
                   output_dir: Path = None) -> list:
    """
    Download recording files for a meeting.

    Args:
        client: ZoomClient instance
        meeting_id: Zoom meeting ID (for scheduled meetings)
        uuid: Meeting UUID (required for PMI meetings — each session has a unique UUID)
        file_type: Specific file type to download
        download_all: Download all available files
        output_dir: Directory to save files

    Returns:
        List of downloaded file paths
    """
    if output_dir is None:
        output_dir = client.download_dir

    # Get recordings
    if uuid:
        encoded = ZoomClient.encode_uuid(uuid)
        endpoint = f"/v2/meetings/{encoded}/recordings"
    else:
        endpoint = f"/v2/meetings/{meeting_id}/recordings"

    response = client.get(endpoint)
    topic = safe_filename(response.get("topic", "meeting"))
    recordings = response.get("recording_files", [])

    if not recordings:
        print("No recording files available.", file=sys.stderr)
        print("Recordings may still be processing.", file=sys.stderr)
        return []

    # Filter by type
    if file_type and not download_all:
        recordings = [r for r in recordings if r.get("file_type") == file_type.upper()]
        if not recordings:
            print(f"No {file_type} file found for this meeting.", file=sys.stderr)
            available = set(r.get("file_type", "?") for r in response.get("recording_files", []))
            print(f"Available types: {', '.join(sorted(available))}", file=sys.stderr)
            return []

    downloaded = []

    for rec in recordings:
        ft = rec.get("file_type", "UNKNOWN")
        download_url = rec.get("download_url", "")
        status = rec.get("status", "")

        if not download_url:
            print(f"  Skipping {ft}: no download URL (status: {status})")
            continue

        if status == "processing":
            print(f"  Skipping {ft}: still processing")
            continue

        # Build filename
        ext = FILE_EXTENSIONS.get(ft, ".bin")
        # Include date from recording start
        rec_start = rec.get("recording_start", "")
        date_str = ""
        if rec_start:
            try:
                dt = datetime.fromisoformat(rec_start.replace("Z", "+00:00"))
                date_str = dt.strftime("%Y-%m-%d")
            except (ValueError, AttributeError):
                pass

        if date_str:
            filename = f"{topic}-{date_str}-{ft.lower()}{ext}"
        else:
            filename = f"{topic}-{ft.lower()}{ext}"

        dest = output_dir / filename

        print(f"  Downloading {ft} ({format_size(rec.get('file_size', 0))})...")
        client.download(download_url, dest)
        print(f"  Saved: {dest}")
        downloaded.append(str(dest))

    return downloaded


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable."""
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f"{size:.1f} {units[i]}"


def main():
    parser = argparse.ArgumentParser(description="Download Zoom Recording Files")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--meeting-id",
                       help="Zoom meeting ID (for scheduled meetings)")
    group.add_argument("--uuid",
                       help="Meeting UUID (for PMI / Personal Meeting Room sessions)")
    parser.add_argument("--type", dest="file_type", default=None,
                        choices=["MP4", "M4A", "CHAT", "TRANSCRIPT", "TIMELINE", "CC"],
                        help="File type to download")
    parser.add_argument("--all", dest="download_all", action="store_true",
                        help="Download all available files")
    parser.add_argument("--output", dest="output_dir", default=None,
                        help="Output directory")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")
    parser.add_argument("--profile", default=None,
                        help="Profile name from config (e.g., main)")
    args = parser.parse_args()

    if not args.file_type and not args.download_all:
        print("Error: Specify --type or --all", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir) if args.output_dir else None
    identifier = args.uuid or args.meeting_id

    client = ZoomClient(profile=args.profile)
    print(f"\nDownloading recordings for meeting {identifier}...")

    downloaded = download_files(
        client, meeting_id=args.meeting_id, uuid=args.uuid,
        file_type=args.file_type,
        download_all=args.download_all,
        output_dir=output_dir
    )

    if args.json:
        print(json.dumps({"downloaded": downloaded}, indent=2))
    else:
        print(f"\nDownloaded {len(downloaded)} file(s).")


if __name__ == "__main__":
    main()
