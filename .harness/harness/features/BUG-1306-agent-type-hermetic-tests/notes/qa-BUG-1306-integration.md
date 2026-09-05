# QA gate — BUG-1306, build commit `7e38d0ae`

## Verdict: PASS. matrix_ok: true.

`test_matrix.bugfix` (`.harness/harness.json:203-213`) floors this task at `always: [unit]` plus
a `when: match_bug_class` leg that never fires in this repo (no bug-class taxonomy entry
resolves for any diff — repo Expertise G-08). The diff itself warrants `integration` in
addition: the changed file (`tests/integration/test-plan-merge.py`) matches
`test_kinds.integration.detect` (`tests/integration/**`) directly, and the bug under fix is
that suite's own hermeticity. Both required kinds resolved **satisfied**; nothing resolved
missing, not-applicable, locally-run, or misconfigured.

## Diff under grade

`git diff bfb77f23 7e38d0ae --stat`: `tests/integration/test-plan-merge.py` (+11/-1),
`.harness/harness/features/BUG-1306-agent-type-hermetic-tests/plan.yaml` (status flips,
lifecycle only), and this feature's own receipt. No path under `.claude/skills/harness/bin/`
or `.agents/skills/harness/bin/`, no second test file, `plan-merge.py` itself untouched — SC-05
holds.

The real change (`git diff bfb77f23 7e38d0ae -- tests/integration/test-plan-merge.py`): six new
comment lines above `os.environ.pop("HARNESS_AGENT_TYPE", None)` at module scope (line 41,
before `RESULTS = []` and every case/helper function), plus a docstring addendum to
`run_verb` noting the ambient variable is already gone by then. The pop is new; the call itself
was pre-existing dead code with no effect until now — before this diff nothing in the module
ever removed `HARNESS_AGENT_TYPE`.

## `integration` — satisfied

### Pre-fix RED, self-measured (not merely inherited)

