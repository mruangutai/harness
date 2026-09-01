# STATE

## Current

- feature: FEAT-51-claude-code-lifecycle-safety
- run: .harness/harness/features/FEAT-51-claude-code-lifecycle-safety/runs/plan-panelverify-c9-validator/state.yaml
- squad: none
- status: Plan

PLAN PHASE COMPLETE. THE PLAN IS PANEL-CLEAN AND AWAITS THE OPERATOR'S SIGNATURE. Nothing below the
main session may sign either artifact, and the signature is the only act left in this phase.

The plan is 7 requirements, 12 success criteria, 9 tasks, 17 decisions. `check-plan-routes.py` exits
0 with zero violations; the four `DEVIATION` lines on T-01, T-02, T-07 and T-10 are the correct
DEC-174 enforcement-layer carve-out. The panel record reads `cycle: 9`, `last_run:
plan-panel-c9-validator`, three readers all `ran`, 13 findings: 4 high all `resolved`, 4 med
`resolved` and 1 open, 2 low `resolved` and 2 open. NO high, critical or unrated finding is open.

The signature briefing is `notes/ship-review-plan-signature-c9.md` (HTML reading view beside it).
It carries the three operator decisions, the twelve-row backlog and the seven build segments.

WHAT THIS PHASE CLOSED, cycles 7 through 9:

1. THE F-1 RULING (cycle 7), conservative clean scope. D-16, D-17 and the discard task deleted; SC-12 withdrawn
   from `BRIEF.md` with the reason recorded and the number left as a gap on purpose. New D-18
   records that `quarantine.py discard` is deliberately uncovered and why: `bash-write-guard.sh`
   permits `rm -rf` of the same directory under D-06's shared glob, so a discard-only rule would
   record a protection that does not exist. Cutting D-16/D-17 restored T-07's own immutable intent,
   which already directed the single verb `adopt`. Three more findings closed in the same
   amendment: T-06 gained an edge to T-07, T-06's `verify:` gained both script-name greps, and T-07
   gained the `--file` fail-open negative control D-13 states and nothing proved.
2. THE DEC NUMBER COLLISION (cycle 8), gating and found by the cycle-7 goal-check. The plan numbered
   its own entry `DEC-209`, TAKEN on main by BUG-1081, so T-06's `verify:` grepped
   `DECISIONS-INDEX.md` for a string already shipped — a gate green before its task ran and unable
   to go red. Everything now reads `DEC-210`. The two `panel.findings` summaries carrying the
   literal `DEC-209` are left byte-identical: a reworded summary mints a new content-hash id and
   voids the operator's ruling on it. T-08 also gained the assertion that closes SC-09's last
   clause.
3. THE CYCLE-9 PANEL, which FAILed on F-A: the boundary does not bound a GENERIC Bash write.
   Orchestrator-measured, not taken on report — `agent_type: harness-pm`, no live claim,
   `cp /tmp/evil.md <feature>/BRIEF.md` fired at all three registered PreToolUse gates in the main
   checkout at `0bc57c88`: `bash-write-guard.sh` 0, `plan-sign-gate.sh` 0, `check-domain.sh` 0.
   This is issue #551's flagship occurrence on a route the feature does not close. The operator's
   own F-1 ruling settles the remedy — admit the hole, do not broaden the feature — so D-19 records
   it, REQ-04 and the `## Goal` are qualified, a verification-gaps bullet carries the measurement,
   and T-06's mandated DEC-210 entry must state it. F-B (the refusal text coaching a repeated
   terminal return), F-C (T-06's bullet list still contradicting D-15) and F-F (T-01's stale line
   anchors) were folded into the same recreate.
4. THE INDEPENDENCE PASS over that fix, because a self-certified closure of a high finding must not
   reach a signature. It confirmed F-A, F-B, F-C and F-F closed at source, 26/26 T-01 anchors
   correct, and no breakage. It returned FAIL on one residue only: T-07's `title:` still reads
   "Close the Bash route", which D-19 forbids asserting unqualified. Med, no `verify:` greps it,
   and all five places that RECORD coverage are qualified.

