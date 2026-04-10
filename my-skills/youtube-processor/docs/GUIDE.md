# YouTube Processor - Your Video Research Assistant

## The One-Sentence Version

Share a YouTube link, get actionable notes tailored to your coaching business.

## Why This Exists

You come across an interesting YouTube video. Could be a tutorial. Could be an interview. Could be something relevant to your content.

Watching takes 20 minutes. You don't have 20 minutes right now. The video goes in a "watch later" list that you never actually get to.

This skill changes the equation. Share the link, get the summary. In 30 seconds you know whether the video is worth your time — and you've captured the key insights either way.

## One-Time Setup

Before using this skill for the first time, you need to run a quick setup. This takes about 30 seconds and only needs to be done once.

**Open your Terminal** (the same place you launch Claude from).

First, make sure you're in your powerhouse folder. Paste this:

```
cd ~/Documents/my-powerhouse
```

Then run the setup:

```
bash my-skills/youtube-processor/scripts/setup.sh
```

**What success looks like:**

```
YouTube Processor Setup
=======================

Found Python 3.12
Creating environment...
Installing transcript tool...

Setup complete!

You can now use the YouTube Processor skill.
Try saying: 'Summarize this video: [paste any YouTube link]'
```

**If you see "Python 3 is needed":**

You need Python installed. On Mac, paste these two commands one at a time:

First, check if Homebrew is installed:
```
which brew
```

If nothing appears, install Homebrew first (this is safe — it's the standard Mac package manager):
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then install Python:
```
brew install python3
```

After that, run the setup command again.

Then run the setup command again.

**If you see any other error**, paste the full error message to Claude and ask for help.

## How to Use It

Share a YouTube link with any of these:
- "Summarize this video: [URL]"
- "What's this video about?"
- "Turn this into notes"
- "Mine this video for content ideas"

The skill extracts the transcript (most videos have captions), then summarizes based on what you need:

**Quick Summary:** One sentence headline, 3-5 key bullets, main takeaway. Takes 30 seconds to read.

**Detailed Analysis:** Full breakdown with context, action items, and how it connects to your coaching work.

**Content Mining:** The power move. Pulls out hooks, core insights, story beats, and content angles you can use in your newsletters, social posts, or workshops.

## Why It Gets Smarter With Your Context

The skill reads your mission context before summarizing. This means instead of a generic summary, you get insights framed through YOUR lens:

- Instead of "This framework helps businesses scale" → "Here's how [your niche] coaches could use this with [your client avatar]"
- Instead of generic action items → "This connects to your [named framework] — consider adding this as a module"

If you haven't built your mission context yet, the skill still works — it just gives you general coaching-focused summaries. Build your context with `/mission-context-builder` to unlock the personalized layer.

## Key Moments

When the skill processes a video, it identifies 3-5 **Key Moments** — the timestamps where the most important insights happen. Each one includes the timestamp and a brief description, so you can jump straight to the parts that matter.

## What Gets Saved

When you ask to save the notes, they get saved as a markdown file:

```
YT - [Topic] - 2026-01-08.md
```

With the source URL, date, tags, and the full transcript at the bottom for searching later.

If you have an Obsidian vault, it saves there. If not, it creates a `video-notes` folder in your project.

## Content Mining — The Killer Use Case

This is where the skill really earns its keep. Ask Claude to "mine this video for content" and you get:

- **Hook ideas** — opening lines that grab attention
- **Core insight** — the main framework or mental model from the video
- **Story beats** — anecdotes you can retell in your own content
- **Content angles** — specific ways to turn these insights into your newsletters, social posts, or workshop material

Combine with the newsletter-coach skill for a full pipeline: video insights flow straight into article development.

## What It's NOT

This isn't transcription. It uses the existing captions (most videos have them).

This isn't a replacement for actually watching. Some videos need to be watched — visual demos, emotional content, things you want to experience. This is for information extraction.

This isn't magic. If a video has no captions or they're disabled, it can't work.

## The Time Arbitrage

A 20-minute video becomes a 30-second read. That's 40x time savings.

Multiply that across all the videos you might watch in a week. That's hours reclaimed — and you still get the key insights tailored to your coaching business.
