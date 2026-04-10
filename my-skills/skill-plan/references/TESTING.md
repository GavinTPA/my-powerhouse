# Testing Plan for skill-plan

## Pre-flight Checks

- [ ] Skill appears in `.claude/skills/` symlinks
- [ ] Skill registered in `settings.local.json`
- [ ] New terminal session started (settings refresh)

## Skill Discovery Test

- [ ] Run: "What skills are available?"
- [ ] Expected: skill-plan appears in list with correct description

## Basic Invocation Test

- [ ] Run: "plan this skill for test-feature"
- [ ] Expected: Skill activates, loads CLAUDE.md, invokes mission-context, runs semantic search

## Context Loading Test

- [ ] Verify CLAUDE.md is read automatically
- [ ] Verify mission-context skill is invoked
- [ ] Verify semantic search runs with skill name as query
- [ ] Expected: Claude mentions what context it found before asking questions

## Question Flow Test

- [ ] Claude asks "What are you building?" first
- [ ] After answer, Claude asks "What problem does this solve?"
- [ ] After answer, Claude asks "What does done look like?"
- [ ] Questions come ONE AT A TIME, not all at once

## Plan Generation Test

- [ ] Plan includes all required sections:
  - [ ] The Problem
  - [ ] What We Learned
  - [ ] What Done Looks Like (as a picture, not checkboxes)
  - [ ] The Build (phased)
  - [ ] Success Criteria
  - [ ] Kill Rules
- [ ] Plan follows template format exactly
- [ ] "What Done Looks Like" is a vision/picture, not a list

## File Routing Test

### New skill (no existing folder)
- [ ] Input: "skill-plan for brand-new-thing"
- [ ] Expected: Saves to `~/Documents/COPYobsidian/MAGI/Zettelkasten/Skill Plan - brand-new-thing - YYYY-MM-DD.md`

### Existing skill improvement
- [ ] Input: "create a plan for improving inbox-triage"
- [ ] Check: `skills/inbox-triage/` folder exists
- [ ] Expected: Saves to `skills/inbox-triage/docs/plans/[feature].md`

## Integration Test

- [ ] After plan is saved, verify semantic search links are included as wikilinks
- [ ] Verify plan can be used as input to new-skill-wizard (manual test)
