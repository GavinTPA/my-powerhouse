# Lets Wrap - Technical Reference

## Overview

End-of-session skill that captures learnings from the conversation and encodes them into the member's mission context and CLAUDE.md. Member-facing version designed for coaches with zero technical background.

## Architecture

```
Conversation → Learning Scan → Classification → Routing → Approval → Save → Dismount
```

### Pipeline Steps

| Step | Action | Tools Used |
|------|--------|------------|
| 1. Session Review | git status/log (silent) | Bash |
| 2. Learning Capture | Conversation scan, classify HIGH/MEDIUM/LOW | — |
| 3. Mission Context Update | Propose edits to SKILL.md | Read, Edit, AskUserQuestion |
| 4. CLAUDE.md Update | Propose edits to CLAUDE.md | Read, Edit, AskUserQuestion |
| 5. Save Your Work | git add/commit/push (silent) | Bash |
| 6. The Dismount | Final summary + exit instructions | — |

### File Targets

| File | What Goes There |
|------|----------------|
| `my-skills/mission-context/SKILL.md` | Identity, voice, terminology, client info |
| `CLAUDE.md` | Workflow preferences, iron rules, working notes |

### Learning Classification

| Level | Trigger | Action |
|-------|---------|--------|
| HIGH | Direct correction from member | Propose immediate update |
| MEDIUM | Observed pattern | Propose with "wait and see" option |
| LOW | Observation | Mention, don't propose edit |

## Key Design Decisions

- **No raw git output** — All terminal commands run silently, results reported in plain English
- **No orphan prompts** — Pipeline ends definitively at Step 6 with exit instructions
- **One approval at a time** — Each learning presented individually for approval
- **Mission context priority** — Most learnings route to MC; CLAUDE.md is secondary
- **No skill packaging** — Members receive skills, they don't build them
- **No branch management** — Members work on main only

## Differences from Ed's Version (powerhouse-lab)

| Feature | Ed's Version | Member Version |
|---------|-------------|----------------|
| Skill packaging | Yes (package-skill.sh) | No |
| Index sync | Yes (Powerhouse Lab Index) | No |
| Branch cleanup | Yes (merged branches) | No |
| Daily note update | Yes (Zettelkasten) | No |
| Rules file routing | Yes (topic-specific rules) | No (MC + CLAUDE.md only) |
| Documentation checklist | Yes (full routing table) | No |
| Language | Technical | Coaching |
| Git output | Shown to user | Hidden |

## Integration

- Reads mission context from `my-skills/mission-context/SKILL.md`
- Reads CLAUDE.md from repo root
- Uses AskUserQuestion for all approval flows
- Commits to main branch only
