# Get New Skills - Technical Reference

## What It Does

Connects to the AI Powerhouse template repository, detects new skills, installs them locally, and registers them in settings. The delivery pipeline for all future Powerhouse skills.

## Architecture

```
get-new-skills/
├── SKILL.md              # Main skill definition (8-step install process)
└── docs/
    ├── README.md         # This file
    ├── GUIDE.md          # Business-friendly explanation
    └── ROADMAP.md        # Future ideas
```

## Dependencies

**Tools required:**
- `Read` - Reads local settings files
- `Write` - Creates new skill folders if needed
- `Edit` - Updates settings.local.json
- `Bash` - Runs gh CLI commands (clone, cleanup)
- `Glob` - Compares local vs remote skill folders

**External requirements:**
- GitHub CLI (`gh`) installed and authenticated
- Member of `ai-powerhouse-hq` GitHub organization (grants Read access to `ai-powerhouse-hq/ai-powerhouse-starter`)

## Usage

**Trigger phrases:**
- "Get new skills"
- "Check for skill updates"
- "Install new skills"
- "Update my skills"
- "Pull latest skills"

**Input:** None required — the skill knows where to look.

**Output:** Summary of what was installed, with trigger phrases for each new skill.

## The 8-Step Process

| Step | Purpose |
|------|---------|
| 1. Fetch | Clone template repo to /tmp |
| 2. Detect | Compare remote vs local skill folders |
| 3. Install | Copy new skill folders to my-skills/ |
| 4. Register | Add Skill() entries to settings.local.json |
| 5. Permissions | Check for new tool permissions needed |
| 6. Settings | Report any template settings changes |
| 7. Clean up | Remove temp clone |
| 8. Report | Tell user what was installed and what to say |

## Safety

- **Never overwrites existing skills.** Only installs folders that don't exist locally.
- **To force-update:** Delete the skill folder first, then run "get new skills" again.
- **Customisations are safe.** If you've edited a SKILL.md, it won't be touched.

## Testing

**Manual verification:**
1. Invoke with "get new skills"
2. Verify it clones the template repo
3. Confirm it skips existing skills
4. Check settings.local.json has new Skill() entries
5. Verify temp folder is cleaned up

## Related Skills

All skills in the Powerhouse are delivered through this mechanism. It's the install pipeline, not a content skill.
