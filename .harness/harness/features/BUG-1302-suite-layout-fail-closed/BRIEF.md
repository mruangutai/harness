# BRIEF — BUG-1302-suite-layout-fail-closed

## Problem

The two test files that prove the suite-layout gate discriminates carry one fail-open branch, two
dead branches, one under-asserting case and one unguarded read. Case 11 of
`tests/unit/test-suite-layout.py` prints `INAPPLICABLE case 11 behavioural: positive control ...` and
asserts nothing when `select_control_candidate()` returns `None` (B-6): the day a `test_kinds` change
blinds the layout detector to an offender class, the control that exists to catch it goes quiet and
green. `_literal_key_present` carries a conjunct that can never be False (B-4) and `_is_inside_tests`
a `".."` comparison nothing can reach (B-5) — dead code inside the file that proves a required CI
gate works, where a reader cannot tell a covered path from an uncovered one. `_violations_callers`
`read_text()`s every git-tracked source file unguarded (B-14), so a tracked-but-deleted or non-UTF-8
source raises a traceback instead of failing as a named assertion. Integration case 2 asserts only
that `PASS test-unit.py` is absent (B-8) where case 4 asserts the broader `PASS test-`, so case 2
would pass with the integration sentinel having run before the refusal.

## Goal

Make the suite-layout enforcement tests fail closed and carry no dead code: every branch in the two
files either reaches an assertion that can go red, or is gone. When a future `test_kinds` change
removes the positive control's ground, the suite turns red with a message that says which of the two
repairs applies — instead of printing a line nobody reads.

## Requirements

- REQ-01 (B-4): `_literal_key_present` in `tests/unit/test-suite-layout.py` no longer contains the
  conjunct that can never be False, and its verdict over every input is unchanged.
- REQ-02 (B-5): `_is_inside_tests` in the same file no longer contains the unreachable `".."`
  comparison, and its verdict over every input — including patterns carrying a `".."` segment — is
  unchanged.
- REQ-03 (B-6): case 11's positive control fails closed. When `select_control_candidate()` yields no
  candidate, the run FAILS, and the failure text names both repairs: extend `CANDIDATE_CORPUS` with a
  shape the new config counts, or treat the config change as a detection regression.
- REQ-04 (B-14): `_violations_callers` reports an unreadable tracked source as an assertion failure
  naming that path, for both hazards — a tracked-but-deleted path and a tracked non-UTF-8 source —
  rather than raising.
- REQ-05 (B-8): integration case 2 asserts that BOTH sentinels are absent, so it cannot pass with the
  integration sentinel having run.
- REQ-06: both suites still pass against the real repository, and the layout assertions over the live
  tree and live `test_kinds` config are unweakened by any of the five fixes.

## Success Criteria

Every criterion is executed by running one of the two files; each new assertion must be demonstrated
failing before the fix lands (revert the removal, or restore the old branch, and observe the red).
No criterion pins a line number: anchors are function names, literal content strings, or AST shape.

- SC-01 (REQ-01, B-4 behavioural): `tests/unit/test-suite-layout.py` asserts `_literal_key_present`
  over a fixed core corpus that includes BOTH cores whose span after the last wildcard is a clean
  source extension (for example `test-*.py`, `probe-*.py`) and cores whose trailing span is not (for
  example `test_*x`, `test-*.p*y`, `test-x.py`, `probe-*.md`), with the verdict for each core stated literally in
  the test and equal to the pre-removal function's verdict.
  verify: automated — `python3 tests/unit/test-suite-layout.py` exits 0 and prints no FAIL line, and
  `git show <review_sha>:tests/unit/test-suite-layout.py | grep -q "b4 corpus: _literal_key_present
  verdicts unchanged"` exits 0 (the named check is absent today, so the criterion is falsifiable).
  evidence: unit
- SC-02 (REQ-01, B-4 structural absence): the same file parses itself with `ast`, locates the
  `_literal_key_present` FunctionDef, and asserts BOTH counts the removal makes true: exactly one
  `ast.Call` whose func is an `ast.Name` with id `any` — the surviving `SOURCE_EXTENSIONS` extension
  check — and exactly one `ast.Constant` whose value is the string `"*?["` — the surviving
  wildcard-position comprehension. Measured against the pre-removal function at
  c369fb1fdfc74a8f78edc9a2df2a8fea738afc94 both counts are 2; reintroducing the removed conjunct
  restores both to 2, so the assertion FAILS. A zero-`any()` anchor would be false of the correct
  fix, because the extension check is itself an `any()` call.
  verify: automated — `python3 tests/unit/test-suite-layout.py` exits 0; restoring the conjunct makes
  it exit 1; the observed FAIL line is recorded in notes/red-demonstrations-2026-09-05.md.
  evidence: unit
