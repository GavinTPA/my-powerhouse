---
name: instagram-poster
description: Posts carousels and Reels to Instagram via Graph API. Use when "post this carousel to Instagram", "publish carousel", "post to Instagram", "post this reel", "publish reel", "set up instagram poster", "set up posting", "configure instagram posting", "refresh my Instagram token".
allowed-tools: Read, Glob, Bash
---

# Instagram Poster

**macOS only.** This skill is not supported on Windows.

## What This Does

Posts carousels and Reels directly to Instagram via the Graph API. Uploads media to Vercel Blob for public URLs, creates containers, and publishes — eliminating manual upload steps.

**Supports:**
- **Carousels** — 2-10 images, swipeable posts
- **Reels** — Short-form video (5-90 seconds)

## Prerequisites

Before first use, ensure these are configured:

1. **Environment variables** (in `~/.zshrc`):
   - `META_APP_ID` — Your Meta Developer App ID
   - `META_APP_SECRET` — Your Meta Developer App Secret
   - `BLOB_READ_WRITE_TOKEN` — Vercel Blob storage token

2. **Config file** (`~/.config/instagram-poster.yaml`):
   - Contains Instagram access token and user ID
   - Created by running `auth_setup.py` (one-time OAuth)

**If not set up:** Say "set up instagram poster" to run the setup wizard.

---

## Pre-Check (Before Any Posting)

Before running any posting tool, verify the config file exists:
```bash
test -f ~/.config/instagram-poster.yaml && echo "Ready" || echo "Not set up"
```

If "Not set up": "Instagram posting isn't set up yet. Say 'set up instagram poster' to connect your Instagram account. It takes about 10 minutes."

---

## Instructions — Carousels

### Step 1: Locate Carousel Images

Find the most recent carousel folder in `~/Downloads/`:
```bash
ls -td ~/Downloads/carousel* | head -1
```

Verify the images:
- Should contain 2-10 PNG images
- Named like `CarouselName01.png`, `CarouselName02.png`, etc.

### Step 2: Get User Approval (REQUIRED)

Before posting, ALWAYS show this confirmation:

```
Ready to post carousel to Instagram:
- X images from ~/Downloads/carouselYYMMDD/
- Caption preview: [first 100 chars of caption...]

Post now? (y/n)
```

DO NOT proceed without explicit user approval.

### Step 3: Execute Posting

Run the post_carousel.py script:

**Option A: Direct caption**
```bash
source ~/.zshrc && python3 my-skills/instagram-poster/tools/post_carousel.py \
  --folder <carousel_folder_path> \
  --caption "<caption_text>"
```

**Option B: Using a template**
```bash
source ~/.zshrc && python3 my-skills/instagram-poster/tools/post_carousel.py \
  --folder <carousel_folder_path> \
  --template carousel \
  --title "Your Headline Here" \
  --topic "business"
```

**Caption options (in priority order):**
1. If `--template` flag provided, render caption from template
2. If user provides `--caption`, use it directly
3. If carousel folder contains `caption.txt`, read it
4. Otherwise, ask user for caption

### Step 4: Report Results

On success, display:
- Instagram post URL
- Number of images posted
- "Carousel is now live!"

On failure:
- Show error message
- Suggest checking token expiry if auth-related

## Caption Templates

Use templates for consistent, high-performing captions. Templates live in `resources/caption-templates.yaml`.

### Available Templates

| Template | Best For | Emoji | Hashtags |
|----------|----------|-------|----------|
| `carousel` | Standard educational carousel | Minimal | 5 |
| `educational` | Deep teaching content | None | 6 |
| `promotional` | Launch/offer content | Minimal | 4 |
| `story` | Personal narrative | Minimal | 5 |
| `quicktip` | Bite-sized actionable tips | Moderate | 5 |

### Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{title}` | Main headline | "5 Things I Wish I Knew" |
| `{topic}` | Subject area (becomes hashtag) | "saas" or "coaching" |
| `{cta}` | Call to action (optional) | "DM me 'START'" |

---

## Instructions — Reels

### Step 1: Locate Video File

Find the Reel video file:
```bash
ls -td ~/Downloads/reels-builder-* | head -1
```

**Video requirements:**
- Duration: 5-90 seconds
- Format: MP4 or MOV
- Aspect ratio: 9:16 (portrait)
- Max size: 300MB

### Step 2: Get User Approval (REQUIRED)

Before posting, ALWAYS show confirmation. DO NOT proceed without explicit user approval.

### Step 3: Execute Posting

```bash
source ~/.zshrc && python3 my-skills/instagram-poster/tools/post_reel.py \
  --video <video_file_path> \
  --caption "<caption_text>"
```

