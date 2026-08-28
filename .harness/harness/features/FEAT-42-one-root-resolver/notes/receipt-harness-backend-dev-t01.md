# Receipt — harness-backend-dev — T-01

Add MARKER and the three resolver functions (`root_from_script`, `resolve_root`,
`root_above`) to `harness_boundary.py`, with `test-harness-boundary.py` written first.

## RED — verbatim stdout+stderr, run against the UNTOUCHED `harness_boundary.py` (pre-edit)

Command: `python3 .claude/skills/harness/bin/test-harness-boundary.py`

```
FAIL case_marker_constant_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'MARKER'")
FAIL case_root_from_script_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'root_from_script'")
FAIL case_resolve_root_strict_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'resolve_root'")
FAIL case_root_above_did_not_crash raised AttributeError("module '_hb_under_test' has no attribute 'root_above'")

4 FAILURE(S): ['case_marker_constant_did_not_crash', 'case_root_from_script_did_not_crash', 'case_resolve_root_strict_did_not_crash', 'case_root_above_did_not_crash']
EXIT=1
```

Note on the FAIL-line naming: `resolve_root_strict` in the task's required token list maps to
the `case_resolve_root_strict` case (function under test is `resolve_root`, called with
`strict=True`) — the token appears in the case name, satisfying the verify's grep. The four
tokens `root_from_script`, `resolve_root_strict`, `root_above`, `marker_constant` each appear
in a FAIL line above.

Each case is invoked through a `run_case()` wrapper that catches any exception and reports it
as a named FAIL rather than letting one crash abort the whole suite silently (an unguarded
`AttributeError` from case 1 would otherwise have skipped cases 2-4 entirely and produced only
one FAIL line instead of the required four).

## GREEN — after implementing MARKER, `root_from_script`, `resolve_root`, `root_above`

Command: `python3 .claude/skills/harness/bin/test-harness-boundary.py`

```
harness_boundary: discarding HARNESS_PROJECT_DIR='/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpgt68ju_c' — it does not carry .harness/team-config.yaml. Falling back to the derived root '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmprl4ilnz7'.
PASS marker_constant_exact_value
PASS root_from_script_four_levels_up_no_marker
PASS root_from_script_unchanged_when_marker_exists
PASS resolve_root_strict_override_with_marker_honoured
PASS resolve_root_strict_bad_override_falls_through_to_derived
PASS resolve_root_strict_bad_override_reported_on_stderr
PASS resolve_root_strict_neither_carries_marker_raises
PASS root_above_finds_marker_walking_up
PASS root_above_bare_dot_harness_does_not_satisfy
PASS root_above_nothing_above_returns_none

ALL PASS
EXIT=0
```

## Imports, post-edit

```
$ grep -nE '^(import|from) ' .claude/skills/harness/bin/harness_boundary.py
12:from `WORKTREES_SEGMENT` rather than spelled again.
19:import os
20:import re
21:import sys
```

Line 12 is a docstring sentence, not a real import statement (the grep pattern matches
`from ` at line start inside prose). The only real imports remain `os`, `re`, `sys`.

## VERIFY — verbatim stdout+stderr

Command form used — the task's `verify:` block, `plan.yaml:123-145`, saved verbatim to
`/tmp/f42-t01-verify.sh` and run with `bash /tmp/f42-t01-verify.sh`:

```
cd "$(git rev-parse --show-toplevel)"
B=.claude/skills/harness/bin
N=.harness/harness/features/FEAT-42-one-root-resolver/notes
python3 $B/test-harness-boundary.py || exit 1
for c in root_from_script resolve_root_strict root_above marker_constant; do
  grep -rqE "FAIL.*$c" $N/receipt-*.md || { echo "SC-10: no red receipt line for $c"; exit 1; }
done
git show 3952814:$B/harness_boundary.py > /tmp/f42-hb-old.py
python3 - <<'P'
import ast, re, sys
def fn(p, n):
    t = ast.parse(open(p).read())
    return next((ast.unparse(x) for x in ast.walk(t)
                 if isinstance(x, ast.FunctionDef) and x.name == n), None)
new = ".claude/skills/harness/bin/harness_boundary.py"
s = open(new).read()
ok = re.search(r'MARKER\s*=\s*os\.path\.join\(\s*"\.harness"\s*,\s*"team-config\.yaml"\s*\)', s)
ok = ok and all(fn(new, f) for f in ("root_from_script", "resolve_root", "root_above"))
ok = ok and fn("/tmp/f42-hb-old.py", "worktree_owner") == fn(new, "worktree_owner")
sys.exit(0 if ok else 1)
P
echo T-01-OK
```

Verbatim stdout+stderr, unedited:

```
harness_boundary: discarding HARNESS_PROJECT_DIR='/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpgm4wo9k9' — it does not carry .harness/team-config.yaml. Falling back to the derived root '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpeqgh66f3'.
PASS marker_constant_exact_value
PASS root_from_script_four_levels_up_no_marker
PASS root_from_script_unchanged_when_marker_exists
PASS resolve_root_strict_override_with_marker_honoured
PASS resolve_root_strict_bad_override_falls_through_to_derived
PASS resolve_root_strict_bad_override_reported_on_stderr
PASS resolve_root_strict_neither_carries_marker_raises
PASS root_above_finds_marker_walking_up
PASS root_above_bare_dot_harness_does_not_satisfy
PASS root_above_nothing_above_returns_none

ALL PASS
T-01-OK
```

Observed exit status: `0` (confirmed via `echo "EXIT_STATUS=$?"` immediately after the run, which
printed `EXIT_STATUS=0`).

## Notes for the reviewer / T-03

- `worktree_owner` is untouched — no lines inside its body were edited.
- `run-unit-tests.sh` was not touched, per the task's own instruction; that file's drift
  detector currently does not know about `test-harness-boundary.py` and T-03 owns wiring it
  in.
- `resolve_root`'s `strict` parameter defaults to `True`, matching the intent's signature
  `resolve_root(bin_dir, strict=True)`.
