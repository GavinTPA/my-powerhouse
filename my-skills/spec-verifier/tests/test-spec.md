# Test Spec - Golden Test Fixture

This is a test specification with 5 known requirements. The test-implementation folder contains a partial implementation (3 of 5 should be met).

## Requirements

1. **Must have a README.md file** - The implementation must include a README.md file in the root.

2. **Must export a main function** - The main script must export a function called `main()`.

3. **Must have error handling** - All functions must include try/catch error handling for edge cases.

4. **Must have tests directory** - The implementation must include a `tests/` directory with at least one test file.

5. **Must have docs folder** - The implementation must include a `docs/` folder with documentation.

## Expected Verification Results

When spec-verifier runs against this spec and the test-implementation folder:

| # | Requirement | Expected Status | Reason |
|---|-------------|-----------------|--------|
| 1 | README.md file | Met | File exists |
| 2 | Export main function | Met | main() exported in index.js |
| 3 | Error handling | Partial | try/catch exists but not all paths |
| 4 | Tests directory | Missing | No tests folder |
| 5 | Docs folder | Missing | No docs folder |

**Expected verdict:** Needs Fixes (2 Met, 1 Partial, 2 Missing)
