Removed 25 key(s) from FEAT-07-verify-teeth-batch-probe's feature.yaml because each had no reader; FEAT-14 closed the key set to eleven. This receipt is the only durable record of their values.

## status collapse (the pre-collapse pair survives only here)

- old status: `in_review`
- old phase: `ship`
- new status: `Review`  (rule)

## value normalization

- `pr`: `'none'` (string) -> `null`

## removed keys, full values

```yaml
approved:
  brief: approved — Mike Ruangutai 2026-08-04, BRIEF.md `## Approval`
  plan: approved — Mike Ruangutai 2026-08-04, PLAN.md `## Approval`
baseline:
  answers: notes/answers-plan-product.md, notes/answers-amf-fix-product.md
  base_sha: 4091b36
  briefing: notes/ship-review-close.md
  closes_issues: '#19 #18 #22'
  commits: none yet by this flow — 4091b36 is the main session's standalone index
    commit
  cost_note: '242.48 is the plan phase CLOSED, against the original 120 and the new
    550. Each run figure is a by_agent DELTA against the prior metered block, never
    a top-line. The 120 was crossed at the architecture review the user ordered after
    seeing the first pass land at 44.57; that review cost 30.49 and found the blocking
    design gap that became D-07. No figure is invented. THE BUILD FIGURE IS UNDERSTATED
    BY CONSTRUCTION: eight of ten tasks run at depth 0 in the main session, which
    cost-report.py cannot separate from the session total. Named, never synthesized.'
  design_pass: SKIPPED by the orchestrator; product-lead independently ruled the prototype
    gate not-fired on every one of its four runs. Zero end-user surface, no DESIGN.md.
    Overridable at signature.
budget_raise:
  decided_by: user 2026-08-04 — recorded with its reason, never a silent edit
  from: 120
  proposed: 400 by the main session, REVISED UPWARD by the orchestrator with this
    reason
  reason: '400 would be crossed before the build finished, and the user''s own standard
    is that a number crossed again in week one is not a budget. Measured basis: the
    plan phase is CLOSED at 242.48; FEAT-06''s build+validate measured 252.63, and
    its own cost_note records that as an UNDERSTATEMENT because 9 of 10 build tasks
    ran at depth-0 in the main session and were not separable. FEAT-07 has 8 of 10
    tasks main-session-direct, so the same understatement applies, and T-01 is now
    roughly DOUBLE its original diff by the pricing the user accepted at the redirect.
    242 plus a scaled 280-330 lands at 520-570 before ship. NOT a licence to spend
    to it; actual-vs-budget is carried in every return per DEC-134.'
  to: 550
