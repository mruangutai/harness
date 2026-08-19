# STATE

## Current

- feature: FEAT-29-graphql-budget
- run: none in flight — `runs/2026-08-19-02-eng/` returned PASS for T-03
- squad: none
- status: Building — blocked on two layer-0 items before the qa gate can run

**All nine tasks are written.** T-03 landed in its six amendment-4 files: unit **160 PASS / 0 FAIL /
exit 0**, up from the 139 baseline, both mandated mutations proven red on named checks and reverted
under sha256 verification. Send-backs 0, so `cycles_used` stays 3. Branch tip `29c3e9d`.

**THE BRANCH IS RED ON `--kind integration` AND THE CAUSE IS OURS.** Six named INV-26 checks in
`test-check-state.py` fail, each reporting `(no INV-26 line)` — the invariant goes silent where it
must speak, issue #588's shape. The squad reported them pre-existing; I bisected in a throwaway
worktree instead of relaying: `bee6234` 0 FAIL → `9fd11d7` 6 FAIL → `29c3e9d` 6 FAIL. **T-01/T-02
caused it, not T-03.** The member's baseline was taken at `d610822`, which already contained T-02, so
its claim was honest in its own frame and wrong in the feature's.

**Production is not at fault.** The fixture's fake `gh` serves `project item-list`
(`test-check-state.py:1315-1322`), the call T-02 replaced; `project_item_stations` raises and
`check-state.sh` swallows it. A live read returned all 486 board-3 cards with correct stations for 5
points. The fixture is stale. `test-check-state.py` is the test file of `check-state.sh`, so under
DEC-174 am.4 its repair is main-session-direct. Nothing could have caught this earlier: T-02 is
`change_type: logic` → unit only, and `test-check-state.py` is in `INTEGRATION_SCRIPTS`.

Second layer-0 item: `.harness/logs/gh-cost-2026-08-19.jsonl` is untracked in the tree, written by the
*existing* suite because T-03's signed default is ON and `harness_root()` falls back to the real
checkout. `--resolve` is `NOBODY`. Not staged by me.

**THE MIRROR REMAINS FROZEN** — no `start-task`, no `close-task`, for any task until T-07's
after-measurement lands. Seven positive-control lines depend on cards reading `Backlog`. `plan.yaml`
records T-03 `done` with its subcommand deliberately unrun.

Next once both clear: qa segment (blocking `test_matrix`; T-03 is `change_type: feature` → unit AND
integration, which is why the fixture must be green first) → SIMPLIFY → re-run suites → pin
`review_sha` at the tip → panel → goal-check → close-out.

Budget: GraphQL 6/5000 at this window's start; 46 points spent all session. 3 cycles of 10; 3 runs
of 20.

## Open Questions

- Q1 (blocking, operator): repair `test-check-state.py`'s INV-26 fake to answer the GraphQL query
  T-02 introduced. Carve-out file, so main-session-direct. Evidence in
  `notes/layer0-batch-b-FEAT-29.md` §A.
- Q2 (blocking, operator): `.harness/logs/gh-cost-<date>.jsonl` is written into the real checkout by
  the test suite. Four routes named in §B; all four are layer-0.
- Q3 (non-blocking): `--kind integration` runtime rose materially — two extra `rate_limit` forks per
  wrapped `gh` call. Pass/fail unchanged. Accept, or sample the counter rather than read per call?
- Q4 (non-blocking): T-02's `change_type: logic` maps to `unit` alone, so a change to the function an
  integration-tested invariant depends on had no path to its own test. A matrix question, not a
  member's error.
