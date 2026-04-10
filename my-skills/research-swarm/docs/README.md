# Research Swarm — Technical Reference

## What It Does

Orchestrates multi-angle parallel research by spawning 3-5 sub-agents simultaneously, each investigating a different perspective on the same topic. Results are synthesized into a unified report with contradictions highlighted and mission relevance scored.

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
[Phase 3] Decompose into 3-5 Angles
    │   Tailored to member's coaching niche
    │
    ▼
[Phase 4] Spawn Parallel Sub-Agents (haiku)
    │   Task tool → run_in_background=true
    │   All launched in single message
    │
    ▼
[Phase 5] Gather Results
    │   TaskOutput for each agent
    │
    ▼
[Phase 6-7] Synthesize → Report
    │   Contradictions table, mission relevance, action verdicts
    │
    ▼
[Phase 8] Save
    Vault → project root fallback → offer alternative
```

## Tools Used

| Tool | Purpose |
|------|---------|
| Glob | Find mission-context, vault, daily notes, youtube-processor |
| Read | Load mission-context SKILL.md, vault notes |
| Task | Spawn parallel research sub-agents |
| TaskOutput | Retrieve sub-agent results |
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
| youtube-processor | No | Skip video research angle |
| Daily notes | No | Skip daily note linking |

## Sub-Agent Model

Sub-agents spawn as `general-purpose` with `model: "haiku"` for cost efficiency. The orchestrator (this skill) runs on whatever model the member's Claude plan provides.

## Report Output

Reports follow a consistent structure:
- Executive Summary
- Prior Knowledge (vault findings)
- Findings by Angle (with per-angle verdicts)
- Contradictions & Tensions table
- Mission Relevance (adapted to member's context)
- Action Verdicts Summary
- Learning Triggers
- Sources

## Save Location Logic

1. Vault found → save in vault root
2. No vault → `./research-reports/` in project root
3. User can override with "save this to [path]"
