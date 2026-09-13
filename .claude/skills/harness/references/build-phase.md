# The build phase — build, validate, fix

Read this at build entry, after the signature. The playbook carries the order in one line; this
is each segment's procedure. Evidence and history: DEC-224, DEC-226, DEC-232.

A `build` team is single-squad by construction (DEC-118), so it is only the eng segment; `validate`
and `fix` each host every reader in one run. In this order.

1. **Build entry.** Immediately after signed approval and before dispatching any task, run
   `gh-sync.py open <feature-dir>`. It records `feature.json` `github.build_entry`; Build does not
   start without one because `gh-sync.py start-task` refuses at exit 2 when it is absent.
   `recovery-required` may proceed, but gates merge until the main session re-runs idempotent `open`.
2. **The eng segment.** Dispatch the named `build` team — resolve it
   `<HARNESS_CONTROL_PLANE_ROOT>/.harness/teams/build.yaml` first, then
   `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/teams/build.yaml` (`harness-team/SKILL.md`
   step 1). **You choose WHICH tasks go to `eng-lead`**; **the lead routes each one to the
   specialist that owns it** by `consult-when`. Two different decisions — it routes, it does not
   revisit your selection. **As the segment starts dispatching — not after it finishes — record the
   FEATURE's own station** with `plan-merge.py set-feature-station --station building`. That is
   the feature's station and not a task's: `gh-sync.py start-task` writes only the task's, so
   without this write nothing advances the feature (BUG-1507). A stale `files:` anchor at build
   entry is the builder's to re-resolve, not a FAIL (SC-07).
3. **SIMPLIFY, the last build step** — once every planned task has a PASS run and **BEFORE
   `review_sha` is pinned**, because an apply commit after the pin moves the tip and invalidates
   every reader's verdict. Sequence it to `harness-eng-lead`, never the validator lead. **The
   dispatch must tell the lead to read
   `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-simplify/SKILL.md` first** — it is not
   preloaded, and the four angles, the apply rules and the one-fix ceiling all live there. Re-run
   the suites after the apply, before the pin. An empty pass is a real outcome; nothing is invented
   to justify the step.
4. **Entering validate**, pin `review_sha` (INV-6) and run `gh-sync.py status <feature-dir> review`
   BEFORE the team is dispatched. Both preconditions sit together on purpose: the pin fixes what is
   reviewed, the station write puts the parent and every sub-issue at review. The station argument
   is LOWERCASE — one vocabulary, and `gh-sync.py` refuses anything else (FEAT-41).
5. **ONE `validate` dispatch** to `harness-validator-lead` —
   `<HARNESS_CONTROL_PLANE_ROOT>/.harness/teams/validate.yaml`, then
   `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/teams/validate.yaml`; run-dir slug
   `validate-validator`. In one turn over that one sha: `qa` (gate-only) enforces the
   `test_matrix` hard gate and writes `fail_first` evidence per automated SC — a green suite with
   none is FAIL (SC-17); beside it `code`, `security`, `ui` (self-scopes out on a non-UI diff) and
   pm's `goalcheck` — the second and last goal-check of the feature, one grade per perspective
   against the diff, written to `notes/research-<FEAT>-goalcheck-validate-c<cycle>.md`. The lead
   fans in to ONE consolidated must-fix list, `kind` on every finding, `severity_max`. No two
   consecutive reader runs over one sha (SC-13).
6. **The fix loop.** On `must_fix`, pin nothing: dispatch `fix` to `harness-validator-lead`
   (`<HARNESS_CONTROL_PLANE_ROOT>/.harness/teams/fix.yaml`, then the skills copy; slug
   `fix-c<N>-validator`) with inputs `feat`, `review_sha` and the must-fix path, **naming the
   owning dev** — the `execution_agent` of the task each must-fix finding cites, read from
   `plan.yaml`; that is the one derivation, and `files_touched` in a build digest is only its echo.
   Two devs in one list is two `fix` runs in dependency order. **A finding that cites no task, or a
   file no task's `files:` owns, has no owning dev and is not fixed here:** it is a new finding
   class — a scope change — and goes to the operator in `open_questions`, never silently to the
   nearest dev. The dev is hosted in the validator lead's run (DEC-224; author and reviewer stay
   distinct personas). The dev fixes test-first and commits; the lead's readers — `qa`, `code`,
   `security`, `ui` — re-verify over the tip that commit produced, in the same run, and the digest
   names that tip. **The pin is yours, never the lead's:** on return, record it as the new
   `review_sha`. Each round is one `cycles_used` and one `regate` judgement. **The loop runs inside
   the operator's rework ruling** — `feature.json` `rework` `rounds` and `wall_clock_minutes`
   (SC-15) — without asking. `substance` findings are fixed inside it; only a NEW finding class (a
   scope change, an emergent SC) or budget exhaustion ends it early, and each of those is a
   `continue` judgement before it is a return.

Documentation is a product segment, sequenced the same way once validate is clean.
