# Receipt — T-01 tracked test-shape guard — harness-backend-dev

VERDICT: PASS. `suite_layout.py` now refuses every tracked test-shaped file outside `tests/`
(two pattern tuples, module-level `is_test_shaped`, `tracked_paths`, `DOCUMENTED_EXCEPTIONS`
registry with self-policing), built test-first with the eleven unit cases specified in T-01's
`intent:`. All existing clauses, message strings and ordering are untouched (additive only).
Files touched: `tests/unit/test-suite-layout.py`, `.claude/skills/harness/bin/suite_layout.py`.
Nothing committed, nothing staged, HEAD unchanged at `5eebad669e323dab3f17c81795f1fde9e11e9f50`.

## 1. RED — observed before any production edit

Added imports (`fnmatch`, `os`, `posixpath`, `code_grade`) and all eleven cases to
`tests/unit/test-suite-layout.py` first, against the **unmodified** `suite_layout.py`. Ran
`python3 tests/unit/test-suite-layout.py`:

```
... (21 pre-existing PASS lines, unchanged) ...
FAIL case 1: rogue tracked file reported exactly once as the outside-tests finding []
PASS case 1: legal manual probe file is not named by any finding
Traceback (most recent call last):
  File ".../tests/unit/test-suite-layout.py", line 185, in <module>
    saved_exceptions = suite_layout.DOCUMENTED_EXCEPTIONS
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: module 'suite_layout' has no attribute 'DOCUMENTED_EXCEPTIONS'
```
Exit code 1. Every case after case 1 depends on `is_test_shaped`, `tracked_paths` or
`DOCUMENTED_EXCEPTIONS`, none of which existed yet, so the whole file is unsatisfiable against
the current predicate: case 1's first assertion FAILs outright (the unmodified `violations()`
never scans the Git index, so `got == []`, no rogue finding), and the second sub-assertion
crashes the moment it touches the missing `DOCUMENTED_EXCEPTIONS` attribute — the exact gap
this task closes. This is genuine RED, not a vacuous pass: every new case is unreachable or
false against the unchanged predicate.

## 2. GREEN — after implementing `suite_layout.py`

Implemented `RESTRICTED_NAME_PATTERNS`, `AGNOSTIC_NAME_PATTERNS`, `SOURCE_EXTENSIONS`,
`DOCUMENTED_EXCEPTIONS` (seeded with the one FEAT-44 entry per D-05), the sole
`is_test_shaped(path)`, `tracked_paths(root)`, `_registry_findings(tracked)`, and appended the
repository-wide clause plus registry self-policing to `violations()` after the existing bin
clause, exactly as T-01's `intent:` specifies. Re-ran:

```
python3 tests/unit/test-suite-layout.py
```
→ exit 0, 46/46 PASS, 0 FAIL, including all 11 new cases and the pre-existing 21 (unchanged
message text, unchanged pass/fail semantics for every prior check).

## 3. Verify command (verbatim, matches plan.yaml T-01 `verify:` at line 495-496)

```
python3 tests/unit/test-suite-layout.py && .claude/skills/harness/bin/run-unit-tests.sh --check-layout
```
Exit code: 0. `test-suite-layout.py` printed 46 PASS / 0 FAIL (listed above);
`run-unit-tests.sh --check-layout` printed nothing (clean) and exited 0.

## 4. Full unit suite

```
env -u HARNESS_AGENT_TYPE .claude/skills/harness/bin/run-unit-tests.sh --kind unit
```
Runner's own exit code: 0. `grep -c '^PASS '` → **341**. `grep -c '^FAIL '` → **0**. Tail:
`pool: 8 workers, 27 files, 2.01s wall`. Baseline at `5eebad66` clean tree: 316 PASS / 0 FAIL /
27 files. Delta: **+25 PASS, 27 files unchanged** — exactly the 25 new `check()` calls added
across the 11 cases (3+1+2+2+1+5+2+2+1+2+4), 0 new FAIL, no file-count drift.

## 5. Case 11's six results, re-proved against the BUILT artifact

Mechanism per dispatch item 4: a throwaway probe at `/tmp/bug1286_probe/probe.py` (deleted
after use) copied the real `.harness/harness.json` to `/tmp/bug1286_probe/harness.json` and
copied `.claude/skills/harness/templates/harness.json` for the case-(i) scenario's fidelity
(both files "move together" per the plan). It imported `tests/unit/test-suite-layout.py` as a
module via `importlib.util.spec_from_file_location` + `exec_module` inside `try/except
SystemExit`, which lets the module run its own existing suite once (against the real repo,
unmodified — harmless side effect) and then exposes the already-bound module-level functions
`hygiene_uncertified(test_kinds_cfg)` and `select_control_candidate(test_kinds_cfg)` — the
exact case-11 hygiene/behavioural logic shipped in the test file, never reimplemented. Each
scenario below built its own deep-copied `test_kinds` dict derived from the COPY's JSON, never
the real file, and called those two functions directly.

- **GREEN control 1 — today's unmutated detect certifies completely.**
  Mechanism: `hygiene_uncertified(real_test_kinds)` called on the harness.json copy's
  `test_kinds` as loaded from disk, unmutated.
  Result: `uncertified == []`.

