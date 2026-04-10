---
name: spec-verifier
description: Verifies completed work against original specifications. Use when "verify spec", "check spec compliance", "verify against [spec file]", "spec verification for [implementation]".
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Spec Verifier

Systematically verify that completed work matches the original specification.

## What This Does

After any build or implementation, this skill:
1. Reads the spec file (SKILL.md, plan, requirements doc)
2. Extracts discrete, checkable requirements
3. Reviews the implementation for evidence of each requirement
4. Produces a Spec Compliance Report with verdict

## Instructions

### Step 1: Identify Spec and Implementation

**If not provided, ask:**
- "Which spec file should I verify against?"
- "What implementation scope should I check?"

**Common spec types:**
- `SKILL.md` files (skill requirements)
- Plan files (implementation plans)
- Analysis and planning documents
- README requirements sections

### Step 2: Extract and Classify Requirements

Read the spec file and extract discrete requirements. Look for:
- Numbered lists
- Bullet points with "must", "should", "will"
- Success criteria sections
- Feature descriptions
- Tables with requirements

**Classify each requirement by severity:**

| Severity | Tag | Signal Words | Default? |
|----------|-----|-------------|----------|
| Blocker | `[BLOCKER]` | "must", "required", "critical", "essential", "shall", "mandatory"; numbered requirements in a "Requirements" section | |
| Should-Have | `[SHOULD]` | "should", "expected", "important", "needs to" | Yes (when unclear) |
| Nice-to-Have | `[NICE]` | "could", "optional", "bonus", "future", "ideally", "consider" | |

**Classification rules:**
1. Look at the language around each requirement for signal words
2. Numbered items in an explicit "Requirements" section default to Blocker
3. Items in "Nice to have", "Future", or "Ideas" sections default to Nice-to-Have
4. When no signal words are present, default to Should-Have

**Output requirements as a numbered list with severity tags** before verification:

```
Extracted N requirements from [spec file]:
1. [BLOCKER] Requirement text
2. [SHOULD] Requirement text
3. [NICE] Requirement text
...
```

### Step 3: Verify Each Requirement

For each requirement (carrying its severity tag forward):
1. **Search implementation** using Glob/Grep for evidence
2. **Read relevant files** to confirm implementation exists
3. **Classify status:**
   - **Met** - Requirement fully satisfied, evidence found
   - **Partial** - Some evidence exists but incomplete
   - **Missing** - No evidence of implementation

4. **Capture evidence** - File:line or specific output that proves status

### Step 4: Generate Spec Compliance Report

Use this format exactly:

```markdown
## Spec Compliance Report

**Spec:** [path to spec file]
**Implementation:** [scope verified]
**Verified:** [YYYY-MM-DD HH:MM]

### Severity Summary

| Severity | Total | Met | Partial | Missing |
|----------|-------|-----|---------|---------|
| Blocker | X | X | X | X |
| Should-Have | X | X | X | X |
| Nice-to-Have | X | X | X | X |

### Requirements Checklist

| # | Severity | Requirement | Status | Evidence | Notes |
|---|----------|-------------|--------|----------|-------|
| 1 | BLOCKER | [Extracted req] | Met | [File:line] | |
| 2 | SHOULD | [Extracted req] | Partial | [What exists] | [What's missing] |
| 3 | NICE | [Extracted req] | Missing | - | [Gap description] |

### Summary
- **Met:** X of Y requirements (Z%)
- **Partial:** X requirements need attention
- **Missing:** X requirements not implemented

### Gaps Requiring Action

1. **[BLOCKER] [Requirement]:** [What's missing]
   - Suggested fix: [How to address]
2. **[SHOULD] [Requirement]:** [What's missing]
   - Suggested fix: [How to address]

**Verdict:** [PASS / PARTIAL / FAIL]
```

### Step 5: Auto-Save Report (Learning Flywheel)

**Always save the report to TWO locations:**

1. **Target's docs/verification folder:**
   - Path: `[target-folder]/docs/verification/YYYY-MM-DD-spec-compliance.md`
   - Create the verification folder if it doesn't exist
   - This builds verification history for that specific target

2. **Daily note Captures section (if using Obsidian daily notes):**
   - Add link: `- [[Spec Compliance - [Target] - YYYY-MM-DD]] - [Verdict summary]`

**Why this matters:** Verification reports become training data. Repeated failures on the same requirement indicate systematic issues.

### Verdicts (Severity-Weighted)

Verdicts are determined by severity, not raw counts:

| Verdict | Condition |
|---------|-----------|
| **PASS** | All Blockers met, all Should-Haves met (Nice-to-Have status doesn't affect verdict) |
| **PARTIAL** | All Blockers met, some Should-Haves are Partial or Missing |
| **FAIL** | Any Blocker is Partial or Missing |

**PASS:** Ready to ship. All critical and expected requirements satisfied.

**PARTIAL:** Blockers are solid, but Should-Have gaps remain. Address gaps, then re-verify.

**FAIL:** Blocker requirements not met. Significant work needed before shipping.

## Fresh Eyes Review Pattern

This skill uses "fresh eyes" verification - treating the implementation as if seeing it for the first time.

**Questions to ask for each requirement:**
- "Does this exist in the implementation?"
- "Does it match what the spec describes?"
- "Is it complete or just partial?"

**Avoid:**
- Assuming intent ("they probably meant to...")
- Giving benefit of the doubt ("this is close enough...")
- Inferring requirements not in the spec

Verify what's written, not what was intended.

## Examples

### Example 1: Skill Verification

**Input:** "Verify [skill] against its plan"

**Process:**
1. Read the plan or spec file provided by the user
2. Extract requirements from Success Criteria and recommended actions
3. Check the implementation folder for evidence
4. Produce compliance report

### Example 2: Plan Verification

**Input:** "Verify this implementation against the plan we made"

**Process:**
1. Read the plan file (usually in `.claude/plans/`)
2. Extract requirements from Implementation Plan section
3. Check modified files for evidence
4. Produce compliance report

## Integration with QA Agents

When a QA agent invokes this skill, it can add:
- QA commentary beyond spec compliance
- User-perspective review
- Edge case identification

The spec-verifier provides the systematic checklist. The QA agent provides the wisdom.
