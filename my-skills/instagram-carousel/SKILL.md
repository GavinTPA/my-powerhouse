---
name: instagram-carousel
description: Carousel creation resources and setup. The instagram-carousel AGENT handles carousel creation — say "create a carousel". This skill provides setup, resources, and image generation tools. Use when "set up instagram carousel", "set up carousel", "configure carousel", "set up my carousel reference photo".
allowed-tools: Read, Write, Edit, Bash, Glob, AskUserQuestion
---

# Instagram Carousel

This skill provides resources and tools for the instagram-carousel agent. The agent handles the full pipeline — say "create a carousel from [article/topic]" to invoke it.

**macOS only.** This skill is not supported on Windows.

## Resources

The agent loads these during carousel creation:
- `resources/visual-metaphors.md` — Visual storytelling inspiration
- `resources/secondary-characters.md` — Character roster for emotional amplification
- `resources/carousel-formats.md` — Slide structure templates
- `resources/prompt-templates.md` — Creative Director Framework for image prompts
- `resources/my-styles.md` — Your visual style library
- `resources/manga-style-guide.md` — Example detailed style guide

## Image Generation Tool

The batch image generator at `my-skills/instagram-carousel/tools/generate_images.py` uses Gemini chat mode for character consistency across all slides.

```bash
source ~/.zshrc && python3 my-skills/instagram-carousel/tools/generate_images.py \
  <prompts_json> <output_dir> \
  --me \
  --name <CarouselName>
```

**Flags:**
- `--me`: Uses your reference image at `my-skills/instagram-carousel/assets/my-reference.jpeg`
- `--name`: Sets file naming (e.g., `Bonsai` → `Bonsai01.png`, `Bonsai02.png`)
- `--reference <path>`: Use a specific reference image instead
- `--logo <path>`: Include a brand logo in all slides
- `--aspect carousel|reel`: Carousel (4:5, default) or Reel (9:16)

---

## Setup Wizard

**Trigger:** "set up instagram carousel", "set up carousel", "configure carousel"

### Step 1: Check Prerequisites

Verify GOOGLE_API_KEY exists:
```bash
echo $GOOGLE_API_KEY | head -c 4
```

If empty, direct the member to nano-banana-pro setup: "Run: set up nano banana pro"

Verify google-genai is installed:
```bash
python3 -c "from google import genai; print('OK')"
```

If it fails, install it: `pip3 install google-genai Pillow`

### Step 2: Reference Photo Setup

Ask: "Do you want to appear as a character in your carousel images? This means the AI will draw YOU into the slides."

**If yes:**
- Ask: "Where is your headshot? Drag it onto your Desktop if it's on your phone, or tell me the filename if it's already on your computer (e.g., 'headshot.jpg on my Desktop')."
- Copy it into place: `cp <their-path> my-skills/instagram-carousel/assets/my-reference.jpeg`
- Verify file exists and has content: `ls -la my-skills/instagram-carousel/assets/my-reference.jpeg`
- Show confirmation: "Got it. Here's the photo I'll use as your reference: [path]. Looks right?"

**If no:**
- "No problem. You can still use character-based carousels with illustrated characters. You can add a reference photo anytime by saying 'set up my carousel reference photo'."

### Step 3: Style Selection

Read `my-skills/instagram-carousel/resources/my-styles.md` to show available styles.

Ask: "Which visual style do you want as your default?"

Present the options from the style library. If they want a custom style, ask them to describe it and add it to `my-styles.md`.

Save their selection by setting `default: true` on their chosen style (and removing it from the previous default).

### Step 4: Verification

- If reference photo exists, confirm it's readable
- Report their chosen style
- "Carousel creation is ready. Say 'create a carousel from [article/topic]' to start."

### Step 5: Next Steps

- "To generate images automatically, your GOOGLE_API_KEY is already set up."
- "To post directly to Instagram, say: set up instagram poster"
- "To create transparent logos/assets, say: set up cutout"

---

## Pre-Setup Checks (for Agent)

Before image generation, the agent should verify:
- If member wants to appear in images AND `my-skills/instagram-carousel/assets/my-reference.jpeg` doesn't exist → "I don't have a reference photo for you yet. Say 'set up instagram carousel' to add one."
- GOOGLE_API_KEY must be set for image generation (text carousel creation works without it)
