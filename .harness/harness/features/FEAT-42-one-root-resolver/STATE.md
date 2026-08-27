# STATE

## Current

- feature: FEAT-42-one-root-resolver
- run: none in flight. Last was 2026-08-26-6-plan-product (harness-product-lead), ESCALATE.
- squad: product
- status: plan phase COMPLETE except one approval-gated SC edit. AWAITING OPERATOR.
- cycles_used: 3 of 10. runs: 5 of 20. Both within budget.
- ORCHESTRATOR CONTEXT: ~250k against a 200k advisory, ~25% over. Handoff note written at this
  seam (`notes/handoff-plan.md`). A successor may take the SC-01 edit; this context should not.
- plan.yaml verified at disk by the orchestrator: 20 tasks, 15 `main-session-direct` / 5 `team`,
  every task carrying `id`/`files`/`execution_mode`/`verify`. T-07 re-laned per DEC-179.
  `approval: pending` in plan.yaml and BRIEF.md. NOTHING IS COMMITTED — deliberately, see Q5.
- The feature directory is UNTRACKED (`git status` shows `??`). This is load-bearing, not incidental.

## Open Questions

- Q5 (BLOCKING, operator only — an approval-gated SC change): SC-01 is satisfiable TODAY and
  unsatisfiable the moment the plan is committed. The lead reported it already broken at "72
  occurrences across 19 files". **That number is wrong.** Re-measured over SC-01's actual scan set
  (`git ls-files`, minus basename `test-*`, minus `harness_boundary.py`, minus `*.md`): **21
  occurrences across 17 files — exactly the recorded baseline.** The lead grepped the worktree, which
  includes untracked files; the feature dir is untracked, so `plan.yaml`'s 49 occurrences are not in
  the scan set. **But its conclusion holds on a one-step delay:** the orchestrator holds the commit
  pen and plan artifacts must be committed, and `git add` makes `plan.yaml` tracked — at which point
  the count passes 70 and can never reach zero. The plan quotes the variable 49 times precisely
  because its job is removing it. Remedy the lead recommends and the orchestrator endorses: a FOURTH
  exclusion for the harness's own record tree (`.harness/harness/features/**`, `.harness/notes/**`,
  `.harness/logs/**`), on the same "records, not code" rationale `*.md` already carries. That keeps
  `.omp/extensions/harness-hooks.ts` in scope, which is the whole reason the scan went repo-wide.
  **Editing an approved SC is not the orchestrator's and not pm's.**
- Q6 (BLOCKING, rides with Q5): the 21/17 baseline was derived by grepping `bin/` plus `.omp/` — a
  directory-scoped measurement standing in for a repo-wide criterion, which is the very scoping
  defect SC-01 was widened to remove. It happens to equal the correct repo-wide figure today, which
  the orchestrator confirmed independently, but it was reached by the wrong method and must be
  re-pinned over the actual scan set once Q5 fixes the exclusions.
- Q3 (OPEN, non-blocking — DEC-179 gap, second occurrence): DEC-179 resolves routing from each task's
  literal `files:` paths, but T-07's ungranted write lived in its `verify:` block, so the route check
  is structurally blind to what a verify touches. Widen it to verify blocks?
- Q4 (OPEN, non-blocking): D-05 records 20/16, D-12 supersedes with 21/17. `plan-merge.py` is
  add-only and exits 7 on a differing value, so supersede was the only legal route. Whether D-05 is
  corrected in place is the operator's call — and Q6 may move both numbers.
- Q7 (OPEN, non-blocking, harness defect): `bash-write-guard.sh` blocked a heredoc artifact write
  because the prose body contained an ASCII arrow, parsed as a redirect to a literal target. pm did
  not retry through bash and used the Write tool, which is correct conduct. Possible false positive
  in redirect detection over heredoc bodies.
