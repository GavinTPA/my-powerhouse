#!/usr/bin/env python3
"""
Zoom API Client
===============
Shared API client for Zoom REST API via Server-to-Server OAuth.

Handles:
- Configuration loading from ~/.config/zoom-connect.yaml
- S2S OAuth token acquisition (fresh token each run)
- Rate limiting (0.05s between calls, well under 40 req/sec)
- Error handling with clear messages
- Pagination helpers

Usage:
    from zoom_client import ZoomClient

    client = ZoomClient()                    # default profile
    client = ZoomClient(profile="main")       # named profile
    response = client.get("/v2/users/me/meetings", params={...})

Test auth:
    python3 zoom_client.py --test
    python3 zoom_client.py --test --profile main
"""

import sys
import time
import argparse
import base64
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml
import requests

# Config file location
CONFIG_PATH = Path.home() / ".config" / "zoom-connect.yaml"

# Rate limiting: well under Zoom's 40 req/sec limit
MIN_REQUEST_INTERVAL = 0.05

# Zoom API base
API_BASE = "https://api.zoom.us"
TOKEN_URL = "https://zoom.us/oauth/token"


class ZoomClient:
    """Zoom API client with S2S OAuth auth, rate limiting, and pagination."""

    def __init__(self, profile: str = None):
        self.config, self.profile_name = self._load_config(profile)
        self.account_id = self.config["account_id"]
        self.client_id = self.config["client_id"]
        self.client_secret = self.config["client_secret"]
        self.user_email = self.config.get("user_email", "me")
        self.download_dir = Path(self.config.get("download_dir", str(Path.home() / "Downloads" / "zoom-recordings"))).expanduser()
        self.timezone = self.config.get("timezone", "UTC")
        self._access_token = None
        self._token_expires = 0
        self._token_scopes = ""
        self._last_request_time = 0

    def _load_config(self, profile: str = None) -> tuple:
        """
        Load configuration from YAML file.

        Supports two formats:
        1. Multi-profile: { default_profile: "name", profiles: { name: {...}, ... } }
        2. Legacy flat: { account_id: "...", client_id: "...", ... }

        Returns:
            Tuple of (config_dict, profile_name)
        """
        if not CONFIG_PATH.exists():
            print(f"Error: Config file not found at {CONFIG_PATH}", file=sys.stderr)
            print("Run scripts/setup.sh first to create the template.", file=sys.stderr)
            sys.exit(1)

        with open(CONFIG_PATH) as f:
            raw_config = yaml.safe_load(f)

        # Detect config format
        if "profiles" in raw_config:
            # Multi-profile config
            profile_name = profile or raw_config.get("default_profile")

            if not profile_name:
                print("Error: No profile specified and no default_profile set in config", file=sys.stderr)
                sys.exit(1)

            if profile_name not in raw_config["profiles"]:
                available = ", ".join(raw_config["profiles"].keys())
                print(f"Error: Profile '{profile_name}' not found in config", file=sys.stderr)
                print(f"Available profiles: {available}", file=sys.stderr)
                sys.exit(1)

            config = raw_config["profiles"][profile_name]
        else:
            # Legacy flat config — ignore profile arg
            config = raw_config
            profile_name = None

        # Validate required fields
        required = ["account_id", "client_id", "client_secret"]
        placeholders = ["YOUR_ACCOUNT_ID", "YOUR_CLIENT_ID", "YOUR_CLIENT_SECRET"]

        for field in required:
            val = config.get(field, "")
            if not val or val in placeholders:
                label = f" (profile: {profile_name})" if profile_name else ""
                print(f"Error: {field} not configured in {CONFIG_PATH}{label}", file=sys.stderr)
                print("Add your S2S OAuth credentials from marketplace.zoom.us", file=sys.stderr)
                sys.exit(1)

        return config, profile_name

    def _get_token(self) -> str:
        """
        Get a valid S2S OAuth access token.

        Tokens expire after 1 hour. We request a fresh one if expired.
        """
        now = time.time()
        if self._access_token and now < self._token_expires:
            return self._access_token

        # Base64 encode client_id:client_secret
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()

        response = requests.post(
            TOKEN_URL,
            headers={
                "Authorization": f"Basic {encoded}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "account_credentials",
                "account_id": self.account_id
            }
        )

        if response.status_code != 200:
            print(f"Error: OAuth token request failed ({response.status_code})", file=sys.stderr)
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            if "reason" in error_data:
                print(f"Reason: {error_data['reason']}", file=sys.stderr)
            elif "error" in error_data:
                print(f"Error: {error_data['error']}: {error_data.get('error_description', '')}", file=sys.stderr)
            else:
                print(f"Response: {response.text[:500]}", file=sys.stderr)
            sys.exit(1)

        data = response.json()
        self._access_token = data["access_token"]
        self._token_scopes = data.get("scope", "")
        # Expire 5 minutes early to avoid edge cases
        self._token_expires = now + data.get("expires_in", 3600) - 300

        return self._access_token

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = time.time()

    def _headers(self) -> dict:
        """Standard headers for Zoom API requests."""
        return {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def get(self, endpoint: str, params: dict = None) -> dict:
        """
        Make a GET request to the Zoom API.

        Args:
            endpoint: API path (e.g., "/v2/users/me/meetings")
            params: Query parameters

        Returns:
            JSON response as dict
        """
        self._rate_limit()

        url = f"{API_BASE}{endpoint}"
        response = requests.get(url, headers=self._headers(), params=params)

        if response.status_code == 401:
            # Token may have expired mid-session — retry once
            self._access_token = None
            self._token_expires = 0
            response = requests.get(url, headers=self._headers(), params=params)

        if response.status_code == 401:
            print("Error: Authentication failed. Check your S2S OAuth credentials.", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 404:
            print(f"Error: Resource not found at {endpoint}", file=sys.stderr)
            print("Check meeting ID and ensure meeting has ended.", file=sys.stderr)
            sys.exit(1)

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After", "60")
            print(f"Error: Rate limited. Retry after {retry_after} seconds.", file=sys.stderr)
            sys.exit(1)

        if response.status_code != 200:
            print(f"Error: API returned {response.status_code}", file=sys.stderr)
            print(f"Response: {response.text[:500]}", file=sys.stderr)
            sys.exit(1)

        return response.json()

    def download(self, url: str, dest_path: Path) -> Path:
        """
        Download a file from a Zoom download URL.

        Zoom download URLs require the access token as a query parameter.

        Args:
            url: The download_url from a recording file
            dest_path: Where to save the file

        Returns:
            Path to the downloaded file
        """
        self._rate_limit()

        # Zoom download URLs need token as query param
        separator = "&" if "?" in url else "?"
        auth_url = f"{url}{separator}access_token={self._get_token()}"

        response = requests.get(auth_url, stream=True)

        if response.status_code != 200:
            print(f"Error: Download failed ({response.status_code})", file=sys.stderr)
            print(f"URL: {url[:100]}...", file=sys.stderr)
            sys.exit(1)

        dest_path.parent.mkdir(parents=True, exist_ok=True)

        with open(dest_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return dest_path

    def paginate(self, endpoint: str, params: dict = None, key: str = None, max_items: int = 500) -> list:
        """
        Paginate through results using Zoom's next_page_token pagination.

        Args:
            endpoint: API path
            params: Query parameters
            key: Key in response containing items
            max_items: Maximum items to fetch

        Returns:
            List of all items
        """
        if params is None:
            params = {}

        all_items = []

        while len(all_items) < max_items:
            response = self.get(endpoint, params)

            # Auto-detect the items key
            if key is None:
                for k in ["meetings", "participants", "recording_files", "recordings", "users"]:
                    if k in response:
                        key = k
                        break
                if key is None:
                    return [response]

            items = response.get(key, [])
            all_items.extend(items)

            # Zoom uses next_page_token for pagination
            next_token = response.get("next_page_token", "")
            if not next_token:
                break

            params["next_page_token"] = next_token

        return all_items[:max_items]

    @staticmethod
    def encode_uuid(uuid_str: str) -> str:
        """Encode UUID for Zoom API path segments.

        Zoom requires double-encoding only if the UUID starts with '/' or
        contains '//'.  All other UUIDs with '/' get single-encoded.
        UUIDs without '/' are returned as-is.

        See: https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/
        """
        if uuid_str.startswith('/') or '//' in uuid_str:
            return requests.utils.quote(requests.utils.quote(uuid_str, safe=''), safe='')
        if '/' in uuid_str:
            return requests.utils.quote(uuid_str, safe='')
        return uuid_str

    def test_connection(self) -> dict:
        """
        Test the API connection by fetching current user info.

        Returns:
            User info dict or error
        """
        try:
            result = self.get("/v2/users/me")
            return {
                "status": "ok",
                "profile": self.profile_name,
                "email": result.get("email", ""),
                "display_name": f"{result.get('first_name', '')} {result.get('last_name', '')}".strip(),
                "plan": result.get("type", 0),
                "account_id": result.get("account_id", "")
            }
        except SystemExit:
            return {"status": "error", "message": "Authentication or API error"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_scopes(self) -> list:
        """Return the list of scopes granted to this app's token."""
        self._get_token()
        return sorted(self._token_scopes.split()) if self._token_scopes else []

    def format_time(self, iso_string: str, fmt: str = "%Y-%m-%d %H:%M %Z") -> str:
        """
        Convert a Zoom UTC timestamp to the profile's local timezone for display.

        Args:
            iso_string: ISO 8601 timestamp from Zoom API (e.g., "2026-02-16T19:58:00Z")
            fmt: strftime format string (default includes timezone abbreviation)

        Returns:
            Formatted local time string, or the raw input if parsing fails
        """
        if not iso_string:
            return ""
        try:
            dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
            local_dt = dt.astimezone(ZoneInfo(self.timezone))
            return local_dt.strftime(fmt)
        except (ValueError, AttributeError, KeyError):
            return iso_string


# Plan type labels
PLAN_TYPES = {
    1: "Basic (Free)",
    2: "Licensed (Pro)",
    3: "On-Prem",
    99: "None"
}


def main():
    """Test the Zoom API connection."""
    parser = argparse.ArgumentParser(description="Zoom API Client")
    parser.add_argument("--test", action="store_true", help="Test API connection")
    parser.add_argument("--scopes", action="store_true", help="List all scopes on this app")
    parser.add_argument("--profile", default=None,
                        help="Profile name from config (e.g., main)")
    args = parser.parse_args()

    if args.scopes:
        client = ZoomClient(profile=args.profile)
        scopes = client.get_scopes()
        label = f" (profile: {client.profile_name})" if client.profile_name else ""
        print(f"Scopes{label}: {len(scopes)} total\n")
        for scope in scopes:
            print(f"  {scope}")
    elif args.test:
        print("Testing Zoom API connection...")
        client = ZoomClient(profile=args.profile)
        result = client.test_connection()

        if result.get("status") == "ok":
            plan_label = PLAN_TYPES.get(result.get("plan", 0), f"Type {result['plan']}")
            scopes = client.get_scopes()
            print("Connection successful!")
            if result.get("profile"):
                print(f"  Profile: {result['profile']}")
            print(f"  Account: {result['display_name']}")
            print(f"  Email: {result['email']}")
            print(f"  Plan: {plan_label}")
            print(f"  Scopes: {len(scopes)}")
            if result.get("plan", 0) < 2:
                print("\n  WARNING: Pro plan or higher required for attendance reports and cloud recordings.")
        else:
            print(f"Connection failed: {result.get('message', 'Unknown error')}")
            sys.exit(1)
    else:
        print("Usage: python3 zoom_client.py --test [--profile NAME]")
        print("       python3 zoom_client.py --scopes [--profile NAME]")
        print("Or import ZoomClient in other scripts.")


if __name__ == "__main__":
    main()
