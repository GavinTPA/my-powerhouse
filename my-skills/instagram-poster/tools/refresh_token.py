#!/usr/bin/env python3
"""
Instagram Token Refresh
=======================
Refreshes the long-lived Instagram access token.

Long-lived tokens expire after 60 days. This script:
1. Uses the current token to request a fresh one
2. Updates ~/.config/instagram-poster.yaml with new token
3. Extends expiry by another 60 days

Run this before your token expires (check token_expires in config).

Usage:
    python3 refresh_token.py
"""

import sys
from datetime import datetime

from token_utils import (
    load_config,
    save_config,
    check_token_age,
    refresh_token,
    CONFIG_PATH,
)


def main():
    print("=" * 50)
    print("Instagram Poster - Token Refresh")
    print("=" * 50)
    print()

    # Load current config
    config = load_config()

    # Check current token status
    days_remaining = check_token_age(config)
    print(f"Current token expires: {config.get('token_expires', 'unknown')}")
    print(f"Days remaining: {days_remaining}")
    print()

    if days_remaining < -60:
        print("Token expired too long ago. Run auth_setup.py for fresh authorization.")
        sys.exit(1)

    if days_remaining > 50:
        print("Token still has plenty of time. No refresh needed.")
        print("(Refresh when under 7 days remaining)")
        return

    # Refresh the token
    print("Refreshing token...")

    try:
        new_token, expires_date = refresh_token(config["access_token"])

        # Update config
        config["access_token"] = new_token
        config["token_expires"] = expires_date.strftime("%Y-%m-%d")
        config["last_refresh"] = datetime.now().strftime("%Y-%m-%d")

        save_config(config)

        print()
        print(f"Token refreshed successfully!")
        print(f"New expiry: {expires_date.strftime('%Y-%m-%d')}")
        print(f"Config updated: {CONFIG_PATH}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        print()
        print("If token is fully expired, run auth_setup.py for fresh authorization.")
        sys.exit(1)


if __name__ == "__main__":
    main()
