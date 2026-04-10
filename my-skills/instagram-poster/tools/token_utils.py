#!/usr/bin/env python3
"""
Instagram Token Utilities
=========================
Shared token management functions for Instagram poster tools.

Functions:
- load_config(): Load YAML config
- save_config(): Save YAML config
- check_token_age(): Check days until token expires
- refresh_token(): Refresh the access token via API
- ensure_fresh_token(): Auto-refresh if expiring soon (main entry point)
"""

import sys
import yaml
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Config file location
CONFIG_PATH = Path.home() / ".config" / "instagram-poster.yaml"

# Threshold for auto-refresh (days)
AUTO_REFRESH_THRESHOLD = 7


def load_config() -> dict:
    """Load config from YAML file."""
    if not CONFIG_PATH.exists():
        print(f"Error: Config file not found at {CONFIG_PATH}", file=sys.stderr)
        print("Run auth_setup.py first.", file=sys.stderr)
        sys.exit(1)

    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def save_config(config: dict):
    """Save config back to YAML file."""
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


def check_token_age(config: dict) -> int:
    """Check days until token expires. Returns negative if expired."""
    expires_str = config.get("token_expires", "")
    if not expires_str:
        return -999

    try:
        expires_date = datetime.strptime(expires_str, "%Y-%m-%d")
        delta = expires_date - datetime.now()
        return delta.days
    except ValueError:
        return -999


def refresh_token(current_token: str) -> tuple:
    """
    Refresh the long-lived token.
    Returns (new_token, expires_date).
    """
    response = requests.get(
        "https://graph.instagram.com/refresh_access_token",
        params={
            "grant_type": "ig_refresh_token",
            "access_token": current_token
        }
    )

    if response.status_code != 200:
        raise Exception(f"Refresh failed: {response.text}")

    data = response.json()
    expires_in = data.get("expires_in", 5184000)  # Default 60 days
    expires_date = datetime.now() + timedelta(seconds=expires_in)

    return data["access_token"], expires_date


def ensure_fresh_token() -> str:
    """
    Ensure the access token is fresh, auto-refreshing if needed.

    Checks token expiry and refreshes if <= 7 days remaining.
    Prints a message when refresh occurs.

    Returns:
        str: The current (possibly refreshed) access token
    """
    config = load_config()
    days_remaining = check_token_age(config)

    # Check if token needs refresh
    if days_remaining <= AUTO_REFRESH_THRESHOLD:
        if days_remaining < -60:
            print(f"Error: Token expired too long ago ({abs(days_remaining)} days). "
                  "Run auth_setup.py for fresh authorization.", file=sys.stderr)
            sys.exit(1)

        # Attempt refresh
        try:
            new_token, expires_date = refresh_token(config["access_token"])

            # Update config
            config["access_token"] = new_token
            config["token_expires"] = expires_date.strftime("%Y-%m-%d")
            config["last_refresh"] = datetime.now().strftime("%Y-%m-%d")

            save_config(config)

            print(f"[Auto-refresh] Token refreshed, new expiry: {expires_date.strftime('%Y-%m-%d')}",
                  file=sys.stderr)

            return new_token

        except Exception as e:
            print(f"Error: Token refresh failed: {e}", file=sys.stderr)
            print("If token is fully expired, run auth_setup.py for fresh authorization.",
                  file=sys.stderr)
            sys.exit(1)

    # Token is fresh, return as-is
    return config["access_token"]
