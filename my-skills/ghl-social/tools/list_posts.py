#!/usr/bin/env python3
"""
List Social Media Posts
========================
View scheduled, published, and draft posts in GHL Social Planner.

Usage:
    python3 list_posts.py                  # All posts
    python3 list_posts.py --json           # Raw JSON
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ghl_social_client import GHLSocialClient


def main():
    parser = argparse.ArgumentParser(description="List social media posts")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    client = GHLSocialClient()
    posts = client.list_posts()

    if args.json:
        print(json.dumps(posts, indent=2))
        return

    if not posts:
        print("No posts found.")
        return

    print(f"Posts ({len(posts)}):")
    print(f"{'─' * 70}")

    for post in posts:
        status = post.get("status", "unknown")
        summary = post.get("summary", "")[:60]
        post_id = post.get("id", "n/a")
        schedule = post.get("scheduleAt", "not scheduled")
        accounts = post.get("accountIds", [])

        print(f"  [{status:10s}] {summary}")
        print(f"  {'':12s} ID: {post_id}")
        print(f"  {'':12s} Schedule: {schedule}")
        print(f"  {'':12s} Accounts: {len(accounts)}")
        print()

    print(f"{'─' * 70}")
    print(f"Total: {len(posts)} posts")


if __name__ == "__main__":
    main()
