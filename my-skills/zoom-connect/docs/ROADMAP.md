# Zoom Connect - Roadmap

## Shipped

| Version | Date | What Changed |
|---------|------|--------------|
| v1.5 | 2026-02-18 | Member deployment — generalized docs and examples for any user, created coach-friendly SETUP-GUIDE.md with all 16 scopes documented, fixed scope count inconsistency in setup.sh, deployed to ai-powerhouse-starter |
| v1.4 | 2026-02-17 | Timezone-aware display — `timezone` config per profile, `format_time()` on ZoomClient. All tools show local time (e.g., AEDT) in human output; JSON stays UTC. Fixed `Path("~/...")` tilde expansion bug in download_dir. |
| v1.3 | 2026-02-17 | Multi-account profiles — `--profile bb` / `--profile aip` on all tools. Backward compatible with legacy flat config. |
| v1.2 | 2026-02-16 | Meeting search by topic — `--topic` flag for case-insensitive keyword filtering |
| v1.1 | 2026-02-12 | Granular scopes (Zoom deprecated broad scopes), list_users tool, multi-user account support, PMI meeting support (report endpoint + UUID-based attendance) |
| v1.0 | 2026-02-12 | Initial release — S2S OAuth client, list_meetings, get_attendance, get_recordings, download_recording |

## Planned

- [ ] **Webhook listener** — Subscribe to `recording.completed` for automatic post-meeting triggers
- [ ] **Bulk download** — Download transcript + chat for multiple meetings at once

## Ideas (Not Committed)

- Real-time attendance via `meeting.participant_joined` webhook
- Storage management — track Zoom cloud storage usage, auto-delete after download
- Meeting creation via API (for scheduling workshops programmatically)

## What We've Learned

- (v1.0) Modeled after ghl-connect — same config pattern, same tool CLI structure, same error handling
- S2S OAuth is simpler than GHL's Private Integration Token — just base64 credentials + POST
- Participant consolidation (handling reconnections) is important for accurate headcounts
- (v1.1) Zoom migrated from broad scopes (`meeting:read:admin`) to granular per-endpoint scopes (`meeting:read:list_meetings:admin`). Old broad scopes no longer appear in marketplace UI
- (v1.1) Multi-user accounts (shared team accounts) need `list_users` to discover who hosts meetings — `user_email` in config must match the meeting host
- (v1.1) PMI (Personal Meeting Room) meetings don't show up via the standard meetings endpoint — must use the report endpoint (`/v2/report/users/{}/meetings?type=past`). PMI reuses the same meeting ID, so attendance requires the UUID (unique per session). UUIDs with `/` need double-encoding.
- (v1.3) Multi-account profiles use format detection (`"profiles" in raw_config`) for backward compatibility. Profile name stored on client instance for display. Config migration was manual (one-time task, not worth scripting).
- (v1.3) When replicating an integration, query the working system's OAuth token `scope` field — don't reconstruct from documentation. The reference app had 16 scopes; initial AIP setup only got 8 because scopes were copied from API.md (stale) instead of queried from the working BB token response. Added `--scopes` flag to prevent this recurring.
- (v1.4) `Path("~/Downloads/zoom-recordings")` does NOT expand tilde — creates a literal `~/` directory. Must use `.expanduser()`. Python stdlib gotcha.
- (v1.4) `zoneinfo.ZoneInfo` (stdlib 3.9+) is the cleanest way to convert Zoom UTC timestamps to local time. `datetime.fromisoformat(s.replace("Z", "+00:00"))` handles Zoom's ISO format.
