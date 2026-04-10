# ghl-connect Roadmap

## Shipped

| Version | Date | What Changed |
|---------|------|--------------|
| v1.3 | 2026-02-16 | Add `--add-tags` flag for tag-only operations (email + tags, no name fields needed) |
| v1.2 | 2026-02-10 | Fix tag search: switch to POST /contacts/search for server-side tag filtering. Fix --email param bug. |
| v1.1 | 2026-02-06 | Fix get_messages pagination: handle nested dict response, fix direction/messageType/subject extraction |
| v1.4 | 2026-02-19 | Mark conversations as read: `mark_read.py` with single and batch modes, --type filter |
| v1.0 | 2026-02-05 | Initial release: read inbox, send emails, search contacts, trigger workflows, security sanitization |

## Planned

- [x] ~~Add `--add-tags` flag to `create_contact.py`~~ — Shipped v1.3
- [x] **Mark conversations as read** — Shipped v1.4 (2026-02-19). `mark_read.py` with `--conversation-id` and `--all-unread` modes, `--type` filter.
- [ ] Conversation assignment (assign to team member)
- [ ] SMS sending support
- [ ] Dynamic email content via custom fields (no need to edit workflow in GHL)
- [ ] Webhook listener for real-time new message notifications

## Ideas (Not Committed)

- **GitHub collaborator detection** - Regex match GitHub usernames in emails, present to Ed for collaborator addition
- **Smart reply templates** - Common responses pre-drafted based on message patterns
- **Member onboarding automation** - Detect new member emails, trigger welcome sequence
- **Email analytics** - Pull open rates, click rates from GHL via API
- **Integration with bb-call-prep** - Auto-fetch Basecamp history when composing replies
- **MCP server** - Expose GHL as an MCP server for broader agent access

## What We've Learned

### 2026-02-10 - Tag Search Fix

- `GET /contacts/` has NO tag parameter — only query, limit, startAfterId, locationId
- Passing tag as `query` does text search, client-side filter misses most results (returned 2/8)
- `POST /contacts/search` supports server-side tag filters via `filters` array
- Official API docs have empty schema — real spec lives on ClickUp: https://doc.clickup.com/8631005/d/h/87cpx-158396/6e629989abe7fad
- Page-based pagination (page/pageLimit) not cursor-based (startAfterId)
- `--email` param was also broken — `GET /contacts/` doesn't accept `email`, must pass as `query`

### 2026-02-06 - Messages Pagination Fix

- Messages endpoint returns nested dict, not flat list like conversations
- `paginate()` helper only works for flat-list endpoints (conversations, contacts)
- Direction lives at `meta.email.direction`, not top-level
- `messageType` field (e.g. `TYPE_EMAIL`) replaces numeric `type`

### 2026-02-05 - Initial Build

- Private Integration Token is simpler than OAuth for personal/single-user use
- No bulk send API exists in GHL -- workflow triggers are the correct pattern for group emails
- GHL email content can be HTML -- need to strip it for safe display
- Prompt injection defense is critical for any skill that reads external messages
- The API uses cursor-based pagination with `startAfterId`, not page numbers
- Rate limits are generous (100 req/10s burst) but worth respecting anyway
