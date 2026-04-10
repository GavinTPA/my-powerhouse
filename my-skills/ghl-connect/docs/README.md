# ghl-connect

## What It Does

Connects Claude Code to GoHighLevel's Conversations API for reading and sending emails from the terminal.

## Dependencies

- Python 3.x
- `requests` - HTTP client
- `pyyaml` - Config loading
- `beautifulsoup4` - Not used (HTML stripped with regex for lighter footprint)

Install if needed:
```bash
# Mac
pip3 install requests pyyaml

# Windows
pip install requests pyyaml
```

## Configuration

**Config file:** `~/.config/ghl-connect.yaml`

Run `scripts/setup.sh` to create the template, or see `docs/SETUP-GUIDE.md` for full setup instructions (including Windows).

**Required fields:**
- `api_token` - Private Integration Token from GHL
- `location_id` - Your GHL location ID

**Required API scopes (start with read-only, add more as needed):**
- contacts.readonly
- conversations.readonly
- conversations/message.readonly

**Additional scopes when ready to interact:**
- contacts.write
- conversations.write
- conversations/message.write
- workflows.readonly (for bulk workflow triggers)

## Architecture

```
ghl-connect/
├── SKILL.md                  # Claude Code skill definition
├── tools/
│   ├── ghl_client.py         # Core API client (auth, rate limiting, pagination)
│   ├── sanitize.py           # Security: HTML stripping, instruction detection
│   ├── get_conversations.py  # Fetch inbox conversations
│   ├── get_messages.py       # Read messages in a thread
│   ├── send_message.py       # Send email (with confirmation)
│   ├── search_contacts.py    # Find contacts by tag/name/email
│   └── trigger_workflow.py   # Add contacts to GHL workflows
├── scripts/
│   └── setup.sh              # First-time config setup (Mac/Linux)
├── references/
│   └── SECURITY.md           # Prompt injection defense documentation
└── docs/
    ├── README.md             # This file
    ├── GUIDE.md              # Business-friendly guide
    ├── SETUP-GUIDE.md        # Step-by-step setup instructions
    ├── api-gotchas.md        # API quirks and workarounds
    └── ROADMAP.md            # Version history and plans
```

## API Reference

**Base URL:** `https://services.leadconnectorhq.com`

**Version header:** `2021-07-28`

**Rate limits:**
- Burst: 100 requests / 10 seconds
- Daily: 200,000 requests

**Auth:** Bearer token (Private Integration Token)

**Pagination:** Cursor-based using `startAfterId` parameter

## Security

See `references/SECURITY.md` for the full prompt injection defense design.

Key points:
- All inbound email content is treated as untrusted
- HTML is stripped before display
- Instruction-like patterns are flagged
- No auto-execution of anything from email content
- Session send limit (default: 10) prevents runaway sends

## Setup

See `docs/SETUP-GUIDE.md` for the full walkthrough (Mac and Windows).

Quick version:
1. Run `scripts/setup.sh` to create config template (Mac/Linux)
2. Create Private Integration Token in GHL:
   - Settings > Private Integrations > Add Integration
   - Grant required scopes (start read-only)
   - Copy token
3. Paste token into `~/.config/ghl-connect.yaml`
4. Add your location_id
5. Test: `python3 tools/ghl_client.py --test`

## Usage

See SKILL.md for full workflow documentation.

Quick examples:
```bash
# Check inbox
python3 tools/get_conversations.py --status unread

# Search contacts
python3 tools/search_contacts.py --tag my-tag

# Send (with preview)
python3 tools/send_message.py --contact-id X --subject "Hi" --html "<p>Hello</p>" --dry-run
```
