# Receipt — harness-backend-dev — T-02 (BUG-1290-factory-claim-repo-root)

## Task
T-02: Move both integration claim fixtures onto the repository's own segment.
File touched (only): `tests/integration/test-factory-integration.py`

## Changes made

1. **Case (F), FEAT-INTEG-HAPPY** — `:879-882` (post-edit): replaced the hardcoded
   `os.path.join(root, ".harness", "harness", "features", feat)` with
   `os.path.join(root, ".harness", REPO.split("/", 1)[-1], "features", feat)`, deriving the
   segment from module-level `REPO = "acme/widget"` rather than typing `widget` a second
   time. Reworded the preceding comment (was: "The fixture plan lives exactly where
   factory_claim's (import-time) FEATURES_ROOT will look for it under this case's
   HARNESS_PROJECT_DIR") to state instead that the fixture lives where claim resolves
   REPO's own features root.

2. **Case (H), FEAT-INTEG-TWOBOARD** — `:1245-1246` (post-edit): same treatment,
   `feat_dir = os.path.join(root, ".harness", REPO.split("/", 1)[-1], "features", feat)`.
   No other line in case (H) touched — decompose (`:1257`), claim (`:1263`), land
   (`:1270`), and the gh-call assertions are byte-identical to before the edit.

3. **File docstring, `:28-30` (pre-edit)** — the sentence claiming
   `factory_claim.py`'s import-time `FEATURES_ROOT` resolves under the case's temp root
   was reworded to state it now resolves per candidate, to
   `<HARNESS_PROJECT_DIR>/.harness/<segment>/features`, never this checkout's real
   `.harness/harness/features`. Preserved the follow-on clause ("This is also why a
   case's own `.harness/factory/fleet.yaml` is never created...") that the original
   sentence fed into, so the paragraph still reads coherently.

4. No case added. No production file touched. No other test file touched.

## Verify — run verbatim, cross-checked against plan.yaml T-02 `verify:` block (identical)

```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1290-factory-claim-repo-root && out=$(python3 tests/integration/test-factory-integration.py 2>&1); printf '%s\n' "$out" | grep -q '^FAIL  (F) claim exits 0' && printf '%s\n' "$out" | grep -q '^FAIL  (H) claim against the two-board fleet exits 0'
```

Result: **exit 0** (both grep -q calls matched).

Actual relevant output lines (grepped from the same run):

```
ok    (F) decompose exits 0
ok    (F) decompose: stdout is one JSON object
ok    (F) decompose: one issue per task
ok    (F) decompose: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (F) decompose: both board items boarded at the fleet's declared ready station
FAIL  (F) claim exits 0
FAIL  (F) claim: stdout is one JSON object
FAIL  (F) claim: board item actually moved to Building
ok    (F) claim: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
FAIL  (F) workspace exits 0
FAIL  (F) workspace: stdout is one JSON object
ok    (F) workspace: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
FAIL  (F) workspace: recorded git commands include a checkout of factory/issue-<n>
FAIL  (F) land exits 0
FAIL  (F) land: stdout is one JSON object
FAIL  (F) land: board item actually moved to Review
ok    (F) land: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
FAIL  (F) land: recorded git commands include a push of factory/issue-<n> to origin
ok    (H) decompose against the two-board fleet exits 0
ok    (H) decompose: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
FAIL  (H) claim against the two-board fleet exits 0
ok    (H) claim: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
FAIL  (H) land against the two-board fleet exits 0
ok    (H) land: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (H) at least one gh call was recorded (anti-vacuum)
ok    (H) no recorded gh call names the other repository's board number
ok    (H) at least one recorded gh call names the served repository's own board number (proves the check above has power)
```

Tallies: 113 `ok` lines, 12 `FAIL` lines (both required markers `FAIL  (F) claim exits 0` and
`FAIL  (H) claim against the two-board fleet exits 0` are present, plus expected downstream
cascade FAILs in (F) workspace/land and (H) land, since decompose already stored plans under the
new per-repo path while claim still resolves the old hardcoded harness path — exactly the RED
state PANEL-01/T-02 calls for). Baseline at eb9d044e (unmodified) was reported by the plan as
exit 0, 131 ok, 0 FAIL — the new red state proves the fixture move actually exercises the seam
gap, not a vacuous file break.

## Notes for T-03

Both fixtures now build their `feat_dir` on `REPO.split("/", 1)[-1]` ("widget"), matching
`segment_of` T-03 is about to add. T-03's own verify (T-03 `&&`-chain) should turn both cases'
`claim`/`workspace`/`land` FAILs green once `factory_claim.py` resolves the features root
per-repository instead of the hardcoded `harness` segment.
