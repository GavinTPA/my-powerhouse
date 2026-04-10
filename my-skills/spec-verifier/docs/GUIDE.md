# Spec Verifier - How It Works

## The One-Sentence Version

Before you ship, check what you built against what you planned - systematically.

## Why This Exists

You know that feeling when you finish a big project and think "Did I actually do everything I said I would?"

Without a systematic check, you either:
- Forget something important
- Spend 20 minutes re-reading the spec manually
- Ship and find out later

This is the "did we actually do it?" checklist on autopilot.

## The Business Coach Analogy

Think of it like a coach reviewing a client's homework:

**Without spec verification:** "I did the work!" → "Great... did you?" → (awkward silence)

**With spec verification:** "Here's exactly what you committed to, here's what I found, here's what's missing." → Clear next steps.

The spec is the promise. The implementation is the delivery. This skill checks the receipts.

## How You Use It

### The Simple Way

Say: "Verify this skill against its spec" or "Check spec compliance for [thing]"

You'll get back a report showing:
- What requirements were found in the spec
- Which ones are done, partial, or missing
- What gaps need attention
- A verdict: ship it, fix it, or major rework

### The Integration Way

If you have a QA agent, it can use this skill automatically when you ask for spec verification. The QA agent adds the "what could go wrong" commentary on top of the systematic checklist.

## What It Doesn't Do

This isn't magic. It:
- Doesn't run your code
- Doesn't test functionality
- Doesn't judge quality of implementation

It checks: "Did the thing you said you'd build actually get built?" Evidence-based, not opinion-based.

## The Learning Flywheel

Every time you run a verification, the report saves to the target's docs folder. Over time, you build a history:

- "Instagram-carousel has failed on audience detection 3 times"
- "This skill consistently misses error handling requirements"

Patterns emerge. You learn. You improve.

That's the "constant and never-ending improvement" loop built into the system.
