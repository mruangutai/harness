# Apply c2 — smoke contradiction corrected; T-03 re-review required

Only T-03 has a substance correction requiring narrow re-review. T-03/T-10 also receive the authorized proportionality trim, without re-panel. Plan check passed; no exit goal-check or implementation is claimed. BRIEF and plan remain pending; approval is untouched.

## Correction and task ownership

- **T-03 / substance:** deleted the entire superseded known-excluded-smoke paragraph, including expected full-fleet aggregate failure, prohibition on removing membership, and pending operator disposition. Retained the settled removal of only smoke's fleet entry, Kaya/all other settings, prohibition on modifying the smoke repository, and unsuppressed remaining refusals.
- **T-03/T-10 / proportionality:** removed exact shipped smoke-absence/Kaya-presence assertions from permanent reader integration coverage. T-03 retains synthetic remote-invalid, remote-source authority/no-checkout-fallback and aggregate failure/no-suppression cases. T-10's bounded feature-only checker/receipt compares committed base/review fleet documents: review must equal base with only smoke's entry removed, with Kaya unchanged and every other setting preserved.
- **T-10:** records actual remaining-fleet validation commands, source/ref context, diagnoses and exits, not a live-fleet assertion that must become green before Kaya migration. Local unit/integration failures remain failures. SC-02/SC-10 obligations and mandatory SC-08 authorized Kaya remote-main landing are unchanged.
- Actual changed task IDs: **T-03, T-10**. Exact substance task ID: **T-03**. T-08, all task anchors/traces/dependencies/literal verify commands, D-01–D-08 and SC text are unchanged. The canonical Shared task contract in research-apply-plan-c1.md now carries this disposition; existing product identity and authority/read pointers remain intact.

## Recorded panel dispositions

record-panel consumed runs/2026-11-22-02-plan-product/panel-c1.md with cycle 1. Union retained all eight prior identities/dispositions and added four supplied findings; set-panel changed dispositions only, preserving supplied severity, kind and summary.

| Finding | Preserved grade | resolved_by | Reason |
|---|---|---|---|
| PF-a622d798c2cd8d491a4aaf0a7237c53a | med/substance | T-03 | Prior smoke disposition is now the authorized membership removal, not a remote-repository migration. |
| PF-877923987af16e3258ccff177e999d6f | med/substance | T-03 | Contradictory no-removal/expected-failure instructions deleted. |
| PF-f42c986b5ce6aa471d698de51d1ff16d | med/substance | T-03 | Independent reader's same superseded paragraph deleted. |
| PF-37db11b709264518077155d42f27d2a2 | low/proportionality | T-10 | Exact shipped membership proof moved to bounded feature-only evidence. |
| PF-f46b3f746baa373ffc63bdf975d9eefc | info/substance | T-03 | Closure observation acknowledges the existing disposition; no new scope or task requirement introduced. |

Resolved records acknowledge the applied repair, not an independent re-review pass. Host must collect the narrow T-03 re-review before the single exit goal-check. No T-08/T-10 substance re-review or proportionality re-panel is requested.

## Writer and check evidence

All plan writes used the control-plane plan-merge.py: record-panel, two guarded amend calls on intent, then set-panel. Every invocation exited 0. Both task-changing stdout streams were captured and printed in full; their receipts were:

```text
AMENDED tasks:T-03.intent
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/plan.yaml
AMENDED tasks:T-10.intent
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/plan.yaml
```

Neither task-changing stdout contained APPROVAL-RESET:, so no gh-sync or other remote call ran. Writer-triggered changed-state diagnostics still report unsigned BRIEF and missing INV-37 Build-entry receipt, plus pending/historical-cycle notes; these are not claimed as a passing state gate.

Authorized final check, exit 0:

```text
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema/.harness/harness/features/FEAT-2297-harness-json-schema/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2297-harness-json-schema: 10 task(s), 102 anchor(s) resolved, 0 failure(s)
```

No production checks/tests/builds/lint/formatters, implementation, approval, or exit goal-check ran. Open questions: none; required next gate is the host-owned T-03 re-review.

## Principles applied

- Experience First: keep transient exact fleet membership evidence out of the evergreen suite so maintainers retain stable behavioral regression coverage without permanent release-specific assertions.
