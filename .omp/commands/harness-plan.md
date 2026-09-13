# /harness-plan — plan a feature to an approved PLAN

Read `.omp/commands/harness.md` and follow it with **mission: plan**. The differences:

- **Step zero, BLOCKING:** load the `harness-grilling` skill and run it first — dialog to clarity
  with the user, name the destination, record settled/fog/out-of-scope, and hand pm the artifact
  **path** as a BRIEF input (DEC-164). A wayfinding map whose frontier and fog are both empty is
  the same hand-off — pass `.harness/efforts/<slug>/MAP.md` (DEC-165). Already have either
  artifact? Cite it and move on. Skipping it is the user's explicit call, never your assumption.
- **Refuse without a mission.** The artifact's `## Mission` block must read `mission: plan`, with
  its `reason:` and the operator's `confirmed-by:` or `overridden-by:` line (SC-01). No block →
  back to step zero; `mission: patch` → this is `/harness-patch`'s feature, not yours. The
  judgement is the harness's and the confirmation is the operator's; you do not re-derive either
  here, and you never pick `plan` because it is the safer-looking route (SC-22).
- **KICKOFF: the source ticket moves to Plan** — before the BRIEF work begins, run
  `python3 .claude/skills/harness/bin/board-station.py <issue-number> plan` from the repo root.
  The ticket is the issue the user names in the opening ask or in answer to step zero; no separate
  question is asked for it, and the number is an issue of `harness.json`'s `github.repo`. When
  **no ticket is named**, write nothing and ask nothing. The source is usually a wayfinding ticket
  the harness did not create — moving it is deliberate: the harness moves any card it is pointed
  at and closes only cards it created. Best-effort: a board failure prints one line and planning
  continues.
- **Target state:** BRIEF and `plan.yaml` `pending`, produced by ONE `plan` run — the orchestrator
  dispatches the `plan` team to product-lead once, and everything the plan phase does happens
  inside that run: pm drafts; in one turn the readers see the same draft — `scope` (code-reviewer:
  orphan SCs, traces to nonexistent SCs, non-topological dependencies, verify-vs-delete, and the
  architecture read), `should-not-exist` (fable-advisor, skipped-and-recorded when it does not
  resolve) and `design` (ui-reviewer, self-scoped out on a non-UI plan); pm fixes every `form`
  finding in place, applies every `substance` finding, records the panel (`plan-merge.py
  record-panel`) and resolves every anchor and route (`plan-merge.py check`); then pm grades the
  plan once, per perspective, against the operator's stated intent. No separate eng-lead review,
  no second squad segment, no per-cycle goal-check (SC-04, SC-09). Every finding carries `kind`;
  a `proportionality` finding no reader opposes downgrades the mission to `patch` inside the
  orchestrator, and you see it at signature, not as a question (SC-03).
- **Terminus:** ONE approval, taken by you — the user signs PLAN **and** the prototype (if the
  feature needs one) together, and **the same signature carries the rework ruling**:
  `plan-merge.py sign-approval --file <plan.yaml> --by <you> --date <YYYY-MM-DD> --rework rounds=N,minutes=M --decision <path>`
  writes `approval.status: approved` and `feature.json` `rework` in one act (SC-15); the
  orchestrator's build-phase fix loop runs inside that ruling and does not ask again. Findings the
  user accepts ride as `--overrule PF-ID:<reason>` on the same command. Completing plan is NOT a
  briefing (§10.3).
  **The signature is immediately followed by**
  `python3 .claude/skills/harness/bin/gh-sync.py status <feature-dir> ready`, which moves the
  task sub-issues to `Ready` and never the parent. It **refuses unless `approval.status` is
  `approved`**, so a card at Ready is proof of a signature rather than a claim about one.
- After approval, offer `/harness-ship` — do not start it unasked.
