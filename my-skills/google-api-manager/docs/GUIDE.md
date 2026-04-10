# Google API Manager — How It Works

## The One-Sentence Version

Manage your team's Google API keys by telling Claude what you want — no gcloud commands, no Googling syntax, no typos.

## Why This Exists

The Teams Edition guide gives you 6 commands to run per team member. That's fine once. But when you're adding 5 people, or revoking someone who left, or checking who's spending what — you don't want to be copy-pasting gcloud commands and swapping variables.

This skill absorbs the complexity. You say "add Sarah Jones" and Claude handles the rest. Same commands, zero friction.

## How You Use It

### First Time (5 minutes, once)

Tell Claude: **"set up google api manager"**

Claude checks if gcloud is installed, walks you through signing in, finds your billing account, and asks for a project prefix (like "ww" for Workshop Whisperer). Saves everything to a config file. Done.

### Adding Someone (30 seconds each)

Tell Claude: **"add team member Sarah Jones"**

Claude creates their project, links billing, enables the API, creates a restricted key, sets a budget alert, and hands you the key string. Send it to Sarah. She types "set up nano banana pro" in her Powerhouse and pastes the key.

### Checking In

- **"show my team"** — See everyone, their status, when they were added
- **"check team spending"** — Budget alert status per person
- **"revoke Sarah Jones"** — Claude asks: disable (reversible), delete key, or delete project?

## What Your Team Members See

Nothing about Google Cloud. They get a key from you, paste it into Claude Code, and start generating images. They don't need a Google account, don't need billing, don't need terminal skills. You handled all of that.

## What It Costs

Nothing extra. Same per-image pricing as individual keys (~$0.13/image). The Google Cloud projects, CLI, budget alerts, and this skill are all free. The only cost is the images your team generates.
