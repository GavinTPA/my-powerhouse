# GHL Connect - Setup Guide

**Time required:** ~15 minutes for setup, ~5 minutes for testing
**What you need:** A GoHighLevel account with API access (paid plan required)

---

## What You're Building

You're creating a secure connection between Claude Code and your GoHighLevel account. This uses something called a **Private Integration Token (PIT)** — GHL's method for granting API access to external tools.

Here's what that means in plain English: you create a "Private Integration" inside your GHL account, choose what it's allowed to do (called scopes), and it generates a token. You paste that token into a config file on your machine. From that point on, the ghl-connect tools can read and interact with your GHL data — no browser login needed.

Your token stays on your machine. It's never uploaded anywhere.

---

## Part 1: Check Your GHL Plan (1 minute)

Private Integrations require a paid GHL plan. The free trial does NOT include API access.

1. Log in to your GHL account
2. Go to **Settings** (gear icon, bottom-left) > **Company Billing**
3. Confirm you're on a paid plan (Starter at $97/mo or higher)

If you're on a free trial — stop here. You need to upgrade first, or wait until your paid plan activates.

**What this step accomplishes:** Confirms your account has API access. Without a paid plan, the Private Integration option won't appear in your settings.

---

## Part 2: Create a Private Integration Token (5 minutes)

1. In GHL, go to **Settings** (gear icon, bottom-left)
2. Click **Integrations** in the left sidebar
3. Click **Private Integrations** at the top
4. Click **+ Add** (or "Create Private Integration")
5. Name it **Powerhouse Connect** (or whatever you like — this is just a label)

### Choose Your Scopes

Scopes control what the integration is allowed to do. **Start with read-only** — you can always add more later.

**Starter scopes (read-only — safe to start here):**

| Scope | What It Enables |
|-------|----------------|
| `contacts.readonly` | Search and view contact records |
| `conversations.readonly` | See your inbox conversations |
| `conversations/message.readonly` | Read message content in threads |

