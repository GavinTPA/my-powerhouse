# Spec Verifier - Technical Reference

## What It Does

Systematically verifies that completed work matches original specifications. Extracts discrete requirements from spec files, searches implementations for evidence, and produces compliance reports with verdicts.

## Dependencies

**Tools required:** Read, Write, Edit, Glob, Grep

**No external APIs or scripts** - pure Claude reasoning against files.

## Usage

**Trigger phrases:**
- "verify spec"
- "check spec compliance"
- "verify against [spec file]"
- "spec verification for [implementation]"

**Inputs:**
- Spec file path (SKILL.md, plan, Ultrathink doc, or requirements file)
- Implementation scope (folder, file set, or auto-detect)

**Output:**
- Spec Compliance Report (markdown)
- Auto-saved to target's `docs/verification/` folder
- Linked in daily note Captures section (if using Obsidian daily notes)

## Spec Types Supported

| Type | Example Path | What to Extract |
|------|--------------|-----------------|
| SKILL.md | `skills/*/SKILL.md` | Instructions, Guidelines, Examples sections |
| Plan file | `.claude/plans/*.md` | Implementation Plan, Success Criteria |
| Analysis doc | `plans/*.md`, `docs/*.md` | Analysis output, Success Criteria |
| README | `*/README.md` | Requirements sections, feature lists |

## Output Format

```markdown
## Spec Compliance Report

**Spec:** [path]
**Implementation:** [scope]
**Verified:** [timestamp]

### Requirements Checklist
| # | Requirement | Status | Evidence | Notes |

### Summary
- Met: X of Y (Z%)
- Partial: X
- Missing: X

### Gaps Requiring Action
[Specific gaps with suggested fixes]

**Verdict:** [Spec Satisfied / Needs Fixes / Major Gaps]
```

## Verdicts

| Verdict | Meaning | Action |
|---------|---------|--------|
| Spec Satisfied | All requirements Met | Ready to ship |
| Needs Fixes | Partial/Missing but no blockers | Address gaps, re-verify |
| Major Gaps | Critical requirements Missing | Significant work needed |

## Testing

1. **Golden test:** Run against `tests/test-spec.md` with `tests/test-implementation/`
   - Expected: 2 Met, 1 Partial, 2 Missing = "Needs Fixes"

2. **Real-world test:** Run against instagram-carousel v2 Ultrathink doc
   - Should produce meaningful compliance report
   - Report saves to `skills/instagram-carousel/docs/verification/`

## Integration Points

- **QA agent:** A QA agent can invoke this skill and add commentary
- **lets-wrap:** Can trigger verification before session close
