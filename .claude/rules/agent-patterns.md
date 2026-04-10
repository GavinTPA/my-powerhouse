# Agent & Skill Instruction Patterns

Topic-specific gotchas for writing effective agent and skill instructions.

---

## Positive Framing

**Anti-pattern:** "DO NOT reimplement" or "DO NOT do your own version"
**Problem:** Negative instructions prime the unwanted behavior (pink elephant problem)

**Pattern that works:**
- "The [skill-name] skill handles X, Y, Z"
- "Continue when the skill completes"
- Trust automatic skill discovery via description matching

---

## Hide Implementation Details

**Anti-pattern:** Showing implementation details before delegation
**Problem:** Gives Claude the recipe to DIY instead of delegating

**Pattern that works:**
- Remove glob paths, file locations, and logic from agents
- Let skills own their own implementation details
- Agents describe WHAT happens, skills describe HOW

---

## Avoid Irrelevant Contrasts

**Anti-pattern:** Introducing irrelevant concepts to contrast against
**Problem:** Primes the unwanted concept, adds confusion

**Example:**
- Wrong: "Session = Day" or "this is a session tool, not a day tool"
- Right: "End-of-session orchestrator that captures learnings"

Describe what something IS. Don't explain what it ISN'T.

---

## Directive Instructions

Skill steps land harder when written as directives with explicit workflows.

**Vague:** "Run through ai-slop-detector to clean up"
**Directive:** "Always invoke ai-slop-detector before presenting. The workflow: 1. Draft 2. Invoke 3. Present cleaned"

The directive version:
- States WHEN (always, before presenting)
- Numbers the steps (creates a checklist)
- Uses active verbs (invoke, draft, present)

"Always" and numbered workflows get followed. Suggestions get skipped.

---

## Skill Output for Copy/Paste

When skills output text meant for copy/paste (Facebook comments, emails, etc.), avoid:
- Wrapping output in code blocks (terminal width becomes hard line breaks)
- Any formatting that adds line breaks mid-paragraph

**Pattern that works:**
- Output as plain text (not in code blocks)
- Explicit instruction: "No hard line breaks mid-paragraph"
- Let text flow naturally, only break between paragraphs

---

## Three-Tier Boundaries

Define graduated autonomy for skills and agents using the three-tier pattern.

| Tier | Symbol | Meaning |
|------|--------|---------|
| Always | Do without asking - autonomous actions |
| Ask First | Check in before proceeding |
| Never | Hard stops - don't do this |

**Why this works:** Research from 2,500+ agent files shows this format gets followed more reliably than prose instructions. It's scannable and unambiguous.

**Template for skills:**

```markdown
## Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| [Autonomous actions] | [Check-in actions] | [Hard stops] |
```

---

## Regenerate vs Targeted Fix

**Anti-pattern:** Asking an agent to "regenerate" content when you only need a targeted fix
**Problem:** Agents run their full pipeline and rewrite everything, losing approved content

**Pattern that works:**
- For targeted fixes: Extract the original content, modify it directly, don't invoke the agent
- For full rewrites: Use the agent, expect all content to change
- If preserving specific content matters, handle it yourself - don't delegate to an agent that will rewrite

**The principle:** "Regenerate" means "create fresh." If you want to preserve content, don't ask for regeneration.

---

## Task Routing Default

**Anti-pattern:** Background agents adding discovered tasks directly to your active work
**Problem:** Exceeds WIP limits without your consent, disrupts carefully planned focus

**Pattern that works:**
- New tasks discovered by agents -> add to a backlog or "Ready" section
- Only promote to active work when you explicitly request
- Let the human decide what gets promoted

**The principle:** Agents discover work; humans prioritize it.
