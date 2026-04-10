---
name: zoom-connect
description: Pull Zoom meeting data — attendance, recordings, transcripts, chat logs. Use when "check zoom attendance", "zoom recordings", "download zoom transcript", "who attended the meeting", "zoom-connect", "pull zoom data".
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Zoom Connect

Connect Claude Code to the Zoom REST API via Server-to-Server OAuth. Pull attendance, list recordings, download transcripts and chat logs — all from the terminal.

---

## Quick Reference

| Task | Command |
|------|---------|
| List recent meetings | `python3 tools/list_meetings.py` |
| List meetings (specific account) | `python3 tools/list_meetings.py --profile secondary` |
| List meetings for user | `python3 tools/list_meetings.py --user <email>` |
| Get attendance | `python3 tools/get_attendance.py --meeting-id <id>` |
| Get attendance (PMI) | `python3 tools/get_attendance.py --uuid <uuid>` |
| List recordings | `python3 tools/get_recordings.py --meeting-id <id>` |
| Download transcript | `python3 tools/download_recording.py --meeting-id <id> --type TRANSCRIPT` |
| Download chat log | `python3 tools/download_recording.py --meeting-id <id> --type CHAT` |
| Download everything | `python3 tools/download_recording.py --meeting-id <id> --all` |
| List account users | `python3 tools/list_users.py` |
| Test connection | `python3 tools/zoom_client.py --test` |
| Test specific profile | `python3 tools/zoom_client.py --test --profile main` |

All commands are in: `skills/zoom-connect/tools/`

All tools accept `--profile <name>` to select which Zoom account to use.

---

## Workflow: Post-Workshop Data Pull

After a meeting ends (~15 minutes wait for data):

1. Find the meeting: `python3 tools/list_meetings.py --profile <profile> --from <date>`
2. Note the **UUID** from the output (required for PMI meetings — meeting ID alone is ambiguous)
3. Get who attended: `python3 tools/get_attendance.py --profile <profile> --uuid <uuid> --include-email`
4. List recordings: `python3 tools/get_recordings.py --profile <profile> --meeting-id <id>`
5. Download transcript + chat: `python3 tools/download_recording.py --profile <profile> --meeting-id <id> --type TRANSCRIPT` and `--type CHAT`

Present attendance summary to the user.

**PMI note:** If your meetings use a Personal Meeting Room, which reuses the same meeting ID for every session, always use the UUID (unique per session) for attendance lookups.

---

## Workflow: Find a Past Meeting

When asked about a past meeting:

1. List meetings in date range: `python3 tools/list_meetings.py --from 2026-02-01 --to 2026-02-12`
2. Identify the correct meeting by topic
3. Use the meeting ID for attendance or recording tools

---

## Workflow: Shared Zoom Account

When a Zoom account has multiple users (e.g., a shared team account), meetings may be hosted by a different user than the one in `user_email`. If `list_meetings` returns 0 results:

1. List all users: `python3 tools/list_users.py`
2. Identify who hosts meetings (look for Licensed users)
3. Query that user directly: `python3 tools/list_meetings.py --user their@email.com`

---

## Multi-Account Profiles

Config file: `~/.config/zoom-connect.yaml`

The config supports named profiles for multiple Zoom accounts:

```yaml
default_profile: "main"

profiles:
  main:
    account_id: "..."
    client_id: "..."
    client_secret: "..."
    user_email: "me"
    download_dir: "~/Downloads/zoom-recordings"
    timezone: "Australia/Melbourne"

  # Add more profiles for additional Zoom accounts:
  # secondary:
  #   account_id: "..."
  #   client_id: "..."
  #   client_secret: "..."
  #   user_email: "other@email.com"
  #   download_dir: "~/Downloads/zoom-recordings"
  #   timezone: "US/Eastern"
```

**Usage:**
- No `--profile` flag → uses `default_profile` from config
- `--profile main` → your primary Zoom account
- `--profile secondary` → additional Zoom accounts

**Backward compatible:** Legacy flat configs (no `profiles:` key) still work.

### For Claude Code

When asked about Zoom data, use the default profile unless the user specifies otherwise. If they have multiple profiles configured, ask which account to use.

---

## Configuration Setup

Run `scripts/setup.sh` to create the config template, then add your S2S OAuth credentials from marketplace.zoom.us.

Required per profile:
- Account ID
- Client ID
- Client Secret

Required Zoom app scopes (all 16 granular scopes are required for full functionality):

**Meeting scopes:**
- `meeting:read:list_meetings:admin`
- `meeting:read:list_meetings:master`
- `meeting:read:meeting:admin`
- `meeting:read:past_meeting:admin`

**Report scopes:**
- `report:read:list_meeting_participants:admin`
- `report:read:user:admin`
- `report:read:chat_session:admin`
- `report:read:list_chat_sessions:admin`

**Cloud recording scopes:**
- `cloud_recording:read:list_recording_files:admin`
- `cloud_recording:read:recording:admin`
- `cloud_recording:read:list_account_recordings:admin`
- `cloud_recording:read:recording_analytics_details:admin`
- `cloud_recording:read:recording_analytics_summary:admin`
- `cloud_recording:read:registrant_status:admin`

**User scopes:**
- `user:read:list_users:admin`
- `user:read:user:admin`

Verify with: `python3 tools/zoom_client.py --scopes --profile <name>`

Minimum Zoom plan: **Pro** (for attendance reports and cloud recordings).

---

## Data Availability

| Data | Available After | Retention |
|------|----------------|-----------|
| Attendance (participants) | ~15 min after meeting ends | 1 month |
| Cloud recordings | Processing time varies (1hr+ for video) | Until deleted |
| Chat logs | With cloud recording | Until deleted |
| Transcripts (VTT) | With cloud recording | Until deleted |

---

## Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Rate limit API calls (0.05s) | Download video files (large) | Delete recordings from Zoom |
| Show data availability warnings | Share attendance data externally | Expose OAuth credentials in output |
| Consolidate reconnection entries | Download all files for a meeting | Modify Zoom settings via API |
| Present attendance summary to the user | | Auto-process without user review |

---

## Gotchas

| Issue | Detail |
|-------|--------|
| Email missing | Participant wasn't signed into Zoom — shows as "(not signed in)" |
| Duplicate entries | Reconnecting creates separate entries — tool consolidates them automatically |
| No data yet | Attendance data takes ~15 min after meeting ends |
| Recording processing | Video may take 1+ hours — transcript and chat are faster |
| Report expiry | Attendance report data expires after 1 month |
| PMI meetings | Personal Meeting Rooms reuse the same meeting ID — use `--uuid` for attendance |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| "Config file not found" | Run `scripts/setup.sh` then edit `~/.config/zoom-connect.yaml` |
| "OAuth token request failed" | Check Account ID, Client ID, Client Secret in config |
| "Resource not found" | Meeting may not have ended yet, or ID is wrong |
| "Rate limited" | Wait and retry (shouldn't happen at normal usage) |
| No recordings listed | Cloud recording may not be enabled, or still processing |
| Plan warning | Attendance reports require Zoom Pro or higher |
