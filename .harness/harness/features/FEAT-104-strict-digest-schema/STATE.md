# STATE

## Current

- feature: FEAT-104-strict-digest-schema
- run: none — no squad run was dispatched this cycle
- squad: none
- status: awaiting-main-session

Plan is SIGNED and Build is OPEN and UNDERWAY. `plan.yaml` `approval.status: approved`, the BRIEF's
own approval section reads `approved — 2026-09-09`, and `feature.json` carries
`github.build_entry: opened` with parent 1584 and nine sub-issues 1585–1593, one for each of the
nine planned tasks. The feature station reads `building`.

The first task has landed. The main session executed T-10 directly at the owner root — commit
`94e5428e [harness:t-10] capture run artifact baseline`, manifest
`notes/run-artifact-manifest-base.txt` at 728 lines against the plan's `assert 726 <= n` floor,
task station `done`.

Build still cannot advance through the enforcement path. Read task by task, eight of the nine
tasks carry `execution_mode: main-session-direct` — T-01, T-03, T-04, T-05, T-06, T-07, T-08 under
the DEC-174 carve-out (validate-digest.py, check-domain.sh, check-state.sh, run-state-schema.json
and each gate's own test, plus two ungranted SKILL.md surfaces), and T-10 because its manifest is
taken at the owner root outside every worktree. The single `team` task, T-09
(`harness-documentor`, DECISIONS.md), declares `depends_on: [T-04, T-06, T-07, T-08]` and is
therefore blocked behind four main-session-direct tasks. **Zero team-owned work is eligible**, so
no lead has been dispatched and no run has been opened.

The next action is T-01, and it is the main session's: `depends_on: [T-10]` is now satisfied.

`notes/handoff-plan.md` said to dispatch T-10 to `harness-eng-lead`. That was validated against the
plan and REJECTED: `plan.yaml:643-644` lanes T-10 `main-session-direct`. The approved plan governs,
and the main session went on to execute T-10 itself. Superseded by `notes/handoff-build.md`.

`check-state.sh` reports nine INV-26 card/plan mismatches on this feature: eight task cards read
`backlog` where the plan reads `ready`, which is the `gh-sync.py status <dir> ready` signature-time
mirror write, and T-10's card reads `building` where the plan reads `done`. Both are mirror-side and
main-session-owned; neither gates the build. cycles_used 4/10 (unchanged — no rework), runs 10/20
(unchanged — a main-session-direct segment is not a run).

## Open Questions

- Whether T-10's INV-26 mismatch is a harness defect rather than drift. D-23 says nothing moves a
  card to the done station before `gh-sync.py ship`, yet INV-26 demands card equals plan station the
  moment a task records `done`. If so, every task will trip it for the rest of the build.
