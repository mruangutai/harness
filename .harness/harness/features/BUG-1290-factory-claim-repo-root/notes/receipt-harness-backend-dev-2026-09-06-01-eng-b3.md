# Receipt — harness-backend-dev — BUG-1290 B-3 fix cycle (T-01) — issue-map cache coverage

## BLUF

Fixed the fixture. `build_features_root()`'s kaya-ai and harness segments now carry
DIFFERENT, NON-EMPTY `factory.issues` maps (kaya: `{"T-77": 850}`, no `T-88`; harness:
`{"T-99": 954}`), and case 5b's harness plan task now depends on `T-99` (was: no
`depends_on` at all) whose issue is registered CLOSED in the fixture. Both cache-key
mutants (M1 plan-cache, M2 issue-map-cache) now redden case 5b; M2 previously did not
(confirmed against the pre-edit fixture). Only `tests/unit/test-factory-claim.py` changed.

## Change

- `build_features_root()` docstring (:335-340): rewritten to state both caches now
  discriminate, not just the plan.
- kaya-ai segment (:373-378): plan unchanged (`T-77 depends_on ["T-88"]`); issue map
  changed from `{}` to `{"T-77": 850}` — non-empty, still without `T-88`, so kaya still
  resolves to `unresolvable` without ever calling `issue_view`.
- harness segment (:380-383): plan's `T-77` now `depends_on=["T-99"]` (was: no
  `depends_on`, a bare clear task) — a DIFFERENT dep id from kaya's `T-88`, so the
  plan-cache mutant (M1) still reddens too; issue map changed from `{}` to `{"T-99": 954}`.
- Case 5b comment (:1179-1183) and a new `rec.issue_data[954] = issue_data(954, "T-99 do
  the thing", state="CLOSED")` line, registering the fixture the Recorder needs when the
  gate now legitimately reaches `factory_gh.issue_view(repo, 954, ["state"])` for the
  harness candidate. 5b's own assertion expression, its `check()` name string, and case
  5a/5c/5d/5e/5f are byte-identical.

## Acceptance

**1. Unmutated green.**
```
$ python3 tests/unit/test-factory-claim.py
...
124/124 checks passed.
```
Zero `^FAIL ` lines; 5a-5f all `ok` (verified in full run output).

**2. M1 — plan-cache mutant still red** (`/tmp/bug1290_probe_m1.py`, degrades
`_BlockerCache._plans`'s key to `feature` alone):
```
ok    BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
ok    BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
```

**3. M2 — issue-map mutant NOW red** (`/tmp/bug1290_probe_m2.py`, degrades
`_BlockerCache.issue_number`'s key to `feature` alone), run against the post-edit
fixture:
```
ok    BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
FAIL  BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
ok    BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
```
Same probe (M2) run against the PRE-EDIT fixture (`git show HEAD:tests/unit/test-factory-claim.py`,
saved at `/tmp/pre-edit-test-factory-claim.py`) reddens NOTHING — the gap this cycle closes:
```
ok    BUG-1290 5a: served non-harness repository reaches its own segment's blocker verdict, not no_plan
ok    BUG-1290 5b: same feature id on two repositories resolves per-segment, no cache bleed
ok    BUG-1290 5c: absent segment root still refuses via no_plan, naming that segment's own path
```
M1 against the same pre-edit fixture (sanity: the plan-cache half was already proven) is
already red there too, confirming the pre-edit gap was specific to the issue-map cache.

**4. T-01's `verify:` run verbatim:**
```
$ cd .../BUG-1290-factory-claim-repo-root && out=$(python3 tests/unit/test-factory-claim.py 2>&1); rc=0; for m in 5a 5b 5c 5d 5e 5f; do printf '%s\n' "$out" | grep -q "^FAIL  BUG-1290 $m" || { echo "MISSING RED: $m"; rc=1; }; done; test $rc -eq 0
MISSING RED: 5a
MISSING RED: 5b
MISSING RED: 5c
MISSING RED: 5d
MISSING RED: 5e
MISSING RED: 5f
```
Exit status: **1**. Meaning: this command is the T-01 RED-gate, written to measure the
seam's ABSENCE (grep for a `FAIL` marker from every 5x case). T-03 has since landed the
seam, so every case now passes (`ok`), no `FAIL` marker exists for any of them, and the
grep necessarily misses all six — exit 1 is the expected, correct result at this point in
the fix cycle, not a regression; per dispatch instructions this status is reported as an
observation, not treated as this task's own pass/fail.

**5. Integration suite unaffected:**
```
$ python3 tests/integration/test-factory-integration.py
...
131/131 checks passed.
```

**6. No production file changed:**
```
$ git status --porcelain
 M .harness/harness/features/BUG-1290-factory-claim-repo-root/feature.json
 M .harness/harness/features/BUG-1290-factory-claim-repo-root/plan.yaml
 M tests/unit/test-factory-claim.py
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/answers-2026-09-06-b3.md
```
Changes confined to `tests/` and the feature directory. `feature.json`/`plan.yaml`/the
`answers-*` note are pre-existing feature-directory artifacts from this fix cycle's
orchestration, not touched by this task's edit to the test file.

## Mutant probes (evidence, kept out of the repo)

`/tmp/bug1290_probe_m1.py` and `/tmp/bug1290_probe_m2.py` — both import `factory_claim`,
substitute a `_BlockerCache` subclass overriding one method (`_plan` for M1,
`issue_number` for M2) to key on `feature` alone, then `runpy.run_path` the unit suite
(catching its `sys.exit`) and print the 5a/5b/5c lines from captured stdout, restoring the
real `_BlockerCache` class in a `finally`. `/tmp/pre-edit-test-factory-claim.py` is `git
show HEAD:tests/unit/test-factory-claim.py`, the fixture as it stood before this edit.
None of these three files are in the repository.

## Open questions

None.
