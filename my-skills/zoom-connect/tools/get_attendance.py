#!/usr/bin/env python3
"""
Get Zoom Meeting Attendance
============================
Pull participant list with join/leave times for a completed meeting.

Usage:
    python3 get_attendance.py --meeting-id <id>
    python3 get_attendance.py --uuid <uuid>

Options:
    --meeting-id ID    Zoom meeting ID (numeric)
    --uuid UUID        Meeting UUID (use for PMI / Personal Meeting Room sessions)
    --json             Output as JSON
    --include-email    Include email addresses (only available for signed-in participants)

Examples:
    python3 get_attendance.py --meeting-id 12345678901
    python3 get_attendance.py --uuid "abc123def=="
    python3 get_attendance.py --meeting-id 12345678901 --json
    python3 get_attendance.py --meeting-id 12345678901 --include-email

Notes:
    - Data available ~15 minutes after meeting ends
    - Report data expires after 1 month
    - Email only present if participant was signed into Zoom
    - Reconnecting participants may appear as separate entries
    - PMI meetings reuse the same meeting ID for every session —
      use --uuid (from list_meetings.py output) to target a specific session
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from zoom_client import ZoomClient


def get_attendance(client: ZoomClient, meeting_id: str = None, uuid: str = None) -> dict:
    """
    Get attendance for a past meeting.

    Uses the report endpoint for richest data (join/leave times, duration).

    Args:
        client: ZoomClient instance
        meeting_id: Zoom meeting ID (for scheduled meetings)
        uuid: Meeting UUID (required for PMI meetings — each session has a unique UUID)

    Returns:
        Dict with meeting info and participants list
    """
    # For PMI meetings, the same meeting ID is reused across sessions.
    # The UUID uniquely identifies each session. Zoom requires double-encoding
    # UUIDs that contain / characters.
    if uuid:
        encoded = ZoomClient.encode_uuid(uuid)
        details_endpoint = f"/v2/past_meetings/{encoded}"
        participants_endpoint = f"/v2/report/meetings/{encoded}/participants"
        identifier = uuid
    else:
        details_endpoint = f"/v2/past_meetings/{meeting_id}"
        participants_endpoint = f"/v2/report/meetings/{meeting_id}/participants"
        identifier = meeting_id

    # Get meeting details (may fail if missing meeting:read:past_meeting:admin scope)
    meeting_info = {}
    try:
        meeting_info = client.get(details_endpoint)
    except SystemExit:
        # Fall back — we can still get participants without meeting details
        print(f"Note: Could not fetch meeting details (may need meeting:read:past_meeting:admin scope).", file=sys.stderr)
        print(f"Proceeding with participant data only.\n", file=sys.stderr)

    # Get participants via report endpoint
    participants = client.paginate(
        participants_endpoint,
        params={"page_size": 300},
        key="participants",
        max_items=500
    )

    return {
        "meeting": {
            "id": meeting_info.get("id", meeting_id or ""),
            "uuid": meeting_info.get("uuid", uuid or ""),
            "topic": meeting_info.get("topic", "(no topic)"),
            "start_time": meeting_info.get("start_time", ""),
            "end_time": meeting_info.get("end_time", ""),
            "duration": meeting_info.get("duration", 0),
            "participants_count": meeting_info.get("participants_count", len(participants))
        },
        "participants": participants
    }


def consolidate_participants(participants: list) -> list:
    """
    Consolidate multiple entries for the same participant (reconnections).

    Groups by name (and email if available), uses earliest join and latest leave.

    Args:
        participants: Raw participant list from API

    Returns:
        Consolidated participant list
    """
    by_identity = {}

    for p in participants:
        name = p.get("name", "Unknown")
        email = p.get("user_email", "")
        # Use email as key if available, otherwise name
        key = email if email else name

        if key not in by_identity:
            by_identity[key] = {
                "name": name,
                "email": email,
                "entries": [],
                "first_join": p.get("join_time", ""),
                "last_leave": p.get("leave_time", ""),
                "total_duration": 0
            }

        entry = by_identity[key]
        entry["entries"].append(p)

        # Track total duration
        duration = p.get("duration", 0)
        entry["total_duration"] += duration

        # Update first join / last leave
        join = p.get("join_time", "")
        leave = p.get("leave_time", "")
        if join and (not entry["first_join"] or join < entry["first_join"]):
            entry["first_join"] = join
        if leave and (not entry["last_leave"] or leave > entry["last_leave"]):
            entry["last_leave"] = leave

    # Build consolidated list
    result = []
    for key, entry in by_identity.items():
        result.append({
            "name": entry["name"],
            "email": entry["email"] or "(not signed in)",
            "first_join": entry["first_join"],
            "last_leave": entry["last_leave"],
            "total_duration_seconds": entry["total_duration"],
            "reconnections": len(entry["entries"]),
        })

    # Sort by first join time
    result.sort(key=lambda x: x.get("first_join", ""))
    return result


def format_participant(p: dict, include_email: bool = False, client: 'ZoomClient' = None) -> str:
    """Format a participant for display."""
    name = p.get("name", "Unknown")
    email = p.get("email", "(not signed in)")
    duration = p.get("total_duration_seconds", 0)
    reconnections = p.get("reconnections", 1)

    # Format duration
    minutes = duration // 60
    if minutes >= 60:
        hours = minutes // 60
        mins = minutes % 60
        dur_str = f"{hours}h {mins}m"
    else:
        dur_str = f"{minutes}m"

    # Format join/leave times using client timezone
    first_join = p.get("first_join", "")
    if first_join and client:
        join_str = client.format_time(first_join, fmt="%H:%M")
    elif first_join:
        try:
            dt = datetime.fromisoformat(first_join.replace("Z", "+00:00"))
            join_str = dt.strftime("%H:%M")
        except (ValueError, AttributeError):
            join_str = first_join
    else:
        join_str = "?"

    last_leave = p.get("last_leave", "")
    if last_leave and client:
        leave_str = client.format_time(last_leave, fmt="%H:%M")
    elif last_leave:
        try:
            dt = datetime.fromisoformat(last_leave.replace("Z", "+00:00"))
            leave_str = dt.strftime("%H:%M")
        except (ValueError, AttributeError):
            leave_str = last_leave
    else:
        leave_str = "?"

    parts = [f"  {name}"]
    if include_email:
        parts.append(f"    Email: {email}")
    parts.append(f"    Time: {join_str} - {leave_str} ({dur_str})")
    if reconnections > 1:
        parts.append(f"    Reconnections: {reconnections}")

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Get Zoom Meeting Attendance")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--meeting-id",
                       help="Zoom meeting ID (for scheduled meetings)")
    group.add_argument("--uuid",
                       help="Meeting UUID (for PMI / Personal Meeting Room sessions)")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--include-email", action="store_true",
                        help="Include email addresses")
    parser.add_argument("--profile", default=None,
                        help="Profile name from config (e.g., main)")
    args = parser.parse_args()

    client = ZoomClient(profile=args.profile)
    data = get_attendance(client, meeting_id=args.meeting_id, uuid=args.uuid)
    meeting = data["meeting"]
    raw_participants = data["participants"]
    participants = consolidate_participants(raw_participants)

    if args.json:
        output = {
            "meeting": meeting,
            "participants": participants,
            "raw_participant_count": len(raw_participants),
            "unique_participant_count": len(participants)
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"\nAttendance: {meeting['topic']}")
        start = meeting.get("start_time", "")
        if start:
            print(f"Date: {client.format_time(start)}")
        print(f"Participants: {len(participants)} unique ({len(raw_participants)} total entries)")
        print()

        if not participants:
            print("No participant data available.")
            print("Note: Data is available ~15 minutes after meeting ends.")
            return

        for i, p in enumerate(participants, 1):
            print(f"[{i}]")
            print(format_participant(p, include_email=args.include_email, client=client))
            print()


if __name__ == "__main__":
    main()
