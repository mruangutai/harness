# Handoff — BUG-2161-abandon-source-tickets, build → validate — written at af83b980, seq-7

## Next

Pin `review_sha` to the seam commit that follows this note (the commit carrying plan.yaml with T-01 and T-02 at `done`), run `gh-sync.py status <feature-dir> review`, re-pin to the station commit, then ONE `validate` dispatch to `harness-validator-lead` (`HARNESS-MISSION: validate`, slug `validate-validator`) over that sha: qa enforces the bugfix+docs `test_matrix` with fail-first evidence for SC-01..SC-05, code/security/ui read the diff `5094e854..<pin>`, pm's goal-check grades SC-01..SC-06 by perspective into `notes/research-BUG-2161-abandon-source-tickets-goalcheck-validate-c0.md`. SC-07 is operator-only post-merge UAT and is carved out of the goal-check. Inputs: `plan.yaml` T-01/T-02 (verify verbatim), `BRIEF.md` SC-01..SC-07, D-01..D-03.

## Trust

- T-01 PASS (run 2026-11-03-05-build-eng, cycles 1: one in-run send-back) at 88e15438 + 767e1f0f; T-02 PASS (run 2026-11-03-06-t02-docs-product, cycles 0) at 21bfa01d; SIMPLIFY PASS (run 2026-11-03-07-simplify-eng, cycles 0, four applies, zero corrective fixes) at af83b980 — `feature.json` runs, `runs/<id>/digest.md` — verified-at af83b980
- T-01 signed verify chain exits 0 at af83b980, run by the orchestrator (`env -u HARNESS_AGENT_TYPE`), 265 ok/PASS lines, zero FAIL — `/tmp` run log not durable; re-run the chain from the worktree root — verified-at af83b980
- T-02 verify (`gen-decisions-index.py --stdout | diff`) exits 0 empty at 21bfa01d, run by the orchestrator — verified-at 21bfa01d
- Both tasks at `done` in `plan.yaml`; feature station `building`; cards #2161/#2162/#2163/#2164 at Building — `plan.yaml`, gh-sync output — verified-at af83b980
- `cycles_used: 1` of 10; rework ruling 2 rounds / 90 min, rework_minutes 0 — `feature.json` — verified-at af83b980
- Leads return by final message; the fenced YAML must be validated (`validate-digest.py <persona> <json>`) and appended to `runs/<id>/digest.md` by hand before close-run — `observations/harness-orchestrator.md` — verified-at af83b980

## Dead ends

- No second goal-check before validate and no re-panel; the validate goal-check is the feature's second and last (SC-09) — `plan-phase.md`, `build-phase.md` step 5 — verified-at af83b980
- SC-07 (live #1774 disposal) is post-merge UAT; no run may claim it, and a goal-check returning it unmet is not a fix cycle — BRIEF SC-07, `## Verification gaps` — verified-at af83b980
- No PR, push, merge, deploy; the merge is the operator's — dispatch boundaries — verified-at af83b980
- Run-dir slugs end `-eng|-product|-validator` — `feature.json` run 2026-11-02-02-engineering BLOCKED — verified-at af83b980

## Working set

- .harness/harness/features/BUG-2161-abandon-source-tickets/plan.yaml
- .harness/harness/features/BUG-2161-abandon-source-tickets/BRIEF.md
- .harness/harness/features/BUG-2161-abandon-source-tickets/feature.json
- .harness/harness/features/BUG-2161-abandon-source-tickets/runs/2026-11-03-07-simplify-eng/digest.md
- /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/references/build-phase.md

## Done when

Scope: review_sha pinned, station at review, one validate run dispatched and graded over the pin
Authority: brief-perspective:.harness/harness/features/BUG-2161-abandon-source-tickets/BRIEF.md#code maintainer
Authority: brief-perspective:.harness/harness/features/BUG-2161-abandon-source-tickets/BRIEF.md#operator