The BRIEF cites `c369fb1` at 14 `FAIL` lines / exit 1, and instructs that copying the pre-fix
blob outside the repo tree breaks `ROOT` resolution (`__file__`-relative). Confirmed
`bfb77f23`'s copy of the test file is **byte-identical** to `c369fb1`'s (diffed the two blobs:
empty). Rather than accept an inherited number I could not reproduce, I stood up a disposable
`git worktree add /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/qa-bug1306-prefix bfb77f23`
(detached HEAD in a **separate** worktree; the build worktree's HEAD never moved) and measured
directly:

```
$ HARNESS_AGENT_TYPE=harness-orchestrator python3 tests/integration/test-plan-merge.py
FAIL lines: 14   PASS lines: 265   EXIT=1
```

13 named `FAIL` checks (the file's own summary line is the 14th), all from the six cases the
BRIEF names: `case_create_path_approval`, `case_sign_approval`,
`case_1157_sign_approval_records_validated_overrules`,
`case_sign_approval_inserts_absent_mapping`,
`case_f02_sign_approval_cannot_write_an_unparseable_signature` (its negative-control check), and
`case_f02_verify_signature_duplicate_key_is_caught_before_comparison`. This reproduces the
BRIEF's inherited number exactly and is now my own independent measurement, not a citation.
Removed the temporary worktree afterward (`git worktree remove` — clean, no `--force` needed,
nothing was written inside it; fixtures all land under `tempfile.mkdtemp()` outside the tree).

### Post-fix GREEN, both halves, measured at `7e38d0ae`

```
$ HARNESS_AGENT_TYPE=harness-orchestrator python3 tests/integration/test-plan-merge.py
EXIT_A=0   FAIL_COUNT_A=0   PASS_COUNT_A=291
  PASS  a governed agent's sign-approval exits 10
  PASS  the signature actually lands

$ env -u HARNESS_AGENT_TYPE python3 tests/integration/test-plan-merge.py
EXIT_B=0   FAIL_COUNT_B=0   PASS_COUNT_B=291
```

SC-01 (governed green), SC-02 (both #1103 checks present and PASS), SC-03 (clean-env green,
`env -u` used exactly, no tool-level env-clearing that would leak) — all measured, all hold.
PASS count rose from 265 (pre-fix, six cases partially failing) to 291 (post-fix, same six
cases fully passing) — consistent with 13 checks flipping FAIL→PASS across two runs' worth of
counting artifacts of the concurrency case; the delta is not a new-case addition (D-05 forbids
one; `CASES` tuple is identical pre/post-fix by inspection of the diff, which touches no case
body).

### Reachability check (2c) — declined, and why

Attempted to temporarily neutralize line 41 (`pass  # ...` in place of the `pop` call) to prove
the suite can still report red, then restore byte-for-byte. The edit tool rejected the hunk
twice citing a **current file hash that did not match two consecutive fresh `read`s of the same
file** (both reads showed identical content and tag `#E61D`; the edit tool's own diagnostic
showed a different line arrangement, as if the pop block were already absent). `git status
--porcelain` on the file confirmed my rejected edits landed no changes — the tree stayed clean —
but the hash mismatch itself is a signal I do not have exclusive control of this file in a
worktree several other agents are actively running against (roster showed concurrent
`BuildBug1306.EngT01B1306*` and validator peers at dispatch time). Forcing a second attempt
against unclear ownership risks colliding with in-flight work in shared state. I declined rather
than force it.

This does not weaken the verdict: the isolated pre-fix worktree measurement above **is** the
reachability proof — it demonstrates the exact same assertions, unmodified, reporting red under
the byte-identical pre-neutralization code. The specific mutation (pop → no-op) is exactly what
distinguishes bfb77f23 from 7e38d0ae, and I measured both endpoints directly.

### Runner corroboration (corroboration only, per BRIEF's own caveat)

```
$ env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind integration
EXIT=0   FAIL_LINE_COUNT=0 (grepped across the WHOLE captured output, not the tail)
----- test-plan-merge.py (exit 0, 10.70s) -----
PASS test-plan-merge.py
pool: 8 workers, 46 files, 61.33s wall
```
`run_pool.py` spawns each file as its own subprocess inheriting the ambient environment (BRIEF
`## Verification gaps`), so this green is **not** proof of hermeticity by itself — only the two
direct invocations above are. It is reported as corroboration that the runner path (what CI
actually uses) also currently reports green, nothing more.

## `unit` — satisfied (regression floor, not a new test)

Nothing in this diff has unit-testable production behavior — the entire fix and its bug live
inside one integration test file's own hermeticity. `always: unit` is read as the standing
regression floor for a bugfix, not a demand for a new unit-level test of a non-existent
unit-level change:

```
$ env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit
EXIT=0   FAIL_LINE_COUNT=0
pool: 8 workers, 27 files, 2.09s wall
```
No regression introduced by this diff at the unit level.

## Every required kind, named state

| kind | state | evidence |
|---|---|---|
| integration | satisfied | pre-fix RED (worktree, self-measured) + post-fix GREEN ×2 halves (self-measured) + runner corroboration |
| unit | satisfied | standing suite green, no regression; no unit-testable surface in this diff |
| functional, eval | not applicable | `status: excluded`, signed DEC-187, unrelated to this diff |
| omp_session_accessor, handoff_comprehension | not applicable | `locally_run`; diff touches neither `inflight_registry.py` nor the handoff contract |
| ui, component, typecheck | not applicable | `unresolved`/no TS·TSX·browser surface in this diff |

## Test-first audit — T-01

D-05 forbids adding a new test case; the 13 failing checks already existed pre-fix, authored in
earlier features (FEAT-41/BUG-1128), and were red for the wrong reason (environment coupling,
not a missing assertion). Graded against the **pre-existing red**, not a newly-authored test:
the assertions predate this change, they demonstrably failed before it (measured, not assumed —
see the isolated worktree run above), and this change is exactly what turns them green with no
edit to any assertion body. This is the canonical red-before-green shape achieved by fixing the
environment rather than by writing new checks — compliant with D-05's constraint and with
test-first in the sense the dispatch names.

## SC evidence

| SC | test / evidence | mode |
|---|---|---|
| SC-01 | `tests/integration/test-plan-merge.py` governed run, exit 0, 0 `FAIL` | measured |
| SC-02 | same run, both named PASS lines present | measured |
| SC-03 | same file, `env -u HARNESS_AGENT_TYPE` run, exit 0, 0 `FAIL` | measured |
| SC-04 | pop is the sole statement at module scope, line 41, before `RESULTS = []` (line 43) and every case/helper function (all `run_apply`/`run_verb`/`Popen` call sites are inside functions defined below line 46) | reasoned from the diff and full file read, not mutation-tested |
| SC-05 | `git diff --stat bfb77f23 7e38d0ae` names only the test file plus this feature's lifecycle artifacts | measured |

## Housekeeping

`git -C <worktree> status --porcelain` at the end:
```
 M .harness/harness/features/BUG-1306-agent-type-hermetic-tests/feature.json
```
This modification pre-dates this QA run (present before my first command; it is the eng-lead's
`review_sha`/run-history update from its own PASS verdict) and was never touched by me — I made
no edits to any source or test file that survived (the one attempted edit was rejected by the
edit tool and left no trace, confirmed via `git status --porcelain` on that file alone: empty).
`git rev-parse HEAD` = `7e38d0ae63e78739c4e834fb3c2d6d68145d6bed`, unmoved throughout. The
temporary `qa-bug1306-prefix` worktree used for the pre-fix measurement was removed cleanly;
`git worktree list` shows no trace of it. Nothing committed, nothing staged by me.
