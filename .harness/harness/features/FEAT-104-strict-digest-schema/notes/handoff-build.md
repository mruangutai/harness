# Handoff — FEAT-104-strict-digest-schema, build → validate — written at ce1fd115, seq-4

## Next

Main session pins `review_sha` at `ce1fd115` in `feature.json`, then runs
`gh-sync.py status .harness/harness/features/FEAT-104-strict-digest-schema review` — the pin fixes
what is reviewed, the station write moves parent 1584 and sub-issues 1585–1593 off `building`. Both
BEFORE the panel is dispatched (INV-6). Build is complete: every task in `plan.yaml` reads `done`,
the blocking `qa_gate` PASSES and SIMPLIFY has run. Decide first whether to land simplify's S2 and
S4 directly under DEC-174 — an apply commit AFTER the pin moves the tip and invalidates the panel's
verdict, so it is now or as briefing rows.

## Trust

- Build is complete: all nine tasks `status: done` — `plan.yaml:106,277,330,389,439,499,532,588,646`
  — verified-at ce1fd115
- The blocking gate passes at the tip: `env -u HARNESS_AGENT_TYPE bash
  .agents/skills/harness/bin/run-unit-tests.sh` exits 0 over 106 files, run by this orchestrator
  both before and after the simplify apply — `runs/2026-09-09-02-qa-gate-validator/digest.md`
  (operative verdict is the LAST anchor, line 216 PASS) — verified-at ce1fd115
- T-09's own `verify:` exits 0 with an empty index diff and the `closed digest contract` phrase
  present — `plan.yaml:594-597`, DEC-223 at `.harness/harness/docs/DECISIONS.md:7092` —
  verified-at ce1fd115
- SIMPLIFY ran and gates nothing: four angles, `must_fix: []`, one finding applied by the main
  session at ce1fd115 — `runs/2026-09-09-03-simplify-eng/digest.md` §S1 — verified-at ce1fd115
- S2 and S4 are UNAPPLIED and are the panel's to see, not defects it may assume handled — same
  digest §S2, §S4 — verified-at ce1fd115
- The `^FAIL ` line count is NOT a suite signal: `tests/unit/test-factory-claim-mutation.py:98`
  builds that literal prefix and prints it at :140 and :199 as its own mutation proof. Exit status
  is the signal — verified-at ce1fd115

## Dead ends

- Do not route the INV-26 FEAT-104 card/plan mismatches as this feature's defects: cards read
  `building` against a plan reading `done` because D-23 moves no card to the done station before
  `gh-sync.py ship` — `.agents/skills/harness/references/github-mirror.md`, station-writer table —
  verified-at ce1fd115
- Do not route INV-29's `qa-bug440-c3-probe` worktree either; its path is outside the worktrees
  segment so no removal command can be composed, and it predates this feature — `check-state.sh`
  run in this worktree — verified-at ce1fd115
- Do not let any team agent edit `validate-digest.py`, `check-domain.sh`, `check-state.sh`,
  `run-state-schema.json`, their tests, or the lead agent files: the category governs, not the
  enumeration, and a team edit there already failed one QA run this cycle — DEC-174 —
  verified-at ce1fd115
- Do not follow the plan's line anchors into DEC-126 (2612-2613); they drifted by two. The clause
  was identified by content and is corrected — `.harness/harness/docs/DECISIONS.md:2614-2617` —
  verified-at ce1fd115

## Working set

- `.harness/harness/features/FEAT-104-strict-digest-schema/plan.yaml`
- `.harness/harness/features/FEAT-104-strict-digest-schema/feature.json`
- `.harness/harness/features/FEAT-104-strict-digest-schema/runs/2026-09-09-02-qa-gate-validator/digest.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/runs/2026-09-09-03-simplify-eng/digest.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/notes/qa-feat104-matrix.md`

## Done when

Scope: review_sha pinned at ce1fd115 and the mirror moved to review before any panel dispatch
Authority: brief-sc:SC-13
