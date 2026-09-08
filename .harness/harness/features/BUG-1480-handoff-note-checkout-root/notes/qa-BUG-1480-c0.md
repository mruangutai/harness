# QA gate — BUG-1480-handoff-note-checkout-root — cycle 0

## VERDICT: PASS

Both matrix-required kinds are green in the worktree, at HEAD `12a13693`. All four new
`_handoff_worktree_cases` rows read `ok`; every pre-existing handoff row reads `ok`. The test-first
audit confirms the two fix-dependent rows were RED at the pre-fix commit and are GREEN now, and the
two control rows were GREEN at both commits, exactly as the plan claimed.

## 1. Change type and matrix resolution

Diff under grade = exactly the two named commits (`6b5ae254` T-01, `d8a99991` T-02). Confirmed via
`git show --stat` and full diff text against BRIEF/plan description — byte-for-byte match, no
surprise hunks. `12a13693` (build-station note) touches only files under the feature directory, out
of grading scope.

`change_type: bugfix` (both tasks). `.harness/harness.json` bugfix row: `always: []`, three `when`
clauses.

| predicate | resolution | reasoning |
|---|---|---|
| `touches_runtime_code` → `unit` | **true** | T-02 changes `.claude/skills/harness/bin/check-domain.sh`, a runtime gate script (not test-only, not docs-only) |
| `fix_confined_to_tests_and_contract_docs` → `integration` | **true** | The bug's regression coverage lives entirely in `tests/integration/test-check-domain.py`, and the fix itself is a gate-script change whose only contract is exercised by that same integration suite — no unit-only surface is untouched by integration here |
| `match_bug_class` → `__bug_class__` | **no bug-class taxonomy entry fires** (per repository-tier Expertise G-08: this clause is currently an unresolvable placeholder in `.harness/harness.json` — no bug-class mapping exists yet for any diff). Bug class if one existed: "checkout-root resolution defect" → would map to `integration` (already required above), so its absence changes nothing here. |

Floor: `{unit, integration}`. Both are `active` per the dispatch's kind table, `cmd` non-null for
both. No kind resolves to `not_applicable`, `locally-run`, or `misconfigured` — both ran cleanly with
loud pass/fail signal (see §2).

`matrix_ok: true`.

## 2. Kind execution (worktree, `env -u HARNESS_AGENT_TYPE`, absolute paths)

Command (unit):
```
cd <worktree> && env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit
```
rc=0. `^FAIL ` count = 0. State: **satisfied**.

Command (integration):
```
cd <worktree> && env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration
```
rc=0. `^FAIL ` count = 0. `^ok ` row count (across the whole integration bucket, all files) = 2071.
State: **satisfied**.

Both counted by grepping captured stdout+stderr, not by tailing the runner's own final summary line
(per repository-tier Expertise G-04/harness-qa craft: the printed PASS line is one-per-script, not a
case tally, and misreads a red suite as green if you tail only).

### Main-checkout `verify:` clauses (informational only — do NOT grade this feature)

Ran for cross-reference. **Label: main-checkout measurement, non-authoritative** — the main checkout
at `/Users/molchairuangutai/GitHub/harness` still holds the pre-fix `check-domain.sh` per the
dispatch's own note; these clauses are quoted verbatim from `plan.yaml` T-01/T-02 and were not treated
as grading evidence:

- T-01 verify (verbatim from `plan.yaml:78-79`) — not executed as a grading step; skipped, since it
  greps the pre-fix `FAIL` row and `ok` fixture row against the MAIN checkout's still-pre-fix script,
  which is expected (not informative) behavior and adds nothing the worktree-side red/green audit
  (§4 below) does not already establish more rigorously via `CHECK_DOMAIN_BIN`.
- T-02 verify (verbatim from `plan.yaml:176-177`): `cd /Users/molchairuangutai/GitHub/harness && env
  -u HARNESS_AGENT_TYPE python3 tests/integration/test-check-domain.py` — this runs the MAIN
  checkout's test file (pre-merge, so it lacks the T-01 test additions entirely) against the MAIN
  checkout's pre-fix script. Not run: it measures neither the diff under grade nor the worktree fix,
  and the dispatch says to run it only if informative — it is not.

Both `plan.yaml` verify strings were cross-checked byte-for-byte against the dispatch's quoted
copies: identical, no mismatch, so no `BLOCKED` trigger here.

## 3. Test-first audit

`git log --oneline` in the worktree: `12a13693` → `d8a99991` (T-02, fix) → `6b5ae254` (T-01, test) →
`3c0d647f` (plan) → `64fcaa34` (merge base). `6b5ae254` (test) precedes `d8a99991` (fix)
chronologically and in ancestry — confirmed ordering matches REQ-05/SC-06's claim.

