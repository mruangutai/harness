# Wayfinding — charting and working the map

**MUST read this in full before charting a map or working an existing map.** The resident rules
live in `harness-wayfinding`; this is its bounded walkthrough (DEC-158, DEC-165/166/167).
Use the config-selected storage mode. All tracker operations go through
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/wayfind.py`; mutations are dry-run
until `--apply`. GitHub is the canonical tracker store, never accompanied by a markdown shadow.

## Charting (first session)

1. **Name the destination** — load and run
   `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-grilling/SKILL.md` on that alone. It fixes
   the scope, so it is settled before anything else.
2. **Map the frontier breadth-first** — grill across the whole space rather than deep on one thread,
   surfacing the open decisions and what is takeable now. **Surfaced no fog?** The idea did not need
   a map: stop, say so, and hand the grilling artifact to `/harness-plan` (offer the hand-off;
   do not start planning unasked).
3. **Create the map** — tracker: `wayfind.py chart "<destination>" --apply`, then fill its body's
   Destination and Notes (decisions empty, the dim view in `## Not yet specified`). Markdown:
   the same from `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/templates/MAP.md` at
   `<HARNESS_CONTROL_PLANE_ROOT>/.harness/efforts/<slug>/MAP.md`, with tickets at `tickets/T-NN-<slug>.md`.
4. **Create the tickets you can specify now** (`wayfind.py ticket <map#> <type> "<title>" --apply`),
   then wire blockers in a **second pass** — issues need ids before they can reference each other
   (`wayfind.py block <n> --by <n> --apply`).
5. **Fire the research tickets in parallel** — they need no user, so they run now while the map is
   fresh.
6. **Stop.** Charting resolves nothing; a session that charts and then starts resolving has spent
   its context on both and done neither well.

## Working the map (each later session)

1. Load the low-res view — `wayfind.py map <n>` (tracker) or `MAP.md` (markdown). Not every
   ticket body.
2. Take the first frontier ticket (or the one the user names) and **claim it first**, before any
   work, so a concurrent session skips it — `wayfind.py claim <n> --apply` (the assignee IS the
   claim; an open unassigned ticket is unclaimed). Markdown: mark the ticket `claimed` in the table
   before working it.
3. Resolve it by its type. Zoom only what this ticket needs. For a frontier round, follow
   `harness-wayfinding`'s resident two-axis batching criteria: research fires in parallel;
   independent shallow HITL questions form one numbered round with a recommendation each, then wait.
4. Record the answer as the ticket's resolution and close the ticket, then gist it on the map.
   Tracker: `wayfind.py resolve <n> --body "<answer>" --gist "<one line>" --apply`; short answers
   need no local file. `--file <path>` can supply an already-file-backed resolution body instead of
   `--body`; it is not permission to create a markdown shadow. Substantial assets stay in repo files
   **linked** from the resolution, never pasted as its body or kept as a second decision copy.
   The tool writes the resolution comment, closes the ticket, and appends the pointing gist to the
   map's `## Decisions so far`. Markdown: write `## Resolution` in the ticket file, mark it `closed`, then
   add **one gisted line** pointing at it in the map's `## Decisions so far`.
5. **Graduate the fog the answer sharpened** into new tickets, clearing those patches from
   `## Not yet specified`. If the answer puts something past the destination, close it into
   `## Out of scope` with the reason — never resolve it on the route.
6. **One THREAD per session, then stop** — even if you feel fine: the next session starts fresh and
   cheap, and a long session writes worse answers (DEC-159). A thread is either one ticket explored
   deeply, **or one frontier round**. Sessions are contexts, not calendar days: running six
   back to back in an afternoon is the intended use, and costs only a map reload each.