build_lanes:
  alias_check: 'harness-documentor maps to `documentor` and harness-product-lead to
    `lead` in ALIAS (validate-digest.py:111-121), so T-01''s new required fields do
    NOT bind the squad run. They DO bind every later dev-persona spawn: distillation
    and ship-refresh dispatches must carry `task: none` and omit `task_verify`, or
    the stop hook rejects them.'
  main_session_direct: T-01, T-02, T-03, T-04, T-05, T-07, T-08, T-10
  segment_1: T-01, T-05, T-07, T-08
  segment_2: T-01 fixture completion FIRST, then T-04, T-02, T-03, T-10
  squad_dispatched: T-06, T-09 — product squad, harness-documentor, docs/**
  t01_gap: 'T-01''s validator half is CORRECT — I re-ran the discriminating clauses
    myself, including the hint text and both licensed repairs. Its FIXTURES are incomplete
    against PLAN step (11) in three enumerated places: (11)(f)''s reviewer half, (11)(i2)''s
    hint-content assertions, and (11)(j2-ii)''s joint-hint followability. SC-17/SC-18
    are `verify: automated evidence: unit`, so hand-run evidence does not satisfy
    them. Routed back — that is the one cycle spent.'
cost_usd: 702.82
gate_status:
  goal_check: 17 met, 1 carved out (SC-12 receipt half). The 4 unmet at 70b0ed3 are
    closed at 98ed3e7 and verified by the orchestrator with each criterion's own method
    — pm has NOT formally re-graded them
  qa_gate: PASS — matrix_ok true at 29b612e; T-01 is the only `logic` task and 19
    new unit cases cover it
  review: PASS — the one med finding (SC-16 on two surfaces) is FIXED at 70b0ed3;
    fail-open hunt clean
  security: SKIPPED — no auth, secrets, input or network in a validator plus nine
    markdown files
  ship_refresh: SKIPPED — .harness/codebase/ does not exist, so there is no map to
    go stale
  uat: NOT_RUN — no uat criterion exists in BRIEF
  ui: SKIPPED — zero end-user surface, no DESIGN.md; O-01's rationale, same as the
    design pass
  unit: PASS — run-unit-tests.sh 10/10 and check-docs.sh over 180 files, both re-run
    by me
max_cost_usd: 550
pending:
- T-09 REGENERATES `docs/harness/DECISIONS-INDEX.md` and its `files:` names it. The
  main session's do-not-touch is read as scoped to the pre-existing +6 drift committed
  alone at 4091b36, NOT to T-09's three generated rows, which SC-12 requires. Stated
  so it is cheap to correct if that reading is wrong.
- 'OUT OF SCOPE BY RULING, do not re-open: #20, #21, perf-doc row 10, and issue #46
  (pm''s missing receipt grant).'
- 'DISTILLATION IS KEPT, user ruling 2026-08-04, not a strike candidate: three of
  this feature''s sharpest lessons came out of the observation-to-Expertise path it
  feeds, so the spend buys the next feature''s starting position. The budget crossing
  is ACCEPTED on the record, not waived, and max_cost_usd is NOT re-baselined to flatter
  the number.'
resolved:
- 'D-07 REDIRECTED AND FULLY APPLIED. The task-id field is the decision; `no-task`
  is recorded as the REJECTED alternative with the user''s reason. Orchestrator-verified
  at final state: ZERO redirect markers survive in BRIEF or PLAN, against six enumerated
  sites and an eleven-hit bare grep whose other five pm had already accounted for.'
- 'THREE USER ROUND TRIPS FOR THE WHOLE PLAN PHASE, each applied as ONE consolidated
  fix: four rulings, then seven review findings, then the redirect. FEAT-03''s counter-example
  was seven serialized runs for the same shape of work. The batching rule this feature
  installs, used on itself, is why — and the build applies it again: two main-session
  segments, not eight.'
- THE ARCHITECTURE REVIEW EARNED ITS SPAWN AND ITS FINDING SURVIVED THE REDIRECT.
  F1 was proven by the review's own return — a harness-backend-dev returning PASS
  with no PLAN task, the exact case the gate makes illegal. Neither planning pass
  before it found the gap.
- 'TWO DEFECTS FOUND BY RUNNING RATHER THAN READING, at the redirect: a re.Pattern
  in SCHEMAS falls through every existing per-field branch in SILENCE, so `task: bogus`
  would be accepted without the new regex branch — the same unknown-key-ignored shape
  that made the old SC-17 vacuous; and D-06''s preload grep cited `.claude/hooks/`,
  which does not exist in this repo (orchestrator-confirmed), so the command warned
  and proved nothing.'
- ORCHESTRATOR MEASUREMENTS HELD TWICE AGAINST CONTRADICTION. The index drift was
  uniformly +6 across 57 rows, ONE edit — the architecture review's two-edits reading
  came from a transposed pair, and the main session's earlier no-drift statement described
  a tree already fixed by an undeclared agent edit. Committed alone at 4091b36; T-09's
  precondition re-measured KNOWN-CLEAN at my own tier rather than trusted.
runs[0].cost_usd: 44.57
runs[10].cost_usd: 14.93
runs[11].cost_usd: 129.1
runs[12].cost_usd: 0.0
runs[13].cost_usd: 0.0
runs[1].cost_usd: 49.44
runs[2].cost_usd: 30.49
runs[3].cost_usd: 55.87
runs[4].cost_usd: 62.11
runs[5].cost_usd: 108.99
runs[6].cost_usd: 75.19
runs[7].cost_usd: 52.27
runs[8].cost_usd: 60.98
runs[9].cost_usd: 18.88
sc_summary:
  note: 'SC-01..SC-18, 10 tasks, 8 decisions D-01..D-08. Ten SCs were amended or replaced
    at the redirect, SC-17 replaced outright. Every task verify: has been EXECUTED
    against the tree and tabled with its result; four commands were rewritten across
    the phase because execution showed they did not discriminate.'
  planned: 18
tasks:
  T-01: PASS
  T-02: PASS
  T-03: PASS
  T-04: PASS
  T-05: PASS
  T-06: PASS
  T-07: PASS
  T-08: PASS
  T-09: PASS
  T-10: PASS
```
