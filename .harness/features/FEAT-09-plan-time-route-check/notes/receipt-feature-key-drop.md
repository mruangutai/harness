Removed 18 key(s) from FEAT-09-plan-time-route-check's feature.yaml because each had no reader; FEAT-14 closed the key set to eleven. This receipt is the only durable record of their values.

## status collapse (the pre-collapse pair survives only here)

- old status: `shipping`
- old phase: `ship`
- new status: `Review`  (rule)

**check-plan-routes.py's verdict on this feature CHANGES.** Its finished-feature skip reads `status`; at `Review` this feature STAYS in the checked set. Named here so a later reader does not read it as a silent regression. The skip is repointed at `Done` by T-11.

## value normalization

- `pr`: `'none'` (string) -> `null`

## removed keys, full values

```yaml
approved:
  brief: approved — Mike Ruangutai, 2026-08-05, BRIEF.md:115-117
  plan: approved — Mike Ruangutai, 2026-08-05, PLAN.md:118-120
backlog:
  b10_squad_dispatched: Two historical plans use a token this feature retires. Normalise?
  b11_files_format_bug_FILED_134: 'PROMOTED — a list-form `files:` block is misread
    INCLUDING the leading dash, producing false VIOLATIONs. Top of the list: it makes
    the checker COST time. notes/does-it-pay-back.md'
  b12_inv17_late: 'INV-17 re-checks a handoff only after phase: advances — unflagged
    during the phase it describes'
  b13_state_cap_story: 'The cap is Write-only; Edit and Bash bypass it. Filed as #132
    — NOT backlog'
  b14_strict_schema_debt: 'Keys this session added that no schema declares yet, listed
    for issue #104''s strict-schema work'
  b15_team_rule_narrower_than_guard: NEW, non-blocking, raised by product-lead. The
    harness-team rule text names the state.yaml violation as top-level keys holding
    PROSE LISTS; the guard rejects ANY unrecognised top-level key including a bare
    integer counter. Doc narrower than enforcement — a lead reading only the rule
    keeps tripping it. Harness-doc defect, deliberately not worked around.
  b1_shared_files_rejected: FLAGGED. A `shared:` file is falsely REJECTED — fails
    CLOSED, not open. Answering it amends DEC-179
  b2_sc08_weaker_than_it_reads: 'FLAGGED. 3 of 4 clauses are respellable greps. Issue
    #74 mode 3, live — same root as mf1'
  b3_matcher_unverified: matches()/glob_to_re() proven not RE-implemented, never proven
    CORRECT. Modes differ on normalisation
  b4_false_positive_rate: MEASURED 2026-08-05, no longer unknown — 2 false positives
    + 35 format artifacts across 5 legacy plans. notes/does-it-pay-back.md
  b5_stale_anchor: Cites check-domain.sh:190-197; real record :61-69. PLAN.md:210
    is the origin — a PLANNING defect
  b6_team_token_unvalidated: LEGAL_TOKENS is display-only. Within the approved intent
    — a design limit, not a defect
  b7_argvless_glob: 'No argv globs relative to CWD: 0 violations across 0 plans, exit
    0. BECOMES BLOCKING if b8 lands'
  b8_promote_invariant: Promote the route checker to a check-state.sh invariant?
  b9_shared_regex: The checker copies check-state.sh's task-block regex (D-08). Consolidate?
  detail: notes/backlog-detail.md — one line each here, rationale there (DEC-150 routing)
baseline:
  base_sha: 47ed11f
  base_sha_note: 'RE-PINNED AT THE REBASE. Was ae2443d, a PRE-FEAT-08 main commit
    that STILL RESOLVES, so nothing errors — git diff ae2443d just returns the WRONG
    SCOPE. MEASURED AGAIN THIS LEG: 71 files against a true 14 at 3c245c3 where it
    was caught, and 84 against 30 at HEAD today. A wrong answer with exit 0. 47ed11f
    is git merge-base main HEAD, measured.'
  briefing: notes/ship-review-close.md
  closes_issues: '#20'
  commits:
  - 6792331 — [harness:t-01] check-domain.sh --resolve + 8 cases
  - e355401 — [harness:t-03] templates/PLAN.md Lanes + execution_mode
  - 358fd36 — [harness:t-04] harness-spec-driven routing rule
  - ae28daf — [harness:t-02] check-plan-routes.py + 17-case test + runner registration
  - 4918d06 — DEC-179 + regenerated index
  - 7218d63 — VF-1 fix, main-session-direct under DEC-174
  commits_note: The PRE-REBASE ids (685901d, 92d254b, 1185d7f, 06a680f, abddb28, 2a242df)
    are DANGLING and must never be cited. Replay verified byte-identical on all four
    source files.
  head_sha: 2d26c2f
  head_sha_note: State BODY was measured at 3a5a245; committing it produced 2d26c2f,
    which is bookkeeping-only. The mismatch is the usual self-reference lag, not drift.
  worktree: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/FEAT-09
cycles_note: STAYS AT 2. The goal-check and the three distillation runs were first-pass
  and clean, and a first pass is work not rework (DEC-157). SC-08 returning unmet
  added ZERO because no send-back was dispatched — it is a user decision, not a fix
  cycle.
filed_not_fixed:
  vf2_shape_gate_covers_1_of_3_write_routes: 'FILED AS ISSUE #132 BY USER RULING —
    a budget/context-hygiene gap, NOT an authorization hole, which is why VF-1 was
    fixed inline and this was not. Write exits 2; Edit and Bash exit 0. Domain enforcement
    is unaffected on all three routes. Costs: notes/vf2-shape-gate-edit-bypass.md.'
gate_status:
  distillation: DONE across 10 agents. All 12 expertise files pass check-expertise.sh
    exit 0, RE-RUN BY ME because leads hold no Bash and two flagged their own files
    unverified.
  docs: PASS — check-docs.sh exit 0, re-run by me
  goal_check: 'RAN via product-lead/pm at 7354ad0: 11 of 12 SCs MET, SC-08 UNMET-AS-UNPROVEN.
    THAT VERDICT IS NOT RETROACTIVELY EDITED — SC-08 was closed AFTERWARDS, at 4769227,
    by a main-session fix carrying its own proof. So: the goal-check returned 11/12
    against the tree it saw; the tree now satisfies 12/12. Anyone re-reading should
    not infer pm returned 12. pm''s premise was re-verified by the main session and
    was stronger than reported. Digest: runs/goalcheck-product/digest.md (GITIGNORED;
    the durable result is sc_status).'
  index: PASS — gen-decisions-index.py --stdout | diff - exits 0, re-run by me
  qa_gate: PASS — re-run at 7218d63; cases (i)/(j) PROVEN to fail against the pre-fix
    guard
  review: PASS. Four-wide at 4918d06 FAILED with one HIGH (VF-1), fixed at 7218d63.
    Delta at 7a1bff8 PASSED, severity_max low, no must_fix; its two findings were
    APPLIED at 7354ad0, not carried.
  security: RAN. Graded the env-var defect med on reachability; the lead overruled
    to high
  ship_refresh: SKIP — .harness/codebase/ does not exist in this tree, so no map to
    refresh
  state: PASS — check-state.sh exit 0, re-run by me
  uat: NOT_REQUIRED — nothing here is operated by hand
  ui: PASS — self-scoped out ON MEASUREMENT, not prediction. No rendered surface
  unit: 'PASS — re-run by ME: exit 0, 32 PASS, 0 FAIL, 13 scripts'
github.closed:
- T-01 -> 99
- T-03 -> 101
- T-04 -> 102
github.filed:
- '#132 — VF-2, the shape gate covers 1 of 3 write routes'
github.open:
- T-02 -> 100 — close CONDITION MET (VF-1 resolved) but gh-sync BLOCKED by the permission
  classifier; still open, carried in the briefing
must_fix_open: {}
must_fix_resolved:
  vf1_env_var_disables_the_guard: 'FIXED AND VERIFIED AT 7218d63 by the MAIN SESSION
    under DEC-174 — the lane the orchestrator identified and could not enter. Reproduced
    with payload FILES before and after. Test-first and proven non-vacuous. SC-04
    is now TRUE AS WRITTEN. Record: notes/vf1-guard-bypass.md.'
posture: 'SHIPPING BY USER RULING 2026-08-05. All 12 SCs met, review PASS, gates green.
  The two limits found while measuring payback are FILED, not fixed here: #134 (list-form
  files: misparse — the one item that makes the checker COST time) and #135 (the tool-collision
  class the checker cannot see by design). Queued next per the ruling: #134 and #133.
  The SC-08 diff (2 files past the pin) is ACCEPTED on its discrimination proof rather
  than delta-reviewed — user ruling.'
receipts:
  dec179: Entry at DECISIONS.md, indexed at DECISIONS-INDEX.md:199. Index regenerates
    byte-identical
  method: 'ME, re-running every verify: after each run returned — corroborated, never
    relayed. Task detail lives in the run digests and in notes/handoff-build.md ##
    Trust, not here.'
  sc11: 'HOLDS, re-run at HEAD: git diff 47ed11f -- .claude/agents/harness-pm.md is
    0 bytes'
  t02: 'Re-run by me. 17 distinct cases, 19 PASS lines. On FEAT-09''s own PLAN: 0
    violations, exit 0, exactly ONE DEVIATION naming T-01'
  t02_no_reimplementation: 'Verified STRUCTURALLY, not by grep: every literal entry
    goes to the check-domain.sh subprocess and :64 parses its OUTPUT'
  t02_scripts_array: THE SHARED-ARRAY HAZARD DID NOT FIRE. SCRIPTS is 13 elements;
    test-cost-report.py appears NOWHERE. FEAT-08's removal preserved
review_sha_note: 'THE PIN MOVED THREE TIMES AND THERE IS NOW UNREVIEWED SOURCE PAST
  IT — both go in the briefing. (1) 1185d7f DANGLING after the rebase, removed not
  carried. (2) 4918d06 for the four-wide panel. (3) 7a1bff8 for the delta review after
  the VF-1 fix made it stale. (4) 7354ad0, applying that reviewer''s own findings.
  CORRECTION, CAUGHT RATHER THAN LEFT STANDING: an earlier version of this note claimed
  "ZERO source has changed since the pin". THAT IS NO LONGER TRUE. The SC-08 fix (4769227)
  changed check-plan-routes.py and test-check-plan-routes.py — measured, `git diff
  --name-only 7354ad0 HEAD -- .claude/ docs/` returns exactly those two. It is UNREVIEWED
  source, pending the user''s call at the ship decision. What it does carry instead
  of a reviewer: a discrimination proof — swap a prefix reimplementation into resolve_agents
  and case 17b FAILS (2 agents expected, 16 returned) while all three original case-17
  assertions still PASS.'
rulings:
  q2_brief_override: 'BRIEF.md:106-109 forbids any task here writing under docs/harness/.
    The user OVERRODE that for the single DECISIONS.md entry plus the regenerated
    index — nothing else. Verified honoured and CONFIRMED NOT A BREACH by the goal-check:
    the commit touched exactly those two files.'
  qE_no_cost_line: 'Write NO cost line, invent NO figure, carry NO budget field. The
    mandate itself is gone: cost-report.py is deleted and cost_model stripped from
    harness.json by FEAT-08. The briefing states once that the harness no longer meters
    spend (DEC-178). HONOURED.'
sc_status:
  met: ALL 12 AT HEAD. SC-01..SC-07 and SC-09..SC-12 were re-derived at 7354ad0 by
    the goal-check; SC-08 closed separately at 4769227 — see sc08_closed. The goal-check
    itself returned 11/12.
  sc08_closed: 'WAS UNPROVEN-NOT-BROKEN; NOW PROVEN. The code was always correct (no
    matcher; it shells out). The fixture could not fail, because a prefix reimplementation
    OVER-grants rather than under-granting — `.harness/features/` prefixes every feature
    file — so it also resolved to somebody, also printed OK and also exited 0. FIX:
    the OK line now names the granting set (the convention the DEVIATION line already
    used) and case 17b asserts the EXACT set. DISCRIMINATION PROVEN BY RUNNING: with
    a prefix reimplementation swapped in, all three original case-17 assertions still
    PASS and 17b FAILS — expected 2 agents, got all 16.'
  sc08_lane_note: NAMED AS A DECLARED DEVIATION, not left looking routine. check-plan-routes.py
    is NOT on DEC-174's carve-out list and T-02's execution_mode is `team`, so a main-session
    edit to it is exactly the DEVIATION shape this feature's own checker exists to
    surface. The user ruled the change directly, so it is authorised — but it is recorded
    as a deviation, not as a normal edit.
  sc08_residual_weakness: 'SAID PLAINLY RATHER THAN CLOSED OVER. Clauses 8, 9 and
    16 remain source greps for the literal strings check-domain.sh, fnmatch and glob_to_re;
    a differently-spelled reimplementation passes all three. SC-08''s strength now
    rests on case 17b alone. This is issue #74 mode 3 and stays on the backlog as
    B-2.'
tasks:
  T-01: DONE
  T-02: DONE
  T-03: DONE
  T-04: DONE
trigger_gap:
  finding: 'NOTHING MECHANICAL INVOKES check-plan-routes.py. Verified by grep: check-state.sh
    0 hits, check-docs.sh 0, settings.json 0 hooks, and run-unit-tests.sh runs only
    the TEST. The sole invocation is a SENTENCE — harness-spec-driven/SKILL.md:39
    telling harness-pm to run it. So FEAT-09 moves routing from build-time discovery
    to plan-time detection ONLY FOR PLANNERS THAT RUN THE SCRIPT. That is prose-only
    enforcement — the shape this feature''s own BRIEF rejected. It is backlog items
    b4 and b8 converging.'
  ordering_trap: b7 MUST land before b8. An argv-less invocation globs relative to
    CWD and returns "0 violations across 0 plans, exit 0", so wiring it into check-state.sh
    naively yields an invariant that passes by checking nothing — the same failure
    class a third time.
  raised_by: THE USER, during the SC-08 ruling, from first principles — and it is
    larger than SC-08 was.
```
