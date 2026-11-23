# Handoff — FEAT-2398-qa-test-kind-status, plan → build — written at 9eb07b4f, seq-3

## Next

Operator signs: `plan-merge.py sign-approval --rework rounds=N,minutes=M --decision <path>` on
`.harness/harness/features/FEAT-2398-qa-test-kind-status/plan.yaml` (D-01 is the one proposed-not-settled
item the signature rules on; PF-* panel findings are all resolved/dismissed, none awaits an overrule).
After signature: build entry — `gh-sync.py open <feature-dir>`, then T-01 executes
main-session-direct under DEC-174 (every `files:` surface is lane `main-session-direct`; no
eng-lead build dispatch exists for this plan). T-01's `verify:` block is carried verbatim to that
segment. Validate then goes to `harness-validator-lead` over the pinned sha (plan task T-01, SC-01..SC-05).

## Trust

- plan.yaml is `approval.status: pending`, `status: plan`, `source_issues: [2398]`, one task T-01, D-01..D-03 — `plan.yaml:1-7,74-100,127` — verified-at 9eb07b4f (working tree, pre-commit)
- `plan-merge.py check --root <worktree>` exits 0, 9 anchors resolved — run by orchestrator after run 03 — verified-at 9eb07b4f
- Panel cycle 1 recorded with scope, should-not-exist, design, goalcheck all `ran`; three proportionality findings (med/low/info) resolved by pm — `plan.yaml` `panel:` block; `runs/2026-11-22-01-plan-product/panel-c1.md` — verified-at 9eb07b4f
- Goal-check: operator, reader, code maintainer all pass against the grilling intent — `notes/research-FEAT-2398-qa-test-kind-status-goalcheck-plan.md` — verified-at 9eb07b4f (lead claim; note on disk)
- Simplify pass (DEC-195) ran: 4 angle receipts under `notes/receipt-*-2026-11-22-02-simplify-eng-*.md`; findings 1,2,4,5,6 folded into T-01 by pm, 3 and 7 are briefing rows, 8–10 left — `notes/research-FEAT-2398-qa-test-kind-status-simplify-apply-plan.md` — verified-at 9eb07b4f (pm note on disk; plan check green afterwards)
- Run 02 closed FAIL at 0 cycles: dev-ops ran a timed git probe in a disposable /tmp repo against the no-git instruction; plan/BRIEF hashes unchanged before and after — `runs/2026-11-22-02-simplify-eng/execution-qualification.md` — verified-at 9eb07b4f (hashes re-measured by orchestrator)
- Source issue #2398 open, no comments, at Plan station; not superseded — gh issue view at dispatch — verified-at 9eb07b4f

## Dead ends

- Do not dispatch T-01 to harness-eng-lead: every owned surface routes `main-session-direct` (validate-digest.py and the QA rules skill are the gate under change, DEC-174) — `plan.yaml:53-72` — verified-at 9eb07b4f
- Do not re-panel on the three PF-* proportionality findings: all `scope: task`, resolved at apply; a re-cycle on proportionality is a defect (DEC-228) — `plan.yaml` `panel.findings` — verified-at 9eb07b4f
- Do not treat the efficiency receipt's 48ms timing claim as evidence — `runs/2026-11-22-02-simplify-eng/digest.md` "Unchanged-plan evidence" — source: eng-lead digest
- INV-37 (no Build-entry receipt) and "BRIEF not approved" check-state VIOLATIONs are expected before signature — `feature-record.py` changed-state output during runs 01–03 — verified-at 9eb07b4f

## Working set

- .harness/harness/features/FEAT-2398-qa-test-kind-status/plan.yaml
- .harness/harness/features/FEAT-2398-qa-test-kind-status/BRIEF.md
- .harness/harness/features/FEAT-2398-qa-test-kind-status/feature.json
- .harness/harness/features/FEAT-2398-qa-test-kind-status/runs/2026-11-22-02-simplify-eng/digest.md (briefing rows 3 and 7)
- /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-qa-unresolved-status-2026-11-22.md

## Done when

Scope: operator signature on the pending plan, then build entry for T-01 main-session-direct
Authority: brief-perspective:.harness/harness/features/FEAT-2398-qa-test-kind-status/BRIEF.md#operator
Authority: approval:.harness/harness/features/FEAT-2398-qa-test-kind-status/BRIEF.md#Approval
Authority: plan-task:T-01.verify
