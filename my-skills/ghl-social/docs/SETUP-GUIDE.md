# GHL Social - Setup Guide

**Time required:** ~5 minutes
**Prerequisite:** ghl-connect must already be set up. If you haven't done that, start with `ghl-connect/docs/SETUP-GUIDE.md`.

---

## What You're Building

You're adding social media scheduling capabilities to your existing GHL connection. The ghl-social skill shares the same config file and token as ghl-connect — you just need to add a few more scopes.

---

## Part 1: Add Social Planner Scopes (3 minutes)

1. Go to **GHL Settings** > **Integrations** > **Private Integrations**
2. Click on your integration (the one you created for ghl-connect)
3. Add these scopes:

| Scope | What It Enables |
|-------|----------------|
| `socialplanner/post.readonly` | View scheduled and published posts |
| `socialplanner/post.write` | Create and schedule new posts |
| `socialplanner/account.readonly` | List connected social accounts |
| `socialplanner/category.readonly` | View post categories |
| `socialplanner/tag.readonly` | View post tags |

4. **Save** — your existing token now has social planner access

**What this step accomplishes:** Expands your existing token's permissions. No new token needed — the same `pit_` token you already configured now works for both email/CRM and social scheduling.

---

## Part 2: Connect Social Accounts in GHL (if not already done)

ghl-social posts through accounts you've already connected in GHL's Social Planner:

1. In GHL, go to **Marketing** > **Social Planner**
2. Click **Settings** (gear icon) or **Accounts**
3. Connect the platforms you want to post to (Facebook, Instagram, LinkedIn, etc.)

Each platform has its own connection flow (usually "Sign in with..."). GHL handles the OAuth — you just authorize.

**Note:** Instagram requires a connected Facebook Page. LinkedIn uses your personal profile.

---

## Part 3: Test the Connection (1 minute)

Tell Claude:

> "List my connected social accounts"

Claude will run `tools/list_accounts.py` and show your connected platforms with their status:

```
Connected Social Accounts:
  Facebook (Page) — Your Business Page — ACTIVE
  LinkedIn (Profile) — Your Name — ACTIVE
  Instagram (Profile) — yourhandle — ACTIVE
```

If any account shows **EXPIRED**, reconnect it in GHL > Marketing > Social Planner > Settings.

---

## Part 4: First Post (5 minutes)

Test with a dry run first:

> "Schedule a test post to LinkedIn saying 'Testing my social planner connection' for tomorrow at 9am — dry run"

You should see a preview of what would be posted. If it looks good:

> "Go ahead and schedule it"

Check that it appears in your GHL Social Planner calendar.

---

## Schedule Time Format

Always use ISO 8601 with your timezone offset. Here are common timezone offsets:

| Timezone | Standard | Daylight Saving |
|----------|----------|-----------------|
| Melbourne (Australia) | AEST +10:00 | AEDT +11:00 |
| US Eastern | EST -05:00 | EDT -04:00 |
| US Pacific | PST -08:00 | PDT -07:00 |
| UK | GMT +00:00 | BST +01:00 |

**Examples:**
```
2026-03-10T09:00:00+11:00   (9am Melbourne AEDT)
2026-03-10T09:00:00-05:00   (9am US Eastern EST)
2026-03-10T09:00:00+00:00   (9am UK GMT)
```

---

## What Success Looks Like

After setup, you should have:

- [ ] Social planner scopes added to your existing Private Integration Token
- [ ] At least one social account connected in GHL Social Planner
- [ ] `list_accounts.py` shows your connected accounts as ACTIVE
- [ ] A dry-run post previews correctly
- [ ] A scheduled post appears in your GHL Social Planner calendar

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Forbidden" or 403 error | Social planner scopes not added. Go back to Part 1 |
| No accounts found | Connect social accounts in GHL Marketing > Social Planner first (Part 2) |
| Account shows EXPIRED | Reconnect in GHL. Token expiry is ~60 days for most platforms |
| Post doesn't appear in calendar | Check the schedule time — wrong timezone offset is the usual cause |
| Instagram post fails | Instagram requires an image. Text-only posts aren't supported |
| "ModuleNotFoundError" | Run `pip3 install requests pyyaml` (Mac) or `pip install requests pyyaml` (Windows) |
