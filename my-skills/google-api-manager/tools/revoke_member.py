#!/usr/bin/env python3
"""
Google API Manager — Revoke Team Member Access
================================================
Disable, delete key, or delete entire project for a team member.

Usage:
    python3 tools/revoke_member.py "Sarah Jones" --disable
    python3 tools/revoke_member.py "Sarah Jones" --delete-key
    python3 tools/revoke_member.py "Sarah Jones" --delete-project
"""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gcloud_client import GCloudClient


def revoke_member(name: str, action: str):
    """Revoke a team member's access."""
    client = GCloudClient()

    if not client.is_configured():
        print("ERROR: Google API Manager is not configured yet.")
        sys.exit(1)

    member = client.find_member(name)
    if not member:
        print(f"ERROR: No team member matching '{name}' found.")
        print("Current members:")
        for m in client.members:
            print(f"  - {m['name']} ({m['project_id']})")
        sys.exit(1)

    project_id = member["project_id"]
    key_id = member.get("key_id", "")
    member_name = member["name"]

    print(f"Revoking access for: {member_name}")
    print(f"Project: {project_id}")
    print(f"Action: {action}")
    print()

    if action == "disable":
        # Disable the key (reversible)
        if not key_id:
            print("ERROR: No key ID stored for this member.")
            print("Check manually: gcloud services api-keys list "
                  f"--project={project_id}")
            sys.exit(1)

        print("Disabling API key (reversible)...")
        result = client.run_raw([
            "services", "api-keys", "update", key_id,
            f"--project={project_id}", "--no-enable"
        ], timeout=30)
        if result["ok"]:
            client.update_member_status(member_name, "disabled")
            print(f"OK: Key disabled for {member_name}")
            print("To re-enable later: gcloud services api-keys update "
                  f"{key_id} --project={project_id} --enable")
        else:
            print(f"ERROR: {result['error']}")
            sys.exit(1)

    elif action == "delete-key":
        # Delete the key (permanent, but project stays)
        if not key_id:
            print("ERROR: No key ID stored for this member.")
            sys.exit(1)

        print("Deleting API key (permanent)...")
        result = client.run_raw([
            "services", "api-keys", "delete", key_id,
            f"--project={project_id}"
        ], timeout=30)
        if result["ok"]:
            client.update_member_status(member_name, "key-deleted")
            print(f"OK: Key deleted for {member_name}")
            print("Project still exists — create a new key if needed.")
        else:
            print(f"ERROR: {result['error']}")
            sys.exit(1)

    elif action == "delete-project":
        # Delete the entire project (nuclear — 30-day recovery window)
        print("Deleting entire project (30-day recovery window)...")
        result = client.run_raw([
            "projects", "delete", project_id
        ], timeout=30)
        if result["ok"]:
            client.update_member_status(member_name, "project-deleted")
            print(f"OK: Project {project_id} scheduled for deletion")
            print("Recovery window: 30 days")
            print(f"To recover: gcloud projects undelete {project_id}")
        else:
            print(f"ERROR: {result['error']}")
            sys.exit(1)

    else:
        print(f"ERROR: Unknown action '{action}'")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Revoke team member access")
    parser.add_argument("name", help="Team member's name")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--disable", action="store_const", const="disable",
                       dest="action", help="Disable key (reversible)")
    group.add_argument("--delete-key", action="store_const", const="delete-key",
                       dest="action", help="Delete key (permanent)")
    group.add_argument("--delete-project", action="store_const",
                       const="delete-project", dest="action",
                       help="Delete entire project (30-day recovery)")
    args = parser.parse_args()

    revoke_member(args.name, args.action)


if __name__ == "__main__":
    main()
