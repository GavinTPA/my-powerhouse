# Session Intelligence — Roadmap

## Shipped

| Version | Date | What Changed |
|---------|------|--------------|
| v1.0 | 2026-02-19 | Initial release — chat analysis engine with prompt burst detection, Training Summary + Attendee Detail document generation, mission-context integration, zero-prompt mode |

## Planned

- [ ] **Transcript-enhanced prompt detection** — Use VTT transcript as second detection signal (host reads prompts aloud). Currently chat-only detection works well; transcript would add confidence
- [ ] **Session-processor incorporation** — Consider using session-processor's `process_transcript.py` for the Training Summary Session Flow section. Session-processor has working key moment detection that could enhance coaching takeaways
- [ ] **Member distribution** — Package for ai-powerhouse-starter. Remove any Ed-specific assumptions, test with member Zoom profiles
- [ ] **Attendance-to-CRM cross-reference** — Match attendees to GHL contacts for richer coaching context (who's a client, who's a lead, who's absent)

## Ideas (Not Committed)

- Post-session-orchestrator integration (auto-detect sessions from calendar, process automatically)
- Trend analysis across sessions (who's attending consistently, who dropped off, topic patterns)
- Auto-generate follow-up email drafts based on coaching notes
- Sentiment scoring on chat messages
- Compare Attendee Detail across sessions for the same person (coaching arc over time)

## What We've Learned

- (v1.0) Burst detection with unique responder count is more reliable than total message count — one person posting 5 times isn't a burst, 5 people posting once is
- (v1.0) Filtering noise (reactions "Reacted to...", reply-quotes "Replying to...", emoji-only) dramatically reduces false positive prompts — from 20 to 2 on a real BB Jam test
- (v1.0) Deduplication within 60-second clusters handles rapid-fire host messages that are all part of one prompt moment
- (v1.0) Zero-prompt mode is essential — labs, hot seats, and Q&A sessions don't use chat prompts. The skill needs to work without them
- (v1.0) BB Jams (40 people, conversational) have very different chat patterns from BB Trainings (100+ people, prompt-heavy). The burst threshold may need to be adjustable per session type
