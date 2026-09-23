# FEAT-64 c0 resolution

## Conclusion

All three c0 findings are applied without changing the exact ten-library/eight-tool scope, byte-identity and divergence obligations, census outcome, task graph, main-session-direct routing, or FEAT-65 exclusion. BRIEF.md and plan.yaml remain pending.

## Evidence

- High substance: plan.yaml T-01 now specifies only the settled unwired hook_guard contract: hook_guard(main, name, fail="open"), successful-result preservation, Exception rather than BaseException handling, existing open/closed return values, invalid-fail rejection before main, and no production caller. It imposes no hook-name/original-exception diagnostic shape; BRIEF.md SC-03 matches this contract.
- Medium substance: plan.yaml T-03 now requires red-first behavioral regression cases for the route-discovery and handoff-authority same-execution reparses, deletion of those reparses, and consumption of the existing parsed values without adding or expanding a detector. SC-06 remains unchanged.
- Low proportionality: plan.yaml T-01 now requires one unrelated RuntimeError escape case per typed-boundary contract and reserves explicit KeyboardInterrupt/SystemExit escape cases for hook_guard. BRIEF.md SC-03 makes the same distinction.
- Panel cycle 0 was recorded only through plan-merge.py record-panel from runs/plan-product/panel-c0.md. The recorded findings retain their original identities, severities, kinds, readers, and summaries: PF-0b7e32972bad5fee79955e3761c650ee (high/substance), PF-0f6f38f647d0a4ccb9fecd14350a1e1c (med/substance), and PF-a7995df8d4353b1784e178552d9b3e18 (low/proportionality).
- The targeted plan-merge.py check exited 0: T-01 resolved 22 anchors, T-02 resolved 20, and T-03 resolved 5; total 3 tasks, 47 anchors, 0 failures. Every task remains cross_module and main-session-direct.
- The two task-changing amend invocations emitted no APPROVAL-RESET receipt, so gh-sync.py status was not run. plan.yaml has approval.status pending and needs_approval true; BRIEF.md has status pending.
