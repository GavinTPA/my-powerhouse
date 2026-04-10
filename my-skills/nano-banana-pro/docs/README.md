# Nano Banana Pro - Technical Reference

## What It Does

Generates images using Google's Gemini 3 Pro Image API. Uses the `generate_content` endpoint with `ImageConfig` for native resolution control (1K/2K/4K) and aspect ratio specification.

## Dependencies

**Tools required:** Read, Write, Bash, Glob

**Python packages:**
- `google-genai` (the new SDK, not `google-generativeai`)
- `pillow` (for any post-processing)

**Environment:**
- `GOOGLE_API_KEY` must be set in `~/.zshrc`

## API Details

**Model:** `gemini-3-pro-image-preview`

**Endpoint:** `generate_content` (not chat mode)

**Configuration:**
```python
config=types.GenerateContentConfig(
    response_modalities=["IMAGE"],
    image_config=types.ImageConfig(
        aspect_ratio="16:9",
        image_size="1K"  # Must be uppercase
    )
)
```

## Usage

**Trigger phrases:**
- "generate an image of..."
- "create a hero image for..."
- "make an image showing..."
- "nano banana [description]"

**CLI tool:**
```bash
python3 tools/generate_image.py \
  "prompt text" \
  --size 1K \
  --aspect 16:9 \
  --output ~/Downloads/ \
  --name hero-image
```

## Parameters

| Parameter | Default | Options |
|-----------|---------|---------|
| `--size` | 1K | 1K, 2K, 4K (accepted but ignored - SDK limitation) |
| `--aspect` | 16:9 | 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 |
| `--ed` | - | Use Ed's default reference image |
| `--reference` | - | Path to custom reference image |
| `--output` | ~/Downloads/ | Output directory |
| `--name` | image | Filename prefix |

**Note:** The `--size` parameter is accepted for future compatibility but currently ignored. The google-genai SDK (v1.47.0) only supports `aspect_ratio`. Resolution control (`image_size`) is documented by Google but not yet implemented in the Python SDK.

## Output

Returns JSON:
```json
{
  "success": true,
  "path": "/path/to/generated-image.png",
  "resolution": "1K",
  "aspect_ratio": "16:9",
  "cost_estimate": "$0.134"
}
```

## Testing

1. **Environment check:**
   ```bash
   echo $GOOGLE_API_KEY | head -c 10
   ```

2. **Basic generation:**
   ```bash
   python3 tools/generate_image.py \
     "A red apple on a white background" \
     --size 1K --aspect 1:1
   ```

3. **With reference:**
   ```bash
   python3 tools/generate_image.py \
     "Person giving a presentation" \
     --ed --size 2K
   ```

## Pricing

- Default (~1K): ~$0.134/image
- 2K: ~$0.24/image (when SDK supports)
- 4K: ~$0.24/image (when SDK supports)

## Differences from instagram-carousel

| Feature | instagram-carousel | nano-banana-pro |
|---------|-------------------|-----------------|
| Mode | Chat (for consistency) | generate_content |
| Resolution | Post-resize only | Native 1K/2K/4K |
| Purpose | Multi-image sets | Single images |
| Default aspect | 4:5 (Instagram) | 16:9 (hero) |
