# Skill Development Rules

Topic-specific gotchas for building and debugging skills in Claude Code.

---

## Session Caching & Settings Refresh

Skills and settings have different refresh behavior in Claude Code:

**Settings files** (`.claude/settings.json`, `.claude/settings.local.json`):
- Changes to permissions, Skill registrations, and other settings require a **new terminal session**
- This includes adding `Skill(<name>)` to the permissions array

**Skills** (SKILL.md files):
- Changes take effect **immediately** - no restart required
- Skills are auto-discovered based on their description
- When you modify a SKILL.md file, Claude loads the updated version on the next matching request

**Practical implication:**
- Editing SKILL.md content? Just save and test - it's instant
- Adding a new skill to settings.local.json? Need new terminal session
- Changing agent definitions? Need new terminal session

---

## Permission Path Syntax (Double Slash)

Paths in `settings.local.json` permissions follow gitignore spec. **A leading `/` is relative to the settings file, not the filesystem root.**

```
WRONG: Read(/Users/yourname/**)     -> Looks for ./Users/yourname/** (relative)
RIGHT: Read(//Users/yourname/**)    -> Looks for /Users/yourname/** (absolute)
```

The double slash `//` means "absolute filesystem path". Without it, permissions silently fail because the relative path doesn't exist.

---

## Global vs Project Settings

Two settings files, different purposes:

| Location | Purpose | What Goes Here |
|----------|---------|----------------|
| `~/.claude/settings.local.json` | Universal | Read/Write/Edit home folder, WebSearch, git commands, common domains |
| `.claude/settings.local.json` | Project-specific | Skill registrations, repo scripts, project-specific Bash commands |

**Rule:** If you'd want the permission in ANY project, put it in global. Project settings add on top.

---

## Debugging Agent Failures

When an agent doesn't work as expected, **fix the skill, not the agent.**

**Diagnostic order:**
1. **Test the skill standalone** - Run trigger phrase directly, without the agent
2. **Check skill registration** - Is `Skill(<name>)` in settings.local.json?
3. **Check skill tools** - Does allowed-tools have what the skill needs?
4. **Only then check agent wiring** - Is skill in agent's `skills:` list?

**The principle:** Agents orchestrate. Skills execute. If execution fails, the skill is broken - not the orchestration.

---

## Skill Registration Checklist

**When a skill doesn't work, check these in order:**

1. Skill folder exists in `my-skills/<name>/`
2. SKILL.md has valid YAML frontmatter (starts/ends with `---`)
3. Skill name in frontmatter uses lowercase, numbers, hyphens only
4. Symlinks created in `.claude/skills/`
5. **Registered in settings:** `Skill(<name>)` in `.claude/settings.local.json`
6. Skill description is specific and includes trigger keywords
7. New terminal session started **for settings changes only** (skill file edits are instant)

Root cause 90% of the time: Step 5 is missing. The skill exists but isn't registered in settings.

---

## Claude.ai Skill Frontmatter Keys

When packaging skills for Claude.ai upload, only these frontmatter keys are valid:

| Key | Required | Purpose |
|-----|----------|---------|
| `name` | Yes | Skill identifier (lowercase, hyphens) |
| `description` | Yes | Trigger phrases and purpose |
| `allowed-tools` | No | Tools the skill can use |

**Common mistake:** Using `tools:` instead of `allowed-tools:`. The `tools:` key works in Claude Code and causes upload errors on Claude.ai.

```yaml
# WRONG - causes "unexpected key" error on Claude.ai
tools:
  - Read
  - AskUserQuestion

# RIGHT - works on both platforms
allowed-tools: Read, AskUserQuestion
```
