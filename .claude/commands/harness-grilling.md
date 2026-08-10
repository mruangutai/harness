# /harness-grilling — dialog to clarity before anything is built

Load `harness-grilling` and run it, here in the main session (no subagent has a user channel).

- **With a loose idea or a feature request** → grill it to clarity, write the artifact, then offer
  `/harness-plan` with the artifact path as pm's input. Do not start planning unasked.
- **Inside onboarding** → `/harness-init` calls this as its interview; the answers seed
  `harness.json`, the domain description, and the first glossary terms.
- **Standalone** ("stress-test this", "grill me on X") → run it and write the artifact; nothing
  downstream is implied.

This is step zero of `/harness-plan` and of `/harness-init`, and it is **blocking** — pm plans from
what it is told, so unstated assumptions become REQs nobody meant (DEC-164). Skipping it is the
user's call to make explicitly, never yours to assume.
