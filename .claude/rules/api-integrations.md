# API Integration Rules

Topic-specific gotchas for external APIs and integrations.

---

## Chrome Browser Tools as Backup

When WebFetch can't access content (auth walls, dynamic JS content), use Chrome browser tools as a backup.

**When to use Chrome instead of WebFetch:**
- Sites requiring authentication or cookies
- Heavy JavaScript-rendered content
- Any content that returns empty or blocked via WebFetch

**The pattern:**
1. Try WebFetch first (fast, no browser needed)
2. If blocked/empty -> fall back to Chrome tools

**Trade-offs:**

| Method | Speed | Access | When to Use |
|--------|-------|--------|-------------|
| WebFetch | Fast (~2s) | Public only | Default for articles, docs |
| Chrome tools | Slow (~5-10s) | Full browser | Backup when WebFetch fails |

**Note:** Chrome tools only work when running locally with the Claude-in-Chrome extension.

---

## Markdown Tables with Scraped Data

When generating markdown tables from scraped web content, always strip newlines from text fields:

```python
desc = desc.replace('\n', ' ').replace('\r', ' ')
while '  ' in desc:
    desc = desc.replace('  ', ' ')
```

Embedded newlines break markdown table rendering - each row must be a single line.

---

## Vercel Domain Management (CLI vs API)

The Vercel CLI's `vercel domains rm` attempts to **delete the entire domain**, not just remove it from a project. For Vercel-purchased domains, this fails entirely (409 error).

**To remove a domain from a specific project only**, use the REST API:

```bash
curl -X DELETE -H "Authorization: Bearer $VERCEL_TOKEN" \
  "https://api.vercel.com/v9/projects/$PROJECT_ID/domains/$DOMAIN?teamId=$TEAM_ID"
```

---

## Vercel Environment Variable Whitespace

Pasting API keys into the Vercel dashboard can introduce invisible newlines when the key wraps in the text field. Symptoms: 401 auth errors, and the API provider shows "Last Used: Never" for the key.

**Fix:** Delete the env var value entirely, re-paste, then click into the field and press End to verify cursor is right after the last character. No trailing whitespace or newlines.
