# Handoff — BUG-1306, build → validate — written at 7e38d0ae, seq-2

## Next

Enter validate: set the feature station to `review` (`plan-merge.py set-feature-station`), run
`gh-sync.py status <feature-dir> review` — both deferred here because this run was told not to
touch GitHub — then dispatch `harness-validator-lead` with the `review` team against the pinned
`review_sha` in `feature.json`. The panel's own work is BRIEF SC-04 and SC-05, the two
`verify: inspection` criteria nobody has graded: SC-04 that the removal happens once at module
import, before any case body and before the raw `Popen` sites, cited `file:line` from
`git show <review_sha>:tests/integration/test-plan-merge.py`; SC-05 that the merge-base diff names
only the test file and this feature's artifacts. SC-01/02/03 are already measured green.

## Trust

- T-01's `verify:` prints `VERIFY-OK`, exit 0, both halves 291 PASS / 0 FAIL — orchestrator ran the block verbatim from the worktree root; builder and qa each measured it independently — verified-at 7e38d0ae
- The suite CAN report red at the shipped file — `PLAN_MERGE_BIN` pointed at a wrapper re-injecting the identity returns exit 1 with 17 failing checks, no repo file modified; this is the reachability proof qa's declined mutation check would have given — verified-at 7e38d0ae
- Both `case_1103_` bodies are byte-identical to pre-fix — region sha1 `0f5a679182…` matches `git show bfb77f23:…| sed -n 1097,1140p` against post-fix lines 1107-1150, and the diff has exactly 2 hunks, at pre-image lines 34 and 141 — verified-at 7e38d0ae
- The pre-fix/post-fix check counts differ by 12 (278 → 290) because a failing signature short-circuits its own case's later assertions, not because coverage moved — the same probe reported 261 PASS + 17 FAIL — verified-at 7e38d0ae
- The main checkout is clean of the builder's two stray early writes — `git -C /Users/molchairuangutai/GitHub/harness status --porcelain -- tests bin .claude .agents` is empty — verified-at 7e38d0ae
- `review_sha` names the seam commit, whose `plan.yaml` is byte-identical to disk, so INV-33 stays quiet — the pin was moved after the last plan write — verified-at 7e38d0ae
- qa's runner corroboration (`run-unit-tests.sh --kind integration`) proves the CI path unbroken and nothing about hermeticity — `run_pool.py:59-63` passes ambient env through — verified-at 7e38d0ae

## Dead ends

- Do not edit `plan-merge.py`; its env read is deliberate #1103 defence — plan.yaml D-03 — verified-at 7e38d0ae
- Do not add a shared `tests/integration/` helper, a second test file, or a tree-wide env lint — plan.yaml D-01, D-04 — verified-at 7e38d0ae
- Do not add a case asserting hermeticity; the checks already go red the moment the pop is removed — plan.yaml D-05 — verified-at 7e38d0ae
- Do not reword the module comment's `line 1188` citation or its tally, and do not fold the `run_verb` docstring sentence into it: all three are dictated verbatim by T-01's approved `intent:` and by D-02, so the edit amends approved plan text through a code file — runs/2026-09-05-01-eng-simplify/digest.md Q1, Q2 — verified-at 7e38d0ae
- Do not re-run the plan panel; it closed at cycle 0 with its one HIGH resolved before signature — plan.yaml `panel` — verified-at 7e38d0ae

## Working set

- .claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/.harness/harness/features/BUG-1306-agent-type-hermetic-tests/feature.json
- .claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/.harness/harness/features/BUG-1306-agent-type-hermetic-tests/BRIEF.md
- .claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/.harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/qa-BUG-1306-integration.md
- .claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/.harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/receipt-harness-backend-dev-T-01-c0.md
- .claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/tests/integration/test-plan-merge.py

## Done when

Scope: the review panel has graded SC-04 and SC-05 at the pinned review_sha
Authority: approval:.claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/.harness/harness/features/BUG-1306-agent-type-hermetic-tests/BRIEF.md#Success Criteria
Authority: approval:.claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/.harness/harness/features/BUG-1306-agent-type-hermetic-tests/BRIEF.md#Approval
