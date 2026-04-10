#!/usr/bin/env python3
"""
Instagram OAuth Setup
=====================
One-time setup to get Instagram access token and user ID.

This script:
1. Opens browser for Instagram OAuth authorization
2. Captures the authorization code from redirect
3. Exchanges code for short-lived token
4. Exchanges for long-lived token (60 days)
5. Gets Instagram User ID
6. Saves config to ~/.config/instagram-poster.yaml

Instagram App credentials are read from environment variables:
- META_APP_ID: Your Meta Developer App ID
- META_APP_SECRET: Your Meta Developer App Secret

Usage:
    source ~/.zshrc && python3 auth_setup.py

After running:
- Config saved to ~/.config/instagram-poster.yaml
- Token valid for 60 days
- Run refresh_token.py before expiry
"""

import os
import sys
import webbrowser
import yaml
import requests
from pathlib import Path
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Instagram App credentials (from environment)
APP_ID = os.environ.get("META_APP_ID")
APP_SECRET = os.environ.get("META_APP_SECRET")

if not APP_ID or not APP_SECRET:
    print("Error: META_APP_ID and META_APP_SECRET environment variables are required.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Add them to your ~/.zshrc:", file=sys.stderr)
    print('  export META_APP_ID="your_app_id_here"', file=sys.stderr)
    print('  export META_APP_SECRET="your_app_secret_here"', file=sys.stderr)
    print("", file=sys.stderr)
    print("Then run: source ~/.zshrc", file=sys.stderr)
    print("", file=sys.stderr)
    print("To get these values, say: set up instagram poster", file=sys.stderr)
    sys.exit(1)

# Redirect URI for OAuth
REDIRECT_URI = "http://localhost:8765/callback"

# Config file location
CONFIG_PATH = Path.home() / ".config" / "instagram-poster.yaml"

# OAuth authorization URL
# Note: Must use api.instagram.com (not www.instagram.com)
# Scopes updated Jan 2025: instagram_business_* replaced instagram_*
AUTH_URL = (
    f"https://api.instagram.com/oauth/authorize"
    f"?client_id={APP_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&scope=instagram_business_basic,instagram_business_content_publish"
    f"&response_type=code"
)


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler to capture OAuth callback."""

    auth_code = None

    def do_GET(self):
        """Handle OAuth redirect."""
        parsed = urlparse(self.path)

        if parsed.path == "/callback":
            query = parse_qs(parsed.query)

            if "code" in query:
                OAuthCallbackHandler.auth_code = query["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"""
                    <html>
                    <body style="font-family: system-ui; text-align: center; padding: 50px;">
                        <h1>Authorization Successful!</h1>
                        <p>You can close this window and return to the terminal.</p>
                    </body>
                    </html>
                """)
            else:
                error = query.get("error_description", ["Unknown error"])[0]
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(f"""
                    <html>
                    <body style="font-family: system-ui; text-align: center; padding: 50px;">
                        <h1>Authorization Failed</h1>
                        <p>Error: {error}</p>
                    </body>
                    </html>
                """.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress HTTP logging."""
        pass


def get_auth_code() -> str:
    """
    Open browser for OAuth and capture the auth code.
    """
    print("Opening browser for Instagram authorization...")
    print(f"If browser doesn't open, visit: {AUTH_URL}")

    # Start local server to capture callback
    server = HTTPServer(("localhost", 8765), OAuthCallbackHandler)
    server.timeout = 120  # 2 minute timeout

    # Open browser
    webbrowser.open(AUTH_URL)

    print("\nWaiting for authorization (timeout: 2 minutes)...")

    # Wait for callback
    while OAuthCallbackHandler.auth_code is None:
        server.handle_request()

    server.server_close()

    return OAuthCallbackHandler.auth_code


def exchange_for_short_token(auth_code: str) -> str:
    """Exchange authorization code for short-lived access token."""
    print("Exchanging code for access token...")

    response = requests.post(
        "https://api.instagram.com/oauth/access_token",
        data={
            "client_id": APP_ID,
            "client_secret": APP_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "code": auth_code
        }
    )

    if response.status_code != 200:
        raise Exception(f"Token exchange failed: {response.text}")

    data = response.json()
    return data["access_token"], data["user_id"]


def exchange_for_long_token(short_token: str) -> tuple:
    """Exchange short-lived token for long-lived token (60 days)."""
    print("Exchanging for long-lived token...")

    response = requests.get(
        "https://graph.instagram.com/access_token",
        params={
            "grant_type": "ig_exchange_token",
            "client_secret": APP_SECRET,
            "access_token": short_token
        }
    )

    if response.status_code != 200:
        raise Exception(f"Long token exchange failed: {response.text}")

    data = response.json()
    expires_in = data.get("expires_in", 5184000)  # Default 60 days in seconds
    expires_date = datetime.now() + timedelta(seconds=expires_in)

    return data["access_token"], expires_date


def get_instagram_user_id(access_token: str) -> str:
    """Get Instagram Business/Creator account user ID."""
    response = requests.get(
        "https://graph.instagram.com/v21.0/me",
        params={
            "fields": "user_id,username",
            "access_token": access_token
        }
    )

    if response.status_code != 200:
        raise Exception(f"Failed to get user ID: {response.text}")

    data = response.json()
    print(f"Authenticated as: @{data.get('username', 'unknown')}")
    return data.get("user_id") or data.get("id")


def save_config(user_id: str, access_token: str, expires_date: datetime):
    """Save configuration to YAML file."""
    config = {
        "instagram_user_id": user_id,
        "access_token": access_token,
        "token_expires": expires_date.strftime("%Y-%m-%d"),
        "last_refresh": datetime.now().strftime("%Y-%m-%d"),
        "app_id": APP_ID
    }

    # Ensure directory exists
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    print(f"\nConfig saved to: {CONFIG_PATH}")
    print(f"Token expires: {expires_date.strftime('%Y-%m-%d')}")


def main():
    print("=" * 50)
    print("Instagram Poster - OAuth Setup")
    print("=" * 50)
    print()

    try:
        # Step 1: Get authorization code
        auth_code = get_auth_code()
        print(f"Got authorization code: {auth_code[:20]}...")

        # Step 2: Exchange for short-lived token
        short_token, user_id = exchange_for_short_token(auth_code)
        print(f"Got short-lived token and user ID: {user_id}")

        # Step 3: Exchange for long-lived token
        long_token, expires_date = exchange_for_long_token(short_token)
        print(f"Got long-lived token (expires: {expires_date.strftime('%Y-%m-%d')})")

        # Step 4: Verify and get username
        verified_user_id = get_instagram_user_id(long_token)

        # Step 5: Save config
        save_config(verified_user_id or user_id, long_token, expires_date)

        print()
        print("Setup complete! You can now use the instagram-poster skill.")

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
