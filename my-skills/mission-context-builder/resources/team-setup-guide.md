# Setting Up Your Mission Context - Team Edition

Your founder has already created the company context. This guide gets YOUR personal AI workspace connected to it in about 15 minutes.

---

## Before You Start

Make sure you have:
- Your Powerhouse folder set up (you've done the Tech Stack Setup)
- Claude Code installed and working
- The `company-context.md` file your founder sent you

---

## Step 1: Drop in the Company Context

Open Finder and navigate to your Powerhouse folder. The path is:

```
my-skills/mission-context/resources/
```

Drop the `company-context.md` file into that `resources` folder.

If you are not sure where your Powerhouse folder is, it is usually at:
```
~/Documents/my-powerhouse/
```

So the full path would be:
```
~/Documents/my-powerhouse/my-skills/mission-context/resources/
```

---

## Step 2: Build Your Context

Open your terminal. Navigate to your Powerhouse folder and start Claude Code:

```
cd ~/Documents/my-powerhouse
claude
```

Then type: **build my mission context**

Claude will automatically detect the company context file and:
1. Show you the team roster and ask which role is yours
2. Ask a few questions about YOUR specific role (5-7 questions, about 10-15 minutes)
3. Build your personalized context file that combines the company info with your role

Answer in your own words. Your answers do not need to be polished - Claude shapes them into the final format.

---

## Step 3: Verify It Worked

After the builder finishes, type: **who am I?**

Claude should know:
- Your name and role at the company
- What the company does and who you serve
- How you communicate
- The company terminology

If something is off, type: **update my mission context to change [whatever needs fixing]**

---

## That's It

Your Powerhouse now knows who you are, who your company serves, and how you communicate. Every skill you use from now on references this context automatically.

### If the Company Context Gets Updated

Your founder may send you an updated `company-context.md` from time to time. When that happens:
1. Drop the new file into the same `resources` folder (it will replace the old one)
2. Type: **rebuild my mission context**

### Questions?

Screenshot the issue and send it to your founder or the AI Powerhouse community.
