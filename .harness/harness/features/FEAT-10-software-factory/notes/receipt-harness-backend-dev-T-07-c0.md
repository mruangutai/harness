# Receipt — harness-backend-dev — T-07 (c0)

## Result

PASS. `factory_land.py` opens a pull request and stops, exactly as T-07's intent specifies.
`test-factory-land.py` is test-first (RED confirmed on `ModuleNotFoundError` before any
production code existed), 45/45 checks green, registered in `run-unit-tests.sh`.

## Baseline (before this task)

`--kind unit` (before): 9 files, exit 0. Captured at `/tmp/baseline-unit.txt`:

```
PASS test-harness-yaml-corpus.py
PASS test-render-brief.py
PASS test-team-catalog.py
PASS test-factory-cli.py
PASS test-factory-gh.py
PASS test-factory-config.py
PASS test-factory-workspace.py
PASS test-factory-decompose.py
PASS test-factory-claim.py
```

`--kind integration` (unaffected by this task, re-confirmed after landing): 13 files, exit 0.
Captured at `/tmp/v-t07-integration.txt`.

## Verify — verbatim command and output

Command (character-exact from plan.yaml:1369):

```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit > /tmp/v-t07.txt 2>&1; s=$?; grep -q "^PASS test-factory-land.py$" /tmp/v-t07.txt && [ "$s" -eq 0 ]
```

Result: **RESULT=0** (verify command's own compound exit), **exit_status=0** (the suite's own
`$?`).

Unit suite file list after this task (10 files, all PASS):

```
PASS test-harness-yaml-corpus.py
PASS test-render-brief.py
PASS test-team-catalog.py
PASS test-factory-cli.py
PASS test-factory-gh.py
PASS test-factory-config.py
PASS test-factory-workspace.py
PASS test-factory-decompose.py
PASS test-factory-claim.py
PASS test-factory-land.py
```

`test-factory-land.py`'s own summary line, verbatim: `45/45 checks passed.`

## RULINGS honoured

- **R-01**: no `from factory_gh import GH`, no third path to the binary. `factory_land.py` calls
  only `factory_gh.preflight`, `factory_gh.issue_view`, `factory_gh.run_gh`,
  `factory_gh.project_items`, `factory_gh.project_field_set` — all pre-existing public functions.
  `run_gh` is the generic, already-public primitive `factory_gh`'s own `preflight`/`create_issue`
  etc. are built on; using it for `gh pr create` (which `factory_gh` has no dedicated wrapper for)
  is not a new accessor and not a second path to the binary — see the finding below.

  **Finding: `factory_land` is the first caller to use `factory_gh.run_gh` directly.**
  `factory_claim.py` and `factory_decompose.py` (both read for this task) go only through named
  helpers (`preflight`, `issue_view`, `project_field_set`, `attach_sub_issue`, ...); neither calls
  `run_gh` itself. `factory_gh` has no `pr_create`-shaped helper, so `factory_land` is the first
  module to reach for the generic primitive. I read this as within R-01 (run_gh is already
  public, not a new accessor), but flagging that it is a precedent, not just a reuse.
- **R-04**: `factory_land.py` imports `factory_workspace` and calls
  `factory_workspace.run_git(["push", "--set-upstream", "origin", branch], path)` — the only git
  invocation in the module. No `FACTORY_GIT` read, no second git-binary resolution.
  `expected=(FleetError, GhError)` is exactly as the intent writes it — `RuntimeError` is not in
  the tuple, so a failed push exits 2, not 1. Case (C3) pins that a plain `ValueError` from
  `pr create` also exits 2, not 1, confirming the trap path.
