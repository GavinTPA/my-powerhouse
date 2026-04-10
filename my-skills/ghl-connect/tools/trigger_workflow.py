#!/usr/bin/env python3
"""
Trigger GHL Workflow
====================
Add contacts to a GHL workflow for bulk email sends.

Usage:
    python3 trigger_workflow.py --workflow-id <id> [options]

Options:
    --workflow-id ID      Required: GHL workflow ID
    --contact-id ID       Single contact to add
    --tag TAG             Add all contacts with this tag
    --limit N             Max contacts when using --tag (default: 50)
    --dry-run             List contacts without triggering

Why workflows?
    - GHL handles deliverability, tracking, unsubscribes
    - No rate limiting concerns (GHL queues sends)
    - One API call per contact vs one per email
    - Ed builds the email template in GHL, skill just triggers

Setup:
    1. Create workflow in GHL (trigger: Contact Added)
    2. Add email action with the message content
    3. Copy workflow ID from URL
    4. Add to ~/.config/ghl-connect.yaml under workflows
"""

import argparse
import json
import sys
from pathlib import Path

# Import shared modules
sys.path.insert(0, str(Path(__file__).parent))
from ghl_client import GHLClient


def search_contacts_by_tag(client: GHLClient, tag: str, limit: int = 50) -> list:
    """
    Find contacts with a specific tag.

    Uses POST /contacts/search with server-side tag filtering.

    Args:
        client: GHLClient instance
        tag: Tag to search for
        limit: Maximum contacts to return

    Returns:
        List of contact dicts with id, name, email
    """
    filters = [{"field": "tags", "operator": "eq", "value": tag}]
    contacts = client.search_contacts_paginated(filters, max_items=limit)

    return [{
        "id": c.get("id"),
        "name": f"{c.get('firstName', '')} {c.get('lastName', '')}".strip(),
        "email": c.get("email", ""),
        "tags": c.get("tags", [])
    } for c in contacts]


def add_to_workflow(client: GHLClient, contact_id: str, workflow_id: str) -> dict:
    """
    Add a contact to a workflow.

    Args:
        client: GHLClient instance
        contact_id: Contact to add
        workflow_id: Workflow to trigger

    Returns:
        API response
    """
    response = client.post(
        f"/contacts/{contact_id}/workflow/{workflow_id}",
        data={}
    )
    return response


def main():
    """Trigger a workflow for contacts."""
    parser = argparse.ArgumentParser(description="Trigger GHL Workflow")
    parser.add_argument("--workflow-id", required=True,
                        help="GHL workflow ID to trigger")
    parser.add_argument("--contact-id", default=None,
                        help="Single contact ID to add")
    parser.add_argument("--tag", default=None,
                        help="Add all contacts with this tag")
    parser.add_argument("--limit", type=int, default=50,
                        help="Max contacts when using --tag (default: 50)")
    parser.add_argument("--dry-run", action="store_true",
                        help="List contacts without triggering")
    args = parser.parse_args()

    # Validate: need either --contact-id or --tag
    if not args.contact_id and not args.tag:
        print("Error: Must specify either --contact-id or --tag", file=sys.stderr)
        sys.exit(1)

    # Initialize client
    client = GHLClient()

    # Build contact list
    contacts = []

    if args.contact_id:
        # Single contact mode
        contacts = [{"id": args.contact_id, "name": "(specified by ID)", "email": ""}]

    elif args.tag:
        # Tag search mode
        print(f"Searching for contacts with tag '{args.tag}'...")
        contacts = search_contacts_by_tag(client, args.tag, args.limit)

        if not contacts:
            print(f"No contacts found with tag '{args.tag}'")
            sys.exit(0)

    # Show what we found/will do
    print(f"\n📋 Contacts to add to workflow ({len(contacts)}):\n")
    for c in contacts:
        print(f"  - {c['name']} ({c['email']}) [ID: {c['id'][:8]}...]")

    print(f"\n🔄 Workflow: {args.workflow_id}")

    if args.dry_run:
        print("\n✋ DRY RUN - No contacts added to workflow.")
        print("Remove --dry-run to execute.")
        return

    # Confirm before triggering
    print(f"\n⚠️  This will add {len(contacts)} contact(s) to the workflow.")
    print("    GHL will start sending emails according to the workflow settings.")

    try:
        confirm = input("\n    Type 'yes' to proceed: ")
        if confirm.lower() != "yes":
            print("Cancelled.")
            return
    except EOFError:
        print("Error: Cannot proceed in non-interactive mode without confirmation.", file=sys.stderr)
        sys.exit(1)

    # Execute
    print("\nAdding contacts to workflow...")
    success = 0
    failed = 0

    for c in contacts:
        try:
            add_to_workflow(client, c["id"], args.workflow_id)
            print(f"  ✅ Added: {c['name']}")
            success += 1
        except Exception as e:
            print(f"  ❌ Failed: {c['name']} - {e}")
            failed += 1

    # Summary
    print(f"\n📊 Results: {success} added, {failed} failed")

    if success > 0:
        print("\n✅ Workflow triggered! GHL will process the email sends.")


if __name__ == "__main__":
    main()
