# YouTube Processor - Technical Reference

## What It Does

Takes YouTube URLs, extracts transcripts via a local Python tool, and Claude summarizes the content with mission-context awareness. Outputs structured markdown notes ready for your knowledge base.

## Architecture

```
youtube-processor/
├── SKILL.md              # Main skill definition
├── scripts/
│   └── setup.sh          # One-time setup (creates venv, installs dependency)
├── tools/
│   └── get_transcript.py # Transcript extraction (uses youtube-transcript-api)
└── docs/
    ├── README.md         # This file
    ├── GUIDE.md          # Plain English guide with setup instructions
    └── ROADMAP.md        # Version history + future plans
```

## Tools Used

| Tool | Purpose |
|------|---------|
| `Read` | Load mission context, vault notes |
| `Write` | Save output to vault or project root |
| `Edit` | Link from daily note |
| `Bash` | Run Python transcript extraction tool |
| `Glob` | Find mission-context, tool paths, vault location, daily notes |
| `AskUserQuestion` | Clarify summary mode, confirm save location |

## Dependencies

**Python dependency (installed by setup.sh):**
```
youtube-transcript-api
```

No API keys needed. The `youtube-transcript-api` package extracts captions directly from YouTube (they're publicly available on most videos).

## How Transcript Extraction Works

1. SKILL.md uses Glob to find `get_transcript.py` in the skill's tools folder
2. Checks for `.venv/bin/python` in the skill directory
3. Runs: `[venv python] get_transcript.py --url "[URL]" --timestamps --json`
4. Returns JSON with timestamped segments + full transcript text

**If venv not found:** Skill instructs user to run `scripts/setup.sh`

## Summary Modes

| Mode | Output |
|------|--------|
| Quick Summary | Headline, 3-5 bullets, main takeaway |
| Detailed Analysis | Headline, key points with context, action items |
| Content Mining | Hooks, core insight, story beats, content angles |

## Mission-Context Integration

Mission context is loaded at 3 touchpoints:

1. **Phase 1:** Load niche, clients, delivery model, terminology, voice
2. **Phase 4:** Tailor summary through user's coaching lens
3. **Phase 5:** Adapt Mission Relevance section to user's categories

Without mission context, the skill uses generic coaching-focused framing.

## Save Location Logic

Three-tier discovery:

1. **Smart Connections MCP** — If available, save to the vault's Zettelkasten
2. **Glob search** — Check CLAUDE.md FILE LOCATIONS, try common vault paths
3. **Project root** — Fall back to `./video-notes/` directory

Filename format: `YT - [Topic] - YYYY-MM-DD.md`

## Error Handling

| Error | Meaning | Resolution |
|-------|---------|------------|
| Transcripts disabled | Creator turned off captions | Video can't be processed |
| No transcript found | No English captions available | Try a different video |
| Video unavailable | Private, deleted, or age-restricted | Check the URL |
| venv not found | Setup hasn't been run | Run `scripts/setup.sh` |

## Testing Checklist

- [ ] Run with a YouTube URL — transcript extracts successfully
- [ ] Verify Key Moments include timestamps
- [ ] Check summary quality with mission context loaded
- [ ] Check summary quality WITHOUT mission context (generic fallback)
- [ ] Verify save to vault (or project root if no vault)
- [ ] Test error case: invalid URL
- [ ] Test error case: no venv (should prompt setup)
