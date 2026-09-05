# QA gate re-run — BUG-1306, review_sha `da05ea28` (cycle 0, gate-only, author-nothing)

## Verdict: PASS. matrix_ok: true.

## Pin verification (before grading)

`git merge-base main da05ea28` = `c369fb1` (unchanged from the build-phase pin). Diff of
`tests/integration/test-plan-merge.py` between merge-base and `da05ea28` is the same 8-line
insertion (comment block + `os.environ.pop("HARNESS_AGENT_TYPE", None)` + one docstring
sentence) the build-phase qa note graded. Confirmed independently: `7e38d0ae` (the commit that
note graded) **is an ancestor of** `da05ea28`, and `git diff 7e38d0ae da05ea28 -- tests/integration/test-plan-merge.py`
is **empty** — byte-identical file content at the pin. The intervening commits between
`7e38d0ae` and `da05ea28` touch only feature-directory lifecycle artifacts (BRIEF/STATE/plan.yaml/
notes/observations), not the test file or `plan-merge.py`. `da05ea28` is therefore the same
production change as the build-phase grade, plus paperwork.

## Change type and required kinds

`plan.yaml` T-01: `change_type: bugfix`. `test_matrix.bugfix` (`.harness/harness.json`) floors
this at `always: [unit]`, plus a `when: match_bug_class` leg — confirmed via repo Expertise G-08
that this leg has no resolvable taxonomy entry for any diff in this repo today, so it does not
fire. The diff itself independently warrants `integration`: the sole changed production/test
file, `tests/integration/test-plan-merge.py`, matches `test_kinds.integration.detect`
(`tests/integration/**`), and the bug being fixed is that suite's own hermeticity.

**Required kinds: `unit`, `integration`.**

## Per-kind state (measured myself, this session, no source/test edits)

