---
name: skill-plan
description: Creates structured implementation plans before building skills or features. Use when starting a new skill, planning an improvement, or formalizing a build approach. Trigger with "plan this skill", "create a plan for", "skill-plan", "I want to plan before building".
allowed-tools: Read, Write, Edit, Glob, Grep, WebSearch, WebFetch
---

# Skill Plan

Creates structured implementation plans before building - the missing link between research and new-skill-wizard.

## When This Activates

- "plan this skill"
- "create a plan for [name]"
- "skill-plan for [description]"
- "I want to plan before building"
- "let's plan [feature/skill] first"

## The Planning Workflow

### Phase 1: Context Loading (Automatic)

**Always load these first:**

1. **CLAUDE.md** - Read from project root for universal workflow rules
2. **mission-context skill** - Invoke for your terminology, frameworks, current focus

**Then search for related work:**

Search your Knowledge Vault for related notes. If Smart Connections MCP is available, use `mcp__smart-connections__semantic_search` with the skill/feature name as the query. If Smart Connections is not available, use Glob and Grep to search your Zettelkasten folder and `my-skills/` for related files. This surfaces:
- Related research
- Prior work on similar skills
- Relevant notes

Present what you found: "I found [N] related notes including [titles]. Want me to pull any of these in?"

### Phase 2: Gather Input

Ask these questions ONE AT A TIME:

1. **What are you building?**
   - Name (kebab-case)
   - One-line description

2. **What problem does this solve?**
   - The pain point
   - Why existing approaches don't work

3. **What does done look like?**
   - Paint the picture, not just criteria
   - "You trigger X, see Y, end up with Z"

If the user provides a research document or screenshots, incorporate those into "What We Learned."

### Phase 3: Generate the Plan

Use this template exactly:

```markdown
# Build Plan: [Skill Name]

**Date:** YYYY-MM-DD
**Goal:** [One sentence from the user's description]
**Research:** [[Wikilinks to related notes from search]]
**Status:** Draft

---

## The Problem

[Why this exists - the pain point described]

---

## What We Learned

[From research, search results, screenshots, exploration]
[If no prior research: "Starting fresh - no prior research found."]

---

## Current State

[What exists now - include if improving an existing skill]
[If net-new: Skip this section entirely]

---

## What Done Looks Like

[Paint the picture from the user's answer. Not just "it works" but what the experience IS when complete.]

---

## The Build (In Order)

### Phase 1: [Name]

**Why:** [Why this comes first]

[Details of what gets built]

**Deliverable:** [What's done when this phase completes]

---

### Phase 2: [Name]

**Why:** [Why this follows Phase 1]

[Details]

**Deliverable:** [What's done]

---

[Continue phases as needed - typically 2-4 phases]

---

## Success Criteria

- [ ] [Specific, testable criterion that proves "What Done Looks Like" is real]
- [ ] [Another criterion]
- [ ] [Keep to 3-5 checkboxes]

---

## Kill Rules

- If [condition], then [pivot action]
- If [condition], then [stop action]

---
```

### Phase 4: Save the Plan

**Routing logic:**

1. **New skill** (no existing folder in `my-skills/`):
   - Save to your Zettelkasten folder: `Zettelkasten/Skill Plan - [Name] - YYYY-MM-DD.md`
   - If no Zettelkasten folder exists, save to: `my-skills/plans/[name]-YYYY-MM-DD.md`

2. **Existing skill improvement** (folder exists in `my-skills/`):
   - Save to: `my-skills/[name]/docs/plans/[feature-name].md`

After saving, confirm:
> Plan saved to [location]. You can now:
> - Hand this to `new-skill-wizard` to create the skill
> - Start building directly using this as your guide
> - Share it for review before committing

## Integration Points

**Connects to:**
- `new-skill-wizard` - Plan becomes the blueprint for skill creation

## Guidelines

1. **Load context automatically** - The user shouldn't have to tell you to check CLAUDE.md or search for related work
2. **One question at a time** - Don't overwhelm with a form
3. **Paint pictures, not checkboxes** - "What Done Looks Like" is a vision, not a list
4. **Keep phases minimal** - 2-4 phases max. More phases = more complexity = more failure points
5. **Kill rules are real** - Every plan needs explicit "when to stop" criteria
6. **Save in the right place** - New skills to Zettelkasten, improvements to skill docs
7. **Mission-context over hard-coded context** - When a plan involves business-specific behavior (coaching terminology, session types, business roles), always design it to pull from mission-context dynamically. Never hard-code business names into skill logic. Mission-context provides your roles — use those.

## Example Interaction

**You:** "skill-plan for inbox-improver"

**Claude:**
1. Loads CLAUDE.md, invokes mission-context
2. Searches for related notes on "inbox-improver" - finds 2 related items
3. "I found related notes: 'Email Triage Research' and 'Inbox Process Notes'. Want me to pull these in?"
4. Asks: "What problem does inbox-improver solve?"
5. Asks: "What does done look like when it's working?"
6. Generates complete plan following template
7. Checks if `my-skills/inbox-improver/` exists
8. Saves to appropriate location
9. "Plan saved. Ready to hand to new-skill-wizard or start building directly."
