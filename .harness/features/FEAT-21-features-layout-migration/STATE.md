# STATE

## Current

- feature: FEAT-21-features-layout-migration
- phase: build — all ten tasks are main-session-direct; layer 0 builds, I sequence and verify
- run: none (main-session-direct segments are not runs)
- squad: none
- status: awaiting-user

Both approvals are signed on disk (BRIEF.md `## Approval`, plan.yaml `approval.status: approved`,
operator, 2026-08-14) and the plan/approval artifacts are committed to
`feat/FEAT-21-features-layout-migration`. feature.json now reads `branch` set, `status: Building`.
cycles_used stays 2 — no rework has occurred.

T-01 is handed back to layer 0 as the first and only ready task. It is the sole task with no
dependencies, it lands as its OWN commit before anything moves, and it also captures the PRE-MOVE
boundary state that T-09 cannot retake. T-01 status is `building` in plan.yaml and `gh-sync.py
start-task T-01` has run.

Base state verified by me at 62fef85, immediately before the hand-back: `layout_migration.py` exits
0 printing `features: CLEAN — evidence legacy`, `docs: CLEAN — evidence legacy`,
`layout: 2 surface(s) clean, 0 mixed, 0 cannot-verify`; `check-state.sh` exits 0 with zero INV-27
lines and no FEAT-21 finding. That is exactly the pre-move state T-09's intent requires T-01 to
capture, so a deviation at T-01 means the tree drifted, not that the expectation is wrong.

The sequence after T-01: T-02..T-08 and T-10 produce NO `[harness:t-NN]` commits — T-09 lands the
whole cluster as one commit. So between T-02 and T-08 "landed" means working-tree edits with the
task's form-check `verify:` green; the full suites are deliberately red in that window and only
T-09 runs them. After T-08 every path I pass to `gh-sync.py` and every state file I write moves to
`.harness/harness/features/FEAT-21-features-layout-migration/`.

## Open Questions

- Q-A (advisory, for the builder, not a blocker; binds T-06 and T-10, NOT T-01): both new clauses
  anchor on the FIRST occurrence of their label string, so an unprompted earlier mention relocates
  the region. Writing `migrated_depth` into test-validate-feature-json.py's module docstring without
  adding the case makes the region docstring-to-first-`def`, which already contains a re-anchored
  path, and it false-greens. Two smaller ones from the same source: a conjunct written against a
  module-level constant instead of an inline literal false-REDS, and a literal parked in case_22a's
  detail f-string rather than its assertion condition false-GREENS.
- Q-B (advisory; binds T-06 and T-10, NOT T-01): zero DEC-182 headroom — T-10's machine fields sit
  at 50/50 and T-06 at 49/50 against `MACHINE_LINES_PER_TASK = 50`
  (check-plan-routes.py:280). Signing is unaffected, since the approval block is not a task, but the
  next line added to either `verify:` reds the gate. This is also why I edit plan.yaml by surgical
  line replacement and never by a YAML load/dump round-trip: a re-wrap reds the gate on a plan whose
  meaning did not change.
- Q9 (from the plan run, unchanged — the harness owner's, not this feature's): a lead hosting a
  team cannot yield its turn while backgrounded members are in flight, and leads hold no
  SendMessage, so a lead cannot resume a member to clear that member's own FAIL. Already noted for
  the backlog.
