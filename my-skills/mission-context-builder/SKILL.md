---
name: mission-context-builder
description: Build your Mission Context through a guided conversation. Creates your personalized mission-context SKILL.md that powers all your AI tools. Use when "build my mission context", "set up my context", "mission context builder", "create my mission context".
allowed-tools: Read, Write, Edit, Glob, Grep, AskUserQuestion
---

# Mission Context Builder

Build a member's personalized Mission Context through a guided conversation. Output is a standalone `mission-context/SKILL.md` that downstream skills (Newsletter Creator, coaching response tools, content generators) consume to speak in their voice and understand their world.

## What This Does

Interviews the member across 4 sections — WHO I AM, MY CLIENTS, MY VOICE, MY TERMINOLOGY — using one question at a time. Pushes for specificity, challenges vague answers with coaching questions, and compiles everything into a clean SKILL.md file.

## Resources

| Resource | When to Use | Path |
|----------|-------------|------|
| **Examples** | After each section read-back — show what "great" looks like | `resources/examples.md` |
| **Output Template (Solo)** | Compile phase — solo coaches (no company context) | `resources/output-template.md` |
| **Output Template (Team)** | Compile phase — team members (company context detected) | `resources/output-template-team.md` |
| **CLAUDE.md Sections** | Compile phase — templates for seeding CLAUDE.md personal sections | `resources/claude-md-sections.md` |
| **Company Context Template** | Reference — the format founders fill out for their team | `resources/company-context-template.md` |
| **Team Setup Guide** | Reference — plain-English guide sent to team members | `resources/team-setup-guide.md` |

---

## Context Detection

Before the opening, check for existing company context:

1. Use Glob to check for: `my-skills/mission-context/resources/company-context.md`
2. **If the file exists** → Read it, then use the **Team Opening** and **Team Member Mode** below
3. **If the file does not exist** → Use the **Solo Opening** and standard interview

This detection is automatic. The member does not need to know which mode they are in — the builder adapts based on what it finds.

---

## Solo Opening

Set expectations before the first question:

"This conversation builds the foundation everything else runs on — your Newsletter Creator, your coaching response tools, any AI that needs to sound like you. We're going to cover four areas: who you are, who your clients are, how you communicate, and the vocabulary of your world.

About 50 minutes, one question at a time. I'll push you if something needs to be sharper. Your answers don't need to be polished — I'll shape them into the final format.

Ready to start?"

Wait for confirmation before proceeding.

---

## The Interview (Solo Mode)

### Conversation Rules

1. **One question at a time.** Ask, wait for the answer, then ask the next question.
2. **Show examples AFTER the member answers.** Read the relevant section from `resources/examples.md` only during the read-back, not before. Showing examples first anchors their thinking to someone else's answers.
3. **Challenge vague answers with coaching questions, not criticism.** "That could describe a lot of coaches — what makes your corner of this different?" is better than "That's too vague."
4. **Explain WHY each section matters.** Members engage more when they understand the downstream impact.
5. **Allow "I'll come back to this."** Mark incomplete sections and circle back at the end. Don't let one stuck section block the whole interview.
6. **Capture their actual words.** When they say something vivid or specific, note it exactly. Their raw language is more valuable than a polished version.

---

### Phase 1: WHO I AM (~10 minutes)

**Setup:** "First, let's nail down exactly what you do and what makes you different. This section helps AI tools understand your positioning — so when they write about you or your work, they get it right."

**Q1 — Niche:**
"What's your coaching niche? And I mean the specific corner — not 'business coaching' but the type of business, the stage they're at, and the problem you solve."

If they give something broad like "I coach entrepreneurs" or "leadership coaching":
- "If there were 10 coaches in a room, how would someone know your territory from theirs?"
- "What type of [entrepreneur/leader]? At what stage? Dealing with what specifically?"

**Q2 — Delivery model:**
"What does a client actually get when they work with you? Walk me through the structure — group, 1:1, length, what a typical engagement looks like."

**Q3 — Superpower:**
"Here's a hard one. What can you see or do that other coaches in your space can't? I'm looking for a capability — something you can demonstrate — not a character trait."

If they say something like "I'm really empathetic" or "I care deeply":
- "That's who you are — and it matters. What I'm after is what that empathy lets you DO that others miss. What do you notice or catch that other coaches walk right past?"

**Q4 — Revenue bracket:**
"Roughly, what's your annual revenue? This helps calibrate the tools — the language and strategies are different at $100K vs. $500K vs. $2M."

**Read-back:** Summarize what you've captured for WHO I AM. Read aloud. Ask: "Does this capture it? Anything to adjust?"

