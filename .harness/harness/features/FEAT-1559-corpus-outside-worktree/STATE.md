# STATE

## Current

- feature: FEAT-1559-corpus-outside-worktree
- mission: plan
- run: .harness/harness/features/FEAT-1559-corpus-outside-worktree/runs/plan-product/digest.md
- run_verdict: ESCALATE
- station: plan
- approval: pending
- panel: cycle 1, readers scope/should-not-exist/design/goalcheck ran, 5 PF open (1 high substance)
- goalcheck: operator partial, reader pass, code-maintainer partial
- plan_check: exit 1 (DEVIATION .harness/team-config.yaml behind main c58c6c88; 45/45 anchors resolved)
- cycles_used: 0 / 10
- next: main session merges main into feat/FEAT-1559-corpus-outside-worktree, re-runs plan-merge.py check (expect exit 0), then asks the operator Q-safety and Q-order before signature

## Open Questions

- Q-routing (main session, mechanical): plan-merge.py check exits 1 only on DEVIATION — the worktree's `.harness/team-config.yaml` predates main's c58c6c88 (#2066 pnpm grants). Merge main into the feature branch and re-run check; the plan does not touch team-config.yaml.
- Q-safety (operator, blocking): PF-5e51b4e658129119f2a1e35df8588f67 — `--repair` cannot distinguish sparse-induced absence from genuine deletion by status alone; authorize an operation-bound sparse provenance mechanism or revise the hidden-feature merge-repair outcome. Recommendation: provenance marker written by the sparse-layout step; ambiguous/mixed dirt stays untouched.
- Q-order (operator, blocking): feature-worktree.py create adds the worktree before the record exists, so post-checkout cannot discover a fresh feature id. Resolve fresh-id convergence vs excluding creator edits. Recommendation: post-checkout exits 0 with a refusal note on absent record; create converges after the record write.
- Q-01 (operator, non-blocking, execution prerequisite): durable FEAT-57 replay-freeze/spot-check receipt and serialized T-19/check_state ownership before T-01, or explicit supersession.