**Cover options:**
- `--thumb-offset <ms>`: Use video frame at this millisecond offset
- `--cover <path>`: Upload a custom cover image

---

## Error Handling

| Error | Meaning | Action |
|-------|---------|--------|
| "Token expired" | Access token > 60 days old | Say "refresh my Instagram token" |
| "Rate limited" | Too many API calls | Wait 1 hour, retry |
| "Container processing failed" | Image/video issue | Check format/size/duration |
| "No config file" | First time use | Say "set up instagram poster" |

---

## Token Management

**Refresh token manually:**
```bash
source ~/.zshrc && python3 my-skills/instagram-poster/tools/refresh_token.py
```

**Token lifecycle:** Your authorization lasts 60 days. If you use the posting skill regularly, it auto-refreshes itself. If you take a long break and see a "Token expired" error, say "refresh my Instagram token" or "set up instagram poster" to re-authorize.

---

## Setup Wizard

**Trigger:** "set up instagram poster", "set up posting", "configure instagram posting"

### Step 1: Check Prerequisites — Account Type

Ask: "Is your Instagram account a Business or Creator account?"

- If Personal → guide them: Settings → Account → Switch to Professional Account → Choose Business
- If already Business/Creator → proceed
- Verify Facebook Page is linked to Instagram (required for Graph API)

### Step 2: Create Meta Developer App

Direct to: `https://developers.facebook.com/apps/`

Walk them through:
1. Click "Create App"
2. Select "Other" for use case
3. Select "Business" app type
4. Name it (e.g., "My Instagram Poster")
5. Go to App Dashboard → Add Product → Instagram → Set Up
6. Go to App Settings → Basic
7. Copy **App ID** and **App Secret** (click "Show" to reveal secret)

**Validation:** Ask member to paste App ID — verify it's numeric, 15-16 digits.

### Step 3: Store Meta App Credentials

Follow the .zshrc Nuclear Protection Protocol (same pattern as nano-banana-pro):

1. Read `~/.zshrc` — if fails or empty, STOP
2. Verify `ANTHROPIC_API_KEY` exists (proof of Powerhouse setup)
3. Create timestamped backup: `cp ~/.zshrc ~/.zshrc.bak-$(date +%s)`
4. Use Edit to append `META_APP_ID` and `META_APP_SECRET`
5. Source: `source ~/.zshrc`
6. Post-edit verify: Read ~/.zshrc, confirm all keys present
7. If ANTHROPIC_API_KEY missing → restore from backup immediately

### Step 4: Set Up Vercel Blob Storage

**Why this step:** Instagram's API needs your images on a public web address temporarily while it processes them. Vercel Blob is a free service that holds them for about 30 seconds, then we clean up. Think of it as a staging area.

Direct to: `https://vercel.com/signup` (free account)

Walk them through:
1. Sign up with GitHub (you already have GitHub from Powerhouse setup)
2. Create a new project — name it anything (e.g., "my-instagram"). This is just a container for the storage.
3. Click the **Storage** tab at the top of your project
4. Click **Create** → **Blob**
5. Name it (e.g., "instagram-uploads") → **Create**
6. You'll see connection details. Copy the `BLOB_READ_WRITE_TOKEN` value

Store in `.zshrc` using same Nuclear Protection Protocol.

**Validation:** Verify token starts with `vercel_blob_rw_`

**Cost note:** Free tier handles ~20-30 carousels/month (500MB storage, 100GB bandwidth). Most members won't hit this.

### Step 5: Run OAuth Authorization

**Pre-check:** Before running, verify port 8765 is free:
```bash
lsof -i :8765
```
If busy, tell member which app is using it and ask them to quit it.

Execute:
```bash
source ~/.zshrc && python3 my-skills/instagram-poster/tools/auth_setup.py
```

Explain what will happen: "A browser window will open. Log into your Instagram account and click 'Authorize'. You'll see a quick redirect — that's normal. The tool captures the authorization automatically."

Verify: Check `~/.config/instagram-poster.yaml` exists and contains `access_token`.

Report token expiry date (60 days from now).

**Token lifecycle:** Your authorization lasts 60 days. If you use the posting skill regularly, it auto-refreshes itself. If you take a long break and see a "Token expired" error, say "refresh my Instagram token" or "set up instagram poster" to re-authorize.

### Step 6: Test Post (Optional)

Ask: "Want to do a test post? I can post a single image to verify everything works."

If yes → guide them through a simple single-image test.
If no → "You're all set. Say 'post this carousel to Instagram' after creating one."

### Setup Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Validate credentials before storing | Post anything to Instagram | Store credentials in code files |
| Backup .zshrc before editing | Run OAuth flow | Show full tokens in output |
| Verify post-edit | Test post | Skip user approval before posting |
| Check token expiry | | |
