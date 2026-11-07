# F1 amendment — pending operator re-signature

T-03 now separates one-time local QA equivalence evidence from permanent regression protection. QA must compare baseline 8e0b9e900986d4e0e07414ffedb1c09a2a6a7554 and the post-change checker on the real tree and every existing structure-lock mutant/fixture through both in-process and CLI paths, recording identical findings/order, exits, stdout/stderr and traversal counts in notes/qa-structure-audit-equivalence.md. Existing structure-lock cases remain intact; one permanent instrumented single-pass check must fail against the pre-change checker during the build and pass against current source. Permanent tests and CI cannot depend on historical extraction.

- T-04 unchanged: no baseline provisioning or history fetch added.
- T-06 unchanged: its existing SC-10 timing ledger already cites independent rule witnesses and red-first traversal evidence, not a permanent differential test.
- BRIEF.md and approval mapping were not edited. amend emitted AMENDED/APPLIED but no APPROVAL-RESET receipt; therefore no gh-sync status call was made. Main must record operator re-signature.
- plan.yaml.panel retains F1's original ID, high severity, substance kind and summary; set-panel records disposition resolved, resolved_by T-03, with resolution explicitly pending operator re-signature.

## Exercised checks

- Control-plane plan-merge.py check --file <feature>/plan.yaml --root <feature worktree>: exit 0; six tasks, 19 anchors, zero failures.
- Control-plane check-plan-routes.py <feature>/plan.yaml: exit 0; zero violations across one plan. Existing DEC-174 main-session-direct task deviations remain advisory.
- set-panel post-write check-state confirms INV-32 disposition resolved. It still reports the pre-existing missing notes/handoff-plan.md at building status; this is outside the assigned amendment, not a failure of either requested check.

## Open questions

None for the amendment. Operator re-signature and Main's existing handoff-plan bookkeeping remain outstanding. No implementation, equivalence proof, traversal execution or timing was run in this planning assignment.
