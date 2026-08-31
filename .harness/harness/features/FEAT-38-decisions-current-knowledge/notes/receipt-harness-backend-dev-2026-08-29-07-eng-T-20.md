# Receipt — harness-backend-dev — T-20 — 2026-08-29-07-eng

## Task

Build `.claude/skills/harness/bin/check-decision-claims.py` (the executable-claims
checker) and `.claude/skills/harness/bin/test-check-decision-claims.py` (its test).
Verify string cross-checked against `plan.yaml` T-20 lines 1375-1381 — matches the
dispatch verbatim, no mismatch.

## Verify command (run verbatim from the worktree root)

```
cd "$(git rev-parse --show-toplevel)"
python3 .claude/skills/harness/bin/test-check-decision-claims.py > /tmp/t20.out 2>&1
rc=$?
grep '^FAIL' /tmp/t20.out && exit 1
test "$(grep -c '^ok - ' /tmp/t20.out)" -ge 5 || exit 1
exit $rc
```

**Exit status: 0**

### Verbatim tail of /tmp/t20.out

```
ok - test_matching_claim_exits_zero
ok - test_mismatching_claim_reports_heading_and_exits_one
ok - test_disallowed_first_token_is_refused_and_exits_one
ok - test_zero_markers_exits_zero_and_says_so
ok - test_nonexistent_path_in_command_is_a_failure_not_a_crash
ok - test_unreadable_target_exits_two_not_zero
ok - test_checker_source_never_uses_shell_true
```

7 `ok - ` lines (≥5 required), 0 `FAIL` lines.

## Live run against the default target

```
$ python3 .claude/skills/harness/bin/check-decision-claims.py
examined 0 claim(s), 0 failed
$ echo $?
0
```

Marker count observed: **0**. Expected and correct at this point in the feature —
T-21 (dependent on this task) is the one that adds claim markers to DECISIONS.md;
none exist yet. The visible "examined 0 claim(s)" line is what makes this a
verified zero-marker pass rather than an indistinguishable silent no-op, per the
task's own zero-marker requirement.

## Safety-boundary evidence: no `shell=True` in either new file

```
$ grep -n "shell=True" .claude/skills/harness/bin/check-decision-claims.py
(no output, grep exit 1 — zero matches)

$ grep -n "shell=True" .claude/skills/harness/bin/test-check-decision-claims.py
209:        if "shell=True" in src:
210:            print(f"FAIL - {name}: checker source contains shell=True")
```

The checker itself (`check-decision-claims.py`) contains the string `shell=True`
nowhere — including its docstring, which was deliberately reworded during
development to avoid the self-referential trap (G-06: a script whose own source is
grep-scanned for a forbidden identifier must not spell that identifier even in
prose explaining the prohibition). The two hits in the test file are the
assertion's own literal — `test_checker_source_never_uses_shell_true` reads
`CHECKER`'s source and greps it for `"shell=True"`, so those two lines are the
check, not a call site. Neither new file invokes `subprocess.run` with
`shell=True` anywhere; `check-decision-claims.py`'s only `subprocess.run` call
passes a `shlex.split` argv list with no `shell` keyword at all.

## Design notes

- Marker grammar: `<!-- claim: <command> :: <expected> -->` on its own line,
  parsed by `CLAIM_RE`; separator is ` :: ` per the decision entry / T-20 intent.
- Default `--file` resolution mirrors `gen-decisions-index.py` and
  `check-decision-anchors.py` exactly: `harness_boundary.resolve_root(_BIN_DIR)` +
  the same `DOCS_DIR`/relative-path constants, resolved at call time. An explicit
  `--file` (as every test case passes) bypasses that resolution and is used as
  given — matching how `check-decision-anchors.py`'s own tests exercise it.
- DEC-heading attribution: tracks the most recent `^##\s+(DEC-\d+.*)$` line seen
  before each marker (same heading shape `gen-decisions-index.py`'s `HEADING_RE`
  uses), reported verbatim in failure/refusal lines.
- Safety boundary: `shlex.split`, then `subprocess.run` on the resulting argv list
  (never a shell string); first token must be exactly `git` or `grep` or the claim
  is REFUSED (reported, exit-1-contributing, never skipped); 10s timeout per
  command, timeout counts as failure; a missing path in the command's argv is a
  normal nonzero-exit / no-match failure, not a crash (git/grep themselves handle
  the missing-path case and this checker just surfaces their result).
- Exit codes: 0 only when every marker examined passed (including the 0-marker
  case); 1 on any failed/refused claim; 2 for a usage error or an unreadable
  `--file` target (open() OSError, or `harness_boundary.resolve_root` raising
  `ValueError` when no default target could be found).

## Files touched

- `.claude/skills/harness/bin/check-decision-claims.py` (new)
- `.claude/skills/harness/bin/test-check-decision-claims.py` (new)

Did not touch `run-unit-tests.sh`, `.harness/harness.json`, or `DECISIONS.md`, per
the task's stated non-goals (T-18/T-19/T-21 respectively).
