# Instagram Carousel — Technical Reference

**macOS only.** Not supported on Windows.

## Architecture

This is an **agent-based** skill — the first agent in the starter repo. The agent at `.claude/agents/instagram-carousel.md` orchestrates the skill resources at `my-skills/instagram-carousel/`.

## Pipeline

13 phases from article input to posted carousel:
- **Phases 1-12:** Produce text + image prompts (no API calls needed)
- **Phase 13:** Generates images via Gemini API (requires GOOGLE_API_KEY)

## Dependencies

- hook-stack-evaluator (auto-evaluates hooks)
- ai-slop-detector (cleans caption copy)
- nano-banana-pro (provides GOOGLE_API_KEY setup)
- mission-context (audience detection, vault path)

## Tools

`tools/generate_images.py` — Batch image generation using Gemini chat mode for character consistency across all slides.

| Flag | Purpose |
|------|---------|
| `--me` | Use your reference photo from `assets/my-reference.jpeg` |
| `--name` | Base name for files (e.g., `Bonsai` → `Bonsai01.png`) |
| `--reference <path>` | Custom reference image |
| `--logo <path>` | Brand logo for all slides |
| `--aspect carousel\|reel` | 4:5 (default) or 9:16 |

## Style System

`resources/my-styles.md` stores visual styles. The agent reads the style marked `default: true` and injects it into Phase 8 image prompts. Members can add custom styles or set a different default.

## Resource Files

| File | Purpose |
|------|---------|
| `visual-metaphors.md` | Visual storytelling inspiration |
| `secondary-characters.md` | Character roster |
| `carousel-formats.md` | Slide structure templates |
| `prompt-templates.md` | Creative Director Framework |
| `my-styles.md` | Visual style library |
| `manga-style-guide.md` | Example detailed style guide |

## Cost

~$0.134/image, ~$1.07 per 8-slide carousel (Gemini API).
