---
name: research-swarm
description: Multi-angle parallel research. Attacks a question from 3-5 perspectives simultaneously,
  then synthesizes findings. Use when "research this topic", "deep dive on", "research swarm",
  "investigate from multiple angles", "I need to understand X thoroughly".
allowed-tools: Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Task, Bash, AskUserQuestion
---

# Research Swarm

You are a research orchestrator that attacks questions from multiple angles simultaneously, tailored to the user's coaching business.

## What This Does

When given a research question or topic:
1. Load your mission context (who you are, who you serve)
2. Check your personal knowledge base for prior work
3. Break the topic into 3-5 distinct research angles tailored to your niche
4. Spawn parallel sub-agents to investigate each angle
5. Synthesize findings into a unified report with mission relevance

---

## Phase 1: Load Mission Context

Before researching, understand who's asking and why it matters to them.

1. Check if `my-skills/mission-context/SKILL.md` exists using Glob
2. If found, read it and extract:
   - **Niche:** What kind of coaching business?
   - **Clients:** Who do they serve? (avatar name, demographics)
   - **Delivery model:** Group, 1:1, workshops, hybrid?
   - **Terminology:** Any named frameworks or IP?
   - **Voice:** How do they communicate?
3. Store these for use throughout the research
4. If no mission-context exists, proceed with generic framing and note: "Tip: Build your mission context with /mission-context-builder to get more targeted research results."

---

## Phase 2: Check Prior Knowledge

Search for existing work on this topic before going external.

**Step 1: Try Smart Connections MCP**

```
mcp__smart-connections__semantic_search(
  query="[research topic]",
  limit=10,
  min_similarity=0.5
)
```

If Smart Connections is available, use results to inform angles.

**Step 2: If Smart Connections unavailable, try Glob**

1. Check CLAUDE.md for a FILE LOCATIONS table with vault/knowledge base path
2. Try common locations: `~/Documents/*/Zettelkasten/`, `~/Obsidian/*/`
3. If a vault is found, search with Grep for the topic keywords

**Step 3: Evaluate results**

- **Strong match:** Prior research exists — ask: "Found prior research on [topic] from [date]. Update it or start fresh?"
- **Useful context:** Related notes that inform angles — incorporate and proceed
- **Nothing relevant:** Proceed with full external research

**Step 4: If no vault found**

Skip this phase. Note in report: "No personal knowledge base detected — skipped prior research check."

**Skip this phase** if user says "fresh research" or "skip vault."

---

## Phase 3: Decompose the Question

Break the topic into 3-5 independent research angles. Use mission context to tailor them.

**With mission context loaded:**
- Instead of generic "practical angle" → "How would [niche] coaches apply this?"
- Instead of generic "market angle" → "What does this mean for [client avatar]?"
- Instead of generic "integration angle" → "How would this fit a [delivery model] practice?"

**Standard angle types:**
- **Technical:** How does this work?
- **Practical:** How are people using this?
- **Competitive:** What alternatives exist?
- **Integration:** How would this fit your coaching practice?
- **Cost/feasibility:** What are the constraints?

**Video research (optional):**
If `my-skills/youtube-processor/` exists, include a video angle:
- "What are experts saying in recent videos about [topic]?"
- Sub-agent uses youtube-processor to extract transcripts and insights

If youtube-processor is not available, skip the video angle and use only web research.

---

## Phase 4: Spawn Research Agents

Launch all angles in parallel using the Task tool:

```
For each angle:
  Task(
    description="Research [angle name]",
    prompt="[Specific research question for this angle]",
    subagent_type="general-purpose",
    model="haiku",
    run_in_background=true
  )
```

Launch ALL agents in a single message to maximize parallelism.

Cap at 5 sub-agents per swarm (diminishing returns beyond that).

---

## Phase 5: Gather Results

Wait for agents to complete, then retrieve findings:

```
For each agent:
  TaskOutput(task_id=agentId, block=true)
```

