# Receipt — harness-backend-dev — S1-projectid-fix

## BLUF

Fixed: `project_field_set` (`factory_gh.py:266`, now the `run_gh(["project","item-edit", ...
"--project-id", project_id, ...])` call) resolves the GraphQL node id via `gh project view`
immediately before the `item-edit` call, instead of passing the bare board number. All three
callers (`factory_decompose.py:363`, `factory_claim.py:330`, `factory_land.py:99`) get the fix for
free — no signature change, zero edits to any caller.

## The bug, and the RED that proves it

`--project-id` was `str(number)` (e.g. `"3"`) where `gh project item-edit` requires the node id
(e.g. `PVT_kwHO...`). Operator-measured live: `--project-id 4` → `GraphQL: Could not resolve to a
node with the global id of '4'`.

**Invocation used for RED:** `python3 .claude/skills/harness/bin/test-factory-gh.py`, against
`factory_gh.py` before the fix, with a new argv-DISPATCHING fake (`dispatching_fake`, matches on
argv[1:] since `subprocess.run` is called with `[gh_binary] + args` — an off-by-one I hit and fixed
in the test helper itself before the real red appeared; the first pass failed for the wrong reason,
prefix-matching `argv[:2]` against `["gh","project"]`).

**Verbatim red (final, discriminating) output:**

```
ok    project_field_set: exactly one item-edit call was made
ok    project_field_set: --project-id is present in the item-edit argv
FAIL  project_field_set: --project-id carries the id from `project view`, NOT the bare board number
        --project-id='3' argv=['gh', 'project', 'item-edit', '--id', 'ITEM1', '--project-id', '3', '--field-id', 'F1', '--single-select-option-id', 'O1']
```

This is a clean value mismatch, not a vacuous pass: the dispatching fake (unlike a positional
3-result list) lets the buggy code — which never calls `["project","view"]` at all — run to
completion, so the only way the assertion could fail is on the actual value reaching
`--project-id`.

## The fix (kept)

`.claude/skills/harness/bin/factory_gh.py`, inside `project_field_set`, placed LATE (after both
existing `raise` paths, immediately before the `item-edit` `run_gh` call), per the dispatch:

```python
project_id = run_gh(
    ["project", "view", str(number), "--owner", owner, "--format", "json"],
    json_out=True,
)["id"]
run_gh([
    "project", "item-edit",
    "--id", item_id,
    "--project-id", project_id,
    "--field-id", field_id,
    "--single-select-option-id", option_id,
])
```

## Caching decision: NOT cached — parity, not a new asymptotic cost

Chose **no caching**, module-level or otherwise. Reasons, per the inputs handed down:

- `project_field_set` already makes one uncached `_field_list` call per invocation
  (`factory_gh.py:241`). Adding one more uncached network call is parity with what the function
  already does, not new asymptotic behaviour.
- `factory_decompose.py:363` calls `project_field_set` inside a loop over tasks — already O(N) in
  tasks today via the field-list call; the new call does not change the complexity class.
- The `id_cache` precedent at `factory_decompose.py:366` is caller-local, not module-level. It does
  not license a module-level dict inside `factory_gh.py`.
- A module-level memo would violate this module's own documented intent (line 11: "importing this
  module has no side effects"; `_gh_binary()` resolved at call time, never cached at import, so a
  test can swap `FACTORY_GH` after import) and would leak state across cases inside
  `test-factory-gh.py`'s single test process.
- Putting `board.id` into `fleet.yaml` was explicitly out of bounds (schema change, touches
  protected SC-18 assertions, makes `load_fleet` network-dependent) — not implemented, not raised
  as an open question since the dispatch already closed it.

## Miss-test: a failed `project view` must raise, never fall back

Added a case: `("project","view")` returns `Result(1, stderr="gh: project not found")`. Asserts
`GhError` is raised AND (the half that matters) that ZERO `["project","item-edit"]` calls were
recorded — the check that would catch a future refactor that swallows the failure and falls back to
`str(number)`, resurrecting this exact bug under a different trigger.

## Grep confirming this was the only site, not a partial fix

