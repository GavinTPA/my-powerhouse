## Testing Plan for spec-verifier

### Pre-flight Checks
- [ ] Skill appears in `.claude/skills/` symlinks
- [ ] Skill registered in `settings.local.json`
- [ ] New terminal session started (settings refresh)

### Skill Discovery Test
- [ ] Run: "What skills are available?"
- [ ] Expected: spec-verifier appears in list with correct description

### Basic Invocation Test
- [ ] Run: "verify spec"
- [ ] Expected: Skill asks for spec file and implementation scope

### Golden Test (Self-Verification)
- [ ] Run: "Verify tests/test-spec.md against tests/test-implementation/"
- [ ] Expected output should match tests/expected-output.md:
  - 2 Met (README.md, main function)
  - 1 Partial (error handling)
  - 2 Missing (tests directory, docs folder)
  - Verdict: Needs Fixes

### Real-World Test
- [ ] Run: "Verify [a real skill in your repo] against its plan"
- [ ] Expected:
  - Produces meaningful compliance report
  - Report saves to target's docs/verification/ folder
  - Link added to daily note Captures (if using Obsidian)

### Auto-Save Test
- [ ] After any verification, check:
  - Report saved to target's docs/verification/ folder
  - Link exists in daily note Captures section

### Integration Test (QA Agent)
- [ ] Run: "QA verify spec for [target]"
- [ ] Expected: QA agent invokes spec-verifier and adds commentary

### Edge Case Tests
- [ ] Empty spec file: Should report "No requirements found"
- [ ] Non-existent spec: Should report file not found error
- [ ] Missing implementation folder: Should report scope not found
