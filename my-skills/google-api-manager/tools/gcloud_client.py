#!/usr/bin/env python3
"""
Google Cloud CLI Client
=======================
Shared client for wrapping gcloud CLI commands.

Handles:
- Configuration loading from ~/.config/google-api-manager.yaml
- gcloud CLI detection and auth verification
- Command execution with JSON output parsing
- Error handling with clear messages

Usage:
    from gcloud_client import GCloudClient

    client = GCloudClient()
    client.run(["projects", "list"])

Test:
    python3 gcloud_client.py --test
"""

import sys
import json
import subprocess
import argparse
from pathlib import Path

import yaml

CONFIG_PATH = Path.home() / ".config" / "google-api-manager.yaml"


class GCloudClient:
    """Wrapper around gcloud CLI with config management."""

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load config from YAML file."""
        if not CONFIG_PATH.exists():
            return {}
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f) or {}

    def save_config(self):
        """Write current config back to YAML file."""
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

    @property
    def billing_account_id(self) -> str:
        return self.config.get("billing_account_id", "")

    @property
    def project_prefix(self) -> str:
        return self.config.get("project_prefix", "")

    @property
    def budget_per_member_usd(self) -> int:
        return self.config.get("budget_per_member_usd", 20)

    @property
    def overall_budget_usd(self) -> int:
        return self.config.get("overall_budget_usd", 100)

    @property
    def members(self) -> list:
        return self.config.get("members", [])

    def is_configured(self) -> bool:
        """Check if initial setup has been completed."""
        return bool(self.billing_account_id and self.project_prefix)

    def check_gcloud_installed(self) -> tuple[bool, str]:
        """Check if gcloud CLI is installed and accessible."""
        try:
            result = subprocess.run(
                ["gcloud", "--version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                version_line = result.stdout.strip().split("\n")[0]
                return True, version_line
            return False, result.stderr.strip()
        except FileNotFoundError:
            return False, "gcloud not found in PATH"
        except subprocess.TimeoutExpired:
            return False, "gcloud command timed out"

    def check_auth(self) -> tuple[bool, str]:
        """Check if user is authenticated with gcloud."""
        try:
            result = subprocess.run(
                ["gcloud", "auth", "list", "--format=json"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                accounts = json.loads(result.stdout)
                active = [a for a in accounts if a.get("status") == "ACTIVE"]
                if active:
                    return True, active[0].get("account", "unknown")
                return False, "No active account"
            return False, result.stderr.strip()
        except Exception as e:
            return False, str(e)

    def run(self, args: list, json_output: bool = True, timeout: int = 60) -> dict:
        """Run a gcloud command and return parsed output.

        Args:
            args: gcloud subcommand args (e.g., ["projects", "list"])
            json_output: Add --format=json flag
            timeout: Command timeout in seconds

        Returns:
            {"ok": True, "data": <parsed JSON or raw text>}
            or {"ok": False, "error": <error message>}
        """
        cmd = ["gcloud"] + args
        if json_output and "--format" not in " ".join(args):
            cmd.append("--format=json")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout
            )
            if result.returncode != 0:
                error = result.stderr.strip()
                if not error:
                    error = result.stdout.strip()
                return {"ok": False, "error": error}

            output = result.stdout.strip()
            if json_output and output:
                try:
                    return {"ok": True, "data": json.loads(output)}
                except json.JSONDecodeError:
                    return {"ok": True, "data": output}
            return {"ok": True, "data": output}

        except subprocess.TimeoutExpired:
            return {"ok": False, "error": f"Command timed out after {timeout}s"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def run_raw(self, args: list, timeout: int = 60) -> dict:
        """Run a gcloud command and return raw text output (no JSON parsing)."""
        return self.run(args, json_output=False, timeout=timeout)

    def find_member(self, name: str) -> dict | None:
        """Find a member by name (case-insensitive partial match)."""
        name_lower = name.lower()
        for member in self.members:
            if name_lower in member.get("name", "").lower():
                return member
        return None

    def add_member_to_config(self, name: str, project_id: str,
                              key_id: str, key_string: str):
        """Add a member to the config and save."""
        from datetime import date
        if "members" not in self.config:
            self.config["members"] = []
        self.config["members"].append({
            "name": name,
            "project_id": project_id,
            "key_id": key_id,
            "key_string": key_string,
            "status": "active",
            "added": date.today().isoformat(),
        })
        self.save_config()

    def update_member_status(self, name: str, status: str):
        """Update a member's status in config."""
        member = self.find_member(name)
        if member:
            member["status"] = status
            self.save_config()


def main():
    parser = argparse.ArgumentParser(description="Google Cloud CLI Client")
    parser.add_argument("--test", action="store_true",
                        help="Test gcloud installation and auth")
    args = parser.parse_args()

    if args.test:
        client = GCloudClient()

        installed, version = client.check_gcloud_installed()
        if installed:
            print(f"gcloud installed: {version}")
        else:
            print(f"gcloud NOT installed: {version}")
            sys.exit(1)

        authed, account = client.check_auth()
        if authed:
            print(f"Authenticated as: {account}")
        else:
            print(f"NOT authenticated: {account}")
            sys.exit(1)

        if client.is_configured():
            print(f"Config: billing={client.billing_account_id}, "
                  f"prefix={client.project_prefix}, "
                  f"members={len(client.members)}")
        else:
            print("Config: Not yet configured (run setup)")

        print("\nAll checks passed.")


if __name__ == "__main__":
    main()
