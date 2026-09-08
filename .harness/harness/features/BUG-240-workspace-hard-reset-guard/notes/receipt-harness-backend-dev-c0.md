# Receipt — harness-backend-dev — BUG-240-workspace-hard-reset-guard

## BLUF
Fixed the self-checkout identity guard in `_main()` (factory_workspace.py:142): it now uses
`os.path.samefile(path, _control_plane_root())`, falling back to realpath string equality only
when `samefile` raises `OSError` (path not yet cloned). A differently-cased spelling of the
control-plane checkout is now correctly identified and refused; previously it slipped past the
string comparison and fell through to `fetch`/`reset --hard` against the control plane.

## Order of operations (test-first, as required)

### Step 1 — RED, observed on unmodified production code
Added case 8 to `tests/unit/test-factory-workspace.py` (after case 7, before the final tally),
following case 5's save/restore pattern for `fw._control_plane_root`, `Recorder(porcelain="")`
and `run_main`/`checkout_path`. The case probes filesystem case-sensitivity at runtime inside the
tempdir and only asserts when the probe reports case-insensitive (true on this host); otherwise it
prints a skip note and calls no `check()` (no vacuous pass).

Command:
```
cd <worktree> && env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-workspace.py; rc=$?; echo "rc=$rc"
```
Verbatim RED output (unmodified production code):
```
FAIL  BUG-240 case-mismatched self checkout: refused via identity, not spelling
        code=None err='' kinds=['status', 'fetch', 'checkout', 'reset', 'branch', 'branch', 'checkout']

1 of 39 FAILING.
rc=1
```
This confirms the finding's premise reaches this code path: the case-mismatched path was NOT
refused, `fetch`/`reset` DID run, and `code` was `None` (process ran to completion) rather than 2.

### Step 2 — the fix
`factory_workspace.py` :142, inside `_main()`, exact diff shape (byte-identical `refuse()` kwargs
and position, unchanged — only the condition expression changed, no helper extracted):
```python
    try:
        is_control_plane = os.path.samefile(path, _control_plane_root())
    except OSError:
        # path (the ordinary not-yet-cloned workspace) doesn't exist yet: samefile can't stat
        # it, so identity falls back to a spelling comparison — the clone-path case, not the
        # self-checkout one this guard exists to catch.
        is_control_plane = os.path.realpath(path) == os.path.realpath(_control_plane_root())

    if is_control_plane:
        factory_cli.refuse(
            tool="workspace",
            what="refusing to reset the harness control-plane checkout",
            value=os.path.abspath(path),
            next_step=(
                "the control plane is never its own scratch workspace: point workspace_root "
                "in fleet.yaml at a directory that is not this checkout"
            ),
        )
```
The refusal still fires before the first destructive git command (`fetch`/`checkout`/`reset
--hard`, unchanged below it) and still names the self-checkout condition.

### Step 3 — verification, in order

**(a) new case alone (re-run, GREEN):**
```
ok    BUG-240 case-mismatched self checkout: refused via identity, not spelling
```
(present twice in the run — once from the isolated confirmation run, once from the full run
below; both green.)

**(b) full unit file:**
```
cd <worktree> && env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-workspace.py
rc=0
39/39 checks passed.
```
(38 pre-existing + the new case 8 = 39; zero FAIL lines.)

**(c) full unit-kind suite:**
```
cd <worktree> && env -u HARNESS_AGENT_TYPE bash .agents/skills/harness/bin/run-unit-tests.sh --kind unit
rc=0
```
`grep -c '^FAIL '` on the captured output: `0`. Tail of run confirms `test-factory-workspace.py`
(embedded in the pooled run) and all sibling suites (`test-suite-layout.py`,
`test-suite-independence.py`, `test-code-grade.py`, etc.) passed; pool summary: 31 files, 2.29s wall.

## Scope discipline
- Untouched: dirty-check placement/logic, TOCTOU window, docstring/D-01 wording, refusal-copy
  style, `--force` bypass guard (case 7 still green).
- No helper extracted; the two `refuse()` guards in `_main` remain exactly as before, only the
  self-checkout condition expression changed.

## `git status --porcelain` (worktree)
```
 M .claude/skills/harness/bin/factory_workspace.py
 M tests/unit/test-factory-workspace.py
?? .harness/harness/features/BUG-240-workspace-hard-reset-guard/notes/review-harness-code-reviewer-c0.md
?? .harness/harness/features/BUG-240-workspace-hard-reset-guard/notes/review-harness-qa-c0.md
?? .harness/harness/features/BUG-240-workspace-hard-reset-guard/notes/review-harness-security-reviewer-c0.md
?? .harness/harness/features/BUG-240-workspace-hard-reset-guard/notes/review-harness-ui-reviewer-c0.md
?? .harness/harness/features/BUG-240-workspace-hard-reset-guard/observations/harness-security-reviewer.md
```
Only the two target files (`M`) were touched by this dispatch. The `??` entries are sibling
validator-panel artifacts (concurrent activity, out of scope for this dispatch) — reported per
O-06, not reverted. Change left UNCOMMITTED as instructed.
</content>