- SC-03 (REQ-02, B-5 behavioural): the file asserts `_is_inside_tests` over a fixed pattern corpus
  that explicitly includes patterns carrying a `".."` segment (for example `../x/*.py`,
  `tests/../evil/*.py`), plus `tests/unit/**`, `**/*_test.*`, an absolute pattern and a bare `*`, with
  each verdict stated literally and equal to the pre-removal function's verdict.
  verify: automated — `python3 tests/unit/test-suite-layout.py` exits 0 and prints no FAIL line, and
  `git show <review_sha>:tests/unit/test-suite-layout.py | grep -q "b5 corpus: _is_inside_tests
  verdicts unchanged"` exits 0 (the named check is absent today, so the criterion is falsifiable).
  evidence: unit
- SC-04 (REQ-02, B-5 structural absence): the file asserts by `ast` that the `_is_inside_tests`
  FunctionDef contains exactly one string constant `".."` — the early guard — so restoring the `".."`
  element of the normalized-prefix comparison makes the assertion FAIL.
  verify: automated — `python3 tests/unit/test-suite-layout.py` exits 0; restoring the disjunct makes
  it exit 1; the observed FAIL line is recorded in notes/red-demonstrations-2026-09-05.md.
  evidence: unit
- SC-05 (REQ-03, B-6 fail-closed): the no-candidate branch of case 11 calls `check(...)` with a
  constant false condition instead of printing, and the file contains no `INAPPLICABLE` string.
  verify: automated — `out=$(python3 tests/unit/test-suite-layout.py)` exits 0,
  `printf '%s\n' "$out" | grep -q '^PASS b6 message: the no-candidate failure names both remedies'`
  succeeds — that check asserts by `ast` that the branch's `check()` call takes the literal `False`
  as its second positional argument, which is what makes "constant false condition" falsifiable
  rather than assumed — and
  `git show <review_sha>:tests/unit/test-suite-layout.py | grep -q INAPPLICABLE` exits non-zero.
  evidence: unit
- SC-06 (REQ-03, B-6 the check can go red): the file asserts that
  `select_control_candidate()` returns `None` under a literal `test_kinds` fixture whose only running
  kind detects `tests/unit/**` (no `CANDIDATE_CORPUS` entry qualifies), proving the branch is
  reachable; and asserts by `ast`, in one check, that the branch's `check()` call carries both remedy
  phrases — one naming `CANDIDATE_CORPUS` extension, one naming a detection regression — AND that
  its second positional argument is the literal `False`.
  verify: automated — `python3 tests/unit/test-suite-layout.py` exits 0; deleting either remedy
  phrase from the detail string, or replacing the literal `False` with a truthy expression, makes it
  exit 1; the observed FAIL line is recorded in notes/red-demonstrations-2026-09-05.md.
  evidence: unit
- SC-07 (REQ-04, B-14 both hazards): the file builds a git fixture containing a tracked-then-deleted
  `.py` file and a tracked `.py` file whose bytes are not valid UTF-8, calls `_violations_callers` on
  it, and asserts the call RETURNS (no exception propagates) with a result naming both offending
  paths, so the repository-wide caller check fails with the path in its detail.
  verify: automated — `python3 tests/unit/test-suite-layout.py` exits 0; against the unguarded
  `read_text()` the same case raises and the run exits non-zero; the observed FAIL line is recorded
  in notes/red-demonstrations-2026-09-05.md.
  evidence: unit
- SC-08 (REQ-05, B-8): integration case 2 asserts the absence of the generic sentinel prefix covering
  both sentinels, and the narrow single-sentinel absence clause survives nowhere in the file. The
  narrow-clause check is what discriminates: the generic clause is ALREADY present in case 4, so
  grepping for it alone would pass before the change.
  verify: automated — over `git show <review_sha>:tests/integration/test-run-unit-tests-layout.py`,
  `grep -q '"PASS test-unit.py" not in p.stdout'` exits NON-ZERO (today it exits 0, so the criterion
  is falsifiable), `grep -c '"PASS test-" not in p.stdout'` reports exactly 2 — cases 2 and 4 — and
  `python3 tests/integration/test-run-unit-tests-layout.py` exits 0. Reverting case 2 to the
  single-sentinel assertion turns the first two clauses red; the observed FAIL line is recorded in
  notes/red-demonstrations-2026-09-05.md.
  evidence: integration
