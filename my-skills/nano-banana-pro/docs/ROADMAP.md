# Nano Banana Pro - Roadmap

## Shipped

| Version | Date | What Changed |
|---------|------|--------------|
| v1.0 | 2026-01-16 | Initial release - single image generation with native resolution support |
| v1.1 | 2026-02-17 | Cost tracking — `--costs` flag, CSV log at `~/.config/nano-banana-pro-costs.csv` |
| v1.2 | 2026-02-23 | Member deployment — guided setup flow, `--test` flag, SETUP-GUIDE.md, .zshrc safety protocol |

## Planned

- [ ] **Resolution control (1K/2K/4K)** - Waiting for google-genai SDK to support `image_size` parameter
- [ ] **Newsletter integration** - newsletter-writer pulls this skill for hero images

## Ideas (Not Committed)

- **Multi-image consistency mode** - Chat-based generation for slide decks (may become separate skill)
- **Batch generation** - Generate N variations of same concept for A/B testing
- **Style presets** - If we discover 5+ reusable styles, consider adding flags
- **Image editing** - Use Gemini's edit capabilities for iterative refinement

## What We've Learned

*To be filled in as we use it*

### Prompting Insights
- [Capture what works well]
- [Note what doesn't work]

### Style Discoveries
- [Link to style-library.md entries that perform great]

### Edge Cases
- [Document any quirks or workarounds]
