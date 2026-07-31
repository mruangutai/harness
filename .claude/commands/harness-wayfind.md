# /harness-wayfind — chart a vague idea to plannable clarity, across sittings

Load `harness-wayfinding` and run it here in the main session (HITL tickets need the user channel).

Storage is chosen by config, never preference: `github.sync: true` → the map is a `wayfinder:map`
issue with tickets as sub-issues, native blocking, assignee-as-claim, all driven through
`bin/wayfind.py` (mutations dry-run until `--apply`). Sync off or `gh` unavailable → local markdown
under `.harness/efforts/<slug>/` (DEC-166).

- **With a loose idea** → apply the entry test first. Fits one conversation? Use `/harness-grill`
  instead and say so — a map for a small idea is overhead. Otherwise **chart**: name the
  destination, map the frontier breadth-first, create the map and the tickets you can specify,
  fire the research tickets, stop.
- **With an existing map** (issue number, or path/slug in markdown mode) → **work it**: take one frontier ticket, claim it, resolve
  it by its type, record the resolution, graduate the fog it sharpened. One decision per session
  (research excepted).
- **When the frontier and the fog are both empty** → the effort is plannable. Hand `/harness-plan`
  the map — issue number or path; do not start planning unasked.

The two doors in order: `/harness-wayfind` for fog that outlasts a sitting, `/harness-grill` for an
idea one sitting can settle. Either way the output is decisions, never deliverables — building is
`/harness-plan` onward (DEC-164/165).
