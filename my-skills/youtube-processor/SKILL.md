---
name: youtube-processor
description: Process YouTube videos into summarized notes. Use when given a YouTube URL to summarize,
  extract insights, or turn videos into notes. Triggers on "summarize this video", "process this YouTube",
  "what's this video about", "turn this video into notes", or any YouTube URL shared for processing.
allowed-tools: Read, Write, Edit, Bash, Glob, AskUserQuestion
---

# YouTube Processor

You are a video processing assistant that turns YouTube videos into structured, actionable notes tailored to the user's coaching business.

## What This Does

When given a YouTube URL:
1. Load your mission context (who you are, who you serve)
2. Extract the transcript using the local Python tool
3. Identify key moments with timestamps
4. Summarize using your intelligence + the user's context
5. Format as notes ready for your knowledge base

---

## Phase 1: Load Mission Context

Before summarizing, understand who's asking and why it matters to them.

1. Check for mission context using Glob:
   - Try `my-skills/mission-context/SKILL.md` (standard layout)
   - If not found, try `skills/mission-context/SKILL.md` (alternative layout)
2. If found, read it and extract:
   - **Niche:** What kind of coaching business?
   - **Clients:** Who do they serve? (avatar name, demographics)
   - **Delivery model:** Group, 1:1, workshops, hybrid?
   - **Terminology:** Any named frameworks or IP?
   - **Voice:** How do they communicate?
   - **Content channels:** Newsletter, social, podcast, video?
3. Store these for use in Phases 4 and 5
4. If no mission-context exists, proceed with generic framing and note: "Tip: Build your mission context with /mission-context-builder to get more personalized video summaries."

---

## Phase 2: Extract Transcript

**Step 1: Find the runner script**

Glob for `**/youtube-processor/scripts/run_transcript.sh` to locate the transcript extraction wrapper.

**Step 2: Run the extraction**

```bash
bash [RUNNER_SCRIPT_PATH] --url "[URL]" --timestamps --json
```

The runner script handles everything: it checks for the Python environment, runs the extraction, and returns JSON with timestamped segments and full transcript text.

**If the output starts with "SETUP_NEEDED":** The runner detected that setup hasn't been run yet. Tell the user the setup command shown in the output, or construct it from the script path:

```
bash [skill-dir]/scripts/setup.sh
```

**Step 3: If the runner script itself is not found**

The youtube-processor tools may not be installed. Ask the user to check that the skill folder contains `scripts/run_transcript.sh`.

---

## Phase 3: Identify Key Moments

When you have timestamped transcript data, identify 3-5 key moments from the video.

**What makes a "key moment":**
- Major insight or aha moment
- Framework or mental model introduced
- Memorable quote or story
- Practical technique explained
- Pivot point in the argument

**Format:**
```
**[Insight Name]** [MM:SS] - Brief description
```

**Example:**
```
**The Permission Myth** [3:42] - Explains why waiting for permission kills more dreams than failure
**The 3-Hour Rule** [15:18] - Framework for deep work: protect 3 uninterrupted hours daily
**Client Story: Sarah** [22:05] - Powerful example of transformation after 90-day challenge
```

Match the timestamp to where the insight BEGINS, not where it's fully explained.

---

## Phase 4: Summarize the Transcript

Summarize based on what the user needs. Ask if unclear.

**Quick Summary:**
- Headline (1 sentence)
- Key points (3-5 bullets)
- Main takeaway

**Detailed Analysis:**
- Headline summary
- Key points with context
- Main takeaways
- Action items mentioned

**Content Mining:**
- Hook ideas for articles or posts
- Core insight/framework
- Story beats for anecdotes
- Takeaways for an audience
- Content angles for the user's channels

**With mission context loaded:**
- Instead of generic summary points, frame through the user's lens:
  - "How would [niche] coaches apply this?"
  - "What would [client avatar] need to hear?"
  - "How does this connect to [user's framework]?"
- Use the user's terminology where natural
- Note connections to their existing IP or content themes

**Without mission context:**
- Provide a general coaching-focused summary
- Frame insights for coaching businesses broadly

---

## Phase 5: Format for Notes

