# Git Safety Rules

Topic-specific gotchas for git operations and critical file editing.

---

## Critical File Editing

**NEVER use `sed -i` on critical config files without backup.**

The command `sed -i '' 'pattern' file` on macOS can destroy files if the pattern fails or has issues.

**Safe alternatives:**

```bash
# Option 1: Always backup first
cp ~/.zshrc ~/.zshrc.bak && sed -i '' 's/old/new/' ~/.zshrc

# Option 2: Use ed or ex (atomic)
printf '%s\n' 'g/old/s//new/g' 'w' 'q' | ed -s ~/.zshrc

# Option 3: Write to temp, then move (safest)
sed 's/old/new/' ~/.zshrc > ~/.zshrc.tmp && mv ~/.zshrc.tmp ~/.zshrc
```

**Files that require backup-first editing:**
- `~/.zshrc` (API credentials, PATH, aliases)
- `~/.zprofile`, `~/.bash_profile`
- Any file with credentials or irreplaceable config

---

## Unauthenticated API Proxies

**Never deploy a serverless function that proxies an API key without authentication on the endpoint.**

Even if the key is stored in environment variables (not source code), a public GitHub repo advertises the endpoint URL and anyone can call it.

**Minimum viable protection:** Check for a secret header or token in the handler:

```javascript
// At the top of any API proxy handler
if (req.headers['x-api-secret'] !== process.env.API_SECRET) {
  return res.status(401).json({ error: 'Unauthorized' });
}
```

**Checklist before deploying any API proxy:**
- Auth check on the endpoint (secret header, token, or OAuth)
- GitHub repo set to **private** (or no repo URL in deployment)
- API key restricted to specific APIs/IPs where possible
- Budget alerts configured on the provider
