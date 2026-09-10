# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- run: none — no squad run was dispatched this cycle
- squad: none
- status: awaiting-main-session

Plan is SIGNED and Build is OPEN. `plan.yaml` `approval.status: approved`, `BRIEF.md ## Approval
status: approved — 2026-09-09`, and `feature.json` `github.build_entry: opened` with parent 1584
and nine sub-issues 1585–1593, one per T-NN. Every Build precondition is satisfied.

Build cannot advance through the enforcement path. Read task by task, eight of the nine tasks
carry `execution_mode: main-session-direct` — T-01, T-03, T-04, T-05, T-06, T-07, T-08 under the
DEC-174 carve-out (validate-digest.py, check-domain.sh, check-state.sh, run-state-schema.json and
each gate's own test, plus two ungranted SKILL.md surfaces), and T-10 because its manifest is taken
at the owner root outside every worktree. The single `team` task, T-09 (`harness-documentor`,
DECISIONS.md), declares `depends_on: [T-04, T-06, T-07, T-08]` and is therefore blocked behind four
main-session-direct tasks. **Zero team-owned work is eligible today**, so no lead was dispatched and
no run was opened.

`notes/handoff-plan.md` `## Next` said to dispatch T-10 to `harness-eng-lead`. That was validated
against the plan and REJECTED: `plan.yaml:643-644` lanes T-10 `main-session-direct`. The approved
plan governs. Superseded by `notes/handoff-build.md`.

No station was written: for a `main-session-direct` task the task station, `gh-sync.py start-task`
and the feature station all belong to the main session. T-10's deliverable
`notes/run-artifact-manifest-base.txt` is absent, confirming T-10 has not run. cycles_used 4/10
(unchanged — no rework), runs 10/20 (unchanged — a main-session-direct segment is not a run).

## Open Questions

- Whether T-10 should stay `main-session-direct`. Its `execution_reason` cites tool reach, not
  DEC-174, so it is the one lane an operator could have pm re-lane to unblock the orchestrator.
  Non-blocking: the main session can simply run it.
