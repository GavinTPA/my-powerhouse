#!/usr/bin/env python3
"""
GHL API Client
==============
Shared API client for GoHighLevel Conversations API.

Handles:
- Configuration loading from ~/.config/ghl-connect.yaml
- Authentication headers
- Rate limiting (100 req / 10 seconds)
- Pagination helpers (cursor-based)
- Error handling

Usage:
    from ghl_client import GHLClient

    client = GHLClient()
    response = client.get("/conversations/search", params={...})

Test auth:
    python3 ghl_client.py --test
"""

import sys
import time
import argparse
from pathlib import Path

import yaml
import requests

# Config file location
CONFIG_PATH = Path.home() / ".config" / "ghl-connect.yaml"

# Rate limiting: 100 requests per 10 seconds = 0.1s between calls
MIN_REQUEST_INTERVAL = 0.1


class GHLClient:
    """GoHighLevel API client with auth, rate limiting, and pagination."""

    def __init__(self):
        self.config = self._load_config()
        self.api_base = self.config.get("api_base", "https://services.leadconnectorhq.com")
        self.api_version = self.config.get("api_version", "2021-07-28")
        self.location_id = self.config.get("location_id", "")
        self.api_token = self.config.get("api_token", "")
        self.test_email = self.config.get("test_email", "")
        self.max_sends = self.config.get("max_sends_per_session", 10)
        self.sends_this_session = 0
        self._last_request_time = 0

    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        if not CONFIG_PATH.exists():
            print(f"Error: Config file not found at {CONFIG_PATH}", file=sys.stderr)
            print("Run scripts/setup.sh first to create the template.", file=sys.stderr)
            sys.exit(1)

        with open(CONFIG_PATH) as f:
            config = yaml.safe_load(f)

        # Validate required fields
        if not config.get("api_token") or config.get("api_token") == "YOUR_TOKEN_HERE":
            print("Error: api_token not configured in config file.", file=sys.stderr)
            print(f"Edit {CONFIG_PATH} and add your Private Integration Token.", file=sys.stderr)
            sys.exit(1)

        if not config.get("location_id") or config.get("location_id") == "YOUR_LOCATION_ID":
            print("Error: location_id not configured in config file.", file=sys.stderr)
            print(f"Edit {CONFIG_PATH} and add your Location ID.", file=sys.stderr)
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

    def get(self, endpoint: str, params: dict = None) -> dict:
        """
        Make a GET request to the GHL API.

        Args:
            endpoint: API path (e.g., "/conversations/search")
            params: Query parameters

        Returns:
            JSON response as dict
        """
        self._rate_limit()

        url = f"{self.api_base}{endpoint}"

        # Add locationId to params if not present
        if params is None:
            params = {}
        if "locationId" not in params:
            params["locationId"] = self.location_id

        response = requests.get(url, headers=self._headers(), params=params)

        if response.status_code == 401:
            print("Error: Authentication failed. Check your API token.", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 429:
            print("Error: Rate limited. Wait and try again.", file=sys.stderr)
            sys.exit(1)

        if response.status_code != 200:
            print(f"Error: API returned {response.status_code}", file=sys.stderr)
            print(f"Response: {response.text[:500]}", file=sys.stderr)
            sys.exit(1)

        return response.json()

    def post(self, endpoint: str, data: dict = None) -> dict:
        """
        Make a POST request to the GHL API.

        Args:
            endpoint: API path (e.g., "/conversations/messages")
            data: JSON body

        Returns:
            JSON response as dict
        """
        self._rate_limit()

        url = f"{self.api_base}{endpoint}"

        response = requests.post(url, headers=self._headers(), json=data)

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

    def post_multipart(self, endpoint: str, files: dict, data: dict = None) -> requests.Response:
        """
        Make a POST request with multipart/form-data (for file uploads).

        Unlike post(), this does NOT set Content-Type header — lets requests
        set it automatically with the multipart boundary.

        Args:
            endpoint: API path (e.g., "/medias/upload-file")
            files: Files dict for requests (e.g., {"file": (name, bytes, mime)})
            data: Form data fields (e.g., {"hosted": "false"})

        Returns:
            Raw requests.Response (caller handles parsing — response schema
            varies and isn't fully documented by GHL)
        """
        self._rate_limit()

        url = f"{self.api_base}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Version": self.api_version,
            # NO Content-Type — requests sets it for multipart with boundary
        }

        response = requests.post(url, headers=headers, files=files, data=data)

        if response.status_code == 401:
            print("Error: Authentication failed. Check your API token.", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 403:
            print("Error: Forbidden. Your Private Integration token may need Media scope enabled.", file=sys.stderr)
            print("Fix: GHL Settings > Integrations > Private Integrations > Edit > Enable Media", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 429:
            print("Error: Rate limited. Wait and try again.", file=sys.stderr)
            sys.exit(1)

        return response

    def put(self, endpoint: str, data: dict = None) -> dict:
        """
        Make a PUT request to the GHL API.

        Args:
            endpoint: API path (e.g., "/contacts/{id}")
            data: JSON body

        Returns:
            JSON response as dict
        """
        self._rate_limit()

        url = f"{self.api_base}{endpoint}"

        response = requests.put(url, headers=self._headers(), json=data)

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

    def paginate(self, endpoint: str, params: dict = None, key: str = None, max_items: int = 1000) -> list:
        """
        Paginate through results using cursor-based pagination.

        GHL uses startAfterId for pagination - pass the last item's ID.

        Args:
            endpoint: API path
            params: Query parameters
            key: Key in response containing items (auto-detected if None)
            max_items: Maximum items to fetch

        Returns:
            List of all items
        """
        if params is None:
            params = {}

        all_items = []

        while len(all_items) < max_items:
            response = self.get(endpoint, params)

            # Auto-detect the items key if not specified
            if key is None:
                # Common keys in GHL responses
                for k in ["conversations", "contacts", "messages"]:
                    if k in response:
                        key = k
                        break
                if key is None:
                    # Return the whole response if no known key found
                    return [response]

            items = response.get(key, [])
            if not items:
                break

            all_items.extend(items)

            # Check for more pages
            meta = response.get("meta", {})
            next_page = meta.get("nextPageUrl") or meta.get("startAfterId")

            if not next_page:
                # Try using last item's ID
                if items and "id" in items[-1]:
                    params["startAfterId"] = items[-1]["id"]
                else:
                    break
            elif isinstance(next_page, str) and next_page.startswith("http"):
                # Full URL provided - parse out the startAfterId
                import urllib.parse
                parsed = urllib.parse.urlparse(next_page)
                query_params = urllib.parse.parse_qs(parsed.query)
                if "startAfterId" in query_params:
                    params["startAfterId"] = query_params["startAfterId"][0]
                else:
                    break
            else:
                params["startAfterId"] = next_page

            # Safety: if we got fewer items than limit, we're done
            limit = params.get("limit", 20)
            if len(items) < limit:
                break

        return all_items[:max_items]

    def search_contacts(self, filters: list, page: int = 1, page_limit: int = 100) -> dict:
        """
        Search contacts using POST /contacts/search (Advanced Search).

        Supports server-side filtering by tags, custom fields, etc.
        See: https://doc.clickup.com/8631005/d/h/87cpx-158396/6e629989abe7fad

        Args:
            filters: List of filter dicts, e.g. [{"field": "tags", "operator": "eq", "value": "my-tag"}]
            page: Page number (1-based)
            page_limit: Results per page (max 500)

        Returns:
            JSON response with "contacts" list and "total" count
        """
        data = {
            "locationId": self.location_id,
            "page": page,
            "pageLimit": min(page_limit, 500),
            "filters": filters
        }
        return self.post("/contacts/search", data=data)

    def search_contacts_paginated(self, filters: list, max_items: int = 500) -> list:
        """
        Paginate through POST /contacts/search results.

        Uses page-based pagination (different from GET /contacts/ which uses startAfterId).

        Args:
            filters: List of filter dicts
            max_items: Maximum contacts to return

        Returns:
            List of contact dicts
        """
        all_contacts = []
        page = 1
        page_limit = 100

        while len(all_contacts) < max_items:
            result = self.search_contacts(filters, page=page, page_limit=page_limit)
            contacts = result.get("contacts", [])
            if not contacts:
                break
            all_contacts.extend(contacts)
            total = result.get("total", 0)
            if len(all_contacts) >= total:
                break
            page += 1

        return all_contacts[:max_items]

    def check_send_limit(self) -> bool:
        """
        Check if we can send another message this session.

        Returns:
            True if under limit, False if at limit
        """
        return self.sends_this_session < self.max_sends

    def increment_send_count(self):
        """Increment the session send counter."""
        self.sends_this_session += 1

    def test_connection(self) -> dict:
        """
        Test the API connection by fetching location info.

        Returns:
            Location info dict or error
        """
        try:
            # Try to get conversations (minimal call)
            result = self.get("/conversations/search", params={"limit": 1})
            return {
                "status": "ok",
                "location_id": self.location_id,
                "conversations_accessible": True,
                "sample_count": len(result.get("conversations", []))
            }
        except SystemExit:
            return {"status": "error", "message": "Authentication or API error"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


def main():
    """Test the GHL API connection."""
    parser = argparse.ArgumentParser(description="GHL API Client")
    parser.add_argument("--test", action="store_true", help="Test API connection")
    args = parser.parse_args()

    if args.test:
        print("Testing GHL API connection...")
        client = GHLClient()
        result = client.test_connection()

        if result.get("status") == "ok":
            print(f"Connection successful!")
            print(f"  Location ID: {result['location_id']}")
            print(f"  Conversations API: accessible")
        else:
            print(f"Connection failed: {result.get('message', 'Unknown error')}")
            sys.exit(1)
    else:
        print("Usage: python3 ghl_client.py --test")
        print("Or import GHLClient in other scripts.")


if __name__ == "__main__":
    main()
