# Receipt — harness-backend-dev — T-02 cycle 2

## BLUF

Fixed. The T-02 run-dir derivation block's launch line in `dispatch-guard.sh` is now
the same-line pop-and-exec bootstrap already used by `check-domain.sh` and
`bash-write-guard.sh`:

```
if _globs=$(python3 -c 'import sys; sys.path.pop(0); exec(compile(sys.stdin.read(), "<stdin>", "exec"))' "$GUARD_BIN_DIR" 2>/dev/null <<'PY'
```

`sys.path.pop(0)` is now literally on the same source line as `python3 -c '...'`, so
`test-no-distribution.py` case7's line-based regex scan
(`python3 (-c |- )` not followed on that line by `sys.path.pop(0)`) no longer flags
line 34 — the pop it used to miss (four statements down, inside the heredoc/`-c`
body) is right there on the launch line itself. The heredoc body drops its own
now-redundant `sys.path.pop(0)` and keeps `sys.path.insert(0, sys.argv[1])`
unchanged; `sys.argv[1]` is still `$GUARD_BIN_DIR`, unchanged, since args are still
passed positionally after the `-c` script string. `2>/dev/null` and the `if
_globs=$(...); then` status capture are both preserved verbatim in shape. No
behaviour changed: refusal text, fail-open semantics, and the two skip-reason
branches are untouched — only the launch mechanics moved.

## Observed counts (all run from worktree root, `env -u HARNESS_AGENT_TYPE`)

- `python3 tests/unit/test-no-distribution.py` → **ALL PASS, exit 0**. `case7_every_python_launch_isolates_the_cwd` green; `case7_the_scan_can_see_the_invocations` green with `safe_hits = 4` (was 3 pre-fix: `check-state.sh`, `bash-write-guard.sh`, `check-domain.sh`, now `dispatch-guard.sh` too — counted directly by re-running the scan's own predicate against `.claude/skills/harness/bin/*.sh`).
- `python3 tests/unit/test-harness-boundary.py` → **ALL PASS, exit 0**, 61 `PASS` lines (60+ ✓).
- `python3 tests/integration/test-dispatch-guard.py` → **69 of 69 cases passed, exit 0**.
- Plan T-02 `verify:` (cross-checked verbatim against `plan.yaml:324-325`, exact match) → **exit 0** (integration suite 69/69, then the piped grep for `eng-t01` succeeded).
- Red proof against the MAIN checkout's pre-change `dispatch-guard.sh` (md5 confirmed `ca904b2906ad8d44662db428cb2dbc89` before trusting the run) via `DISPATCH_GUARD_BIN=<main checkout path>`: **61 of 69 passed**, same 8 red cases observed: `case 18a: an inverted run-dir slug is refused`, `case 18a/b: stderr names the slug and the run-dir slug wording`, `case 18b: stderr names a compliant form ending in -eng`, `case 18g: the refusal strands no claim for the dispatched persona`, `case 21: stderr says the manifest declares no run-dir write grant`, `case 22: oddsquad-t01 is refused`, `case 22: the refusal names oddsquad in its compliant form`, `case 23: stderr says the run-dir vocabulary derivation failed`.
- `git diff --numstat` on the worktree: `dispatch-guard.sh` shows `8 5` (8 insertions, 5 deletions — comment reword plus the launch-line/body restructure). A second line, `feature.json` (`7 1`), is present but is orchestrator run-tracking (`cycles_used`, a new validator run entry) — not touched by this dispatch, confirmed by inspecting its diff content, which matches none of this task's edits.

## Scope confirmation

Only `.claude/skills/harness/bin/dispatch-guard.sh` was edited by this dispatch, and
only the comment block (lines 27–36) and the launch/heredoc block (lines 37–59) that
the assignment named. No test file, no plan.yaml, no team-config.yaml, no other
source file was touched.
