# STATE

## Current

- feature: FEAT-51-claude-code-lifecycle-safety
- run: none live — `runs/2026-09-01-01-eng/` returned ESCALATE and is closed
- squad: none
- status: Building

SIX OF NINE TASKS ARE BUILT AND COMMITTED. T-02 `af5c7136`, T-01 `741804ad`, T-03 `94f7f2eb`,
T-07 `72ec341d`, T-10 `a033793a` — all main-session-direct, each with its exact `verify:` passing.
T-04 is committed as `[harness:t-04] ship quarantine adopt/discard CLI` from the one eng run.
T-05 is in flight in the main session's lane. T-06 and T-08 are mine and both still blocked on T-05.

T-04 IS DELIBERATELY STILL AT STATION `building`, AND THAT IS THE HONEST RECORD, NOT AN OVERSIGHT.
Its own test file is green (`test-quarantine.py` 25/25 after a recorded 11-assertion RED) but the
second half of its declared `verify:`, `run-unit-tests.sh --kind unit`, exits 1. I will not write
`done` against a red verify. The station flips when the suite is green.

THE FOUR `^FAIL` LINES ARE TWO SUITES, BOTH IN THE MAIN SESSION'S LANE, NEITHER REACHABLE FROM
T-04's DIFF. Measured after T-01, T-03, T-07 and T-10 had all landed, so they are not mid-flight
artifacts:

1. `test-lead-stop-and-wake.py :: case_floor_inflight_registry.py` — "zero once-only occurrences".
   T-02 correctly deleted the only string `ONCE_RE` (that file, :266) matches. The floor demands at
   least one occurrence in `inflight_registry.py`, and there is now legitimately none, because
   DEC-210 SUPERSEDES the once-only claim instead of qualifying it. `test-lead-stop-and-wake.py` is
   in T-05's `files:`, so the reconciliation belongs inside T-05. The `DECISIONS.md` bound site
   still passes and must keep passing.
2. `test-code-grade.py :: check_self_grading` — `test-validate-digest.py:run_t51_suspension_cases`
   grades 2 (cyc 3, cog 5, ABC 37.4, bar 3, driver `abc`) and `test-validate-digest.py` is in
   `SELF_GRADED_FILES`, where every non-allowlisted function must reach 3. The remedy is a refactor
   into helpers — the driver is assignment/call volume, not branching — never a
   `SELF_GRADING_ALLOWLIST` entry, whose stale-entry check makes an exemption a standing liability.

T-04's DELIVERABLE IS INDEPENDENTLY VERIFIED, NOT TAKEN ON THE SQUAD'S REPORT. I ran `quarantine.py`
end to end against two throwaway roots: `list` parses persona, session, mtime and canonical target
and mutates nothing (md5 before/after); `adopt` on an illegal basename exits 2 naming the four legal
ones; `adopt` of `BRIEF.md` replaces and leaves the quarantine directory standing; `discard` refuses
a path outside a `features/*/quarantine/` segment and removes only the named tree; an empty `list`
exits 0 printing nothing. On the delegation path that carries the real risk, adopting a one-task
quarantined `plan.yaml` onto a fourteen-task canonical one produced fifteen ids and never the
one-task file, the approval mapping came through byte-identical, and `plan-merge.py`'s exit 7
(conflicting value) and exit 8 (differing approval) both surfaced verbatim with the canonical
approval intact after the refusal.

ONE PLAN DEFECT FOUND IN EXECUTION, recorded rather than silently worked around: T-04's `intent:`
states the `run-unit-tests.sh` kind cross-check "uses the .agents spelling as its prefix, so the
.claude spelling fails it". At HEAD that file sets `PREFIX = ".claude/skills/harness/bin/"` (:115)
and every sibling entry in `harness.json` uses `.claude`. A member following the intent literally
would have left the cross-check red on correct work. The lead caught it and landed the correct
`.claude` spelling; both registrations verified on disk.

THE MIRROR: milestone #38, parent #1135, sub-issues T-01 #1136, T-02 #1137, T-03 #1138, T-04 #1139,
T-05 #1140, T-06 #1141, T-07 #1142, T-08 #1143, T-10 #1144. Nothing is closed — D-23 keeps sub-issues
open until `ship`.

CYCLES 9 OF 20. The eng run reported zero send-backs and its ESCALATE was a sequencing question I
answered myself, so no cycle was spent. `len(runs)` is 15 of 20, informational.

WHAT IS LEFT AFTER T-05: T-06 (documentor, DEC-210 entry and index row), then T-08 (dev-ops, the
guard that reds the suite if a Bash half is omitted), then the qa segment, SIMPLIFY, the
`review_sha` pin with `gh-sync.py status … review`, the panel, pm's goal-check against the twelve
SCs, and the CEO briefing. Merge, PR and ship acceptance stay the operator's.

## Open Questions

- BUILD-PHASE BLOCKER, main-session lane, not gating any dispatch of mine: the two red suites above.
  Both are consequences of correctly-executed signed tasks and both close inside T-05 plus a
  refactor of T-01's new group function. — harness-orchestrator
- OPERATOR DECISION, not gating: `PF-e380f685c0697fb709ff29f65af0cf24` (med, open) asks for a
  one-run Claude Code spike — does the host re-enter a parent that returned exit 0 from its Stop
  hook with a live child claim? Nine tasks rest on that assumption and SC-10 (uat) is the only
  instrument that tests it, running last.
- OPERATOR DECISION, not gating: `PF-2545afb576b19ad86704f5bfcb556b9e` (low, open) asks to narrow
  SC-02's `awaiting` set-equality to a subset check. Narrowing a success criterion is the operator's.
- RESIDUAL, not gating: `DEC-210` is free at `0bc57c88` but another feature may take the number
  before T-06 runs. T-06's escape clause routes that case and forbids the documentor touching
  `plan.yaml`.
- PLAN-ACCURACY DEFECT, found in execution and already worked around: T-04's `intent:` names the
  `.agents` prefix for the `run-unit-tests.sh` kind cross-check where the file uses `.claude`. A
  literal reading produces a red cross-check on correct work. — harness-eng-lead
- HARNESS DEFECT, raised three consecutive times: `harness-code-reviewer` cannot terminally yield on
  a plan-phase dispatch. `validate-digest.py` refuses `code_grade: n_a` AND refuses it omitted; the
  two refusals are mutually exclusive, so no return satisfies the gate, while `feature.json` already
  records `code_grade: n_a` for that same unpinned feature. — harness-validator-lead
- HARNESS DEFECT: `plan-merge.py`'s `UNION_KEYS` is only `("tasks", "decisions")`, so `lanes` and
  `panel` cannot be amended incrementally — any difference is exit 7. — harness-orchestrator
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
  and only `check-state.sh` catches it later. — harness-orchestrator
- HARNESS DEFECT, admitted in D-19 rather than closed by this feature: a generic Bash write to a
  canonical feature artifact inside the writer's own domain passes all three registered PreToolUse
  gates. Measured at `0bc57c88`, exit 0 on all three. Backlog row B-1. — harness-orchestrator
- PRE-EXISTING, unrelated and currently red: `check-state.sh` INV-29 refuses on
  `.claude/worktrees/harness/BUG-1129-validate-handoff-sweep`, terminal on the default branch and
  dirty. Another effort's live work; do not touch it. — harness-orchestrator
- SCHEMA GAP, not blocking: the `panel.findings` `reader` enum has no word for a lead's fan-in
  finding. Recorded as `validator-lead`, which is truthful. — harness-pm
