---
name: session-intelligence
description: Analyzes Zoom sessions to produce Training Summary and Attendee Detail documents with per-person coaching notes. Use when "session intelligence", "analyze this session", "process this zoom call", "session analysis", "attendee intelligence".
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch
---

# Session Intelligence

Turns raw Zoom session data into two coaching intelligence documents — a **Training Summary** and an **Attendee Detail** report — with per-person coaching notes powered by mission-context.

## When This Activates

- "session intelligence"
- "analyze this session"
- "process this zoom call"
- "session analysis for [meeting]"
- "attendee intelligence"

---

## The Workflow

### Step 1: Gather Session Info

Ask these questions ONE AT A TIME:

**1a. Meeting type:**
> Was this a scheduled meeting or a Personal Meeting Room (PMI)?
> - Scheduled: I'll use the meeting ID
> - PMI: I'll need the UUID (unique per session)

**1b. Zoom profile:**
> Which Zoom account? (Check zoom-connect config for available profiles)

Do NOT hard-code profile names. Read from `~/.config/zoom-connect.yaml` to discover available profiles.

**1c. Find the meeting:**

Use zoom-connect to list recent meetings for the selected profile and date range. Confirm which meeting to process.

For PMI meetings, capture the UUID from the output.

**1d. Trainers/hosts:**

> Who were the trainers or hosts for this session?

Use zoom-connect to get attendance for the meeting. For PMI meetings, use the UUID instead of meeting ID. Zoom attendance data includes the host role — use that as the starting point.

Confirm the trainer names with the user. The host from Zoom is usually the primary trainer, but there may be co-trainers.

**1e. Business context:**

Invoke **mission-context** to discover the user's roles and businesses. If the user operates across multiple businesses, ask which context applies to this session:

> Your mission-context shows you work with [Business A] and [Business B]. Which applies to this session?

The Zoom profile often implies the business (e.g., a BB Zoom profile = BlackBelt context). If it's unambiguous, confirm rather than ask:

> This is on the [profile name] Zoom account — I'll use [Business] context for the coaching notes. Correct?

Load the relevant mission-context section for terminology, frameworks, and coaching vocabulary.

---

### Step 2: Pull Session Data

Pull all available data via zoom-connect:

Use zoom-connect to pull all available data:

- **Attendance** — get attendance report for the meeting
- **Chat log** — download recording type CHAT
- **Transcript (if available)** — download recording type TRANSCRIPT

**Graceful degradation:**
- Chat + Attendance = full Attendee Detail, reduced Training Summary
- All three = full output
- If transcript is still processing, note it and proceed with chat + attendance. Add a note: "Transcript was still processing — Training Summary generated from chat data only."

---

### Step 3: Analyze Chat

Run the chat analysis engine:

```bash
python3 tools/parse_chat.py \
  --file <chat-file-path> \
  --hosts "<Trainer1>,<Trainer2>" \
  --json
```

This produces:
- **Detected prompts** with time windows and codes
- **Per-person index** mapping each participant's messages to prompt windows
- **Engagement stats** (message counts, top participants)

**Review gate:** Show the detected prompts to the user before proceeding:

> I detected **N prompts** from the chat:
>
> | Code | Time | Prompt | Responses |
> |------|------|--------|-----------|
> | WIN | 00:14:00 | "Type your win this week" | 23 |
> | LES | 00:16:00 | "Biggest lesson?" | 19 |
> | ... | ... | ... | ... |
>
> Does this look right? Should I adjust any codes or add/remove prompts?

If the user corrects codes (e.g., "P3 should be GAP not P3"), note the corrections for document generation.

**If zero prompts detected:** This is a valid outcome for sessions that don't use chat prompts (labs, hot seats, Q&A sessions). Proceed with engagement-only analysis — per-person message summaries without prompt mapping.

---

### Step 4: Generate Training Summary

Create the Training Summary document following this structure:

```markdown
# [Session Name] — Training Summary

**Date:** YYYY-MM-DD (HH:MM timezone)
**Trainers:** [Names]
**Duration:** [X] minutes
**Attendance:** [N] participants ([M] total including bots/notetakers)
**Chat Messages:** [N] from [M] participants
**Engagement:** [Brief characterization — e.g., "High", "Moderate", "Very active chat"]

## Session Overview

[2-3 paragraph summary of what the session covered. Use transcript if available,
otherwise synthesize from chat messages and attendance patterns.]

## Session Flow

### [Section Name] (HH:MM–HH:MM)
[What happened in this time block. Key teaching points, activities, exercises.]

### [Section Name] (HH:MM–HH:MM)
[Continue for each major section of the session.]

## Key Questions Asked

[Numbered list of substantive questions from participants, with attribution.
Extract from chat messages containing "?" that aren't prompt responses.]

## Key Answers from Trainers

[Trainer responses to the key questions above. Quote directly from chat
where possible. Attribute to specific trainer.]

## Coaching Takeaways

[3-6 synthesized insights from the session. These are the coaching intelligence
— patterns, themes, and strategic observations that emerged from the data.
Use mission-context vocabulary and frameworks.]

## Linked Files

- [[{Session Name} - Attendee Detail - YYYY-MM-DD]] — Per-person responses and coaching intel
```

