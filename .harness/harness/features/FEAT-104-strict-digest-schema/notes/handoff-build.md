# Handoff — FEAT-104-strict-digest-schema, build → validate — written at e53f252b, seq-4

## Next

Main session pins `review_sha` at `e53f252b`, the branch tip, then runs
`gh-sync.py status .harness/harness/features/FEAT-104-strict-digest-schema review` — the pin fixes
what is reviewed, the station write moves parent 1584 and sub-issues 1585–1593 off `building`. Both
BEFORE the panel is dispatched (INV-6). The code boundary is `ce1fd115`; `e53f252b` adds only this
feature's own records, so pinning at the tip reviews the same code. Decide FIRST whether to land
simplify's S2 and S4 directly under DEC-174: an apply commit after the pin moves the tip and
invalidates the panel's verdict, so it is now or as briefing rows.

## Trust

- Build is complete: all nine tasks `status: done` — `plan.yaml:106,277,330,389,439,499,532,588,646`
  — verified-at e53f252b
- The blocking gate passes at the code tip: `env -u HARNESS_AGENT_TYPE bash
  .agents/skills/harness/bin/run-unit-tests.sh` exits 0 over 106 files, run by this orchestrator
  both before and after the simplify apply — `runs/2026-09-09-02-qa-gate-validator/digest.md`
  (operative verdict is the LAST anchor, line 216 PASS) — verified-at ce1fd115
- `e53f252b` changes no path outside the feature directory relative to `ce1fd115` — `git diff
  --stat ce1fd115 e53f252b` with the feature dir excluded is empty — verified-at e53f252b
- T-09's own `verify:` exits 0 with an empty index diff and the `closed digest contract` phrase
  present — `plan.yaml:594-597`, DEC-223 at `.harness/harness/docs/DECISIONS.md:7092` —
  verified-at e53f252b
- SIMPLIFY gates nothing: four angles, `must_fix: []`, one finding applied by the main session at
  ce1fd115; S2 and S4 stay UNAPPLIED and are the panel's to see, not defects it may assume handled
  — `runs/2026-09-09-03-simplify-eng/digest.md` §S1, §S2, §S4 — verified-at e53f252b

## Dead ends

- Do not route the INV-26 FEAT-104 card/plan mismatches as this feature's defects: cards read
  `building` against a plan reading `done` because D-23 moves no card to the done station before
  `gh-sync.py ship` — `.agents/skills/harness/references/github-mirror.md`, station-writer table —
  verified-at e53f252b
- Do not route INV-29's `qa-bug440-c3-probe` worktree either; its path is outside the worktrees
  segment so no removal command can be composed, and it predates this feature — `check-state.sh`
  run in this worktree — verified-at e53f252b
- Do not let any team agent edit `validate-digest.py`, `check-domain.sh`, `check-state.sh`,
  `run-state-schema.json`, their tests, or the lead agent files: the category governs, not the
  enumeration, and a team edit there already failed one QA run this cycle — DEC-174 —
  verified-at e53f252b
- Do not read a `^FAIL ` line count as a suite signal: `tests/unit/test-factory-claim-mutation.py`
  builds that literal prefix at :98 and prints it at :140 and :199 as its own mutation proof, so a
  green run still shows several. Exit status is the signal — verified-at e53f252b

## Working set

- `.harness/harness/features/FEAT-104-strict-digest-schema/plan.yaml`
- `.harness/harness/features/FEAT-104-strict-digest-schema/feature.json`
- `.harness/harness/features/FEAT-104-strict-digest-schema/runs/2026-09-09-02-qa-gate-validator/digest.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/runs/2026-09-09-03-simplify-eng/digest.md`
- `.harness/harness/features/FEAT-104-strict-digest-schema/notes/qa-feat104-matrix.md`

## Done when

Scope: review_sha pinned at the tip and the mirror moved to review before any panel dispatch
Authority: brief-sc:SC-13
