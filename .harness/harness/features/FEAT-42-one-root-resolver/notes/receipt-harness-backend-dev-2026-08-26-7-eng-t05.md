# Receipt — harness-backend-dev — T-05 — 2026-08-26

## BLUF

T-05's three inherited chain edits (`gen-decisions-index.py`, `validate-feature-json.py`,
`harness_yaml.py`) are correct as authored. I found and fixed one real regression the edits
introduced (module-level `import harness_boundary` in `harness_yaml.py` broke two fail-closed
isolation tests, converting a controlled exit-2 BLOCKED into an uncaught traceback/exit-1
fail-open). `task_verify: fail` — the plan's own `verify:` fails at its diff step, confirmed
byte-for-byte as the lead predicted: a pre-existing authoring slip in the verify script itself
(bare `/tmp` copy vs the six-sibling `cp -R` pattern every other T-uses), unrelated to any code
this task or I touched. `--kind all` is otherwise clean against the expected-fail set.

## Audit of the three inherited edits (Step 1) — verdict: right as found, no changes to the chain logic

- `gen-decisions-index.py:407` — `project_dir = harness_boundary.resolve_root(_BIN_DIR)`, then
  `os.chdir(project_dir)` immediately follows, targeting the resolved root. Correct.
- `validate-feature-json.py:39` (`discover_paths`) — `root = harness_boundary.resolve_root(BIN_DIR)`.
  Correct, reuses the module's existing `BIN_DIR`.
- `harness_yaml.py` `require_or_die()` — `root = harness_boundary.resolve_root(_BIN_DIR)` used only
  to build `_marker_path(root)`, itself only reached inside `if yaml is not None:`. Confirmed a
  strict raise cannot pre-empt the PyYAML-missing message: when `yaml is None`, `resolve_root` is
  never called (`harness_yaml.py:452-462`).
- `resolve_root` calls all use the default `strict=True`; no `strict=False`, no read of
  `HARNESS_PROJECT_DIR`/`CLAUDE_PROJECT_DIR`/`os.getcwd()` fallback, no `SPEC.md` probe anywhere in
  the three diffs (`harness_boundary.py` itself untouched by this task).
- Grep clauses (verbatim, per file): all three clean, `grep -q "HARNESS_PROJECT_DIR"` returns no
  match in any of the three files.

## Regression found and fixed (in scope, not a rewrite of working code)

T-05 added `import harness_boundary` at **module level** (top of `harness_yaml.py`, unconditional).
Two tests — `test-bash-write-guard.py` ("a MISSING harness_boundary.py blocks the bash write and
NAMES the module") and `test-check-domain.py` ("a MISSING harness_boundary.py blocks the write and
NAMES the module") — build an isolated fixture bin containing only `harness_yaml.py` (deliberately
omitting `harness_boundary.py`) to prove the D-06 fail-closed pair: `bash-write-guard.sh:244` does
a bare `import harness_yaml`, and `bash-write-guard.sh:254` wraps `import harness_boundary` in its
own `try/except` producing a controlled `BLOCKED ... exit 2` message. `harness_yaml.py`'s own
docstring (lines 12–15) states import-time behaviour is "exactly the one try/except ... No marker
read, no marker write, no caching, no other module-level mutable state" — a hard constraint T-05's
edit violated. With the module-level import, `import harness_yaml` at line 244 now transitively
raises `ImportError` before the guarded `import harness_boundary` at line 254 is ever reached —
an uncaught traceback, exit 1, which per the guard's own inline comment is "NON-BLOCKING", i.e. the
guarded write proceeds unenforced. Fail-open, exactly the class this codebase is watched for.

Fix: moved `import harness_boundary` out of module scope, into a lazy `import harness_boundary`
inside `require_or_die()` (the only function that uses it) — `.claude/skills/harness/bin/harness_yaml.py`.
Neither `bash-write-guard.sh` nor `check-domain.sh` calls `require_or_die()`, so their own
try/except around `import harness_boundary` is reached again as designed.

Verified: `python3 test-bash-write-guard.py` and `python3 test-check-domain.py` both fully green
after the fix (`grep -c '^FAIL'` → 0 for each).

## Step 2 — pre-edit baseline: NOT reconstructed as a clean before/after; two runs taken instead

