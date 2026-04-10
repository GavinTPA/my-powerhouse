---
name: setup-vault
description: Set up your Obsidian Knowledge Vault — daily note template, folder structure, and Smart Connections semantic search for Claude Code. Use when "set up my vault", "setup vault", "knowledge vault setup", "configure obsidian", "set up daily notes", "connect my vault", "setup smart connections".
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# Setup Vault — Your Knowledge Vault Configuration

This skill configures your Obsidian vault as a working Knowledge Vault and connects it to Claude Code via semantic search. Run it once — it checks what's already done and only sets up what's missing.

---

## Before We Start

Tell the member what this skill does and check prerequisites before touching anything.

**Say this:**

> "This sets up three things:
> 1. **Your daily note template** — so Obsidian creates a fresh command center every day
> 2. **Your folder structure** — Templates and Zettelkasten folders where everything lives
> 3. **Semantic search for Claude Code** — so I can search your vault by meaning, not just keywords
>
> Let me check what's already in place."

---

## Step 1: Find the Vault

Search for the MAGI vault. Check these locations in order:

1. `~/Documents/MAGI/`
2. `~/Documents/COPYobsidian/MAGI/`
3. `~/MAGI/`
4. Search: `find ~/Documents -maxdepth 3 -name ".obsidian" -type d 2>/dev/null`

**If found:** Confirm with the member: "I found your vault at [path]. Is that right?"

**If not found:** Ask: "I can't find your MAGI vault. Where did you create it? (Check Obsidian — the vault name shows at the top of the sidebar.)"

Store the vault path — every subsequent step uses it.

---

## Step 2: Prerequisites Check

Run these checks and report results as a checklist:

```
CHECK 1: Obsidian vault exists at [path]
CHECK 2: .obsidian/ folder exists (Obsidian has been opened at least once)
CHECK 3: Smart Connections plugin installed (.obsidian/plugins/smart-connections/ exists)
CHECK 4: Smart Connections has indexed (.smart-env/multi/ folder exists with .ajson files)
CHECK 5: python3 available (python3 --version)
CHECK 6: git available (git --version)
```

**Report format:**

> "Here's your setup status:
> - [pass/fail] Vault found
> - [pass/fail] Obsidian configured
> - [pass/fail] Smart Connections installed
> - [pass/fail] Smart Connections has indexed your vault
> - [pass/fail] Python available
> - [pass/fail] Git available"

**If Smart Connections is not installed (CHECK 3 fails):**
> "Smart Connections isn't installed yet. Open Obsidian → Settings → Community Plugins → Browse → search 'Smart Connections' → Install → Enable. Then come back and run this again."
> Stop here. Don't continue without SC installed.

**If SC hasn't indexed yet (CHECK 4 fails):**
> "Smart Connections is installed and it hasn't built its search index yet. Open Obsidian and leave it running for a few minutes — it indexes automatically in the background. The daily note setup will work fine now. The semantic search connection will work once indexing completes."
> Continue with all steps — the MCP server will work once indexing finishes.

**If python3 is missing (CHECK 5 fails):**
> "Python isn't installed. I'll set up your daily notes now. For the semantic search connection, you'll need Python first — try: brew install python (Mac) or download from python.org (Windows). Then run this skill again."
> Continue with Steps 3-4. Skip Steps 5-6.

**If all checks pass:**
> "Everything looks good. Let me set up your vault."

---

## Step 3: Create Folders

Inside the vault, create these if they don't exist:

- `Templates/`
- `Zettelkasten/`

**Tell the member:**
> "Templates/ is where your note templates live. Zettelkasten/ is where all your notes go — daily notes, research, coaching summaries, everything."

---

## Step 4: Daily Note Template

### 4a: Create the template

Write `Templates/Daily Note.md` inside the vault:

```
---
type: daily
date: {{date:YYYY-MM-DD}}
---
# {{date:dddd, D MMM, YYYY}}

## Ship This = Win Day


## Today's 3
- [ ]
- [ ]
- [ ]

## Captures


## Done Today


## Scratch

```

IMPORTANT: The `{{date:...}}` tags must be written EXACTLY as shown — with the double curly braces. Do NOT evaluate or replace them. Obsidian fills them in when creating a new daily note.

**If the file already exists:** Ask the member before overwriting: "You already have a Daily Note template. Want me to replace it with the standard Powerhouse template, or keep yours?"

