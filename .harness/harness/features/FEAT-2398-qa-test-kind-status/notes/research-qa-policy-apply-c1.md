# Cycle-1 application — ready for plan goal-check, unsigned

The non-PASS floor is narrowed without weakening the settled unresolved/active-null hard gate. All three canonical findings are retained and resolved at the proposal level through T-01; this is not implementation evidence or operator approval. BRIEF and plan remain pending at plan, source_issues [2398], one main-session-direct task, three proposed decisions, five SCs (four integration, one inspection; no personal UAT).

## Every finding disposition

Source: runs/2026-11-22-01-plan-product/panel-c1.md, canonical should-not-exist findings. Scope passed and design self-scoped out; neither erases the advisor's specific counterexample. All findings keep reader should-not-exist, kind proportionality and scope task, with their original identities, summaries and severities:

- **PF-145060c3e846ad4a0e711a2ad4236227 — med:** Floor-omission refusal under BLOCKED/FAIL exceeds the settled unresolved gate and can refuse legitimate early-exit BLOCKED digests.
  **Resolved by narrowing D-02, SC-04 and T-01.** Grilling Settled requires unresolved/active-null omissions to refuse under every verdict, not a blanket non-PASS presence floor. Existing validate-digest.py#_qa_kinds_errors applies the complete satisfied floor only at PASS/matrix_ok true; the five-state QA table has no truthful not-yet-run entry. Keep that complete PASS floor; policy-check every reported kind under every verdict; add all-verdict mandatory presence only for unresolved/active-null always-floor kinds. T-01 independently tests mixed-floor BLOCKED acceptance with just the misconfigured kind reported, refusal if that kind disappears, and early BLOCKED/FAIL omission of otherwise configured runnable/locally_run kinds. No fictitious state, receipt, predicate evaluator, exclusion or coverage claim is introduced. Conditional applicability and the stronger all-excluded no-kind exemption are unchanged.
- **PF-22552338e7f54f4eab80c56b2219a49c — low:** Pin-blob reads for unbound Harness features plus suite-wide fixture migration exceed settled part 3 (product features); name the cost before signature.
  **Resolved by explicit proposed cost/compatibility disclosure, not scope removal or presumed operator consent.** Retain one pinned-policy path for Harness and fleet products; a second current-tree Harness path would preserve drift. D-01, T-01 and BRIEF Constraints now name the migration of affected fixtures in the owned validator integration test to real Git commits and trusted feature/pin bindings, preserving every assertion. Runtime adds local commit/blob reads and one config validation per QA return, with no network lookup. Unpinned Harness QA reports that formerly used current-tree policy now refuse until a trusted pin exists. No bulk historical backfill, extra owned files or non-QA product_config change is authorized. The operator sees this trade-off before signature; it is not a vague open question.
- **PF-e8ec73fa933b33c999cd27085bf7da0b — info:** SC-02's with/without INV-49-disclosure control tests a coupling absent from the validator.
  **Assessed-and-dismissed as a reason to remove the control; retained and resolved through T-01's bounded specification.** The validator has no Verification gaps read today, so this is noninterference regression coverage, not a repair to an existing coupling. The operator explicitly settled that disclosure never waives the gate. Reuse one fixture, vary only that BRIEF section, and assert the identical unresolved refusal; no INV-49 edit or separate test subsystem. No assertion is deleted or weakened, and no red-first claim is made for this already-passing control.

The older research-qa-policy-draft.md now carries these revised D-01/D-02 claims rather than leaving superseded all-verdict-floor wording live. T-01 also makes the scope review's existing all-QA-consumers watchpoint explicit for _qa_floor_requires_nothing and _active_receipt_kinds; it does not change their receipt/exemption contracts.

## Exact command receipts

Feature-root resolution returned /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status. All commands used the read-only control-plane tool, targeting only the feature worktree. Complete task-changing stdout was captured and printed; selected exact receipt lines follow, not a replacement transcript of the long intent diff.

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py apply --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status/.harness/harness/features/FEAT-2398-qa-test-kind-status/plan.yaml --proposal -
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status/.harness/harness/features/FEAT-2398-qa-test-kind-status/plan.yaml
EXIT: 0

python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py record-panel --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status/.harness/harness/features/FEAT-2398-qa-test-kind-status/plan.yaml --digest /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status/.harness/harness/features/FEAT-2398-qa-test-kind-status/runs/2026-11-22-01-plan-product/panel-c1.md --cycle 1
ADDED PF-145060c3e846ad4a0e711a2ad4236227
ADDED PF-22552338e7f54f4eab80c56b2219a49c
ADDED PF-e8ec73fa933b33c999cd27085bf7da0b
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status/.harness/harness/features/FEAT-2398-qa-test-kind-status/plan.yaml

python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py set-panel --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status/.harness/harness/features/FEAT-2398-qa-test-kind-status/plan.yaml --value-file /dev/stdin
PANEL cycle 1 -> /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status/.harness/harness/features/FEAT-2398-qa-test-kind-status/plan.yaml
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status/.harness/harness/features/FEAT-2398-qa-test-kind-status/plan.yaml
EXIT: 0

python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status/.harness/harness/features/FEAT-2398-qa-test-kind-status/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status
OK T-01 6 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status/.harness/harness/features/FEAT-2398-qa-test-kind-status/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2398-qa-test-kind-status: 1 task(s), 6 anchor(s) resolved, 0 failure(s)
```

Record-panel and final check both exited 0. The apply proposal replaced only D-01.choice/because, D-02.choice/because and T-01.intent; set-panel changed only disposition/resolved_by on the three tool-generated findings after asserting their exact identity/severity/summary/kind/scope. No findings or run artifacts were hand-edited. No APPROVAL-RESET: receipt was emitted; no gh-sync invocation or remote transition occurred. Neither approval mapping was edited.

Automatic check-state --changed output accompanying the merge verbs still reports the unsigned BRIEF and INV-37 missing Build-entry receipt, plus pending-plan, historical-cycle-attribution and untracked-feature notes. These remain visible rather than being disguised as a green state check; they do not negate the separately successful plan check or authorize signing/opening Build. No standalone state check, builds, tests, lint, formatters or smoke runs were run. Main still owns baseline RED/focused GREEN and final unit/integration evidence after signature.

## Principles applied

- Experience First — preserve truthful early refusals instead of forcing invented not-yet-run states, while retaining both legitimate repair paths.
- Redesign From First Principles — retain one reviewed-policy source for both repository cases and all QA consumers, explicitly pricing its compatibility effect rather than preserving a parallel current-tree path.

## Open questions

None. The host's plan goal-check and simplification pass remain outside this apply assignment; operator signature remains mandatory before implementation.
