# Receipt — harness-dev-ops — B-16 independent re-check — BUG-1290

BLUF: all four claims CONFIRMED. 125/125 green in the worktree; the committed baseline
independently re-derives to 124 (delta exactly 1); the self-defence control on a scratch copy
reddens `5g` alone while `5b` stays ok; production tree shows exactly one modified tracked file
(`tests/unit/test-factory-claim.py`) with an empty `.agents/`/`.claude/skills/` diffstat.

## M1 — working-tree suite

Command: `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py` (run from worktree root)

Exit: 0

Markers:
```
ok    BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
ok    BUG-1290 5g: collapsing the issue-map cache key to feature-only breaks 5b's property
```

Summary line (verbatim): `125/125 checks passed.`
`ok` count: 125. `not ok`/`FAIL` count: 0.

**Claim "125/125 checks passed" — CONFIRMED.** Both `5b` and `5g` present and `ok`.

## M2 — previous count, independently derived

- Copied the worktree to `/tmp/b16_m2`.
- Obtained the committed (pre-edit) test file via `git -C <worktree> show HEAD:tests/unit/test-factory-claim.py` → `/tmp/committed_test_factory_claim.py`.
- Overwrote only `tests/unit/test-factory-claim.py` in the `/tmp/b16_m2` copy with that content.
- Ran: `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py` from `/tmp/b16_m2`.

Exit: 0. Summary line (verbatim): `124/124 checks passed.` `ok` count: 124.

Delta: 125 (M1) − 124 (M2) = **1**.

**Claim "delta is exactly 1" — CONFIRMED.**

## M3 — self-defence control, on a copy only

- Fresh copy at `/tmp/b16_m3` (separate from M2's copy).
- In the copy only, inside `build_features_root()`, changed the `harness_seg` plan write
  (originally line 382) from
  `plan_dict(SEG_FEATURE, [task_dict("T-77", depends_on=["T-99"])]))` to
  `plan_dict(SEG_FEATURE, [task_dict("T-77")]))` — verified the sibling `kaya_seg` write on
  line 377 (`task_dict("T-77", depends_on=["T-88"])`) was untouched (grep confirmed both lines
  before and after the edit; only line 382 changed).
- Ran: `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py` from `/tmp/b16_m3`.

(a) Verbatim FAIL marker line:
```
FAIL  BUG-1290 5g: collapsing the issue-map cache key to feature-only breaks 5b's property
        (0, '{"repo": "acme/harness", "issue": 952, "title": "T-77 do the thing", "branch": "factory/issue-952", "feature": "FEAT-99-seg"}\n', 'factory: claim: skip #951 — issue #951 depends_on T-88, which has no recorded issue in feature.json (unresolvable blocker)\n')
```

(b) Verbatim summary line: `1 of 125 FAILING.`

(c) `BUG-1290 5b` in this run: `ok    BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed` — still `ok`.

(d) Failing-marker count: exactly 1 (`5g` only). `ok` count: 124 (124 + 1 fail = 125 total, matching M1's total case count).

**Claim "5g is the sole failure, 5b still ok" — CONFIRMED.** No marker other than `5g` failed.

## M4 — production byte-identity and tree state

`git -C <worktree> status --porcelain` (full, verbatim):
```
 M tests/unit/test-factory-claim.py
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/answers-2026-09-06-b16.md
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/receipt-harness-backend-dev-2026-09-06-08-eng-b16.md
```
Every modified tracked path: exactly one — `tests/unit/test-factory-claim.py`. The two `??`
entries are untracked bookkeeping notes under this feature's own directory (expected, not
violations).

`git -C <worktree> diff --stat -- .agents/ .claude/skills/` (verbatim): *(empty output)*

`git -C <worktree> diff --stat` (full, verbatim):
```
 tests/unit/test-factory-claim.py | 65 +++++++++++++++++++++++++++++++++++-----
 1 file changed, 57 insertions(+), 8 deletions(-)
```

**Claim "one modified tracked file, empty production diffstat" — CONFIRMED.**

## Tree state at end of run

Re-ran `git -C <worktree> status --porcelain` after all four measurements and cleanup of every
`/tmp` copy (`/tmp/b16_m2`, `/tmp/b16_m3`, `/tmp/committed_test_factory_claim.py`, and scratch
logs). Output is identical to the M4 snapshot above (this receipt file did not yet exist at that
check; it is the only file this run added, at the dispatched receipt path). No other file in the
worktree was touched.

## Verdict basis

All four claims CONFIRMED with no discrepancy. This supports a PASS verdict for the B-16 fix
cycle from the re-measurement side.
