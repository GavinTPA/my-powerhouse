# Spec Verifier - Roadmap

## Shipped

| Version | Date | What Changed |
|---------|------|--------------|
| v1.0 | 2026-01-14 | Initial release - core verification logic, auto-save reports |
| v1.1 | 2026-02-06 | Severity weighting - Blocker/Should-Have/Nice-to-Have classification, severity-based verdicts |

## Planned

- [ ] Integration with lets-wrap skill (auto-verify before session close)
- [ ] Integration with package-skill.sh (verify SKILL.md before packaging)
- [ ] Aggregate verification history analysis ("what patterns keep failing?")
- [x] Severity weighting for requirements (blocker vs nice-to-have) — shipped 2026-02-06

## Ideas (Not Committed)

- Multi-spec verification (verify against multiple specs at once)
- Diff mode (compare two verification runs)
- Auto-fix suggestions for common gaps
- Integration with adversarial-spec tool for multi-model consensus

## What We've Learned

*To be filled in as we use it*

**Initial design decisions (2026-01-14):**
- Hybrid approach: skill handles methodology, QA agent adds wisdom
- Fresh eyes pattern: verify what's written, not what was intended
- Learning flywheel: auto-save reports builds improvement data
- Sources: @trq212 tweet, Boris Cherny insights, adversarial-spec tool
