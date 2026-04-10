#!/usr/bin/env python3
"""
Mark GHL Conversations as Read
===============================
Mark one or all unread conversations as read via the GHL API.

Usage:
    python3 mark_read.py --conversation-id <id>
    python3 mark_read.py --all-unread
    python3 mark_read.py --all-unread --type Email

Options:
    --conversation-id ID   Mark a single conversation as read
    --all-unread           Mark all unread conversations as read
    --type TYPE            Filter type for --all-unread: Email, SMS, all (default: all)
"""

import argparse
import sys
from pathlib import Path

# Import shared modules
sys.path.insert(0, str(Path(__file__).parent))
from ghl_client import GHLClient
from get_conversations import get_conversations


def mark_conversation_read(client: GHLClient, conversation_id: str) -> bool:
    """
    Mark a single conversation as read by setting unreadCount to 0.

    Args:
        client: GHLClient instance
        conversation_id: The conversation ID to mark as read

    Returns:
        True if successful, False otherwise
    """
    try:
        client.put(
            f"/conversations/{conversation_id}",
            data={
                "locationId": client.location_id,
                "unreadCount": 0,
            },
        )
        return True
    except SystemExit:
        return False


def main():
    parser = argparse.ArgumentParser(description="Mark GHL conversations as read")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--conversation-id", help="Mark a single conversation as read")
    group.add_argument(
        "--all-unread", action="store_true", help="Mark all unread conversations as read"
    )
    parser.add_argument(
        "--type",
        default="all",
        choices=["Email", "SMS", "all"],
        help="Filter type for --all-unread (default: all)",
    )
    args = parser.parse_args()

    client = GHLClient()

    if args.conversation_id:
        # Single conversation
        if mark_conversation_read(client, args.conversation_id):
            print(f"Marked conversation {args.conversation_id} as read")
        else:
            print(f"Failed to mark conversation {args.conversation_id} as read", file=sys.stderr)
            sys.exit(1)
    else:
        # All unread
        print("Fetching unread conversations...")
        conversations = get_conversations(client, status="unread", msg_type=args.type, limit=100)

        if not conversations:
            print("No unread conversations found.")
            return

        total = len(conversations)
        print(f"Found {total} unread conversation(s). Marking as read...")

        succeeded = 0
        failed = 0
        for i, conv in enumerate(conversations, 1):
            conv_id = conv.get("id", "")
            contact = conv.get("contactName", "Unknown")
            if mark_conversation_read(client, conv_id):
                succeeded += 1
                print(f"  [{i}/{total}] Marked as read: {contact} ({conv_id})")
            else:
                failed += 1
                print(f"  [{i}/{total}] FAILED: {contact} ({conv_id})")

        print(f"\nDone. {succeeded} marked as read, {failed} failed.")
        if failed:
            sys.exit(1)


if __name__ == "__main__":
    main()
