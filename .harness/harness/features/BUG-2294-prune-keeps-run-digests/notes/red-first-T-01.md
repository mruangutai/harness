# Red-first evidence — BUG-2294 T-01 (SC-01, SC-02)

Test file: tests/unit/test-prune-run-evidence.py (sha256 f6cfe5ea1ed249a141d795ee9479c3e333aadcc72a551409e50be4523b3bad0b, uncommitted worktree state).
Subject override: PRUNE_RUN_EVIDENCE_BIN. The red subject is a byte copy of the base pruner placed beside the live bin (so sibling imports resolve), then deleted.

## RED — base pruner
Subject: git show c1724230c4d931ad46d433c8ba93df8cf312f898:.claude/skills/harness/bin/prune-run-evidence.py (sha256 cd58e0b94f18c24d2d90e60930cfb879c206f8e1b6594d32ea72c5a26e8688c0)

```
set +e; unset CLAUDE_PROJECT_DIR HARNESS_PROJECT_DIR HARNESS_AGENT_TYPE
B=.claude/skills/harness/bin/prune-run-evidence-base.py; git show c1724230:.claude/skills/harness/bin/prune-run-evidence.py > $B
PRUNE_RUN_EVIDENCE_BIN=$PWD/$B python3 tests/unit/test-prune-run-evidence.py; echo rc=$?; rm $B
```
Exit: 1. Seven assertion failures, no setup/import error. Every refusal case and both FEAT-2229 check-state-clean-before / empty-keep-exit-0 checks pass, so the fixture is sound. Full stdout+stderr:

```
FAIL - dry-run names exactly the ui/ lanes it would drop — no kept run, no run without ui/
       would remove runs/briefing-reconciliation-validator
would remove runs/build-c0-eng
would remove runs/distill-validator
would remove runs/fix-c3-eng
would remove runs/fix-c5-eng
would remove runs/plan-c0-product
would remove runs/validate-c1-validator
would remove runs/validate-c4-validator
would remove runs/validate-ship-validator
kept 3 of 12 run(s): fix-c5-validator, simplify-eng, validate-c2-validator

PASS - dry-run changes no bytes
PASS - dry-run leaves every run record byte-identical
PASS - keeps the ui/ of every PASS validator validate/fix run and any run bound to the pin; drops eng, failed, reconciliation, distill ui/
PASS - kept runs' UI evidence is byte-identical
FAIL - exit 0 and names the ui/ it removed
       removed runs/briefing-reconciliation-validator
removed runs/build-c0-eng
removed runs/distill-validator
removed runs/fix-c3-eng
removed runs/fix-c5-eng
removed runs/plan-c0-product
removed runs/validate-c1-validator
removed runs/validate-c4-validator
removed runs/validate-ship-validator
kept 3 of 12 run(s): fix-c5-validator, simplify-eng, validate-c2-validator

FAIL - every run directory, digest.md, state.yaml, .run-identity.json and non-UI sentinel survives prune
       dirs=['fix-c5-validator', 'simplify-eng', 'validate-c2-validator'] changed=['briefing-reconciliation-validator/.run-identity.json', 'briefing-reconciliation-validator/digest.md', 'briefing-reconciliation-validator/notes/sentinel.txt', 'briefing-reconciliation-validator/state.yaml', 'build-c0-eng/.run-identity.json', 'build-c0-eng/digest.md', 'build-c0-eng/notes/sentinel.txt', 'build-c0-eng/state.yaml', 'distill-validator/.run-identity.json', 'distill-validator/digest.md', 'distill-validator/note
PASS - a second prune succeeds and removes nothing more
FAIL - a repeated prune still leaves every run record byte-identical
       dirs=['fix-c5-validator', 'simplify-eng', 'validate-c2-validator'] changed=['briefing-reconciliation-validator/.run-identity.json', 'briefing-reconciliation-validator/digest.md', 'briefing-reconciliation-validator/notes/sentinel.txt', 'briefing-reconciliation-validator/state.yaml', 'build-c0-eng/.run-identity.json', 'build-c0-eng/digest.md', 'build-c0-eng/notes/sentinel.txt', 'build-c0-eng/state.yaml', 'distill-validator/.run-identity.json', 'distill-validator/digest.md', 'distill-validator/note
PASS - refuses the placeholder review_sha 'none' — nothing shipped, nothing pruned
PASS - refuses an empty review_sha
PASS - refuses a --keep that names no run directory
PASS - refuses an unknown feature
PASS - refuses a feature.json with a duplicate key through the canonical reader, pruning nothing (#1993)
PASS - an explicit --keep of an otherwise pruned run keeps its ui/
FAIL - an explicit --keep prune leaves every run record byte-identical
       dirs=['build-c0-eng', 'fix-c5-validator', 'simplify-eng', 'validate-c2-validator'] changed=['briefing-reconciliation-validator/.run-identity.json', 'briefing-reconciliation-validator/digest.md', 'briefing-reconciliation-validator/notes/sentinel.txt', 'briefing-reconciliation-validator/state.yaml', 'distill-validator/.run-identity.json', 'distill-validator/digest.md', 'distill-validator/notes/sentinel.txt', 'distill-validator/state.yaml', 'fix-c3-eng/.run-identity.json', 'fix-c3-eng/digest.md', '
PASS - FEAT-2229 shape: check-state is clean before prune
PASS - FEAT-2229 shape: an empty keep set still exits 0
FAIL - FEAT-2229 shape: every cycle_evidence digest survives prune at its recorded hash
       lost or changed: ['validate-c0-validator', 'validate-c1-validator', 'validate-c2-validator', 'validate-c3-validator', 'validate-c4-validator', 'validate-c5-validator', 'validate-c6-validator', 'validate-c7-validator', 'validate-c8-validator', 'validate-c9-validator']
FAIL - FEAT-2229 shape: check-state is still clean after prune
         VIOLATION  FEAT-9-thing: run validate-c0-validator cycle/refusal evidence: [Errno 2] No such file or directory: '/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmp0ohmhay0/.harness/harness/features/FEAT-9-thing/runs/validate-c0-validator/digest.md'
  VIOLATION  FEAT-9-thing: run validate-c1-validator cycle/refusal evidence: [Errno 2] No such file or directory: '/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmp0ohmhay0/.harness/harness/features/FEAT-9-thing/runs/validate-c1
7 failure(s)
rc=1
```

