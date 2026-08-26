# Handoff — plan phase — FEAT-41-one-station-vocabulary

## Next

The plan is COMPLETE and awaiting the operator's signature. Nothing is built.
The next act is NOT an agent's: the main session signs `approval:` in both
`plan.yaml` and `BRIEF.md`. Until both read `approved`, a build orchestrator
stops at step 0 and returns BLOCKED.

After signature, the build phase starts at T-01 and T-03 (the only tasks with
`depends_on: []` or depending solely on T-01). TWELVE of the thirteen tasks are
`main-session-direct` under DEC-174 and are NOT dispatchable to a squad; only
T-12 (docs, harness-documentor) is a team lane. A build orchestrator that tries
to dispatch T-01 through T-11 or T-13 to eng-lead is making a planning error the
route checker already anticipates.

Sequencing hazard, encoded not narrated: T-09 denies every LLM Edit of plan.yaml.
It depends on T-03, T-04, T-05 and T-08 so the write verbs exist and are proven
before the denial lands. Do not reorder around it.

## Trust

- 13 tasks, 12 main-session-direct, 11 decisions, approval pending — verified by me, safe_load at ee66ae2
- check-plan-routes.py exits 0, "0 violation(s) across 2 plan(s)" — verified by me at ee66ae2
- INV-26 FEAT-40 violation is LIVE and in scope; T-10 closes it, SC-09 asserts it — verified by me, check-state.sh run at ee66ae2
- T-06's deletion set is exactly six lines (1403,1404,1405,1432,1475,1501) — verified by me, grep at ee66ae2
- T-13's grep excludes worktrees; without it, 338 worktree files vs 10 live — verified by me at ee66ae2
- D-07's gate costs about 26 ms, not the 40 ms first estimated — measured by me, 10 runs
- SC-02's corrected count is 27 across 5 files — pm measured, I did NOT re-verify the per-file split | UNVERIFIED
- D-11 reprices gh_board import as already-paid — eng-lead verified at source; I did not | UNVERIFIED
- "every sub-issue lands at backlog on open", the premise under D-11's ready-projects-to-backlog exception — pm's claim | UNVERIFIED

## Dead Ends

- Do not re-run the four-angle simplify pass on this plan — it ran, returned nine blocking findings, all applied, and the architecture passed twice
- Do not re-open the tool name, the feature-level `status:` field, the mandate, or lowercase-everywhere — settled in the grilling and in D-01/D-02
- Do not propose a team lane for any file under .claude/skills/harness/bin/ — DEC-174 forbids it and check-plan-routes.py will call it a deviation
- Do not add a glossary task without the operator's word — it is a WARN that fires independently of this feature
- Do not cite runs/*/digest.md as durable evidence — .gitignore:7 makes run dirs worktree-local and they die with the checkout; notes/ survives

## Working Set

- .harness/harness/features/FEAT-41-one-station-vocabulary/plan.yaml
- .harness/harness/features/FEAT-41-one-station-vocabulary/BRIEF.md
- .harness/harness/features/FEAT-41-one-station-vocabulary/notes/orchestrator-measurements-2026-08-25.md
- .harness/harness/features/FEAT-41-one-station-vocabulary/feature.json
- .harness/notes/grilling-845-one-vocabulary-2026-08-25.md
