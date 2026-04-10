#!/usr/bin/env python3
"""
Search GHL Contacts
===================
Find contacts by tag, name, or email.

Usage:
    python3 search_contacts.py [options]

Options:
    --tag TAG          Search by tag (e.g., "ai-powerhouse")
    --query TEXT       Search by name or email
    --email EMAIL      Search by exact email
    --limit N          Maximum contacts (default: 50)
    --json             Output as JSON

Examples:
    python3 search_contacts.py --tag ai-powerhouse
    python3 search_contacts.py --query "john"
    python3 search_contacts.py --email "john@example.com"
"""

import argparse
import json
import sys
from pathlib import Path

# Import shared client
sys.path.insert(0, str(Path(__file__).parent))
from ghl_client import GHLClient


def search_contacts(client: GHLClient, tag: str = None, query: str = None,
                    email: str = None, limit: int = 50) -> list:
    """
    Search for contacts.

    Uses POST /contacts/search for tag filtering (server-side, reliable).
    Uses GET /contacts/ for query and email search (text-based).

    Args:
        client: GHLClient instance
        tag: Tag to filter by (uses Advanced Search endpoint)
        query: Name/email search query
        email: Exact email to find
        limit: Max results

    Returns:
        List of contact dicts
    """
    if tag:
        # Use POST /contacts/search with server-side tag filter
        filters = [{"field": "tags", "operator": "eq", "value": tag}]
        contacts = client.search_contacts_paginated(filters, max_items=limit)
    else:
        # Use GET /contacts/ for text-based search
        params = {
            "limit": min(limit, 100)
        }
        if email:
            params["query"] = email
        elif query:
            params["query"] = query

        contacts = client.paginate(
            "/contacts/",
            params=params,
            key="contacts",
            max_items=limit
        )

    return contacts


def format_contact(contact: dict) -> str:
    """
    Format a contact for display.

    Args:
        contact: Contact dict from API

    Returns:
        Formatted string
    """
    first = contact.get("firstName", "")
    last = contact.get("lastName", "")
    name = f"{first} {last}".strip() or "(no name)"

    email = contact.get("email", "(no email)")
    phone = contact.get("phone", "")
    contact_id = contact.get("id", "")

    # Get tags
    tags = contact.get("tags", [])
    tag_names = []
    for t in tags:
        if isinstance(t, str):
            tag_names.append(t)
        elif isinstance(t, dict):
            tag_names.append(t.get("name", ""))
    tags_str = ", ".join(tag_names[:5]) or "(no tags)"

    output = []
    output.append(f"  Name: {name}")
    output.append(f"  Email: {email}")
    if phone:
        output.append(f"  Phone: {phone}")
    output.append(f"  Tags: {tags_str}")
    output.append(f"  ID: {contact_id}")

    return "\n".join(output)


def main():
    """Search for contacts."""
    parser = argparse.ArgumentParser(description="Search GHL Contacts")
    parser.add_argument("--tag", default=None,
                        help="Filter by tag")
    parser.add_argument("--query", default=None,
                        help="Search by name or email")
    parser.add_argument("--email", default=None,
                        help="Search by exact email")
    parser.add_argument("--limit", type=int, default=50,
                        help="Maximum contacts (default: 50)")
    parser.add_argument("--json", action="store_true",
                        help="Output as JSON")
    args = parser.parse_args()

    # At least one search criteria required
    if not any([args.tag, args.query, args.email]):
        print("Error: Specify at least one of --tag, --query, or --email", file=sys.stderr)
        sys.exit(1)

    # Initialize client
    client = GHLClient()

    # Search
    contacts = search_contacts(
        client,
        tag=args.tag,
        query=args.query,
        email=args.email,
        limit=args.limit
    )

    if args.json:
        # Simplify for JSON output
        simplified = []
        for c in contacts:
            tags = c.get("tags", [])
            tag_names = []
            for t in tags:
                if isinstance(t, str):
                    tag_names.append(t)
                elif isinstance(t, dict):
                    tag_names.append(t.get("name", ""))

            simplified.append({
                "id": c.get("id"),
                "name": f"{c.get('firstName', '')} {c.get('lastName', '')}".strip(),
                "email": c.get("email"),
                "phone": c.get("phone"),
                "tags": tag_names
            })
        print(json.dumps(simplified, indent=2))
    else:
        # Formatted output
        search_desc = []
        if args.tag:
            search_desc.append(f"tag='{args.tag}'")
        if args.query:
            search_desc.append(f"query='{args.query}'")
        if args.email:
            search_desc.append(f"email='{args.email}'")

        print(f"\n👥 Contact Search ({', '.join(search_desc)})")
        print(f"   Found: {len(contacts)} contact(s)\n")

        if not contacts:
            print("No contacts found matching your criteria.")
            return

        for i, contact in enumerate(contacts, 1):
            print(f"[{i}]")
            print(format_contact(contact))
            print()


if __name__ == "__main__":
    main()