## GREEN — fixed pruner
Subject: .claude/skills/harness/bin/prune-run-evidence.py in the worktree (sha256 d3f2c38e2a54a8fa6c55fde020efcebaa5907a74733421acdc50ea975a332fe9)

```
set +e; unset CLAUDE_PROJECT_DIR HARNESS_PROJECT_DIR HARNESS_AGENT_TYPE
python3 tests/unit/test-prune-run-evidence.py; echo rc=$?
```
Exit: 0, about 0.7 s wall time, no FAIL lines. Full stdout+stderr:

```
PASS - dry-run names exactly the ui/ lanes it would drop — no kept run, no run without ui/
PASS - dry-run changes no bytes
PASS - dry-run leaves every run record byte-identical
PASS - keeps the ui/ of every PASS validator validate/fix run and any run bound to the pin; drops eng, failed, reconciliation, distill ui/
PASS - kept runs' UI evidence is byte-identical
PASS - exit 0 and names the ui/ it removed
PASS - every run directory, digest.md, state.yaml, .run-identity.json and non-UI sentinel survives prune
PASS - a second prune succeeds and removes nothing more
PASS - a repeated prune still leaves every run record byte-identical
PASS - refuses the placeholder review_sha 'none' — nothing shipped, nothing pruned
PASS - refuses an empty review_sha
PASS - refuses a --keep that names no run directory
PASS - refuses an unknown feature
PASS - refuses a feature.json with a duplicate key through the canonical reader, pruning nothing (#1993)
PASS - an explicit --keep of an otherwise pruned run keeps its ui/
PASS - an explicit --keep prune leaves every run record byte-identical
PASS - FEAT-2229 shape: check-state is clean before prune
PASS - FEAT-2229 shape: an empty keep set still exits 0
PASS - FEAT-2229 shape: every cycle_evidence digest survives prune at its recorded hash
PASS - FEAT-2229 shape: check-state is still clean after prune
all checks passed
rc=0
```

