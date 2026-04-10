# YouTube Processor - Roadmap

## What's Shipped

| Version | Date | What Changed |
|---------|------|--------------|
| v1.0 | 2026-01-02 | Initial build with transcript extraction |
| v1.1 | 2026-01-03 | Added alternative transcript extraction method |
| v1.2 | 2026-01-08 | Added docs/ folder (README, GUIDE, ROADMAP) |
| v1.3 | 2026-01-24 | Timestamp extraction — `--timestamps` flag, Key Moments section |
| v2.0 | 2026-02-17 | Member-ready release — mission-context integration, portable paths, setup.sh, content mining mode |

## v2.0 Changes (Member-Ready)

- Rewrote SKILL.md following the member-ready skill pattern (mission-context at 3 touchpoints)
- Portable tool paths via Glob discovery (no hardcoded paths)
- Added `scripts/setup.sh` for one-time member setup
- "Content Mining" mode replaces newsletter-specific mining
- Three-tier save location discovery (vault -> Glob -> project root)
- Portable shebang in `get_transcript.py`
- Plain English GUIDE.md with copy-paste setup instructions

## Planned Improvements

- [ ] **Batch Processing** — Process multiple URLs at once. "Summarize these 5 videos" gives individual summaries plus cross-video synthesis.

- [ ] **Content Coach Integration** — One-click handoff from video summary to newsletter development. Video insights flow into article drafts.

## Ideas (Not Committed)

- **Video Library** — Track all processed videos. "What videos have I processed about X?"
- **Playlist Processing** — Process all videos in a YouTube playlist, synthesize themes
- **Speaker Identification** — For interviews, separate host questions from guest insights
- **Quote Extraction** — Pull the most quotable moments for social or content
- **Comparison Mode** — "Compare these two videos on the same topic"

## What We've Learned

**youtube-transcript-api just works.** No API keys needed. Most videos have auto-generated English captions. Extraction takes 3-5 seconds.

**Claude summarizing beats API summarizing.** Having Claude do the summarization means it can use your mission context — your terminology, your audience, your content style.

**Content mining is the killer use case.** Quick summary is useful. Pulling out hooks, story beats, and angles for your content — that's where the real value is.

**Save the transcript.** Even after summarizing, keep the full transcript. You'll want to search it later or quote specific parts.