- **R-05**: cases (M5)/(M6) each assert `len(...) > 0` on the full recorded call list before
  asserting the negative over it (anti-vacuum, matching test-factory-decompose.py's (22) shape).

Two miss cases were added after the first self-check, following this domain's fail-open
discipline ("for every branch you write, ask: when this misses, does it block or sail through?"):
- **(M2b)** a `GhError` from `pr create` that is NOT the already-open shape (an auth-style error,
  matching test-factory-decompose.py's case (21)) stays fatal — exits 2, and `project_field_set`
  is never called, so the station cannot advance for a pull request that was never created.
- **(M2c)** the board carries no item for the issue: `_find_item_id` returning `None` exits 2, not
  0 or 1, and `project_field_set` is never called. The push and `pr create` have already run by
  this point (asserted in the case) — the point of no return the intent documents, and the reason
  the recovery is "re-run the same command," not "the tool silently reports success."
- **R-02**: `test-factory-land.py` ends with `f"\n{RAN - FAILS}/{RAN} checks passed."` —
  `38/38 checks passed.`, matching the other nine unit files.

## Finding — three sibling copies of the "already open" discrimination, not two

T-07's step 4 must treat "a pull request is already open for this head" as non-fatal. The two
cited siblings both match on `"422"` AND a phrase in the combined stdout+stderr, because they go
through `gh api` (a REST call): `factory_gh.py:229` matches `"422"` AND `"already exists"`;
`factory_decompose.py:407` matches `"422"` AND `"already been taken"`.

`factory_land.py`'s discrimination is a **third, different shape**, because `gh pr create` is not
a raw REST call — it goes through gh's own client-side pre-check rather than a bare `gh api`
call, so a `"422"` co-condition (the shape both siblings use) would be wrong here: **Educated
guess, not verified** — I ran no real `gh pr create` and read no gh source or docs in this
session; this is recalled from prior exposure to gh CLI's output, not checked in this task. The
recalled message shape is `a pull request for branch "<head>" into branch "<base>" already
exists:` followed by the URL on its own line. `factory_land.py` matches on `"already exists"`
alone (case-insensitive, no `"422"` co-condition), then extracts the URL via
`re.search(r"https?://\S+", combined)`. If the phrase matches but no URL is found, it re-raises
rather than fabricating a URL.

**Open question (non-blocking) for the panel**: gh is also known to emit a phrase-only variant
with no URL in some code paths — recalled as something like `GraphQL: A pull request already
exists for owner:branch. (createPullRequest)`. Against that exact text, `factory_land.py`'s
`"already exists"` match fires but the URL regex finds nothing, so the code re-raises and the
tool exits 2 — the single-shot failure step 4 exists to prevent. I did not add a `gh pr view`
fallback to recover a URL in that case; that is a scope call for the lead, not mine to make
silently. Flagging it rather than deciding it. This is unverified real-gh behaviour on my part —
worth a live `gh` sanity check before this ships against a real fleet.

This is not a call to unify the three copies — that stays out of scope per the dispatch.

## Cosmetic item accepted, not fixed

Per R-04(a): a failed push's `run_git` failure line reads
`factory: workspace: git push ... failed (exit N): ...` — "workspace" rather than "land" — because
the print lives inside `factory_workspace.run_git` itself. Not touched; fixing it would require a
second git invocation path, exactly what R-04 forbids.

## Files touched

- `.claude/skills/harness/bin/factory_land.py` (new)
- `.claude/skills/harness/bin/test-factory-land.py` (new)
- `.claude/skills/harness/bin/run-unit-tests.sh` — one-line append to `UNIT_SCRIPTS` on line 58
  only (`"test-factory-claim.py")` → `"test-factory-claim.py" "test-factory-land.py")`).
  `INTEGRATION_SCRIPTS` (line 59) untouched by this task; it already carried held dirt
  (`test-gen-omp-agents.py`, `test-omp-reviewer-guard.py`) from unrelated work before this task
  started.

## Not touched (leave list / out of scope)

`factory_config.py`, `factory_gh.py`, `factory_decompose.py`, `factory_claim.py`,
`factory_workspace.py`, `factory_cli.py`, `check-state.sh`, `test-check-state.py`,
`.harness/factory/fleet.yaml` — none edited, none read for editing.
