# /harness-plan — plan a feature to an approved PLAN

Read `.claude/commands/harness.md` and follow it with **mission: plan**. The differences:

- **Step zero, BLOCKING:** load the `harness-grilling` skill and run it first — dialog to clarity
  with the user, name the destination, record settled/fog/out-of-scope, and hand pm the artifact
  **path** as a BRIEF input (DEC-164). A wayfinding map whose frontier and fog are both empty is
  the same hand-off — pass `.harness/efforts/<slug>/MAP.md` (DEC-165). Already have either
  artifact? Cite it and move on. Skipping it is the user's explicit call, never your assumption.
- **KICKOFF: the source ticket moves to Plan** — before the BRIEF work begins, run
  `python3 .claude/skills/harness/bin/board-station.py <issue-number> Plan` from the repo root.
  The ticket is the issue the user names in the opening ask or in answer to step zero; no separate
  question is asked for it, and the number is an issue of `harness.json`'s `github.repo`. When
  **no ticket is named**, write nothing and ask nothing. The source is usually a wayfinding ticket
  the harness did not create — moving it is deliberate: the harness moves any card it is pointed
  at and closes only cards it created. Best-effort: a board failure prints one line and planning
  continues.
- **Target state:** BRIEF approved (write it via `pm` if absent — or route to `/harness-init` if the
  project has no `.harness/` at all), then the plan-feature sequence run by the orchestrator:
  product-lead's squad plans, the eng squad runs the four-angle simplify pass over the plan surface (`.claude/skills/harness-simplify/SKILL.md`) — FLAG-ONLY, findings return to `harness-pm`, which applies them to its own draft before the signature, because `check-domain.sh` grants `plan.yaml` and `BRIEF.md` to pm alone (D-03) — eng-lead reviews architecture, ui-reviewer checks the design contract.
- **Terminus:** ONE approval, taken by you — the user signs PLAN **and** the prototype (if the
  feature needs one) together. Completing plan is NOT a briefing (§10.3).
  **The signature is immediately followed by**
  `python3 .claude/skills/harness/bin/gh-sync.py status <feature-dir> Ready`, which moves the
  task sub-issues to `Ready` and never the parent. It **refuses unless `approval.status` is
  `approved`**, so a card at Ready is proof of a signature rather than a claim about one.
- After approval, offer `/harness-ship` — do not start it unasked.
