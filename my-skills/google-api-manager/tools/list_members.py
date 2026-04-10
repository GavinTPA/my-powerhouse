#!/usr/bin/env python3
"""
Google API Manager — List Team Members
========================================
Shows all team members with their status, project IDs, and key info.

Usage:
    python3 tools/list_members.py
    python3 tools/list_members.py --verify   # Cross-check against live gcloud
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gcloud_client import GCloudClient


def list_members(verify: bool = False):
    """List all team members from config."""
    client = GCloudClient()

    if not client.is_configured():
        print("ERROR: Google API Manager is not configured yet.")
        print("Run setup first.")
        sys.exit(1)

    members = client.members
    if not members:
        print("No team members yet.")
        print('Add one with: "add team member Sarah Jones"')
        return

    print(f"Team Members ({len(members)})")
    print(f"Prefix: {client.project_prefix}")
    print(f"Billing: {client.billing_account_id}")
    print()

    # Table header
    print(f"{'Name':<25} {'Project ID':<30} {'Status':<10} {'Added':<12}")
    print("-" * 77)

    for m in members:
        name = m.get("name", "?")
        project_id = m.get("project_id", "?")
        status = m.get("status", "?")
        added = m.get("added", "?")
        print(f"{name:<25} {project_id:<30} {status:<10} {added:<12}")

    if verify:
        print()
        print("Verifying against live gcloud data...")
        for m in members:
            project_id = m.get("project_id", "")
            result = client.run(["projects", "describe", project_id], timeout=15)
            if result["ok"]:
                state = result["data"].get("lifecycleState", "UNKNOWN")
                print(f"  {project_id}: {state}")
            else:
                print(f"  {project_id}: ERROR — {result['error'][:60]}")

    print()
    print(f"Budget per member: ${client.budget_per_member_usd}/month")
    print(f"Overall budget: ${client.overall_budget_usd}/month")
    print(f"Billing dashboard: console.cloud.google.com/billing")


def main():
    parser = argparse.ArgumentParser(description="List team members")
    parser.add_argument("--verify", action="store_true",
                        help="Cross-check against live gcloud data")
    args = parser.parse_args()

    list_members(verify=args.verify)


if __name__ == "__main__":
    main()
