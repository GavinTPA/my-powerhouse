# GHL Social — Technical Reference

## Architecture

```
ghl-social/
├── SKILL.md                    — Skill instructions and workflow
├── tools/
│   ├── ghl_social_client.py    — Social Planner API client
│   ├── list_accounts.py        — Discover connected platforms
│   ├── schedule_post.py        — Create/schedule posts (with dry-run)
│   └── list_posts.py           — View post queue
├── docs/
│   ├── README.md               — This file
│   ├── GUIDE.md                — Business-friendly guide
│   ├── SETUP-GUIDE.md          — Setup instructions (adds to ghl-connect config)
│   ├── ROADMAP.md              — Shipped + planned
│   └── api-gotchas.md          — API-specific gotchas
└── plans/
```

## Config

Shares config with ghl-connect: `~/.config/ghl-connect.yaml`

No additional configuration needed — same token, same location ID. You just need to add social planner scopes to your existing Private Integration Token.

## API Surface

Base: `https://services.leadconnectorhq.com/social-media-posting/{locationId}/`

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /accounts | List connected social accounts |
| POST | /posts/list | List posts (GET /posts is 404) |
| POST | /posts | Create/schedule a post |
| PUT | /posts/{id} | Update a post |
| DELETE | /posts/{id} | Delete a post |
| GET | /tags | List tags |
| GET | /categories | List categories |
| GET | /statistics | Post performance data |

## Dependencies

- Python 3.x
- `requests` (system Python usually has this)
- `pyyaml` (system Python usually has this)

Install if needed:
```bash
# Mac
pip3 install requests pyyaml

# Windows
pip install requests pyyaml
```

No venv needed — uses only standard packages already available.

## Integration Points

| Skill | How It Connects |
|-------|----------------|
| ghl-connect | Shared config file, same API client patterns |
| substack-publisher | Source content for cross-posting (if installed) |
| ai-slop-detector | Content quality gate before scheduling (if installed) |
