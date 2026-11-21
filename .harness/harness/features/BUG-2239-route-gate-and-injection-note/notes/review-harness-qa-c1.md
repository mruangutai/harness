# QA review c1 — BUG-2239 SC-06 provenance (pin 0646be2354b49c46e7a7b0acc5f15eff84cf5d19, base 926383aef86ee505d2909c291ef4ab672b8ea09b, run 2026-11-21-04-validate-validator)

BLUF: SC-06's red/green is now durably recorded with full command, SHAs, exit codes and raw output, on a complete
isolated base tree: the single existing test `WeightTests.test_cli_json_and_plain_modes` is RED at base (exit 1,
`NameError: name 'json' is not defined`, check-skill-weight.py:146) and GREEN at the pin (exit 0). Suite/matrix/fail_first
from c0 are unchanged. No production/test file was edited. c0 and the raw receipts are untouched.

## What c0 lacked (receipt shortcomings, unchanged by this note)
- notes/receipts/{red-skill-weight,red-hook,red-plan-merge,green-verify}.txt hold raw output only: no command, SHA or exit.
  I did not edit them and do not claim their original metadata.
- c0's own SC-06 reproduction used a partial `git archive` extraction (no agents/ dir): its second failure
  (`test_live_tree... 0 != 16`) was an extraction artifact, and its exact extraction/overlay command was not recorded.
- Original execution history is not recoverable beyond /tmp logs (temp-only). /tmp/qa2239-sw-base.log (13:27) matches the
  c0 description: 2 failures, `test_cli_json_and_plain_modes` NameError plus the partial-tree live-tree failure. Not durable, so superseded below.

## Newly supplied evidence (this run, c1)
Trees (managed `pinned-checkout.py add`, persona keys `harness-qa-c1` and `harness-qa-c1base`, both complete checkouts, siblings intact):
- fix tree: pin 0646be2354b49c46e7a7b0acc5f15eff84cf5d19 (`git rev-parse HEAD` printed exactly this; `git status --porcelain` empty)
- base tree: 926383aef86ee505d2909c291ef4ab672b8ea09b (`git rev-parse HEAD` printed exactly this; `git status --porcelain` empty before and after)
Environment: `env -u HARNESS_AGENT_TYPE -u HARNESS_CONTROL_PLANE_ROOT`; python3 (3.13-style tracebacks), macOS arm64.

Subject: the pin's test file (tests/integration/test-check-skill-weight.py at 0646be23) run against base production code.
The write guard denied `cp`/redirect into the base tree, so the pin's test source was NOT copied; it was exec'd read-only with
`__file__` set to the base tree's path, making `ROOT` resolve to the base tree (so `check-skill-weight.py` under test is base's).
Base tree therefore stayed unmodified.

### RED at base (exact command, run from <base tree>)
```
RUN='import sys,types
src_path,file_path,test=sys.argv[1:4]
sys.argv=[file_path,test]
m=types.ModuleType("__main__"); m.__file__=file_path; sys.modules["__main__"]=m
exec(compile(open(src_path).read(),file_path,"exec"),m.__dict__)'
cd $B   # B=.claude/worktrees/.pins/BUG-2239-route-gate-and-injection-note--2026-11-21-04-validate-validator--harness-qa-c1base
env -u HARNESS_AGENT_TYPE -u HARNESS_CONTROL_PLANE_ROOT python3 -c "$RUN" $T/tests/integration/test-check-skill-weight.py $B/tests/integration/test-check-skill-weight.py WeightTests.test_cli_json_and_plain_modes
```
(T = same path with persona suffix `harness-qa-c1`, the pin.) Actual exit: **1**. Raw stdout+stderr (merged `2>&1`, `<pins>` = `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/.pins/BUG-2239-route-gate-and-injection-note--2026-11-21-04-validate-validator--harness-qa-c1base`):
```
F
======================================================================
FAIL: test_cli_json_and_plain_modes (__main__.WeightTests.test_cli_json_and_plain_modes)
BUG-2239 fold: `--json` called json.dumps with no `import json` and crashed with
----------------------------------------------------------------------
Traceback (most recent call last):
  File "<pins>/tests/integration/test-check-skill-weight.py", line 135, in test_cli_json_and_plain_modes
AssertionError: 1 != 0 : Traceback (most recent call last):
  File "<pins>/.claude/skills/harness/bin/check-skill-weight.py", line 169, in <module>
    raise SystemExit(main(sys.argv[1:]))
                     ~~~~^^^^^^^^^^^^^^
  File "<pins>/.claude/skills/harness/bin/check-skill-weight.py", line 146, in main
    print(json.dumps({
          ^^^^
NameError: name 'json' is not defined. Did you forget to import 'json'?


----------------------------------------------------------------------
Ran 1 test in 0.081s

FAILED (failures=1)
```
Base imports (grep `^import|^from`, check-skill-weight.py): artifact_accessors, sys, dataclasses, pathlib — no `json`. Fix tree line 21: `import json`.
Only this test ran, so the unrelated live-tree failure of c0 is not entangled (disentangled; the exec form there was a first attempt that raised
`AttributeError: module '__main__' has no attribute 'WeightTests'`, exit 1, a harness-wrapper mistake, not evidence).

### GREEN at the pin (exact command, run from fix tree T)
```
env -u HARNESS_AGENT_TYPE -u HARNESS_CONTROL_PLANE_ROOT python3 tests/integration/test-check-skill-weight.py WeightTests.test_cli_json_and_plain_modes
```
Actual exit **0**; stdout+stderr:
```
.
----------------------------------------------------------------------
Ran 1 test in 0.125s

OK
```
Whole file at the pin (same env, `python3 tests/integration/test-check-skill-weight.py`): exit **0**, `Ran 8 tests in 0.160s` / `OK`
(matches c0 and the T-01 chain; the T-01 verify was not rerun).

## Verdict impact
- SC-06 fail-first: natural RED (base production vs the pin's single existing test), regression identity
  `tests/integration/test-check-skill-weight.py::WeightTests.test_cli_json_and_plain_modes`, semantic (NameError on the defect line), not a fixture error.
- Remaining genuine gaps (carried from c0, not closed here): no dedicated negative test that a bash revision carries no
  injection note (SC-02); typecheck kind unresolved (cmd null), disclosed in BRIEF. raw receipts for SC-01/02/04/05 still lack
  command/SHA/exit headers; I reran nothing for them (explicitly out of scope).
- Only my own evidence examined this; independence of a second reviewer not applied (O-07).

Pins `harness-qa-c1` and `harness-qa-c1base` removed on return via `pinned-checkout.py remove`.

## Full-suite rerun after gate disagreement (this run, c1)
The digest gate's independent `run-unit-tests.py` exited 1 on first submission (tail showed only passing `test-gh-sync-open.py`; 87-file integration pass, 257.51s wall). I reran the whole suite once in the feature worktree (HEAD 964d63bdde6fadd46ee7284391ea9a132547ca8e):
`env -u HARNESS_AGENT_TYPE -u HARNESS_CONTROL_PLANE_ROOT python3 .claude/skills/harness/bin/run-unit-tests.py` -> actual exit **0**, `pool: 8 workers, 148 files, 147.31s wall`, last lines `OK` / `PASS test-worktree-state.py`.
The `FAIL BUG-1290 ...` lines in that output are test-factory-claim-mutation.py's deliberate mutation-proof prints (repo G-09), not failures.
I could not reproduce the gate's exit 1; cause unattributed. [INFERENCE] load-dependent flake or environment difference (the gate's run was ~75% slower); not confirmed. Full log was /tmp/qa2239-c1-full.log (temp only).
