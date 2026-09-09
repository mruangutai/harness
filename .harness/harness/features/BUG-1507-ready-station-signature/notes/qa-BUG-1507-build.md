# QA gate — BUG-1507-ready-station-signature — build diff `4b5dbb23..64bc9351`

**VERDICT: PASS.** Every matrix-required kind for every task resolves to a test that exists and passes, quoted verbatim below.

## 1. Matrix derivation (harness.json `bugfix`/`docs` rows, quoted)

```
"bugfix": { "always": [], "when": [
    { "kind": "unit",           "if": "touches_runtime_code" },
    { "kind": "integration",    "if": "fix_confined_to_tests_and_contract_docs" },
    { "kind": "__bug_class__",  "if": "match_bug_class" } ] },
"docs": { "always": [] }
```

- **T-01** (`.claude/commands/harness-plan.md`, bugfix): `touches_runtime_code` = **false** — a markdown instruction file, no runtime code. `fix_confined_to_tests_and_contract_docs` = **true** — the entire diff is two token edits inside a contract instruction doc, nothing else touched. `match_bug_class` = **false/unresolvable** — the repository's own Expertise (G-08) records this predicate as a currently-unresolvable placeholder: no bug-class taxonomy entry fires for any diff yet, confirmed unchanged on this branch. → **required: integration only.**
- **T-02** (`.claude/skills/harness/references/github-mirror.md`, bugfix): identical reasoning — a reference doc, `touches_runtime_code` false, `fix_confined_to_tests_and_contract_docs` true, `match_bug_class` unresolvable. → **required: integration only.**
- **T-05** (`tests/integration/test-station-argument-spelling.py`, bugfix, new file): `touches_runtime_code` = **false** — the file itself is a test, not runtime code. `fix_confined_to_tests_and_contract_docs` = **true** — trivially confined to tests. `match_bug_class` unresolvable as above. → **required: integration only**, and this task's own file *is* the discharging test.
- **T-03** (`.claude/skills/harness/SKILL.md`, docs) and **T-04** (`.claude/skills/harness/bin/gh-sync.py`, docs, docstring-only, 16 insertions/0 deletions): `docs.always` = `[]` and there is **no `when` list** for `docs` in harness.json — the required set is **explicitly empty**, stated rather than left implicit. `gh-sync.py` is real runtime code, but T-04 is typed `docs` per the operator's signed ruling (plan.yaml D-02/`_matrix_provenance` scope), and the matrix keys off the task's own signed `change_type`, not the file's general nature — no kind is obligated.

`matrix_ok: true` — no task drops below its floor.

## 2. Kind resolution — the discharging test

Candidate/only evidence: `tests/integration/test-station-argument-spelling.py`.

Cross-checked the plan's T-05 `verify:` string against `plan.yaml` lines 321-323 **before** running — exact match, no BLOCKED.

```
$ python3 tests/integration/test-station-argument-spelling.py
PASS - the instruction scope is non-empty
PASS - at least the measured number of station-argument occurrences are found
PASS - harness-plan.md is among the swept occurrence files
PASS - github-mirror.md is among the swept occurrence files
PASS - SKILL.md is among the swept occurrence files
PASS - every station argument in the instruction scope is an accepted station
PASS - the unmutated scratch copy reports no offender
PASS - the sweep reddens on a reintroduced capital
EXIT:0
```

Full T-05 verify block, run verbatim:
```
$ python3 tests/integration/test-station-argument-spelling.py && \
  python3 tests/integration/test-station-argument-spelling.py | grep -q '^PASS - every station argument in the instruction scope is an accepted station$' && \
  python3 tests/integration/test-station-argument-spelling.py | grep -q '^PASS - the sweep reddens on a reintroduced capital$'
VERIFY_EXIT:0
```
(A `BrokenPipeError` traceback appears on stderr on the piped legs — `grep -q` closes stdin the instant it matches, against a `print`-heavy producer; it does not change `$?` of the `&&` chain, confirmed `0`.)

Configured kind command — the gate the floor actually rests on, run directly:
```
$ .agents/skills/harness/bin/run-unit-tests.sh --kind integration
...
----- test-station-argument-spelling.py (exit 0, 0.08s) -----
PASS test-station-argument-spelling.py
...
pool: 8 workers, 50 files, 70.36s wall
EXIT:0
```
3767 `ok`/`PASS` lines, **0** `not ok`/`FAIL` lines across the whole integration bucket. T-01, T-02 and T-05 all resolve to **satisfied**, discharged by this one file (it is the test added in this very diff — P-05).

## 3. SC-09 regression guard

