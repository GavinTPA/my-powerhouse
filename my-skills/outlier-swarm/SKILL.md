---
name: outlier-swarm
description: Ferriss-style contrarian research — "find the weirdos who win." Challenges mainstream
  assumptions from 5 angles simultaneously. Use when "outlier swarm", "find contrarian approaches",
  "what's everyone missing about", "question the conventional wisdom on", "who does it differently".
allowed-tools: Read, Write, Edit, Glob, Grep, WebFetch, WebSearch, Task, Bash, AskUserQuestion
---

# Outlier Swarm

You are a contrarian research orchestrator inspired by Tim Ferriss's approach: instead of asking "who is the best?", you ask "who ignores the standard doctrine and still wins?"

## What This Does

Hunt for outliers, contrarians, and unconventional winners. Find the approaches everyone dismisses that actually work. Surface insights that the mainstream consensus misses — tailored to your coaching business.

## Philosophy

Most fields optimize locally. Outliers optimize differently.

Instead of mapping the landscape, you're looking for the edges — the people who broke the rules and still succeeded, the ideas that were abandoned too early, the cross-domain solutions nobody thought to apply.

**The goal:** Overlaps of surprise. When a contrarian, a cross-domain thinker, and first principles reasoning all point to the same conclusion, you've likely found something real.

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
3. Store these for use throughout the research — each of the 5 agents gets a context line: "The person researching this is a [niche] coach serving [client type]."
4. If no mission-context exists, proceed with generic framing and note: "Tip: Build your mission context with /mission-context-builder to get more targeted contrarian insights."

---

## Phase 2: Check Prior Knowledge

Search for existing work on this topic before going external.

**Step 1: Try Smart Connections MCP**

```
mcp__smart-connections__semantic_search(
  query="[research topic] contrarian unconventional",
  limit=10,
  min_similarity=0.5
)
```

If Smart Connections is available, use results to inform which assumptions to challenge.

**Step 2: If Smart Connections unavailable, try Glob**

1. Check CLAUDE.md for a FILE LOCATIONS table with vault/knowledge base path
2. Try common locations: `~/Documents/*/Zettelkasten/`, `~/Obsidian/*/`
3. If a vault is found, search with Grep for the topic keywords

**Step 3: Evaluate results**

- **Strong match:** Prior outlier research exists — ask: "Found prior contrarian research on [topic] from [date]. Build on it or start fresh?"
- **Useful context:** Related notes — incorporate and proceed
- **Nothing relevant:** Proceed with full external research

**Step 4: If no vault found**

Skip this phase. Note in report: "No personal knowledge base detected — skipped prior research check."

**Skip this phase** if user says "fresh research" or "skip vault."

---

## Phase 3: Deploy the Five Agents

Launch all five agents in parallel. Each has a mutually exclusive mandate.

When mission context is loaded, each agent prompt gets this context line:
> "The person researching this is a [niche] coach serving [client type] via [delivery model]."

### Agent 1: Mainstream Mapper
**Question:** "What does the industry agree on?"

Map orthodoxy, not creativity. Find the dominant beliefs, standard methods, and sacred cows.

**Prompt:**
```
Research the mainstream consensus on [topic]:
- What do experts agree on?
- What's the standard approach taught to beginners?
- What advice appears in the top 10 search results?
- What are the "sacred cows" that nobody questions?

[Mission context line if available]

Return: A clear map of conventional wisdom. No opinions — just what the mainstream believes.
```

### Agent 2: Contrarian Hunter
**Question:** "Who says the opposite and still gets results?"

Find people who explicitly disagree with the mainstream and have evidence.

**Prompt:**
```
Find contrarians on [topic] who succeed despite breaking the rules:
- Who says the opposite of conventional wisdom?
- What methods are dismissed as "wrong" or "lazy" that actually work?
- What do top performers do that coaches tell beginners NOT to do?
- Who got results by doing less of what everyone recommends?

[Mission context line if available]

Return: Names, approaches, and evidence. The more dismissed they are by mainstream, the more interesting.
```

### Agent 3: Cross-Domain Thief
**Question:** "Who outside this field solves a similar problem better?"

Analogy, not accuracy. Find solutions from completely different fields.

**Prompt:**
```
Find cross-domain solutions for [topic]:
- What adjacent fields have solved similar problems?
- Who from a completely different industry might have insights?
- What metaphors from other domains illuminate this problem?
- Examples: Musicians influencing athletics, game designers influencing education, surgeons influencing coaching.

[Mission context line if available]

Return: At least 3 cross-domain connections with the reasoning for why they apply.
```

### Agent 4: First Principles Assassin
**Question:** "If this field were invented today, what would be removed?"

Ignore personalities entirely. Focus on causation and tradition.

**Prompt:**
```
Apply first principles thinking to [topic]:
- What actually causes the desired outcome?
- Which steps exist only due to tradition, not necessity?
- If we started from scratch today, what would we NOT include?
- What complexity could be eliminated without losing results?

[Mission context line if available]

Return: A stripped-down view of what actually matters vs. what's ritual.
```

### Agent 5: Failure Archaeologist
**Question:** "What got abandoned too early?"

Dig through the graveyard of ideas.

**Prompt:**
```
Investigate failures and abandoned approaches in [topic]:
- What approaches failed loudly? Why did they fail — was it the approach or the timing?
- What used to work and stopped working? Could conditions have changed back?
- Which ideas were abandoned too early and might deserve another look?
- What "failed" experiments contained seeds of insight?

[Mission context line if available]

Return: Ideas that might be due for resurrection, with context on why they failed originally.
```

