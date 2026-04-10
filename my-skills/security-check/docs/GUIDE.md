# Security Check - How It Works

## The One-Sentence Version

Your bodyguard that makes a photocopy of important documents before anyone touches them.

## Why This Exists

A sed command wiped an entire `.zshrc` file. All API credentials — Gmail, Google, X/Twitter, everything — gone in one command. The file that took months to accumulate, destroyed in milliseconds.

This is the digital equivalent of accidentally shredding your master swipe file.

**The lesson:** Some files are too important to edit without a safety net.

## The Analogy

Think of this like a copy editor's protocol:

Before you mark up the original manuscript, you **make a photocopy**. Always. Even if you're "just fixing a typo." Because the one time you don't, that's when you spill coffee on the original.

Security Check is that protocol, automated.

## How You Use It

### The Automatic Way (Best)

You don't have to remember. When you say "add this to my .zshrc" or "update my git config", the skill automatically:

1. Makes a timestamped backup
2. Does the edit
3. Verifies the file still works

You'll see: "Created backup at ~/.zshrc.backup.20260119_143022"

That's your insurance policy.

### The Manual Way

Say "run a security check" and get a full audit:

- **Secrets scan** - Are there API keys hardcoded in your settings file that shouldn't be there?
- **Settings hygiene** - Is your permissions list getting bloated with junk?
- **Environment health** - Are all your API credentials actually loaded?

It's like running `/doctor` but for your security posture.

## What It Catches

### The .zshrc Problem
Backup before any edit. Period.

### The Settings Creep Problem
Every time you approve a command, it gets saved. Say yes to `git commit -m "fix: specific thing"` enough times and your settings file becomes a mess of specific commands that should be wildcards.

### The Hardcoded Secret Problem
Sometimes in the flow of approving things, a secret ends up in the settings file. "Just approve it to keep moving." Now that token is in a git-tracked file.

This finds those and tells you to move them to proper environment variables.

### The Missing Credential Problem
You set up a skill, but forgot to add the API key to your shell config. The skill fails silently. This tells you which variables are missing before you waste time debugging.

## The Safety Net Philosophy

Every word processor has Undo. Every version control system has history. But shell config files? One bad command and they're gone.

This skill adds the "Undo" that should have been there from the start.

## The Git History Problem

Even if you delete a file with secrets, **it's still in git history**. Anyone who clones the repo can see every version of every file that was ever committed.

The new git history scan catches this. Say "scan repo for secrets" and it searches every commit for credential patterns. If it finds something, you'll get:
- The commit hash where it appeared
- The file path
- What type of secret it looks like
- How risky it is (HIGH/MEDIUM)

**The fix:** Use tools like `git filter-repo` or BFG Repo-Cleaner to permanently remove the secrets from history, then rotate the compromised credentials.

## When to Run It

- **Automatically:** Let it do its thing before critical file edits
- **Weekly:** "Security check" as part of your weekly review
- **Before open-sourcing:** "Scan repo for secrets" to catch anything in history
- **After incidents:** Something broke? Run a check to see what's exposed
