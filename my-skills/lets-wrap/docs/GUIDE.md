# Lets Wrap - Your End-of-Session Ritual

## Why This Matters

Every time you use Claude, it learns things about you. How you like your emails to start. What you call your clients. The phrases you'd never use. Your preferences, your corrections, your way of working.

Here's the problem: Claude forgets everything when you close the terminal.

Lets-wrap fixes that. It's a 2-minute ritual at the end of every session that captures what Claude learned and writes it into your system permanently. Next session, Claude starts smarter.

Think of it like this: imagine hiring a new assistant every day, but they always read yesterday's notes before starting. That's what lets-wrap does — it writes the notes.

## How It Works

At the end of any session, just say:

> lets wrap

Claude will:

1. **Review the session** — Summarise what you worked on (in plain English, not code)
2. **Scan for learnings** — Find corrections, preferences, and discoveries from your conversation
3. **Propose updates** — Show you exactly what it wants to remember, and where it goes
4. **Ask your approval** — Nothing gets saved without your say-so
5. **Save to GitHub** — Back everything up safely
6. **Close cleanly** — Tell you exactly how to exit and how to come back

The whole thing takes about 2 minutes.

## What Gets Smarter

Your system has two places where Claude stores what it knows about you:

**Mission Context** (`my-skills/mission-context/SKILL.md`)
This is the big one. It's your identity file — who you are, who your clients are, your voice, your terminology. Every skill reads this. When lets-wrap updates your mission context, every tool you use gets better.

**CLAUDE.md** (your operating manual)
This is for workflow preferences and standing instructions. Things like "always explain the why" or "I work on newsletters in the morning."

Lets-wrap knows the difference and routes each learning to the right place.

## The Compound Effect

Session 1: Claude has no idea who you are.
Session 5: Claude knows your voice and your client language.
Session 10: Claude writes first drafts that sound like you.
Session 20: Claude anticipates what you need.

This is the compound loop in action. Every session that ends with lets-wrap makes every future session better. Skip it, and you're starting from scratch.

## Tips

- **Run it every session.** Even short ones. Small corrections compound fast.
- **Be honest when it asks.** If it proposes a learning that's wrong, say so — that's a learning too.
- **Don't worry about "doing it right."** There's no wrong way to end a session. Lets-wrap handles the details.
- **It's fast.** If nothing was learned, it says so and closes in 30 seconds.

## Common Questions

**What if I forget to run it?**
No harm done — you just miss capturing that session's learnings. Run it next time.

**What if it proposes something wrong?**
Say "skip" or "no." It only saves what you approve.

**What if I haven't built my mission context yet?**
Lets-wrap will save learnings to your CLAUDE.md instead, and remind you to build your mission context when you're ready.

**What if I close the terminal without wrapping?**
Your work files are still saved locally. You just missed the learning capture. The git backup won't happen until next time you wrap.