**Intermediate scopes (when you're ready to interact):**

| Scope | What It Enables |
|-------|----------------|
| `contacts.write` | Create and update contact records |
| `conversations.write` | Create conversations |
| `conversations/message.write` | Send emails and messages |

**Advanced scopes (media uploads, workflows):**

| Scope | What It Enables |
|-------|----------------|
| `medias.write` | Upload files to GHL Media Library |
| `medias.readonly` | List files in Media Library |
| `workflows.readonly` | Trigger workflows (for bulk email) |

**Tip:** You can always come back to Settings > Private Integrations, edit your integration, and add more scopes later. Better to build up than start with everything.

6. Click **Save** / **Create**
7. You'll see your token — it starts with `pit_` followed by a long string
8. **Copy this token now.** You'll need it in Part 5.

**What this step accomplishes:** Creates the secure bridge between your machine and GHL's API. The token is the only credential needed — no client IDs, no OAuth flows, no redirect URLs.

---

## Part 3: Find Your Location ID (2 minutes)

The Location ID tells the API which GHL sub-account to connect to.

**Method 1 — From the URL bar:**
1. Go to your GHL dashboard
2. Look at the URL: `https://app.gohighlevel.com/v2/location/XXXXXXXX/...`
3. The string after `/location/` is your Location ID

**Method 2 — From Settings:**
1. Go to **Settings** > **Business Info** (or **Business Profile**)
2. Look for "Location ID" or "Sub-Account ID"

Copy this value — you'll need it in Part 5.

**What this step accomplishes:** Identifies which specific GHL account (location) the tools should connect to. If you only have one location, there's only one ID.

---

## Part 4: Install Python Dependencies (1 minute)

The tools need two Python packages. Tell Claude:

> "Install the ghl-connect Python dependencies"

Or run it yourself:

**Mac/Linux:**
```bash
pip3 install requests pyyaml
```

**Windows:**
```bash
pip install requests pyyaml
```

Most systems already have these. If you get "ModuleNotFoundError" later, come back and run this.

---

## Part 5: Run Setup (2 minutes)

### Mac/Linux

Tell Claude:

> "Run the ghl-connect setup script"

Claude will run `scripts/setup.sh` which creates a config file at `~/.config/ghl-connect.yaml`.

Then tell Claude your token and location ID:

> "Here's my GHL token: pit_XXXXX... and my location ID: XXXXXXXX"

Claude will add them to the config file.

### Windows

The setup script doesn't run on Windows. Instead, tell Claude:

> "Create my ghl-connect config file"

Claude will create the config at the right path for your OS. Then give Claude your token and location ID as above.

**Alternatively**, you can create the file manually:

1. Create folder: `C:\Users\YourName\.config\`
2. Create file: `ghl-connect.yaml` in that folder
3. Paste this template:

```yaml
# GHL Connect Configuration
api_token: "YOUR_TOKEN_HERE"
location_id: "YOUR_LOCATION_ID"
api_base: "https://services.leadconnectorhq.com"
api_version: "2021-07-28"
default_from_email: ""
max_sends_per_session: 10
```

4. Replace `YOUR_TOKEN_HERE` with your `pit_` token
5. Replace `YOUR_LOCATION_ID` with your location ID

**What this step accomplishes:** Saves your credentials locally on your machine. The token never leaves your computer — it's used to authenticate directly with GHL's servers each time you run a command.

---

## Part 6: Test the Connection (1 minute)

Tell Claude:

> "Test the ghl-connect connection"

Claude will run `python3 tools/ghl_client.py --test` and you should see:

```
Connection successful!
  Location ID: XXXXXXXX
  Conversations API: accessible
```

**If you see an error:**

| Error | Fix |
|-------|-----|
| "Config file not found" | Run setup again (Part 5) |
| "api_token not configured" | Open `~/.config/ghl-connect.yaml` and paste your token |
| "Authentication failed" | Token is wrong or expired. Copy fresh from GHL Settings |
| "Rate limited" | Wait 10 seconds, try again |

---

## Part 7: First Operation (5 minutes)

Test with a real operation. Try one of these:

### Check your inbox

> "Check my GHL inbox"

You should see a list of recent conversations with sender info, dates, and message previews.

### Search contacts

> "Search GHL contacts by tag [your-tag-name]"

Replace `[your-tag-name]` with a tag that exists in your GHL account.

### Read a conversation

If you saw conversations in the inbox check, try:

> "Show me the messages in GHL conversation [conversation-id]"

This pulls the full thread for that conversation.

**What this step accomplishes:** Confirms the full pipeline works — auth, API calls, and data formatting. If this works, you're ready to use ghl-connect.

---

## Part 8: Adding More Scopes Later

You can always add scopes without creating a new token:

1. Go to **GHL Settings** > **Integrations** > **Private Integrations**
2. Click on your integration (Powerhouse Connect)
3. Add the new scopes you want
4. **Save** — the same token now has the expanded permissions

Here's a reference for what each capability requires:

| You Want To... | Scopes Needed |
|----------------|---------------|
| Read inbox and messages | `conversations.readonly`, `conversations/message.readonly` |
| Search contacts | `contacts.readonly` |
| Send emails | `conversations/message.write` |
| Create/update contacts | `contacts.write` |
| Upload files (PDFs, images) | `medias.write`, `medias.readonly` |
| Trigger workflows (bulk email) | `workflows.readonly` |
| Schedule social media posts | See ghl-social skill SETUP-GUIDE |

---

## Part 9: Where the Real API Docs Live

GHL's official API documentation (on the Stoplight/Marketplace site) is JavaScript-rendered and has **empty response schemas for many endpoints.** This means the docs often show you the request format but not what comes back.

The best documentation for the GHL V2 API lives on **ClickUp**: [GHL Advanced Search Spec](https://doc.clickup.com/8631005/d/h/87cpx-158396/6e629989abe7fad)

The `docs/api-gotchas.md` file in this skill documents what actually works — confirmed via live testing. When in doubt, trust the gotchas file over the official docs.

---

## What Success Looks Like

After setup, you should have:

- [ ] GHL paid plan confirmed (Starter or higher)
- [ ] Private Integration Token created with at least read-only scopes
- [ ] Location ID found and saved
- [ ] Python dependencies installed (`requests`, `pyyaml`)
- [ ] Config file created at `~/.config/ghl-connect.yaml`
- [ ] Connection test passes
- [ ] At least one real operation works (inbox check, contact search, etc.)

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Config file not found" | Run `scripts/setup.sh` (Mac) or create manually (Windows) — see Part 5 |
| "api_token not configured" | Open `~/.config/ghl-connect.yaml` and paste your `pit_` token |
| "Authentication failed" | Token is wrong, expired, or from a different location. Copy fresh from GHL |
| "Rate limited" | Wait 10 seconds and retry. The tools enforce rate limits automatically |
| "Cannot send message as DND is active" | Contact has unsubscribed. Toggle DND off in their GHL contact record |
| "No conversations found" | Try `--status all` instead of `--status unread` |
| "ModuleNotFoundError" | Run `pip3 install requests pyyaml` (Mac) or `pip install requests pyyaml` (Windows) |
| Private Integration option missing | You need a paid GHL plan. Free trials don't include API access |
| Products show "No Data" on invoices | Invoice type (one-time vs recurring) must match product price type |
