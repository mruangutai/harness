# FEAT-2452 apply, cycle 1: all seven panel findings dispositioned, panel recorded, check green, still pending

All seven cycle-1 findings are repaired in `plan.yaml` and `BRIEF.md`: three substance, two form and two proportionality trims. `record-panel --cycle 1` exited 0 and recorded seven PF ids with severities unchanged. `check` exited 0 (5 tasks, 30 anchors, 0 failures). Approval is `pending`, `status: plan`, and all five tasks are `main-session-direct`. One question is open for the operator at signature: OQ-1, DEC-138's stale implementation sentence. It does not block the apply step. The required four-angle simplify pass was escalated outside the product team. It has **not** been done and is not claimed here.

## Finding dispositions (panel ids, severities as recorded)

| PF | Kind/sev | Disposition |
|---|---|---|
| PF-3bfe1e6f… safe caller-level single-override red run | substance/high | **Applied.** T-02 lands confinement first, so it also holds for the old code. `gh_sync_support.run` and every owned runner set only FACTORY_GH, strip any inherited GH_SYNC_GH, and prepend to PATH a separate offline sentinel `gh` that logs and exits 97. A failing-first regression in test-gh-sync-open.py runs the real `gh-sync open` with HARNESS_GH_COST_LOG=1 and a tmp HARNESS_PROJECT_DIR. It asserts: the sentinel log is empty; the fake transcript brackets each operation with the counter argv; and there is one cost-log line per operation. Any default-binary dispatch fails it, even when the mirror exits 0 through SKIP. T-03 applies the same confinement and red run to the board fixtures, and T-04 to wayfind tests. SC-02 wording is updated to match. |
| PF-500b6ede… 404 vs status-zero JSON | substance/med | **Applied.** In T-04, absence requires a completed gh process with a nonzero integer status (None is a launch failure) AND an explicit HTTP 404 in stderr. A status-zero response with malformed JSON raises GhError even when stderr mentions HTTP 404, and this counterexample is added to the T-04 regressions. Classification stays local. SC-03 is updated. |
| PF-1d616c71… stale GH patches + mirror telemetry | substance/med | **Applied.** In T-02, `replacement_undispatched_case` and `replacement_confirmed_save_failure_cases` move from `patch.object(module, "GH")` to call-time FACTORY_GH through `patch.dict(os.environ)`, keeping their durable-intent assertions. Mirror telemetry is bound to T-02 by adding `tests/unit/test-gh-cost-log.py` to the T-02 verify pool, which runs the file but does not edit it, so edit ownership stays disjoint. T-01 keeps those wrap-site cases transport-agnostic: they intercept the shared `subprocess.run` attribute (`test-gh-cost-log.py _counting_fake`), so the same assertions hold before and after the cutover. The final cumulative unit gate re-proves it. |
| PF-264d65c0… DEC-220/167 + DEC-138 clause | form/med | **Applied, with OQ-1 raised.** Keep rows were added for DEC-167 (gist clause) and DEC-220 (two rows: undispatched-intent clause and Build-entry absence clause). A second DEC-138 keep row quotes the separate-runner clause and states the conflict. BRIEF Constraints now name DEC-220 as BLOCKS, DEC-167 as SUPPLIES, and the DEC-138 conflict. |
| PF-f10c24fc… live probe receipt | form/low | **Applied.** T-05 owns `notes/issue-types-live-probe.txt` (create). Main runs the default read-only probe (no `--create-in`). The T-05 verify reads `.harness/harness.json github.repo` and accepts only `CAPABILITY PRESENT <repo> …` or `CAPABILITY ABSENT <repo> declares no native issue types`. Any line containing SKIP fails. BRIEF Verification gaps names the receipt. |
| PF-e4b1875d… milestone (e) over-bar | proportionality/low | **Trimmed.** The dual spelling is removed. The matcher is now the in-tree `factory_gh.create_ref` conjunction: lowercased stdout+stderr contains both `422` and `already exists`, inline, with no helper. The five-scenario matrix is cut to two regressions: 422 → lookup, 401 → no lookup. If the conjunction needs more than that, the implementer invokes the settled first-to-cut lever: keep today's lookup, and return to PM so SC-04 is re-worded at re-signature. SC-04 is updated. |
| PF-3cf5ab12… changelog in reference | proportionality/info | **Trimmed.** The T-05 instruction to put #893/#1542/#13 evidence into github-mirror.md is replaced: the reference holds current policy rows only, and closure evidence goes to the ship record and commit trail. Traceability is unchanged: #893 → T-02 (closes; T-01 seam), #1542 → T-01 parser + T-02/T-04 consumers, #13 → T-02 abandon regression. The enforcement ticket is still owned by T-05 / SC-07. |

