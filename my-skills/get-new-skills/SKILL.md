---
name: get-new-skills
description: Install new skills from the AI Powerhouse skill library. Use when "get new skills", "check for skill updates", "install new skills", "update my skills", "pull latest skills", or when Ed announces new skills are available.
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Get New Skills

Install new skills from the AI Powerhouse template repository into your Powerhouse.

---

## Prerequisites

GitHub CLI (`gh`) must be installed and authenticated.

**Check:** Run `gh auth status`

**If not installed:**
- Mac: `brew install gh`
- Windows: `winget install GitHub.cli`

**If not authenticated:**
- Run: `gh auth login`
- Choose: GitHub.com → HTTPS → Login with a web browser
- Follow the browser prompts

Do not proceed until `gh auth status` shows a logged-in account.

---

## Step 1: Fetch the Template Repo

```bash
gh repo clone ai-powerhouse-hq/ai-powerhouse-starter /tmp/powerhouse-skills-update -- --depth 1 --quiet
```

If this fails with a permission error, the user may need to accept their GitHub invitation first. Direct them to github.com/notifications.

---

## Step 2: Detect New Skills and Agents

**Skills:** List all skill folders in `/tmp/powerhouse-skills-update/my-skills/`. Compare against local `my-skills/` folders.

**Agents:** List all `.md` files in `/tmp/powerhouse-skills-update/.claude/agents/` (if the directory exists). Compare against local `.claude/agents/` files.

For each item in the template:
- **Doesn't exist locally** → NEW (will be installed)
- **Already exists locally** → SKIP (never overwrite member customizations)

Report what was found before proceeding:

```
Found [X] new skills to install:
- newsletter-coach: Writing coach that turns your experiences into newsletter drafts

Found [Y] new agents to install:
- instagram-carousel: Creates Instagram carousels from articles

[Z] skills already installed (skipping):
- mission-context, mission-context-builder
```

---

## Step 3: Install New Skills and Agents

Copy each new skill folder:

```bash
cp -r /tmp/powerhouse-skills-update/my-skills/SKILL_NAME/ ./my-skills/SKILL_NAME/
```

Copy each new agent file:

```bash
mkdir -p .claude/agents
cp /tmp/powerhouse-skills-update/.claude/agents/AGENT_NAME.md .claude/agents/AGENT_NAME.md
```

---

## Step 3.5: Wire Skills

Claude Code discovers skills via symlinks in `.claude/skills/`. For EVERY skill folder in `my-skills/` (not just newly installed ones), ensure a symlink exists:

```bash
mkdir -p .claude/skills
ln -sf "../../my-skills/SKILL_NAME" ".claude/skills/SKILL_NAME"
```

Loop through all folders in `my-skills/` and create any missing symlinks. This self-heals broken symlinks for existing skills too.

---

## Step 4: Register Skills

Read `.claude/settings.local.json`.

For each newly installed skill, add a `Skill(skill-name)` entry to the permissions allow array. Place new entries after any existing `Skill()` entries.

**Example:** If installing newsletter-coach, hook-stack-evaluator, and ai-slop-detector, add:
```
"Skill(newsletter-coach)",
"Skill(hook-stack-evaluator)",
"Skill(ai-slop-detector)",
```

Use the Edit tool to make this change. Verify the JSON is still valid after editing.

---

## Step 5: Check for New Permissions

Read the SKILL.md of each newly installed skill. Check its `allowed-tools` frontmatter.

If any tool isn't already in the settings permissions, add it:

| Tool | Permission Entry |
|------|-----------------|
| WebSearch | `"WebSearch"` |
| WebFetch | `"WebFetch"` |

`Read`, `Write`, `Edit`, `Glob`, `Bash` are typically already present. Only add what's missing.

---

## Step 6: Update Settings (If Template Has Newer Version)

Compare `.claude/settings.local.json` from the template with the local version. Check for TWO types of changes:

**6a: New permission entries**
If the template has permission entries not in the local file (beyond skill registrations), report them:

"The template also includes these new permissions: [list]. Want me to add them?"

**6b: New top-level settings (spinnerVerbs, companyAnnouncements, etc.)**
If the template has top-level keys that don't exist in the local settings file, add them automatically. These are experience enhancements, not security-sensitive.

For example, if the template has `spinnerVerbs` and local doesn't:
1. Read the `spinnerVerbs` object from the template settings
2. Add it to the local `.claude/settings.local.json` using the Edit tool
3. Report what was added: "Added custom spinner verbs to your settings — you'll see Powerhouse-themed loading messages."

If the local file already has the key (member customized it), skip it — never overwrite member customizations.

---

## Step 7: Clean Up

```bash
rm -rf /tmp/powerhouse-skills-update
```

---

## Step 8: Report

Tell the user exactly what happened:

```
Installed [X] new skills:

1. newsletter-coach - Writing coach for newsletter drafts (say "help me write a newsletter")
2. hook-stack-evaluator - Headline scoring (runs automatically inside newsletter-coach)
3. ai-slop-detector - AI pattern cleaner (runs automatically inside newsletter-coach)

Registered all skills in your settings.

NEXT STEP: Type /exit to close Claude, then type claude to relaunch.
(Stay in this Terminal window — don't open a new tab.)
The new skills activate when you start a fresh session.

Try saying: "help me write a newsletter"
```

---

## Important

- This skill NEVER overwrites existing skills. Your customizations are safe.
- To force-update a skill: delete its folder first, then run "get new skills" again.
- Skills that call other skills (like newsletter-coach calling ai-slop-detector) work automatically — no extra setup needed.
- Your Mission Context feeds into skills that need your voice — the richer your MC, the better the output.
