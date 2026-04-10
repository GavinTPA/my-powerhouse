#!/usr/bin/env python3
"""
List Zoom Meetings
==================
Find meetings by date range for a user.

Usage:
    python3 list_meetings.py [options]

Options:
    --from DATE        Start date (YYYY-MM-DD), default: 30 days ago
    --to DATE          End date (YYYY-MM-DD), default: today
    --type TYPE        Meeting type: past, upcoming (default: past)
    --user EMAIL       User email to query (default: from config)
    --limit N          Maximum meetings (default: 30)
    --json             Output as JSON

Examples:
    python3 list_meetings.py
    python3 list_meetings.py --from 2026-02-01 --to 2026-02-12
    python3 list_meetings.py --user host@example.com
    python3 list_meetings.py --json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from zoom_client import ZoomClient


def list_meetings(client: ZoomClient, from_date: str = None, to_date: str = None,
                  meeting_type: str = "past", limit: int = 30,
                  user_email: str = None) -> list:
    """
    List meetings for a user.

    Args:
        client: ZoomClient instance
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        meeting_type: "past" or "upcoming"
        limit: Max meetings to return
        user_email: User email to query (default: from config)

    Returns:
        List of meeting dicts
    """
    user = user_email or client.user_email

    # Report endpoint requires an actual email — "me" is not accepted.
    # Resolve it by calling /v2/users/me to get the real email.
    if user == "me" and meeting_type == "past":
        me = client.get("/v2/users/me")
        user = me.get("email", user)

    if meeting_type == "past":
        # Report endpoint returns ALL past meetings including PMI sessions.
        # The standard /v2/users/{}/meetings?type=previous_meetings does NOT
        # reliably return Personal Meeting Room meetings.
        endpoint = f"/v2/report/users/{user}/meetings"
        params = {
            "type": "past",
            "page_size": min(limit, 300)
        }
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        meetings = client.paginate(endpoint, params, key="meetings", max_items=limit)
    else:
        # Upcoming meetings
        endpoint = f"/v2/users/{user}/meetings"
        params = {
            "type": "upcoming",
            "page_size": min(limit, 300)
        }
        meetings = client.paginate(endpoint, params, key="meetings", max_items=limit)

    return meetings


def format_meeting(meeting: dict, client: ZoomClient = None) -> str:
    """Format a meeting for display."""
    topic = meeting.get("topic", "(no topic)")
    meeting_id = meeting.get("id", "")
    uuid = meeting.get("uuid", "")
    start = meeting.get("start_time", "")
    duration = meeting.get("duration", 0)

    # Parse start time for display
    if start and client:
        start_display = client.format_time(start)
    elif start:
        try:
            dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            start_display = dt.strftime("%Y-%m-%d %H:%M UTC")
        except (ValueError, AttributeError):
            start_display = start
    else:
        start_display = "(no start time)"

    lines = []
    lines.append(f"  Topic: {topic}")
    lines.append(f"  Meeting ID: {meeting_id}")
    if uuid:
        lines.append(f"  UUID: {uuid}")
    lines.append(f"  Start: {start_display}")
    if duration:
        lines.append(f"  Duration: {duration} min")

    return "\n".join(lines)


def filter_by_topic(meetings: list, topic_keyword: str) -> list:
    """Filter meetings whose topic contains the keyword (case-insensitive)."""
    keyword_lower = topic_keyword.lower()
    return [m for m in meetings if keyword_lower in m.get("topic", "").lower()]


def main():
    parser = argparse.ArgumentParser(
        description="List Zoom Meetings",
        epilog="""examples:
  python3 list_meetings.py --topic "powerhouse"
  python3 list_meetings.py --topic "workshop" --from 2026-02-01
  python3 list_meetings.py --topic "coaching" --user host@example.com"""
    )
    parser.add_argument("--from", dest="from_date", default=None,
                        help="Start date YYYY-MM-DD (default: 30 days ago)")
    parser.add_argument("--to", dest="to_date", default=None,
                        help="End date YYYY-MM-DD (default: today)")
    parser.add_argument("--type", dest="meeting_type", default="past",
                        choices=["past", "upcoming"],
                        help="Meeting type (default: past)")
    parser.add_argument("--user", dest="user_email", default=None,
                        help="User email to query (default: from config)")
    parser.add_argument("--topic", default=None,
                        help="Filter meetings by topic keyword (case-insensitive)")
    parser.add_argument("--limit", type=int, default=30,
                        help="Max meetings (default: 30)")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--profile", default=None,
                        help="Profile name from config (e.g., main)")
    args = parser.parse_args()

    # Defaults for date range
    if not args.from_date:
        args.from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if not args.to_date:
        args.to_date = datetime.now().strftime("%Y-%m-%d")

    client = ZoomClient(profile=args.profile)
    meetings = list_meetings(client, args.from_date, args.to_date,
                             args.meeting_type, args.limit, args.user_email)
    user = args.user_email or client.user_email

    # Apply topic filter if specified
    if args.topic:
        meetings = filter_by_topic(meetings, args.topic)
        if not meetings:
            print(f"No meetings found matching topic: {args.topic}")
            return

    if args.json:
        simplified = []
        for m in meetings:
            simplified.append({
                "id": m.get("id"),
                "uuid": m.get("uuid"),
                "topic": m.get("topic"),
                "start_time": m.get("start_time"),
                "duration": m.get("duration"),
                "type": m.get("type")
            })
        print(json.dumps(simplified, indent=2))
    else:
        header_parts = [f"User: {user}", f"Type: {args.meeting_type}"]
        if args.topic:
            header_parts.append(f'Topic: "{args.topic}"')
        header_parts.append(f"Found: {len(meetings)}")

        print(f"\nZoom Meetings ({args.from_date} to {args.to_date})")
        print(f"{' | '.join(header_parts)}\n")

        if not meetings:
            print("No meetings found in this date range.")
            return

        for i, meeting in enumerate(meetings, 1):
            print(f"[{i}]")
            print(format_meeting(meeting, client=client))
            print()


if __name__ == "__main__":
    main()
