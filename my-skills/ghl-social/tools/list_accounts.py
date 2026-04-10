#!/usr/bin/env python3
"""
List Connected Social Accounts
===============================
Shows all social media accounts connected in GHL Social Planner.

Usage:
    python3 list_accounts.py              # Human-readable table
    python3 list_accounts.py --json       # Raw JSON
    python3 list_accounts.py --platform facebook  # Filter by platform
"""

import sys
import json
import argparse
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent))
from ghl_social_client import GHLSocialClient


def main():
    parser = argparse.ArgumentParser(description="List connected social accounts")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--platform", help="Filter by platform (facebook, instagram, linkedin, etc.)")
    args = parser.parse_args()

    client = GHLSocialClient()
    accounts = client.list_accounts()

    if args.platform:
        accounts = [a for a in accounts if a.get("platform") == args.platform]

    if args.json:
        print(json.dumps(accounts, indent=2))
        return

    if not accounts:
        print("No social accounts connected.")
        if args.platform:
            print(f"No {args.platform} accounts found. Check GHL > Marketing > Social Planner")
        return

    print(f"Connected Social Accounts ({len(accounts)}):")
    print(f"{'─' * 70}")

    for acct in accounts:
        expired_flag = " EXPIRED" if acct.get("isExpired") else ""
        stats_flag = " +stats" if acct.get("hasStatisticsPermissions") else ""
        expire_date = acct.get("expire", "")[:10] if acct.get("expire") else "n/a"

        print(f"  {acct['platform']:12s} | {acct['name']:25s} | {acct['type']:8s} | expires {expire_date}{expired_flag}{stats_flag}")

    print(f"{'─' * 70}")
    print(f"Total: {len(accounts)} accounts")


if __name__ == "__main__":
    main()
