# Image Generation Rules

Topic-specific gotchas for AI image generation.

*Add your image generation patterns and gotchas here as you discover them.*

---

## Character Consistency

When generating multiple images that need the same character:

```python
# Wrong - loses context between calls
model.generate_content(prompt1)
model.generate_content(prompt2)

# Right - chat maintains character
chat = model.start_chat()
chat.send_message([reference_image, prompt1])
chat.send_message(prompt2)  # remembers character
```

---

## Saving Prompts

When creating image prompts, save them as markdown files for reuse:
- Put the prompt in a code block for one-click copy
- Include metadata: platform, aspect ratio, model used
