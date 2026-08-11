# Observations — harness-orchestrator — FEAT-16

- 2026-08-11: external state moved UNDER the plan mid-run. I measured board 2 at session start (118
  Done / 82 Todo / 11 In Progress, three Status options) and again at plan return (118 Done / 82
  Backlog / 11 Building, SIX options). An SC hard-coded the baseline. The rule that caught it:
  re-measure every hard-coded LIVE number at return, not only at baseline — a plan whose criteria
  cite external state has a shelf life, and the plan run itself is long enough to exceed it.

- 2026-08-11: a lead's "verbatim" gate paste was output from a DIFFERENT plan. pm's research note
  headed `Gate 2 — check-plan-routes.py (verbatim, cycle 2)` shows a command line naming the FEAT-16
  plan but output containing `gate-probe.yaml` / `review.yaml` / `harness-team`, which appear 0 times
  in FEAT-16's plan and match FEAT-12's. Its tree-wide claim (exit 1, 2 DEC-182 budget violations,
  FEAT-14 T-04 at 54 lines / T-08 at 61) did not reproduce: I measured exit 0, `0 violation(s) across
  12 plan(s)`, no budget logic anywhere in the checker, and those intents at 203 and 73 lines. The
  underlying plan was fine — the defect was in the EVIDENCE, which a shape gate cannot see. Re-run
  the gate yourself; a pasted gate result is a claim, not a measurement.

- 2026-08-11: option ids in GitHub Projects v2 are NOT board-identifying. Boards 2, 3 and 6 all carry
  `f75ad846` / `47fc9ee4` / `98236657` — GitHub's default Todo/In Progress/Done template ids, which
  survive renaming. Pinning them is a sound rename-vs-recreate discriminator and a worthless board
  identity check. Board 6 (untouched fixture) is what proves this, in one read.

- 2026-08-11: HEAD moved under me too (`d97f5ea` on `feat/239-domain-product-base` → `a29ad06` on
  main), and FEAT-17 appeared on disk during the run. Concurrent flows mean `lanes.resolved_at` and
  any cited sha need re-proving at return, and a leaf tier holding no Bash cannot settle ancestry —
  that question is the orchestrator's to close, never the user's.
