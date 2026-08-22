# Receipt — harness-backend-dev — T-05 — c1

## Task
Rewire `expertise-merge.py` onto `harness_merge` so there is one lock dialect across the three
write routes (T-02/T-03/T-04 precedent). Files: `.claude/skills/harness/bin/expertise-merge.py`,
`.claude/skills/harness/bin/test-expertise-merge.py`.

## TDD order — corrected mid-run
I initially wrote the production rewire before editing the test file — caught it before
returning. Reverted `expertise-merge.py` to `git show HEAD:...`, ran
`test-expertise-merge.py` (already carrying the edited assertions + case10) against the
UNMODIFIED original production code, and confirmed RED: case10 failed
(`exit 6: LOCKED ... within 10.0s`, and the proposed entry absent) exactly as the task predicted —
the original `acquire_lock`'s `O_CREAT|O_EXCL` check treats the mere PRESENCE of the flock-created
lock file as busy, so a SIGKILLed holder (through `harness_merge.acquire`, not the tool's own
lock) bricks every following apply. The three benign-second-apply replacements for cases 4/5/6
already passed against the original code — expected, since they don't change behaviour, only
what is asserted. Then reapplied the production rewire and reran: full GREEN, 38/38 checks.

## What changed
- `expertise-merge.py`: removed `acquire_lock`, `LOCK_TIMEOUT_SECONDS`/`LOCK_RETRY_INTERVAL`, the
  tempfile+`os.replace` block, and the lock-removal `finally`. Added `import harness_merge`
  (with the same `sys.path.insert` fix-up plan-merge.py/observations-merge.py use). `cmd_apply`
  now: (1) calls `require_expertise_destination` (a thin wrapper, ORIGINAL docstring verbatim,
  now delegating to `harness_merge.require_destination` with the same `EXPERTISE_TAIL` regex and
  hint lines carrying the same substantive wording) inside its own try/except that prints to
  **stderr** and exits on `MergeRefusal`; (2) parses the proposal once outside the lock; (3) calls
  `harness_merge.locked_update(resolved, transform)`, where `transform(base_bytes)` does the
  union/conflict/cap computation and returns bytes only — no `sys.exit` inside it, since
  `locked_update` wraps the write in `except BaseException` and a `sys.exit` there would report
  APPLIED after writing nothing; (4) catches `MergeRefusal` from `locked_update` (codes 6/7/8) and
  prints to **stdout**, matching the original's stream for those three codes exactly.
  `CAPS`, `SECTION_RE`, `ENTRY_RE`, `parse_expertise`, `render`, `compute_union`, `default_title`,
  `EXPERTISE_TAIL`, `UNION_APPLY`, every exit code and every printed line format are unchanged.
- `test-expertise-merge.py`: replaced the three `not os.path.exists(path + ".lock")` assertions
  (lines 203/221/237 at c32f332) with a benign second `run_apply` on the same fixture asserting
  `returncode == 0` — case4's second proposal is `P-01: one` (matches the base, no conflict),
  case5's is `P-01: text 1` (matches the base id+text, cap not re-breached), case6's is the same
  entries file it already applied. Added `case_stale_lock_recovery` (case10): forks a child that
  takes `harness_merge.acquire(lock_path)` on a fresh fixture, signals readiness over a pipe,
  blocks in `time.sleep(3600)`, gets SIGKILLed by the parent, then the parent runs the CLI's own
  `apply` and asserts both exit 0 and the proposed entry on disk. Imports `harness_merge` from
  `os.path.dirname(os.path.abspath(CLI))` (not `HERE`) so the red proof's `EXPERTISE_MERGE_BIN`
  substitution also swaps which `harness_merge.py` this test's own fork-side `acquire` call uses.

## Stream per refusal code (measured, not assumed)
- exit 6 (LOCKED) → stdout (from the `locked_update` `except` block; unconditional `print(line)`)
- exit 7 (CONFLICT) → stdout (same block)
- exit 8 (CAP EXCEEDED) → stdout (same block)
- exit 9 (destination refusal) → stderr (separate top-level try/except around
  `require_expertise_destination`, explicit `file=sys.stderr`)
Confirmed by case4/case5 (`r.stdout`) and case9 (`r.stderr`) all passing unchanged, plus case3's
`"LOCKED" in lock_stdout` passing across 20 trials.

## `verify:` result
Ran verbatim, with ONE substitution — the plan's authorised swap of the literal
`cp -R .claude/skills/harness/bin "$T/bin"` for
`python3 -c "import shutil, sys; shutil.copytree('.claude/skills/harness/bin', sys.argv[1] + '/bin')" "$T"`
(same effect, `bash-write-guard.sh` denies `cp` with an unexpanded `$T` target). No other line
changed. **Exit code: 0.** All four grep clauses passed (import found; no own
flock/O_EXCL/os.replace; no lock-file-absence assertion; `case10` present). Full 38/38 case run
is PASS. The mutant step: `USE_FLOCK = True` → `False` replaced BY NAME in the copied
`harness_merge.py`; import-and-run sanity check confirmed `harness_merge.USE_FLOCK == False` in
the mutated copy before asserting on the suite; running the Expertise suite against that mutant
via `EXPERTISE_MERGE_BIN` produced **exactly two failures and nothing else**:
```
FAIL  case10: a following apply exits 0 after the lock holder is SIGKILLed
      | exit 6: 'LOCKED: could not acquire .../.harness/expertise/harness-case10.md.lock within 10.0s\n'
FAIL  case10: the proposed entry is on disk after recovery
```
Every other case (1,2,3,4,5,6,8,9 — 36 checks) stayed PASS under the mutant, so the red proof is
specific to the stale-lock-recovery contract, not a broad breakage.

## `--check-kinds`
```
MISCONFIGURED: .claude/skills/harness/bin/test-dispatch-guard.py is not in run-unit-tests.sh's explicit script list
```
Exit 2. Pre-existing, named in the dispatch as the main session's T-07, out of this task's domain
and files. `test-expertise-merge.py` needed no registration — already in `INTEGRATION_SCRIPTS`.

## Open questions
None. `expertise_update: []`.
