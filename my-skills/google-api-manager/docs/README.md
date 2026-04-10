# google-api-manager — Technical Reference

## What It Does

Wraps the `gcloud` CLI to manage Google API keys for a team. Creates per-person Google Cloud projects, restricted API keys, and budget alerts — all through natural language commands in Claude Code.

## Architecture

```
User: "add team member Sarah Jones"
  → SKILL.md instructs Claude
    → Claude runs tools/add_member.py "Sarah Jones"
      → add_member.py calls gcloud CLI (6 commands)
        → Returns AIza key string
    → Claude presents key to user
```

**No Google Cloud Python SDK required.** All operations go through `gcloud` CLI via `subprocess.run()`. This keeps dependencies at zero (beyond PyYAML for config).

## Dependencies

- **gcloud CLI** — Google Cloud SDK (`brew install --cask google-cloud-sdk`)
- **PyYAML** — Config file handling (usually pre-installed with Python)
- **Google Cloud billing account** — Required for API key provisioning

## Config

Location: `~/.config/google-api-manager.yaml`

```yaml
billing_account_id: "01A2B3-4C5D6E-7F8G9H"
project_prefix: "ww"
budget_per_member_usd: 20
overall_budget_usd: 100
members:
  - name: "Sarah Jones"
    project_id: "ww-sarah-jones"
    key_id: "projects/123/locations/global/keys/abc-def"
    key_string: "AIza..."
    status: "active"
    added: "2026-02-24"
```

## Tools

| File | Purpose | CLI Usage |
|------|---------|-----------|
| `gcloud_client.py` | Shared client — config loading, gcloud execution, member management | `python3 gcloud_client.py --test` |
| `setup.py` | First-time configuration wizard | `python3 setup.py` or `--check` |
| `add_member.py` | Provision a new team member (6-step sequence) | `python3 add_member.py "Name"` |
| `list_members.py` | Show all members with status | `python3 list_members.py [--verify]` |
| `revoke_member.py` | Disable/delete key or project | `python3 revoke_member.py "Name" --disable` |
| `check_spending.py` | Budget alert status | `python3 check_spending.py` |

## The 6-Step Provisioning Sequence

Per the Teams Edition guide, each member requires:

1. `gcloud projects create {prefix}-{name}` — Create dedicated project
2. `gcloud billing projects link` — Connect to billing account
3. `gcloud services enable generativelanguage.googleapis.com` — Enable image gen API
4. `gcloud services api-keys create --api-target=service=generativelanguage.googleapis.com` — Restricted key
5. `gcloud services api-keys get-key-string` — Retrieve the AIza key
6. `gcloud billing budgets create` — Per-member budget alert

## Testing

```bash
# Test gcloud and config
python3 tools/gcloud_client.py --test

# Check setup status
python3 tools/setup.py --check

# Verify members against live data
python3 tools/list_members.py --verify
```

## Security

- API keys are restricted to `generativelanguage.googleapis.com` — a leaked key can only generate images
- Key strings stored in YAML config on the team lead's machine only
- Budget alerts warn at 90% and 100% of per-member limit
- Revocation is instant (disable or delete)
