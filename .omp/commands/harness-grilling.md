# /harness-grilling — dialog to clarity before anything is built

Load `harness-grilling` and run it, here in the main session (no subagent has a user channel).

- **With a loose idea or a feature request** → grill it to clarity, write the artifact, then offer
  `/harness-plan` with the artifact path as pm's input. Do not start planning unasked.
- **Inside repository registration** → the `harness-add-repo` skill calls this for its technical
  interview; the answers seed the repository's own `harness.json`, which must land on its default
  branch.
- **Standalone** ("stress-test this", "grill me on X") → run it and write the artifact; nothing
  downstream is implied.

This is step zero of `/harness-plan` and is **blocking** — pm plans from what it is told, so unstated
assumptions become REQs nobody meant (DEC-164). Skipping it is the
user's call to make explicitly, never yours to assume.
