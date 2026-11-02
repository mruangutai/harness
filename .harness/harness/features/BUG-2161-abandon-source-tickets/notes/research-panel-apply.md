# BUG-2161 — panel application

Both cycle-0 task-only proportionality findings are addressed without a panel re-cycle; BRIEF and plan approvals remain pending. Two tasks and D-01 through D-03 are retained unchanged in scope.

## Findings addressed

- PF-a68755d85a05e098891d2d28274a6e7a (med): T-01 and BRIEF SC-05 drop the speculative corpus-lookup detector and perturbation gate. The second-active-feature positive fixture, authoritative plan.yaml source list, red-first planner coverage and no-corpus-check contract remain. SC-06 assigns the negative contract to pinned decision/code inspection. Recorded resolved_by T-01.
- PF-f3f10babb2e63d106e0d0d8db679839c (info): T-02's receipt now points to canonical BRIEF SC-07 instead of copying its runbook; T-02 traces only SC-06. SC-07 retains merged executable and archived record revision provenance, an operator-selected archive checkout, signed reason-file dry run followed by both confirmation flags, and the required source/local outcomes. Recorded resolved_by T-02.

The six settled behavioral constraints remain: both flags authorize source writes; each opted-in source closes not_planned then returns Backlog, receives abandoned and the signed reason with every write previewed; operator confirmation replaces any corpus check; without opt-in sources are untouched; unopened mirrors record abandoned before pruning runs/; gh-close-gate.py remains unchanged. Post-merge operator-only archived FEAT-1774 acceptance and already-abandoned re-entry remain binding. D-01/D-02/D-03 still govern confirmation risk, idempotent re-entry and verbatim reason provenance.

## Receipts

Three plan-merge amend invocations changed T-01.intent, T-02.intent and T-02.traces; each exited 0 with AMENDED/APPLIED stdout captured in this run. No APPROVAL-RESET: receipt appeared, so no gh-sync status call was made. A preliminary traces --show without --yaml-value exited 4 read-only; the structured invocation supplied the required hash.

Required record-panel --cycle 0 exited 0 and emitted the two PF ids above; set-panel then recorded resolved dispositions through the supported verb, preserving reader records, severities and summaries. Required plan-merge check --root PRODUCT exited 0: 2 tasks, 5 anchors resolved, 0 failures.

Plan-merge's automatic check-state messages report the unsigned BRIEF, pending plan and missing github.build_entry (INV-37). These are disclosed, not claimed repaired: no approval or live GitHub write was authorized. No production edits, tests, builds, lint, formatter, goal-check or live source disposal ran.

## Principles applied

- Experience First: retain one canonical operator acceptance sequence instead of a build-time receipt copy.
- Redesign From First Principles: propagate the detector removal through both SC-05 and T-01, retaining the positive behavioral contract.
- PRODUCT PRINCIPLES, No more specific than necessary: constrain source targeting and reviewable policy, not speculative filesystem interception.

## Open questions

None for this apply step. Separate final goal-check and operator approvals remain outside this assignment.
