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

- 2026-08-12: `files_touched` is a CLAIM, and the T-10 run's omitted a file. `git status --porcelain`
  before staging showed `.claude/skills/harness/references/missions.md` modified — absent from the
  task's `files:`, absent from the member's and the lead's reported `files_touched`, and unrelated to
  the feature. The tree was verified clean at `689b557` immediately before dispatch, so it landed
  during the run. The rule: as commit-pen holder, diff the WHOLE dirty set against the reported
  `files_touched` and treat the difference as unattributed, never stage from the digest's list.
  The content mattered too — it was prose "tightening" that deleted evidence pointers (the kaya-audit
  observation, the concrete `WORKER → api/` example, DEC-141 provenance). Weaker prose that no gate
  reads is how a rule quietly stops teaching what it was written to teach.

- 2026-08-12: I could NOT reproduce the channel that wrote that file, and the negative is worth
  recording. `check-domain.sh --resolve` returns NOBODY for it; feeding the hook a payload for
  `harness-documentor`, `harness-product-lead`, `harness-orchestrator` and `harness-backend-dev`
  against `Write`, `Edit`, `MultiEdit` and `NotebookEdit` returns BLOCKED every time; the
  `PreToolUse` matcher is `Write|Edit`, so those are the covered tools; and `bash-write-guard.sh` is
  live enough that it blocked my own probe command for merely CONTAINING a redirect to the path. So
  the decision layer denies every agent × every edit tool, and the write landed anyway. Diagnosing
  further would mean editing a DEC-174 carve-out script, which is exactly what the carve-out
  forbids — so the honest terminus is a loud defect report, not a quiet workaround.
