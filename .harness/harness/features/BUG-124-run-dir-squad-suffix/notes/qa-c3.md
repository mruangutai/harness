# QA Gate — BUG-124-run-dir-squad-suffix — cycle 3 (causation falsification)

## BLUF

**The hypothesis HOLDS.** `harness_boundary.py:22`'s bare `import harness_yaml` (T-01, present
since cycle 1, hunk `@@ -21,0 +22 @@` in `80ce35d1..e7994376`) breaks any synthetic fixture that
copies `harness_boundary.py` without also copying `harness_yaml.py`. Three of the four full-sweep
failures cycle 2 called "pre-existing, unrelated" are actually **caused by T-01's own diff**. The
fourth (`test-check-domain.py`) fails for a different, genuinely pre-existing reason.

**Supersedes cycle 2 §"Full-project sweep re-investigated" and its conclusion "matrix_ok: true...
its failing surface is entirely pre-existing, unrelated code untouched by BUG-124."** That was
wrong for 3 of 4 files. Cycle 2's reasoning ("`resolve_root` is untouched, so the diff can't be
responsible") checked the wrong function — the failure is at `import harness_boundary` itself,
before `resolve_root` is ever called.

**Ruling: `integration` kind is FAILING at `c06c483c`. `matrix_ok: false`.**

## Per-file measurements (run by me, `env -u HARNESS_AGENT_TYPE python3 tests/integration/<file>`)