**Tell the member:**
> "Your daily note template is ready. Here's what each section is for:
> - **Ship This = Win Day** — your ONE thing for today
> - **Today's 3** — three tasks, no more
> - **Captures** — everything you discover today lands here
> - **Done Today** — your victory lap at end of day
> - **Scratch** — temporary notes, thinking space"

### 4b: Configure Daily Notes core plugin

Read `.obsidian/core-plugins.json` from the vault. Set `"daily-notes"` to `true` and `"templates"` to `true`. Preserve all other values. If the file doesn't exist, create it:

```json
{
  "file-explorer": true,
  "global-search": true,
  "command-palette": true,
  "switcher": true,
  "backlink": true,
  "tag-pane": true,
  "page-preview": true,
  "daily-notes": true,
  "templates": true,
  "note-composer": true,
  "outline": true,
  "file-recovery": true
}
```

### 4c: Configure Daily Notes settings

Write `.obsidian/daily-notes.json` in the vault:

```json
{
  "format": "",
  "folder": "Zettelkasten",
  "template": "Templates/Daily Note"
}
```

This tells Obsidian: create daily notes in the Zettelkasten folder using the Daily Note template.

### 4d: Configure Templates settings

Write `.obsidian/templates.json` in the vault:

```json
{
  "folder": "Templates"
}
```

---

## Step 5: Smart Connections MCP Server

This connects the vault to Claude Code so semantic search works from the terminal.

### 5a: Clone the server

Check if `~/smart-connections-mcp/` already exists.

**If yes:** Skip cloning. Tell the member: "Smart Connections MCP server already installed."

**If no:**
```bash
git clone https://github.com/dan6684/smart-connections-mcp.git ~/smart-connections-mcp
```

### 5b: Install dependencies

Check if `~/smart-connections-mcp/.venv/` exists and has a working Python.

**If yes:** Skip. Tell the member: "Dependencies already installed."

**If no:**
```bash
cd ~/smart-connections-mcp
```

Check if `uv` is available (`uv --version`). If not:
- Mac: `brew install uv`
- Windows: `pip install uv`

Then:
```bash
cd ~/smart-connections-mcp && uv venv && uv pip install -r requirements.txt
```

### 5c: Configure MCP connection

Determine the three absolute paths needed:
1. Python in the venv: `~/smart-connections-mcp/.venv/bin/python` (Mac) or `~/smart-connections-mcp/.venv/Scripts/python.exe` (Windows)
2. Server script: `~/smart-connections-mcp/server.py`
3. Vault path: from Step 1

Read `~/.mcp.json` if it exists.

**If it already has a `"smart-connections"` entry:** Skip. Tell the member: "MCP already configured."

**If not (or file doesn't exist):** Add or create the entry. IMPORTANT — if the file exists with other servers, MERGE the new entry. Do NOT overwrite.

```json
{
  "mcpServers": {
    "smart-connections": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/absolute/path/to/vault"
      }
    }
  }
}
```

Use the actual absolute paths on this machine. No tildes — full paths only.

---

## Step 6: Summary

Tell the member exactly what was done and what they need to do:

> "Your Knowledge Vault is configured. Here's what I set up:
>
> [list only the things that were actually created/changed — skip items that already existed]
>
> **Two things you need to do now:**
>
> 1. **Close and reopen Obsidian** — this activates the daily notes plugin
> 2. **Restart Claude Code** — type `/exit`, then type `claude` in the same window — this connects the semantic search
>
> **After restarting Obsidian:**
> Click the calendar icon in the left sidebar (or press Cmd+P and type 'Open today's daily note'). You should see your template with today's date filled in.
>
> **After restarting Claude Code:**
> Try saying 'search my vault for daily notes' to test the semantic search connection."

---

## Boundaries

| ✅ Always | ⚠️ Ask First | 🚫 Never |
|-----------|--------------|----------|
| Check prerequisites before acting | Overwrite existing template files | Modify Smart Connections plugin settings |
| Report what's already done vs what's new | Install uv or Python | Delete any existing vault content |
| Use absolute paths in MCP config | Skip MCP if Python missing | Overwrite ~/.mcp.json (always merge) |
| Explain the WHY at each step | | Touch files outside the vault and ~/smart-connections-mcp |

---

*Version 1.0 — Workshop 3, February 2026*
