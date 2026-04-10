# Zoom Connect - Guide

## What It Does

Zoom Connect pulls data from your Zoom meetings automatically. Instead of manually checking who attended, downloading recordings one by one, and hunting for chat logs — you run one command and get everything.

## Why It Matters

Every meeting or workshop generates data sitting in Zoom:
- **Who showed up** (and who didn't)
- **How long they stayed** (did they bail early?)
- **What was said in chat** (links shared, questions asked)
- **The recording and transcript** (for session summaries)

Processing this manually takes ~30 minutes after every session. Zoom Connect turns that into a 2-minute command sequence.

## How It Works

After a workshop ends, you wait about 15 minutes (Zoom needs time to process), then:

1. **Find the meeting** — Lists your recent Zoom meetings so you can grab the ID
2. **Pull attendance** — Shows who was there, when they joined, when they left
3. **Download files** — Grabs the transcript, chat log, or full recording

The attendance data gives you a clear picture of engagement. You can use it for follow-up emails, session summaries, or tracking member participation over time.

## What You Can Do With the Data

Zoom Connect gives you the raw data. What you build on top of it is up to you:

- **Post-workshop follow-ups** — Know who attended and who didn't, send targeted follow-ups
- **Session summaries** — Download the transcript and have Claude summarize the key points
- **Engagement tracking** — Track who shows up consistently and who's disengaging
- **Content repurposing** — Pull chat logs for Q&A highlights, transcripts for articles or training materials

## Setup (One-Time)

1. Create a Server-to-Server OAuth app at marketplace.zoom.us
2. Run `scripts/setup.sh` to create the config template
3. Add your credentials to `~/.config/zoom-connect.yaml`
4. Test: `python3 tools/zoom_client.py --test`

See `docs/SETUP-GUIDE.md` for the full step-by-step walkthrough with plain English explanations of each step.

Takes about 15 minutes. After that, it works forever.

## What You Need

- **Zoom Pro plan** (minimum) — for attendance reports and cloud recordings
- **Cloud recording enabled** — so transcripts and chat logs are saved
- **"Save chat messages" enabled** — so chat is included with recordings
- **Python 3** with `requests` and `pyyaml` packages
