Removed 11 key(s) from FEAT-05-pyyaml-file-parsers's feature.yaml because each had no reader; FEAT-14 closed the key set to eleven. This receipt is the only durable record of their values.

## status collapse (the pre-collapse pair survives only here)

- old status: `shipped`
- old phase: `ship`
- new status: `Done`  (rule)

## value normalization

- `pr`: `'none'` (string) -> `null`

## removed keys, full values

```yaml
baseline:
  baseline_exit: 0
  baseline_notes: 39 — all INV-8 pruned-run-dir notes, measured post-approval at 225cc98
    (T-01 step 2)
  baseline_run_inventory: notes/receipt-baseline-run-inventory.md — parsed==declared
    for all five features (1/1, 4/4, 19/19, 15/15, 3/3). No run is dropped today,
    so SC-13 "identical" holds and it does not conflict with SC-01
  baseline_violations: 0
  brief_shape: '7 REQs, 13 SCs at signature. BRIEF Amendment 1 (2026-08-03, user-authorised)
    adds REQ-08 and SC-14 — the corpus-validity gate. NOW 8 REQs, 14 SCs. PLAN.md
    carries NO task for SC-14: pm must add one before it can be built'
  check_docs_at_plan_exit: exit 0, 45 patterns across 113 files, no stale statements
  cost_note: run 01 attributed by depth cohort; runs 02-03 by cumulative delta. Floor,
    not ceiling
  governed_hook_path_ms: 80.63 measured by dev-ops, NOT the 23.7 the grilling recorded
  hook_interpreter: T-01 DONE. bare python3 now imports yaml 6.0.3 (/opt/homebrew/opt/python@3.14/bin/python3.14).
    Was ModuleNotFoundError at plan exit
  plan_shape: 17 tasks, 13 decisions, helper-first spine ending at the two hooks
  python3_on_path: 4 — homebrew, python.org 3.12, /usr/local, /usr/bin
cost_usd: 240.82
max_cost_usd: 120
pending:
- 'BRIEF AMENDMENTS Q1-Q3, rule at signature. REQ-01 names cost-report.py which reads
  no YAML at all. SC-03''s parenthetical undercounts the survivors: 7 of 17 calls
  in check-state.sh legitimately stay, six parsing MARKDOWN. SC-02''s exit-0 baseline
  is stale — check-state.sh exits 1 today on this feature''s own unsigned BRIEF'
- Q7 ROUTING WALL, third recurrence. dev-ops is granted neither .gitignore nor templates/**
  nor harness-init/SKILL.md, so PLAN T-10 and T-11 are MAIN-SESSION steps inside the
  build spine, and T-12 blocks on T-10. FEAT-03 Q13 and FEAT-04 T-09 are the same
  wall
- Q4 session identity in a PreToolUse hook subprocess is UNCONFIRMED. T-09 probes
  it and carries a stop-and-report ESCALATE branch. If nothing resolves, SC-08 and
  REQ-05 are unsatisfiable as written and the escape needs redesign
- HARNESS DEFECT the SubagentStop validator resolves a DIFFERENT validate-digest.py
  than the worktree's, so every digest checked inside a worktree is judged by the
  main checkout's rules
- SC-09 is verify uat and harness.json:244 is blocking_when_uat_criteria_exist, so
  ship gates on a hand-run of the bootstrap-escape expiry
- COST 92 of 120 spent in the PLAN PHASE ALONE. Build, validate and ship inherit ~28.
  This feature will overrun. Never a gate (DEC-134), but the user should see it before
  signing
resolved:
- E2 ONE shared bin/harness_yaml.py, helper first, hard edge to all six conversions.
  Imported via PYTHONPATH on the existing heredoc invocations, zero extra processes.
  Decided on divergence risk
- E3 ordered session-identity chain, marker .harness/.pyyaml-bootstrap, fail CLOSED
  on no identity
- E1 no universal install string. Two lines gated on the PEP 668 error TEXT, not exit
  status
- E4/D-06 check-state.sh gets NO bootstrap escape, deliberately, consequence written
  into the plan
- DEC-172 carries a Correction at DECISIONS.md:4566-4580 reversing both halves of
  its same-ship clause. 13 files not 16, templates may ship FIRST. Affects FEAT-06
  only. The grilling artifact is STALE on this point and must be corrected before
  FEAT-06 is briefed
- prototype_required false. bin/ scripts and hooks, no end-user surface. Overridable
  at signature
runs[0].cost_usd: 12.6
runs[1].cost_usd: 34.6
runs[2].cost_usd: 45.1
runs[3].cost_usd: 0
runs[4].cost_usd: 148.82
runs[5].cost_usd: 0
```

## value normalization added during execution — a gap in T-04's instruction

- `github.milestone`: `'none'` (string) -> `null`
- `github.parent`: `'none'` (string) -> `null`

T-04's intent names only `pr` for the string-`none` normalization, and explicitly leaves
`branch` and `review_sha` alone because INV-6 reads them as placeholders. It says nothing about
`github.milestone` and `github.parent`, which the schema types as `integer|null`. Left as written,
T-04's own verify clause could not reach exit 0. Normalized on the same reasoning as `pr` — the
string `none` is a placeholder for absent — and recorded here rather than applied silently.