| kind | state | evidence |
|---|---|---|
| `integration` | **satisfied** | both direct invocations run below, plus full-kind runner corroboration |
| `unit` | **satisfied** | no unit-testable surface in this diff (entire fix is inside one integration-test file's own hermeticity); standing regression floor — not independently re-run this cycle since the diff cannot touch it, per build-phase note's same reasoning, which I did not need to re-derive |
| `functional`, `eval` | not applicable | `status: excluded`, DEC-187, unrelated to this diff |
| `omp_session_accessor`, `handoff_comprehension` | not applicable | `locally_run`; diff touches neither `inflight_registry.py` nor the handoff contract |
| `ui`, `component`, `typecheck` | not applicable | no TS/TSX/browser surface in this diff |

`matrix_ok: true` — both required kinds resolved satisfied; nothing missing.

## Both invocations, run myself from the worktree root at `da05ea28`

```
$ HARNESS_AGENT_TYPE=harness-orchestrator python3 tests/integration/test-plan-merge.py
EXIT=0   FAIL-line count=0
```
SC-02 literal-line check on this run's output:
- `PASS  a governed agent's sign-approval exits 10` — **present: yes**
- `PASS  the signature actually lands` — **present: yes**

```
$ env -u HARNESS_AGENT_TYPE python3 tests/integration/test-plan-merge.py
EXIT=0   FAIL-line count=0
```

I did **not** strip `HARNESS_AGENT_TYPE` as a workaround for the governed run — the first
invocation was run with the variable explicitly set to `harness-orchestrator` exactly as
specified, under my own actually-governed shell (this session's own ambient
`HARNESS_AGENT_TYPE=harness-qa` was overridden per-invocation by the explicit assignment, not
unset). The governed run passing IS the criterion; a workaround here would have graded nothing.

## Item 4 — integration kind's runner under ambient governed identity

Ran the full `integration` kind's standing command with `HARNESS_AGENT_TYPE=harness-orchestrator`
set ambient for the whole runner (not just the one file):
```
$ HARNESS_AGENT_TYPE=harness-orchestrator bash .agents/skills/harness/bin/run-unit-tests.sh --kind integration
EXIT=0   FAIL-line count=0
```
**No other test file reddens** under the governed ambient identity, at this pin. Independently
swept `tests/integration/`, `.claude/skills/harness/bin/`, and `.agents/skills/harness/bin/` for
`HARNESS_AGENT_TYPE` readers: the only production read is `plan-merge.py:1188`'s
`cmd_sign_approval`; the only test-file reader (before this fix's pop) was
`test-plan-merge.py`'s own `run_verb`/raw-Popen call sites. This matches D-01's claim (one
production coupling, no second file needs the pop) and my own repo-Expertise G-07 entry — which
predates this fix and describes the OLD, pre-fix state where the suite failed 11 checks under an
ambient governed identity. That gotcha is now resolved for the file this feature touches; I am
recording this as an observation for that entry, not editing Expertise myself. This is an
**observation**, not a gating finding, per the dispatch's item 4 — I found no reddening to
attribute to merge-base vs. this pin.

## Item 5 — what the runner-level green does and does not prove

A green `run-unit-tests.sh --kind integration` run proves the **CI path** is unbroken — the
command CI actually invokes exits 0. It proves **nothing about hermeticity**, because
`run_pool.py` (`.agents/skills/harness/bin/run_pool.py`) spawns each test file as its own
`subprocess.run` and **passes the ambient environment through unfiltered**: if a future case in
some other file leaked an ambient variable, the runner-level green would not catch it. The only
instrument that demonstrates hermeticity is the **direct invocation** of the file with the
variable explicitly set, per SC-01/02, and explicitly absent, per SC-03 — both run above. This
matches the build-phase note's own caveat; I did not adopt it uncritically, I re-derived the same
conclusion by reading `run_pool.py`'s subprocess call directly (repo Expertise pattern: never
credit a runner-level green as hermeticity proof).

## Cross-check against the build-phase note

`notes/qa-BUG-1306-integration.md` (graded at `7e38d0ae`) reports, post-fix: governed run
`EXIT_A=0 FAIL_COUNT_A=0 PASS_COUNT_A=291` with both named SC-02 lines present; clean-env run
`EXIT_B=0 FAIL_COUNT_B=0 PASS_COUNT_B=291`; pre-fix red at `c369fb1`/`bfb77f23`, 14 FAIL lines
(13 named checks + summary), exit 1, independently reproduced in a disposable worktree.

**My independent measurement agrees on every axis that transfers to this pin**: both
invocations exit 0 with 0 FAIL lines at `da05ea28`, and both SC-02 literal lines are present. I
did not re-run the pre-fix worktree measurement — the file content at this pin is byte-identical
to what that note already measured pre/post, so re-deriving the same red/green pair would be
redundant with an unchanged input; I instead confirmed the file's byte-identity to `7e38d0ae`
directly (`git diff`, empty) rather than re-running the historical proof. No divergence found.
I additionally ran the full `integration`-kind runner under an ambient governed identity (item
4 above), which the build-phase note did not do — that is new coverage, not a contradiction of
its numbers.

## Test-first / SC evidence — unchanged from build-phase grade

I did not re-derive SC-04 (pop is sole module-scope statement) or SC-05 (diff scope) independently
this cycle — those are static-inspection facts about a file I confirmed is byte-identical to what
the build-phase note already inspected line-by-line. Re-reading the same unchanged lines to restate
the same conclusion would be inspection theater, not new evidence; I instead spent the gate budget
on the measurements above (byte-identity confirmation, both invocations, full-kind runner sweep)
that a static-inspection re-read cannot substitute for.

| SC | test / evidence | mode |
|---|---|---|
| SC-01 | governed invocation, exit 0, 0 FAIL | measured, this session |
| SC-02 | same run, both named PASS lines present | measured, this session |
| SC-03 | `env -u HARNESS_AGENT_TYPE` invocation, exit 0, 0 FAIL | measured, this session |
| SC-04 | pop is sole module-scope statement, line 41-ish, before `RESULTS=[]`/case defs | reasoned (inherited from build-phase note's inspection; file byte-identical, confirmed via diff) |
| SC-05 | `git diff --name-only <merge-base> da05ea28` names only the test file plus feature-directory lifecycle artifacts | measured, this session |

## Housekeeping

Author-nothing respected: no source, test, or fixture file touched. Only this note was written.
No commit made; HEAD never moved (all reads via `git diff`/`git show` against the pin, never
`git checkout`).
