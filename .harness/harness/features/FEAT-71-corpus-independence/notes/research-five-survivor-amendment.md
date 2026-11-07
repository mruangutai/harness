# Five-survivor amendment — FEAT-71

The operator-authorized fifth survivor is added throughout BRIEF and plan survivor statements. The amended plan check passed (exit 0). No implementation or T-01 verification was executed.

## Authority and scope

Sole operator authority: notes/answers-2026-11-07-02-product.md, answer A. Exact set:
- FEAT-71-corpus-independence
- BUG-2161-abandon-source-tickets
- BUG-2141-dec174-main-orchestrator
- FEAT-2037-product-document-guidance
- BUG-20261006-fleet-planning-recovery

BRIEF changes: operator perspective's recent-feature count, SC-01 exact set, SC-03 retained-corpus count, and the constraint's survivor count/answer pointer. Plan changes: T-01 intent's exact list and exact-five wording, T-01 verify's set assertion, and the feature-corpus lane reason. No SCs, task set, verification method, pruning rule, or other scope changed.

## Legal amendment and approval

Control-plane CLI: /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py. Actual amend --help and plan_merge/amend.py were consulted; hash-checked amend replaces an existing task field without resetting approval (DEC-229, product DECISIONS.md). Product AGENTS.md Project map, SPEC writer ownership/state-consistency guidance, DEC-229/DEC-232, and relevant BUILD approval guidance were read as unchanged inputs.

Both amend calls used --key tasks --id T-01, this note path as their transient --value-file, and --reason naming the operator answer. Their --expect-sha256 values were:
- intent: c7b81a0742de44f3e7df15cba2c818ba3fc333382e98c4c79964dc890443181a
- verify: 5c5b2ff795b2d9251ebf77b3ff9b2645462d7dea662bff095f1216ffb4782b92

Both exited 0, printed AMENDED tasks:T-01.<field> judgement=amendment and APPLIED receipts for plan.yaml and feature.json. set-lanes exited 0 and printed LANES 11 row(s) resolved at c4e8bbc87e858bb2a0320efd766c7036cbcebb8b plus APPLIED plan.yaml. The tool's automatic check-state --changed hooks printed notes only; no separate check-state invocation was made.

No APPROVAL-RESET: receipt was emitted; no gh-sync call was made. Plan approval stays approved, not pending. BRIEF's approval section was untouched and stays approved by Mike Ruangutai, dated 2026-11-07. No approval was authored or renewed by PM. feature.json changes are the legal amend tool's two required amendment judgements; signed task hashes are not rewritten by amend. set-lanes necessarily serializes the lane mapping through its controlled writer.

## Explicit check evidence

Working directory: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-71-corpus-independence

Exact command:
```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-71-corpus-independence/.harness/harness/features/FEAT-71-corpus-independence/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-71-corpus-independence
```

Exit: 0. Exact output:
```text
OK T-01 20 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-71-corpus-independence/.harness/harness/features/FEAT-71-corpus-independence/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-71-corpus-independence: 1 task(s), 20 anchor(s) resolved, 0 failure(s)
```

Changed deliverable paths, all within this feature directory: BRIEF.md; plan.yaml; feature.json (amend-tool output); notes/research-five-survivor-amendment.md. No lead run-directory writes. No builds, tests, linters, formatters, panel, goal-check, or T-01 verification command was run. This check establishes plan validity, not delivery of SC-01–SC-05.

Open questions: none.