| file | exit | failures | first failure (verbatim) |
|---|---|---|---|
| `test-run-unit-tests-kinds.py` | 1 | 2 | `FAIL --kind all excludes comprehension probe run-unit-tests.sh: no harness root could be resolved from <tmp>/.claude/skills/harness/bin — refusing to run` |
| `test-run-unit-tests-layout.py` | 1 | 13 | `FAIL clean layout run-unit-tests.sh: no harness root could be resolved from <tmp>/.claude/skills/harness/bin — refusing to run` |
| `test-check-plan-routes.py` | 1 | 2 | `FAIL case_19b_unresolvable_root_exits_2_not_0 exit 1 stdout='' stderr='Traceback (most recent call last):\n  File ".../check-plan-routes.py", line 34, in <module>\n    import harness_boundary  # noqa: E4` (truncated by the test's own `[:200]` slice) |
| `test-check-domain.py` | 1 | 1 | `FAIL  sweep/clean-tracked RED: the mutant reported no more than the original, so case A does not discriminate the fix from its absence.` |

## Attribution — bounded

**Mechanism explains (3 of 4 files):**

- `test-run-unit-tests-kinds.py:49-52` and `test-run-unit-tests-layout.py:19-22` copy exactly
  `run-unit-tests.sh, harness_boundary.py, run_identity.py, suite_layout.py, run_pool.py` —
  `harness_yaml.py` omitted. `run-unit-tests.sh:4` runs `python3 -I -c '... import
  harness_boundary; print(harness_boundary.resolve_root(...))' 2>/dev/null`. Under `-I`,
  `harness_yaml` is not importable from the fixture bin dir; `import harness_boundary` raises
  `ModuleNotFoundError` before `resolve_root` runs; stderr is swallowed by `2>/dev/null`; `_ROOT`
  comes back empty; line 6 prints the observed message verbatim, exit 2, and the wrapping test
  reports it as a script-level FAIL.
- `test-check-plan-routes.py:438-439` (case_19b/19b2) copies only `harness_boundary.py,
  run_identity.py` beside a copy of `check-plan-routes.py`. Its own comment at lines 433-437
  **predicts this exact failure mode almost verbatim**: "Without these modules beside the copy
  the script dies on ImportError at exit 1 before it can refuse, and both assertions go red for a
  reason that has nothing to do with an unresolvable root." The captured traceback confirms: `File
  ".../check-plan-routes.py", line 34, in <module>\n    import harness_boundary` — the crash is at
  the `import harness_boundary` line itself, not inside `resolve_root`. Expected exit 2 with
  `check-plan-routes: ...` on stderr; actual is an uncaught exit-1 traceback.
- Both control fixtures behave as the hypothesis predicts they should, confirming the mechanism is
  specific to the omission rather than a general fixture-building defect:
  `test-check-plan-routes.py:686-689` copies **every** `.py`/`.sh` in the bin dir (includes
  `harness_yaml.py`) and is unaffected. `test-check-domain.py:1690`'s fixture area also copies
  `harness_yaml.py` explicitly and that case is not among the failures.

**Mechanism does NOT explain (1 of 4 files, different cause):**

- `test-check-domain.py`'s single failure is `sweep/clean-tracked RED` at
  `test-check-domain.py:2326-2330` — a **non-discriminating mutation self-test**: `mut <= base`
  (both counts equal), not a crash, not a traceback. This is the identical failure signature cycle
  1 and cycle 2 both already recorded under this name; it is unaffected by whether
  `harness_boundary` imports cleanly (the assertion fires on mutant-vs-original count parity, and
  the printed line shows a clean numeric comparison, not an exception path). This file's fixture at
  `test-check-domain.py:2313-2316` (`harness_boundary.py`, `run_identity.py`, no `harness_yaml.py`)
  is a candidate for the same mechanism in principle, but the actual recorded failure text does not
  show it firing there in this run — I did not find a second, distinct import-traceback failure
  from this file. **Ruling stands: this file's failure is the pre-existing non-discriminating
  self-test (Q2-adjacent), separate from T-01's causal mechanism**, not attributed to T-01.

## A/B repro (step 2) — write guard refused; substituted evidence used instead

Attempted the prescribed A/B in a disposable scratch location twice: first a plain tempdir, then a
disposable `git worktree add` per repository Expertise G-06 (`.claude/worktrees/harness/qa-c3-repro`
at `c06c483c`, removed afterward from the main checkout, not from inside it). **Both `cp` attempts
were denied by bash-write-guard** ("outside your domain") — neither a bare `/tmp` path nor a
sibling scratch worktree is in this agent's write domain for this feature. Per the dispatch's own
fallback instruction, I did not manufacture write-guard evasion and moved to the alternative
evidence in step 2's own log: **the test suite's own subprocess IS the A/B**, and its result is
decisive without a hand-built fixture — `test-check-plan-routes.py:433-437`'s own comment states
the predicted failure mode before I ever ran it, and the captured traceback matches it exactly
(`import harness_boundary` crashing at the module's own top level, not inside `resolve_root`).
Cycle 2's `git diff -U0 80ce35d1..e7994376 -- harness_boundary.py` (hunks only at `@@ -21,0 +22 @@`
and `@@ -806,0 +808,98 @@`) plus `git show c06c483c:.claude/skills/harness/bin/harness_boundary.py`
lines 18-24 (read this cycle, confirms line 22 is the bare top-level `import harness_yaml`) is the
second, independent confirmation the dispatch asked for as an alternative to the temp-dir A/B.

## Step 3 — file provenance (confirms BUG-124 did not touch the four test files)

`git diff --stat 80ce35d1..c06c483c -- tests/integration/` shows only
`test-dispatch-guard.py | 183 +++...` — no other integration test file changed. `git log --oneline
-1` for each of the four failing files resolves to pre-BUG-124 commits (`c569d8a9`, `c569d8a9`,
`ab1d3527`, `252a18a9`) — none is a BUG-124 commit. This is consistent with the hypothesis: the
fixtures were already shaped this way; T-01's new import is what turned a previously-inert
omission into a live crash.

## Remedy shape (not implemented, per dispatch)

T-01's own `intent:` claim — "importing harness_yaml at module top level is safe (it already wraps
its yaml import in try/except)" — is true for the case it addresses (PyYAML absent) and false for
the case that actually broke (`harness_yaml.py` itself absent from a synthetic bin tree).
`run_dir_grant_globs`'s own stated contract ("return the empty list and never raise when the
manifest is absent, unreadable, does not parse, or PyYAML is missing") is a contract about what
happens *after* a successful import, not about import failure itself — so it does not by itself
argue for either remedy family. The coherent fix belongs to `harness_boundary.py`'s own import,
not the fixtures: **guard the `import harness_yaml` in `harness_boundary.py`** (e.g. try/except
falling back to a no-op shim, matching the resilience pattern `harness_yaml`'s own internal
PyYAML-absent handling already uses), rather than adding `harness_yaml.py` to every fixture's copy
list — the fixtures encode a deliberate "minimal bin dir" test surface (case_19b's own comment: "it
is not about a missing module"; the kinds/layout fixtures name an explicit, curated file list), and
widening every one of them to chase a new transitive dependency each time `harness_boundary.py`
gains one is the wrong side of the coupling to fix.

## Ruling

- `integration`: **FAILING** at `c06c483c` — the required kind's own governed suites do not pass.
- `matrix_ok`: **false**.
- Routable as a fix cycle (the causal line, `harness_boundary.py:22`, is inside T-01's own declared
  `files:`), not an escalation.
- Cycle 1 and cycle 2's `unit` kind ruling (satisfied), the three `bugfix` predicate evaluations,
  the assertion-strength review, the Q1 test-first ruling, `test-dispatch-guard.py` at 69/69, the
  61/69 red-capability reproduction, and the four behavioural-equivalence rulings are **not
  re-litigated** and stand.