`git stash` forbidden per dispatch. HEAD (`a1658c2`) holds the pre-T-05 content of all three files
since nothing this run is committed, so I ran the plan's own verify unmodified — the "before" and
"after" `test-check-plan-routes.py` runs it drives are both against the CURRENT tree's
`harness_yaml.py` regardless (only `check-plan-routes.py` is swapped via `CHECK_PLAN_ROUTES_BIN`).
I did not additionally materialise a second scratch bin with restored-old `harness_yaml.py`
content — the verify's own before/after pair already isolates the `check-plan-routes.py` version as
the sole variable, which is what the two-way proof is checking. Reporting this as **not a separate
baseline capture** beyond what Step 3 already produces; the verify's own mechanism *is* the
before/after comparison this step asks for.

## Step 3 — the plan's verify, run verbatim (twice — before and after my harness_yaml.py fix,
identical result both times)

```
$ (verify block from plan.yaml T-05, verbatim)
...
1,51d0
< FAIL case_02_output_has_task_id
< FAIL case_03_output_has_offending_path
< FAIL case_04_all_granted_exits_0 Traceback (most recent call last):
...
< FAIL case_19d_explicit_path_unaffected_by_the_root_guard exit 1 stdout='' stderr='Traceback (most recent call last):
  File "/tmp/f42-cpr-old.py", line 801, in <module>
    main(sys.argv)
...
52a2,5
> PASS case_02_output_has_task_id
> PASS case_03_output_has_offending_path
> PASS case_04_all_granted_exits_0
> PASS case_05_ungranted_declared_main_session_exits_0
...
harness_yaml change moved the gate
```
(51 "before" FAILs collapse to mostly PASS "after"; `diff` exits non-zero; verify's own
`|| { echo "harness_yaml change moved the gate"; exit 1; }` fires; `bash run-unit-tests.sh` is
never reached.)

**Root cause, confirmed:** `git show 3952814:$B/check-plan-routes.py > /tmp/f42-cpr-old.py` places
the restored copy at a bare `/tmp` path, not inside a bin directory.
`check-plan-routes.py:300`'s lazy `import harness_yaml` finds nothing on `sys.path[0]` (`/tmp`, the
child process's script directory per `test-check-plan-routes.py:54-61`'s `subprocess.run`), and
`check-plan-routes.py:29`'s `CHECK_DOMAIN = os.path.join(BIN_DIR, "check-domain.sh")` resolves to
`/tmp/check-domain.sh`, which does not exist. Every other T- in this feature restores via
`cp -R $B $M/.claude/skills/harness/bin` (whole directory); T-05 alone copies one file to a bare
path. **`task_verify: fail`** — not attributable to T-05's code.

## Step 4 — supplementary diagnostic: sha-3952814 copy placed AMONG SIBLINGS (whole bin dir)

Copied the full current `bin/` to a scratch dir, overwrote only `check-plan-routes.py` with the
sha-3952814 version, ran both the swapped and live invocations from there:

```
diff /tmp/f42-t05-sibling-before.txt /tmp/f42-t05-sibling-after.txt
1,16d0
< FAIL case_02_output_has_task_id
...
< FAIL case_19d_explicit_path_unaffected_by_the_root_guard exit 2 stdout='' stderr='check-domain: no
  .../.harness/team-config.yaml — cannot resolve routes.'
17a2,5
> PASS case_02_output_has_task_id
...
SIBLING DIFF EXIT CODE: 1
```

Sibling placement fixes the `sys.path`/`CHECK_DOMAIN` problem (fewer failures, 16 vs 51, and no more
raw import tracebacks) but does **not** produce a byte-identical set either — remaining mismatches
are `check-domain: BLOCKED — the fleet declaration does not load` in the "before" run, which is a
separate root-finding disagreement between the restored old `check-plan-routes.py` and the test
harness's synthetic tmp trees, not something this task's three files caused. This is evidence about
cause only, not a substitute for Step 3.

## `--kind all` — final run, after the harness_yaml.py fix

Exit 1. 1015 PASS, 7 FAIL — **all 7 inside `test-check-state.py`**, matching the dispatch's stated
expected/out-of-scope set (`FAIL test-check-state.py` is a DEC-174 am.4 gate, main-session-direct,
explicitly DO NOT TOUCH):

