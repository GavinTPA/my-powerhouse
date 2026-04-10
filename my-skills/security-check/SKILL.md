---
name: security-check
description: Protects critical files and detects hardcoded secrets before risky edits. Use when "security check", "audit my settings", "check for secrets", before editing .zshrc or config files.
allowed-tools: Read, Glob, Grep, Bash, Edit
---

# Security Check

Prevents critical config files from being accidentally destroyed. Audits critical files, detects hardcoded secrets, and creates backups before dangerous edits.

## When This Activates

- Manual: "security check", "audit my settings", "check for secrets"
- Git history scan: "scan repo for secrets", "check git history for secrets", "scan history"
- Pre-commit hook: "install pre-commit hook", "install secret detection hook"
- Automatic: Before ANY edit to files in the critical files list

## Critical Files (Always Backup Before Editing)

These files require backup before any modification:

```
~/.zshrc
~/.zprofile
~/.bash_profile
~/.bashrc
~/.gitconfig
~/.ssh/config
~/.config/**/*.yaml
~/.config/**/*.json
.claude/settings.local.json
.claude/settings.json
```

## The Five Checks

### 1. Pre-Edit Backup (AUTOMATIC)

Before editing any critical file:

```bash
# Create timestamped backup
cp ~/.zshrc ~/.zshrc.backup.$(date +%Y%m%d_%H%M%S)
```

**Tell the user:** "Created backup at ~/.zshrc.backup.20260119_143022"

### 2. Secret Detection in Settings

Scan `.claude/settings.local.json` for hardcoded secrets:

**Patterns that indicate secrets:**
- Strings longer than 20 chars that look like tokens (alphanumeric + special chars)
- Anything containing `Bearer`, `token=`, `key=`, `password=`
- Base64-encoded strings (contain only A-Za-z0-9+/=)
- Anything matching common API key patterns:
  - `sk-...` (OpenAI)
  - `ghp_...` (GitHub)
  - `xoxb-...` (Slack)
  - `AKIA...` (AWS)

**When found:**
1. List the offending entries (show pattern, not full secret)
2. Recommend: "Move this to ~/.zshrc as an environment variable"
3. Offer to help migrate

### 3. Settings Audit

Check `.claude/settings.local.json` for hygiene issues:

**Flag these problems:**
- Duplicate permission entries
- Specific commands that could be wildcards (e.g., `git commit -m "specific message"` should be `Bash(git:*)`)
- Permissions with embedded file paths that expose structure
- Overly broad permissions that could be scoped

**Output format:**
```
Settings Audit Results
======================

Secrets Found: 2
- Line 47: Possible API key (sk-...)
- Line 89: Possible token (Bearer ...)

Hygiene Issues: 3
- Line 12: Specific git command - recommend: Bash(git:*)
- Line 34: Duplicate of line 12
- Line 56: Embedded absolute path

Recommendation: Clean up settings to remove secrets and consolidate wildcards.
```

### 4. Environment Variable Health Check

Verify expected environment variables are set:

```bash
# Check for common required vars
env | grep -E "^(GMAIL_|KINDLE_|GOOGLE_|AUTH_TOKEN|CT0|ANTHROPIC_)" | wc -l
```

**Required variables to check:**
- `GMAIL_ADDRESS` - Email sending
- `GMAIL_APP_PASSWORD` - Email auth
- `KINDLE_EMAIL` - Send to Kindle
- `GOOGLE_API_KEY` - Gemini/AI Studio
- `AUTH_TOKEN` - X/Twitter
- `CT0` - X/Twitter CSRF

**Output:**
```
Environment Health
==================
Set: GMAIL_ADDRESS, GMAIL_APP_PASSWORD, KINDLE_EMAIL, GOOGLE_API_KEY
Missing: AUTH_TOKEN, CT0

Note: Missing variables will cause related skills to fail.
```

### 5. Git History Secret Scan

Scan entire git history for accidentally committed credentials. This catches secrets that were committed and later removed - they're still in history!

**Trigger:** "scan repo for secrets", "check git history for secrets", "scan history"

**Run the script:**
```bash
scripts/scan-git-secrets.sh
```

Or for verbose output:
```bash
scripts/scan-git-secrets.sh --verbose
```

**Patterns detected:**

