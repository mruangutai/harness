# BUG-2399 — pending patch ready for signature

One bounded direct task owns all five settled files; no production changes, regression execution, panel or goal-check occurred. BRIEF is 45 lines (limit 120); its approval is pending. plan.yaml has status plan, approval.status pending and exactly one bugfix T-01 tracing SC-01–03. The plan's adequacy_notes incorporates this receipt by path.

## Evidence and scope

- Operator-confirmed source: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-run-records-staged-at-ship-2026-11-23.md; issue https://github.com/mruangutai/harness/issues/2399. Reported CI failures are accepted, not reproduced.
- Inspected base 9eb07b4f3cd235c234a10edddbfe5542c1e85fba: pruner main currently prunes and returns success without staging; _ui_targets protects linked run/UI directories. Preserve that safety while adding staging. Precedent BUG-2294 supplies direct-route and coupled-index conventions, not scope.
- PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are absent: the assigned checkout docs directory contains only PRINCIPLES.md and invalid-states-audit.html. No substitute product guidance was authored. Issue-list intake read the current open backlog; adjacent #2306/#2307 and check-state changes remain outside this patch.
- SC-01 and SC-02 require new genuine failing assertions against the explicit base and passing fixed-subject receipts. SC-03 requires pinned inspection. All implementation outcomes remain unverified. Unit is active, runnable and matches tests/unit/test-prune-run-evidence.py; browser null runners are unrelated. No UAT/prototype is required, subject to main override.
- D-01 amends only DEC-238's Ship keeps the record and drops the rest bullet; decisions_affected row 0 owns that clause. DEC-174/179/225/254/187 remain keep dispositions. DEC-238's other bullets stay unchanged. Regenerate the index preserving handwritten tails.

## Intake verification / adequacy receipt

Exact command:

```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2399-run-records-staged-at-ship/.harness/harness/features/BUG-2399-run-records-staged-at-ship/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2399-run-records-staged-at-ship
```

Run once after apply; exit 0. Exact stdout:

```text
OK T-01 5 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2399-run-records-staged-at-ship/.harness/harness/features/BUG-2399-run-records-staged-at-ship/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2399-run-records-staged-at-ship: 1 task(s), 5 anchor(s) resolved, 0 failure(s)
```

Same invocation's structural measurement: BRIEF_LINES=45; BRIEF_PENDING=True; PLAN_APPROVAL=pending; PLAN_STATUS=plan; TASK_COUNT=1. Plan creation used the control-plane plan-merge.py apply only, exit 0 with APPLIED receipt and no APPROVAL-RESET. Its automatic changed-state check reported unsigned BRIEF and missing Build-entry receipt, plus pending/historical attribution notes. Those are preserved as pending-intake findings, not repaired by unauthorized signature or build entry. No builds, tests, linters or formatters ran.

## Principles applied

- Experience First — stage records inside the existing ship operation instead of retaining a routine manual force-add burden.
- Redesign From First Principles — one task aligns behavior, ship instructions and the governing ship bullet without introducing a second interface.

## Open questions

None. Main must obtain the operator's signature before implementation; no approval was manufactured.
