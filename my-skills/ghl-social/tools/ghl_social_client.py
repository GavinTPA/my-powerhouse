#!/usr/bin/env python3
"""
GHL Social Planner API Client
==============================
Extends ghl_client patterns for the Social Planner API surface.

Handles:
- Social account discovery (connected platforms)
- Post creation and scheduling
- Post listing and management
- Statistics retrieval

Uses the same config file as ghl-connect (~/.config/ghl-connect.yaml).

Usage:
    from ghl_social_client import GHLSocialClient

    client = GHLSocialClient()
    accounts = client.list_accounts()
    client.create_post(account_ids=["..."], summary="Hello world")

Test:
    python3 ghl_social_client.py --test
    python3 ghl_social_client.py --accounts
"""

import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

import yaml
import requests

# Config file location (shared with ghl-connect)
CONFIG_PATH = Path.home() / ".config" / "ghl-connect.yaml"

# Rate limiting: 100 requests per 10 seconds
MIN_REQUEST_INTERVAL = 0.1


class GHLSocialClient:
    """GoHighLevel Social Planner API client."""

    def __init__(self):
        self.config = self._load_config()
        self.api_base = self.config.get("api_base", "https://services.leadconnectorhq.com")
        self.api_version = self.config.get("api_version", "2021-07-28")
        self.location_id = self.config.get("location_id", "")
        self.api_token = self.config.get("api_token", "")
        self._last_request_time = 0

    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        if not CONFIG_PATH.exists():
            print(f"Error: Config file not found at {CONFIG_PATH}", file=sys.stderr)
            print("Set up ghl-connect first.", file=sys.stderr)
            sys.exit(1)

        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)

        if not config.get("api_token") or config.get("api_token") == "YOUR_TOKEN_HERE":
            print("Error: api_token not configured.", file=sys.stderr)
            sys.exit(1)

        if not config.get("location_id") or config.get("location_id") == "YOUR_LOCATION_ID":
            print("Error: location_id not configured.", file=sys.stderr)
            sys.exit(1)

        return config

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.time()

    def _headers(self) -> dict:
        """Standard headers for GHL API requests."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Version": self.api_version,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _social_base(self) -> str:
        """Base path for social planner endpoints."""
        return f"/social-media-posting/{self.location_id}"

    def _request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> dict:
        """Make an API request with error handling."""
        self._rate_limit()

        url = f"{self.api_base}{self._social_base()}{endpoint}"

        response = requests.request(
            method, url,
            headers=self._headers(),
            json=data,
            params=params
        )

        if response.status_code == 401:
            print("Error: Authentication failed. Check your API token.", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 429:
            print("Error: Rate limited. Wait and try again.", file=sys.stderr)
            sys.exit(1)

        if response.status_code not in (200, 201):
            print(f"Error: API returned {response.status_code}", file=sys.stderr)
            print(f"Response: {response.text[:500]}", file=sys.stderr)
            sys.exit(1)

        return response.json()

    # ── Account Operations ──────────────────────────────────────────

    def list_accounts(self) -> list:
        """List all connected social media accounts."""
        result = self._request("GET", "/accounts")
        return result.get("results", {}).get("accounts", [])

    def list_groups(self) -> list:
        """List all connected social media groups."""
        result = self._request("GET", "/accounts")
        return result.get("results", {}).get("groups", [])

    def get_accounts_by_platform(self) -> dict:
        """Get connected accounts organized by platform."""
        accounts = self.list_accounts()
        by_platform = {}
        for acct in accounts:
            platform = acct.get("platform", "unknown")
            if platform not in by_platform:
                by_platform[platform] = []
            by_platform[platform].append(acct)
        return by_platform

    # ── Post Operations ─────────────────────────────────────────────

    def list_posts(self, filters: dict = None) -> list:
        """
        List posts. Uses POST /posts/list (GET /posts does not exist).

        Args:
            filters: Optional filter dict (e.g., {"type": "scheduled"})

        Returns:
            List of post dicts
        """
        body = filters or {}
        result = self._request("POST", "/posts/list", data=body)
        return result.get("results", {}).get("posts", [])

    def get_post(self, post_id: str) -> dict:
        """Get a single post by ID."""
        result = self._request("GET", f"/posts/{post_id}")
        return result.get("results", {})

    def create_post(
        self,
        account_ids: list,
        summary: str,
        post_type: str = "post",
        schedule_date: str = None,
        media: list = None,
        tags: list = None,
        instagram_details: dict = None,
        facebook_details: dict = None,
        linkedin_details: dict = None,
        youtube_details: dict = None,
    ) -> dict:
        """
        Create (and optionally schedule) a social media post.

        Args:
            account_ids: List of connected account IDs to post to
            summary: Post text content
            post_type: "post", "story", or "reel"
            schedule_date: ISO datetime for scheduling (None = publish immediately)
            media: List of media dicts [{"url": "...", "type": "image/png"}]
            tags: Optional tags for organization
            instagram_details: Optional Instagram-specific settings
                e.g. {"type": "post", "collaborators": [...], "showOnFeed": true}
            facebook_details: Optional Facebook-specific settings
                e.g. {"type": "post"}
            linkedin_details: Optional LinkedIn-specific settings
                e.g. {"postAsPdf": true, "pdfTitle": "My Carousel"}
            youtube_details: Optional YouTube-specific settings
                e.g. {"type": "video", "title": "...", "privacyLevel": "public"}

        Returns:
            API response with created post info
        """
        data = {
            "accountIds": account_ids,
            "summary": summary,
            "type": post_type,
            "media": media or [],
            "userId": self.location_id,
        }

        if schedule_date:
            data["scheduleDate"] = schedule_date
            data["status"] = "scheduled"

        if tags:
            data["tags"] = tags

        if instagram_details:
            data["instagramPostDetails"] = instagram_details
        if facebook_details:
            data["facebookPostDetails"] = facebook_details
        if linkedin_details:
            data["linkedinPostDetails"] = linkedin_details
        if youtube_details:
            data["youtubePostDetails"] = youtube_details

        return self._request("POST", "/posts", data=data)

    def update_post(self, post_id: str, data: dict) -> dict:
        """Update an existing post."""
        return self._request("PUT", f"/posts/{post_id}", data=data)

    def delete_post(self, post_id: str) -> dict:
        """Delete a post."""
        return self._request("DELETE", f"/posts/{post_id}")

    # ── Tags & Categories ───────────────────────────────────────────

    def list_tags(self) -> list:
        """List social planner tags."""
        result = self._request("GET", "/tags")
        tags = result.get("results", {}).get("tags", [])
        return tags if isinstance(tags, list) else []

    def list_categories(self) -> list:
        """List social planner categories."""
        result = self._request("GET", "/categories")
        return result.get("results", {}).get("categories", [])

    # ── Statistics ──────────────────────────────────────────────────

    def get_statistics(self, params: dict = None) -> dict:
        """Get post performance statistics."""
        return self._request("GET", "/statistics", params=params)

    # ── Convenience Methods ─────────────────────────────────────────

    def get_account_id(self, platform: str) -> str:
        """Get the first account ID for a given platform."""
        accounts = self.list_accounts()
        for acct in accounts:
            if acct.get("platform") == platform and not acct.get("deleted"):
                return acct["id"]
        return None

    def test_connection(self) -> dict:
        """Test the Social Planner API connection."""
        try:
            accounts = self.list_accounts()
            platforms = list(set(a.get("platform") for a in accounts))
            return {
                "status": "ok",
                "location_id": self.location_id,
                "connected_accounts": len(accounts),
                "platforms": platforms
            }
        except SystemExit:
            return {"status": "error", "message": "Authentication or API error"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


def main():
    parser = argparse.ArgumentParser(description="GHL Social Planner Client")
    parser.add_argument("--test", action="store_true", help="Test API connection")
    parser.add_argument("--accounts", action="store_true", help="List connected accounts")
    parser.add_argument("--posts", action="store_true", help="List posts")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    client = GHLSocialClient()

    if args.test:
        result = client.test_connection()
        if result["status"] == "ok":
            print(f"Connection successful!")
            print(f"  Location: {result['location_id']}")
            print(f"  Accounts: {result['connected_accounts']}")
            print(f"  Platforms: {', '.join(result['platforms'])}")
        else:
            print(f"Connection failed: {result.get('message')}")
            sys.exit(1)

    elif args.accounts:
        accounts = client.list_accounts()
        if args.json:
            print(json.dumps(accounts, indent=2))
        else:
            if not accounts:
                print("No social accounts connected.")
                print("Connect accounts in GHL > Marketing > Social Planner")
                return
            print(f"Connected accounts ({len(accounts)}):\n")
            for acct in accounts:
                expired = " [EXPIRED]" if acct.get("isExpired") else ""
                stats = " [stats]" if acct.get("hasStatisticsPermissions") else ""
                print(f"  {acct['platform']:12s} {acct['name']:30s} ({acct['type']}){expired}{stats}")
                print(f"  {'':12s} ID: {acct['id']}")
                if acct.get("expire"):
                    print(f"  {'':12s} Expires: {acct['expire'][:10]}")
                print()

    elif args.posts:
        posts = client.list_posts()
        if args.json:
            print(json.dumps(posts, indent=2))
        else:
            if not posts:
                print("No posts found.")
                return
            for post in posts:
                print(f"  [{post.get('status', '?')}] {post.get('summary', '')[:80]}")
                print(f"  ID: {post.get('id')}")
                print()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
