# CLAUDE.md - Your AI Operating Manual

## CURRENT FOCUS
<!-- Update this section each session -->
```
Working on: [What you're building today]
Why: [The leverage it creates]
Next: [What ships after this]
```

---

<!-- BUILDER:START:WHO_I_AM -->
## WHO I AM

*Run "build my mission context" to populate this section.*
<!-- BUILDER:END:WHO_I_AM -->

---

<!-- BUILDER:START:MY_CLIENTS -->
## MY CLIENTS

*Run "build my mission context" to populate this section.*
<!-- BUILDER:END:MY_CLIENTS -->

---

<!-- BUILDER:START:MY_TERMINOLOGY -->
## MY TERMINOLOGY

*Run "build my mission context" to populate this section.*

For tech-to-coaching translations, see `my-skills/mission-context/resources/terminology.md`.
<!-- BUILDER:END:MY_TERMINOLOGY -->

---

## FILE LOCATIONS

| Location | What Lives There |
|----------|------------------|
| `~/Documents/my-powerhouse/` | This repo - your AI workspace |
| *Add your key folders here as you discover them* | |

---

<!-- BUILDER:START:IRON_RULES -->
## THE IRON RULES

1. **ALWAYS EXPLAIN THE WHY.** Tell me what AND why - in plain English.

2. **MAKE FIXES AS SIMPLE AS POSSIBLE.** Impact as little code as possible. Zero new bugs.

*Run "build my mission context" to add your personal iron rules.*

**Iron Rules** = Known failure modes. Use sparingly.
**Guidelines** = Default style. Trust Claude's judgment. Upgrade to Iron Rule only after something fails.
<!-- BUILDER:END:IRON_RULES -->

---

<!-- BUILDER:START:WRITING_RULES -->
## WRITING RULES

*Run "build my mission context" to populate this section with your voice, signature phrases, and words to avoid.*
<!-- BUILDER:END:WRITING_RULES -->

---

## MY TOOLS

*Add your tools and integrations here as you set them up.*

| Tool | What It Does | Notes |
|------|-------------|-------|
| Claude Code | AI-powered terminal assistant | Your primary tool |
| GitHub | Cloud filing cabinet for code and skills | Stores your Powerhouse |
| Obsidian | Personal knowledge base | Connected notes (Zettelkasten) |

---

## WORKING NOTES

*Temporary notes, patterns you're noticing, things to revisit. Clean this up periodically.*

---

## THIS REPO: MY POWERHOUSE

This is your **personal AI workspace** - where your context, skills, and customizations live.

**Folder purposes:**
- `my-skills/` - Your AI tools (skills you build and customize)
- `my-agents/` - Your workflow orchestrators (combine skills into pipelines)
- `.claude/rules/` - Guardrails that prevent common mistakes

**How skills work:**
- `my-skills/mission-context/` contains YOUR context (who you are, your voice, your terminology)
- `my-skills/mission-context-builder/` is the tool that helps you build that context
- Future skills go in `my-skills/` - each skill is a folder with a SKILL.md file

---

## AUTONOMY BOUNDARIES

Three tiers of autonomy - know when to act, check in, or stop.

| Always (do without asking) | Ask First | Never |
|---------------------------|-----------|-------|
| Check git status before work | Structural/architectural decisions | `sed -i` on critical configs without backup |
| Use Edit tool for existing files | Choosing between valid approaches | Commit files containing secrets |
| Explain the why in plain English | Delete vs refactor decisions | Force push to main |
| Mark todos complete as you go | New external dependencies | Skip pre-commit hooks |
| | Breaking changes to skill APIs | Guess at missing parameters |

**The principle:** Graduated autonomy. You know what's free, what needs a check-in, and what's off-limits.

---

## THE WORKFLOW

### Before You Touch Code

0. **Check git status** - Know the state before touching anything
1. **Think through the problem** - Read the codebase for relevant files
2. **Write a plan** - A checklist you'll work through
3. **Check in with me** - I verify the plan before you start

### While You Work

4. **Execute the plan** - Mark complete as you go
5. **Give me high-level summaries** - What changed and why
6. **Keep changes minimal** - Every edit should be as small as possible

### When You Finish

7. **Review** - Verify it works, check quality
8. **Git sync** - Commit and push all work

### When to Stop and Ask

**STOP AND ASK:** Structural decisions, UX changes, choosing between valid approaches, something feels wrong.

**MAKE THE CALL:** Naming, minor implementation details, code organization, standard library choices.

### Communication Style

**One question at a time.** Terminal format makes multiple questions hard to answer. Give context, then ask ONE focused question. Wait for the answer before asking the next.