## DEC-138 literal conflict, OQ-1 (my reasoning)

`DECISIONS.md` DEC-138, "Shared code, and migration scope", says `gh_bin()` lives in `gh_issues.py` and "each caller keeps its own runner". T-04 deletes `gh_bin` (settled Q3), and T-02/T-04 route every launch through factory_gh. The **policy** behind that sentence survives the cutover: argv builders, caller-specific SKIP/0 vs exit 1, and gh-sync importing no `parent_args`/`blocked_by_args`. The **implementation claim** does not.

DEC-205 ("this file states current truth") and DEC-254's scope rule (amend a partly overtaken ruling) point to `amend`. The grilling settled "DEC amendments: none required". Its single escape hatch, a change "only if the table would otherwise contradict the index rows", does not fire, because the DEC-138 index row says nothing about `gh_bin` or runners. Resolving this inside settled scope is therefore impossible without either leaving a stale sentence or amending.

I kept the row as `keep` and record the conflict here. **OQ-1, for the operator at signature:** add an `amend` row for DEC-138's shared-code clause? That amendment would make the clause read: argv builders stay in `gh_issues.py`; binary resolution and launch live in `factory_gh`; each caller keeps its own failure policy. It would also need an owning task, either T-05 with DECISIONS.md added to its files or a new task. The alternative is to accept the stale sentence until a later sweep. I recommend the amend. I did not apply it, because the amend reopens settled scope.

## Writer receipts (every invocation, cwd = product worktree, absolute feature path)

1. `apply --proposal -` (task fields T-01..T-05), **exit 0**. This verb changes tasks. Its stdout lines are `REPLACED T-01.intent`, `REPLACED T-02.intent`, `REPLACED T-02.verify`, `REPLACED T-03.intent`, `REPLACED T-04.intent`, `REPLACED T-05.intent`, `REPLACED T-05.files`, `REPLACED T-05.verify`, then `APPLIED <plan.yaml>`. Each REPLACED line carries the full old and new string and was printed only to the first 300 characters. **No `APPROVAL-RESET:` line was present (grep count 0), so no gh-sync call was made.**
2. `set-key --key decisions_affected`, **exit 0**:
   ```text
   KEY decisions_affected -> /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
   APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
   ```
   Before writing, each clause was asserted to be a verbatim substring of its DEC section.
3. Every writer's automatic check-state guard printed two VIOLATIONs: the BRIEF is not approved, and INV-37 finds no Build-entry receipt. It also printed notes for pending approval, unknown historical cycle attribution and an untracked feature dir. These are expected while the feature is pending. They are not presented as green, and the guard's `gh-sync open` suggestion was not followed.

No invocation failed.

## Required commands, literal output

`python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py record-panel --file <feature-dir>/plan.yaml --digest <feature-dir>/runs/r-20261123-1-plan-product/panel-c1.md --cycle 1`, **exit 0**:
```text
ADDED PF-3bfe1e6fa1d390a01608f9f4691e5d27
ADDED PF-500b6edeb3f44a1077e3d17823d19094
ADDED PF-1d616c71fa78e2127146432752890b56
ADDED PF-264d65c0b4c11c8fc335feb5240c3635
ADDED PF-f10c24fc64326826c94b4b2326fd8010
ADDED PF-e4b1875dab5b26b1e625b00544388f1e
ADDED PF-3cf5ab1247b91727827d2acdc2d6b56a
PANEL cycle 1 from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/r-20261123-1-plan-product/panel-c1.md -> /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml
```
(stderr: the same check-state guard block as receipt 3.)

`python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file <feature-dir>/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport`, **exit 0**:
```text
OK T-01 4 anchor(s) resolved
OK T-02 13 anchor(s) resolved
OK T-03 5 anchor(s) resolved
OK T-04 3 anchor(s) resolved
OK T-05 5 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport: 5 task(s), 30 anchor(s) resolved, 0 failure(s)
```
No OVERLAP lines appeared, so file ownership stays disjoint.

## Not done here
- No signature, no approval write and no gh-sync call. No code or test edits, and no tests, build, lint or formatters were run.
- The four-angle simplify pass is escalated outside the product team and is not complete.
- No new independent readers and no goal-check were run.

## Principles applied
- **Outcome-Oriented Execution**: confinement lands before the red run, so the failing-first phase is safe and discriminating on the old code. Mirror telemetry is bound to the phase that changes it (T-02), not to T-01.
- **Experience First**: the milestone precision trim keeps the operator-visible behavior and drops the matrix; the reference stays current policy, not history.