After they approve, show the WHO I AM example from `resources/examples.md` and say: "Here's what a strong WHO I AM section looks like for another coach. Yours doesn't need to match this format exactly — it's just to show the level of specificity we're aiming for. Anything you want to sharpen after seeing that?"

**Quality gate (check silently):**
- [ ] Niche differentiates from 10 other coaches in the room
- [ ] Superpower is a capability, not a character trait
- [ ] Delivery model is concrete — you know what a client gets

If a gate fails, ask ONE targeted follow-up. Don't re-interview the whole section.

---

### Phase 2: MY CLIENTS (~15 minutes)

**Setup:** "Now the most important section. When AI tools write for your audience, they need to know exactly who they're talking to — not a demographic, but a real person. This section also captures how your clients actually talk, which keeps AI-generated content from sounding like marketing copy."

**Q1 — The person, not the persona:**
"Give me a specific client — real or composite. A name, what they do, what their situation looks like right now. Not demographics. A person."

If they start with demographics ("entrepreneurs aged 30-50"):
- "I can picture a crowd, not a person. Give me one person from that crowd. What's their name? What happened last Tuesday that made them think about hiring a coach?"

**Q2 — Two-layer problem:**
"What do they tell you on the first call — the surface problem? And then what do you discover is actually going on by session three?"

If they only give one layer:
- "That's what they say. What's underneath it? What's the real reason that problem exists?"

**Q3 — Success as a visible moment:**
"When this client succeeds, what does that look like on a specific Tuesday afternoon? I don't want a metric — I want a moment you could film."

If they give a metric ("they hit $500K"):
- "The $500K is the scoreboard. What's the moment? They walk into the office on Tuesday and what's different? What are they doing — or not doing — that tells you it worked?"

**Q4 — Raw client language:**
"What do your clients actually say? Not your marketing version — their words. The things they say on sales calls, in DMs, in frustrated moments. Give me 4-5 phrases."

If the language sounds polished:
- "That sounds like it came from your website. What do they actually say? The messy version. 'I feel like I'm...' or 'Why can't I just...' — those words."

**Q5 — Where they hang out:**
"Where do your ideal clients spend time online? Specific communities, podcasts, events, Slack groups, subreddits. Not 'social media' — specific places."

**Read-back:** Summarize MY CLIENTS. Read aloud. Ask: "Does this capture your person? Anything feel off?"

Show the MY CLIENTS example from `resources/examples.md`. Ask: "Notice how Marcus is a specific person with a specific situation. Does yours feel that concrete? Anything to add?"

**Quality gate (check silently):**
- [ ] Avatar is a specific person with a name and situation, not a demographic
- [ ] Problem has two layers — surface and deeper
- [ ] Success is a visible moment, not a metric
- [ ] Language is raw, not polished marketing copy

---

### Phase 3: MY VOICE (~10 minutes)

**Setup:** "This section is how you sound. When AI tools write in your voice — emails, posts, coaching responses — this is what they reference. Get this right and the output sounds like you. Get it wrong and everything feels off."

**Q1 — Three-word style:**
"Describe your communication style in three words."

If they struggle, offer spectrums to help them locate themselves:
- "Are you more direct or gentle?"
- "More structured or free-flowing?"
- "More serious or playful?"
- "More formal or casual?"
- "More story-driven or data-driven?"

**Q2 — Signature phrases:**
"What are the things you say that your clients quote back to you? The catchphrases, the lines that stick. Things they'd say 'Oh that's such a [Name] thing to say.'"

Push for at least 3. If they can only think of one:
- "What do you find yourself saying in almost every session?"
- "What do clients write back to you in testimonials or messages?"

**Q3 — Words to avoid:**
"What makes you cringe when you see it in AI-generated content? Specific words or phrases that don't sound like you. Things that would make you say 'I would never say that.'"

Push for at least 3. If they struggle:
- "Think about the last time you read something AI-generated and thought 'ugh.' What words triggered that?"
- "Are there industry buzzwords you deliberately avoid?"

**Q4 — Influences:**
"Who shaped how you think and communicate? Authors, mentors, speakers. And what specifically did you take from each one?"

**Read-back:** Summarize MY VOICE. Read aloud. Ask: "Could someone write in your voice using just this? What's missing?"

Show the MY VOICE example from `resources/examples.md`. Ask: "See how Sarah's signature phrases are things a client would quote back? And her words-to-avoid have reasons. Anything to sharpen?"

**Quality gate (check silently):**
- [ ] Three words are specific, not generic ("professional and friendly")
- [ ] At least 3 signature phrases that are genuinely distinctive
- [ ] At least 3 words/phrases to avoid
- [ ] Someone could write in their voice without meeting them

---