| Pattern | Service | Risk |
|---------|---------|------|
| `AKIA[0-9A-Z]{16}` | AWS Access Key | HIGH |
| `ghp_[a-zA-Z0-9]{36}` | GitHub PAT | HIGH |
| `sk-[a-zA-Z0-9]{48}` | OpenAI Key | HIGH |
| `sk-ant-[a-zA-Z0-9-_]{80,}` | Anthropic Key | HIGH |
| `xoxb-...` | Slack Bot Token | HIGH |
| `AIza[0-9A-Za-z-_]{35}` | Google API Key | MEDIUM |
| `Bearer [token]` | OAuth Token | MEDIUM |
| `password=`, `secret=`, `api_key=` | Hardcoded credentials | MEDIUM |

**File types scanned:**
- `.env`, `.env.*`, `*.yaml`, `*.yml`
- `*.json`, `*.config`, `*.conf`
- `*.sh`, `*.properties`, `*.toml`

**Excludes:**
- Lock files (package-lock.json, yarn.lock)
- Markdown documentation
- node_modules

**Output format:**
```
## Git History Secret Scan

Found 3 potential secrets in git history:

| Commit | File | Pattern | Risk |
|--------|------|---------|------|
| abc123 | .env.backup | AWS Access Key | HIGH |
| def456 | config.json | Generic API Key | MEDIUM |
| 789abc | setup.sh | Hardcoded Password | HIGH |

**Recommended actions:**
1. Rotate compromised credentials
2. Remove from history using git filter-repo or BFG Repo-Cleaner
3. Force-push to update remote
4. Add to .gitignore
```

**Important:** Environment variables (from `~/.zshrc` etc.) are NOT flagged - they're loaded at runtime, not committed. This only flags secrets that exist in git history.

## Usage Examples

### Manual Full Audit
```
User: "Run a security check"
→ Run all 4 checks, output full report
```

### Before Critical Edit
```
User: "Add a new export to my .zshrc"
→ Automatically backup first
→ Then make the edit
→ Verify the file is valid: source ~/.zshrc
```

### Quick Secret Scan
```
User: "Check for secrets in my settings"
→ Run check #2 only
→ Output findings
```

### Git History Scan
```
User: "Scan repo for secrets"
→ Run check #5 (git history scan)
→ Search all commits for leaked credentials
→ Output table of findings with remediation steps
```

## Integration with CLAUDE.md

This skill enforces the Iron Rule from CLAUDE.md:

> **NEVER use `sed -i` on critical config files without backup.**

When Claude is about to edit a critical file, this skill intercepts and:
1. Creates the backup
2. Proceeds with the edit
3. Verifies the file still works (for shell configs: `source` it)

## 6. Pre-Commit Hook (Prevention)

Blocks commits that contain hardcoded secrets before they enter git history. While the git history scanner (Check #5) catches secrets already committed, this hook prevents them from getting in at all.

**Install:**
```bash
scripts/install-hook.sh
```

**What it does:**
1. Scans staged files (`git diff --cached`) for secret patterns
2. Checks only added/modified lines (not the entire file)
3. Blocks the commit if secrets are detected (exit 1)
4. Shows which file, what pattern, and the matched line
5. Allows the commit if clean (exit 0)

**Patterns detected (consistent with Check #5):**

| Pattern | Service | Risk |
|---------|---------|------|
| `AKIA[0-9A-Z]{16}` | AWS Access Key | HIGH |
| `ghp_[a-zA-Z0-9]{36}` | GitHub PAT | HIGH |
| `sk-[a-zA-Z0-9]{48}` | OpenAI Key | HIGH |
| `sk-ant-[a-zA-Z0-9-_]{80,}` | Anthropic Key | HIGH |
| `-----BEGIN PRIVATE KEY-----` | Private Key | HIGH |
| `Bearer [token]` | OAuth Token | MEDIUM |
| `API_KEY=`, `SECRET=`, `TOKEN=`, `PASSWORD=` | Env var assignments | MEDIUM-HIGH |
| `password=`, `secret=`, `api_key=`, `token=` | Config values | MEDIUM-HIGH |

**Handling false positives:**

Create a `.secretsignore` file in the repo root with regex patterns to skip (one per line):

```
# Example .secretsignore
sk-test-fake-key-for-documentation
AKIA_EXAMPLE_PLACEHOLDER
```

Lines starting with `#` are comments. Patterns match against both the line content and the file path.

**Bypassing the hook:**
```bash
# Only when you're certain there are no real secrets
git commit --no-verify
```

## What This Prevents

- Accidental wipe of shell configuration (API credentials lost)
- Hardcoded secrets in git-tracked settings files
- Accumulation of stale/duplicate permissions
- Silent failures from missing environment variables
- Secrets lurking in git history (committed then "deleted" but still recoverable)
- New secrets entering git history (pre-commit hook blocks them before commit)