---

## THE COMPOUND ENGINEERING LOOP

Every session follows this cycle:

```
Plan --> Work --> Review --> Compound
  ^                           |
  +---------------------------+
```

| Phase | What Happens |
|-------|--------------|
| **Plan** | Understand task, write a checklist |
| **Work** | Execute the plan, ship code |
| **Review** | Verify it works, check quality |
| **Compound** | Extract learnings, encode back into the system |

**The magic is in Compound.** Without it, you repeat the same mistakes. With it, each session leaves the system smarter.

**How Compound works in practice:**
- When you discover something that should be standard, update this CLAUDE.md
- When you hit a topic-specific gotcha, add it to `.claude/rules/`
- When a skill needs a tweak, update the skill docs

**This is how your AI gets smarter over time.** Every session that closes the loop makes the next session better.

---

## ARCHITECTURE PHILOSOPHY

| Layer | What It Is | Who Maintains |
|-------|------------|---------------|
| **Tools** | Python scripts, APIs, Bash | Hidden inside skills |
| **Skills** | SKILL.md with instructions | Edit markdown to change |
| **Agents** | Orchestrators pulling skills | Reference skills, not tools |

**The Golden Rule:**
```
WRONG: Agent -> has Bash -> calls tool directly
RIGHT: Agent -> pulls Skill -> Skill contains tool instructions -> Claude executes
```

**Why:** Fix one skill, not 58 agents. Skills encapsulate complexity. Non-coders edit markdown, not code.

**Tool Access Rule:** Skills tell Claude what to run. Agents grant permission to run it. Agents need `Bash` in tools if skills require it.

---

## SKILL ISOLATION (Anti-Contamination)

When working on a specific skill:

| Always | Ask First | Never |
|--------|-----------|-------|
| Scope changes to that skill's folder | Modify shared utilities | Touch other skill directories |
| Load skill-specific CLAUDE.md if present | Add cross-skill dependencies | "Fix" code in unrelated skills |
| Commit skill changes separately | Refactor multiple skills at once | Assume permission extends beyond current skill |

**The rule:** One skill at a time. Commit before switching. If you need to modify another skill, ASK FIRST.

### Skill-Specific CLAUDE.md

Skills can have their own CLAUDE.md in their root folder. Claude loads these on-demand when working in that directory.

**When to add skill-level CLAUDE.md:**
- The skill has complex internal structure
- You want extra protection for a production skill

---

## KILL RULES

Stop and pivot when:
- We've looped on the same bug 3+ times
- The "simple fix" keeps getting more complex
- My energy drops (I'll tell you)
- 90 minutes on a prototype with no working v1

---

## GETTING NEW SKILLS

When Ed releases new skills, say **"get new skills"** to install them.

This uses the `get-new-skills` skill in your `my-skills/` folder. It connects to the AI Powerhouse template repo, detects what's new, installs the skills, and registers them in your settings.

**Requires:** GitHub CLI (`gh`) installed and authenticated. If you don't have it:
- Mac: `brew install gh` then `gh auth login`
- Windows: `winget install GitHub.cli` then `gh auth login`

**After installing new skills:** Open a new terminal session for them to activate.

**First time / skill not found?** If Claude doesn't recognize "get new skills" yet, paste this prompt:

> Install the latest skills from the AI Powerhouse template repo (github.com/ai-powerhouse-hq/ai-powerhouse-starter). Clone it to /tmp, copy any new skill folders from my-skills/ that I don't already have into my local my-skills/, register them in .claude/settings.local.json, clean up the temp folder, and tell me what was installed. Include the get-new-skills skill itself if I don't have it yet.

---

## WHERE TO FIND MORE

| Topic | Location |
|-------|----------|
| Your context, terminology, voice | `my-skills/mission-context/` |
| Topic-specific gotchas | `.claude/rules/` |
| Your skills | `my-skills/` |
| Your workflow orchestrators | `my-agents/` |

---

## CONTENT HIERARCHY

When updating system docs, route by type:

| Finding Type | Target |
|--------------|--------|
| Universal workflow rule | CLAUDE.md |
| Topic-specific gotcha | `.claude/rules/<topic>.md` |
| Skill-specific pattern | `my-skills/<skill>/docs/` |
| Reference data (terminology) | `my-skills/mission-context/resources/` |

**The test:** "Does this apply to EVERY session, regardless of task?" Yes -> CLAUDE.md. No -> rules/ or skill docs.

---

## LIVING DOCUMENT

This file evolves. When you discover something that should be standard, add it here - only if it's universal.

**Last updated:** February 2026
**Version:** 1.0 - Initial setup
