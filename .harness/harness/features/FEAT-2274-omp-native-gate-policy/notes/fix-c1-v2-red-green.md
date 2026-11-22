# Fix c1 — V2 (dispatch-guard silent pass-throughs) RED → GREEN

Finding V2 (med, SC-01): `dispatch-guard.py` skipped a failed run-dir vocabulary derivation
and an unreadable target tool-grants file with stderr only, so the extension saw a normal pass.

## Change
- `.claude/skills/harness/bin/dispatch-guard.py`
  - run-dir vocabulary derivation failed (`HARNESS_RUN_DIR_DERIVED` != "0", no globs): keeps the
    SKIPPED stderr line and the pass-through, and now calls
    `hb.emit_unavailable(__file__, "the run-dir vocabulary could not be derived ...; the run-dir slug shape was not checked")`.
  - target tool grants unreadable (`OSError`/`ValueError`/`IndexError`): keeps the stderr line and
    `has_bash = True`, and now calls
    `hb.emit_unavailable(__file__, "could not read tool grants for <target> (<exc>); the shell-less feature-tree-root check was not run")`.
  - The grant-less manifest (`HARNESS_RUN_DIR_DERIVED == "0"`), readable grants without Bash and
    non-governed targets are unchanged and emit nothing.
- `tests/integration/test-dispatch-guard.py`: three new small cases plus two helpers
  (`_f2274_v2_member_dispatch`, `_f2274_v2_check`); `case_f2274_unavailable_outcome` is not grown.
  - `case_f2274_v2_failed_run_dir_vocabulary_is_unavailable`: one fault (unparseable manifest + run-dir reference) → exit 0, claim receipt, exactly `["dispatch-guard"]`.
  - `case_f2274_v2_unreadable_tool_grants_are_unavailable`: one fault (target persona file removed) → exit 0, claim receipt, exactly `["dispatch-guard"]`.
  - `case_f2274_v2_legitimate_passthroughs_stay_quiet`: controls. A readable shell-less grant (product lead with a matching root), a grant-less run-dir manifest (and a check that it reached the declared-empty branch), and a non-governed target all exit 0 with no unavailable line.

## Fixture migration (no assertion weakened)
`_PERSONAS` now also copies `harness-pm.md`. `_feat65_fire` and `case_f2274_unavailable_outcome`
dispatch `harness-pm` into a `_checkout()` that never contained its grants file. That was a
second fault nobody noticed: the guard silently hit the unreadable-grants branch. Once that
branch reports itself (GREEN run 1), "an own crash" and "the claim step's own registry failure"
produced TWO unavailable lines (grants + the injected fault) and failed their "exactly one"
assertion. The assertion is correct and unchanged. The fixture now carries the persona it
dispatches, so each case injects only its own fault. harness-pm grants `bash`, so no other
case's path changes.

## RED
Command: `python3 tests/integration/test-dispatch-guard.py` (worktree root), before the guard change:
```
FAIL  f2274 v2: a failed run-dir vocabulary derivation is one unavailable line
      | exit 0, stdout='{"harness_claim": {"agent": "harness-backend-dev", ...}}\n', stderr='dispatch-guard: run-dir shape check SKIPPED -- the run-dir vocabulary derivation failed (manifest unreadable, unparseable, or PyYAML unavailable to that python3).\n'
FAIL  f2274 v2: unreadable target tool grants are one unavailable line
      | exit 0, stdout='{"harness_claim": {"agent": "harness-backend-dev", ...}}\n', stderr="dispatch-guard: could not read tool grants for harness-backend-dev ([Errno 2] No such file or directory: '.../.omp/agents/harness-backend-dev.md') -- passing through.\n"
PASS  f2274 v2: a readable shell-less grant passes with no unavailable line
PASS  f2274 v2: a grant-less run-dir manifest passes with no unavailable line
PASS  f2274 v2: a non-governed target passes with no unavailable line
171 of 173 cases passed
```

## GREEN
Intermediate run after the guard change, before the fixture migration: 172 of 174. "an own crash"
and "the claim step's own registry failure" each printed two lines: the harness-pm grants line
plus the injected fault. See "Fixture migration".

Final: `python3 tests/integration/test-dispatch-guard.py` → exit 0:
```
PASS  f2274 v2: a failed run-dir vocabulary derivation is one unavailable line
PASS  f2274 v2: unreadable target tool grants are one unavailable line
PASS  f2274 v2: a readable shell-less grant passes with no unavailable line
PASS  f2274 v2: a grant-less run-dir manifest passes with no unavailable line
PASS  f2274 v2: the grant-less control reached the declared-empty vocabulary
PASS  f2274 v2: a non-governed target passes with no unavailable line
174 of 174 cases passed
```