```
$ python3 tests/integration/test-gh-sync.py
... ALL PASSED ... (0 not-ok lines)
GHSYNC_EXIT:0

$ python3 tests/integration/test-board-station.py
... all pass ...
BOARDSTATION_EXIT:0
```
Both green — SC-09 **satisfied**.

## 4. SC-02 — sweep derived, not spelled, at least the measured floor

Read the witness body directly (not just PASS labels, per P-07/P-01):
- `ACCEPTED_STATIONS` is derived from `factory_config.MANDATED_STATIONS`/`TERMINAL_MARKER`, never a hand-spelled list (lines 44-47).
- `occurrences()`/`offenders()` operate over `scope_files(root)` = `.claude/commands/*.md` ∪ `.claude/skills/**/*.md`.
- Instrumented the sweep directly (label-only PASS output never prints the count on success — `check()` only prints `detail` on failure):
```
$ python3 -c "...import test-station-argument-spelling as m; occ=m.occurrences(m.REPO_ROOT); print(len(occ), m.MIN_OCCURRENCES)"
found 6  MIN_OCCURRENCES 6
```
All 6 real occurrences enumerated: 2 in `harness-plan.md`, 1 in `SKILL.md`, 3 in `github-mirror.md` — every `EXPECTED_FILES` entry present, `offenders(REPO_ROOT) == []`. The floor (6) exactly equals what plan D-05/T-05 intent states was measured at `4b5dbb23`; the sweep is not vacuous over an empty scope (`len(scope_files) > 0` asserted as its own row).
**SC-02 verdict: PASS.** Method: direct instrumented run + read of the label-only case row. Evidence: `tests/integration/test-station-argument-spelling.py:90-104` (`case_every_argument_is_accepted`), exit 0 above.

## 5. SC-03 — the sweep CAN go red

Read `case_reddens_on_a_reintroduced_capital` (lines 107-138):
- **(a)** it copies two real files into a `tempfile.TemporaryDirectory()`, asserts the unmutated copy is clean **first**, as its own row `"the unmutated scratch copy reports no offender"` (line 121-123) — the anti-false-red control is present and runs before the mutation, confirmed in the PASS output above.
- **(b)** the mutation does `before.replace("status <feature-dir> ready", "status <feature-dir> Ready")` and **asserts the text actually changed** (`assert before != after`, line 129) before writing — not a no-op.
- The reddened-row assertion (line 134-138) requires `offenders(tmp)` non-empty **and** one tuple to name exactly `(plan_copy, "gh-sync.py status", "Ready")` — attributing the red to the specific reintroduced token, not to any other scratch-root difference.
**SC-03 verdict: PASS.** Method: read + the case's own PASS row (`"the unmutated scratch copy reports no offender"`, `"the sweep reddens on a reintroduced capital"`), both green above. Evidence: `tests/integration/test-station-argument-spelling.py:107-138`.

**Falsification probe (scope-repoint):** grepped the witness file for `os.environ`/`os.getenv` — zero hits. `offenders(root)` → `occurrences(root)` → `scope_files(root)` is a plain parameter chain end to end; no module-level scope variable, no env override exists that could silently repoint the positive sweep. Confirmed by direct read, not inference.

## 6. Test-first compliance (step 4)

- **Dependency order is signed and honoured.** `plan.yaml` T-05 carries `depends_on: [T-01, T-02]` (line 316) — T-05's positive controls assert the FIXED (lowercase) state, so writing it before T-01/T-02 landed would have been vacuous by construction. Git log confirms landing order: `e5223f10` (T-01) → `d9caec31` (T-02) → `3063b1dc` (T-03) → `64bc9351` (T-04+T-05 together). This is the plan's own signed dependency order, not a violation.
- **Pre-build RED is recorded**, at `.harness/harness/features/BUG-1507-ready-station-signature/notes/handoff-plan.md:19-21`: *"Every one of the five `verify:` commands is RED on the unfixed tree (T-01..T-04 exit 1, T-05 exit 2, file absent) — orchestrator ran all five from the worktree root, verified-at 4b5dbb23."* This is the orchestrator's own pre-build measurement, reachable and cited here — not invented.
- **T-05's own receipt** (`notes/receipt-harness-backend-dev-t04-t05-eng.md:102-123`) independently reproduces this for the sweep specifically: staged the two pre-fix files from `4b5dbb23` into a scratch root in-process and printed `offenders()`, finding **5 offending occurrences** across the two files — none present in the current tree. Two independent pieces of RED evidence for the same class, not one.
**Grade: compliant.** No violation to report; both halves (signed dependency order, pre-build RED) are established from artifacts, not inferred.

## Files touched by this gate

None under grade. Only this note.
