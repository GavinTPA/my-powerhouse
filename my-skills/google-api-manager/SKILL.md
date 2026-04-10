---
name: google-api-manager
description: Manage Google API keys for your team via gcloud CLI. Use when "add team member", "show my team", "list team members", "check team spending", "revoke member", "remove member", "set up google api manager", "google api setup".
allowed-tools: Read, Bash, AskUserQuestion
---

# Google API Manager

Manage Google API keys for your team through natural language. Add members, check spending, revoke access — all without touching gcloud commands.

## How It Works

Each team member gets their own Google Cloud project linked to your billing account. One project per person means per-person cost tracking, budget alerts, and instant revocation.

Config lives at `~/.config/google-api-manager.yaml`.

## Instructions

### First-Time Setup

When the user says "set up google api manager":

1. Run `python3 tools/setup.py --check` to show current status
2. If not configured, run `python3 tools/setup.py` interactively
3. The wizard handles: gcloud install check, auth, billing account selection, project prefix, budget settings
4. Confirm setup is complete by running `--check` again

**Prerequisites the user needs before setup:**
- gcloud CLI installed (`brew install --cask google-cloud-sdk` on Mac, `winget install Google.CloudSDK` on Windows)
- A Google account with a billing account at console.cloud.google.com/billing

### Add a Team Member

When the user says "add team member [name]" or "add [name] to my team":

1. Confirm the name: "Adding Sarah Jones — that will create project `{prefix}-sarah-jones`. Go ahead?"
2. Run: `python3 tools/add_member.py "Sarah Jones"`
3. The tool runs the full 6-step sequence:
   - Creates Google Cloud project
   - Links billing
   - Enables Generative Language API
   - Creates restricted API key (image generation only)
   - Retrieves the AIza key string
   - Sets per-member budget alert
4. Present the key string to the user: "Here's Sarah's key. Send it to her — she pastes it when Claude asks during 'set up nano banana pro'."

**If the project ID is taken** (globally unique requirement), the tool automatically appends a number suffix.

### List Team Members

When the user says "show my team" or "list team members":

1. Run: `python3 tools/list_members.py`
2. Shows table: name, project ID, status, date added
3. For live verification: `python3 tools/list_members.py --verify`

### Check Spending

When the user says "check team spending" or "how much is my team spending":

1. Run: `python3 tools/check_spending.py`
2. Shows budget alert status per member
3. For detailed spend breakdown, direct user to: console.cloud.google.com/billing → Reports → filter by project

**Note:** Detailed spend data requires the browser dashboard. The CLI shows budget alert thresholds, not real-time spend.

### Revoke Access

When the user says "revoke [name]" or "remove [name]":

1. Confirm which action:
   - **Disable** (reversible) — key stops working, can re-enable later
   - **Delete key** (permanent) — key gone, project stays, can create new key
   - **Delete project** (nuclear) — everything gone, 30-day recovery window
2. Run the appropriate command:
   - `python3 tools/revoke_member.py "Sarah Jones" --disable`
   - `python3 tools/revoke_member.py "Sarah Jones" --delete-key`
   - `python3 tools/revoke_member.py "Sarah Jones" --delete-project`
3. Confirm the action completed

### Re-enable a Disabled Key

If someone was disabled and needs to be re-enabled:

```bash
gcloud services api-keys update KEY_ID --project=PROJECT_ID --enable
```

Get the KEY_ID and PROJECT_ID from `list_members.py` output or the YAML config.

## Tool Reference

All tools live in `tools/` within this skill folder.

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `setup.py` | First-time config wizard | `--check` for status only |
| `add_member.py` | Full provisioning sequence | `"Name"`, `--budget N` |
| `list_members.py` | Show all members | `--verify` for live check |
| `revoke_member.py` | Remove access | `--disable`, `--delete-key`, `--delete-project` |
| `check_spending.py` | Budget status | — |
| `gcloud_client.py` | Shared client (not called directly) | `--test` |

## Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Confirm member name before provisioning | Revoke action type (disable vs delete) | Delete a project without explicit confirmation |
| Save member to YAML after adding | Budget amount overrides | Modify billing account settings |
| Show key string after creation | Re-enable a disabled key | Store keys anywhere except the YAML config |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "gcloud not found" | Install: `brew install --cask google-cloud-sdk` (Mac) or `winget install Google.CloudSDK` (Windows). Restart terminal. |
| "Not authenticated" | Run: `gcloud auth login` |
| "billing account not found" | Run: `gcloud billing accounts list` to find the correct ID |
| "project ID already exists" | Tool auto-appends number suffix. If still fails, choose a more unique prefix. |
| "permission denied on billing" | Check you're a billing admin at console.cloud.google.com/billing |
| Config file missing | Run setup again: `python3 tools/setup.py` |