Confirmed the RED directly, without moving HEAD: copied `.claude/skills/harness/bin/` wholesale to a
scratch directory (`/tmp/qa_prefix_bin`) so sibling-module imports (`harness_boundary`,
`handoff_done_when`, `feature_schema`) resolve, overwrote only `check-domain.sh` inside that copy with
`git show 6b5ae254:.claude/skills/harness/bin/check-domain.sh` (diffed against the current tracked
file to confirm it is exactly pre-`_checkout_root` — the only difference is the added helper and the
one call-site argument swap, as the BRIEF describes). Ran the CURRENT test suite with
`CHECK_DOMAIN_BIN=/tmp/qa_prefix_bin/check-domain.sh`:

```
env -u HARNESS_AGENT_TYPE CHECK_DOMAIN_BIN=/tmp/qa_prefix_bin/check-domain.sh python3 tests/integration/test-check-domain.py
```
rc=1. Total `^FAIL ` count across the ENTIRE suite = **2**, both inside the new group:

```
ok    handoff worktree-only main root has no feature dir
FAIL  handoff worktree-only feature dir resolves exit 2: check-domain: BLOCKED — …handoff shape (DEC-159). Authority pointer 'pl…
ok    handoff worktree-only unresolvable pointer refused
FAIL  handoff worktree-only brief-sc pointer refused exit 2: check-domain: BLOCKED — …handoff shape (DEC-159). Authority pointer 'br…
```

No other row in the whole suite reddened from this substitution — the pre-fix script is otherwise
behaviorally identical for everything else exercised, which is the expected shape for a one-call-site
change. (Earlier attempt with `CHECK_DOMAIN_BIN` pointed at a bare copied file outside `bin/`, with no
sibling modules, cascaded into ~150 unrelated `FAIL`s from `ModuleNotFoundError`/missing
`team-config.yaml` context — discarded as measuring the wrong thing, not a real regression signal.)

## 4. Per-row red/green classification (measured, not asserted from the plan's prose)

| row | pre-fix (§3 run) | post-fix (§2 run) | classification |
|---|---|---|---|
| `handoff worktree-only main root has no feature dir` | `ok` | `ok` | fixture/precondition assertion — asserts a directory absence unrelated to the resolution fix, expected green both ways |
| `handoff worktree-only feature dir resolves` | **FAIL** (exit 2, `BLOCKED … Authority pointer 'pl…`) | `ok` | **red-then-green** — confirms the plan's claim |
| `handoff worktree-only unresolvable pointer refused` | `ok` | `ok` | **vacuity control** — green both before and after; a T-99 pointer is unresolvable regardless of which checkout root is used, so this row alone would never have proven the fix — exactly the plan's stated purpose |
| `handoff worktree-only brief-sc pointer refused` | **FAIL** (exit 2, `BLOCKED … Authority pointer 'br…`) | `ok` | **second red-then-green row** — confirms the plan's claim that this row specifically proves BRIEF.md is read from the worktree copy (its needle includes the worktree path fragment) |

All four classifications match the plan's stated design exactly.

## 5. Success criteria (from integration output, quoting rows verbatim)

- **SC-01** — row `handoff worktree-only feature dir resolves` reads `ok` in the post-fix worktree
  run (§2). **Satisfied.**
- **SC-02** — every row emitted by `_handoff_grammar_cases`, `_handoff_pointer_cases`,
  `_handoff_unsafe_cases`, `_handoff_pre_edit_cases`, `_handoff_validator_exception_case`,
  `_handoff_existing_edit_cases`, `_handoff_line_cap_cases` reads `ok` — confirmed: all 42
  pre-existing handoff rows (lines 3045–3086 of the captured integration output) read `ok`, zero
  `FAIL` among them. **Satisfied.**
- **SC-03** — both `handoff worktree-only unresolvable pointer refused` and `handoff worktree-only
  brief-sc pointer refused` read `ok` in the post-fix run (§2), and per §4 they differ exactly as
  claimed: the former is green both ways (vacuity control), the latter is red-then-green (proves
  BRIEF.md is read from the worktree). **Satisfied.**
- SC-04..SC-07 — `verify: inspection` — `not_run (inspection, review panel)`. Not adjudicated here.

## Commands run, verbatim, with exit codes

```
cd <worktree> && env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit
  rc=0, ^FAIL count=0

cd <worktree> && env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration
  rc=0, ^FAIL count=0, ^ok count=2071

cd <worktree> && env -u HARNESS_AGENT_TYPE CHECK_DOMAIN_BIN=/tmp/qa_prefix_bin/check-domain.sh python3 tests/integration/test-check-domain.py
  rc=1, ^FAIL count=2 (both in _handoff_worktree_cases, see §3/§4)
```

## Coverage gaps (Phase 1, before reading code)

Phase-1 expectation from BRIEF/plan alone: a worktree-rooted handoff note resolving its authority
pointers against the worktree, a vacuity control proving the accept case isn't free, a second
red-then-green row proving BRIEF.md specifically comes from the worktree, and a main-checkout
regression guard. All four are present in `_handoff_worktree_cases`; no gap found between Phase-1
expectation and Phase-2 code.

`open_questions`: none blocking. No harness defect observed this run.