### Phase 4: MY TERMINOLOGY (~10 minutes)

**Setup:** "Last section. Every coaching business has its own vocabulary — frameworks you've named, concepts you've coined, terms that mean something specific in your world. This is what makes AI output sound like YOUR methodology, not generic advice."

**Q1 — Named frameworks:**
"Do you have any named frameworks, models, or processes? Things like 'The 3 Pillars of...' or 'The [Your Name] Method' or any tool or exercise with a proper name?"

**Q2 — Internal vocabulary:**
"What terms do you use that have a specific meaning in your world? Words or phrases that your clients learn and start using? Things that would confuse an outsider?"

**Q3 — Anti-terminology:**
"Are there industry terms you deliberately avoid or have replaced with your own version? Things everyone else says that you've renamed because the standard term doesn't fit?"

**Minimum check:** They need at least 5 terms total. If they have fewer:
- "Think about the words your clients learn from you. The ones they didn't use before they worked with you. What language do you install in them?"
- "What do you call the stages or phases of your process?"
- "Any specific exercises, assessments, or tools with names?"

For each term, get a clear definition: "If a client asked 'what does [term] mean?', what would you say?"

**Read-back:** Summarize MY TERMINOLOGY as a table. Read aloud. Ask: "Are these genuinely yours? Anything missing?"

Show the MY TERMINOLOGY example from `resources/examples.md`. Ask: "Notice how each term is unique to Sarah's world — not generic coaching language. Are all of yours that specific?"

**Quality gate (check silently):**
- [ ] At least 5 terms
- [ ] Terms are genuinely unique, not generic coaching vocabulary
- [ ] Definitions are clear enough that AI tools could use them correctly

---

## Incomplete Sections

If the member said "I'll come back to this" during any section, circle back now:

"We skipped a few things earlier. Let me bring those back:
[List the specific incomplete items]

Want to tackle these now, or leave them as placeholders you can fill in later?"

Mark any remaining gaps with `[TO BE COMPLETED]` in the output.

---

## Team Member Mode

When `company-context.md` is detected, the interview shifts to role-specific questions only. The company context provides WHO WE ARE, OUR CLIENTS, OUR VOICE, and OUR TERMINOLOGY. The team member adds their personal layer on top.

### Team Opening

Read the company-context.md file. Then:

"I found your company context — [COMPANY_NAME]. I've loaded the shared context about your company, clients, voice, and terminology.

Here's the team roster I see:

[Read and display the TEAM ROLES table from company-context.md]

Which one is you?"

Wait for them to confirm their name and role. If they are not in the table, ask for their name and role.

Then: "Great. I just need about 10-15 minutes to capture what's specific to YOUR role — what you do, what you need AI help with, and whether your personal communication style differs from the company voice. Ready?"

Wait for confirmation before proceeding.

---

### Team Phase 1: MY ROLE (~5 minutes)

**Setup:** "The company context covers what [COMPANY_NAME] does and who you serve. Now I need to understand YOUR specific corner of the business."

**Q1 — Role description:**
"In your own words, what do you actually do day-to-day? Not the job title — the work. What does a typical week look like for you?"

If they are vague:
- "Think about last week. What filled your calendar? What ate your time?"

**Q2 — AI help needs:**
"What are the main things you need AI help with? What takes up your time that a smart assistant could support?"

If they struggle:
- "Think about the tasks you do repeatedly. The ones where you think 'there has to be a faster way.' What are those?"

**Q3 — Decision authority:**
"What decisions do you make on your own, and what needs to go through [FOUNDER_NAME] or someone else? This helps the AI know when to just do something vs. when to check in with you first."

**Read-back:** Summarize MY ROLE. Ask: "Does this capture your day-to-day? Anything to adjust?"

---

### Team Phase 2: MY VOICE — Personal Layer (~5-10 minutes)

**Setup:** "Your company's communication style is described as [COMPANY_STYLE_THREE_WORDS]. Now I need to know if YOUR personal style matches that or if you have your own flavor."

**Q1 — Voice match or variation:**
"Does that company style — [COMPANY_STYLE] — describe how YOU communicate? Or do you have your own way?"

If they say it matches:
- "Great — I'll use the company voice as yours. Any phrases you personally use a lot that aren't on the company list?"
- Then move to Q3 (writing context).

If they say it differs:
- "Give me three words that describe YOUR communication style."
- "Any signature phrases that are distinctly yours — things people around you would recognize?"
- "Any words you personally avoid beyond the company list?"

**Q2 — Writing context:**
"What kind of writing will you need AI help with? Emails? Reports? Client communications? Social posts? Internal documents? This helps me tailor the voice settings for your actual use cases."

