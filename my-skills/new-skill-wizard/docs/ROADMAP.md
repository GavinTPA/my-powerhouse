# New Skill Wizard - Roadmap

## What's Shipped

| Version | Date | What Changed |
|---------|------|--------------|
| v1.0 | 2025-12 | Initial wizard with git workflow |
| v1.1 | 2026-01 | Added docs/ folder to created structure |
| v1.2 | 2026-01 | Added settings.local.json registration step |
| v1.3 | 2026-01 | Added testing plan generation |
| v1.4 | 2026-01 | Added docs/ folder (README, GUIDE, ROADMAP) |
| v1.5 | 2026-02-06 | Added post-creation verification step |

## The Vision

Right now, the wizard creates skills and walks you through development interactively. You're in the loop for every decision.

The vision: template-based skill generation. "Create a review skill like magic-model-review but for [X]." Clone patterns, not just structure.

## Planned Improvements

These are on the list. Not "someday maybe" - actually planned.

- [ ] **Skill Templates** - Pre-built patterns for common skill types:
  - Review skills (like magic-model-review, offer-diamond-review)
  - Triage skills (like capture-triage)
  - Generator skills (like onboarding-doc-builder)

- [ ] **Dependency Detection** - If a skill mentions "run through ai-slop-detector," automatically verify ai-slop-detector is registered.

- [x] **Post-Creation Verification** - After wiring up, automatically test that the skill is discoverable. *(Shipped 2026-02-06)*

## Ideas (Not Committed)

These are interesting but not proven necessary yet. Parking lot stuff.

- **Skill Conversion** - Turn a ChatGPT custom GPT into a Claude skill. Parse the instructions, adapt the format.

- **Agent Wizard** - Similar process for creating agents. Different structure, same automation.

- **Skill Health Check** - Scan all skills for common problems: missing registration, outdated dependencies, broken references.

- **Interactive Testing** - Built-in test runner that executes the testing plan and reports results.

- **Skill Analytics** - Track which skills are used most, which have errors, which need updates.

- **Auto-Upload to Claude.ai** - After `package-skill.sh` creates the ZIP, optionally upload to claude.ai via browser automation (Chrome tools). Must be opt-in — not all skills work in claude.ai's sandbox (no Bash, no external APIs, no filesystem access). Would navigate Settings → Features → Upload.

## What We've Learned

Building this wizard taught us a few things:

**Registration is the silent killer.** Skills that "don't work" almost always have a registration problem. Adding that step to the wizard eliminated most support issues.

**Documentation as part of creation.** When docs are optional, they get skipped. Making them automatic means every skill ships complete.

**Testing plans prevent debugging.** A checklist of "did you do X?" catches problems before they become mysteries.

**One question at a time.** Asking for name, description, and triggers all at once overwhelms. One at a time keeps momentum.

**Git workflow prevents disasters.** Always branching from main means you can throw away bad experiments. The wizard enforces this discipline.

## Decision Log

When we make significant changes, the plan lives in `plans/` and the decision rationale gets archived in `plans/archive/`. That way we remember WHY we did things, not just what we did.
