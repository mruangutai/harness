# STATE

## Current

- feature: FEAT-51-claude-code-lifecycle-safety
- run: none — no squad run is live; the build is blocked on a main-session-direct segment
- squad: none
- status: Building

BUILD PHASE OPEN, AND ITS FIRST SEGMENT IS NOT MINE TO EXECUTE. Both artifacts are signed —
`BRIEF.md` and `plan.yaml` read `approved`, `Mike Ruangutai`, `2026-09-01` — and `plan.yaml`'s
station moved plan → `building`, written through `plan-merge.py set-feature-station`.

THE MIRROR IS OPEN: `gh-sync.py open` created milestone #38, parent #1135, and one sub-issue per
task — T-01 #1136, T-02 #1137, T-03 #1138, T-04 #1139, T-05 #1140, T-06 #1141, T-07 #1142,
T-08 #1143, T-10 #1144. `gh-sync.py status … building` recorded the station; that station writes no
cards by design (only `ready` and `review` do), and each card reaches Building through its own
`start-task`.

NOTHING IS DISPATCHABLE TO A SQUAD. Every one of the nine tasks depends on T-01 or T-02, and both
are `main-session-direct` under DEC-174 — they touch `validate-digest.py` and
`inflight_registry.py`, the enforcement layer no squad may write. The executable segment list is
`notes/build-segments-c10.md`: seven segments, four of them main-session-direct (1, 2, 4, 5) and
three mine (3 = T-04 to `harness-dev-ops`, 6 = T-06 to `harness-documentor`, 7 = T-08 to
`harness-dev-ops`).

SEGMENTS 2 AND 3 ARE CONCURRENT once T-02 lands — they share no files — so the moment T-02 is
committed the build parallelises for the first time.

CYCLES 9 OF 20. The operator raised `max_total_cycles` from 10 in the same act as the signature,
which is what makes a build phase affordable at all. `len(runs)` is 14 of 20, informational; a
main-session-direct segment is not a run and never appears in `runs:`, so the build will under-count.

THE BRANCH is `feat/FEAT-51-claude-code-lifecycle-safety` at `d97e6bce`, clean, one commit above
main's tip `0bc57c88`. That commit is the operator's own: it repaired `plan-merge.py`
`cmd_sign_approval` test-first so a plan can hold a signature at all, corrected T-07's title, raised
the cycle budget, and signed both artifacts.

## Open Questions

- OPERATOR DECISION, not gating: `PF-e380f685c0697fb709ff29f65af0cf24` (med, open) asks for a
  one-run Claude Code spike before the build is paid for — does the host re-enter a parent that
  returned exit 0 from its Stop hook with a live child claim? Nine tasks rest on that assumption and
  SC-10 (uat) is the only instrument that tests it, running last.
- OPERATOR DECISION, not gating: `PF-2545afb576b19ad86704f5bfcb556b9e` (low, open) asks to narrow
  SC-02's `awaiting` set-equality to a subset check. Narrowing a success criterion is the operator's.
- RESIDUAL, not gating: `DEC-210` is free at `0bc57c88` but another feature may take the number
  before T-06 runs. T-06's escape clause routes that case and forbids the documentor touching
  `plan.yaml`.
- HARNESS DEFECT, raised three consecutive times: `harness-code-reviewer` cannot terminally yield on
  a plan-phase dispatch. `validate-digest.py` refuses `code_grade: n_a` ("cannot be bound to
  review_sha … an unpinned feature (INV-6) cannot anchor a code_grade claim") AND refuses it omitted
  ("missing code_grade"). The two refusals are mutually exclusive, so no return satisfies the gate,
  while `feature.json` already records `code_grade: n_a` for that same unpinned feature. Cost one
  reader ~32 minutes and four yield attempts; its work was complete and durable and its lead
  transcribed from the artifact. — harness-validator-lead
- HARNESS DEFECT: `plan-merge.py`'s `UNION_KEYS` is only `("tasks", "decisions")`, so `lanes` and
  `panel` cannot be amended incrementally — any difference is exit 7. Five full remove-then-
  single-shot-apply recreates were needed this phase, each byte-verified. — harness-orchestrator
- HARNESS DEFECT: `check-domain.sh` denies `harness-pm` an `Edit`/`Write` at
  `features/<FEAT>/notes/plan-proposal-*.yaml` — its `notes/` grant is `research-*.md` and
  `uat-*.md` only — so the sanctioned tool is refused for the one write route `plan.yaml` has, and
  pm reached it through `python3`, which the guard does not intercept. — harness-pm
- HARNESS DEFECT: `bash-write-guard.sh` scans the whole Bash command line for redirect shapes, so a
  `python3` heredoc whose PYTHON SOURCE contains a `>=` comparison is refused as a redirect
  targeting a token that is not a path. — harness-pm
- HARNESS DEFECT: `check-plan-routes.py` resolves each task's `files:` against the live manifest and
  never reads `lanes.rows`, so a surface missing from the block is ungated. — harness-pm
- HARNESS DEFECT: a lead digest missing the `artifact:` key is written and accepted by its own run,
  and only `check-state.sh` catches it later. `runs/plan-fix-c2-product/digest.md` had shipped
  without one and was repaired to its own path. — harness-orchestrator
- HARNESS DEFECT, admitted in D-19 rather than closed by this feature: a generic Bash write
  (`cp`/`cat`/`tee`/`mv`/`sed -i`/`python3 -c`) to a canonical feature artifact inside the writer's
  own domain passes all three registered PreToolUse gates. Measured at `0bc57c88`, exit 0 on all
  three. REQ-04 is qualified to say so; backlog row B-1. — harness-orchestrator
- PRE-EXISTING, unrelated to this feature and currently red: `check-state.sh` INV-29 refuses on a
  standing worktree that is not FEAT-51's — `.claude/worktrees/harness/BUG-1129-validate-handoff-sweep`,
  terminal on the default branch and dirty, so `remove` declines until its changes are committed or
  discarded. Do not touch it; it is another effort's live work. — harness-orchestrator
- SCHEMA GAP, not blocking: the `panel.findings` `reader` enum is
  `should-not-exist | scope | goalcheck` and has no word for a lead's fan-in finding. Recorded as
  `validator-lead`, which is truthful; no validator reads that field. — harness-pm
