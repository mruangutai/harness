# BUG-2253 c8 code review — PASS

**Amended SC-01/SC-02 satisfied by inspection; scope-reduction cleanup leaves no dead helpers or new blocker.** Reviewed `3dd8bb677bb2936361e3952030fc24f15bf9afc6..7e590f735af90220baec7013c7ce8eafc2163bce`; previous PASS `3ba8dd4bf65392a1dd4fe99dddfebb14fe68d01d`. No source changes or reviewer executions of tests.

## Stage 1 — specification compliance

- Read current BRIEF, plan (decisions empty), feature pin, operator amendment and previous lead assessment before judging the diff. SC-02 is now inspection-only; removed behavioral machinery is deliberately not required. Product `docs/` contains neither `spec.md`, `decisions.md` nor `architecture.md`; no substitute guidance invented.
- SC-01 / T-01: `validate-digest.py:2489-2549` lists ordered FAIL/MUTATED lines, retaining duplicates, before the existing 20-line tail only after a nonzero independent run. Heading is conditional; no-match fallback, stdout-then-stderr concatenation, exit 2, suite selection and 1800s timeout remain. Integration `test-validate-digest.py:6413-6465` retains three genuine hook-path cases; unit `test-validate-digest-run-pool-lines.py:30-71` retains seven production-loaded parser/report cases. Canonical-reader inventory is unchanged.
- SC-02 inspection / T-01: `tests/integration/test-validate-digest.py:1025-1030` defines `HOOK_HANG_BUDGET_S = 30` with FIFO, dangling-symlink, 10,000-deep-JSON, fail-not-hang and load-headroom rationale. Exactly six calls use it at `:3033`, `:3066`, `:3286`, `:3288`, `:3316`, `:3318`. Full base diff changes no other timeout. Actual hostile-metadata and restoration safety cases remain (`:3011-3094`, `:3278-3348`).
- Full commit walk identifies no foreign work or human-tagged commits; initial git status is clean. Current pin agrees with feature.json. Requirement/record commits after the pin are not treated as source changes.

## Stage 2 — quality and evidence

- Previous-PASS-to-pin Python diff contains only integration cleanup: 224 removed / 3 added lines (221 net removed), not 232. All site-observation, blocked-process, watchdog and containment definitions/callers are gone. Pinned-tree removed-symbol sweep finds no executable references; imports are unchanged and removed-only imports were local to deleted helpers. Retained gate fixture helpers/constants all have callers; ordinary group registration remains.
- Empty git diffs establish validator equivalence from `3c6fb908` and unit equivalence from `d9026b74` through this pin; gate/unit also have no changes from previous PASS. Integration's three gate cases are untouched by the cleanup. `run_pool.py:110-136` confirms the parsed header/FAIL/mutation shapes. No new silent-loss or fail-open branch found.
- Exact-output unit assertions bind real production behavior; empty/None returns cannot satisfy them. `receipts/red-c4.txt/.stdout` records exact-base diagnostic loss; `green-c4.txt` records fixed execution. `unit-red-b228c3a2.stderr` exposes genuine no-hide failure. Exact-base unit errors are missing-helper errors, not seven behavioral reds. Historical 17-case receipts include deliberately deleted SC-02 cases and are not claimed as current execution.
- Main supplies pinned grading: exit 0, **21 PASSING**, supporting `code_grade: pass`. Used git diff/show/grep/log/status, source inspection and supplied receipts only. No tests, mutants, grader, builds, lint, formatter or broad suites run. QA alone executes the signed verify: `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases && python3 tests/unit/test-validate-digest-run-pool-lines.py`.

## Retained advisories — no fix order

- **substance / low / T-01, accepted:** echoed runner-shaped headers plus FAIL or adjacent mutation-note text can over-list a filename; real failures cannot be un-named and nonzero runs still refuse.
- **substance / info / outside T-01:** unchanged runner launch/timeout fail-open can leave a QA claim unverified; explicitly excluded policy, not a BUG-2253 blocker. #2283 concurrency is likewise excluded.

## Principles applied

- **Delete First:** accepted removal of all SC-02 machinery without replacement scaffolding; preserved real safety cases and six constant arguments.
- **harness-code-review:** distinguished behavioral failure receipts from missing-helper errors and historical execution from current inspection.

Open questions: none. Must-fix: none.