- SC-09 (REQ-06 regression safety): both files pass end to end against the real repository with the
  live `test_kinds` config, and the pre-existing checks — real layout clean, sole-implementation
  sweep, case 11 hygiene certification, cases 1 to 10 — still report PASS. Exit 0 alone does NOT
  discharge this criterion: a suite that runs and discovers nothing also exits 0, so each named
  pre-existing check is asserted by name against the run output.
  verify: automated — `out=$(python3 tests/unit/test-suite-layout.py)` exits 0 and
  `printf '%s\n' "$out" | grep -q '^PASS <name>'` succeeds for each of `real layout is valid`,
  `sole implementation sweep` and `case 11 hygiene: every running-kind detect pattern is certified`,
  and for the prefix `^PASS case N: ` for every N from 1 to 10;
  `int=$(python3 tests/integration/test-run-unit-tests-layout.py)` exits 0 and carries a `^PASS `
  line for each of `clean layout`, `runs unit`, `runs integration`,
  `git clean tree runs both sentinels`, `git tracked rogue refused before sentinels`,
  `git three tracked rogues reported in sorted path order`,
  `git enumeration failure refused before sentinels` and
  `git untracked rogue is not reported and both sentinels run`. Neither run may print a FAIL line.
  Deleting or short-circuiting any one of those pre-existing checks leaves its grep with nothing to
  match, so the criterion goes red on a suite that discovers less than it did at `<review_sha>`.
  OWNER AND TIMING: the build-time qa gate executes this command, once, after all five tasks have
  landed and before the ship decision, and cites the run transcript in its DIGEST. No task's
  `verify:` owns it and none should: T-01 to T-04 gate on whole-file exit code, which catches a
  pre-existing check that BREAKS but not one silently DELETED, and T-05 declares `depends_on: []`,
  so a clause attached to the last task of the T-01 to T-04 chain could run before T-05's edit to
  the integration file had landed. This criterion spans BOTH files, so it is checked once at the
  gate rather than per task.
  evidence: unit
- SC-10 (REQ-06 routing recorded): the plan's routing is what DEC-174 requires — every implementation
  task `main-session-direct`, with the two test files declared as carve-out lanes.
  verify: inspection — a reader runs `python3 .claude/skills/harness/bin/check-plan-routes.py
  .harness/harness/features/BUG-1302-suite-layout-fail-closed/plan.yaml` and confirms it exits 0,
  printing five DEVIATION lines — one per task, naming only those two paths — and no VIOLATION line.
  The method is `inspection`, not `automated`, because no test under `tests/unit/` or
  `tests/integration/` runs this checker over a live plan; the live-tree run is the CI `integration`
  job (`.github/workflows/tests.yml`, DEC-183). The evidence is the cited command transcript, not a
  test kind.

## Constraints

- DEC-174 BINDS both files (Advisor RULING, this feature's validator digest, run
  `2026-09-05-2-validator`). `run-unit-tests.sh` is a gate and DEC-174's enumeration reaches the test
  file of each. Every implementation task is `main-session-direct`; no squad member may write either
  file. The blanket `tests/**` grant to backend-dev, dev-ops and qa in `team-config.yaml` carries no
  weight against it. `check-plan-routes.py` prints a DEVIATION line for these tasks; that is designed
  audit trail, it does not count as a violation, and the plan accepts it. This SUPPLIES the route; it
  does not block the work.
- DEC-213 SUPPLIES the layout predicate these tests exercise — `tests/unit/**` and
  `tests/integration/**` select the kind, and the predicate refuses tracked test-shaped files outside
  `tests/`. Nothing in this feature changes the predicate or the registry; only its tests change.
- DEC-179 and DEC-183 SUPPLY the plan-time routing check that SC-10 runs.
- No file outside these two is edited: `suite_layout.py`, `run-unit-tests.sh`, `code_grade.py`,
  `.harness/harness.json` and `team-config.yaml` are read-only for this feature.
