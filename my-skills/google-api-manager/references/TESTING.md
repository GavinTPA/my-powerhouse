# Testing Plan for google-api-manager

## Pre-flight Checks
- [ ] Skill appears in `.claude/skills/` symlinks
- [ ] Skill registered in `settings.local.json`
- [ ] New terminal session started (settings refresh)
- [ ] gcloud CLI installed (`gcloud --version`)
- [ ] gcloud authenticated (`gcloud auth list`)

## Skill Discovery Test
- [ ] Run: "What skills are available?" or trigger with "show my team"
- [ ] Expected: google-api-manager appears in skill list

## Setup Test
- [ ] Run: "set up google api manager"
- [ ] Expected: Wizard checks gcloud, auth, billing, asks for prefix and budget
- [ ] Verify: `~/.config/google-api-manager.yaml` created with correct values

## Status Check Test
- [ ] Run: `python3 tools/setup.py --check`
- [ ] Expected: Shows gcloud status, auth, config values

## Add Member Test
- [ ] Run: "add team member Test Person"
- [ ] Expected: 6-step sequence runs, AIza key returned
- [ ] Verify: Member appears in YAML config
- [ ] Verify: Project exists in Google Cloud (`gcloud projects list`)

## List Members Test
- [ ] Run: "show my team"
- [ ] Expected: Table with Test Person, project ID, status, date

## Revoke Test (Disable)
- [ ] Run: "revoke Test Person" → choose disable
- [ ] Expected: Key disabled, status updated to "disabled" in YAML
- [ ] Verify: The AIza key no longer works for API calls

## Revoke Test (Delete Project — Cleanup)
- [ ] Run: `python3 tools/revoke_member.py "Test Person" --delete-project`
- [ ] Expected: Project scheduled for deletion (30-day window)

## Spending Test
- [ ] Run: "check team spending"
- [ ] Expected: Budget alert status shown (or link to billing dashboard)

## Edge Cases
- [ ] Add member with same name twice → should reject with error
- [ ] Revoke non-existent member → should show member list and error
- [ ] Run add_member without setup → should tell user to run setup first
- [ ] Project ID collision → should auto-append number suffix
