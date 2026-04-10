#!/usr/bin/env python3
"""
Google API Manager — Setup
===========================
First-time setup wizard. Checks gcloud, auth, billing, and creates config.

Usage:
    python3 tools/setup.py
    python3 tools/setup.py --check   # Just verify current state
"""

import sys
import argparse
from pathlib import Path

# Add tools dir to path for sibling imports
sys.path.insert(0, str(Path(__file__).parent))
from gcloud_client import GCloudClient


def check_status(client: GCloudClient):
    """Print current setup status."""
    print("Google API Manager — Status Check")
    print("=" * 40)

    installed, version = client.check_gcloud_installed()
    print(f"gcloud CLI:    {'OK — ' + version if installed else 'NOT INSTALLED'}")

    if installed:
        authed, account = client.check_auth()
        print(f"Authentication: {'OK — ' + account if authed else 'NOT AUTHENTICATED'}")
    else:
        print("Authentication: SKIPPED (gcloud not installed)")

    if client.is_configured():
        print(f"Billing Account: {client.billing_account_id}")
        print(f"Project Prefix:  {client.project_prefix}")
        print(f"Member Budget:   ${client.budget_per_member_usd}/month")
        print(f"Overall Budget:  ${client.overall_budget_usd}/month")
        print(f"Team Members:    {len(client.members)}")
        for m in client.members:
            status_icon = "active" if m.get("status") == "active" else "disabled"
            print(f"  - {m['name']} ({m['project_id']}) [{status_icon}]")
    else:
        print("Config: NOT YET CONFIGURED")
        print(f"Config file: {GCloudClient.CONFIG_PATH if hasattr(GCloudClient, 'CONFIG_PATH') else '~/.config/google-api-manager.yaml'}")

    print()


def run_setup(client: GCloudClient):
    """Interactive setup wizard."""
    print("Google API Manager — Setup Wizard")
    print("=" * 40)
    print()

    # Step 1: Check gcloud
    installed, version = client.check_gcloud_installed()
    if not installed:
        print("ERROR: gcloud CLI is not installed.")
        print()
        print("Install it first:")
        print("  Mac:     brew install --cask google-cloud-sdk")
        print("  Windows: winget install Google.CloudSDK")
        print()
        print("Then close this terminal, open a new one, and run setup again.")
        sys.exit(1)
    print(f"[OK] gcloud CLI installed: {version}")

    # Step 2: Check auth
    authed, account = client.check_auth()
    if not authed:
        print()
        print("Not authenticated. Running: gcloud auth login")
        print("This will open your browser — sign in with the Google account")
        print("that will own the billing for your team.")
        print()
        import subprocess
        result = subprocess.run(["gcloud", "auth", "login"], timeout=120)
        if result.returncode != 0:
            print("ERROR: Authentication failed. Try again.")
            sys.exit(1)
        authed, account = client.check_auth()
    print(f"[OK] Authenticated as: {account}")

    # Step 3: Get billing account
    print()
    print("Looking for billing accounts...")
    result = client.run(["billing", "accounts", "list"])
    if not result["ok"]:
        print(f"ERROR: {result['error']}")
        print()
        print("You may need to create a billing account first:")
        print("  Open: console.cloud.google.com/billing")
        sys.exit(1)

    accounts = result["data"]
    if not accounts:
        print("No billing accounts found.")
        print("Create one at: console.cloud.google.com/billing")
        print("Then run setup again.")
        sys.exit(1)

    if len(accounts) == 1:
        billing_id = accounts[0]["name"].split("/")[-1]
        billing_name = accounts[0].get("displayName", "")
        print(f"[OK] Found billing account: {billing_name} ({billing_id})")
    else:
        print("Multiple billing accounts found:")
        for i, acct in enumerate(accounts, 1):
            acct_id = acct["name"].split("/")[-1]
            acct_name = acct.get("displayName", "")
            print(f"  {i}. {acct_name} ({acct_id})")
        print()
        choice = input(f"Which one? [1-{len(accounts)}]: ").strip()
        try:
            idx = int(choice) - 1
            billing_id = accounts[idx]["name"].split("/")[-1]
        except (ValueError, IndexError):
            print("Invalid choice. Run setup again.")
            sys.exit(1)

    # Step 4: Get project prefix
    print()
    prefix = input("Project prefix for your team (e.g., 'ww' for Workshop Whisperer): ").strip().lower()
    if not prefix:
        print("Prefix is required. Run setup again.")
        sys.exit(1)
    # Clean prefix — lowercase, hyphens only
    prefix = "".join(c if c.isalnum() or c == "-" else "-" for c in prefix)
    print(f"[OK] Project prefix: {prefix}")
    print(f"     Members will get projects like: {prefix}-sarah-jones")

    # Step 5: Budget settings
    print()
    budget_input = input("Per-member monthly budget alert (USD) [20]: ").strip()
    member_budget = int(budget_input) if budget_input else 20

    overall_input = input("Overall team monthly budget alert (USD) [100]: ").strip()
    overall_budget = int(overall_input) if overall_input else 100

    # Step 6: Save config
    client.config.update({
        "billing_account_id": billing_id,
        "project_prefix": prefix,
        "budget_per_member_usd": member_budget,
        "overall_budget_usd": overall_budget,
        "members": client.config.get("members", []),
    })
    client.save_config()
    print()
    print(f"[OK] Config saved to ~/.config/google-api-manager.yaml")

    # Step 7: Offer to create overall budget alert
    print()
    create_budget = input(f"Create overall budget alert for ${overall_budget}/month? [Y/n]: ").strip().lower()
    if create_budget != "n":
        result = client.run_raw([
            "billing", "budgets", "create",
            f"--billing-account={billing_id}",
            f'--display-name=Team Monthly Budget',
            f"--budget-amount={overall_budget}",
            "--threshold-rule=percent=0.5,basis=current-spend",
            "--threshold-rule=percent=0.9,basis=current-spend",
            "--threshold-rule=percent=1.0,basis=current-spend",
        ], timeout=30)
        if result["ok"]:
            print(f"[OK] Budget alert created: ${overall_budget}/month")
        else:
            print(f"Warning: Budget alert failed: {result['error']}")
            print("You can create it manually later at console.cloud.google.com/billing/budgets")

    print()
    print("Setup complete! You can now add team members:")
    print('  "add team member Sarah Jones"')


def main():
    parser = argparse.ArgumentParser(description="Google API Manager Setup")
    parser.add_argument("--check", action="store_true",
                        help="Check current status without modifying anything")
    args = parser.parse_args()

    client = GCloudClient()

    if args.check:
        check_status(client)
    else:
        run_setup(client)


if __name__ == "__main__":
    main()
