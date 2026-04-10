# google-api-manager — Roadmap

## Shipped

| Version | Date | What Changed |
|---------|------|--------------|
| v1.0 | 2026-02-24 | Initial release — setup wizard, add/list/revoke members, budget checking |

## Planned

- [ ] `--re-enable` flag for revoke_member.py (currently manual gcloud command)
- [ ] Export team roster to markdown (for Zettelkasten archiving)
- [ ] Batch add members from a list (CSV or names)

## Ideas (Not Committed)

- Multi-API support (not just image generation — could enable other APIs per member)
- Google Cloud Python client library as alternative to subprocess gcloud (if CLI proves flaky cross-platform)
- Integration with ghl-connect to auto-send key to member via GHL email
- Dashboard view of actual spend (requires Google Cloud Billing API, more complex than CLI)

## What We've Learned

- gcloud API key commands were promoted from alpha to GA recently — stable enough for production use
- Budget alerts are email-only. No hard spending caps without custom Pub/Sub automation. This is fine for coaching teams.
- Project IDs must be globally unique across all of Google Cloud — the prefix pattern (ww-sarah-jones) helps, but collisions are possible. Tool auto-appends numbers as fallback.
