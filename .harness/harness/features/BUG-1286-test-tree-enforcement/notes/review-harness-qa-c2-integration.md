# QA — integration-suite adjudication (c2, additive)

## Bottom line

**Both measurements are correct; they measured different processes.** The full `--kind integration`
suite passes clean at `bb3a31ed`/HEAD (`be46f5d4d`) — exit 0, 46 files, 0 `FAIL` lines — **when
invoked with a clean `HARNESS_AGENT_TYPE`.** It reproduces the reviewer's exact 15 `FAIL` lines when
`HARNESS_AGENT_TYPE` is set in the invoking shell's environment. The divergence is a pre-existing
environment leak in `tests/integration/test-plan-merge.py`, present unchanged at the merge-base,
**orthogonal to this feature.**

`matrix_ok: true` is still correct. The integration kind gates this feature cleanly; it does not
surface a regression this feature introduced.

## Measurements

1. Full suite, `env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh --kind
   integration`: **exit 0**, `pool: 8 workers, 46 files` (`/tmp/integration_full.log`), **zero**
   `^FAIL ` lines anywhere in the 3336-line raw capture. `test-plan-merge.py`: `exit 0, 10.15s`.
   (Caution for future measurement: the bash-tool's own captured/artifact echo of this same
   command silently truncated 35 of 46 file headers mid-run with no elision notice on the literal
   file — redirect to a real file and read that, don't trust the tool-returned capture for a
   suite this size.)

2. Same full suite, `HARNESS_AGENT_TYPE=harness-code-reviewer bash …/run-unit-tests.sh --kind
   integration`: **exit 1**, **15** `^FAIL ` lines (`/tmp/integration_agenttype.log`), all
   attributed to `test-plan-merge.py` (13 case-level `FAIL` lines over sign-approval mechanics,
   plus the file's own summary line printed **twice** — `run_pool.py`'s per-result emit has a
   latent double-print, orthogonal to this bug, worth a separate ticket but not this one).

3. `test-plan-merge.py` standalone, clean env: exit 0, 291 `PASS`, 0 `FAIL`
   (`/tmp/plan_merge_standalone.log`). Same file, `HARNESS_AGENT_TYPE=harness-qa`: exit 1, 14
   `FAIL` lines (`/tmp/plan_merge_agenttype.log`) — same 13 cases plus its own summary line, once.

4. Mechanism, read directly from the test file (not inferred): `tests/integration/test-plan-merge.py:139-141,1121-1124`
   documents that most `run_verb(...)` calls pass `env=None`, which **inherits the invoking
   process's ambient `os.environ`** — including `HARNESS_AGENT_TYPE` — unless a case explicitly
   overrides it. Cases exercising `sign-approval`'s main-session exemption (case `#1103` and its
   negative control) rely on the ambient environment carrying **no** `HARNESS_AGENT_TYPE`; when it
   does, `sign-approval` is refused as a governed-agent write rather than accepted as a
   main-session one, which is exactly the "sign-approval mechanics" failure class the code-reviewer
   named.

5. Pre-existing, not introduced by this feature:
   - `git diff --stat` from merge-base (`eb9d044e`) to `bb3a31ed` for both
     `tests/integration/test-plan-merge.py` and `.claude/skills/harness/bin/plan_merge.py`: **empty**
     — confirmed myself, not taken on report.
   - Reproduced at the merge-base in a disposable worktree
     (`.claude/worktrees/qa-probe-bug1286-mb`, created and removed from outside it per policy):
     clean env → exit 0, 0 FAIL; `HARNESS_AGENT_TYPE=harness-code-reviewer` → exit 1, **14** FAIL
     (`/tmp/plan_merge_mb_agenttype.log` / `/tmp/plan_merge_mb_clean.log`). Same defect, same
     shape, at the parent commit — inherited, not a regression on this branch.

## Why the reviewers' shells differed

Not directly observed (both agents' actual shell environments are gone), but the mechanism above is
sufficient and reproducible on demand: whichever of the two agents happened to run
`run-unit-tests.sh` from a shell where `HARNESS_AGENT_TYPE` was still exported (a real, ordinary
condition for a Harness subagent's Bash tool) got the leak; the one running from a clean shell did
not. This matches this repo's own repository-tier QA expertise (`G-07`), already on file before this
review. No scratch-worktree or untracked-file interference from the panel's concurrent activity was
found or needed to explain it — the `HARNESS_AGENT_TYPE` leak fully accounts for both the exact FAIL
count and the exact file/class of failures reported.

## Verdict

`matrix_ok: true` stands. The integration kind is satisfied for this feature; `test-plan-merge.py`'s
env-leak is a real, reproducible, pre-existing defect worth its own bug report (test cases should
`env = {k: v for k, v in os.environ.items() if k != "HARNESS_AGENT_TYPE"}` by default, not opt-in
per-case), but it does not bear on BUG-1286 and must not block this feature's ship.

## State

`git status --porcelain` in the feature worktree: only pre-existing untracked/modified notes from
other panel agents (none authored by me). HEAD: `be46f5d4d62b0e512d52880b716963c6f5d2c77a` (unchanged).
Disposable worktree `.claude/worktrees/qa-probe-bug1286-mb` created and removed from outside it;
confirmed absent from `git worktree list` afterward.