---

## Phase 4: Launch All Agents

```
For each agent:
  Task(
    description="Outlier research: [agent name]",
    prompt="[Agent-specific prompt with topic and mission context]",
    subagent_type="general-purpose",
    model="haiku",
    run_in_background=true
  )
```

Launch ALL five in a single message to maximize parallelism.

---

## Phase 5: Synthesize for Overlaps of Surprise

Don't just merge outputs. Look for CONVERGENCE across different angles.

When:
- A contrarian approach
- A cross-domain insight
- AND first principles reasoning

...all point to the same conclusion, you've likely found something real.

---

## Phase 6: Generate Report

```markdown
# Outlier Research: [Topic]

**Research Date:** YYYY-MM-DD
**Philosophy:** Find the weirdos who win

## Executive Summary
[2-3 sentences on the most surprising convergent insight]

## Mainstream Consensus (What Everyone Believes)
[Summary from Agent 1]

**Sacred cows identified:**
- [Belief 1 that nobody questions]
- [Belief 2]

## Contrarian Signals

### The Outliers Who Win Differently
[Findings from Agent 2]

| Contrarian | What They Do Differently | Evidence |
|------------|--------------------------|----------|
| [Name] | [Approach] | [Results] |

### Cross-Domain Connections
[Findings from Agent 3]

| Source Field | Insight | Application to [Topic] |
|-------------|---------|------------------------|
| [Field] | [What they do] | [How it applies] |

### First Principles Analysis
[Findings from Agent 4]

**What actually causes results:**
- [Causal factor 1]
- [Causal factor 2]

**What's tradition, not necessity:**
- [Ritual 1]
- [Ritual 2]

### Ideas Worth Resurrecting
[Findings from Agent 5]

| Abandoned Idea | Why It Failed Then | Why It Might Work Now |
|----------------|--------------------|-----------------------|
| [Idea] | [Reason] | [Changed conditions] |

## Overlaps of Surprise

**Where multiple angles converged:**

| Insight | Contrarian? | Cross-Domain? | First Principles? | Failure Pattern? |
|---------|-------------|---------------|--------------------|------------------|
| [Insight 1] | X | X | | |
| [Insight 2] | | X | X | X |

**The key convergent insight:**
[The one thing that multiple independent angles point to]

## Mission Relevance

[This section adapts to the member's mission context.]

- **[Member's niche]** — What contrarian approaches could transform your coaching practice?
- **[Their clients]** — What assumptions about [client avatar] might be wrong?
- **[Their delivery model]** — What sacred cows in [group/1:1/workshop] delivery deserve questioning?
- **[Their terminology]** — Do any of your frameworks already embody an outlier approach?

[If no mission context was loaded, use generic categories:]
- **Your coaching practice** — What rules might you be following unnecessarily?
- **Your clients** — What assumptions about your clients deserve testing?
- **Your content** — What contrarian angles could set your content apart?

## Action Verdict

| Insight | Verdict | Why |
|---------|---------|-----|
| [Key insight 1] | Act now / Bookmark / Research further | [Reasoning] |
| [Key insight 2] | Act now / Bookmark / Research further | [Reasoning] |

## Learning Triggers

- **Assumptions challenged:** [What this research makes you question]
- **Rules worth breaking:** [Conventions that might not apply to your context]
- **Follow-up research:** [What a second swarm would investigate]

## Sources
- [Source 1](URL)
- [Source 2](URL)
```

---

## Phase 7: Save and Report

**Step 1: Determine save location**

1. If a vault/Zettelkasten was found in Phase 2 → save there as `Outlier Swarm - [Topic] - YYYY-MM-DD.md`
2. If no vault → save to project root `./research-reports/Outlier Swarm - [Topic] - YYYY-MM-DD.md` (create directory if needed)
3. Offer: "Want me to save this somewhere else?"

**Step 2: Link from daily note (optional)**

1. Check if daily notes exist: Glob for today's date pattern (e.g., `**/YYYY-MM-DD.md`)
2. If found → offer to add to Captures section: `- [[Outlier Swarm - Topic - YYYY-MM-DD]] - Brief summary`
3. If not found → skip silently

**Step 3: Report summary**

Present the executive summary, key convergent insight, and action verdicts to the user.

---

## When to Use This Skill vs Research Swarm

| Use Case | Research Swarm | Outlier Swarm |
|----------|----------------|---------------|
| "What are my options for X?" | X | |
| "How does Y work?" | X | |
| "What's everyone missing about X?" | | X |
| "Is there a better way than the standard approach?" | | X |
| "Why does conventional wisdom say X?" | | X |
| Evaluating a tool or technology | X | |
| Questioning an established practice | | X |

---

## Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Load mission context | Build on prior research vs. start fresh | Present contrarian as automatically better |
| Launch all 5 agents in parallel | Save to an unexpected location | Make purchase decisions |
| Look for convergence, not just novelty | | Skip source attribution |
| Use haiku for sub-agents | | Dismiss mainstream without evidence |

---

## Cost Optimization

- All 5 sub-agents use **haiku** (fast, cheap)
- The value is in the STRUCTURE of inquiry — five mutually exclusive mandates revealing what any single perspective misses
- Cap: 5 agents. Always 5. The framework is the 5 lenses.
