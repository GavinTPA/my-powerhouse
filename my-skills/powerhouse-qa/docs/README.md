# Powerhouse QA — Technical Reference

## Overview

QA review skill that reads mission-context to understand the user's business, then applies quality checks through that lens. Five review modes: Content QA, Team Safety Audit, Pre-Ship Check, Red Team, User Perspective.

## Architecture

Pure instruction skill — no tools, no scripts, no external dependencies. Reads mission-context dynamically at the start of every review.

```
powerhouse-qa/
  SKILL.md          — Core instructions (all review modes)
  docs/
    README.md       — This file
    GUIDE.md        — Coach-friendly guide
    ROADMAP.md      — Shipped + planned
```

## How It Works

1. User triggers the skill ("review this", "red team this", "team safety audit")
2. Skill invokes mission-context to load the user's business context
3. Matches the request to one of five review modes
4. Runs the review using mission-context as the quality lens
5. Outputs structured findings (Passed / Issues / Edge Cases / Verdict)

## Review Modes

| Mode | Trigger | Focus |
|------|---------|-------|
| Content QA | "review this", "QA check" | Voice, audience, slop, terminology |
| Team Safety Audit | "team safety audit" | Would people described be upset? |
| Pre-Ship Check | "is this ready to ship?" | Edge cases, failures, completeness |
| Red Team | "red team this" | Security, abuse, cost, reputation |
| User Perspective | "how would a user experience this?" | Friction, confusion, first-time experience |

## Dependencies

- **mission-context** — Must exist in the user's repo for context-aware reviews. Skill works without it (generic review) but warns the user.

## Distribution

Ships to all Powerhouse repos via `get-new-skills`. No configuration needed — reads whatever mission-context the user has built.

## Relationship to Casper (Ed's MAGI Agent)

Ed's personal Casper agent (`.claude/agents/casper.md`) is a separate MAGI agent with Evangelion theming and Ed-specific skills. Casper can invoke powerhouse-qa for mission-context-aware reviews. powerhouse-qa is the universal capability; Casper is Ed's personal wrapper.
