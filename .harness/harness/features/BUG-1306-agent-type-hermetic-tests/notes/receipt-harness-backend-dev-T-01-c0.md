# Receipt — harness-backend-dev — BUG-1306 T-01

## Pre-edit RED (self-measured, governed invocation, before any change)

Command: `HARNESS_AGENT_TYPE=harness-orchestrator python3 tests/integration/test-plan-merge.py`
run from a shell whose own `HARNESS_AGENT_TYPE=harness-backend-dev` (agent's own ambient value),
against the unmodified worktree file at HEAD `bfb77f23`.

```
RC=1
FAIL count=14
PASS count=265
```

FAIL lines observed:
```
FAIL  case11a: a newly created plan can be signed
FAIL  sign-approval exits 0
FAIL  sign-approval writes status: approved
FAIL  sign-approval writes approved_by
FAIL  sign-approval writes date, and it reloads as the string that was passed
FAIL  sign-approval leaves status: pending behind nowhere
FAIL  1157: sign-approval accepts repeatable --overrule
FAIL  1157: each ruling records finding, attribution, date, and full reason
FAIL  sign-approval inserts an absent approval mapping
FAIL  the inserted approval records the exact signature
FAIL  F-02 NEGATIVE CONTROL: an ordinary signer name stays unquoted
FAIL  F-02: a duplicate approved_by key in the base is REFUSED at exit 5 — caught by the stricter loader before signing, not after
FAIL  F-02: the refusal names the duplicate key, so a reader can act on it
FAIL test-plan-merge.py
```

This matches the orchestrator's independently recorded measurement at `c369fb1` (14 FAIL, exit 1),
confirming the red state is real and reproducible from a fresh agent shell, not inherited prose.

## Change made

`tests/integration/test-plan-merge.py` only:
1. After the `TEMPLATE_PLAN` constant (was line 33), added a comment block plus
   `os.environ.pop("HARNESS_AGENT_TYPE", None)` at module import time — before any case body
   and before the two raw Popen call sites.
2. Added one sentence to `run_verb`'s docstring stating the ambient `HARNESS_AGENT_TYPE` is
   already removed at module import, so `env=None` is hermetic on its own.

No other file touched. `.claude/skills/harness/bin/plan-merge.py` unchanged (D-03). No shared
`tests/integration/` helper, no second test file (D-01). No new test case (D-05).

## Post-edit verify — BOTH halves, run verbatim from the worktree toplevel

Full verify block (as declared in plan.yaml T-01 `verify:`, cross-checked byte-for-byte against
the dispatch text — they match) run as one shell invocation:

```
$ cd "$(git rev-parse --show-toplevel)"
$ out=$(HARNESS_AGENT_TYPE=harness-orchestrator python3 tests/integration/test-plan-merge.py)
$ rc=$?          # rc=0
$ printf '%s\n' "$out" | grep -c '^FAIL'   # 0
$ printf '%s\n' "$out" | grep -c '^PASS'   # 291
$ printf '%s\n' "$out" | grep -qF "PASS  a governed agent's sign-approval exits 10"   # found
$ printf '%s\n' "$out" | grep -qF "PASS  the signature actually lands"                # found
$ clean_out=$(env -u HARNESS_AGENT_TYPE python3 tests/integration/test-plan-merge.py)
$ clean_rc=$?    # clean_rc=0
$ printf '%s\n' "$clean_out" | grep -c '^FAIL'   # 0
$ printf '%s\n' "$clean_out" | grep -c '^PASS'   # 291
$ echo VERIFY-OK
VERIFY-OK
```

Overall shell exit status of the full verify block: **0**. Output printed: `VERIFY-OK`.

Summary counts:
| Half | rc | PASS | FAIL |
|---|---|---|---|
| Governed (`HARNESS_AGENT_TYPE=harness-orchestrator`) | 0 | 291 | 0 |
| Clean (`env -u HARNESS_AGENT_TYPE`) | 0 | 291 | 0 |

## Evidence for byte-identity of lines 1097-1140 (case_1103_ region)

`git status --porcelain` (worktree):
```
 M .harness/harness/features/BUG-1306-agent-type-hermetic-tests/plan.yaml
 M tests/integration/test-plan-merge.py
```
(The `plan.yaml` modification predates this dispatch — seeded by the lead/pm panel-close pass
before T-01 was picked up; not touched by this agent.)

`git diff --stat`:
```
 .../features/BUG-1306-agent-type-hermetic-tests/plan.yaml    |  4 ++--
 tests/integration/test-plan-merge.py                         | 12 +++++++++++-
 2 files changed, 13 insertions(+), 3 deletions(-)
```

`git diff -U0 -- tests/integration/test-plan-merge.py` hunk headers:
```
@@ -34,0 +35,8 @@ TEMPLATE_PLAN = os.path.join(HERE, "..", "templates", "plan.yaml")
@@ -141 +149,3 @@ def run_verb(*argv, env=None):
```

Both hunks are at original lines 34-35 and 141, well outside the 1097-1140 `case_1103_` region.
No hunk range intersects 1097-1140 — confirmed from the diff itself, not inferred from the green
suite.

## Operational note (self-correction, recorded for the record)

Mid-task the edit tool was first invoked with a workspace-relative path header while a duplicate
main-repo checkout also exists at `/Users/molchairuangutai/GitHub/harness`; the first two edits
landed in the main checkout instead of the worktree (main repo showed as modified, worktree showed
clean). Caught via `git status --porcelain` cross-check in both locations before running verify.
Reverted the main-repo file with `git -C /Users/molchairuangutai/GitHub/harness checkout --
tests/integration/test-plan-merge.py` (confirmed clean afterward), then redid both edits against
the fully-qualified worktree path. Final state: worktree carries the only change; main repo
checkout is untouched (`git status --porcelain` empty for that file there).
