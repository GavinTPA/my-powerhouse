# Task Tools Rules

Topic-specific gotchas for Claude Code's Tasks system.

---

## Task Tools Overview

Claude Code provides persistent Tasks for tracking work across sessions.

| Tool | Purpose |
|------|---------|
| `TaskCreate` | Create new task with subject, description, activeForm |
| `TaskUpdate` | Change status, add dependencies, update metadata |
| `TaskGet` | Retrieve full task details by ID |
| `TaskList` | List all tasks with summary info |

---

## Status Workflow

Tasks progress: `pending` -> `in_progress` -> `completed`

**Before starting work:**
```
TaskUpdate(taskId="1", status="in_progress")
```

**After completing:**
```
TaskUpdate(taskId="1", status="completed")
```

---

## Dependencies Pattern

For sequenced work, use `addBlockedBy`:

```
# Task 2 can't start until Task 1 completes
TaskUpdate(taskId="2", addBlockedBy=["1"])
```

---

## Metadata for Context

Store arbitrary data in `metadata`:

```
TaskCreate(
    subject="Fix authentication bug",
    metadata={
        "skill": "my-skill-name",
        "branch": "fix/auth-refresh",
        "complexity": "Low"
    }
)
```

---

## Gotchas

### TaskCreate returns ID in output

The task ID is in the tool output message. Parse it to use for dependencies.

### Tasks persist after session ends

Tasks stay on disk. Clean up completed batches periodically or they accumulate.

### blockedBy prevents work

A task with unresolved `blockedBy` dependencies can't be worked on. Use `TaskGet` to check dependency status before claiming a task.

### activeForm shows in spinner

The `activeForm` field appears while the task is `in_progress`. Write it in present continuous ("Running tests" not "Run tests").
