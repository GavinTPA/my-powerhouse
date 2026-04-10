#!/usr/bin/env python3
"""
Create or Update GHL Contacts
==============================
Create new contacts or update existing ones with tags and company info.

Checks for existing contacts by email first to avoid duplicates.

Usage:
    python3 create_contact.py --first-name "David" --last-name "Watts" \
        --email "ppm@workshopwhisperer.com" --company "The Workshop Whisperer" \
        --tags "aipowerhouseVIPteam"

    python3 create_contact.py --batch contacts.json --dry-run

Batch JSON format:
    [
      {"firstName": "David", "lastName": "Watts", "email": "d@example.com",
       "companyName": "Acme", "tags": ["tag1", "tag2"]}
    ]
"""

import argparse
import json
import sys
from pathlib import Path

# Import shared client
sys.path.insert(0, str(Path(__file__).parent))
from ghl_client import GHLClient


def find_contact_by_email(client: GHLClient, email: str) -> dict | None:
    """Search for an existing contact by email. Returns contact dict or None."""
    contacts = client.paginate(
        "/contacts/",
        params={"limit": 1, "query": email},
        key="contacts",
        max_items=5
    )
    # Verify exact email match (query is fuzzy)
    for c in contacts:
        if c.get("email", "").lower() == email.lower():
            return c
    return None


def create_contact(client: GHLClient, first_name: str, last_name: str,
                   email: str, company: str = None, tags: list = None,
                   dry_run: bool = False) -> dict:
    """
    Create or update a single contact.

    Returns dict with: action (created/updated/skipped), contact_id, details
    """
    result = {"email": email, "name": f"{first_name} {last_name}"}

    # Step 1: Check if contact already exists
    existing = find_contact_by_email(client, email)

    if existing:
        contact_id = existing["id"]
        result["contact_id"] = contact_id
        result["action"] = "updated"
        result["details"] = []

        if dry_run:
            result["action"] = "would_update"
            if tags:
                result["details"].append(f"Would add tags: {tags}")
            if company:
                result["details"].append(f"Would set company: {company}")
            return result

        # Update company if provided and different
        if company:
            existing_company = existing.get("companyName", "")
            if existing_company != company:
                client.put(f"/contacts/{contact_id}", data={
                    "companyName": company
                })
                result["details"].append(f"Updated company: {company}")

        # Add tags if provided
        if tags:
            client.post(f"/contacts/{contact_id}/tags", data={
                "tags": tags
            })
            result["details"].append(f"Added tags: {tags}")

        if not result["details"]:
            result["action"] = "skipped"
            result["details"].append("Already exists with correct data")

        return result

    # Step 2: Create new contact
    if dry_run:
        result["action"] = "would_create"
        result["details"] = [f"New contact: {first_name} {last_name} <{email}>"]
        if company:
            result["details"].append(f"Company: {company}")
        if tags:
            result["details"].append(f"Tags: {tags}")
        return result

    payload = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "locationId": client.location_id,
    }
    if company:
        payload["companyName"] = company

    response = client.post("/contacts/", data=payload)
    contact = response.get("contact", response)
    contact_id = contact.get("id")

    result["contact_id"] = contact_id
    result["action"] = "created"
    result["details"] = [f"Created: {first_name} {last_name} <{email}>"]

    # Add tags after creation
    if tags and contact_id:
        client.post(f"/contacts/{contact_id}/tags", data={
            "tags": tags
        })
        result["details"].append(f"Added tags: {tags}")

    return result


def add_tags_to_contact(client: GHLClient, email: str, tags: list,
                        dry_run: bool = False) -> dict:
    """
    Add tags to an existing contact found by email.

    Returns dict with: action, contact_id, details
    """
    result = {"email": email}

    existing = find_contact_by_email(client, email)

    if not existing:
        print(f"Error: No contact found with email '{email}'", file=sys.stderr)
        sys.exit(1)

    contact_id = existing["id"]
    contact_name = f"{existing.get('firstName', '')} {existing.get('lastName', '')}".strip()
    result["name"] = contact_name
    result["contact_id"] = contact_id

    if dry_run:
        result["action"] = "would_add_tags"
        result["details"] = [f"Would add tags to {contact_name}: {tags}"]
        return result

    client.post(f"/contacts/{contact_id}/tags", data={
        "tags": tags
    })
    result["action"] = "tags_added"
    result["details"] = [f"Added tags to {contact_name}: {tags}"]
    return result


