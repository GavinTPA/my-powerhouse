# GHL Social — Roadmap

## Shipped

### v0.1 — MVP (2026-03-09)
- Social Planner API client (`ghl_social_client.py`)
- Account discovery (`list_accounts.py`)
- Post scheduling with dry-run (`schedule_post.py`)
- Post listing (`list_posts.py`)
- SKILL.md with full workflow
- Token verified working with Social Planner endpoints
- Connected: Facebook, Instagram, Threads, LinkedIn, YouTube

### v0.1.1 — Carousel Support (2026-03-10)
- Platform-specific detail objects (instagramPostDetails, facebookPostDetails, linkedinPostDetails, youtubePostDetails)
- `--post-type` flag (post/story/reel) in schedule_post.py
- `--pdf-carousel` and `--pdf-title` flags for LinkedIn PDF carousels
- Instagram carousel preview detection in dry run
- Documented "No Carousel Type" pattern in api-gotchas.md
- Added API research escalation rule to api-integrations.md
- **Verified:** First Instagram carousel scheduled via API (8-slide Greenline on-ramp)

## Planned

### v0.2 — Content Adaptation
- Platform-specific content adaptation from source article
- ai-slop-detector integration
- mission-context voice matching
- One article → LinkedIn + Facebook + Instagram + Threads versions

### v0.3 — Content Calendar & Bulk Upload
- Weekly content calendar format (markdown or YAML)
- Bulk scheduling from calendar
- CSV upload support (GHL supports 90 posts per CSV)
- MBA-style content planning workflow

### v0.4 — Measurement
- Statistics retrieval (`get_stats.py`)
- Weekly performance report
- Cross-platform comparison (same content, different results)
- Top performer surfacing

### v0.5 — Learning Loop
- Pattern detection (topics, formats, times)
- Data-driven content calendar recommendations
- A/B testing framework

### v1.0 — X + Medium Integration
- X article posting via X API
- Medium publishing via Medium API
- Canonical URL management
- Unified scheduling across all platforms

## Research Queue
- Facebook professional mode / personal profile posting via API
- GHL Phase 2+ API features (stats, CSV-via-API, RSS)
- Platform-specific optimal posting times from data
