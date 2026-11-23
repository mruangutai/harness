# QA review — BUG-2399 validate c2 (gate-only), pin 74e6896c6113f916efd9c5ceb24a7d60e7c5c0cd

**BLUF: PASS.** Unit kind satisfied at the pin (65 files, exit 0). Old must_fix MF-1 is resolved; MF-2 is closed by the operator ruling. SC-01 and SC-02 have retained natural-RED evidence bound by hash to the pinned test and base pruners.

## Phase 1 (BRIEF + plan only)
- SC-01: index assertions on real git repos with ignored runs/ (nested qa/ staged, ui/ and unrecorded runs not, symlink isolation, dry-run immutability, repeat prune), and a retrieval failure on an unreadable recorded subtree.
- SC-02: exit 2 naming every missing cycle_evidence path, no mutation on refusal, complete evidence passes.
- SC-03 is `inspection`, not gated here. The removal clause is ruled vacuously satisfied (`notes/answers-2026-11-23-c1-ruling.md`).

## Matrix
T-01 is `bugfix`. harness.json: `always: []`. `unit` fires on `touches_runtime_code` (true, `prune-run-evidence.py`). `integration` needs `fix_confined_to_tests_and_contract_docs` (false). `__bug_class__` is a placeholder that never fires (repo G-08). Required: **unit only**. `matrix_ok: true`.

## Pin / HEAD relation
Managed pin `.claude/worktrees/.pins/BUG-2399-run-records-staged-at-ship--2026-11-23-03-fix-validator--harness-qa`, HEAD = 74e6896c, `git status --porcelain` clean. Feature worktree HEAD is 5a1becd6; 74e6896c is its ancestor, and `git diff --name-only 74e6896c HEAD` lists only feature.json and plan.yaml under the feature directory. No production or test byte differs between pin and HEAD. Only the pin was tested.

## Runner receipt (DEC-255)
Command (HARNESS_AGENT_TYPE, CLAUDE_PROJECT_DIR, HARNESS_PROJECT_DIR unset), run once from the pin:
`python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <feature>/runs/2026-11-23-03-fix-validator/qa/manifest-unit.json`
Result: exit 0; `pool: 8 workers, 65 files, 47.53s wall`. The manifest holds `tested_commit` 74e6896c…, `selected_files` 65, `completed_files` 65, `runner_exit` 0. `tests/unit/test-prune-run-evidence.py` is a member, returncode 0 (P-14). Full output: `/tmp/qa-b2399-c2-unit.log` (2501 lines; the write guard refused copies into notes). The receipt was not edited.
Installed-vs-candidate: this diff changes `prune-run-evidence.py` and the ship command, not an enforcing hook. The receipt is the candidate's own run.

## T-01 verify, verbatim (distinct from the production runner)
Both ran at the pin. Task verify is the task's own two-line check; the production runner is the standing `--kind unit` bucket (G-04). I ran both and recorded them separately.
1. `python3 tests/unit/test-prune-run-evidence.py` gave exit 0, 40 PASS, 0 FAIL, 0 SKIP, `all checks passed` (`/tmp/qa-b2399-c2-prune.log`). The run was uid 501, so chmod 000 took effect and the unreadable cases ran.
2. `gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md` gave exit 0, no diff.

## MF-1 (unreadable traversal silent omission): RESOLVED
Pinned pruner: `_run_files` now passes `onerror=note` to `os.walk` and appends the failing path to `unreadable`. `_stage_paths` collects the result, and `main` writes `cannot read recorded run content: <paths>` to stderr and returns 1 before `_prune` and `_stage`. Dry-run takes the same route. The new `unreadable_cases` test (`tests/unit/test-prune-run-evidence.py`, `unreadable_checks`) chmods `runs/build-c0-eng/qa` to 000 and asserts exit 1, the path named, no index change, and no ui/ removal, for both dry-run and prune. All four PASS in the run above, none skipped. Mutant check by reading: the fixed behavior depends on `onerror`, and the old code had none.
Regression sweep of neighbouring paths: `git diff 69b14e22 74e6896c` touches only the pruner, test, notes. The 36 earlier checks still pass (40 total), so the keep selection, refusal, symlink and staging checks are unchanged. The refusal order is preserved: `--keep` mismatch and missing evidence refuse (exit 2) before the walk.
Note: the unreadable failure is exit 1, not 2. It fires before any mutation, so it is atomic, unlike a `git add` failure (exit 1 after the UI prune, advisory carried from c1).

## MF-2 (SC-03 removal clause): CLOSED by ruling
The operator accepted the clause as vacuously satisfied. I graded the remaining SC-03 clauses by inspection only. Reviewers/PM own those.

## Fail-first (natural RED, signature-bearing assertion diffs; audited, not rerun)
Source: `notes/red-first-T-01.md`. I verified identities by sha256 of git blobs:
- Test at pin 74e6896c = `5431b502…a05d`, equal to the c1-fix section's test hash. The pruner at the c1 base 9db1ba98 = `4ccdd6bf…b08c`. The pruner at the pin = `55df0581…93ef`, equal to the c1-fix section's fixed subject.
- First section (staging, SC-01/SC-02): base 9eb07b4f pruner `3ce3bb40…af9`, test `1f896bd0…08bc`. I confirmed the base hash in c1. In that run, 27 PASS (25 pre-existing) and 9 assertion FAILs with empty stderr.
- SC-01: base index empty, `would stage` lines absent, staged=[] on the symlink case. Plus c1-fix red: the 9db1ba98 pruner returned rc=0 on an unreadable recorded subtree and staged only the readable files (3 assertion FAILs, 37 PASS, stderr empty).
- SC-02: base rc=0 where 2 was expected, base pruned ui/ in the refusal fixture, 4 FAIL lines.
The SC-02 tests remain in the pinned test file unchanged by the c2 delta. Reds are semantic, not signature-absent: the base has the features absent and the asserted contract rejects it, so they discriminate rather than only proving the tests install.

## Coverage gaps (advisory, carried from c1)
`git add` failure, unsafe run ids, nested `ui/` such as `qa/ui/x`, linked files, evidence hash mismatch and escaped evidence paths still lack dedicated regressions. A mutant excluding any `ui` dir at any depth would still pass the suite.

## Findings by kind
None gating. All advisories above belong to T-01 and are not blocking.

## Principles applied
None cited from craft leaves.
