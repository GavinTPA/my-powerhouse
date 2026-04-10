# Zoom Connect - Technical Reference

## Architecture

```
skills/zoom-connect/
├── SKILL.md                    # Skill instructions (Claude reads this)
├── tools/
│   ├── zoom_client.py          # S2S OAuth client, rate limiting, error handling
│   ├── list_meetings.py        # Find meetings by date range
│   ├── get_attendance.py       # Participants + join/leave times
│   ├── get_recordings.py       # List recording files for a meeting
│   └── download_recording.py   # Download specific files to local storage
├── scripts/
│   └── setup.sh                # Creates ~/.config/zoom-connect.yaml template
├── references/
│   └── API.md                  # Zoom endpoints, response formats, gotchas
└── docs/
    ├── README.md               # This file
    ├── GUIDE.md                # Business-friendly guide
    ├── ROADMAP.md              # Version history + future plans
    └── plans/                  # Improvement plans
```

## Dependencies

- Python 3.x (system Python is fine)
- `requests` (HTTP client)
- `pyyaml` (config loading)

No ML dependencies, no venv needed.

## Configuration

Config: `~/.config/zoom-connect.yaml`

| Field | Required | Description |
|-------|----------|-------------|
| `account_id` | Yes | From S2S OAuth app |
| `client_id` | Yes | From S2S OAuth app |
| `client_secret` | Yes | From S2S OAuth app |
| `user_email` | No | Default: "me" |
| `download_dir` | No | Default: ~/Downloads/zoom-recordings |

## Authentication Flow

1. Client reads credentials from config
2. Base64-encodes `client_id:client_secret`
3. POSTs to `https://zoom.us/oauth/token` with `account_credentials` grant
4. Token cached in memory, refreshed when expired (1hr TTL, refreshed 5min early)
5. Token passed as Bearer header for API calls, query param for downloads

## Tool Design

All tools follow the same pattern:
- Standalone CLI with argparse
- Import `zoom_client.py` via sys.path
- Support `--json` for programmatic output
- Human-readable default output
- Clear error messages with actionable suggestions

## Integration

This skill provides raw Zoom data via its Python tools. Other skills or scripts can import these tools to build automated post-meeting pipelines (session summaries, attendance tracking, follow-up workflows).
