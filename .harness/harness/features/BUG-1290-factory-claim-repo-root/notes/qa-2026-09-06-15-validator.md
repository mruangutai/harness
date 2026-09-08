# QA — test-matrix gate — BUG-1290 B-27 fix cycle (HEAD fb9a4ac4)

## BLUF

**PASS.** The B-27 fix does exactly what the operator's directive asked, and I reddened it four
independent ways myself, including the one that matters most: neutering the key-collapse mutant
while keeping its reached-marker leaves `5b` green, proving the new arm discriminates the
collapse itself rather than the mutant's mere presence. Both named suites print their exact
expected final lines at exit 0. The full-suite unit and integration runners are green (0
`^FAIL ` lines in integration; the 4 in unit are `test-factory-claim-mutation.py`'s own internal
PROOF markers inside its exit-0 pass, not script failures). Production is confirmed
byte-identical to `c488218e` by my own re-measurement. Working tree is clean; no scratch worktree
created.

## Phase 1 (no source access)

From BRIEF/plan/operator answer alone, this cycle needed: (1) `5g` to stop accepting a merely-
raising mutant as satisfying the negation — i.e. assert the mutation's *specific* observable, and
(2) an independent path where the real suite literally *prints* `FAIL BUG-1290 5b` under the
key-collapse, not just an in-process capture. Both exist and both are test-only (SC-07/SC-08/SC-09
integration & mutation-boundary requirements were already closed in prior cycles; this cycle
touches only `5b`/`5g` and the mutation file's second arm). No Phase-1 expectation for this
directed fix cycle is uncovered — `coverage_gaps: []`.

## Matrix resolution (change_type: bugfix, graded over the FEATURE diff `main..HEAD`, not the
fix-cycle diff, per standing instruction)

- **unit** — required (`touches_runtime_code`, since the feature diff touches
  `factory_claim.py`/`factory_config.py`/`feature-worktree.py`/`layout_fixtures.py`/
  `layout_migration.py`). **satisfied** — `run-unit-tests.sh --kind unit`, exit 0, all 28
  script rows `PASS`, including `test-factory-claim.py` and `test-factory-claim-mutation.py`.
- **integration** — the `bugfix` `when` predicate `fix_confined_to_tests_and_contract_docs` does
  NOT fire for the feature as a whole (production changed in earlier cycles), but SC-07/SC-09
  name `tests/integration/test-factory-integration.py` and `test-layout-migration.py` as their own
  verification, so I add it per the floor-not-ceiling rule. **satisfied** — `run-unit-tests.sh
  --kind integration`, exit 0, 46 files, all `PASS`, both named scripts among them, 0 `^FAIL `
  lines.
- **`__bug_class__` / `match_bug_class`** — **n/a**. Per repository Expertise G-08, this predicate
  is a currently-unresolvable placeholder (no bug-class taxonomy entry fires for any diff), so no
  kind is obligated by it. Grounds: read directly, no taxonomy table exists to match against.
- **ai_behavior / config / frontend / feature / api / cross_module / logic** — **n/a**, none of
  their `always`/`when` conditions apply; this is a `bugfix`-typed task set exclusively.
- **eval, functional, component, ui, typecheck, omp_session_accessor, handoff_comprehension,
  issue_types_live** — not implicated by this diff (no touched files match their `detect` globs);
  **n/a**, not required by the matrix for this change.

## Suites run (verbatim final lines, my own re-run)

- `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py` → `125/125 checks passed.`,
  exit 0.
- `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim-mutation.py` → prints
  `MUTATION PROOF: 3/3 cases reddened` and `KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed`, exit 0.
- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` → runner
  exit **0**; `grep -c '^FAIL '` = **4** — all four are `test-factory-claim-mutation.py`'s own
  internal `FAIL  BUG-1290 5x: ...` diagnostic print lines (its intentional mutation-proof output,
  captured inside an exit-0, `PASS`-scored script row), not a script-level failure; `grep -nE
  '^(PASS|FAIL) test-'` shows 28/28 `PASS`, 0 `FAIL`.
- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` →
  runner exit **0**; `grep -c '^FAIL '` = **0**; 46/46 scripts `PASS`, including
  `test-factory-integration.py` and `test-layout-migration.py`.
- Production identity: `git diff --stat c488218e -- .agents/ .claude/skills/ bin/` → empty,
  re-measured myself (not inherited from the eng digest).

## Test-first audit (test-only change)

There is no production code in this cycle's diff — `git show --stat fb9a4ac4` touches only
`feature.json`, the operator note, two receipts, and the two test files. "Test written before the
code" doesn't apply; the honest statement is that this cycle *is* the test, in response to an
operator-signed gap in a prior cycle's test. No violation to report, none invented.

## Each new arm — can it report red, and how I proved it myself

1. **`5g` (tightened assertion, `test-factory-claim.py:1319-1352`).** Perturbed the in-suite
   mutant's `issue_number` to `raise RuntimeError(...)` instead of delegating (a "merely raising"
   mutant — exactly the B-27 defect class). Result: `5g` **reddened**
   (`(False, 2, '', 'factory: claim: unexpected failure: RuntimeError...')` — code 2, not the
   expected 1, message doesn't match "unresolvable blocker"). Under the OLD bare
   `not _5b_property_holds(...)` this would have passed vacuously (property_holds already returns
   False for any non-zero code). Restored; suite back to 125/125, `git status --porcelain` clean.
2. **Harness fixture's `depends_on=["T-99"]` (`test-factory-claim.py:382`).** Deleted it (task
   `T-77` with no dependency). Result: suite **reddened** — `5g` failed (`mutant_cond` flipped to
   `True` since the now-dependency-free task resolves "clear" even under the collapsed cache, so
   the mutation stops producing its expected observable). Confirms the dependency is load-bearing
   for the mutation proof's discriminating power. Restored; verified clean.
3. **Harness issue map (`test-factory-claim.py:383`).** Emptied `{"T-99": 954}` to `{}`. Result:
   `5b` **reddened directly** (not via `5g`) — `(1, '', 'factory: claim: skip #951 ... skip #952 ...
   no claimable work')`, since `T-99` now unresolvable in harness's own map too. Restored; verified
   clean.
4. **Key-collapse arm neutered (`test-factory-claim-mutation.py:175`).** Changed
   `super().issue_number(canonical, ...)` to `super().issue_number(repo, ...)` — keeps the
   `_reached` marker firing (still prints `MUTANT KEY-COLLAPSE ACTIVE`) but removes the actual
   key-collapse effect. Result: mutant **REACHED** yet `5b` **NOT** red —
   `KEY-COLLAPSE MISSING: 5b`, `KEY-COLLAPSE PROOF: INCOMPLETE`, exit 1. This is the load-bearing
   proof: the arm's redness depends on the collapse itself, not merely on the mutant class being
   installed. Restored; `git status --porcelain` clean, suite back to expected two marker lines
   at exit 0.

All four perturbations were in-place edits in this assigned worktree, each restored immediately
and confirmed via `git -C <worktree> status --porcelain <path>` (empty after every restore, and
empty at final return). No scratch worktree created anywhere.

## sc_evidence (this cycle's scope)

- Operator directive item 1 (`5g` tightened) → `tests/unit/test-factory-claim.py:1319-1352`.
- Operator directive item 2 (literal `5b` failure, no mutant leak) →
  `tests/unit/test-factory-claim-mutation.py:150-201`.

## Open questions

None. The dispatch's non-goals (no code review, no fixing) are respected; nothing found here
returns to a dev.
