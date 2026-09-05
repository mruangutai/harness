## BLUF

Both remedies closed. `code-grade.py` now exits 0 for `suite_layout.py` (graded via
`git stash create` object `a6faf32d`, which `git show --stat` confirms carries both edited
files); the two remaining `RESULT: FAIL` records (`tracked_paths`, `_literal_key_present`) are
pre-existing grade-2 reasoned records at HEAD `b86498a0`, out of scope, unchanged. SC-16's
single-caller property is now pinned repository-wide and proven to redden on a real mutation.
HEAD is still `b86498a0`; nothing staged or committed.

## B-1: decomposition

`violations` split into `_unit_integration_findings`, `_runner_selection_findings`,
`_bin_planted` / `_bin_planted_findings`, `_tracked_outside_tests_findings` (further split
into `_is_untracked_exclusion` after first cut left it grade 3/cognitive 10) and `_tracked_scan`,
in that call order — matching the reviewer's five responsibilities exactly. `_registry_findings`
split into `_duplicate_or_malformed`, `_unnecessary_or_stale`, `_entry_finding` (per-entry, called
once per loop iteration; `seen.add` happens only after the first two rules pass, exactly as
the original single loop did).

| qualname | cyclomatic | cognitive | ABC | grade | bar |
|---|---|---|---|---|---|
| violations (unchanged signature, now 15-line body) | — | — | — | — | — |
| _unit_integration_findings | 6 | 3 | 9.8 | 4 | 4 PASS |
| _runner_selection_findings | 6 | 6 | 8.8 | 4 | 4 PASS |
| _bin_planted | 2 | 1 | 4.6 | 5 | 4 PASS |
| _bin_planted_findings | 2 | 0 | 1.0 | 5 | 4 PASS |
| _is_untracked_exclusion | 3 | 1 | 4.1 | 5 | 4 PASS |
| _tracked_outside_tests_findings | 6 | 1 | 7.7 | 4 | 4 PASS |
| _tracked_scan | 4 | 3 | 6.7 | 5 | 4 PASS |
| _duplicate_or_malformed | 4 | 2 | 4.2 | 5 | 4 PASS |
| _unnecessary_or_stale | 5 | 6 | 7.3 | 4 | 4 PASS |
| _entry_finding | 2 | 1 | 3.7 | 5 | 4 PASS |
| _registry_findings | 3 | 3 | 7.1 | 5 | 4 PASS |

(`violations()` itself is now a straight-line dispatcher: no branches beyond the tuple unpack,
graded well inside bar 4 — the grader doesn't print a standalone record for it because its body
is entirely calls/extends, confirmed by its absence from any `RESULT: FAIL`.)

Graded input: `git stash create` → `a6faf32d6899810bcce4114fbdad84fcd0dbaddc` (a dangling commit;
HEAD/index/worktree untouched). `git show --stat a6faf32d` lists both
`.claude/skills/harness/bin/suite_layout.py` and `tests/unit/test-suite-layout.py` as changed,
confirming the graded object includes this run's edits.
`python3 .claude/skills/harness/bin/code-grade.py --base "$(git merge-base origin/main HEAD)" --head a6faf32d`
→ exit 0, `PASSING: 33`. Two `RESULT: FAIL` records remain, both pre-existing at HEAD `b86498a0`
(confirmed by grading HEAD directly before any edit): `tracked_paths` (grade 2, ABC, untouched —
non-goal) and `_literal_key_present` in `tests/unit/test-suite-layout.py` (grade 2, cyclomatic,
pre-existing case-11 code — non-goal, backlog per dispatch).

## Behaviour preservation — how checked

- **Finding strings byte-identical**: extracted the sorted set of string/f-string literals from
  `git show HEAD:.../suite_layout.py` and from the edited file; diffed. Every line in the diff is
  an addition (new helper docstrings only) — zero removed or altered lines, so every pre-existing
  finding message (all 4 registry messages, the enumeration-failure message, all pre-existing
  clause messages) is untouched.
- **Output order**: preserved by construction — `violations()` calls the five helpers in the same
  sequence the original single function executed its five blocks, each `out.extend(...)`-ing in
  turn, then `_registry_findings(tracked)` last.
- **D-03 ordering**: `_tracked_scan` calls `tracked_paths(root)` (unmodified, untouched) before
  testing self-ownership (`".../suite_layout.py" in tracked`) — the toplevel precondition inside
  `tracked_paths` always resolves first, exactly as before, because it's still the same function
  call, just relocated into a helper rather than inlined.
- **Case 4 (broken `.git`) contract**: `_tracked_scan` returns `([finding], None)` on `LookupError`;
  `_registry_findings(None)` receives `None` and only its last rule (`tracked is not None and ...`)
  short-circuits — verified by the case 4 assertion passing (see suite results below).
- **Case: self-ownership false, tracked non-None**: `_tracked_scan` returns `([], tracked)` — the
  real tuple, not `None` — so `_registry_findings` still sees the real tracked set, matching the
  original's post-loop behaviour (case 9's assertion passes).
- Read the rewritten `violations()`/`_registry_findings()` end to end against the original;
  confirmed no reordering, no removed continue/branch, no changed default/mutable-argument capture
  (`DOCUMENTED_EXCEPTIONS` still read at call time inside `_duplicate_or_malformed`/
  `_unnecessary_or_stale`, never captured as a default).

