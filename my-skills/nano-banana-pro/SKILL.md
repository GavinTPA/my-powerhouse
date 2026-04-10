---
name: nano-banana-pro
description: Generate images via Gemini 3 Pro Image API. Use when "generate an image", "create a hero image", "make an image showing", "nano banana", "set up nano banana", "set up image generation".
allowed-tools: Read, Write, Bash, Glob
---

# Nano Banana Pro

Generate images using Google's Gemini 3 Pro Image API with native resolution support (1K/2K/4K) and flexible aspect ratios.

## When This Activates

- "Generate an image of..."
- "Create a hero image for..."
- "Make an image showing..."
- "Nano banana [description]"
- Any request to create/generate an image
- "Set up nano banana pro" / "configure nano banana" / "set up image generation" → go to **Setup** section

## How It Works

1. Parse the request for: prompt, resolution, aspect ratio, character reference
2. Run the Python tool with extracted parameters
3. Report the generated image path to the user

## Parameter Detection

### Resolution
**Note:** The google-genai SDK (v1.47.0) currently only supports aspect ratio control. Resolution parameters (1K/2K/4K) are documented by Google but not yet available in the Python SDK. Images generate at ~1K by default. Resolution control will be added when SDK support arrives.

For now, accept --size parameter but ignore it (generates at default resolution).

### Aspect Ratio (defaults to 16:9)
| Mentioned | Maps To |
|-----------|---------|
| "landscape", "hero image", "banner" | 16:9 |
| "portrait", "vertical", "story" | 9:16 |
| "square", "thumbnail", "profile" | 1:1 |
| "Instagram", "social post" | 4:5 |
| Explicit ratio (e.g., "3:2") | Use as-is |

Supported ratios: 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9

### Character Reference
- If user says "me", "image of me", "myself" → use `--ed` flag
- If user provides a path → use `--reference <path>`
- Otherwise → no reference image

### Output Location
- Default: `~/Downloads/`
- If user specifies folder → use that path
- Filename: content-based (e.g., `hero-coaching-clarity.png`)

## Prompting Best Practices (Built In)

When constructing the prompt for the API, apply these principles:

1. **Keep it concise** - Under 25 words performs best. Don't pad with tags.
2. **Natural language** - Write like briefing a photographer, not keyword soup.
3. **Positive framing** - Say what you want, not what you don't want.
   - Good: "empty room with wooden floors"
   - Bad: "room without furniture"
4. **Specific visual details** - Include lighting, composition, mood when relevant.
5. **Style goes in the prompt** - No separate style parameter. Include style naturally:
   - "professional photography style"
   - "manga illustration style"
   - "minimalist graphic design"

## Execution

Run the Python tool:

```bash
python3 tools/generate_image.py \
  "<prompt>" \
  --size <1K|2K|4K> \
  --aspect <ratio> \
  [--ed | --reference <path>] \
  --output <folder> \
  --name <filename_prefix>
```

The tool returns JSON:
```json
{
  "success": true,
  "path": "/Users/eddale/Downloads/hero-coaching-clarity.png",
  "resolution": "1K",
  "aspect_ratio": "16:9",
  "cost_estimate": "$0.134"
}
```

## After Generation

1. Report the image path to the user
2. If requested, link in daily note Captures section
3. If user wants to iterate, offer to regenerate with modified prompt

## Example Interactions

**User:** "Generate a hero image for my article about the power of clarity in coaching"

**What happens:**
- Resolution: 1K (default)
- Aspect: 16:9 (hero image default)
- Reference: None (no "me" mentioned)
- Prompt: "Professional photograph of a lighthouse beacon cutting through fog at dawn, symbolizing clarity and guidance, warm golden light, cinematic composition"

**User:** "Create a 4K image of me presenting to a small group, professional photography"

**What happens:**
- Resolution: 4K (explicitly requested)
- Aspect: 16:9 (default)
- Reference: Ed's image (--ed flag)
- Prompt: "Professional photograph of [reference person] presenting to an engaged small group in a modern meeting room, natural lighting, documentary style"

**User:** "Make a 1:1 thumbnail showing a lightbulb moment"

**What happens:**
- Resolution: 1K (default)
- Aspect: 1:1 (explicitly requested)
- Reference: None
- Prompt: "Stylized illustration of a glowing lightbulb above a person's head, warm yellow light radiating outward, clean minimal background, insight concept"

## Pricing

~$0.134 per image (default resolution, ~1K)

Higher resolution pricing (when SDK supports it):
- 2K: ~$0.24
- 4K: ~$0.24

## Error Handling

- **Missing GOOGLE_API_KEY:** Tell user to run "set up nano banana pro" for guided setup
- **Invalid aspect ratio:** Default to 16:9 and warn user
- **API failure:** Report error, suggest retry or modified prompt
- **Reference image not found:** Continue without reference, warn user
- **Billing error (402/403):** Tell user to enable billing at console.cloud.google.com/billing

## Style Library

Check `resources/style-library.md` for prompts that have worked well. Add new successful styles there to build our library over time.

---

## Setup

