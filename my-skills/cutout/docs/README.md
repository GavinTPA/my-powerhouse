# Cutout — Technical Reference

**macOS only.** Not supported on Windows.

## Architecture

Creates transparent PNG assets using `rembg` for background removal and Gemini API for AI-generated cutouts. Runs in an isolated Python virtual environment.

## Dependencies

- Python 3.11, 3.12, or 3.13 (onnxruntime doesn't support 3.14)
- rembg (background removal via U2Net model)
- google-genai (Gemini API for AI-generated cutouts)
- Pillow (image processing)

## Tools

| Tool | Purpose |
|------|---------|
| `tools/cutout.py` | Generate transparent cutouts from prompts or images |
| `tools/remove_bg.py` | Remove background from existing images |
| `tools/model_cleanup.py` | Clean up downloaded U2Net models |

## Virtual Environment

The skill uses its own `.venv/` to isolate ML dependencies:

```
my-skills/cutout/.venv/bin/python3  # Use this Python for all tool execution
```

All tool execution must use the venv Python to access rembg and dependencies.

## Model Storage

The U2Net model (~180MB) downloads to `~/.u2net/` on first use. If corrupted, delete the folder and re-run to re-download.

## Cost

Background removal is free (local processing). AI-generated cutouts use Gemini API (~$0.134/image).
