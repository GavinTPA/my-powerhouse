---
name: cutout
description: Create transparent PNG assets from prompts or existing images. Use when "make a cutout", "transparent logo", "sticker of", "remove background", "create transparent", "cutout of", "set up cutout", "set up background removal", "configure cutout".
allowed-tools: Read, Write, Bash, Glob
---

# Cutout

**macOS only.** This skill is not supported on Windows.

Create transparent PNG assets by generating images and removing backgrounds, or by processing existing images.

## When This Activates

- "Create a cutout of..."
- "Make a transparent logo..."
- "Sticker of..."
- "Remove the background from..."
- "Create a transparent image of..."
- "Cutout of me..."
- "Remove backgrounds from all images in ~/Downloads/photos"
- "Process this folder of images as cutouts"

## Pre-Check (Before Any Use)

Before running cutout tools, verify the venv exists:
```bash
test -f my-skills/cutout/.venv/bin/python3 && my-skills/cutout/.venv/bin/python3 -c "from rembg import remove; print('OK')" 2>/dev/null || echo "Not set up"
```

If "Not set up": "Background removal isn't set up yet. Say 'set up cutout' to install the tools. It takes about 5 minutes."

## How It Works

**Three modes:**

1. **Generate Mode:** Prompt → Gemini generates with white background → rembg removes background → transparent PNG
2. **Process Mode:** Existing image → rembg removes background → transparent PNG
3. **Folder Mode:** Directory of images → rembg removes backgrounds from all → transparent PNGs with "-cutout" suffix

## Parameter Detection

### Mode Detection
| Request Contains | Mode |
|------------------|------|
| Image path, "from this", "from ~/Downloads" | Process (use existing image) |
| Folder path, "all images in", "process folder" | Folder (batch process directory) |
| Description of what to create | Generate (create new image) |

### Aspect Ratio (defaults to 1:1)
| Mentioned | Maps To |
|-----------|---------|
| "square", "icon", "logo", "sticker" | 1:1 |
| "portrait", "vertical" | 9:16 |
| "landscape", "wide" | 16:9 |
| Explicit ratio (e.g., "3:2") | Use as-is |

### Character Reference
- If user says "me", "of me" → use `--me` flag
- If user provides a reference path → use `--reference <path>`
- Otherwise → no reference image

### Output Format
| Mentioned | Maps To |
|-----------|---------|
| "webp", "smaller file", "web format" | webp |
| Default (nothing mentioned) | png |

### Multiple Sizes
| Mentioned | Maps To |
|-----------|---------|
| "at 1x, 2x, 3x", "retina sizes" | --sizes 1x,2x,3x |
| "at 512 and 1024", "multiple sizes" | --sizes 512,1024 |

### rembg Model
- Default: `birefnet-general` (highest accuracy, best for logos/graphics)
- User can request: `birefnet-general-lite` (faster), `isnet-general-use`, `u2net` (classic)

## Execution

The tools use a local venv with rembg pre-installed. All commands MUST use the venv python.

### Generate Mode
```bash
my-skills/cutout/.venv/bin/python3 my-skills/cutout/tools/cutout.py \
  "<prompt>" \
  --aspect <ratio> \
  [--me | --reference <path>] \
  --output <folder> \
  --name <filename_prefix> \
  [--model <rembg_model>] \
  [--format png|webp] \
  [--sizes 1x,2x,3x | --sizes 512,1024,2048]
```

### Process Mode
```bash
my-skills/cutout/.venv/bin/python3 my-skills/cutout/tools/cutout.py \
  --input <path_to_image> \
  --output <folder> \
  --name <filename_prefix> \
  [--model <rembg_model>] \
  [--format png|webp] \
  [--sizes 1x,2x,3x | --sizes 512,1024,2048]
```

### Folder Mode
```bash
my-skills/cutout/.venv/bin/python3 my-skills/cutout/tools/cutout.py \
  --folder <path_to_folder> \
  [--output <output_folder>] \
  [--model <rembg_model>] \
  [--format png|webp]
```

### Standalone Background Removal
```bash
my-skills/cutout/.venv/bin/python3 my-skills/cutout/tools/remove_bg.py \
  <input_path> \
  <output_path> \
  [--model <rembg_model>] \
  [--format png|webp]
```

### Model Cleanup
```bash
my-skills/cutout/.venv/bin/python3 my-skills/cutout/tools/model_cleanup.py --list
my-skills/cutout/.venv/bin/python3 my-skills/cutout/tools/model_cleanup.py --remove MODEL_NAME
```

## Prompting Tips (For Generate Mode)

The tool automatically appends cutout-friendly modifiers to prompts. For best results, prompt for:
- **Simple subjects** — single object/person, not complex scenes
- **Clean lines** — "minimalist", "icon style", "graphic design"
- **Defined edges** — avoid fuzzy, transparent, or wispy elements

## After Generation

1. Report the transparent PNG path to the user
2. If edges are rough, offer to retry with different model

## Pricing

- **Generate mode:** ~$0.134 (Gemini generation) + $0.00 (local rembg)
- **Process mode:** $0.00 (local only)

---

## Setup Wizard

**Trigger:** "set up cutout", "set up background removal", "configure cutout"

### Step 1: Check Python Version

```bash
python3 --version
```

Must be 3.11, 3.12, or 3.13 (onnxruntime doesn't support 3.14 yet).

If wrong version:
- Install Python 3.12: `brew install python@3.12`
- Then use `python3.12` explicitly in Step 2

### Step 2: Create Virtual Environment

```bash
python3 -m venv my-skills/cutout/.venv
```

If Python 3.14 is the default, use: `python3.12 -m venv my-skills/cutout/.venv`

Explain: "This creates an isolated Python environment for the background removal tool."

### Step 3: Install Dependencies

```bash
my-skills/cutout/.venv/bin/pip install "rembg[cpu,cli]" google-genai Pillow
```

This takes 1-2 minutes (downloads ML dependencies).

### Step 4: First Run (Model Download)

Run a quick test to trigger the model download:
```bash
echo "test" | my-skills/cutout/.venv/bin/rembg i -m birefnet-general > /dev/null 2>&1
```

This downloads about 180MB — expect 2-5 minutes on a typical connection. You'll see a progress bar. Don't close the terminal while it downloads.

**If the download fails:** `rm -rf ~/.u2net/` clears any corrupted partial downloads, then try again.

### Step 5: Verify

```bash
my-skills/cutout/.venv/bin/python3 -c "from rembg import remove; print('rembg OK')"
```

Report: "Cutout is ready. Say 'remove background from [image]' or 'create a cutout of [description]'."
