# Receipt — harness-backend-dev — BUG-201 SIMPLIFY fold-in (altitude)

## What
Applied the single permitted SIMPLIFY finding from the four-reader pass over the built BUG-201
fix: `refuse()` (`.claude/skills/harness/bin/gh-sync.py:164`) now takes an optional `stream`
parameter, resolved to `sys.stdout` inside the call (not as a bound default — a default bound
at def time would capture whatever `sys.stdout` was at import, breaking under
`contextlib.redirect_stdout`). `_projected_for`'s inline `print(..., file=sys.stderr);
sys.exit(2)` for a plan that fails to load is now `refuse(msg, stream=sys.stderr)`
(`gh-sync.py:1174`), the same shape its sibling `FleetError` branch already uses.

No other `refuse(...)` caller changed — all five other call sites keep the implicit stdout
default.

## Skipped, one-fix ceiling
The reader pass's separate finding — `gh_issue_types.UnknownWorkNature` +
`missing_types`/`refusal_text` handling duplicated verbatim at two call sites
(`gh-sync.py:969-971,976-977` and `:1652-1654,1659-1660`) — was NOT folded in. Recorded here
for the build digest to pick up in a future pass.

## TDD evidence
Added a unit-level RED test in `tests/integration/test-gh-sync.py` (after the existing
`_ghs` module import, appended near EOF) that calls `_ghs.refuse(...)` and
`_ghs.refuse(..., stream=sys.stderr)` directly under `contextlib.redirect_stdout/stderr`,
via a `_call_refuse` wrapper that turns any raise (SystemExit or an unexpected TypeError) into
a comparable tuple rather than letting it abort the rest of the suite.

RED (pre-fix), captured verbatim:
```
ok    refuse() default: still exits 2, unaffected by the new parameter
ok    refuse() default: message on stdout, exactly as before
ok    refuse() default: nothing written to stderr
FAIL  refuse(stream=sys.stderr): exits 2
      ('typeerror', "refuse() got an unexpected keyword argument 'stream'")
FAIL  refuse(stream=sys.stderr): message on stderr, not stdout
      ('', '')
```

GREEN (post-fix): all 5 of the new checks pass; full suite 318 checks, 0 failures, exit 0.

## Verify run
```
$ python3 tests/integration/test-gh-sync.py
... (all 318 checks) ...
$ echo $?
0
```
No `FAIL` lines in the output. Cases (d)-(g) (BUG-201's own dangling-plan integration checks,
which exercise `_projected_for`'s stderr line end-to-end through `start-task`/`status`) are
byte-identical to their pre-refactor pass — the fold-in changed no observable behavior.

## Contract preserved
- `refuse(msg)` (no `stream=`): message on stdout, exit 2 — unchanged for all 5 existing
  callers.
- `_projected_for`'s dangling-plan refusal: one stderr line naming both task ids, exit 2, no
  traceback — unchanged (cases (d), (f) in `test-gh-sync.py`).

## Scope
Files touched: `.claude/skills/harness/bin/gh-sync.py` (hardlinked twin at
`.agents/skills/harness/bin/gh-sync.py` updated automatically — same inode),
`tests/integration/test-gh-sync.py`. No formatters/linters/project-wide suites run, per
assignment.
