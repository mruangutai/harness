# Handoff — BUG-1302-suite-layout-fail-closed, build → validate — written at ac8dd671, seq-1

<!-- RESHAPED, NOT RE-AUTHORED. The build ran main-session-direct under DEC-174 and left this
     note freeform; check-state.sh flagged it against the DEC-159/160 shape gate. The validate
     orchestrator rewrote it into the five-section grammar on 2026-09-05. Every claim below was
     already made by the build note or is cited to an artifact predating this rewrite. -->

## Next

Dispatch the independent validation panel against `feature.json` `review_sha`, never a moving
HEAD: the validator squad for the qa test-matrix gate and the two-stage code review, the product
squad for the SC-01..SC-10 goal-check. Both test files are `main-session-direct` under DEC-174, so
a panel member may read and run them but never edit them; a defect returns as a send-back.

## Trust

- T-01..T-05 are at station `done` and the feature station is `review` — plan.yaml `tasks[].status`
  and top-level `status:` — verified-at ac8dd671
- `python3 tests/unit/test-suite-layout.py` exits 0, every printed check PASS — covering the four
  new B-4/B-5 checks, both B-6 checks, B-14, the real-layout check, the sole-implementation sweep,
  case 11 hygiene and cases 1..10 — build-time run — verified-at ac8dd671
- `python3 tests/integration/test-run-unit-tests-layout.py` exits 0 with all eight pre-existing
  named checks plus the widened case 2 — build-time run — verified-at ac8dd671
- Each of the five B-row reds was observed before its fix landed —
  notes/red-demonstrations-2026-09-05.md — verified-at ac8dd671
- B-8's assertion discriminates: the widened clause exited 1 against a runner mutated to print the
  integration sentinel before refusal, the old narrow clause exited 0 against the identical mutant
  — notes/red-demonstrations-2026-09-05.md T-05 — verified-at ac8dd671
- `code-grade.py` over the branch diff PASSes; `_violations_callers`, `_is_inside_tests` and
  `_literal_key_present` are each grade 3 — build-time run — verified-at ac8dd671
- The four-angle simplify pass ran BEFORE the pin: REUSE, EFFICIENCY, ALTITUDE empty;
  SIMPLIFICATION one positional-AST extraction applied; unit suite re-run exit 0 —
  notes/receipt-harness-dev-ops-2026-09-05-2-eng-altitude.md — verified-at ac8dd671
- Only the two approved test files and BUG-1302 lifecycle artifacts changed —
  `git diff --stat 54f01854 ac8dd671` — verified-at ac8dd671

## Dead ends

- Editing either test file from inside a squad — DEC-174 reserves both to the main session and the
  blanket `tests/**` grant carries no weight — BRIEF.md ## Constraints — verified-at ac8dd671
- Remedy (b) for B-6, a positive control independent of the live `test_kinds` config — it proves
  only that the pipeline reddens in a fabricated world — BRIEF.md ## Residual risk — verified-at ac8dd671
- Widening scope to `sole_implementations`'s silent skip — a real fail-open of B-6's own class in
  the same file, ruled out of scope — runs/2026-09-05-2-eng/digest.md AR-08 — verified-at c369fb1
- Reviewing a moving HEAD — the only commit after the pin changes one line of feature.json and
  carries no implementation — `git show --stat ee1eeb67` — verified-at ee1eeb67

## Working set

- .harness/harness/features/BUG-1302-suite-layout-fail-closed/BRIEF.md
- .harness/harness/features/BUG-1302-suite-layout-fail-closed/feature.json
- .harness/harness/features/BUG-1302-suite-layout-fail-closed/notes/red-demonstrations-2026-09-05.md
- tests/unit/test-suite-layout.py
- tests/integration/test-run-unit-tests-layout.py

## Done when

Scope: the validation panel and the goal-check have both reported against the pinned review_sha
Authority: finding:.claude/worktrees/harness/BUG-1302-suite-layout-fail-closed/.harness/harness/features/BUG-1302-suite-layout-fail-closed/notes/research-BUG-1302-goalcheck-plan-c1.md#F-2
