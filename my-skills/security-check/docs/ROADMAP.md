# Security Check - Roadmap

## Shipped

| Version | Date | What Changed |
|---------|------|--------------|
| v1.0 | 2026-01-19 | Initial release - 4 core checks |
| v1.1 | 2026-01-22 | Git history secret scanning |
| v1.2 | 2026-02-04 | Pre-commit hook integration |

## Planned

- [ ] **Auto-recovery suggestions** - When backup exists, offer to restore
- [ ] **Credential rotation reminders** - Track age of API keys

## Ideas (Not Committed)

- Integration with macOS Keychain for secure credential storage
- Automatic cleanup of old backups (keep last 5 per file)
- "Panic button" that restores all critical files from latest backups
- Audit trail logging to daily note

## What We've Learned

### The .zshrc Incident

A `sed -i ''` command with a failing pattern wiped an entire .zshrc file. No backup existed. All API credentials accumulated over months were lost.

**Root cause:** sed -i on macOS behaves differently than Linux. With a failing pattern, it can truncate the file to zero bytes.

**Prevention:** This skill now creates timestamped backups before ANY edit to critical files.

### Settings Hygiene Discovery

While building this skill, we found hardcoded secrets in settings.local.json that had been approved during fast-moving sessions. The permission system saves the exact command approved, including any inline credentials.

**Lesson:** Never approve commands with secrets inline. Configure them properly first.
