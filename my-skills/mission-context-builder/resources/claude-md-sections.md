# CLAUDE.md Section Templates

These templates define how interview answers map to CLAUDE.md personal sections. The builder uses these during the compile phase to seed the member's CLAUDE.md.

## How It Works

The member's CLAUDE.md contains builder markers like:
```
<!-- BUILDER:START:WHO_I_AM -->
...placeholder content...
<!-- BUILDER:END:WHO_I_AM -->
```

After the interview, the builder replaces the content between each marker pair with the populated template below.

---

## WHO_I_AM

### Solo Mode (no company context)

```markdown
## WHO I AM

I'm [COACH_NAME], a **[ONE_LINE_DESCRIPTION]**.

**My niche:** [SPECIFIC_NICHE_WITH_REVENUE_OR_STAGE]

**What clients get:** [DELIVERY_MODEL_DESCRIPTION]

**My superpower:** [CAPABILITY_NOT_TRAIT]

**My mental models come from:** [INFLUENCES_SHORT_LIST]. If you can explain something using a [THEIR_DOMAIN] analogy, do it.
```

### Team Mode (company-context.md exists)

```markdown
## WHO I AM

I'm [MEMBER_NAME], **[ROLE_TITLE]** at **[COMPANY_NAME]**.

**The company:** [COMPANY_ONE_LINE]

**My role:** [ROLE_DESCRIPTION]

**I need AI help with:** [PRIMARY_AI_USE_CASES]

**My mental models come from:** [INFLUENCES_SHORT_LIST]. If you can explain something using a [THEIR_DOMAIN] analogy, do it.
```

---

## MY_CLIENTS

```markdown
## MY CLIENTS

**Who I serve:** [AVATAR_SUMMARY_ONE_SENTENCE]

**Their surface problem:** [WHAT_THEY_SAY_ON_CALL_ONE]

**What's really going on:** [WHAT_EMERGES_BY_SESSION_THREE]

**Their words:** [2-3 RAW_CLIENT_PHRASES_INLINE]

When writing for my audience, use their language - not marketing copy. They say "[RAW_PHRASE_1]" not "[POLISHED_VERSION]".
```

---

## MY_TERMINOLOGY

```markdown
## MY TERMINOLOGY

| Term | Meaning |
|------|---------|
[TERMINOLOGY_TABLE_ROWS]

For the full terminology reference, see `my-skills/mission-context/resources/terminology.md`.
```

---

## WRITING_RULES

```markdown
## WRITING RULES

When writing ANY content for me (emails, newsletters, coaching responses, articles):

**My style:** [THREE_WORD_STYLE]

**How I communicate:**
[COMMUNICATION_PATTERNS_AS_BULLET_LIST]

**Signature phrases (use these):**
[PHRASES_CLIENTS_QUOTE_BACK_AS_BULLET_LIST]

**Words I avoid (never use these):**
[SPECIFIC_WORDS_WITH_REASONS_AS_BULLET_LIST]
```

---

## IRON_RULES

```markdown
## THE IRON RULES

1. **ALWAYS EXPLAIN THE WHY.** Tell me what AND why - in plain English.

2. **MAKE FIXES AS SIMPLE AS POSSIBLE.** Impact as little code as possible. Zero new bugs.

[ADDITIONAL_IRON_RULES_FROM_INTERVIEW]

**Iron Rules** = Known failure modes. Use sparingly.
**Guidelines** = Default style. Trust Claude's judgment. Upgrade to Iron Rule only after something fails.
```

---

## Builder Instructions

When populating these sections:

1. **Find CLAUDE.md** in the working directory root
2. **Determine mode:** Check if `my-skills/mission-context/resources/company-context.md` exists
   - If yes → use **Team Mode** templates (where available)
   - If no → use **Solo Mode** templates
3. **For each section** with a `BUILDER:START` / `BUILDER:END` marker pair:
   - Read the current content between the markers
   - Replace it with the populated template from above (team or solo variant)
   - Keep the marker comments intact (they allow future updates)
4. **If no markers found** - tell the member their CLAUDE.md doesn't have builder markers and they can update it manually
5. **If CLAUDE.md not found** - skip this step and tell the member

The markers are preserved so the builder can update sections later without touching the rest of CLAUDE.md.
