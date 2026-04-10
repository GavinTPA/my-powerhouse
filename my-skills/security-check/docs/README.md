# Security Check - Technical Reference

## What It Does

Protects critical configuration files and detects hardcoded secrets before Claude makes risky edits. Implements five safety checks:

1. **Pre-edit backup** - Timestamped copies of critical files before modification
2. **Secret detection** - Scans settings.local.json for API keys and tokens
3. **Settings audit** - Flags hygiene issues (duplicates, specific commands, exposed paths)
4. **Env var health** - Verifies required environment variables are set
5. **Git history scan** - Searches commit history for accidentally committed credentials

## Dependencies

**Tools required:** Read, Glob, Grep, Bash, Edit

**No external dependencies** - uses built-in shell commands only.

## Usage

**Trigger phrases:**
- "security check" - Full audit
- "audit my settings" - Settings-focused check
- "check for secrets" - Secret detection only
- "scan repo for secrets" / "scan history" - Git history scan
- Automatic before editing critical files

## Critical File Patterns

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

## Secret Detection Patterns

| Pattern | Service |
|---------|---------|
| `sk-...` | OpenAI |
| `ghp_...` | GitHub |
| `xoxb-...` | Slack |
| `AKIA...` | AWS |
| `Bearer ...` | Generic OAuth |
| Base64 strings | Various tokens |

## Environment Variables Checked

| Variable | Purpose |
|----------|---------|
| `GMAIL_ADDRESS` | Email sender |
| `GMAIL_APP_PASSWORD` | Email auth |
| `KINDLE_EMAIL` | Kindle delivery |
| `GOOGLE_API_KEY` | Gemini/AI Studio |
| `AUTH_TOKEN` | X/Twitter |
| `CT0` | X/Twitter CSRF |

## Testing

### Pre-flight
```bash
# Verify skill is registered
grep "security-check" .claude/settings.local.json
```

### Manual Test
```
"Run a security check"
→ Should output all 4 checks with findings
```

### Automatic Trigger Test
```
"Add export FOO=bar to my .zshrc"
→ Should create backup BEFORE editing
→ Should verify file still sources correctly
```

## Output Format

```
Security Check Report
=====================

1. Backup Status
   [x] ~/.zshrc backed up to ~/.zshrc.backup.20260119_143022

2. Secret Detection
   Found: 2 potential secrets
   - Line 47: Possible API key (sk-...)
   - Line 89: Possible token (ghp_...)

3. Settings Hygiene
   Issues: 3
   - Duplicate permission entries
   - Specific commands → use wildcards
   - Exposed file paths

4. Environment Health
   Set: 4/6 required variables
   Missing: AUTH_TOKEN, CT0
```

## Git History Scan

Searches entire git history for accidentally committed secrets.

**Run:**
```bash
scripts/scan-git-secrets.sh
```

**Patterns detected:**
- AWS keys (AKIA, ASIA prefixes)
- GitHub tokens (ghp_, gho_, ghu_, github_pat_)
- OpenAI/Anthropic keys (sk-, sk-ant-)
- Slack tokens (xoxb-, xoxp-)
- Google API keys (AIza)
- Generic passwords, secrets, API keys, tokens

**Output:** Markdown table with commit, file, pattern type, and risk level.

## Related

- `~/.zshrc` contains all API credentials — protect this file
