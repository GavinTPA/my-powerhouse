# skill-plan - Technical Reference

## What It Does

Creates structured implementation plans before building skills or features. Bridges the gap between research (research-swarm) and creation (new-skill-wizard) by formalizing the planning phase with consistent structure.

## Dependencies

**Tools required:** Read, Write, Edit, Glob, Grep, WebSearch, WebFetch

**MCP servers (optional):**
- `smart-connections` - For semantic search of your Knowledge Vault (falls back to Glob/Grep if unavailable)

**Related skills:**
- `mission-context` - Loaded for your terminology and frameworks
- `new-skill-wizard` - Plans guide skill creation

## Usage

**Trigger phrases:**
- "plan this skill"
- "create a plan for [name]"
- "skill-plan for [description]"
- "I want to plan before building"

**Input options:**
- Skill/feature name and description
- Optional: Research swarm document, screenshots, prior notes

**Output:**
- Structured markdown plan document
- Saved to Zettelkasten (new skills) or skill docs folder (improvements)

## File Locations

| Scenario | Save Location |
|----------|---------------|
| New skill | `Zettelkasten/Skill Plan - [Name] - YYYY-MM-DD.md` (or `my-skills/plans/` if no Zettelkasten) |
| Existing skill improvement | `my-skills/[name]/docs/plans/[feature].md` |

## Testing

### Basic invocation
```
"skill-plan for test-skill"
```
Expected: Claude loads context, runs semantic search, asks questions, generates plan.

### With existing skill
```
"create a plan for improving inbox-triage"
```
Expected: Plan saves to `my-skills/inbox-triage/docs/plans/` since folder exists.

### Verify template compliance
- Plan should have all sections: Problem, What We Learned, What Done Looks Like, The Build, Success Criteria, Kill Rules
- "What Done Looks Like" should be a vision/picture, not just checkboxes