REQ-04 WAS NARROWED AND THAT IS A SCOPE REDUCTION, flagged rather than buried. It now names the two
governed write routes the feature actually gates and states that a generic Bash write inside the
writer's own domain is not covered (D-19). The operator accepts or refuses that at signature.

CYCLES ARE 9 OF 10 AND THE LAST ONE IS DELIBERATELY UNSPENT. The budget is per feature, not per
phase, so spending it on the T-07 title would leave the build with none. `len(runs)` is 14 against
`max_total_runs` 20.

THE BRANCH IS REBASED AND HEAD IS EXACTLY MAIN'S TIP `0bc57c88`. Of the plan's 21 target files, 19
are byte-identical between the original anchor sha `ad93d43e` and `0bc57c88`; the two that moved are
`validate-digest.py` (+270/-158) and `test-validate-digest.py` (+654/-119), both T-01's, and every
anchor in T-01's intent has been re-measured at `0bc57c88` and independently checked.

## Open Questions

- OPERATOR ACT OUTSTANDING, gating and terminal for this phase: the signature, plus acceptance of
  the REQ-04 narrowing and a ruling on the T-07 title residue. All three are §1, §2 and §3 of
  `notes/ship-review-plan-signature-c9.md`.
- HARNESS DEFECT, blocking this feature's own signature, main-session-direct under DEC-174 and
  re-measured against main at `0bc57c88`: a plan created by `plan-merge.py apply` can never acquire
  an `approval:` mapping, so this plan cannot be signed and `check-state.sh` reports it as a
  VIOLATION. Four probes: `apply` refuses a proposal carrying `approval` onto an absent base (exit
  8, `plan-merge.py:468`); onto an approval-less base it exits 0 and SILENTLY DROPS the block
  (`:536`); `sign-approval` exits 5 on a plan carrying none (`:903`); and the editor route is denied
  for every author including the main session (probed, exit 2). Recommended repair:
  `cmd_sign_approval` INSERTS the mapping when absent instead of exiting 5. It adds no capability —
  that verb is already the only writer and since #1103 already exits 10 for every governed caller.
  It cannot be a task in this plan because it must land BEFORE the signature. — harness-orchestrator
- HARNESS DEFECT, raised three consecutive times: `harness-code-reviewer` cannot terminally yield on
  a plan-phase dispatch. `validate-digest.py` refuses `code_grade: n_a` ("cannot be bound to
  review_sha … an unpinned feature (INV-6) cannot anchor a code_grade claim") AND refuses it omitted
  ("missing code_grade"). The two refusals are mutually exclusive, so no return satisfies the gate,
  while `feature.json` already records `code_grade: n_a` for that same unpinned feature. Cost one
  reader ~32 minutes and four yield attempts; its work was complete and durable and its lead
  transcribed from the artifact. — harness-validator-lead
- OPERATOR DECISION, not gating: `PF-e380f685c0697fb709ff29f65af0cf24` (med, open) asks for a
  one-run Claude Code spike before the build is paid for — does the host re-enter a parent that
  returned exit 0 from its Stop hook with a live child claim? Nine tasks rest on that assumption and
  SC-10 (uat) is the only instrument that tests it, running last.
- OPERATOR DECISION, not gating: `PF-2545afb576b19ad86704f5bfcb556b9e` (low, open) asks to narrow
  SC-02's `awaiting` set-equality to a subset check. Narrowing a success criterion is the operator's.
- RESIDUAL, not gating: `DEC-210` is free at `0bc57c88` but this plan is unapproved, so another
  feature may take the number before T-06 runs. T-06's escape clause routes that case and forbids
  the documentor touching `plan.yaml`.
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
- PRE-EXISTING, unrelated to this feature and currently red: `check-state.sh` INV-29 refuses on
  `.claude/worktrees/bug1128-qa-mutate-c2`, a standing worktree outside `WORKTREES_SEGMENT` whose
  terminal status cannot be determined. — harness-orchestrator
- SCHEMA GAP, not blocking: the `panel.findings` `reader` enum is
  `should-not-exist | scope | goalcheck` and has no word for a lead's fan-in finding. Recorded as
  `validator-lead`, which is truthful; no validator reads that field. — harness-pm