```
FAIL - case (u.7) F-B: an unimportable harness_boundary.py is a VIOLATION, not a silent skip of INV-25
FAIL - (x.2) an unjudgeable tree -> exit 1, INV-27 CANNOT VERIFY
FAIL - (x.5) unimportable layout_migration -> INV-27 CANNOT RUN, exit 1
FAIL - INV-29 (e) a Done feature's worktree in a SECOND fleet-declared repository produces an INV-29 line from ONE run
FAIL - INV-29 (f.7) SC-17(c): the printed command RUNS and exits 0
FAIL - INV-29 (f.8) SC-17(c): and that worktree is GONE afterwards
FAIL test-check-state.py
```

`(u.7)` and `(x.5)` were not individually enumerated in the dispatch's sample list but are confirmed
present in the pre-fix run too (`/tmp/f42-t05-kindall.txt`, before my harness_yaml.py fix) — not a
regression I introduced, and both fall under the umbrella `FAIL test-check-state.py` line that
dispatch already scoped as out-of-bounds. `test-validate-digest.py` fully PASSED this run (the
[hook] cases that read the live in-flight registry did not collide this time). No other failures
anywhere in the 1015+7-line suite.

## `sys.path` / `require_or_die` ordering findings

- `require_or_die()`'s `if yaml is not None:` guard means a strict `resolve_root` raise can never
  pre-empt the PyYAML-missing stderr message — confirmed correct in the inherited edit.
- `check-plan-routes.py`'s lazy `import harness_yaml` depends on `sys.path[0]` being the script's
  own directory (subprocess default) — the plan's verify places the restored copy at a bare `/tmp`,
  breaking this. This is a defect in T-05's `verify:` text itself, not in any `.py` file under this
  task's `files:` list.

## Bearing on T-07–T-20

- The plan's `verify:` for T-05 needs the same `cp -R $B $M/.claude/skills/harness/bin` treatment
  every other T- verify uses, or it will never pass regardless of code correctness — flagged as
  `open_questions` below, not something I am authorized to edit (main-session-direct territory /
  plan text, not a `.claude/skills/harness/bin/*.py` file).
- Any later task that adds a module-level import to `harness_yaml.py` should re-check
  `test-bash-write-guard.py` / `test-check-domain.py`'s isolated-fixture cases — they are the only
  proof of the D-06 fail-closed pair, and they will not warn you with anything friendlier than a
  raw traceback if violated again.

## Files touched

- `.claude/skills/harness/bin/harness_yaml.py` (T-05's own edit, verified correct, plus my fix:
  moved `import harness_boundary` from module scope into `require_or_die()`)
- `.claude/skills/harness/bin/gen-decisions-index.py` — audited only, no change
- `.claude/skills/harness/bin/validate-feature-json.py` — audited only, no change

---

## CYCLE 1 (send-back) — 2026-08-26

### Correction to cycle 0's record, stated plainly

Cycle 0's "confirmed present in the pre-fix run too" claim (line 143-145 above) was **wrong**. It
compared `(u.7)` and `(x.5)` against its own mid-task run, which already contained cycle 0's own
`harness_yaml.py` fix (import moved into `require_or_die()`) — not against a tree without T-05 at
all. Compared against the real baseline (T-04's completed, non-truncated `--kind all`, confirmed
twice, exactly 5 FAILs, none named `(u.7)` or `(x.5)`), both were new. **T-05 caused them.** Cycle 0
mis-filed two new failures as "expected", which is a real error in that record, not a difference of
interpretation — recording it here per rule 15 rather than quietly overwriting cycle 0's prose above.

### The mechanism — confirmed exactly as the dispatch described, one caller short

Cycle 0's fix moved `import harness_boundary` out of module scope and into `require_or_die()`
(`.claude/skills/harness/bin/harness_yaml.py`), which restored `bash-write-guard.sh` and
`check-domain.sh` (neither calls `require_or_die()`). It did **not** cover `check-state.sh`, which
calls `harness_yaml.require_or_die()` near its own top (`check-state.sh:35`) — before its own later,
properly guarded `import harness_boundary as _hb` at `:1080` (INV-25) ever runs. In the isolated
fixture both `(u.7)` and `(x.5)` build (a bin/ dir carrying only `harness_yaml.py`, no
`harness_boundary.py`), `require_or_die()`'s `import harness_boundary` now raised uncaught —
`ModuleNotFoundError`, uncaught, `check-state.sh` died before it could ever reach `:1080`/`:1657` to
print the "CANNOT RUN" violation both cases assert must appear. Confirmed live before any further
edit: an isolated bin/ with only `harness_yaml.py` and `require_or_die()` called directly raised
`ModuleNotFoundError: No module named 'harness_boundary'` (exit 1) instead of returning.