**Writing guidelines for Training Summary:**
- Use mission-context terminology (the frameworks, stage language, and vocabulary of the business)
- The Session Flow section uses transcript timestamps if available; otherwise estimate from chat timestamps
- Key Questions: only include substantive questions (not "can you repeat that?" or "what page?")
- Coaching Takeaways: these are the strategic patterns — what a senior coach would want to know

---

### Step 5: Generate Attendee Detail

Create the Attendee Detail document following this structure:

```markdown
# [Session Name] — Attendee Detail

**Date:** YYYY-MM-DD | **Trainers:** [Names] | **Duration:** [X] min
**Parent:** [[{Session Name} - Training Summary - YYYY-MM-DD]]

---

## How to Read This File

Each attendee who chatted has their responses mapped to the trainer's prompts
by time window. Prompts are abbreviated:

| Code | Prompt | Time Window |
|------|--------|-------------|
| **WIN** | [Full prompt text] | HH:MM–HH:MM |
| **LES** | [Full prompt text] | HH:MM–HH:MM |
[... all detected prompts ...]

---

## Active Chat Participants (Alphabetical)

### [Participant Name]
**Time on call:** [X] min | **Chat messages:** [N]

| Prompt | Response |
|--------|----------|
| WIN | "[Their response]" |
| LES | "[Their response]" |
| Other | "[Any messages not in a prompt window]" |

**Coaching note:** [2-4 sentences synthesizing what their responses reveal.
Where are they in their journey? What are their wins? What gaps show up?
What would you focus on in a 1:1? Use mission-context frameworks.]

---

[Repeat for each active chat participant, alphabetically]

---

## Attendees Present But Not Chatting

| Name | Time (min) | Notes |
|------|-----------|-------|
| [Name] | [X] | [Any notable info — left early, known identity, etc.] |

---

## Team / Staff Present

| Name | Role | Time (min) | Notes |
|------|------|-----------|-------|
| [Name] | Trainer | [X] | Led the session |
| [Name] | Co-trainer | [X] | [Notes] |

---

## Coaching Intelligence Summary

### Common Bottlenecks (by frequency)
[Numbered list of the most common challenges/gaps mentioned across all attendees.
Synthesized from GAP-type prompt responses and other indicators.]

### [Custom aggregation sections as relevant — e.g.:]
### Revenue Aspirations (current → target)
### Free vs Paid Split
### Top Engaged (by chat message count)
```

**Writing guidelines for Attendee Detail:**
- Coaching notes are the VALUE — don't just echo what they said. Read between the lines.
- Use mission-context vocabulary in coaching notes (the frameworks, training names, stage indicators)
- "Attendees Present But Not Chatting" comes from attendance data minus chat participants
- Team/Staff: identify from the host list and any known team members
- The Coaching Intelligence Summary at the bottom aggregates patterns — what a coach scanning for trends would want

---

### Step 6: Save and Link

**Save both documents to Zettelkasten:**

Save to the user's Zettelkasten folder with these filenames:
```
[Session Name] - Training Summary - YYYY-MM-DD.md
[Session Name] - Attendee Detail - YYYY-MM-DD.md
```

**Link from daily note Captures:**
```
- [[Session Name - Training Summary - YYYY-MM-DD]] — Session intel: [brief summary]
- [[Session Name - Attendee Detail - YYYY-MM-DD]] — Per-person coaching notes for [N] participants
```

**Tell the user:**
> Session intelligence complete:
> - Training Summary: [[link]]
> - Attendee Detail: [[link]] ([N] active chatters, [M] present but silent)
> - [N] prompts detected and mapped

---

## Zero-Prompt Mode

When no prompts are detected (labs, hot seats, Q&A sessions, small groups):

**Training Summary:** Same structure, but Session Flow is based on transcript/chat timestamps without prompt mapping.

**Attendee Detail:** Instead of prompt-response tables, list each person's chat contributions chronologically:

```markdown
### [Participant Name]
**Time on call:** [X] min | **Chat messages:** [N]

**Chat contributions:**
- [HH:MM] "[Message text]"
- [HH:MM] "[Message text]"

**Coaching note:** [Synthesis based on what they said and asked]
```

The coaching notes are still the valuable output — they just draw from conversation context rather than structured prompt responses.

---

## Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Pull data via zoom-connect | Confirm detected prompts before generating | Share attendee data outside Zettelkasten |
| Use mission-context for coaching vocabulary | Confirm trainer names | Hard-code business names or roles |
| Save both documents to Zettelkasten | Adjust prompt codes if user corrects | Generate coaching notes without mission-context |
| Link from daily note | | Skip the review gate on prompt detection |

---

## Dependencies

- **zoom-connect** — Data source (attendance, chat, transcript)
- **mission-context** — Business vocabulary and coaching frameworks for notes
