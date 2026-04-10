# GHL API Gotchas

> Working copy for ghl-connect skill. These gotchas were discovered through live testing and save you from hitting the same walls.

---

## GHL Email Defaults

When creating emails for GHL, always apply these defaults unless you specify otherwise.

### First Name Personalization (Default: Always)

**Always use `{{contact.first_name}}` in email greetings.** You'll rarely want an email without it.

```html
Hey {{contact.first_name}},<br><br>
```

**Merge field syntax:** `{{contact.first_name}}` — double curly braces, lowercase, underscored.

**Blank name gotcha:** If a contact has no first name on file, GHL renders it blank (e.g. "Hey ,"). Either:
- Ensure all contacts have a first name before sending
- Set up an If/Else fallback in the workflow to catch blanks

**The only exception:** When the email intentionally opens cold without a greeting (e.g. urgency emails that start with a punchy line). Specify it explicitly when this is the case.

### HTML Paragraph Spacing

GHL's email editor collapses `<p>` paragraph tags, resulting in a wall of text. Use `<br><br>` for paragraph spacing instead.

**Wrong:**
```html
<p>First paragraph.</p>
<p>Second paragraph.</p>
```

**Right:**
```html
First paragraph.<br><br>

Second paragraph.<br><br>
```

### Email Archiving (Default: Always)

**Every GHL email gets saved to your knowledge vault and linked from your daily note.** This creates a permanent record of what was sent, when, and to whom.

**Pattern:**
1. Create file: `Zettelkasten/GHL Email - [Subject/Purpose] - YYYY-MM-DD.md`
2. Include: subject line, audience, date, attachment links, full HTML body in a ` ```html ` code block (one-click copy in Obsidian)
3. Add to daily note Captures: `- [[GHL Email - Subject - YYYY-MM-DD]] - Brief description`

**Why:** Emails are ephemeral in GHL. Having them in your knowledge vault means they're searchable, linkable, and available for reference when building future campaigns or onboarding sequences.

### Quick Reference

| Element | GHL Code |
|---------|----------|
| First name | `{{contact.first_name}}` |
| Full name | `{{contact.name}}` |
| Email | `{{contact.email}}` |
| Paragraph break | `<br><br>` |
| Bold text | `<b>text</b>` |
| Link | `<a href="URL">text</a>` |

---

## GHL Email Copy Review Workflow

When composing GHL emails, always follow this sequence:

1. **Show copy inline first** — review the text in the terminal before it goes anywhere
2. **Save to your knowledge vault** — only after you approve the copy
3. **Send a test to yourself** — visual check before bulk send
4. **Send to recipients** — only after the test email looks right

This prevents wasted effort from saving/sending unapproved copy, and catches formatting issues before recipients see them.

---

## GHL Invoice Product Visibility (Price Type Filtering)

GHL invoices filter the "Select Product" dropdown by price type. If your products don't appear (shows "No Data"), it's a mismatch between the invoice type and the product's price configuration.

| Invoice Type | Shows Products With |
|-------------|-------------------|
| One-time/Standard | One-time prices only |
| Recurring | Recurring prices only |

**What happened (2026-02-04):** Products existed but showed "No Data" when creating an invoice. Products were configured as recurring; invoice was one-time. Switching to recurring invoice fixed it.

**Fix options:**
1. Create a recurring invoice instead (if the product IS recurring)
2. Add a one-time price variant to the existing product
3. Don't create a new product -- the existing one just needs the right invoice type

**Also:** GHL has no admin "retry payment" button for pending orders. For stuck initial payments, send a fresh invoice. Automatic retries only apply to subscription renewals (2nd+ payments), not first-time order form submissions.

---

## GHL Conversations API Timestamps

GHL returns `lastMessageDate` and similar timestamp fields as **Unix timestamps in milliseconds**, not ISO strings. Convert before display:

```python
from datetime import datetime

if isinstance(timestamp, int):
    dt = datetime.fromtimestamp(timestamp / 1000)
