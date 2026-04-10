#!/usr/bin/env python3
"""
Google API Manager — Check Team Spending
==========================================
Shows budget status for all team members.

Usage:
    python3 tools/check_spending.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gcloud_client import GCloudClient


def check_spending():
    """Show budget status for all team members."""
    client = GCloudClient()

    if not client.is_configured():
        print("ERROR: Google API Manager is not configured yet.")
        sys.exit(1)

    billing_id = client.billing_account_id

    print("Team Spending — Budget Status")
    print("=" * 50)
    print()

    # Get all budgets
    result = client.run([
        "billing", "budgets", "list",
        f"--billing-account={billing_id}"
    ], timeout=30)

    if not result["ok"]:
        print(f"ERROR: {result['error']}")
        print()
        print("Check spending in the browser instead:")
        print("  console.cloud.google.com/billing")
        sys.exit(1)

    budgets = result["data"] if isinstance(result["data"], list) else []

    if not budgets:
        print("No budget alerts configured.")
        print("Budget alerts are set when adding team members.")
        return

    for budget in budgets:
        display_name = budget.get("displayName", "Unknown")
        amount = budget.get("amount", {})
        specified = amount.get("specifiedAmount", {})
        currency = specified.get("currencyCode", "USD")
        units = specified.get("units", "0")

        print(f"  {display_name}: ${units} {currency}/month")

    print()
    print("Note: Budget alerts are email notifications only.")
    print("For detailed per-person spend, open:")
    print("  console.cloud.google.com/billing")
    print("  Go to Reports > filter by project")
    print()

    # Also show member list for context
    members = client.members
    if members:
        active = [m for m in members if m.get("status") == "active"]
        print(f"Active team members: {len(active)}")
        for m in active:
            print(f"  - {m['name']} ({m['project_id']})")


def main():
    check_spending()


if __name__ == "__main__":
    main()
