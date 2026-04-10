#!/usr/bin/env python3
"""
Schedule a Social Media Post
==============================
Create and schedule a post across one or more connected platforms.

Usage:
    # Dry run (preview only, no post created)
    python3 schedule_post.py --platform linkedin --text "Hello world" --dry-run

    # Schedule for a specific time
    python3 schedule_post.py --platform linkedin --text "Hello" --schedule "2026-03-10T09:00:00+11:00"

    # Post to multiple platforms
    python3 schedule_post.py --platform linkedin,facebook --text "Hello" --dry-run

    # With media
    python3 schedule_post.py --platform instagram --text "Caption" --media "https://cdn.example.com/image.jpg" --dry-run
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))
from ghl_social_client import GHLSocialClient


def resolve_account_ids(client: GHLSocialClient, platforms: list) -> list:
    """Resolve platform names to account IDs."""
    accounts = client.list_accounts()
    resolved = []
    missing = []

    for platform in platforms:
        found = False
        for acct in accounts:
            if acct.get("platform") == platform and not acct.get("deleted") and not acct.get("isExpired"):
                resolved.append({
                    "id": acct["id"],
                    "platform": platform,
                    "name": acct["name"],
                    "type": acct["type"]
                })
                found = True
                break
        if not found:
            missing.append(platform)

    if missing:
        print(f"Warning: No connected account for: {', '.join(missing)}", file=sys.stderr)
        print("Connect these in GHL > Marketing > Social Planner", file=sys.stderr)

    return resolved


def main():
    parser = argparse.ArgumentParser(description="Schedule a social media post")
    parser.add_argument("--platform", required=True,
                       help="Platform(s) to post to, comma-separated (facebook,instagram,linkedin,threads,youtube)")
    parser.add_argument("--text", required=True, help="Post text content")
    parser.add_argument("--schedule", help="Schedule time as ISO datetime (e.g., 2026-03-10T09:00:00+11:00)")
    parser.add_argument("--media", help="Comma-separated media URLs")
    parser.add_argument("--post-type", default="post", choices=["post", "story", "reel"],
                       help="Post type (default: post). Carousels use 'post' with multiple --media URLs.")
    parser.add_argument("--pdf-carousel", help="LinkedIn PDF carousel: path or URL to PDF file")
    parser.add_argument("--pdf-title", help="Title for LinkedIn PDF carousel")
    parser.add_argument("--tags", help="Comma-separated tags")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't create post")
    parser.add_argument("--json", action="store_true", help="Output raw JSON response")
    args = parser.parse_args()

    client = GHLSocialClient()
    platforms = [p.strip() for p in args.platform.split(",")]

    # Resolve platform names to account IDs
    resolved = resolve_account_ids(client, platforms)
    if not resolved:
        print("Error: No valid accounts found for specified platforms.", file=sys.stderr)
        sys.exit(1)

    account_ids = [r["id"] for r in resolved]
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None

    # Build media objects from URLs (GHL requires {url, type} objects)
    media = None
    if args.media:
        media = []
        for url in args.media.split(","):
            url = url.strip()
            # Infer mime type from extension
            if url.lower().endswith((".png",)):
                mime = "image/png"
            elif url.lower().endswith((".jpg", ".jpeg")):
                mime = "image/jpeg"
            elif url.lower().endswith((".gif",)):
                mime = "image/gif"
            elif url.lower().endswith((".mp4",)):
                mime = "video/mp4"
            elif url.lower().endswith((".webp",)):
                mime = "image/webp"
            else:
                mime = "image/png"  # default for GHL CDN URLs without extension
            media.append({"url": url, "type": mime})

    # Build platform-specific details
    platform_names = [r["platform"] for r in resolved]
    instagram_details = None
    facebook_details = None
    linkedin_details = None

    if "instagram" in platform_names:
        instagram_details = {"type": args.post_type}

    if "facebook" in platform_names:
        facebook_details = {"type": args.post_type}

    if "linkedin" in platform_names and args.pdf_carousel:
        linkedin_details = {"postAsPdf": True}
        if args.pdf_title:
            linkedin_details["pdfTitle"] = args.pdf_title

    # Preview
    print("=" * 60)
    print("POST PREVIEW")
    print("=" * 60)
    print(f"\nPlatforms:")
    for r in resolved:
        print(f"  - {r['platform']} ({r['name']}, {r['type']})")

    print(f"\nPost type: {args.post_type}")

    if media and len(media) > 1 and "instagram" in platform_names:
        print(f"  → Instagram carousel ({len(media)} images)")

    if args.schedule:
        print(f"\nScheduled for: {args.schedule}")
    else:
        print(f"\nWARNING: No schedule time — will publish IMMEDIATELY")

    if media:
        print(f"\nMedia ({len(media)}):")
        for m in media:
            print(f"  - {m['url']} ({m['type']})")

    if linkedin_details:
        print(f"\nLinkedIn PDF carousel: {args.pdf_carousel}")
        if args.pdf_title:
            print(f"  Title: {args.pdf_title}")

    if tags:
        print(f"\nTags: {', '.join(tags)}")

    print(f"\nContent ({len(args.text)} chars):")
    print("-" * 40)
    print(args.text[:500])
    if len(args.text) > 500:
        print(f"... ({len(args.text) - 500} more chars)")
    print("-" * 40)

    if args.dry_run:
        print("\n[DRY RUN] Post not created. Remove --dry-run to create.")
        return

    # Create the post
    result = client.create_post(
        account_ids=account_ids,
        summary=args.text,
        post_type=args.post_type,
        schedule_date=args.schedule,
        media=media,
        tags=tags,
        instagram_details=instagram_details,
        facebook_details=facebook_details,
        linkedin_details=linkedin_details,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\nPost created successfully!")
        if "results" in result:
            posts = result["results"]
            if isinstance(posts, list):
                for p in posts:
                    print(f"  ID: {p.get('id', 'n/a')}")
                    print(f"  Status: {p.get('status', 'n/a')}")
            elif isinstance(posts, dict):
                print(f"  ID: {posts.get('id', 'n/a')}")
                print(f"  Status: {posts.get('status', 'n/a')}")


if __name__ == "__main__":
    main()