```

Discovered during ghl-connect build (2026-02-05).

---

## GHL Messages Endpoint (Nested Response Structure)

The messages endpoint returns a DIFFERENT structure from other GHL endpoints:

| Endpoint | Structure |
|----------|-----------|
| `/conversations/search` | `{"conversations": [...], "meta": {"startAfterId": "..."}}` |
| `/conversations/{id}/messages` | `{"messages": {"lastMessageId": "...", "nextPage": true, "messages": [...]}}` |

**Don't use `paginate()` for messages.** The nested dict causes `KeyError: -1` when treated as a list.

**Field mapping differences:**
- `direction` → `meta.email.direction` (not top-level)
- `type` → `messageType` (e.g. `TYPE_EMAIL`, not numeric)
- `subject` → `meta.email.subject`

Discovered during ghl-connect pagination bug fix (2026-02-06).

---

## GHL Inbound Email Body Quirk

The `get_messages` endpoint (conversation thread view) returns `[Empty content]` for inbound email bodies. The `get_conversations` endpoint (inbox list view) shows the full text in the `lastMessage` field. When reading inbound messages, use the conversation summary for the message content, not the individual message from the thread.

Discovered during GHL inbox triage (2026-02-16).

---

## GHL Contact Search — Use the Right Endpoint

GHL has two contact search endpoints. Using the wrong one for tag searches returns incomplete results.

| Endpoint | Method | Tag Support | Use For |
|----------|--------|-------------|---------|
| `/contacts/` | GET | None (text search only) | `--query`, `--email` lookups |
| `/contacts/search` | POST | Server-side filtering | `--tag` lookups |

**Root cause of the old bug:** `GET /contacts/` has no tag parameter. Passing a tag as `query` does a text search, then client-side filtering only finds contacts where the tag name happens to match searchable text fields. This returned 2/8 contacts.

**Fix (2026-02-10):** `search_contacts.py` and `trigger_workflow.py` now use `POST /contacts/search` with proper filters for tag searches:

```python
filters = [{"field": "tags", "operator": "eq", "value": "foundation-10-buyer"}]
client.search_contacts_paginated(filters, max_items=500)
```

**Available tag filter operators:** `eq`, `not_eq`, `contains`, `not_contains`, `exists`, `not_exists`

**Pagination:** Page-based (`page`/`pageLimit`, max 500/page, 10,000 total). For 10,000+ use cursor-based (`searchAfter`).

**Filter grouping (AND/OR):**
```python
filters = [{"group": "AND", "filters": [
    {"field": "tags", "operator": "eq", "value": "foundation-10-buyer"},
    {"field": "tags", "operator": "not_eq", "value": "aipowerhousevipteam"}
]}]
```

**Source:** [GHL Advanced Search Spec (ClickUp)](https://doc.clickup.com/8631005/d/h/87cpx-158396/6e629989abe7fad) — the official API docs page has an empty schema; the real spec lives on ClickUp.

---

## GHL Contact Creation (Create or Update)

Create: `POST /contacts/` with `{firstName, lastName, email, companyName, locationId}`
Tags: `POST /contacts/{id}/tags` with `{tags: ["tag1", "tag2"]}`
Update: `PUT /contacts/{id}` with fields to change

Always search by email first to avoid duplicates. Tool: `tools/create_contact.py`

---

## GHL DND / Unsubscribe Blocks API Sends

If a contact has unsubscribed or DND is active for Email, the API returns 400 with "Cannot send message as DND is active for Email." Updating their email does NOT clear DND — it must be toggled off manually in GHL's contact record.

Discovered when a contact's old email was unsubscribed. Updating to a new email didn't clear the DND flag (2026-02-07).

---

## GHL Communities API (None)

GHL's built-in Communities/Kollab feature has NO public API. Not "limited" - zero endpoints. Feature request open since 2023 with ~30 votes. No timeline. Cannot build any programmatic integrations for GHL communities.

The mobile app (GoKollab) has 3.0 stars with 6 ratings. Broken push notifications reported since January 2026.

---

## GHL Direct Webhook to Slack (No Middleware)

GHL Custom Webhook workflow action supports full HTTP control: method, URL, headers, and custom JSON body with template variables. This sends directly to Slack incoming webhooks without Zapier/Make.

**GHL Workflow Configuration:**

| Field | Value |
|-------|-------|
| Method | POST |
| URL | Slack incoming webhook URL |
| Headers | `Content-Type: application/json` |
| Body | `{"text": "{{contact.first_name}} {{contact.last_name}} just joined!"}` |

For rich formatting, use Slack Block Kit in the body. GHL template variables (`{{contact.*}}`) render before sending.

Confirmed working (2026-02-06).

---

## GHL Media Library Upload API

Upload files to GHL Media Library via API and get back a permanent CDN URL.

**Endpoint:** `POST /medias/upload-file`
**Content-Type:** `multipart/form-data` (NOT JSON — override default headers)
**Limits:** 25 MB standard files, 500 MB video

**Request:**
```
files={"file": (filename, bytes, mime_type)}
data={"hosted": "false"}
```

**Response (confirmed 2026-02-20):**
```json
{
  "fileId": "69978f0e18171558e0bb7892",
  "url": "https://assets.cdn.filesafe.space/TAkJ8H3DfDYzhAfrhFFV/media/uuid.pdf",
  "traceId": "uuid"
}
```

**URL field:** `url` — contains the permanent CDN link.

**CDN domain note:** API uploads return `assets.cdn.filesafe.space` URLs. Manually uploaded files (via GHL dashboard) use `storage.googleapis.com/msgsndr/` URLs. Both work and both stay alive permanently. Same location ID in both.

**Versioning strategy:** Each upload creates a new file with a unique URL. Old URLs stay alive forever — safe to upload updated versions without breaking old email links. Update indexes to point to the new URL. Never delete old versions (GHL has no delete media API anyway).

**Token scope:** Requires `medias.write` on the Private Integration token. 403 = scope not enabled.

**Tool:** `tools/upload_media.py`

**Official docs note:** GHL's official API docs page has an empty response schema for this endpoint. The real spec lives on ClickUp, and the actual response shape was confirmed via live testing above.

_Source: Extracted from API Gotchas Master Index, 2026-02-25_

---

## GHL Media Upload — HTML Files Rejected

GHL's upload API rejects `.html` files with `400 Invalid File Type`. This is a security restriction on their end — HTML files could contain scripts.

**Workaround:** Zip the HTML file first, then upload the `.zip`. Recipients download, unzip, and open in browser.

```bash
zip file.zip file.html
python3 tools/upload_media.py file.zip
```

Discovered during RRM report prototype delivery (2026-03-06).
