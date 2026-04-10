---
name: new-skill-wizard
description: Creates a new skill in your Powerhouse skills library with proper file structure and wiring. Use when the user wants to create a new skill, add a skill, build a skill, or says "new skill called X".
allowed-tools: Read, Write, Bash, Glob, Grep
---

# New Skill Wizard

You help users create new skills in their Powerhouse skills library. You handle all the file creation and wiring automatically.

## WHEN TO ACTIVATE

Trigger on phrases like:
- "Create a new skill"
- "I want to make a skill for..."
- "New skill called..."
- "Add a skill"
- "Build a skill"

## THE PROCESS

### Step 1: Get the Basics

If the user hasn't provided these, ask ONE question at a time:

1. **Skill name** (kebab-case like `brand-voice` or `client-intake`)
2. **What it does** (one sentence)
3. **When to use it** (trigger phrases)

If they give you everything upfront, skip the questions.

### Step 2: Prepare (Do This Automatically)

Make sure you're in the Powerhouse directory and on main:

```bash
cd ~/Documents/my-powerhouse
git pull origin main 2>/dev/null || true
```

Tell them: "Ready to create your skill."

### Step 3: Create the Skill Files (Do This Automatically)

```bash
# Create skill folder with all subdirectories including docs/
mkdir -p my-skills/<name>/{scripts,references,assets,docs/plans/archive}

# Add .gitkeep files so empty folders are tracked
touch my-skills/<name>/scripts/.gitkeep
touch my-skills/<name>/references/.gitkeep
touch my-skills/<name>/assets/.gitkeep
touch my-skills/<name>/docs/plans/.gitkeep
touch my-skills/<name>/docs/plans/archive/.gitkeep
```

**Create documentation files (part of shipping, not a follow-up):**

Create `my-skills/<name>/docs/README.md`:
```markdown
# <Name> - Technical Reference

## What It Does
[One paragraph description]

## Dependencies
**Tools required:** [List from allowed-tools]

## Usage
**Trigger phrases:**
- [phrase 1]
- [phrase 2]

## Testing
[How to verify it works]
```

Create `my-skills/<name>/docs/GUIDE.md`:
```markdown
# <Name> - How It Works

## The One-Sentence Version
[Elevator pitch]

## Why This Exists
[The problem it solves - use business analogies]

## How You Use It
[Step by step, in human terms]
```

Create `my-skills/<name>/docs/ROADMAP.md`:
```markdown
# <Name> - Roadmap

## Shipped
| Version | Date | What Changed |
|---------|------|--------------|
| v1.0 | [today] | Initial release |

## Planned
- [ ] [Future improvement ideas]

## Ideas (Not Committed)
- [Parking lot stuff]

## What We've Learned
[To be filled in as we use it]
```

Create `my-skills/<name>/SKILL.md`:

```yaml
---
name: <name>
description: <their description>. Use when <their trigger phrases>.
allowed-tools: Read, Glob, Grep, WebSearch, WebFetch
---

# <Name in Title Case>

## What This Does
<Their one-sentence description>

## Instructions

[We'll develop this together]

## Examples

[To be added after testing]

## Guidelines

- [To be defined]
```

**YAML Frontmatter Rules (Anthropic Spec):**

Only 4 fields are supported:

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | kebab-case, match directory name |
| `description` | Yes | What it does + when to use (max 1024 chars) |
| `allowed-tools` | No | **Tool names only** - not other skills |
| `model` | No | Specific Claude model if needed |

**`allowed-tools` contains ONLY actual tools:**
- Valid: `Read, Write, Edit, Glob, Grep, Bash, WebFetch, WebSearch`
- Valid patterns: `Bash(python:*)`, `WebFetch(domain:github.com)`
- **NOT valid**: Other skill names like `ai-slop-detector`

**Skill chaining:** If a skill says "run through ai-slop-detector" in the instructions,
Claude will invoke that skill automatically. Do NOT put other skills in `allowed-tools`.

**Keep SKILL.md under 500 lines.** Use progressive disclosure: essential instructions
in SKILL.md, detailed docs in `references/` folder.

**Folder structure created:**
```
my-skills/<name>/
├── SKILL.md              # The skill instructions
├── docs/
│   ├── README.md         # Technical reference (for Claude)
│   ├── GUIDE.md          # Business-friendly (your voice, analogies)
│   ├── ROADMAP.md        # Shipped history + future ideas
│   └── plans/            # Improvement plans
│       └── archive/      # Completed plans (decision log)
├── scripts/              # Executable code (Python, Bash)
├── references/           # Docs Claude loads when needed
└── assets/               # Static resources (templates, images, data)
```

**Documentation is part of creation.** The docs/ folder enables the autonomous improvement
cycle - Claude can read ROADMAP.md and README.md to understand how to improve the skill.

### Step 4: Wire It Up (Do This Automatically)

**4a: Create symlink:**
```bash
cd .claude/skills && ln -sf "../../my-skills/<name>" "<name>" && cd ../..
```

**4b: Register with Claude Code (CRITICAL):**
Add `"Skill(<name>)"` to `.claude/settings.local.json` in the `permissions.allow` array.

```bash
# Example: For a skill called "brand-voice"
# Add this line to settings.local.json:
"Skill(brand-voice)"
```

