#!/usr/bin/env python3
"""
List Zoom Users
===============
List all users on a Zoom account (for shared/multi-user accounts).

Usage:
    python3 list_users.py [options]

Options:
    --status STATUS    User status: active, inactive, pending (default: active)
    --limit N          Maximum users (default: 100)
    --json             Output as JSON

Examples:
    python3 list_users.py
    python3 list_users.py --status active --json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from zoom_client import ZoomClient


def list_users(client: ZoomClient, status: str = "active", limit: int = 100) -> list:
    """
    List users on the Zoom account.

    Args:
        client: ZoomClient instance
        status: "active", "inactive", or "pending"
        limit: Max users to return

    Returns:
        List of user dicts
    """
    endpoint = "/v2/users"
    params = {
        "status": status,
        "page_size": min(limit, 300)
    }

    users = client.paginate(endpoint, params, key="users", max_items=limit)
    return users


def format_user(user: dict) -> str:
    """Format a user for display."""
    name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "(no name)"
    email = user.get("email", "(no email)")
    user_type = user.get("type", 0)
    status = user.get("status", "")

    type_labels = {1: "Basic", 2: "Licensed", 3: "On-Prem", 99: "None"}
    type_label = type_labels.get(user_type, f"Type {user_type}")

    lines = []
    lines.append(f"  Name: {name}")
    lines.append(f"  Email: {email}")
    lines.append(f"  Type: {type_label}")
    if status:
        lines.append(f"  Status: {status}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="List Zoom Users")
    parser.add_argument("--status", default="active",
                        choices=["active", "inactive", "pending"],
                        help="User status (default: active)")
    parser.add_argument("--limit", type=int, default=100,
                        help="Max users (default: 100)")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    parser.add_argument("--profile", default=None,
                        help="Profile name from config (e.g., main)")
    args = parser.parse_args()

    client = ZoomClient(profile=args.profile)
    users = list_users(client, args.status, args.limit)

    if args.json:
        simplified = []
        for u in users:
            simplified.append({
                "id": u.get("id"),
                "email": u.get("email"),
                "first_name": u.get("first_name"),
                "last_name": u.get("last_name"),
                "type": u.get("type"),
                "status": u.get("status")
            })
        print(json.dumps(simplified, indent=2))
    else:
        print(f"\nZoom Users (status: {args.status})")
        print(f"Found: {len(users)}\n")

        if not users:
            print("No users found with this status.")
            return

        for i, user in enumerate(users, 1):
            print(f"[{i}]")
            print(format_user(user))
            print()


if __name__ == "__main__":
    main()