Condensed from the raw `grep -rn -- "--project-id" .claude/skills/harness/bin/*.py` output: three
textual hits in `factory_gh.py` — two are inside the explanatory comment at lines 263-264
("`item-edit --project-id` takes the GraphQL node id...", "...that every other `gh project`
subcommand accepts..."), one is the actual argv element at line 275
(`"--project-id", project_id,`). No second emitter of the flag exists in production code. The
remaining hits are in the two test files (`test-factory-integration.py:196,198`,
`test-factory-gh.py:93,286,300-306`) — test assertions, not production code.

```
$ grep -rn "project_field_set" .claude/skills/harness/bin/*.py
factory_gh.py:240        def project_field_set(...)          # the one definition
factory_claim.py:330     factory_gh.project_field_set(...)   # caller 1
factory_decompose.py:363 factory_gh.project_field_set(...)   # caller 2
factory_land.py:99       factory_gh.project_field_set(...)   # caller 3
```

Exactly one definition, exactly three production callers, matching the dispatch's line numbers —
confirmed by grep, not taken on the dispatch's word.

## Files touched

- `.claude/skills/harness/bin/factory_gh.py` — the fix (production).
- `.claude/skills/harness/bin/test-factory-gh.py` — new `PROJECT_VIEW_JSON` fixture, new
  `dispatching_fake` helper, new discriminating RED-then-GREEN test block, and the two pre-existing
  `project_field_set` cases updated from a 2-result to a 3-result recorder (field-list, project
  view, item-edit) since the call sequence changed.
- `.claude/skills/harness/bin/test-factory-integration.py` — added a `["project","view"]` branch to
  `fake_gh` returning a stable fake id (`PVT_kwFAKE`), and the existing `item-edit` branch now
  asserts it received that id (fails the fake, not the harness, if a caller ever regresses to the
  bare number). This is an ADDITION to the stub, not an alteration of any SC-19 assertion.

## Verification — exit codes and counts, verbatim

```
$ python3 .claude/skills/harness/bin/test-factory-gh.py            → 82/82 checks passed. exit=0
$ python3 .claude/skills/harness/bin/test-factory-claim.py         → 77/77 checks passed. exit=0
$ python3 .claude/skills/harness/bin/test-factory-config.py        → 56/56 checks passed. exit=0
$ python3 .claude/skills/harness/bin/test-factory-integration.py   → 97/97 checks passed. exit=0
$ .claude/skills/harness/bin/run-unit-tests.sh --kind unit         → exit=0, 10/10 files PASS, 0 FAIL
$ .claude/skills/harness/bin/run-unit-tests.sh --kind integration  → exit=0, 14/14 files PASS, 0 FAIL
$ .claude/skills/harness/bin/check-docs.sh                         → exit=0, run AFTER this receipt
                                                                       existed on disk (re-run per
                                                                       harness-handoff: the gate scans
                                                                       every .md under .harness/,
                                                                       including this file):
                                                                       "checked 62 superseded
                                                                       pattern(s) across 308 file(s).
                                                                       no stale statements found."
```

## Counts that moved, and why

- `test-factory-gh.py`: **76 → 82** (up, as required). +6 checks total: 3 from the discriminating
  `--project-id` value-mismatch test ("exactly one item-edit call was made", "--project-id is
  present in the item-edit argv", "--project-id carries the id from `project view`, NOT the bare
  board number"), and 3 from the miss-test added after an advisor review flagged its absence
  ("a failed `project view` raises GhError", "makes ZERO item-edit calls", plus the RAISED-invariant
  loop picking up the new GhError instance).
- `test-factory-claim.py`: 77 → 77, unchanged (not touched).
- `test-factory-config.py`: 56 → 56, unchanged (not touched).
- `test-factory-integration.py`: 97 → 97, unchanged. The only integration change is the `fake_gh`
  stub branch (an addition to the stub script, not a check inside the test file) plus one new
  inline assertion inside that stub's `item-edit` branch that fails the FAKE with `bad(...)` rather
  than adding a `check(...)` call — so the check count in the harness's own tally does not move,
  matching the operator's stated expectation.

No count decreased. `check-docs.sh`'s pattern/file count is unrelated to this change and reported
only as evidence the gate ran clean, not as a baseline being tracked; it was re-run after this
receipt was written to disk (see note above) rather than trusted from the earlier pre-receipt run.

## Scope respected

- No edit to `check-state.sh`, `check-docs.sh`, `bash-write-guard.sh`, `validate-digest.py`,
  `check-domain.sh`.
- No edit to any SC-13 / SC-18 / SC-19 assertion in `test-factory-claim.py`,
  `test-factory-config.py`, or `test-factory-integration.py` — only additions.
- `project_field_set`'s signature is unchanged; grepped all three callers
  (`factory_decompose.py:363`, `factory_claim.py:330`, `factory_land.py:99`) — none need edits,
  confirmed by the green end-to-end SC-19 journey in `test-factory-integration.py`.
- No git command run; nothing staged or committed. No mutation to any factory file needed a
  copy/restore cycle — the bug was live at `factory_gh.py:266` already, so writing the discriminating
  test first produced red for free, per the dispatch's own prediction.
- Did not touch the publish `feature`-key path or `factory_claim.py:43`'s hardcoded features dir —
  out of scope for this ticket, per the dispatch.