check-state invocation in the FEAT-2229-shaped case: real .claude/skills/harness/bin/check-state.py --feature FEAT-9-thing --only INV-7 (the cycle-evidence row), cwd at the temp fixture root, CLAUDE_PROJECT_DIR and HARNESS_PROJECT_DIR cleared from the inherited env and then set to that root. Unscoped repo-level rows (INV-27 readers, INV-31 hooks) report on fixture scaffolding unrelated to run evidence, so the run is narrowed to the row that reads cycle_evidence.

## c1 fix

Must-fix: SEC-01 (notes/must-fix-c1.md). Before the fix, a run entry that is a directory symlink entered `present`, and `_ui_targets` followed it. `rmtree(runs/<alias>/ui)` then deleted the link target's real ui/, whether that target was a kept run or a directory outside the feature. A `ui` that was itself a symlink was handed to `rmtree`. The fix: a run entry or a ui/ that is a symlink is never a target; prune prints `skipped runs/<id> (symlink)` or `skipped runs/<id>/ui (symlink)` and leaves it alone. The keep set, `--keep`, the refusals, the CLI and the return codes are unchanged.

Test file: tests/unit/test-prune-run-evidence.py (sha256 7f4274f8e272d112c29405dc4690fce6498bc99d8a6550ecdc8f85f1522cdd23). New checks in `symlink_cases`, which uses the fixture `linked_feature`: runs/build-alias -> validate-c2-validator (a kept run), runs/evil-alias -> <tmp>/outside-run (which holds ui/), and runs/ui-link-run/ui -> <tmp>/outside-ui/ui.
- `dry-run names no deletion target through a symlink`
- `dry-run leaves every link destination's ui/ byte-identical`
- `prune removes no ui/ through a symlink and still prunes the real run`
- `prune names each symlink it skipped`
- `a kept run, an outside run and an outside ui/ reached through links keep their ui/ bytes`

### RED — pruner pinned at 70981edd
Subject: git show 70981edd6f9f110965a0148b4490ed2673d262dc:.claude/skills/harness/bin/prune-run-evidence.py (sha256 d3f2c38e2a54a8fa6c55fde020efcebaa5907a74733421acdc50ea975a332fe9). It was copied to prune-run-evidence-c1base.py beside the live bin, so the sibling imports resolve, and deleted after the run.

