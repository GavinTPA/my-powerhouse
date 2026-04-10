---
name: lets-wrap
description: End-of-session skill that makes your AI smarter every time you use it. Captures what Claude learned about you during the session and saves it permanently. Use when "lets wrap", "wrap up", "end of session", "save what you learned", "close the loop".
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# Lets Wrap

Your end-of-session ritual. This is how your AI gets smarter every time you use it.

## What This Does

During every session, Claude learns things about you — your preferences, your corrections, your way of working. Without this skill, all of that disappears when you close the terminal. Lets-wrap captures those learnings and writes them into your system permanently, so the next session starts smarter than this one ended.

Think of it like a coaching debrief: "What did we learn today, and how do we make sure we don't forget it?"

---

## The Pipeline

Run all six steps in order. Use coaching language throughout — explain WHAT is happening and WHY it matters at every step.

### Step 1: Session Review

**What you say:** "Let me check what we worked on today..."

Run these commands silently (do NOT show raw git output to the member):

```bash
git status --porcelain
git log --since="midnight" --oneline
```

Summarise the session in 2-3 plain English sentences. Focus on what was accomplished, not technical details.

**Example output:**
"This session you worked on your newsletter about client onboarding. We refined your voice settings and I learned a few things about how you like to open emails. Let me capture those so I remember next time."

If nothing was worked on (empty session), say so warmly and skip to Step 6.

---

### Step 2: Learning Capture

**What you say:** "I'm scanning our conversation for things worth remembering..."

Scan the entire conversation for learnings. Look for:
- **Direct corrections** — Member said "No, that's not how I..." or "Actually, I prefer..."
- **Revealed preferences** — Patterns in how they responded, what they liked/disliked
- **Discoveries** — New information about their business, clients, or workflow

**Classify each finding:**

| Level | What It Means | Example |
|-------|---------------|---------|
| **HIGH** | Member directly corrected you | "I don't call them 'customers', I call them 'members'" |
| **MEDIUM** | Pattern you noticed | They consistently preferred shorter paragraphs |
| **LOW** | Observation worth noting | They mentioned a new program launching in March |

**Present each finding in coaching language:**

"I noticed you corrected me when I called your clients 'customers' — you always say 'members'. That tells me this distinction matters to your brand. I'd like to remember this so I always use the right word."

If no learnings found, say: "Clean session — I didn't spot any corrections or new patterns. Your system is already well-tuned." Then skip to Step 5.

---

### Step 3: Mission Context Update

**What you say:** "Here's how I'd like to update your mission context..."

This is where learnings become permanent. Your mission context is the file that tells every skill who you are, how you speak, and what matters to you.

**For each HIGH finding:**

1. Read the current mission context:
   - First check: `my-skills/mission-context/SKILL.md`
   - If that doesn't exist, check for mission context content in `my-skills/mission-context/resources/`

2. Show the member exactly what you want to change:

   ```
   **What I learned:** You call your clients "members", not "customers"

   **Where it goes:** Mission Context > MY TERMINOLOGY section

   **The change:** Add "members" as the preferred term for clients

   **Why this matters:** Every skill that writes for you — newsletters,
   coaching responses, emails — will now use "members" automatically.
   You won't have to correct me again.
   ```

3. Ask for approval using AskUserQuestion:
   - "Apply this update?" with options: "Yes, save it" / "Skip this one"

4. If approved, use Edit tool to update the file

**For MEDIUM findings:** Present the same way, but note: "This is a pattern I noticed — want me to save it, or wait until we see it again?"

**For LOW findings:** Mention briefly but don't propose edits: "I also noticed [observation]. Not saving this yet, just flagging it."

**If mission context SKILL.md doesn't exist yet:** Tell the member: "You haven't built your mission context yet — that's what makes everything personal. Try saying 'build my mission context' in your next session. For now, I'll save today's learnings to your CLAUDE.md instead."

---

### Step 4: CLAUDE.md Update

**What you say:** "A couple of things for your operating manual too..."

Some learnings belong in CLAUDE.md instead of mission context. Route them here:

| Learning Type | Where It Goes in CLAUDE.md |
|---------------|---------------------------|
| Workflow preferences ("always do X before Y") | WORKING NOTES section |
| Hard rules ("never use Comic Sans") | IRON RULES section |
| Tool preferences ("I prefer bullet points over paragraphs") | WORKING NOTES section |
| Session patterns ("mornings are for writing, afternoons for admin") | WORKING NOTES section |

**For each CLAUDE.md update:**

1. Read current CLAUDE.md
2. Show what you want to add and which section it goes in
3. Explain WHY it goes there: "This goes in your CLAUDE.md because it applies to every session, not just [specific skill]. It's like a standing instruction."
4. Ask approval
5. If approved, use Edit tool to add to the appropriate section

**If WORKING NOTES section is still the default placeholder text:** Replace the placeholder with the first real entry.

**If no CLAUDE.md updates needed:** Skip silently.

---

### Step 5: Save Your Work

**What you say:** "Let me save everything to GitHub so it's safe..."

Run these commands silently:

```bash
# Check if there are changes to save
git status --porcelain
```

**If there are changes:**

```bash
# Stage all changed files in the repo
git add -A

# Commit with a descriptive message
git commit -m "Session update: [brief description of what changed]

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to GitHub
git push
```

Report in plain English: "Saved. Your changes are backed up to GitHub."

**If push fails** (common for new members): Report the error in plain English and suggest: "It looks like your GitHub connection needs a quick fix. Try running `gh auth login` and follow the prompts, then say 'lets wrap' again."

**If there are no changes:** Say "Nothing new to save this time — your previous work is already backed up."

After this step: NO follow-up prompts. NO suggestions. NO "would you also like to..." — the pipeline moves directly to Step 6.

---

### Step 6: The Dismount

This is the final output. It must feel complete, warm, and leave no loose ends.

```
---

## Session Complete

**What got smarter:** [1-2 sentences in THEIR language about what was
encoded. Reference specific things: "I now know you prefer 'members'
over 'customers' and that your Tuesday emails always open with a
personal story."]

**To close this session:**
Type `/exit` and press Enter

**To start your next session:**
Open Terminal and paste: `cd ~/Documents/my-powerhouse && claude`

[Warm closing line based on what they accomplished. Examples:
- "Good session. Your system knows you a little better now."
- "Every correction makes the next session smoother. Nice work."
- "That mission context is getting rich. Your tools will notice."]
```

**After the dismount: STOP.** Do not output anything else. Do not suggest next steps. Do not ask follow-up questions. The session is over.

---

## Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Explain what's happening in plain English | Before saving any learning to mission context or CLAUDE.md | Show raw git commands or terminal output |
| Run git commands silently | Before overwriting existing content | Add learnings without member approval |
| Frame updates as coaching moments | | Suggest additional work after the dismount |
| End cleanly with the dismount format | | Leave orphan prompts or dangling questions |

---

## Important Notes

- **Coaching language always.** "I noticed..." not "Git diff shows..."
- **One approval at a time.** Don't batch updates — each learning gets its own approval moment
- **The dismount is sacred.** No follow-up prompts, no suggestions, no "one more thing"
- **Mission context is the priority.** That's what every other skill reads. CLAUDE.md is secondary.
- **If member seems confused:** Explain the WHY — "This is how your AI remembers what you taught it today"