- Operator stop conditions carried from the stated-intent artifact
  (`.harness/notes/grilling-six-residual-bugs-2026-09-05.md`): no risk acceptance, no scope
  reduction, no failed-gate waivers; unrelated cleanup, redesigns and compatibility shims are out of
  scope; existing unrelated user changes stay untouched.

## Residual risk and its owner

B-6 is fixed by remedy (a) — convert the `INAPPLICABLE` branch into a hard failure. Remedy (b),
synthesising a positive control independent of the live `test_kinds` config, was REJECTED: such a
control proves only that the pipeline can go red in a fabricated world, and would pass silently
through exactly the live-config regression B-6 exists to catch.

Accepted risk of (a): a legitimate `test_kinds` change that leaves `CANDIDATE_CORPUS` with no
qualifying candidate turns the suite red on fixture maintenance rather than on a real layout
violation. This is why the failure message must name both remedies — extend `CANDIDATE_CORPUS` with a
shape the new config counts, or treat the config change as a detection regression — so the red routes
to a five-line fixture fix rather than being misread as a gate regression. Coverage of the live
config does not rest on the positive control alone: `hygiene_uncertified` / `_certify_pattern`
assert unconditionally in the same case — but that compensating control is narrower than it looks.
It certifies the SHAPE of every running kind's configured `detect` pattern against the adversarial
basename corpus; it never runs a live path through `offenders()`. So it catches a malformed or
over-broad `detect` pattern, and it does NOT catch a well-formed config change that blinds the gate
to a real offending path. That residual blind spot is the price of remedy (a), and the two-remedy
failure message is what routes it.

RED OWNERSHIP (lead-tier finding, carried here so a later run does not rediscover it): because
`CANDIDATE_CORPUS` lives inside a DEC-174 file, that future red can never be cleared by a squad
member. The fixture fix is `main-session-direct` by construction, and belongs to the main session.

AST PIN FALSE POSITIVES, AND WHO CLEARS THEM (plan-panel cycle 1, finding
PF-1ada4741b4b00970cf6013518244f0f5, low, reader `should-not-exist`). The structural AST assertions
in T-01, T-02 and T-03 are the correct trade and are not weakened here: the B-4 tautological
conjunct and the B-5 unreachable comparison are invisible to any behavioural corpus — every input
returns the same verdict with or without them — so a structural assertion is the only detector that
can exist. The cost, recorded so it reaches the signature rather than being rediscovered later: any
legitimate future refactor that changes the `any()` / `"*?["` / `".."` census inside those functions
turns the gate suite red under a FAIL name that misdescribes the cause — for example `b4 structural:
the tautological conjunct is absent` firing when nothing was reintroduced. Because both pins live
inside `tests/unit/test-suite-layout.py`, a DEC-174 file, that red is main-session-only to clear,
exactly like the B-6 fixture red above. The repair is to re-derive the expected count against the
refactored function and update the pin; it is fixture maintenance, not a gate regression.

## Verification gaps

- None on the surfaces this feature touches: `unit` and `integration` are `active` kinds with real
  runners in `.harness/harness.json`, and every criterion here rests on one of them. The kinds with
  `cmd: null` — `component`, `ui`, `typecheck`, `eval`, `functional` — cover no surface this feature
  changes.

## Non-goals

- B-4's ship-review row also records "the remaining grade-2 med code-grade record". That clause IS
  delivered here, as a measured consequence of REQ-01, not a disclaimed non-goal:
  `_literal_key_present` is grade 2 at `c369fb1fdfc74a8f78edc9a2df2a8fea738afc94` (cyclomatic 12,
  cognitive 13, abc 18.4) and grade 3 once T-02 deletes the tautological conjunct (cyclomatic 10,
  cognitive 13, abc 15.1), both measured with `code_grade.grade_source` over the file's own text.
  T-02's `verify:` pins the post-fix grade at 3, so the clearance is verified rather than claimed.
  The other grade-2 record that row could mean — `suite_layout.py tracked_paths` — is NOT touched:
  `suite_layout.py` is read-only for this feature. Beyond that one function, no code-grade record is
  produced, re-graded or cleared, and no grading run is added to any gate.
- No production code changes: neither `suite_layout.py` nor `run-unit-tests.sh` is edited.
- Amending DEC-174's enumeration to name `run-unit-tests.sh` is not done here — it is an open
  question for the operator.
- The other residual rows from the BUG-1286 ship review (B-7, B-9 to B-13, B-15) belong to their own
  issues.

## Approval

status: pending
