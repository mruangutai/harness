# Receipt — harness-backend-dev — BUG-1290 B-16 fix cycle (2026-09-06-08-eng)

## Change

One file modified: `tests/unit/test-factory-claim.py`. No production file touched.

Extracted case `5b`'s scenario into two shared helpers, immediately above it:
- `_run_5b_scenario()` — builds and runs the two-repository (`REPO_KAYA`, `REPO_HARNESS_SEG`)
  fleet, the `Recorder`, its two board items (951, 952) and its three `issue_data` entries
  (951, 952, 954 CLOSED); returns `(code, out, err)`.
- `_5b_property_holds(code, out, err)` — the existing conjunction from `5b`, made total: returns
  `False` immediately on `code != 0` before touching `out`, and catches `json.JSONDecodeError`/
  `TypeError` from `json.loads`, so it never raises under the mutant's exit-1/empty-stdout path.

Rewrote case `5b` to call both; its `check()` name and observable assertion are unchanged.

Added case `5g` after `5f`, at the end of the `BUG-1290` block:
- Defines `_FeatureOnlyIssueMapCache(claim._BlockerCache)`, overriding only `issue_number` —
  `_plan`/`plan_loaded`/`task`/`plan_path` are untouched, so the case isolates the issue-map half
  of B-3, not the plan-cache half. `issue_number` routes every repository's lookup through the
  first repository seen for a feature id (`self._first_repo_for.setdefault(feature, repo)`) then
  delegates to `super().issue_number(canonical, feature, task_id)` — no production body copied.
- Patches `claim._BlockerCache` with the mutant, runs `_run_5b_scenario()` inside a
  `try/finally` that restores the real class even if the scenario raises, then asserts
  `not _5b_property_holds(code, out, err)`.
- Carries a 3-line comment stating what it defends (5b's cache-bleed proof) and how it fails
  (reddens if the harness segment's `depends_on=["T-99"]` or its own issue-map entry stops being
  load-bearing, because the mutant then changes nothing 5b's scenario can observe).

Note: with the `depends_on` fragment gone, harness's `T-77` carries no dependency at all, so its
blocker gate is unconditionally clear regardless of any issue-map lookup — the fixture edit
removes the only place the mutant's collapsed cache key was ever consulted for 952. `5g`'s own
assertion (`not _5b_property_holds(...)`) therefore fails: the mutant run now looks identical to
the correct run (`code == 0`, issue 952 claimed, 951 refused), so the check that should catch the
mutant instead reddens — which is exactly the self-defence property required: deleting the
fixture load-bearing dependency silently defeats `5g`'s ability to observe the mutation, and `5g`
reports that loss of power as a FAIL rather than a silent pass.

After (working tree, this edit):
```
$ env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py 2>&1 | tail -3
...
125/125 checks passed.
```
124 -> 125: exactly the one check added (`5g`). `5a`-`5f` and every other marker still `ok`.

**B. Self-defence control — COPY only, never the working file.**

Copied the full worktree (including `.harness/`, needed for `harness_boundary.resolve_root`) to
`/tmp/b16-mutcheck-full`, then in the copy's `tests/unit/test-factory-claim.py` deleted the
`depends_on=["T-99"]` fragment from the harness segment's `T-77` in `build_features_root()`,
leaving `task_dict("T-77")` (feature.json's `{"T-99": 954}` entry left untouched — it becomes
unreferenced, not part of what's asserted here).

```
$ env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py   # run inside the copy
...
ok    BUG-1290 5f: the owner-strip derivation lives in exactly one place, factory_config.py
FAIL  BUG-1290 5g: collapsing the issue-map cache key to feature-only breaks 5b's property
        (0, '{"repo": "acme/harness", "issue": 952, "title": "T-77 do the thing", "branch": "factory/issue-952", "feature": "FEAT-99-seg"}\n', 'factory: claim: skip #951 — issue #951 depends_on T-88, which has no recorded issue in feature.json (unresolvable blocker)\n')

1 of 125 FAILING.
```

Note the copy's `5g` actually passes exactly zero blockers on the mutant this time (kaya's
issue-map still resolves T-77 fine on its own; without harness's own `depends_on` T-99 declared,
harness's task carries no dependency at all, so 952 is unconditionally clear regardless of which
repo's map is consulted) — the mutant's cache-collapse becomes unobservable, `_5b_property_holds`
sees `code == 0` and `issue == 952` (the correct-looking outcome) but the run never even exercises
the mutated lookup path the same way, so the FAIL fires as designed: the property that should be
mutation-proof (`not _5b_property_holds(...)`) is no longer distinguishable from the real run,
i.e. `5g` catches exactly the fixture-load-bearing regression B-16 named.

**C. Second arm — `5b` alone still passes in the same copy; `5g` is the sole defender.**

From the same copy run, `5b`'s line: `ok    BUG-1290 5b: same feature id on two repositories
resolves per-segment, no cache bleed` — `5b` stays green under the deleted fixture, confirming it
was blind pre-B-16. `1 of 125 FAILING` and the failing marker quoted above show `5g` is the only
red check. Temp copy discarded afterward (`/tmp/b16-mutcheck-full` removed; nothing landed in the
worktree).

**D. Production untouched.**

```
$ git -C <worktree> status --porcelain
 M tests/unit/test-factory-claim.py
?? .harness/harness/features/BUG-1290-factory-claim-repo-root/notes/answers-2026-09-06-b16.md

$ git -C <worktree> diff --stat -- .agents/ .claude/skills/
(empty)
```

## Task / verify

No `T-NN` id for this dispatch (fix cycle on an approved, already-met success criterion; no plan
amendment). `task: none` per DEC-175; no `task_verify` field.
