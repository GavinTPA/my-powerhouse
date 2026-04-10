#!/usr/bin/env python3
"""
Get Zoom Meeting Recordings
=============================
List recording files (MP4, TRANSCRIPT, CHAT, etc.) for a meeting.

Usage:
    python3 get_recordings.py --meeting-id <id>
    python3 get_recordings.py --uuid <uuid>

Options:
    --meeting-id ID    Zoom meeting ID
    --uuid UUID        Meeting UUID (use for PMI / Personal Meeting Room sessions)
    --json             Output as JSON
    --type TYPE        Filter by file type: MP4, M4A, CHAT, TRANSCRIPT, TIMELINE, CC

Examples:
    python3 get_recordings.py --meeting-id 12345678901
    python3 get_recordings.py --uuid "abc123def=="
    python3 get_recordings.py --meeting-id 12345678901 --type TRANSCRIPT
    python3 get_recordings.py --meeting-id 12345678901 --json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from zoom_client import ZoomClient


def get_recordings(client: ZoomClient, meeting_id: str = None, uuid: str = None,
                   file_type: str = None) -> dict:
    """
    Get recording files for a meeting.

    Args:
        client: ZoomClient instance
        meeting_id: Zoom meeting ID (for scheduled meetings)
        uuid: Meeting UUID (required for PMI meetings — each session has a unique UUID)
        file_type: Optional filter (MP4, M4A, CHAT, TRANSCRIPT, TIMELINE, CC)

    Returns:
        Dict with meeting info and recording_files list
    """
    if uuid:
        encoded = ZoomClient.encode_uuid(uuid)
        endpoint = f"/v2/meetings/{encoded}/recordings"
    else:
        endpoint = f"/v2/meetings/{meeting_id}/recordings"

    response = client.get(endpoint)

    recordings = response.get("recording_files", [])

    if file_type:
        recordings = [r for r in recordings if r.get("file_type") == file_type.upper()]

    return {
        "meeting": {
            "id": response.get("id"),
            "uuid": response.get("uuid"),
            "topic": response.get("topic", "(no topic)"),
            "start_time": response.get("start_time"),
            "duration": response.get("duration"),
            "total_size": response.get("total_size", 0),
            "recording_count": response.get("recording_count", len(recordings)),
            "share_url": response.get("share_url", ""),
            "password": response.get("password", "")
        },
        "recording_files": recordings
    }


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


def format_recording(rec: dict, client: ZoomClient = None) -> str:
    """Format a recording file for display."""
    file_type = rec.get("file_type", "?")
    file_size = rec.get("file_size", 0)
    status = rec.get("status", "")
    recording_start = rec.get("recording_start", "")
    rec_id = rec.get("id", "")

    lines = []
    lines.append(f"  Type: {file_type}")
    lines.append(f"  Size: {format_size(file_size)}")
    lines.append(f"  Status: {status}")

    if recording_start and client:
        lines.append(f"  Recorded: {client.format_time(recording_start)}")
    elif recording_start:
        try:
            dt = datetime.fromisoformat(recording_start.replace("Z", "+00:00"))
            lines.append(f"  Recorded: {dt.strftime('%Y-%m-%d %H:%M UTC')}")
        except (ValueError, AttributeError):
            lines.append(f"  Recorded: {recording_start}")

    if rec_id:
        lines.append(f"  Recording ID: {rec_id}")

    has_url = bool(rec.get("download_url"))
    lines.append(f"  Download URL: {'available' if has_url else 'not yet available'}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Get Zoom Meeting Recordings")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--meeting-id",
                       help="Zoom meeting ID (for scheduled meetings)")
    group.add_argument("--uuid",
                       help="Meeting UUID (for PMI / Personal Meeting Room sessions)")
    parser.add_argument("--type", dest="file_type", default=None,
                        choices=["MP4", "M4A", "CHAT", "TRANSCRIPT", "TIMELINE", "CC"],
                        help="Filter by file type")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--profile", default=None,
                        help="Profile name from config (e.g., main)")
    args = parser.parse_args()

    client = ZoomClient(profile=args.profile)
    data = get_recordings(client, meeting_id=args.meeting_id, uuid=args.uuid,
                          file_type=args.file_type)
    meeting = data["meeting"]
    recordings = data["recording_files"]

    if args.json:
        # Include download URLs in JSON output for programmatic use
        simplified = []
        for r in recordings:
            simplified.append({
                "id": r.get("id"),
                "file_type": r.get("file_type"),
                "file_size": r.get("file_size"),
                "status": r.get("status"),
                "recording_start": r.get("recording_start"),
                "recording_end": r.get("recording_end"),
                "download_url": r.get("download_url", "")
            })
        output = {
            "meeting": meeting,
            "recording_files": simplified
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\nRecordings: {meeting['topic']}")
        print(f"Total size: {format_size(meeting.get('total_size', 0))}")
        print(f"Files: {len(recordings)}")
        if meeting.get("share_url"):
            print(f"Share link: {meeting['share_url']}")
            if meeting.get("password"):
                print(f"Password: {meeting['password']}")
        print()

        if not recordings:
            print("No recording files found.")
            print("Recordings may still be processing (can take 1+ hours).")
            return

        for i, rec in enumerate(recordings, 1):
            print(f"[{i}]")
            print(format_recording(rec, client=client))
            print()


if __name__ == "__main__":
    main()
