# Outlier Swarm — Technical Reference

## What It Does

Orchestrates contrarian research by deploying 5 specialized agents with mutually exclusive mandates. Each agent challenges the topic from a different angle: mainstream mapping, contrarian hunting, cross-domain theft, first principles analysis, and failure archaeology. The synthesis focuses on "overlaps of surprise" — where multiple independent angles converge on the same unexpected conclusion.

## Architecture

```
User Question
    │
    ▼
[Phase 1] Load Mission Context
    │   Read my-skills/mission-context/SKILL.md
    │   Extract: niche, clients, delivery model, terminology
    │
    ▼
[Phase 2] Check Prior Knowledge
    │   Smart Connections MCP → Glob fallback → skip
    │
    ▼
[Phase 3] Deploy 5 Agents (always 5, always parallel)
    │   1. Mainstream Mapper
    │   2. Contrarian Hunter
    │   3. Cross-Domain Thief
    │   4. First Principles Assassin
    │   5. Failure Archaeologist
    │
    ▼
[Phase 4] Launch via Task tool (haiku)
    │   All 5 in single message
    │
    ▼
[Phase 5] Synthesize — Overlaps of Surprise
    │   Where do 2+ independent angles converge?
    │
    ▼
[Phase 6] Report
    │   Sacred cows, contrarian signals, convergence matrix
    │
    ▼
[Phase 7] Save
    Vault → project root fallback → offer alternative
```

## The Five Agents

| Agent | Mandate | What They Return |
|-------|---------|------------------|
| Mainstream Mapper | Map orthodoxy | Dominant beliefs, standard methods, sacred cows |
| Contrarian Hunter | Find rule-breakers who win | Names, approaches, evidence of unconventional success |
| Cross-Domain Thief | Steal solutions from other fields | 3+ cross-domain connections with reasoning |
| First Principles Assassin | Strip to causation | What matters vs. what's ritual |
| Failure Archaeologist | Dig up abandoned ideas | Ideas worth resurrecting, changed conditions |

## Tools Used

| Tool | Purpose |
|------|---------|
| Glob | Find mission-context, vault, daily notes |
| Read | Load mission-context SKILL.md, vault notes |
| Task | Spawn 5 parallel research agents |
| TaskOutput | Retrieve agent results |
| WebSearch | Sub-agents use for web research |
| WebFetch | Sub-agents use for page content |
| Write | Save final report |
| Edit | Link from daily note |
| Grep | Search vault when Smart Connections unavailable |
| AskUserQuestion | Clarify scope, confirm save location |

## Dependencies

| Dependency | Required? | Fallback |
|------------|-----------|----------|
| mission-context | No | Generic framing, tip to build it |
| Smart Connections MCP | No | Glob/Grep vault search |
| Vault/Zettelkasten | No | Skip prior knowledge check |
| Daily notes | No | Skip daily note linking |

## Sub-Agent Model

All 5 agents spawn as `general-purpose` with `model: "haiku"`. The orchestrator runs on whatever model the member's Claude plan provides.

## Convergence Matrix

The key output differentiator is the Overlaps of Surprise table — a matrix showing which insights were surfaced by multiple independent agents. An insight flagged by 3+ agents has high signal.

## Save Location Logic

1. Vault found → save in vault root
2. No vault → `./research-reports/` in project root
3. User can override with "save this to [path]"
