# Handoff — BUG-1306, validate → ship — written at 6b2ef992, seq-3

## Next

Ship is the operator's gate, not a squad's: no fix cycle is owed, and `check-state.sh` now exits
0 with ZERO violations repo-wide. Put the two non-blocking operator questions in front of the
user — pm Q1 (BRIEF SC-04 / plan D-02 cite the raw `Popen` sites as "near lines 305/309"; at the
pin they are 315/319, both files approval-gated) and pm Q2 (EMERGENT: no standing gate exercises
this suite under a governed ambient identity, so deleting the pop keeps CI green and reintroduces
the bug for agents only — pm recommends a separate dev-ops ticket, out of scope here per BRIEF
## Constraints). Then run the ship phase against `review_sha` `6b2ef992`. Backlog candidates for
the ship briefing, all advisory, none gating: B-1 the SC-04/D-02 anchor drift (chore), B-2 the
governed-identity CI leg (enhancement), B-3 the security note's internal miscitation (chore),
B-4 the standing `plan.yaml` finding PF-15e50cd4137f8309fac4057506bd40a5 — SC-05 gates which
FILES changed, not which LINES (bug, open for FUTURE edits, discharged for this one), B-5
`handoff_done_when.py` FINDING_RE requiring numeric finding ids (bug), B-6 `check-state.sh`
INV-35 being line-based (bug — worked around here by rewording, not fixed in the checker).

## Trust

- The pin is now `6b2ef992` and the executable payload is UNCHANGED across every pin this feature has had: tests/integration/test-plan-merge.py is the same blob object `8fde5efc9c05eac9f3f312dd6191b45c89ad2f23` at 7e38d0ae, 536afda3, da05ea28, 6b2ef992 and e2bf649c, and `git diff --name-only da05ea28 e2bf649c -- tests bin .claude .agents '*.py' '*.sh'` is empty — verified-at 6b2ef992
- The owner's INV-35 remediation changed exactly ONE panel string and nothing else: finding PF-15e50cd…'s `consequence` now reads `issue 1103` instead of `#1103`; all six finding ids, `approval: approved`, `status: review` and T-01 `done` are intact, re-loaded with yaml.safe_load — .harness/harness/features/BUG-1306-agent-type-hermetic-tests/plan.yaml — verified-at 6b2ef992
- `check-state.sh` exits 0 with zero violations repo-wide; INV-35, INV-33 and INV-26 are all green — run from this worktree, which is the only checkout whose working tree holds the feature dir — verified-at 6b2ef992
- All five criteria are met and were re-measured by pm, then SC-01/02/03/05 re-measured again at THIS pin: governed run exit 0 / 0 FAIL with both SC-02 literals present, clean run exit 0 / 0 FAIL, and the merge-base diff names 23 paths — the one test file plus 22 lifecycle artifacts, no `bin/` path, no second test file — notes/research-BUG-1306-goalcheck-validate-c0.md — verified-at 6b2ef992
- The panel is PASS with `must_fix` empty, severity_max `info`, `code_grade: pass`; all four reviewers reached their own verdict and ui declined on a measured census, not a prediction — notes/review-harness-code-reviewer-c0.md, notes/review-harness-qa-c0.md, notes/review-harness-security-reviewer-c0.md, notes/review-harness-ui-reviewer-c0.md — verified-at da05ea28, whose code blob is identical to this pin
- The suite CAN report red: the pinned source with its one pop line replaced by `pass`, under `HARNESS_AGENT_TYPE=harness-orchestrator`, exits 1 with 14 FAIL lines — the BRIEF's pre-fix shape. Compiled in memory under the original `__file__`; no repo file written — verified-at da05ea28, same blob as this pin
- The `unit` kind is EXECUTED, not inherited: exit 0 / 0 FAIL both with `env -u HARNESS_AGENT_TYPE` and ambient governed, 27 files and 342 check lines discovered — verified-at da05ea28, same blob as this pin

## Dead ends

- Do not re-pin again or re-run the panel; the pin is current, plan.yaml has not moved since it, and INV-33 is green — .harness/harness/features/BUG-1306-agent-type-hermetic-tests/feature.json — verified-at 6b2ef992
- Do not edit `plan-merge.py`, add a shared `tests/integration/` helper, a second test file, a runner scrub, or a tree-wide env lint — plan.yaml D-01, D-03, D-04 — verified-at 6b2ef992
- Do not "fix" the SC-04 / D-02 line numbers on the branch: BRIEF and plan are approval-gated and only the main session signs — .harness/harness/features/BUG-1306-agent-type-hermetic-tests/BRIEF.md ## Approval — verified-at 6b2ef992
- Do not treat a green `run-unit-tests.sh --kind integration` as hermeticity evidence; `run_pool.py` passes ambient env through, so only the direct invocation measures it — notes/review-harness-qa-c0.md — verified-at 6b2ef992
- Do not record run dir `2026-09-05-05-validator`; its own state.yaml reads `status: superseded` and its record moved to `2026-09-05-06-validator` — runs/2026-09-05-05-validator/state.yaml — verified-at 6b2ef992

## Working set

- .harness/harness/features/BUG-1306-agent-type-hermetic-tests/feature.json
- .harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/research-BUG-1306-goalcheck-validate-c0.md
- .harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/review-harness-code-reviewer-c0.md
- .harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/review-harness-qa-c0.md
- .harness/harness/features/BUG-1306-agent-type-hermetic-tests/BRIEF.md

## Done when

Scope: the operator has ruled on Q1 and Q2 and the ship phase has run against 6b2ef992
Authority: approval:.claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/.harness/harness/features/BUG-1306-agent-type-hermetic-tests/BRIEF.md#Success Criteria
Authority: approval:.claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/.harness/harness/features/BUG-1306-agent-type-hermetic-tests/BRIEF.md#Approval