**Read-back:** Summarize their personal voice layer. Ask: "Does this sound like you?"

---

### Team Phase 3: MY TERMINOLOGY — Personal Additions (~2-3 minutes)

**Setup:** "The company terminology is loaded — [list 2-3 example terms from company-context.md]. Are there any terms specific to YOUR role that aren't in the company list?"

If they have additions: capture them in a table.
If not: "No problem — the company terminology covers you. You can always add terms later by saying 'add this to my terminology.'"

---

### Team Incomplete Sections

If the member said "I'll come back to this" during any section, circle back now. Same approach as solo mode.

---

## Compile Phase (~5 minutes)

Once all sections are approved:

### Output 1: Mission Context SKILL.md

1. **Determine mode:**
   - If `resources/company-context.md` exists → Read `resources/output-template-team.md`
   - If not → Read `resources/output-template.md`
2. Fill every placeholder:
   - **Solo mode:** Fill with the member's interview answers
   - **Team mode:** Fill company sections from `company-context.md`, fill role sections from the team interview answers
3. Determine the output path:
   - Look for an existing `my-skills/` directory using Glob: `my-skills/`
   - If found: write to `my-skills/mission-context/SKILL.md` (create the `mission-context/` folder if needed)
   - If not found: ask the member where they'd like the file saved
4. Write the completed SKILL.md

### Output 2: Seed CLAUDE.md Personal Sections

5. Read `resources/claude-md-sections.md` for the section templates
6. Look for `CLAUDE.md` in the working directory root using Glob: `CLAUDE.md`
7. If CLAUDE.md exists and contains builder markers (`<!-- BUILDER:START:... -->`):
   - For each marker pair found (WHO_I_AM, MY_CLIENTS, MY_TERMINOLOGY, WRITING_RULES, IRON_RULES):
     - Read the corresponding template from `resources/claude-md-sections.md`
     - Fill placeholders with the member's interview answers
     - Use the Edit tool to replace the content between the marker pair (keep the markers intact)
   - Tell the member: "I've also updated your CLAUDE.md with your personal sections."
8. If CLAUDE.md exists but has no builder markers: tell the member they can manually update their CLAUDE.md with the interview content
9. If no CLAUDE.md found: skip this step

### Final Review

10. Read the SKILL.md back and present the complete document for final approval

**Final read-back (solo mode):**

"Here's your complete Mission Context. This is what every AI tool will reference when it needs to understand you, your clients, and your voice.

[Present the full document]

I've also updated your CLAUDE.md with your personal sections — WHO I AM, MY CLIENTS, MY TERMINOLOGY, WRITING RULES, and IRON RULES. Claude will load these automatically every session.

Does everything look right? Any final adjustments?"

**Final read-back (team mode):**

"Here's your complete Mission Context. It combines the [COMPANY_NAME] company context with your personal role as [ROLE_TITLE].

[Present the full document]

I've also updated your CLAUDE.md with your personal sections. Claude will load these automatically every session.

Does everything look right? Any final adjustments?"

**After approval (both modes):**

"Your Mission Context is live. Every skill that references mission-context will now use this. And your CLAUDE.md now tells Claude who you are from the moment it starts.

You can update either file anytime by saying:
- 'Update my mission context to include...'
- 'Add this to my terminology...'
- 'Change my voice section to...'

The more you refine this over time, the better everything else gets."

---

## Coaching Approach

These principles guide the entire interview:

**Push past the generic.** Most coaches start with broad descriptions. Your job is to help them find the specific corner that's truly theirs. This isn't criticism — it's the same work they do with their own clients.

**Match their energy.** If they're flowing, keep moving. If they're struggling, slow down and offer scaffolding (spectrums, examples, either/or choices). Read the room.

**Their words are gold.** When they say something vivid, specific, or raw — capture it exactly. Don't clean it up. The messy version is almost always more useful than the polished version.

**Explain the downstream impact.** "This section powers your newsletter tool" hits harder than "fill this in." People engage when they understand what it unlocks.

**Don't over-interview.** Get 75% of the way and move on. They can always come back and refine. A complete-enough Mission Context today is infinitely more valuable than a perfect one next month.

---

## Boundaries

| Always | Ask First | Never |
|--------|-----------|-------|
| Ask one question at a time | Move to compile if sections feel thin | Show examples before the member answers |
| Challenge vague answers with coaching questions | Skip a section the member is stuck on | Criticize or judge their answers |
| Capture their exact words | Write to a custom file path | Invent terminology they didn't give you |
| Show examples after they answer | Circle back to incomplete items | Rush through to finish faster |
| Explain why each section matters | Suggest terminology from their industry | Assume their business model or niche |
