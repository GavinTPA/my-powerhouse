# Zoom API Reference

Quick reference for endpoints used by zoom-connect tools.

## Authentication

**Server-to-Server OAuth** (S2S) — no user interaction needed.

```
POST https://zoom.us/oauth/token
Authorization: Basic base64(client_id:client_secret)
Content-Type: application/x-www-form-urlencoded

grant_type=account_credentials&account_id=YOUR_ACCOUNT_ID
```

Returns: `{"access_token": "...", "token_type": "bearer", "expires_in": 3600}`

Token expires in 1 hour. Request fresh each run.

---

## Endpoints

### List Meetings (Upcoming)
```
GET /v2/users/{userId}/meetings
  ?type=upcoming
  ?page_size=300
```

Pagination: `next_page_token` in response.

### List Past Meetings (Report)
```
GET /v2/report/users/{userId}/meetings
  ?type=past
  ?from=YYYY-MM-DD
  ?to=YYYY-MM-DD
  ?page_size=300
```

Returns ALL past meetings including PMI (Personal Meeting Room) sessions. The standard `/v2/users/{}/meetings?type=previous_meetings` endpoint does NOT reliably return PMI meetings.

Pagination: `next_page_token` in response.

**Required scope:** `report:read:user:admin` (may need to be added alongside existing scopes).

### Meeting Details (Past)
```
GET /v2/past_meetings/{meetingId}
```

Returns: topic, start_time, end_time, duration, participants_count.

### Attendance (Participants Report)
```
GET /v2/report/meetings/{meetingId}/participants
  ?page_size=300
```

Returns per participant: name, user_email, join_time, leave_time, duration.

**Requires:** Pro plan. Data available ~15 min after meeting ends. Expires after 1 month.

**Gotcha:** email only present if participant signed into Zoom. Reconnections create separate entries.

### Recordings
```
GET /v2/meetings/{meetingId}/recordings
```

Returns: recording_files array with file_type, file_size, download_url, status.

File types: MP4, M4A, CHAT, TRANSCRIPT, TIMELINE, CC.

### Download Recording File

Use the `download_url` from recordings response + access token:

```
GET {download_url}?access_token={token}
```

Or with Authorization header.

### List Users
```
GET /v2/users
  ?status=active|inactive|pending
  ?page_size=300
```

Returns per user: id, email, first_name, last_name, type (1=Basic, 2=Licensed), status.

Pagination: `next_page_token` in response.

---

## Rate Limits

| Category | Limit |
|----------|-------|
| Light (list, get) | 80 req/sec |
| Medium (user ops) | 60 req/sec |
| Heavy (recordings, reports) | 40 req/sec + 60K/day |

Our usage: ~5-10 calls per workshop. Non-issue.

---

## Required Scopes (16 Granular)

Authoritative source: `python3 tools/zoom_client.py --scopes --profile <name>`

| Scope | For |
|-------|-----|
| `meeting:read:list_meetings:admin` | List meetings (upcoming) |
| `meeting:read:list_meetings:master` | Master-level meeting list access |
| `meeting:read:meeting:admin` | Meeting details |
| `meeting:read:past_meeting:admin` | Past meeting details (attendance) |
| `report:read:list_meeting_participants:admin` | Participant reports (attendance) |
| `report:read:user:admin` | Past meetings via report endpoint |
| `report:read:chat_session:admin` | Chat session reports |
| `report:read:list_chat_sessions:admin` | List chat sessions |
| `cloud_recording:read:list_recording_files:admin` | List recording files |
| `cloud_recording:read:recording:admin` | Download recording files |
| `cloud_recording:read:list_account_recordings:admin` | Account-level recording list |
| `cloud_recording:read:recording_analytics_details:admin` | Recording analytics |
| `cloud_recording:read:recording_analytics_summary:admin` | Recording analytics summary |
| `cloud_recording:read:registrant_status:admin` | Recording registrant data |
| `user:read:list_users:admin` | List account users |
| `user:read:user:admin` | Get current user info (/v2/users/me) |

---

## Personal Meeting Rooms (PMI)

PMI meetings reuse the same meeting ID for every session. To distinguish sessions:

- Use the **UUID** (unique per session) instead of the meeting ID
- UUIDs containing `/` must be **double URL-encoded**: `/` → `%2F` → `%252F`
- The report endpoint (`/v2/report/users/{}/meetings?type=past`) returns PMI sessions; the standard meetings endpoint may not

**Double-encoding example:**
```
UUID: abc/def==
Encoded: abc%252Fdef%3D%3D
```

Both `/v2/past_meetings/{uuid}` and `/v2/report/meetings/{uuid}/participants` accept UUIDs in place of meeting IDs.

---

## Sources

- [Zoom API Reference](https://developers.zoom.us/docs/api/rest/reference/zoom-api/methods/)
- [S2S OAuth Docs](https://developers.zoom.us/docs/internal-apps/s2s-oauth/)
- [Rate Limits](https://developers.zoom.us/docs/api/rate-limits/)
