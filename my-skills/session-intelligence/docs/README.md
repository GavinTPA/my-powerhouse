# Session Intelligence — Technical Reference

## What It Does

Analyzes Zoom session data (attendance, chat, transcript) and produces two coaching intelligence documents:

1. **Training Summary** — Session-level coaching brief (overview, flow, Q&A, takeaways)
2. **Attendee Detail** — Per-person chat responses mapped to trainer prompts, with coaching notes

## Architecture

```
zoom-connect (data pull)
    ├── attendance → participant list, time on call
    ├── chat log → parse_chat.py → prompt detection + person index
    └── transcript → session flow context (optional)
         ↓
mission-context (business vocabulary)
         ↓
Claude generates both documents
         ↓
Zettelkasten (save + daily note link)
```

## Tools

| Tool | Purpose | CLI |
|------|---------|-----|
| `tools/parse_chat.py` | Chat analysis engine — prompt detection, person indexing | `--file <chat.txt> --hosts "Name1,Name2" [--json]` |

### parse_chat.py Options

| Flag | Default | Description |
|------|---------|-------------|
| `--file` | (required) | Path to Zoom chat file |
| `--hosts` | (required) | Comma-separated trainer/host names |
| `--burst-threshold` | 5 | Minimum unique responders to detect a prompt |
| `--window-secs` | 180 | Response window in seconds |
| `--json` | false | Output full analysis as JSON |

### Prompt Detection Algorithm

1. Parse all chat messages with timestamps and sender names
2. Identify host/trainer messages (from `--hosts` list)
3. Filter noise: skip reactions ("Reacted to..."), reply-quotes ("Replying to..."), emoji-only
4. For each host message to Everyone: count unique non-host responders within `window_secs`
5. If unique responders >= `burst_threshold`, mark as prompt candidate
6. Deduplicate: cluster candidates within 60s, keep highest responder count
7. Auto-generate prompt codes (WIN, LES, GAP, etc.) from message content
8. Resolve overlapping windows so each prompt has a distinct time range

### Prompt Code Detection

The engine auto-generates codes from message content using keyword patterns:

| Code | Detected When Message Contains |
|------|-------------------------------|
| WIN | "win" |
| LES | "lesson", "learned", "learning" |
| TAW | "tweak" |
| RES | "resonat..." |
| CLI | "client" + "how many" |
| REV | "revenue", "income", "how much" |
| F/P | "free" + "paid", "type 1/type 2" |
| RHT | "relieved", "happy", "thrilled" |
| GAP | "gap", "concern", "worry", "challenge" |
| BEST | "best thing", "takeaway", "biggest thing" |
| P{N} | Fallback — numbered sequentially |

## Dependencies

- **zoom-connect** — Provides attendance, chat, and transcript data
- **mission-context** — Provides business vocabulary for coaching notes
- **Python 3.9+** — For parse_chat.py (no external packages required)

## Output

Two markdown files saved to Zettelkasten:
- `[Session Name] - Training Summary - YYYY-MM-DD.md`
- `[Session Name] - Attendee Detail - YYYY-MM-DD.md`

Cross-linked via wikilinks. Linked from daily note Captures section.

## Testing

```bash
# Test parse_chat.py with a real chat file
python3 tools/parse_chat.py --file ~/Downloads/zoom-recordings/some-chat.txt --hosts "Trainer Name"

# Test with JSON output for full analysis
python3 tools/parse_chat.py --file ~/Downloads/zoom-recordings/some-chat.txt --hosts "Trainer Name" --json

# Test with lower threshold for small sessions
python3 tools/parse_chat.py --file ~/Downloads/zoom-recordings/some-chat.txt --hosts "Trainer Name" --burst-threshold 3
```
