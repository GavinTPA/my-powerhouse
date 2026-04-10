#!/usr/bin/env python3
"""
Google API Manager — Add Team Member
======================================
Creates a Google Cloud project, links billing, enables API,
creates a restricted key, sets budget alert, and returns the key string.

Usage:
    python3 tools/add_member.py "Sarah Jones"
    python3 tools/add_member.py "Sarah Jones" --budget 30
"""

import sys
import re
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gcloud_client import GCloudClient


def name_to_project_id(prefix: str, name: str) -> str:
    """Convert a name to a valid GCP project ID.

    Rules: 6-30 chars, lowercase, letters/numbers/hyphens only.
    """
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    project_id = f"{prefix}-{slug}"
    # Truncate to 30 chars (GCP limit)
    project_id = project_id[:30].rstrip("-")
    return project_id


def add_member(name: str, budget_override: int = None):
    """Add a team member — full provisioning sequence."""
    client = GCloudClient()

    if not client.is_configured():
        print("ERROR: Google API Manager is not configured yet.")
        print("Run setup first: python3 tools/setup.py")
        sys.exit(1)

    # Check for duplicate
    existing = client.find_member(name)
    if existing:
        print(f"ERROR: '{name}' already exists as {existing['project_id']} "
              f"(status: {existing['status']})")
        print("Use revoke_member.py to remove them first, or choose a different name.")
        sys.exit(1)

    project_id = name_to_project_id(client.project_prefix, name)
    billing_id = client.billing_account_id
    budget_amount = budget_override or client.budget_per_member_usd

    print(f"Adding team member: {name}")
    print(f"Project ID: {project_id}")
    print(f"Budget alert: ${budget_amount}/month")
    print()

    # Step 1: Create project
    print("[1/6] Creating Google Cloud project...")
    result = client.run_raw([
        "projects", "create", project_id, f'--name={name}'
    ], timeout=30)
    if not result["ok"]:
        error = result["error"]
        if "already exists" in error.lower():
            # Try with a number suffix
            for i in range(2, 10):
                alt_id = f"{project_id}-{i}"[:30]
                result = client.run_raw([
                    "projects", "create", alt_id, f'--name={name}'
                ], timeout=30)
                if result["ok"]:
                    project_id = alt_id
                    print(f"  Used alternate ID: {project_id}")
                    break
            else:
                print(f"  ERROR: {error}")
                sys.exit(1)
        else:
            print(f"  ERROR: {error}")
            sys.exit(1)
    print(f"  OK: Project {project_id} created")

    # Step 2: Link billing
    print("[2/6] Linking billing account...")
    result = client.run_raw([
        "billing", "projects", "link", project_id,
        f"--billing-account={billing_id}"
    ], timeout=30)
    if not result["ok"]:
        print(f"  ERROR: {result['error']}")
        print("  You may need to link billing manually at console.cloud.google.com/billing")
        sys.exit(1)
    print("  OK: Billing linked")

    # Step 3: Enable API
    print("[3/6] Enabling Generative Language API...")
    result = client.run_raw([
        "services", "enable", "generativelanguage.googleapis.com",
        f"--project={project_id}"
    ], timeout=60)
    if not result["ok"]:
        print(f"  ERROR: {result['error']}")
        sys.exit(1)
    print("  OK: API enabled")

    # Step 4: Create restricted API key
    print("[4/6] Creating restricted API key...")
    result = client.run_raw([
        "services", "api-keys", "create",
        f"--project={project_id}",
        f'--display-name={name} Gemini Key',
        "--api-target=service=generativelanguage.googleapis.com"
    ], timeout=60)
    if not result["ok"]:
        print(f"  ERROR: {result['error']}")
        sys.exit(1)
    print("  OK: API key created (restricted to image generation)")

    # Step 5: Get the key string
    print("[5/6] Retrieving key string...")
    result = client.run([
        "services", "api-keys", "list",
        f"--project={project_id}",
        '--format=value(name)',
        "--limit=1"
    ], json_output=False, timeout=30)
    if not result["ok"] or not result["data"]:
        print(f"  ERROR: Could not list keys: {result.get('error', 'no output')}")
        sys.exit(1)
    key_id = result["data"].strip()

    result = client.run([
        "services", "api-keys", "get-key-string", key_id,
        f"--project={project_id}"
    ], json_output=False, timeout=30)
    if not result["ok"]:
        print(f"  ERROR: Could not get key string: {result['error']}")
        sys.exit(1)

    # Parse key string from output (format: "keyString: AIza...")
    key_string = result["data"].strip()
    if "keyString:" in key_string:
        key_string = key_string.split("keyString:")[-1].strip()

    if not key_string.startswith("AIza"):
        print(f"  WARNING: Key string doesn't start with AIza: {key_string[:20]}...")
        print("  This might still work — verify manually.")

    print(f"  OK: Key string retrieved")

    # Step 6: Set budget alert
    print(f"[6/6] Setting budget alert (${budget_amount}/month)...")
    result = client.run_raw([
        "billing", "budgets", "create",
        f"--billing-account={billing_id}",
        f'--display-name={name} Budget',
        f"--budget-amount={budget_amount}",
        f'--filter-projects=projects/{project_id}',
        "--threshold-rule=percent=0.9,basis=current-spend",
        "--threshold-rule=percent=1.0,basis=current-spend",
    ], timeout=30)
    if result["ok"]:
        print(f"  OK: Budget alert set at ${budget_amount}/month")
    else:
        print(f"  WARNING: Budget alert failed: {result['error']}")
        print("  You can create it manually at console.cloud.google.com/billing/budgets")

    # Save to config
    client.add_member_to_config(name, project_id, key_id, key_string)

    # Summary
    print()
    print("=" * 50)
    print(f"DONE: {name} is set up")
    print(f"Project:    {project_id}")
    print(f"Key String: {key_string}")
    print(f"Budget:     ${budget_amount}/month alert")
    print()
    print("Send this key to your team member.")
    print('They paste it when Claude asks during "set up nano banana pro".')
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Add a team member")
    parser.add_argument("name", help="Team member's full name (e.g., 'Sarah Jones')")
    parser.add_argument("--budget", type=int, default=None,
                        help="Override per-member budget (default: from config)")
    args = parser.parse_args()

    add_member(args.name, args.budget)


if __name__ == "__main__":
    main()