def main():
    parser = argparse.ArgumentParser(description="Create or Update GHL Contacts")

    # Mode group: mutually exclusive modes
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--add-tags", action="store_true",
                            help="Add tags to an existing contact (requires --email and --tags only)")
    mode_group.add_argument("--batch", help="Path to JSON file with contact list")

    parser.add_argument("--first-name", help="First name")
    parser.add_argument("--last-name", help="Last name")
    parser.add_argument("--email", help="Email address")
    parser.add_argument("--company", help="Company name")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without making changes")
    args = parser.parse_args()

    # Validate args
    if args.add_tags:
        if not args.email:
            parser.error("--add-tags requires --email")
        if not args.tags:
            parser.error("--add-tags requires --tags")
    elif args.batch:
        batch_path = Path(args.batch)
        if not batch_path.exists():
            print(f"Error: Batch file not found: {args.batch}", file=sys.stderr)
            sys.exit(1)
    elif args.first_name and args.last_name and args.email:
        pass  # Valid create/update mode
    else:
        print("Error: Provide --first-name, --last-name, --email OR --batch OR --add-tags",
              file=sys.stderr)
        sys.exit(1)

    client = GHLClient()

    # Handle --add-tags mode
    if args.add_tags:
        tags = [t.strip() for t in args.tags.split(",")]
        mode = "DRY RUN" if args.dry_run else "LIVE"
        print(f"\n{'=' * 60}")
        print(f"  Add Tags [{mode}]")
        print(f"{'=' * 60}\n")

        result = add_tags_to_contact(client, args.email, tags, dry_run=args.dry_run)

        icon = "+" if "would" not in result["action"] else "~"
        print(f"  [{icon}] {result.get('name', args.email)} <{result['email']}>")
        for detail in result.get("details", []):
            print(f"      {detail}")

        print(f"\n{'=' * 60}")
        if args.dry_run:
            print(f"  Preview complete. Remove --dry-run to execute.")
        else:
            print(f"  Done: tags added successfully")
        print(f"{'=' * 60}\n")
        return

    # Build contacts list for create/update mode
    if args.batch:
        with open(Path(args.batch)) as f:
            contacts_list = json.load(f)
    else:
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        contacts_list = [{
            "firstName": args.first_name,
            "lastName": args.last_name,
            "email": args.email,
            "companyName": args.company,
            "tags": tags
        }]

    # Preview
    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"\n{'=' * 60}")
    print(f"  Contact {'Preview' if args.dry_run else 'Creation'} — {len(contacts_list)} contact(s) [{mode}]")
    print(f"{'=' * 60}\n")

    results = []
    for contact_data in contacts_list:
        first = contact_data.get("firstName", "")
        last = contact_data.get("lastName", "")
        email = contact_data.get("email", "")
        company = contact_data.get("companyName")
        tags = contact_data.get("tags", [])

        if not email:
            print(f"  Skipping {first} {last} — no email provided")
            continue

        result = create_contact(
            client, first, last, email,
            company=company, tags=tags,
            dry_run=args.dry_run
        )
        results.append(result)

        # Display result
        icon = {"created": "+", "updated": "~", "skipped": "=",
                "would_create": "+", "would_update": "~"}.get(result["action"], "?")
        print(f"  [{icon}] {result['name']} <{result['email']}>")
        print(f"      Action: {result['action']}")
        for detail in result.get("details", []):
            print(f"      {detail}")
        print()

    # Summary
    print(f"{'=' * 60}")
    actions = [r["action"] for r in results]
    if args.dry_run:
        print(f"  Preview complete. Remove --dry-run to execute.")
    else:
        created = actions.count("created")
        updated = actions.count("updated")
        skipped = actions.count("skipped")
        print(f"  Done: {created} created, {updated} updated, {skipped} skipped")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
