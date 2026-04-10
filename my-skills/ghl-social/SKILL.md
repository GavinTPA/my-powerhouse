---
name: ghl-social
description: Schedule and manage social media posts via GHL Social Planner API. Use when "schedule a post", "post to LinkedIn", "post to Facebook", "social media schedule", "schedule this article", "content calendar", "list social accounts", "check social posts", "social planner".
allowed-tools: Bash, Read, Edit, Write, Glob, Grep
---

# GHL Social — Social Media Scheduling via GoHighLevel

> **Requires ghl-connect to be configured first.** This skill shares the same config file (`~/.config/ghl-connect.yaml`). If you haven't set up ghl-connect, start there — see `docs/SETUP-GUIDE.md` in ghl-connect.

Schedule and manage social media posts across connected platforms using the GHL Social Planner API.

> **First time?** Start with `docs/SETUP-GUIDE.md` for adding social planner scopes to your existing ghl-connect token.

## Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Preview posts with --dry-run before scheduling | Schedule posts to live platforms | Post without reviewing the content first |
| Show account status before first use | Bulk schedule a full content calendar | Modify or delete existing published posts |
| Use your voice and style for content adaptation | Post to platforms not in initial scope | Share API credentials |
| Run content through ai-slop-detector if installed | Change schedule times on live posts | Exceed platform rate limits |

## Connected Platforms

Run `tools/list_accounts.py` to discover your connected platforms and their status.

## Workflow

### Step 1: Verify Accounts

Before scheduling, confirm accounts are still connected:

```bash
python3 tools/list_accounts.py
```

If any account shows EXPIRED, reconnect in GHL > Marketing > Social Planner.

### Step 2: Prepare Content

When adapting content for multiple platforms:

1. Read the source content (article, newsletter, carousel)
2. Adapt per platform using your voice and style:
   - **LinkedIn:** Professional, insight-led hook, key takeaway, article link. Up to 3,000 chars.
   - **Facebook:** Conversational, community-focused, link to full article. No char limit in practice.
   - **Instagram:** Short caption, CTA to link in bio. Max 2,200 chars. Needs image/carousel.
   - **Threads:** Punchy, conversational, max 500 chars. Can include up to 20 images.
   - **YouTube:** Video required. Title up to 5,000 chars.

### Step 3: Preview (Dry Run)

Always preview before scheduling:

```bash
python3 tools/schedule_post.py \
  --platform linkedin \
  --text "Your post content here" \
  --schedule "2026-03-10T09:00:00+11:00" \
  --dry-run
```

Present the preview for review. Wait for approval before proceeding.

### Step 4: Schedule

After approval:

```bash
python3 tools/schedule_post.py \
  --platform linkedin \
  --text "Your post content here" \
  --schedule "2026-03-10T09:00:00+11:00"
```

For multiple platforms with the same content:
```bash
python3 tools/schedule_post.py \
  --platform linkedin,facebook \
  --text "Your post content here" \
  --schedule "2026-03-10T09:00:00+11:00"
```

### Step 5: Verify

After scheduling, confirm the post appears:

```bash
python3 tools/list_posts.py
```

## Platform-Specific Notes

### Not Covered by GHL
- **X (Twitter):** GHL removed X integration Dec 2024. Use X API directly.
- **Medium:** Not supported by GHL. Use Medium API separately.
- **Substack:** Use substack-publisher skill if installed.

### Platform Limitations
- **Instagram:** Requires image/video. Text-only posts not supported.
- **YouTube:** Requires video. Text-only not supported.
- **Threads:** Max 500 chars, up to 20 images.
- **TikTok:** Connected in GHL but requires mobile app for posting.

## Schedule Time Format

Always use ISO 8601 with your timezone offset:

```
2026-03-10T09:00:00+11:00   (9am AEDT / Melbourne)
2026-03-10T09:00:00-05:00   (9am EST / US Eastern)
2026-03-10T09:00:00-08:00   (9am PST / US Pacific)
2026-03-10T09:00:00+00:00   (9am GMT / UK)
```

### Common Timezone Offsets

| Timezone | Standard | Daylight Saving |
|----------|----------|-----------------|
| Melbourne | AEST +10:00 | AEDT +11:00 |
| US Eastern | EST -05:00 | EDT -04:00 |
| US Pacific | PST -08:00 | PDT -07:00 |
| UK | GMT +00:00 | BST +01:00 |

Example posting windows (adjust to your timezone):
- LinkedIn: 8-9am Tuesday-Thursday
- Facebook: 9-11am or 1-3pm
- Instagram: 11am-1pm or 7-9pm

## API Gotchas

- GET /posts returns 404 — listing uses POST /posts/list only
- Account discovery is GET /accounts (flat), not /oauth/{platform}/accounts
- Token expiry: Facebook/Instagram/Threads/LinkedIn expire ~60 days (check with list_accounts.py)
- YouTube token is short-lived but auto-refreshes
- Version header 2021-07-28 works for all social planner endpoints

See `docs/api-gotchas.md` for the complete list.
