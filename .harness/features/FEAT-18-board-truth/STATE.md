# STATE

## Current

- feature: FEAT-18-board-truth
- run: .harness/features/FEAT-18-board-truth/runs/t03-eng/state.yaml
- squad: eng
- status: building

**Three of six tasks are done.** T-01 and T-05 at `1fd6f9a`, T-02 at `4755b6e`; sub-issues #327, #331
and #328 closed on the mirror. All gates green at HEAD, re-run by me rather than taken from a digest:
unit 0, integration 0, `check-state.sh` 0 with no FEAT-18 finding, `check-plan-routes.py` 0
violations. `run-unit-tests.sh` no longer reports `MISCONFIGURED` — the main session registered both
`test-gh-board.py` and `test-branch-create-gate.py` in `UNIT_SCRIPTS` in T-02's turn, which is what
closed the declared transient.

**One rework cycle spent, 1 of 10** — T-05's missing unit test. The operator settled the surface
question by amending T-05's `files:` list and **re-signing the plan at `3862a64`**, so the plan now
matches the tree and the mismatch is closed, not carried.

**In flight: T-03**, the only remaining team task — `start-task`, the derived parent station, and the
loud-and-continue failure posture in `gh-sync.py`. Then T-04 and T-06 go back to the main session
together as one relay; both are `main-session-direct` and neither is mine to attempt.

**Sequencing decision, mine:** the `test_matrix` qa segment runs **after all six tasks land**, not
after T-03. The build is split across main-session relays, so a qa run now would gate an incomplete
diff and would have to re-run anyway once T-04 adds `test-check-state.py`. `review_sha` gets pinned
at the commit containing all six before any validator run.

## Open Questions

- None blocking. Q1 and Q3 were answered at signature in `BRIEF.md`'s `## Approval` block — D-05's
  three board keys stay in `harness.json`, knowingly temporary pending `#206`. Q2 was overtaken by
  the 2026-08-13 revision. Q4 was settled by the operator with a re-signature. Q5 is moot: the
  advisor is unavailable this session, so judgement calls are made unreviewed and said to be so.
- Standing, for the ship review rather than for anyone to fix: **no criterion in this feature
  observes GitHub.** Every automated criterion runs against a fake `gh` because `functional` has
  `cmd: null` (DEC-187), and striking SC-08 removed the only live-API criterion. Signed knowingly.