**Why this matters:** The symlinks make the skill *visible*, but Claude Code won't *use* it
unless it's registered in settings.local.json. This is the most common reason a skill
doesn't work.

Tell them: "Skill is now wired up. You'll need to start a new terminal session for Claude Code to recognize it."

### Step 5: Develop the Content Together

Ask:
> Now let's build out what this skill actually does.
>
> When someone triggers this skill, what should I do step-by-step?

Work with them to fill in:
- Instructions (the core logic)
- Examples (what good output looks like)
- Guidelines (rules to follow)

Update the SKILL.md as you go.

**Also update the docs/ files as you develop:**
- `docs/README.md` - Fill in technical details as they emerge
- `docs/GUIDE.md` - Write the "why" explanation in your voice with analogies
- `docs/ROADMAP.md` - Add any future ideas that come up during development

The docs should be complete by the time you ship, not added later.

### Step 5.5: API Gotcha Inheritance

If the skill calls any external APIs:

1. Ask: "Does this skill call any external APIs?" (e.g., GHL, Zoom, Slack, Gemini, Google Sheets)
2. If yes → create `docs/api-gotchas.md` with a starter template:
   ```markdown
   # API Gotchas — <skill-name>

   Known platform-specific issues that affect this skill. Updated as you discover them.

   ## [API Name]
   - [Gotcha 1]
   - [Gotcha 2]
   ```
3. Add a reference line to SKILL.md: `Before making API calls, read docs/api-gotchas.md for known platform gotchas.`
4. Tell them: "Created api-gotchas.md. As you use this skill, lets-wrap will capture any API issues here."

If the skill doesn't call external APIs, skip this step silently.

### Step 6: Create Testing Plan

Before testing, create a testing plan the user can execute:

```markdown
## Testing Plan for <skill-name>

### Pre-flight Checks
- [ ] Skill appears in `.claude/skills/` symlinks
- [ ] Skill registered in `settings.local.json`
- [ ] New terminal session started (settings refresh)

### Skill Discovery Test
- [ ] Run: "What skills are available?"
- [ ] Expected: <skill-name> appears in list with correct description

### Basic Invocation Test
- [ ] Run: "<trigger phrase>"
- [ ] Expected: Skill activates, follows instructions

### Happy Path Test
- [ ] Input: <typical input scenario>
- [ ] Expected output: <what should happen>

### Edge Case Tests
- [ ] Empty input: <what should happen>
- [ ] Missing data: <what should happen>

### Integration Test (if skill uses other skills/tools)
- [ ] Verify dependent skills are also registered
- [ ] Test full workflow end-to-end
```

Save this plan to `my-skills/<name>/references/TESTING.md` so it persists.

**Lesson learned:** Always test the skill ALONE before testing it inside an agent.
If the skill doesn't work standalone, adding it to an agent won't fix it.

### Step 7: Execute Tests

Tell them:
> Ready to test! Start a fresh terminal session, then run through the testing plan.
> Come back and tell me what needs adjusting.

### Step 8: Save Your Work (When They're Happy)

```bash
git add my-skills/<name>/ .claude/skills/<name> .claude/settings.local.json
git commit -m "feat: Add <name> skill"
git push origin main
```

Tell them: "`<name>` is now saved and backed up."

### Step 9: Post-Creation Verification

Run this automatically after wiring (Step 4) completes. It catches the problems that cause "my skill doesn't work" before the user hits them.

**9a: Check registration:**
```bash
grep -q 'Skill(<name>)' .claude/settings.local.json && echo "Registration: OK" || echo "Registration: MISSING"
```

**9b: Check YAML frontmatter:**
Read the `my-skills/<name>/SKILL.md` file and verify:
- Starts with `---` on line 1
- Has a closing `---` within the first 10 lines
- Contains `name:` field matching the skill directory name
- Contains `description:` field that is non-empty

Report: `Frontmatter: OK` or `Frontmatter: INVALID - [what's wrong]`

**9c: Check symlink:**
```bash
test -L .claude/skills/<name> && test -e .claude/skills/<name> && echo "Symlink: OK" || echo "Symlink: MISSING"
```

**9d: Report the checklist:**

```
Skill Verification: <name>
─────────────────────────
Registration:    OK / MISSING
Frontmatter:     OK / INVALID
Symlink:         OK / MISSING
```

**If anything is MISSING or INVALID:** Offer to fix it automatically.
- Missing registration → add `Skill(<name>)` to `.claude/settings.local.json`
- Invalid frontmatter → show what's wrong and fix it
- Missing symlink → create it: `cd .claude/skills && ln -sf "../../my-skills/<name>" "<name>"`

**Note:** Settings changes (registration) require a new terminal session to take effect. Skill file edits are instant.

## IMPORTANT RULES

1. **Do the file setup automatically** - don't make them run commands
2. **Ask questions one at a time** - don't overwhelm
3. **Show them what you created** - paste the SKILL.md content so they can see it
4. **Keep iterating** - update the file as they refine the instructions
5. **Celebrate when done** - this is a big deal, they just shipped a skill!
6. **Mission-context over hard-coded context** - When the skill needs business-specific behavior (terminology, coaching frameworks, business roles), design it to read from mission-context dynamically. Never hard-code business names into the skill logic. Mission-context provides your roles and vocabulary — use those.