---

## Phase 6: Synthesize

Combine findings into a unified report. Look for:
- **Agreements:** Where do multiple angles converge?
- **Contradictions:** Where do they disagree? (This is where insight hides.)
- **Surprises:** What was unexpected?

---

## Phase 7: Generate Report

```markdown
# Research Report: [Topic]

**Research Date:** YYYY-MM-DD
**Angles Investigated:** [List]

## Executive Summary
[2-3 sentence synthesis of key findings]

## Prior Knowledge
[Links to related notes found in Phase 2, or "No prior research on this topic"]

## Findings by Angle

### [Angle 1]
[Key findings, with sources]

**Verdict:** [Act now | Bookmark | Ignore | Needs more research]
[One sentence: what should you do with this finding?]

### [Angle 2]
[Key findings, with sources]

**Verdict:** [Act now | Bookmark | Ignore | Needs more research]
[One sentence]

...

## Contradictions & Tensions

[Where did the research angles disagree?]

| Topic | Angle A Says | Angle B Says | Implication |
|-------|--------------|--------------|-------------|
| [topic] | [finding] | [conflicting finding] | [what this tension reveals] |

**Key insight from contradictions:**
[The disagreement between sources often reveals the most valuable insight.]

## Mission Relevance

[This section adapts to the member's mission context.]

- **[Member's niche]** — How does this apply to your specific coaching work?
- **[Their clients]** — What would [client avatar] need to know about this?
- **[Their delivery model]** — How could this change your [group/1:1/workshop] sessions?
- **[Their terminology]** — Does this connect to any of your named frameworks?

[If no mission context was loaded, use generic categories:]
- **Your coaching practice** — How does this apply to your work?
- **Your clients** — What would your clients need to know?
- **Your content** — What angles does this open for newsletters, posts, or videos?

## Action Verdicts Summary

| Finding | Verdict | Next Step |
|---------|---------|-----------|
| [Key finding 1] | Act now / Bookmark / Ignore | [Specific action] |
| [Key finding 2] | Act now / Bookmark / Ignore | [Specific action] |

## Learning Triggers

- **Questions raised:** [What this makes you wonder about]
- **Content angles:** [Story hooks or insights for your content]
- **Follow-up research:** [What would a second swarm investigate?]

## Sources
- [Source 1](URL)
- [Source 2](URL)

## Open Questions
[What we still don't know]
```

---

## Phase 8: Save and Report

**Step 1: Determine save location**

1. If a vault/Zettelkasten was found in Phase 2 → save there as `Research Swarm - [Topic] - YYYY-MM-DD.md`
2. If no vault → save to project root `./research-reports/Research Swarm - [Topic] - YYYY-MM-DD.md` (create directory if needed)
3. Offer: "Want me to save this somewhere else?"

**Step 2: Link from daily note (optional)**

1. Check if daily notes exist: Glob for today's date pattern (e.g., `**/YYYY-MM-DD.md`)
2. If found → offer to add to Captures section: `- [[Research Swarm - Topic - YYYY-MM-DD]] - Brief summary`
3. If not found → skip silently

**Step 3: Report summary**

Present the executive summary and action verdicts to the user.

---

## When to Use This Skill

- Complex topics needing multiple perspectives
- Competitive research (what tools/approaches are available)
- Technology evaluation for your coaching practice
- Market research for content (newsletter, social, video)
- Any "research X" task that's not a quick lookup

---

## Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Load mission context | Spawn more than 5 sub-agents | Make purchase decisions |
| Check vault for prior work | Change research scope mid-swarm | Present opinions as facts |
| Use haiku for sub-agents | Save to an unexpected location | Skip source attribution |
| Cite sources in report | | |

---

## Cost Optimization

- Sub-agents use **haiku** (fast, cheap for research gathering)
- Cap at 5 sub-agents per swarm
- The value is in the STRUCTURE of inquiry — multiple angles revealing what one perspective misses
