# Handoff — FEAT-32, plan → build — written at b1281df, seq-1

<!-- Written by the ship-phase orchestrator crossing the seam, not by the plan-phase
     author: the plan phase ended at the operator's signature without leaving a note.
     Nothing here is attributed to that predecessor. -->

## Next

Build segment A is dispatched: the `build` team to eng-lead with T-02 (plan.yaml:440-559),
then T-03 (:560-738), T-04 (:739-840), T-05 (:841-934) — all `harness-backend-dev` per the
`lanes:` block (plan.yaml:9-80). After it returns: T-06 (gated on main-session T-01), then
T-10 (gated on T-07), then the documentor segment T-13 → T-17 (gated on T-08, T-09).

## Trust

- Both signatures read `approved` / `operator` / `2026-08-22` — plan.yaml:4-7, BRIEF.md:431-435 — verified-at b1281df
- The worktree is current with main and the merge was clean — `git log` shows b1281df merging d1a8c56 — verified-at b1281df
- 17 tasks; 9 are main-session-direct (T-01, T-07, T-08, T-09, T-11, T-12, T-14, T-15, T-16) and 8 are the team's — dispatch brief + plan.yaml `lanes:` rows — verified-at b1281df
- The GitHub mirror opened: milestone 21, parent #700 `created`, sub-issues #701-717 — feature.json `github` — verified-at b1281df
- **feature.json writes are DENIED right now.** `RUNS_AGENT_EXEMPT` in `feature_schema.py` holds FEAT-01..FEAT-31 only, so FEAT-32 defaults to 0 exemptions and all 5 legacy runs fail the `agent` rule. The main session is fixing it in the main checkout (hooks resolve via `CLAUDE_PROJECT_DIR`) — evidence: `feature_schema.py:160-207` + coordinator message — verified-at b1281df
- SC-14 naming 221 as its basis is a CARRIED open question the operator declined to overturn, not an oversight — STATE.md `## Open Questions` Q2 — UNVERIFIED at this sha (inherited from the plan phase)

## Dead ends

- Do NOT backfill `agent` into the 5 legacy runs entries to unblock feature.json — the indices are load-bearing and the runs predate the rule by two hours (`d03a835` 06:40 vs `ee608d2` 08:48) — coordinator instruction, this run
- Do NOT re-merge main, re-run the signature hash check, or touch FEAT-26's unapproved-BRIEF violation in `check-state.sh` — all three discharged or pre-existing — dispatch brief, this run
- Do NOT edit any main-session-direct surface, `feature_schema.py` included and being edited live — plan.yaml `lanes:` rows + coordinator message — verified-at b1281df

## Working set

- `.harness/harness/features/FEAT-32-concurrent-write-merge/plan.yaml` (read by line range; 153 KB)
- `.harness/harness/features/FEAT-32-concurrent-write-merge/feature.json`
- `.harness/harness/features/FEAT-32-concurrent-write-merge/STATE.md`
- `.claude/skills/harness/teams/build.yaml`
- `.claude/skills/harness/bin/run-unit-tests.sh` (`--check-kinds` before every commit)
