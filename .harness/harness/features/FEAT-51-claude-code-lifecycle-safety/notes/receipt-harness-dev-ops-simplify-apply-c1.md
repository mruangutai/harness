# SIMPLIFY — APPLY step — FEAT-51 — c1

**BLUF:** Applied the one appliable simplification finding (`COLLECT_FIXTURE`'s repeated
`shared` list, my own SIMPLIFICATION-angle finding) to
`.claude/skills/harness/bin/test-harness-yaml.py`. Both suites re-run at baseline: unit
exit 0 / 0 FAIL, integration exit 1 / 7 FAIL, all seven in the `test-check-plan-routes.py`
manifest-DEVIATION family. Main checkout unaffected. No commit made.

## Edit as applied

File: `.claude/skills/harness/bin/test-harness-yaml.py`

1. Inserted, immediately above `COLLECT_FIXTURE` (after the existing D-03 comment block,
   now lines 31-39):
   ```python
   # The nine `shared` manifest paths every agent's row below repeats verbatim. ONE literal
   # list, still not derived from harness_yaml — same reason the fixture as a whole is inlined
   # (see above): this must catch harness_yaml disagreeing with the manifest, never agree with
   # it by construction.
   SHARED_MANIFEST_PATHS = [
       ".harness/*/features/*/quarantine/**",
       "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
       "pyproject.toml", "uv.lock", "requirements.txt", "tsconfig.json",
   ]
   ```
2. Replaced each of the six inline 5-line `shared` lists (pre-edit lines 41-45, 58-62,
   77-81, 94-98, 117-121, 132-136 — for `harness-backend-dev`, `harness-dev-ops`,
   `harness-pm`, `harness-documentor`, `harness-eng-lead`, `harness-orchestrator`
   respectively) with a single line `SHARED_MANIFEST_PATHS,` at the same 8-space
   indentation, each as the second tuple element.
3. Nothing else touched. Diffed all nine strings against the pre-edit copies before
   deleting them — byte-identical.

## Two invariants verified by construction

- `SHARED_MANIFEST_PATHS` is a plain module-level Python literal in the test file. It is
  never computed from `harness_yaml.manifest_domains`, `.harness/team-config.yaml`, or
  anything else — confirmed by inspection of the post-edit file (lines 31-39): the RHS is
  a bracketed literal, no call expression.
- The nine strings are byte-identical to what all six inline copies held (verified before
  replacing; all six pre-edit copies were themselves already byte-identical to each other
  per the prior SIMPLIFICATION-angle receipt).

## Six-comparisons-preserved confirmation

`test_manifest_domains_matches_the_regex_walk_on_the_real_manifest` (now ~line 175) is
byte-unchanged: still `for agent, (expected_mine, expected_shared) in
COLLECT_FIXTURE.items():` with one `assert list(mine) == expected_mine` and one
`assert list(shared) == expected_shared` per iteration. `COLLECT_FIXTURE` still has six
keys, each a 2-tuple; the second tuple element's value is now the same object
(`SHARED_MANIFEST_PATHS`) for all six agents instead of six separately-authored literals,
but `.items()` yields six entries and the loop body performs six independent comparisons
before the edit and six after — count and per-iteration assertion shape unchanged.

## Suite results

Both runners' own exit status captured separately from `^FAIL ` count, from the worktree:

```
unit_exit=0
grep -c '^FAIL ' /tmp/f51-unit.log  →  0
integration_exit=1
grep -c '^FAIL ' /tmp/f51-int.log   →  7
```

Required end state: unit exit 0 / 0 FAIL — **met**. Integration exit 1 / 7 FAIL — **met**.
No eighth failure; no regression from the apply.

Seven named failures (`grep '^FAIL ' /tmp/f51-int.log`), all in the
`test-check-plan-routes.py` manifest-DEVIATION family (caused by T-03's approved route line
existing on the branch's `.harness/team-config.yaml` and not on main's, per `harness_yaml`
`_manifest_deviation`'s own docstring, which records that an intended manifest deviation is
expected here):

1. `case_04_all_granted_exits_0` — MANIFEST deviation vs `/Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml`
2. `case_05_ungranted_declared_main_session_exits_0` — same MANIFEST deviation
3. `case_15_deviation_plan_still_exits_0` — same MANIFEST deviation
4. `case_17_midpattern_wildcard_grant_exits_0` — same MANIFEST deviation
5. `case_19d_explicit_path_unaffected_by_the_root_guard` — exit 1, stdout shows
   `DEVIATION .../worktrees/.../.harness/team-config.yaml differs from
   .../GitHub/harness/.harness/team-config.yaml; routes we[re granted differently]`
6. `case_19d2_explicit_path_with_no_tasks_still_exits_0` — same DEVIATION stdout
7. `test-check-plan-routes.py` — the file-level summary line for the above six case
   failures inside that one script

All seven trace to the one pre-existing, approved manifest-deviation condition — none is a
regression caused by this apply.

## Main checkout status (proof the write landed in the worktree only)

`git -C /Users/molchairuangutai/GitHub/harness status --porcelain`:

```
?? .harness/harness/features/BUG-1030-stale-anchor-write-hazard/notes/review-harness-ui-reviewer-c1.md
?? .harness/harness/features/BUG-1080-inv6-plan-phase-runs/notes/qa-digest-validation-bug1080.md
?? .harness/harness/features/BUG-251-inv35-hash-truncation/
?? .harness/logs/2026-09-01.md
?? .harness/notes/grilling-factory-control-plane-root-2026-09-01.md
?? .harness/notes/grilling-metrics-dashboard-2026-09-01.md
```

None of these paths touch `test-harness-yaml.py` or FEAT-51; all are pre-existing untracked
artifacts from unrelated features/logs in the ambient main checkout. No FEAT-51 write
leaked outside the worktree.

## Not committed

Working tree left dirty in the worktree per instruction; the orchestrator holds the commit
pen (DEC-153).