```
set +e; unset CLAUDE_PROJECT_DIR HARNESS_PROJECT_DIR HARNESS_AGENT_TYPE
B=.claude/skills/harness/bin/prune-run-evidence-c1base.py; git show 70981edd:.claude/skills/harness/bin/prune-run-evidence.py > $B
PRUNE_RUN_EVIDENCE_BIN=$PWD/$B python3 tests/unit/test-prune-run-evidence.py; echo rc=$?; rm $B
```
Exit: 1, with 4 assertion failures and no setup or import error. The 20 earlier checks pass against this subject. The dry run printed `would remove` for build-alias, evil-alias and ui-link-run. During the prune, rmtree on the ui/ symlink raised OSError (that traceback is in the prune check's output). The kept run's ui/ and the outside run's ui/ were deleted (`[[], [], [...]]`). Full stdout and stderr:

```
PASS - dry-run names exactly the ui/ lanes it would drop — no kept run, no run without ui/
PASS - dry-run changes no bytes
PASS - dry-run leaves every run record byte-identical
PASS - keeps the ui/ of every PASS validator validate/fix run and any run bound to the pin; drops eng, failed, reconciliation, distill ui/
PASS - kept runs' UI evidence is byte-identical
PASS - exit 0 and names the ui/ it removed
PASS - every run directory, digest.md, state.yaml, .run-identity.json and non-UI sentinel survives prune
PASS - a second prune succeeds and removes nothing more
PASS - a repeated prune still leaves every run record byte-identical
PASS - refuses the placeholder review_sha 'none' — nothing shipped, nothing pruned
PASS - refuses an empty review_sha
PASS - refuses a --keep that names no run directory
PASS - refuses an unknown feature
PASS - refuses a feature.json with a duplicate key through the canonical reader, pruning nothing (#1993)
PASS - an explicit --keep of an otherwise pruned run keeps its ui/
PASS - an explicit --keep prune leaves every run record byte-identical
PASS - FEAT-2229 shape: check-state is clean before prune
PASS - FEAT-2229 shape: an empty keep set still exits 0
PASS - FEAT-2229 shape: every cycle_evidence digest survives prune at its recorded hash
PASS - FEAT-2229 shape: check-state is still clean after prune
FAIL - dry-run names no deletion target through a symlink
       would remove runs/build-alias/ui
would remove runs/build-c0-eng/ui
would remove runs/evil-alias/ui
would remove runs/ui-link-run/ui
kept 1 of 5 run(s): validate-c2-validator

PASS - dry-run leaves every link destination's ui/ byte-identical
FAIL - prune removes no ui/ through a symlink and still prunes the real run
       removed runs/build-alias/ui
removed runs/build-c0-eng/ui
removed runs/evil-alias/ui
removed runs/ui-link-run/ui
Traceback (most recent call last):
  File "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests/.claude/skills/harness/bin/prune-run-evidence-c1base.py", line 149, in <module>
    sys.exit(main())
             ~~~~^^
  File "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2294-prune-keeps-run-digests/.claude/skills/harne
FAIL - prune names each symlink it skipped
       removed runs/build-alias/ui
removed runs/build-c0-eng/ui
removed runs/evil-alias/ui
removed runs/ui-link-run/ui

FAIL - a kept run, an outside run and an outside ui/ reached through links keep their ui/ bytes
       [[], [], ['evidence/shot.webp', 'results.json']]
4 failure(s)
rc=1
```

### GREEN — fixed pruner
Subject: the worktree's .claude/skills/harness/bin/prune-run-evidence.py (sha256 3ce3bb40d97f8cb7c3274826f6cc4f3db653f38eadca8de76a0411a5aef02af9).

```
set +e; unset CLAUDE_PROJECT_DIR HARNESS_PROJECT_DIR HARNESS_AGENT_TYPE
python3 tests/unit/test-prune-run-evidence.py; echo rc=$?
```
Exit: 0, all 25 checks PASS, no FAIL lines. Full stdout and stderr:

```
PASS - dry-run names exactly the ui/ lanes it would drop — no kept run, no run without ui/
PASS - dry-run changes no bytes
PASS - dry-run leaves every run record byte-identical
PASS - keeps the ui/ of every PASS validator validate/fix run and any run bound to the pin; drops eng, failed, reconciliation, distill ui/
PASS - kept runs' UI evidence is byte-identical
PASS - exit 0 and names the ui/ it removed
PASS - every run directory, digest.md, state.yaml, .run-identity.json and non-UI sentinel survives prune
PASS - a second prune succeeds and removes nothing more
PASS - a repeated prune still leaves every run record byte-identical
PASS - refuses the placeholder review_sha 'none' — nothing shipped, nothing pruned
PASS - refuses an empty review_sha
PASS - refuses a --keep that names no run directory
PASS - refuses an unknown feature
PASS - refuses a feature.json with a duplicate key through the canonical reader, pruning nothing (#1993)
PASS - an explicit --keep of an otherwise pruned run keeps its ui/
PASS - an explicit --keep prune leaves every run record byte-identical
PASS - FEAT-2229 shape: check-state is clean before prune
PASS - FEAT-2229 shape: an empty keep set still exits 0
PASS - FEAT-2229 shape: every cycle_evidence digest survives prune at its recorded hash
PASS - FEAT-2229 shape: check-state is still clean after prune
PASS - dry-run names no deletion target through a symlink
PASS - dry-run leaves every link destination's ui/ byte-identical
PASS - prune removes no ui/ through a symlink and still prunes the real run
PASS - prune names each symlink it skipped
PASS - a kept run, an outside run and an outside ui/ reached through links keep their ui/ bytes
all checks passed
rc=0
```
