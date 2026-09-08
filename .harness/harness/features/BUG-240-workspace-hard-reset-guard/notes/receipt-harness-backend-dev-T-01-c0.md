# Receipt — harness-backend-dev — BUG-240 T-01

## Task
T-01: Add the failing guard cases to the factory_workspace unit suite (tests only).
File touched: `tests/unit/test-factory-workspace.py` (the only file in scope; the production
guard, `.claude/skills/harness/bin/factory_workspace.py`, was not touched).

## What was added
- `Recorder.__init__` gained a `porcelain=""` keyword; `Recorder.__call__` answers any `status`
  argv with it, leaving every other answer unchanged.
- `_env_without_harness_project_dir()` — a context manager popping `HARNESS_PROJECT_DIR` before
  a run and restoring it in `finally`, used by the real-git cases and the stderr-content cases.
- `real_repo(wr)` — builds a real bare `origin.git` plus a real working checkout at
  `checkout_path(wr)` with one committed `tracked.txt`, used by cases 2, 3 and 4.
- Seven new cases, each named with the `BUG-240 ` prefix and each emitting exactly one
  `check(...)` call, appended after case (K).
- One additional check inside the existing case (B) block, pinning SC-04's refresh order
  (`fetch` → `checkout <default>` → `reset --hard`, no `clone`, issue-branch checkout last).

## Task `verify:` — run verbatim, cross-checked against plan.yaml T-01 (identical)

Command:
```
cd "$(git rev-parse --show-toplevel)"
out=$(python3 tests/unit/test-factory-workspace.py); rc=$?
test "$rc" = 1 \
  && test "$(printf '%s\n' "$out" | grep -c '^FAIL  ')" = 4 \
  && printf '%s\n' "$out" | grep -q '^FAIL  BUG-240 dirty tracked: exits 2 before any fetch' \
  && printf '%s\n' "$out" | grep -q '^FAIL  BUG-240 dirty tracked: refusal line names the path and the uncommitted-work condition' \
  && printf '%s\n' "$out" | grep -q '^FAIL  BUG-240 dirty tracked: the modified file survives byte-identical' \
  && printf '%s\n' "$out" | grep -q '^FAIL  BUG-240 self checkout: refused when clean, naming the self-checkout condition' \
  && printf '%s\n' "$out" | grep -q '^ok    BUG-240 ignored-only dirt: not refused' \
  && printf '%s\n' "$out" | grep -q '^ok    BUG-240 other harness checkout: onboarded but not the control plane is not refused' \
  && printf '%s\n' "$out" | grep -q '^ok    BUG-240 no bypass: the parser rejects --force' \
  && printf '%s\n' "$out" | grep -q '^ok    BUG-240 existing checkout: refresh order is fetch, checkout default, reset --hard'
```
Run with `env -u HARNESS_AGENT_TYPE` prefixing the python invocation, from the worktree root.
Result: **exit 0**.

## Evidence

- Observed `rc` of `python3 tests/unit/test-factory-workspace.py`: **1**
- Observed count of `^FAIL  ` lines: **4**
- Verify block's own exit status: **0**

## Verbatim result lines for the eight BUG-240 names, plus the trailing summary line

```
FAIL  BUG-240 dirty tracked: exits 2 before any fetch
        code=None kinds=['fetch', 'checkout', 'reset', 'branch', 'branch', 'checkout']
FAIL  BUG-240 dirty tracked: refusal line names the path and the uncommitted-work condition
        code=None err=''
FAIL  BUG-240 dirty tracked: the modified file survives byte-identical
        after=b'tracked content, known bytes\n'
ok    BUG-240 ignored-only dirt: not refused
FAIL  BUG-240 self checkout: refused when clean, naming the self-checkout condition
        code=None err='' kinds=['fetch', 'checkout', 'reset', 'branch', 'branch', 'checkout']
ok    BUG-240 other harness checkout: onboarded but not the control plane is not refused
ok    BUG-240 no bypass: the parser rejects --force

4 of 38 FAILING.
```
(`BUG-240 existing checkout: refresh order is fetch, checkout default, reset --hard` — the
added (B)-block check — printed earlier in the run, in place, as `ok`:)
```
ok    BUG-240 existing checkout: refresh order is fetch, checkout default, reset --hard
```

## Scope check

`git -C <worktree> status --porcelain` shows exactly:
```
 M .harness/harness/features/BUG-240-workspace-hard-reset-guard/BRIEF.md
 M .harness/harness/features/BUG-240-workspace-hard-reset-guard/STATE.md
 M .harness/harness/features/BUG-240-workspace-hard-reset-guard/plan.yaml
 M tests/unit/test-factory-workspace.py
```
plus this receipt (untracked, new). `BRIEF.md`/`STATE.md`/`plan.yaml` are the operator's
pre-existing modifications, not mine. No production file was touched.

## Notes for T-02

- Case 5 requires a module-level `fw._control_plane_root()` that T-02 must introduce; the case
  stubs it unconditionally via `setattr`/sentinel-`getattr` restore, per the intent's discipline.
- The refusal message format expected by cases 2/5: caught by `factory_cli.run`'s `expected=`
  trap and printed as a single `factory: workspace: <msg>` line on stderr, containing the
  absolute checkout path and either "uncommitted" (case 2) or "control-plane" (case 5), never
  both, and never "unexpected failure".
