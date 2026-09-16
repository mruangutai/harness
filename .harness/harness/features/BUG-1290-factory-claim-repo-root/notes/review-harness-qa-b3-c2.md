# QA measurement — B-3 fixture mutation adequacy — review_sha 7104aa43

**Verdict: the B-3 fixture is adequate.** Both required mutants behave exactly as specified, and no
collateral case is affected by either the cache-key mutation or by perturbing the specific fixture
values this delta changed.

## 1. Baseline

```
$ git -C <worktree> diff 7104aa43 -- tests/unit/test-factory-claim.py
(empty — tree matches the pin for this file)

$ env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py
... 124 "ok" lines ...
124/124 checks passed.
$ echo $?
0
```

## 2. Issue-map mutant (`_BlockerCache.issue_number` re-keyed on `feature` alone)

Used `/tmp/bug1290-orch-probe.py <worktree> issues` after reading it — confirmed its mutation is
exactly this: `key = feature` discarding `repo`, applied to `issue_number`. Ran in-process against
both trees via disposable git worktrees (`git worktree add /tmp/bug1290-pin-tree 7104aa43`,
`.../bug1290-old-tree 76e26386`; both removed after, `git status --porcelain` clean before removal,
no writes to the feature worktree).

```
PIN  (7104aa43): MUTANT=issues cases={'5a':'ok','5b':'FAIL', rest ok} total_FAIL_lines=1
OLD  (76e26386): MUTANT=issues cases={'5a':'ok','5b':'ok',   rest ok} total_FAIL_lines=0
```

Required result met: 5b FAILs at the pin, and the identical mutant reddened NOTHING on the pre-fix
tree. This is the fixture doing its job — before this delta the issue-map cache was unproven.

## 3. Plan mutant (`_BlockerCache._plan` re-keyed on `feature` alone) — regression check

```
PIN (7104aa43): MUTANT=plans cases={'5a':'ok','5b':'FAIL', rest ok} total_FAIL_lines=1
OLD (76e26386): MUTANT=plans cases={'5a':'ok','5b':'FAIL', rest ok} total_FAIL_lines=1
```

5b FAILs at both trees — the plan-cache proof was not traded away for the issue-map proof.

## 4. Collateral — value perturbation, not just key mutation

`build_features_root()`'s two changed segments (`kaya-ai`, `harness`, both under `SEG_FEATURE =
"FEAT-99-seg"`) are consumed ONLY by cases 5a/5b: grepped `SEG_FEATURE`, `kaya-ai`, and the
`REPO_HARNESS_SEG` fixture repo across the whole file — no B*/R*/P*/C*/X case references them.
Every other case's fleet repo resolves to a different `.harness/<segment>/features` path under the
same monkeypatched `fixture_features_root`, so the two changed `feature.json`s and the two changed
`plan.yaml` deps are structurally unreachable outside 5a/5b.

Confirmed by direct perturbation in the disposable pin worktree (edit, run, restore, verify
`git status --porcelain` clean after restore):

- kaya's filler value `{"T-77": 850}` → `{"T-77": 999}` (unasserted — kaya's dep is on T-88, absent
  from kaya's map either way): **0 FAIL lines**, 124/124 pass. This value is not load-bearing;
  correctly so, since 5a/5b's kaya assertion is about T-88 staying unresolvable, not about T-77's
  entry.
- harness's load-bearing value `{"T-99": 954}` → `{"T-99": 999}` (mismatches `rec.issue_data[954]`,
  the CLOSED issue 5b's harness-clear verdict depends on): **exactly 1 FAIL line**,
  `BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed`. Nothing
  else reddens.

## 5. Stays-green-under-its-own-bug audit (5a/5b only)

5b's check is content-specific, not token-presence: `code == 0 and json.loads(out).get("issue") ==
952` (harness's own candidate claimed, not kaya's) `and "951" in err and "unresolvable blocker" in
err` (kaya's candidate named and blocked for the right reason) `and "no plan could be read" not in
err` (rules out the case degrading into a no_plan/misconfiguration read instead of a real blocker
verdict). Directly exercised in §2: the exact re-keying bug the fix addresses turns this from `ok`
to `FAIL` on the pin, and was `ok` (i.e. undetected) on the pre-fix tree — matching what B-3
reported as the panel's finding.

## Verdict inputs

- `matrix_ok: true` — established by `notes/qa-2026-09-06-03-validator.md`; not re-derived here per
  dispatch scope.
- No test file was authored or modified by this review; all perturbations ran in disposable git
  worktrees under `/tmp`, removed after use, never touching the feature worktree or main checkout.