## B-3: single-caller assertion

Added `_is_violations_invocation` (argument-present regex, excludes zero-arg
`suite_layout.violations()` docstring mentions) and `_violations_callers` (git-tracked,
source-extension-filtered via `suite_layout.SOURCE_EXTENSIONS`, `tests/`-excluded, comment-lines
skipped), then one `check(...)` asserting the resulting set equals
`{".claude/skills/harness/bin/run-unit-tests.sh"}`, passing the observed set as detail. Existing
`"runner delegates layout once"` check left untouched (purely additive, inserted after it).

**Scoping decisions** (all as required):
- Executable surfaces only: candidates come from `git ls-files` filtered to
  `suite_layout.SOURCE_EXTENSIONS` (`.py .sh .ts .tsx .js .mjs .cjs`) — `BRIEF.md`, `plan.yaml` and
  every `notes/*.md` file that mentions `violations()` in prose have no matching extension and
  can't be candidates at all.
- Prose inside code excluded via an argument-presence regex
  (`suite_layout\.violations\(\s*[^)\s]`): `layout_fixtures.py:12`'s docstring reads
  `suite_layout.violations()` (empty parens) and fails this regex, so it is never counted.
  Comment lines (stripped line starting `#`) are skipped outright regardless of content.
- `tests/` excluded by path prefix, stated explicitly here as the scoping decision: the assertion
  therefore pins **non-test** callers only. `tests/unit/test-suite-layout.py`,
  `tests/integration/test-run-unit-tests-layout.py` and `tests/manual/suite-census.py` are free to
  keep invoking `violations()` for their own exercises.
- `check-instruction-paths.py`'s own module-level `violations()` is never matched: the regex
  requires the qualified `suite_layout.violations(` spelling, which that file's own function
  definition/calls never use.
- Assertion equates the observed **set** to the single-element set naming
  `.claude/skills/harness/bin/run-unit-tests.sh` (not a bare length check), and passes
  `repr(_violations_callers(...))` as the `check(...)` detail.

**RED proof (mutation probe)**:
- Probe file: `.claude/skills/harness/bin/board-station.py` (unrelated script, not
  `run-unit-tests.sh`).
- sha256 before: `80042071e34bc51ab4fabfb0f163b66780b73c476c0dc7aeafdaec38a6297043`
- Appended a genuine invocation (`suite_layout.violations("/tmp/probe-root")`, an argument
  present) via the Edit tool, ran `tests/unit/test-suite-layout.py`:
  ```
  FAIL violations() has exactly one non-test caller repository-wide ['.claude/skills/harness/bin/board-station.py', '.claude/skills/harness/bin/run-unit-tests.sh']
  ```
  Exit 1.
- Restored the file (removed the appended lines via Edit tool). sha256 after:
  `80042071e34bc51ab4fabfb0f163b66780b73c476c0dc7aeafdaec38a6297043` — matches before,
  byte-for-byte. `git status --porcelain` for the probe file: empty (not listed).

## Verification (all run from the worktree root)

1. `python3 tests/unit/test-suite-layout.py` — exit 0, 47 checks, 0 FAIL (baseline 46 + 1 new).
2. `.claude/skills/harness/bin/run-unit-tests.sh --kind unit` — exit 0, 342 PASS, 0 FAIL, 27 files
   (baseline 341 + 1 new).
3. `python3 tests/integration/test-run-unit-tests-layout.py` — exit 0, 14 PASS, 0 FAIL (unchanged).
4. `.claude/skills/harness/bin/run-unit-tests.sh --check-layout` — exit 0.
5. `python3 tests/manual/suite-census.py tree-audit --ref HEAD` — `TOTAL 85 OUTSIDE 9 VIOLATIONS 0`
   (unchanged).
6. `python3 .claude/skills/harness/bin/code-grade.py --base "$(git merge-base origin/main HEAD)" --head "$(git stash create)"`
   — exit 0, `PASSING: 33`. No `RESULT: FAIL` for `suite_layout.py`.

All commands run with `env -u HARNESS_AGENT_TYPE`, each read as its own `$?`.

## Scope and state

Exactly two source files changed plus this receipt:
- `.claude/skills/harness/bin/suite_layout.py`
- `tests/unit/test-suite-layout.py`

`git -C <worktree> status --porcelain`:
```
 M .claude/skills/harness/bin/suite_layout.py
 M .harness/harness/features/BUG-1286-test-tree-enforcement/feature.json
 M .harness/harness/features/BUG-1286-test-tree-enforcement/notes/qa-tree-audit.md
 M tests/unit/test-suite-layout.py
?? .harness/harness/features/BUG-1286-test-tree-enforcement/notes/answers-2026-09-05-budget-c11.md
?? .harness/harness/features/BUG-1286-test-tree-enforcement/notes/qa-audit-sha-correction.md
?? .harness/harness/features/BUG-1286-test-tree-enforcement/observations/harness-qa.md
```
The `feature.json`/`qa-tree-audit.md`/untracked `notes` and `observations` entries are the
concurrent B-2 (`ShipBug1286.FixB2`) run's own files — not touched by this run, reported per
O-06.

`git rev-parse HEAD` = `b86498a066019ea57b7b50290324756f15de7921` (unchanged). Nothing staged,
nothing committed. `tracked_paths` and `_registry_findings`'s named non-goal
(`tracked_paths`) were not touched.
