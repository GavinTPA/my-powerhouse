# Testing Plan for security-check

## Pre-flight Checks

- [ ] Skill folder exists at `skills/security-check/`
- [ ] SKILL.md has valid YAML frontmatter
- [ ] Symlinks created via `./scripts/setup-skills.sh`
- [ ] `Skill(security-check)` in `.claude/settings.local.json`
- [ ] New terminal session started

## Skill Discovery Test

- [ ] Run: "What skills do you have for security?"
- [ ] Expected: security-check appears with description about protecting files and secrets

## Basic Invocation Tests

### Test 1: Full Security Check
- [ ] Run: "Run a security check"
- [ ] Expected: All 4 checks execute and produce output:
  - Backup status (or note that no edits pending)
  - Secret detection results
  - Settings hygiene audit
  - Environment variable health

### Test 2: Secret Scan Only
- [ ] Run: "Check for secrets in my settings"
- [ ] Expected: Scans settings.local.json, reports findings

### Test 3: Environment Health Only
- [ ] Run: "Check my environment variables"
- [ ] Expected: Lists which required vars are set vs missing

## Automatic Backup Test (CRITICAL)

### Test 4: .zshrc Edit Trigger
- [ ] Run: "Add a comment to my .zshrc that says # test comment"
- [ ] Expected BEFORE edit: "Created backup at ~/.zshrc.backup.[timestamp]"
- [ ] Expected AFTER edit: Comment added successfully
- [ ] Verify: `ls -la ~/.zshrc.backup.*` shows new backup
- [ ] Cleanup: Remove test comment and backup

### Test 5: Settings Edit Trigger
- [ ] Run: "Add a comment to settings.local.json"
- [ ] Expected: Backup created before edit

## Git History Scan Tests

### Test 6: Git History Scan Execution
- [ ] Run: "Scan repo for secrets"
- [ ] Expected: Script executes successfully, produces markdown table output
- [ ] Verify: Output includes commit count and file types scanned

### Test 7: Git History Scan - Direct Script
- [ ] Run: `./skills/security-check/scripts/scan-git-secrets.sh`
- [ ] Expected: Exit code 0 (no secrets) or 1 (secrets found)
- [ ] Verify: Output is valid markdown table format

### Test 8: Git History Scan - Verbose Mode
- [ ] Run: `./skills/security-check/scripts/scan-git-secrets.sh --verbose`
- [ ] Expected: Additional debug output showing patterns being searched

### Test 9: Git History Scan - Different Repo
- [ ] Run: `./skills/security-check/scripts/scan-git-secrets.sh /path/to/other/repo`
- [ ] Expected: Scans specified repository instead of current directory

### Test 10: Git History Scan - Base64 Detection
- [ ] Create test file with base64 string: `echo "secret=SGVsbG9Xb3JsZFRoaXNJc0FWZXJ5TG9uZ0Jhc2U2NEVuY29kZWRTZWNyZXRLZXk=" > test-secret.yaml`
- [ ] Commit: `git add test-secret.yaml && git commit -m "test"`
- [ ] Run: `./skills/security-check/scripts/scan-git-secrets.sh --verbose`
- [ ] Expected: Detects "Base64 Encoded Secret" with MEDIUM risk
- [ ] Cleanup: `git reset --hard HEAD~1`

## Edge Cases

### Test 11: No Secrets in Settings
- [ ] With clean settings file, run secret scan
- [ ] Expected: "No secrets detected" (positive confirmation)

### Test 12: Missing Environment Variables
- [ ] Temporarily unset a variable: `unset GMAIL_ADDRESS`
- [ ] Run environment health check
- [ ] Expected: GMAIL_ADDRESS listed as missing
- [ ] Restore: Re-source .zshrc

### Test 13: Backup Recovery Scenario
- [ ] Create a backup: "Add test to .zshrc" (creates backup)
- [ ] Ask: "I need to restore my .zshrc from backup"
- [ ] Expected: Skill identifies available backups, offers restoration

## Integration Tests

### Test 14: Skill Works in Agent Context
- [ ] Use a skill/agent that edits critical files
- [ ] Verify backup still created automatically

### Test 15: Multiple Rapid Edits
- [ ] Make 3 quick edits to .zshrc
- [ ] Verify: 3 separate backups created with different timestamps

## Verification Commands

```bash
# Check skill registration
grep "security-check" .claude/settings.local.json

# Check symlinks exist
ls -la .claude/skills/ | grep security-check

# List any existing backups
ls -la ~/.zshrc.backup.* 2>/dev/null || echo "No backups yet"

# Check current env var status
env | grep -E "^(GMAIL_|KINDLE_|GOOGLE_|AUTH_TOKEN|CT0)" | wc -l
```

## Pass Criteria

- [ ] All pre-flight checks pass
- [ ] Skill discovered with correct description
- [ ] Full audit produces all 5 sections
- [ ] Automatic backup triggered before .zshrc edit
- [ ] No false positives in secret detection
- [ ] Environment health accurately reports set/missing vars
- [ ] Git history scan runs without error
- [ ] Git history scan output is valid markdown table format
