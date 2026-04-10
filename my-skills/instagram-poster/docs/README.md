# Instagram Poster — Technical Reference

**macOS only.** Not supported on Windows.

## Architecture

Posts carousels and Reels to Instagram via the Meta Graph API. Handles image upload staging (Vercel Blob), container creation, and publishing.

## Dependencies

- Vercel Blob (temporary image staging)
- Meta Graph API (Instagram publishing)
- OAuth long-lived token (60-day expiry, auto-refreshes with regular use)

## Tools

| Tool | Purpose |
|------|---------|
| `tools/post_carousel.py` | Upload and publish carousel posts |
| `tools/post_reel.py` | Upload and publish Reels |
| `tools/auth_setup.py` | OAuth authorization flow |
| `tools/refresh_token.py` | Manual token refresh |
| `tools/token_utils.py` | Shared token management utilities |

## Configuration

Credentials stored as environment variables in `~/.zshrc`:
- `META_APP_ID` — Meta Developer App ID
- `META_APP_SECRET` — Meta Developer App Secret
- `BLOB_READ_WRITE_TOKEN` — Vercel Blob storage token

OAuth token stored in `~/.config/instagram-poster.yaml`.

## Token Lifecycle

- Initial authorization creates a 60-day long-lived token
- Regular posting auto-refreshes the token
- If expired, run `set up instagram poster` to re-authorize
- Manual refresh: `python3 my-skills/instagram-poster/tools/refresh_token.py`

## Cost

Free (Meta Graph API and Vercel Blob free tier).
