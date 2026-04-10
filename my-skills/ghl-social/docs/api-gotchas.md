# GHL Social Planner — API Gotchas

## Endpoint Path Gotchas

### GET /posts Does Not Exist
Listing posts requires `POST /posts/list` with a body. `GET /posts` returns 404.

### Account Discovery Path
Connected accounts are at `GET /accounts` (flat endpoint).
NOT at `/oauth/{platform}/accounts` or `/oauth/{platform}/accounts/{locationId}`.

### locationId in Body Not Allowed
For `POST /posts/list`, do NOT include `locationId` in the request body — it's already in the URL path. Including it returns 422: "property locationId should not exist".

## Create Post — Correct Field Names (Confirmed 2026-03-09)

The GHL docs (Stoplight/Marketplace) are JS-rendered and incomplete. These field names were confirmed via trial and error against the live API:

| Field | Correct Name | Wrong Names (422) |
|-------|-------------|-------------------|
| Post type | `type` ("post", "story", "reel") | — |
| User ID | `userId` (use locationId value) | — |
| Schedule time | `scheduleDate` (ISO 8601) | `scheduleAt`, `scheduledAt`, `publishAt`, `schedule`, `scheduledDate`, `publishDate`, `postDate`, `publishTime`, `displayDate` |
| Media | `media` (array of objects) | `mediaUrls` (array of strings) |
| Media object | `{"url": "...", "type": "image/png"}` | `{"url": "...", "format": "image"}`, `{"url": "...", "type": "image"}` |

### Scheduling Requires Explicit Status

Setting `scheduleDate` alone publishes immediately. You MUST also set `"status": "scheduled"` for the post to be held until the scheduled time.

```json
{
  "accountIds": ["..."],
  "summary": "Post text",
  "type": "post",
  "media": [{"url": "https://...", "type": "image/png"}],
  "userId": "LOCATION_ID",
  "scheduleDate": "2026-03-11T05:00:00+11:00",
  "status": "scheduled"
}
```

### Platform Field in List Response Is Misleading

`POST /posts/list` returns a `platform` field that may show "google" even for LinkedIn posts. The `accountIds` array is what determines the actual destination. Ignore the `platform` field — check `accountIds` against the accounts list.

### Delete Is Soft-Delete in List

`DELETE /posts/{id}` returns 200 success, but the post may still appear in `POST /posts/list` results. Posts that published before deletion remain live on the platform — API delete only removes from GHL's queue.

### Post IDs

The post ID in the create response comes back in `results.post._id`. The `id` field may be absent. Use `_id` consistently.

## Carousel Posts — No Carousel Type (Confirmed 2026-03-10)

There is no `type: "carousel"`. Instagram carousels are created by using `type: "post"` with multiple images in the `media` array.

### Platform-Specific Carousel Behavior

| Platform | How Carousels Work | Max Items | Format |
|----------|-------------------|-----------|--------|
| Instagram | `type: "post"` + multiple media objects | 10 images | JPEG, PNG only |
| LinkedIn | `linkedinPostDetails.postAsPdf: true` + `pdfTitle` | 300 pages, 100MB PDF | PDF only |
| Facebook | `type: "post"` + multiple media objects | 10 recommended | JPEG, PNG, GIF |

### Instagram Carousel Example

```json
{
  "accountIds": ["instagram-account-id"],
  "summary": "Caption with hashtags",
  "type": "post",
  "media": [
    {"url": "https://cdn.example.com/slide1.jpg", "type": "image/jpeg"},
    {"url": "https://cdn.example.com/slide2.jpg", "type": "image/jpeg"},
    {"url": "https://cdn.example.com/slide3.jpg", "type": "image/jpeg"}
  ],
  "instagramPostDetails": {"type": "post"},
  "userId": "LOCATION_ID",
  "scheduleDate": "2026-03-11T05:00:00+11:00",
  "status": "scheduled"
}
```

### LinkedIn PDF Carousel Example

```json
{
  "accountIds": ["linkedin-account-id"],
  "summary": "Post text",
  "type": "post",
  "media": [{"url": "https://cdn.example.com/carousel.pdf", "type": "application/pdf"}],
  "linkedinPostDetails": {"postAsPdf": true, "pdfTitle": "Carousel Title"},
  "userId": "LOCATION_ID",
  "status": "scheduled"
}
```

### Instagram Constraints

- Media is REQUIRED for all Instagram posts (text-only not supported)
- Images: JPEG, PNG only (no GIF, no WebP)
- Max 30 hashtags in caption
- Stories: captions NOT supported, JPEG only
- Reels: exactly 1 video required
- Aspect ratio: 4:5 to 1.91:1

### Platform-Specific Detail Objects (Optional, Backward Compatible)

The API supports per-platform customization via optional objects:
- `instagramPostDetails: { type, collaborators, showOnFeed }`
- `facebookPostDetails: { type }`
- `linkedinPostDetails: { postAsPdf, pdfTitle }`
- `youtubePostDetails: { type, title, privacyLevel }`

When omitted, the top-level `type` field serves as default.

**Source:** [GHL Marketplace API - Create Post](https://marketplace.gohighlevel.com/docs/ghl/social-planner/create-post/index.html), confirmed via Chrome (JS-rendered docs).

## Authentication

### Private Integration Token Works
Confirmed 2026-03-09: Private Integration Tokens (`pit-*`) work with all Social Planner endpoints. No OAuth2 Marketplace app needed for single-user use.

### Sub-Account Scope Required
Agency-level tokens reportedly don't work for post creation. Sub-Account scoped tokens work fine.

## Token Expiry

| Platform | Expiry | Auto-Refresh |
|----------|--------|-------------|
| Facebook | ~60 days | No — reconnect in GHL |
| Instagram | ~60 days | No — reconnect in GHL |
| Threads | ~60 days | No — reconnect in GHL |
| LinkedIn | ~60 days | No — reconnect in GHL |
| YouTube | Short-lived | Yes — auto-refreshes |

Check expiry with `list_accounts.py`. If `isExpired: true`, reconnect in GHL dashboard.

## Platform Removals

### X/Twitter — Removed December 2024
GHL removed X integration entirely. X charged $504K/year for enterprise API access. No timeline for return. Use X API directly.

### Medium — Never Supported
Zero GHL integration for Medium. Use Medium's own API (`api.medium.com`).

## Rate Limits
- Burst: 100 requests per 10 seconds
- Daily: 200,000 requests per day
- Platform-specific limits apply on top (e.g., Instagram 25 posts/day, LinkedIn 200/day)

## Version Header
`Version: 2021-07-28` works for all Social Planner endpoints. Same as Conversations API.