**`(x.5)`'s cause, checked rather than assumed: identical to `(u.7)`, not a second defect.** `(x.5)`'s
fixture bin/ also carries only `harness_yaml.py` (deliberately omitting BOTH `harness_boundary.py`
and `layout_migration.py` — `check-state.sh:1657`'s own guarded `import layout_migration` is meant to
be what fires). But `require_or_die()` at `check-state.sh:35` raises on the missing
`harness_boundary.py` first, before the script ever reaches `:1657` to prove the `layout_migration`
guard works. Same root cause, same fix.

### The fix, and the mechanism I chose

`require_or_die()`'s resolved root is used for exactly one purpose: building `_marker_path(root)` to
best-effort-unlink the PyYAML bootstrap marker, reached only inside `if yaml is not None:`
(`harness_yaml.py:451-459`). That is opportunistic cleanup, not load-bearing state — unlike the other
two chain sites T-05 touched (`gen-decisions-index.py`'s `os.chdir(project_dir)`,
`validate-feature-json.py`'s `discover_paths` root), where the resolved root drives real behaviour
and a strict raise is the intended signal per T-05's approved intent.

I wrapped the `import harness_boundary` + `resolve_root()` pair inside `require_or_die()` in a
`try/except Exception: return` — if either fails, `require_or_die()` returns normally rather than
propagating. `yaml is not None` was already established by the enclosing branch, meaning PyYAML
itself — the thing this function exists to gate — is fine; only the best-effort marker cleanup is
skipped. This does not weaken `resolve_root` (still `strict=True` everywhere, no env-var fallback, no
`SPEC.md` probe) and does not touch the two chain sites where a strict raise is load-bearing. I did
consider returning `BLOCKED` instead — i.e., concluding the only safe fix contradicts T-05's intent —
but rejected that: T-05's intent is about `resolve_root`'s own callers needing to see the raise, and
`require_or_die()` was never one of those callers for anything except this one incidental cleanup
call; suppressing an incidental caller's incidental failure does not touch the raise's visibility
anywhere it matters.

### TDD: RED confirmed before the fix, GREEN after

Test-check-state.py and check-state.sh are DEC-174 am.4, off-limits — the fix and its test both had
to live in `harness_yaml.py`'s own suite, `test-harness-yaml.py`. Added
`test_require_or_die_survives_a_missing_harness_boundary` (an isolated bin/ carrying only
`harness_yaml.py`, subprocess-imports it and calls `require_or_die()` directly, asserts exit 0 /
stdout `"OK"`). Run before the fix: `FAIL ... ModuleNotFoundError: No module named
'harness_boundary'` (RED, watched). Run after the fix: `ok   test_require_or_die_survives_a_missing_harness_boundary`,
full suite 21/21 tests green (GREEN). Registered in `TESTS` — the list this file's own `main()`
iterates, per its own inline warning about tests defined but never called.

### `--kind all`, run to completion, failures enumerated BY CASE NAME

Invocation: `bash .claude/skills/harness/bin/run-unit-tests.sh --kind all` from the worktree root,
run to completion (no timeout, ~several minutes), exit 1, 3092 `ok`/`PASS` lines, 12 `FAIL` lines:

```
FAIL  [hook] F1.1 quoted headline text must not satisfy the verdict lookup
FAIL  [hook] F1.2 multi-line inline members list is followed to its close
FAIL  [hook] F1.4 empty members against a nonzero steps_run is rejected
FAIL  [hook] DEC-156: narrative digest.md with no contract block is exit 2
FAIL  [hook] DEC-156: digest.md carrying the same valid block is exit 0
FAIL  [hook] DEC-156: missing file fails OPEN with the INV-15 pointer, not a block
FAIL test-validate-digest.py
FAIL - (x.2) an unjudgeable tree -> exit 1, INV-27 CANNOT VERIFY
FAIL - INV-29 (e) a Done feature's worktree in a SECOND fleet-declared repository produces an INV-29 line from ONE run
FAIL - INV-29 (f.7) SC-17(c): the printed command RUNS and exits 0
FAIL - INV-29 (f.8) SC-17(c): and that worktree is GONE afterwards
FAIL test-check-state.py
```

**Matches the T-04 baseline exactly.** The 6 `[hook]` cases + umbrella `FAIL test-validate-digest.py`
are the dispatch's named non-hermetic exception (live in-flight registry collision) — expected,
untouched, `test-validate-digest.py` and its hooks not edited. The remaining 5 lines are the T-04
baseline verbatim: `(x.2)`, `INV-29 (e)`, `INV-29 (f.7)`, `INV-29 (f.8)`, umbrella
`FAIL test-check-state.py`. **`(u.7)` and `(x.5)` are gone.** Neither `test-check-state.py` nor
`check-state.sh` was edited to reach this — only `harness_yaml.py`.

### `test-bash-write-guard.py` / `test-check-domain.py` — still green on MY change, pre-existing
unrelated noise found and isolated

Running these two directly on the current worktree HEAD-plus-uncommitted-work shows non-zero FAIL
counts (2 and 7 respectively) — but confirmed, via `git stash push -- harness_yaml.py
test-harness-yaml.py` (reverting only my two files, leaving every other in-flight task's uncommitted
edits — `harness_boundary.py`, `layout_migration.py`, etc. — untouched) and re-running, that the
**identical** failure set exists with my two files reverted to cycle 0's already-fixed state. This
noise is pre-existing in the current worktree's uncommitted, multi-task state and is orthogonal to
both cycle 0's and my `require_or_die()` change — neither `bash-write-guard.sh` nor
`check-domain.sh` calls `require_or_die()`, and my change touches no other code path. `git stash
pop` restored both my files correctly (confirmed by re-reading `require_or_die()` and the new test
name post-pop). Not investigated further — out of scope for T-05, and the dispatch's own instruction
was "confirm STILL green after your change", which the stash comparison answers: unchanged by my
edit, not caused by it. Flagged in `open_questions` since it is new information the lead did not
have.

### Verify — verbatim, run to completion (matches cycle 0's Q1 exactly, unchanged)

```
$ (plan.yaml T-05's verify block, run verbatim from the worktree root)
...
52a2,5
> PASS case_02_output_has_task_id
> PASS case_03_output_has_offending_path
> PASS case_04_all_granted_exits_0
> PASS case_05_ungranted_declared_main_session_exits_0
...
> PASS case_26g_two_features_DECLARING_the_same_number_still_collide
harness_yaml change moved the gate
```
`diff` between the before/after `test-check-plan-routes.py` runs is non-empty (dozens of PASS lines
only in "after"), so the verify's own `|| { echo "harness_yaml change moved the gate"; exit 1; }`
fires and `bash run-unit-tests.sh --kind all` inside the verify is never reached by the verify script
itself (I ran it separately, above, to get the full case-name enumeration). `task_verify: fail`, same
root cause cycle 0 identified and I did not re-litigate: `check-plan-routes.py`'s restored copy is
placed at a bare `/tmp` path (`git show 3952814:$B/check-plan-routes.py > /tmp/f42-cpr-old.py`)
instead of the sibling-bin pattern every other T- verify uses, so its lazy `import harness_yaml`
finds nothing on `sys.path[0]`. Plan-text defect, not mine to edit, already escalated per the
dispatch — one clean confirming run, not re-proven further.

### Files touched, cycle 1

- `.claude/skills/harness/bin/harness_yaml.py` — `require_or_die()`: wrapped `import
  harness_boundary` + `resolve_root()` in `try/except Exception: return`, so a missing
  `harness_boundary.py` or a `resolve_root` raise cannot abort every caller (including
  `check-state.sh`) over a best-effort marker-cleanup failure.
- `.claude/skills/harness/bin/test-harness-yaml.py` — added
  `test_require_or_die_survives_a_missing_harness_boundary` (RED confirmed pre-fix, GREEN post-fix),
  registered in `TESTS`.