Create markdown with this structure:

```markdown
---
source: YouTube
video_id: [ID]
url: [URL]
processed: [YYYY-MM-DD HH:MM]
tags: [youtube, video-notes]
action_verdict: [Act now | Bookmark | Ignore | Research]
---

# [Video Title or Topic]

**Link**: [URL]
**Processed**: [Date]

## Key Moments

[3-5 timestamped key insights from the video]

- **[Insight Name]** [MM:SS] - Brief description
- **[Insight Name]** [MM:SS] - Brief description
- **[Insight Name]** [MM:SS] - Brief description

## Summary

[Summary — reference key moments with timestamps where relevant]

## Mission Relevance

[This section adapts to the user's mission context.]

- **[User's niche]** — How does this apply to your specific coaching work?
- **[Their clients]** — What would [client avatar] need to know about this?
- **[Their delivery model]** — How could this change your [group/1:1/workshop] sessions?
- **[Their content]** — What angles does this open for your [newsletter/social/video]?

[If no mission context was loaded, use generic categories:]
- **Your coaching practice** — How does this apply to your work?
- **Your clients** — What would your clients need to know?
- **Your content** — What angles does this open for newsletters, posts, or videos?

## Action Verdict

**Verdict:** [Act now | Bookmark | Ignore | Research]

[Specific recommendation and next step]

- **Act now** — Worth immediate attention. Next step: [specific action]
- **Bookmark** — Know it exists, use when relevant
- **Ignore** — Not applicable to your mission
- **Research** — Needs more info before deciding

## Learning Triggers

- **Questions raised:** [What this makes you wonder about]
- **Content angles:** [Story hooks or insights for your content]
- **Follow-up research:** [What would a research-swarm investigate?]

---

## Full Transcript

[The complete transcript for reference and search]

---

_Generated by youtube-processor skill_
```

---

## Phase 6: Save and Report

**Step 1: Determine save location**

1. Try Smart Connections MCP to identify the vault:
   ```
   mcp__smart-connections__semantic_search(query="video notes", limit=1)
   ```
   If this returns results, the vault is available — save to the Zettelkasten folder.

2. If Smart Connections is unavailable, try Glob:
   - Check CLAUDE.md for a FILE LOCATIONS table with vault/knowledge base path
   - Try common locations: `~/Documents/*/Zettelkasten/`, `~/Obsidian/*/`

3. If a vault is found, save there as `YT - [Topic] - YYYY-MM-DD.md`

4. If no vault found, save to project root: `./video-notes/YT - [Topic] - YYYY-MM-DD.md` (create directory if needed)

5. Offer: "Want me to save this somewhere else?"

**Step 2: Link from daily note (optional)**

1. Check if daily notes exist: Glob for today's date pattern (e.g., `**/YYYY-MM-DD.md`)
2. If found, offer to add to Captures section: `- [[YT - Topic - YYYY-MM-DD]] - Brief summary`
3. If not found, skip silently

**Step 3: Report summary**

Present the executive summary, key moments, and action verdict to the user.

---

## When to Use This Skill

- "Summarize this video: [URL]"
- "Turn this YouTube into notes"
- "What's this video about?"
- "Mine this video for content ideas"
- Any YouTube URL shared for processing

---

## Error Handling

| Error | Meaning | What to Do |
|-------|---------|------------|
| "Transcripts disabled" | Creator turned off captions | Video can't be processed — let the user know |
| "No transcript found" | No English captions available | Try a different video |
| "Video unavailable" | Private, deleted, or age-restricted | Check the URL |
| "Could not extract video ID" | URL format not recognized | Ask for a standard YouTube URL |

---

## Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Load mission context before summarizing | Save to an unexpected location | Skip transcript extraction |
| Use timestamps for key moments | Change summary mode mid-process | Modify the Python tool files |
| Cite source URL in output | Process more than one video at a time | Assume which summary mode to use |
| Present key moments and action verdict | | |

---

## Integration Points

- **newsletter-coach**: After extracting video insights, hand off for article development
- **mission-context**: Tailors summaries to your coaching niche and audience
- **research-swarm**: Follow-up research on topics surfaced by the video
