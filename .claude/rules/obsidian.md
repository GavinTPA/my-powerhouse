# Obsidian Rules

Topic-specific gotchas for Obsidian, Templater, and Smart Connections.

---

## Smart Connections MCP Caching

The Smart Connections MCP server caches embedding results. After changing folder exclusions or re-embedding in Obsidian, **restart the Claude Code terminal** to reset the MCP connection. Otherwise searches will return stale results.

---

## iPhone Performance (Plugin Culprits)

Obsidian on iPhone can take 3-5 minutes to become usable, with constant restarts when switching back to the app. **Root cause: Community plugins, not sync.**

**Mobile killers (keep OFF on iPhone):**

| Plugin | Why |
|--------|-----|
| `dataview` | Runs vault-wide queries on every load |
| `smart-connections` | Embedding computations, memory intensive |
| `obsidian-tasks-plugin` | Scans entire vault for task markers |
| `omnisearch` | Builds search index on startup |

**Safe to enable on mobile:**
- `recent-notes` - Lightweight, useful
- `periodic-notes` - Daily notes, minimal overhead
- `templater-obsidian` - Fine unless auto-running
- `obsidian-kanban` - Only loads when viewing kanban
- `table-editor-obsidian` - Editor enhancement
- `better-word-count` - Tiny

**Fix:** Settings -> Community Plugins -> Toggle OFF on iPhone. Enable only the safe ones. iOS aggressively kills memory-heavy apps.

---

## Templater Syntax

Templater uses different tag prefixes for different purposes:
- `<%*` = Execute JavaScript silently (control flow: `if`, `for`, `while`)
- `<%` = Output expression result (values like `<% variableName %>`)
- `<%*` with `-%>` = Execute and trim trailing whitespace

**Common error:** Using `<% if (...)` throws "Unexpected token 'if'" because `<%` expects an expression to output, not a statement to execute.

---

## Documentation as Linked Files (Not Inline)

When producing any documentation (guides, processes, research, reference material), **always save it as a separate Zettelkasten file and link it from the daily note** - never paste it inline in the daily note.

**Pattern:**
1. Create the doc: `Zettelkasten/[Title] - YYYY-MM-DD.md`
2. Link from the daily note

**Why:** Inline docs bloat the daily note, can't be linked from elsewhere, and get lost in the noise. Separate files are searchable, linkable, and reusable.

---

## Daily Note Safety

**When updating daily notes:**
1. **Find the file first** - Search for the actual filename (don't assume)
2. **Read it** - Confirm it exists and see its structure
3. **Edit to append** - Use Edit to add to the appropriate section
4. **Never use Write** - Write overwrites the entire file and destroys existing content