- **GREEN control 2 — the legitimate narrowing that drops `**/test_*.py` stays green.**
  Mechanism: deep-copied `test_kinds`, rewrote `unit.detect` by filtering out the
  `**/test_*.py` member, then called `hygiene_uncertified(narrowed)` and
  `select_control_candidate(narrowed)`.
  Result: `uncertified == []`; `select_control_candidate` returns
  `'.harness/tools/a.test.d/gen.py'` (the selection falls through from
  `.harness/tools/test_dir/gen.py`, confirming the positive control is config-derived, not
  copied).

- **RED (i) — `tests/../evil/**` substituted for `tests/unit/**` in both `harness.json`
  copies.** Mechanism: mutated `unit.detect` in the harness.json copy, mirrored the
  substitution into a copy of the template at `/tmp/bug1286_probe/templates_harness.json`
  (both files move together, per the plan; `hygiene_uncertified` itself only consumes the
  in-memory `test_kinds` dict, so the template copy is not read by the probe, only produced
  for fidelity to the exact scenario).
  Result: `uncertified == ['unit: tests/../evil/** (core contains a directory separator)']` —
  a `..` segment rejects it from inside-tests outright, and its core still carries `/`, so it
  is not guard-covered either.

- **RED (ii) — `**/test_*/**` added to `unit.detect` (non-final-segment wildcard).**
  Mechanism: appended the pattern via `|`-join to `unit.detect` on a deep copy.
  Result: `uncertified == ['unit: **/test_*/** (core contains a directory separator)']` — the
  literal prefix is empty (first segment `**` carries a wildcard) so it is not inside-tests,
  and its core `test_*/**` still carries `/` so it is not guard-covered.

- **RED (iii) — `**/*.spec.*` added to `unit.detect`.**
  Mechanism: same append technique.
  Result: `uncertified == ['unit: **/*.spec.* (no fixed literal key (_test., .test., or a
  restricted prefix plus a source extension))']`. The built implementation's `certify_pattern`
  short-circuits at condition (c) — core `*.spec.*` carries neither the agnostic literal key
  (`_test.` / `.test.`) nor a restricted prefix, so it is rejected before the corpus oracle (d)
  is even consulted. The plan's narrative attributes this escape to (d) matching
  `x.spec.y`/`x.spec.tsx`/`x.e2e.spec.ts`; this is a discrepancy between the plan's illustrative
  mechanism text and the actual (equally sufficient, strictly earlier) closure this
  implementation takes — recorded honestly rather than reshaped to match the narrative. The
  observable contract holds either way: the pattern is uncertified and the case fails naming it.

- **RED (iv) — `**/test_*.p?` added to `unit.detect` (the extension-position escape).**
  Mechanism: same append technique.
  Result: `uncertified == ['unit: **/test_*.p? (no fixed literal key (_test., .test., or a
  restricted prefix plus a source extension))']` — core `test_*.p?` clears (a) and (b), starts
  with `test_`, but the region after its last wildcard (`?`) is empty, so no fixed source
  extension is present and the RESTRICTED key is absent; this matches the plan's stated
  mechanism for (iv) exactly (it also independently fails the corpus oracle (d): matches
  basename `test_x.pw`, which `is_test_shaped` rejects).

After the probe run: `git -C <worktree> status --porcelain -- .harness/harness.json
.claude/skills/harness/templates/harness.json` printed nothing (neither file touched). The
probe directory `/tmp/bug1286_probe` was deleted afterward.

## Exactly two files changed

```
$ git -C <worktree> status --porcelain
 M .claude/skills/harness/bin/suite_layout.py
 M .harness/harness/features/BUG-1286-test-tree-enforcement/STATE.md
 M .harness/harness/features/BUG-1286-test-tree-enforcement/feature.json
 M .harness/harness/features/BUG-1286-test-tree-enforcement/plan.yaml
 M tests/unit/test-suite-layout.py
```
Only the two files named in T-01's `files:` were touched by this dispatch
(`suite_layout.py`, `tests/unit/test-suite-layout.py`). The three feature-tracking files
(`STATE.md`, `feature.json`, `plan.yaml`) are concurrent sibling/orchestrator checkpointing
activity (the `EngBuildT01T03` lead is running concurrently per the roster) — not edited by
this task and unrelated to T-01's scope. Nothing staged; HEAD unchanged at `5eebad66`.

## Notes on a mid-task tooling hazard (not a finding for this feature's record)

Early in this dispatch, an `edit` call using an absolute worktree-prefixed path string as the
bracket-header path landed correctly, but a *subsequent* call using a bare relative path
(`tests/unit/test-suite-layout.py` with no worktree prefix) resolved against the **main
checkout** (`/Users/molchairuangutai/GitHub/harness`) instead of the worktree, silently editing
the wrong file. Caught via `wc -l` / `git status --porcelain` cross-checks in both locations
before any test ran; the accidental 4-line change to the main checkout's
`tests/unit/test-suite-layout.py` was reverted with `git checkout --` (uncommitted, unstaged,
safe — my own mistake) before continuing, entirely with the worktree-prefixed absolute path for
every subsequent read/edit/bash call. Confirmed clean via `git status --porcelain` in the main
checkout (no diff) throughout the remainder of this session.
