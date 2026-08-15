# Handoff — plan phase — FEAT-10-software-factory

## Next

Wait for the user's ONE signature covering BRIEF.md and plan.yaml. On signature the build phase
starts at the DAG roots — T-01, T-03, T-09, T-10, T-11 (`plan.yaml depends_on`). T-01 is
`main-session-direct` and cannot be dispatched until the operator's answers are written into
`.harness/factory/fleet.yaml` AND the board rename below is done. There is no UAT script.

## Trust

- 12 tasks, 20 criteria (18 automated / 2 inspection / **0 uat**), 8 REQs, 15 decisions — counted
  by me from BRIEF.md and `load_plan` — verified-at 914b6fd
- Every criterion carries a REQ trace and no REQ is uncovered after SC-07's deletion; REQ-04 →
  SC-04/SC-19, REQ-05 → SC-05/SC-19 — computed by me — verified-at 914b6fd
- Zero `SC-07` references remain in BRIEF.md, plan.yaml or DESIGN.md — grepped by me
- No task `id`, `depends_on`, `files` or `verify` changed in ANY revision — verified-at 914b6fd
- Gates: `load_plan`, `check-plan-routes.py`, `check-docs.sh` all exit 0 — re-run by me
- `check-state.sh` shows FEAT-10's only violation as the unapproved BRIEF; four others belong to
  FEAT-04/FEAT-07 and predate this feature — verified-at 914b6fd
- T-01 and T-08 are the only `main-session-direct` tasks (DEC-179; DEC-174 carve-out)
- Re-POSTing an existing `blocked_by` edge returns 422 "Target issue has already been taken"; a
  repeat `sub_issues` attach returns a 422 CONFLATING duplicate-edge with different-parent —
  `notes/probe-edge-idempotence.md` — verified-at 914b6fd
- **NOT TRUE YET:** board 3 offers no `Building` or `Review` Status option; the operator renames
  before T-01 — `notes/probe-board-limits.md` — verified-at 914b6fd
- **UNVERIFIABLE, not merely unverified:** 13 of 20 criteria have no pre-rewrite baseline because
  the feature dir is untracked, so the plain-English rewrite could only be checked mechanically on
  them — `runs/prose-delta-validator/digest.md`
- **UNVERIFIED:** concurrent `create_ref` serialisation is inferred, not measured. SC-07 was the
  criterion that would have raced it and the operator deleted it, accepting that **no criterion
  exercises the live GitHub API before ship**

## Dead ends

- Do not re-add SC-07 or any live-API criterion — the operator ruled it anticipation under #194's
  one-in-flight cap and accepted the consequence
- Do not re-litigate `prototype_required: false` — `DESIGN.md:3-19`
- Do not replace `create_ref` with the additive-assignee claim — `notes/research-FEAT-10-claim-atomicity.md`
- Do not add pagination to the board read — superseded by the server-side query filter, D-10
- Do not extend E-1's narrowed fatal rule to `sub_issues` — its 422 conflates two causes
- Do not copy the plain-English rule into `harness-brief` — it lives in `harness-handoff/SKILL.md:57`
- Do not make `blocked_by` merely advisory — the operator ruled ENFORCE and D-01 was amended for it

## Working set

- `.harness/features/FEAT-10-software-factory/BRIEF.md`
- `.harness/features/FEAT-10-software-factory/plan.yaml`
- `.harness/features/FEAT-10-software-factory/DESIGN.md`
- `.harness/features/FEAT-10-software-factory/notes/answers-esc1-a1.md`
- `.harness/features/FEAT-10-software-factory/runs/prose-delta-validator/digest.md`
