# Nano Banana Pro — Setup Guide

**For:** Connecting image generation to your AI Powerhouse workspace
**Time:** About 10 minutes
**Cost:** ~$0.13 per image (no subscription, pay as you go)

---

## The Easy Way (Recommended)

Open Claude Code in your workspace and type:

```
set up nano banana pro
```

Claude walks you through everything — getting the key, storing it safely, and testing the connection. You don't need to read the rest of this guide unless you prefer to do it manually.

---

## Manual Setup

If you'd rather set things up yourself, follow these steps.

### Part 1: Get Your API Key

**Why:** The API key connects your tools to Google's image generation AI. Think of it as a VIP pass — it identifies you, lets your tools in, and tracks your usage.

**You'll need:** A personal Google (Gmail) account. Work or school Google accounts often block access to AI Studio.

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Sign in with your **personal Gmail account**
3. Click **"Create API key in new project"**
4. **Copy the key immediately** — it starts with `AIza` and is only shown once. If you lose it, you can delete it and create a new one.

**If you see "Permission Denied":** You're likely signed into a work or school account. Switch to your personal Gmail.

### Part 2: Enable Billing

**Why:** Image generation through the API requires a billing account. The cost is about 13 cents per image — cheaper than any stock photo subscription, and every image is custom-made for your business.

1. Go to [console.cloud.google.com/billing](https://console.cloud.google.com/billing)
2. Select the project where you created your API key (if prompted)
3. Click **"Link a billing account"** or **"Enable billing"**
4. Add a payment method (credit card)

**Recommended:** Set a budget alert so you're never surprised:
1. Go to [console.cloud.google.com/billing/budgets](https://console.cloud.google.com/billing/budgets)
2. Create a budget: **$20/month** is plenty for normal use
3. Set alerts at 50%, 90%, and 100%

**Typical spending:** A carousel of 8 images costs about $1.07. Even generating 10 images a day, you'd spend about $40/month. Most coaches use far less.

### Part 3: Store Your Key

**Mac (zsh):**

1. Open Terminal
2. Type: `open ~/.zshrc` (this opens your shell config file in TextEdit)
3. Add this line at the end:
   ```
   export GOOGLE_API_KEY="AIzaSyD-YOUR-ACTUAL-KEY-HERE"
   ```
   Replace `AIzaSyD-YOUR-ACTUAL-KEY-HERE` with your actual key.
4. Save and close the file
5. Back in Terminal, type: `source ~/.zshrc`

**Windows (PowerShell):**

1. Open PowerShell
2. Type: `notepad $PROFILE` (this opens your PowerShell profile in Notepad)
3. If Notepad asks to create the file, click Yes
4. Add this line:
   ```
   $env:GOOGLE_API_KEY = "AIzaSyD-YOUR-ACTUAL-KEY-HERE"
   ```
5. Save and close
6. Close and reopen PowerShell

**The Golden Rule:** Never share your API key in email, Slack, or any message. Never paste it into a document someone else can see. It lives on your computer and nowhere else.

### Part 4: Install the Python Package

In Terminal (Mac) or PowerShell (Windows):

```
pip install google-genai pillow
```

### Part 5: Test the Connection

Open Claude Code in your workspace and type:

```
set up nano banana pro
```

Or run the test directly:

**Mac:**
```
python3 tools/generate_image.py --test
```

**You should see:** A success message and a test image saved to your Downloads folder — Hello Kitty and Chibi Gundam giving you a thumbs up.

---

## Troubleshooting

| What You See | What It Means | What To Do |
|---|---|---|
| `GOOGLE_API_KEY not set` | Key not in your shell config | Re-do Part 3, then run `source ~/.zshrc` |
| `Key starts with... — expected AIza` | Wrong key or copy error | Go to aistudio.google.com/apikey, copy the key again |
| `ModuleNotFoundError: google` | Python package not installed | Run `pip install google-genai pillow` |
| `billing` or `402` error | Billing not enabled | Re-do Part 2 |
| `Invalid API key` or `401` | Key revoked or incorrect | Delete the key at aistudio.google.com/apikey, create a new one |
| `Permission Denied` on AI Studio | Work/school Google account | Sign in with your personal Gmail instead |
| `quota` or `429` error | Rate limit hit | Wait a minute and try again |

---

## Quick Reference

| What | Where |
|------|-------|
| Create/view API keys | https://aistudio.google.com/apikey |
| Billing setup | https://console.cloud.google.com/billing |
| Budget alerts | https://console.cloud.google.com/billing/budgets |
| API restrictions (optional) | https://console.cloud.google.com/apis/credentials |
| Your API key | `~/.zshrc` (Mac) or `$PROFILE` (Windows) |
| Cost tracking | Type `nano banana costs` in Claude Code |

---

## If Something Goes Wrong with Your Shell Config

If you edited `~/.zshrc` and something broke (Claude Code stopped working, commands not found, etc.):

1. The setup process creates a backup before any changes
2. In Terminal, type: `ls -t ~/.zshrc.bak-* | head -1` to find the most recent backup
3. Restore it: `cp <that-backup-file> ~/.zshrc && source ~/.zshrc`

If there's no backup, check if TextEdit has a version: File > Revert To > Browse All Versions.

---

*v1.0 — Created for Lab 4: Your First API Key. February 2026.*