Activated by: "set up nano banana pro", "configure nano banana", "set up image generation"

This guided setup connects image generation to the user's workspace. Follow these steps exactly.

### Step 1: Check if Already Configured

Run: `echo $GOOGLE_API_KEY | head -c 4`

If it returns `AIza` → tell the user image generation is already configured. Offer to run `python3 tools/generate_image.py --test` to verify. Skip to Step 7.

### Step 2: Check Dependencies

Run: `python3 -c "from google import genai; print('OK')"`

If it fails, install: `pip install google-genai pillow`

### Step 3: Explain What's Needed

Tell the user:

"To generate images, you need two things from Google:

1. **An API key** from Google AI Studio (takes 2 minutes)
2. **A billing account** linked to the project (image generation costs about 13 cents per image — cheaper than any stock photo, and every image is custom-made for your business)

I'll walk you through both. You'll need your personal Gmail account — not a work or school account."

### Step 4: Walk Through API Key Creation

Tell the user to:

1. Open https://aistudio.google.com/apikey in their browser
2. Sign in with their **personal Gmail account** (work/school accounts often block access)
3. Click **"Create API key in new project"**
4. **Copy the key immediately** — it starts with `AIza` and is only shown once

### Step 5: Walk Through Billing

Tell the user to:

1. Open https://console.cloud.google.com/billing
2. Link a billing account to the project (add a payment method)
3. Recommended: set a $20/month budget alert at https://console.cloud.google.com/billing/budgets

### Step 6: Install the Key

Ask the user to paste their API key in the chat (in their local Claude Code terminal, not a browser or shared document).

**Validate the key before doing anything:**
- Strip whitespace from both ends
- Verify it starts with `AIza`
- Verify length is between 30 and 50 characters
- Check for smart/curly quotes and replace with straight quotes
- If validation fails, tell the user what's wrong and ask them to paste again

**`.zshrc` Nuclear Protection Protocol — follow every step:**

1. **Read ~/.zshrc** using the Read tool.
   - If Read fails or returns empty → **STOP**. Tell the user: "Your shell config looks different than expected. Let's verify your Powerhouse setup is complete before adding the image generation key."
   - Do NOT create a new .zshrc file. Do NOT use the Write tool.

2. **Verify the file is real** — confirm it contains the text `ANTHROPIC_API_KEY`. Every member who completed the Powerhouse setup has this in their .zshrc. If it's missing → **STOP** and ask the user to verify their setup.

3. **Check for existing GOOGLE_API_KEY** — search for a line containing `GOOGLE_API_KEY`. If found, show it to the user and ask: "You already have a Google API key set. Do you want to replace it with the new one, or keep the existing one?"

4. **Create a timestamped backup:**
   ```bash
   cp ~/.zshrc ~/.zshrc.bak-$(date +%s)
   ```

5. **Use the Edit tool to append** the following line to ~/.zshrc:
   ```
   export GOOGLE_API_KEY="<the-validated-key>"
   ```
   Use the Edit tool. NEVER use the Write tool on .zshrc — Write overwrites the entire file.

6. **Source the file:**
   ```bash
   source ~/.zshrc
   ```

7. **Post-edit verification** — Read ~/.zshrc again using the Read tool. Confirm BOTH of these are present:
   - A line containing `ANTHROPIC_API_KEY`
   - A line containing `GOOGLE_API_KEY`
   If `ANTHROPIC_API_KEY` is missing, something went wrong. Restore immediately:
   ```bash
   # Find the most recent backup
   ls -t ~/.zshrc.bak-* | head -1
   # Restore it
   cp <most-recent-backup> ~/.zshrc && source ~/.zshrc
   ```
   Then tell the user what happened and that their original config has been restored.

**For Windows members (PowerShell):**
- Detect with: `echo $SHELL` — if it doesn't return `/bin/zsh` or `/bin/bash`, ask the user if they're on Windows
- Target file: `$PROFILE` (PowerShell profile, typically `~\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`)
- Syntax: `$env:GOOGLE_API_KEY = "<key>"` (not `export`)
- Follow the same verification pattern: read first, confirm Anthropic key exists, backup, edit, verify

### Step 7: Run the Test

```bash
python3 tools/generate_image.py --test
```

This validates the key, generates a test image (Hello Kitty and Chibi Gundam giving a thumbs up saying "You Did It!"), and confirms the connection works.

Tell the user to open the image file when it's done.

### Step 8: Celebrate

Tell the user they're all set. Suggest they try:

"Try asking me to generate an image — just say something like 'nano banana, create an image of a confident coach presenting on stage, professional photography style'"

### Setup Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Read .zshrc and verify ANTHROPIC_API_KEY exists first | Replace existing GOOGLE_API_KEY | Use Write tool on .zshrc |
| Timestamped backup before any edit | Proceed if .zshrc looks unexpected | Create a new .zshrc if Read fails |
| Post-edit verify both keys still present | | Show the full API key value in output |
| Use Edit tool only (append) | | Echo full key to terminal |
| Validate key format before saving | | Touch .zshrc if ANTHROPIC_API_KEY is missing |
