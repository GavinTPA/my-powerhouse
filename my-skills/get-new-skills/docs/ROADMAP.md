# Get New Skills - Roadmap

## What's Shipped

| Version | Date | What Changed |
|---------|------|--------------|
| v1.0 | 2026-02-09 | Initial skill — full install pipeline with detection, registration, and reporting |
| v1.1 | 2026-02-10 | Added docs/ folder (README, GUIDE, ROADMAP) |

## The Vision

Right now, "get new skills" installs new skills from the template repo. Simple and reliable.

As the AI Powerhouse skill library grows, this becomes the delivery backbone for everything. One command keeps every member current.

## Planned Improvements

- [ ] **Update Detection** — Currently only detects new skills (folders that don't exist locally). Could also detect when a skill has been updated in the template and offer to pull the latest version without overwriting customisations.

- [ ] **Changelog Display** — When new skills arrive, show a brief "what's new" summary pulled from each skill's ROADMAP.md. So you know what you're getting before you restart.

## Ideas (Not Committed)

- **Version Tracking** — Store a local version number per skill so update detection can compare versions instead of just folder existence.

- **Selective Install** — "Get new skills" installs everything. Could offer "install newsletter-coach" for picking specific skills.

- **Rollback** — If an update breaks something, offer "roll back newsletter-coach to previous version."

## What We've Learned

**Simple beats clever.** The whole install process is just: clone, compare folders, copy what's new, register, clean up. No package managers, no version databases, no dependency resolution. It works because skills are self-contained folders.

**Never overwrite.** The golden rule. Members will customise their skills — tweak a prompt, adjust a resource file. Overwriting would destroy their work. New installs only.
