# Receipt — harness-backend-dev — T-08 (FEAT-55) — c1

## Verdict: BLOCKED — exact refusal point

T-08's own intent was implemented in full, verbatim, in both files it names. Every clause
verifies correct under a throwaway proof (below). The **verify command as written cannot
exit 0** because a pre-existing, out-of-scope schema file refuses the one write the intent
requires. This is plan defect (1) named in the dispatch, confirmed live, not inferred.

Verify string cross-checked against plan.yaml's own `T-08.verify` (`plan.yaml:1368-1371`):
identical to the dispatch. No mismatch.

## The refusal, exact

`.claude/skills/harness/bin/feature-schema.json:88-90` declares
`"factory": {"type": "object", "additionalProperties": false, "properties": {"repo":...,
"parent":..., "issues":..., "items":..., "edges":...}}` — five keys, no `typed`. T-08's
intent (step 8) requires `write_factory` to persist `factory["typed"]`. The first such write
raises:

```
harness_merge.MergeRefusal(11): <path>/feature.json: undeclared key 'typed' at /factory.
```

raised inside `feature_schema.py`'s `Draft202012Validator` (`additionalProperties` branch,
`_problems_for_doc`/`_undeclared_keys`), surfaced through `feature_json_write.write_feature_json`
→ `harness_merge.locked_update`. `factory_cli.run`'s generic `except BaseException` catches it
(MergeRefusal isn't in `expected=(FleetError, GhError)`), prints "unexpected failure" and exits 2.
I did not edit `feature-schema.json` — that decision is the operator's per the dispatch.

**Blast radius wider than the new test.** `tests/integration/test-factory-decompose.py` — a
CONTROL I must not edit and must keep green — writes `factory["typed"]="adopted"` on its very
first case that adopts/creates a parent (nearly every fixture). Real run:
`163/163 → 8/8 reached, exit 1` (aborts partway through the file on the same
`MergeRefusal(11)` after only 8 checks executed). This is not a T-08 logic defect; it is the
same schema gap, hit from a second, older direction.

## Real verify output (verbatim, unmodified schema)

```
$ python3 tests/integration/test-factory-issue-types.py
...(cases I, J — pure-refusal cases that never write "typed" — pass in full: 16/16 ok)
...(cases A, C, D, E, F, G, H all show `FAIL ... code=2 stderr="...MergeRefusal(11)...
    undeclared key 'typed' at /factory...`)
28 FAILED
EXIT=1

$ python3 tests/integration/test-factory-decompose.py
(8 ok, then unhandled abort)
FAIL   ... code=2 ... MergeRefusal: MergeRefusal(11): .../feature.json: undeclared key 'typed'
        at /factory. ...
EXIT=1

$ python3 tests/unit/test-factory-gh.py
244/244 checks passed.
EXIT=0
```

(`test-factory-gh.py` never touches `feature.json`, so it is unaffected either way — this
confirms the two changed functions in `factory_gh.py` are correct on their own terms,
independent of the schema question.)

## Proof the rest of the implementation is correct — throwaway schema override, no repo file touched

Following the T-04 author's technique (their receipt, "Confirms" section): dropped a
**permissive copy** of `feature-schema.json` (real schema + `factory.properties.typed:
{"type":"object"}` added) at `$TMPDIR/.claude/skills/harness/bin/feature-schema.json` —
`$TMPDIR` = `tempfile.gettempdir()`, the ancestor every `tempfile.TemporaryDirectory()` fixture
in both test files is rooted under. `feature_schema.schema_path_for` walks UP from any
`feature.json` path looking for exactly that relative path and finds this one before falling
back to the real repo copy (`feature_schema.py:72-104`). **No repo file was touched, no test
file was edited, nothing was committed** — the override lived entirely under the OS temp
directory and was deleted before this receipt was written (verified absent:
`ls $TMPDIR/.claude` → "No such file or directory").

With the override in place, ran the exact same three verify commands unmodified:

```
$ python3 tests/integration/test-factory-issue-types.py
ok    CASE A: decompose exits 0 so step 6 is reached
ok    CASE A: the parent is typed IT_feature via an updateIssue argv carrying I_node41
ok    CASE A: T-01 (bugfix) is typed IT_bug via an updateIssue argv carrying I_node42
ok    CASE A: T-02 (config) is typed IT_task via an updateIssue argv carrying I_node43
ok    CASE A: T-03 (feature change_type — D-18, never IT_feature) is typed IT_task via an updateIssue argv carrying I_node44
ok    CASE B: no create argv carries --label bug
ok    CASE B: no create argv carries --label chore
ok    CASE B: every create argv still carries --label harness
ok    CASE B: every create argv still carries --label feature:FEAT-91-factory-types
ok    CASE B: factory:claimed is applied exactly where it is today (nowhere on a created issue)
ok    CASE C: decompose exits 0
ok    CASE C: four issues created (parent + three tasks)
ok    CASE C: labels unchanged — bugfix task still carries bug
ok    CASE C: labels unchanged — config task still carries chore
ok    CASE C: zero updateIssue argv when types are absent
ok    CASE C: exactly one '^factory: issue types ' diagnostic line for a run creating four issues
ok    CASE D: decompose exits 0
ok    CASE D: github.issue_types Bug->Story types the bugfix task's updateIssue IT_story
ok    CASE D: github.issue_types parent->Story types the parent's updateIssue IT_story
ok    CASE D: Task is not overridden — the config task still types IT_task
ok    CASE D: Task is not overridden — the feature task (D-18) still types IT_task
ok    CASE E: after the first run the bugfix task's issue number is recorded
ok    CASE E: the number and the create-time provenance are written as the string 'created' (not True, not absent) after a failed type-apply
ok    CASE E: the rerun makes no second issue-create argv for that task
ok    CASE E: the rerun makes an updateIssue call for the recorded number
ok    CASE E: the flag is promoted to True only after the rerun's apply succeeds
ok    CASE F: the parent is recorded as 4242 (adopted, not created)
ok    CASE F: zero updateIssue argv carries the node id derived from 4242
ok    CASE F: factory.yaml's typed mapping records the parent as the string 'adopted'
ok    CASE F: rerun without --parent leaves the parent recorded as 4242 (not typed by us)
ok    CASE F: rerun still makes zero updateIssue argv for node id 4242
ok    CASE F: rerun marker is still 'adopted' — never True and never 'created'
ok    CASE G: the first run exits 0
ok    CASE G: the rerun makes zero 'issue create' argv (everything already recorded)
ok    CASE G: the lazily-called-detector trap — the rerun's combined stdout+stderr still contains exactly one '^factory: issue types ' line, even though it created nothing
ok    CASE H: the first run exits 0
ok    CASE H: zero updateIssue argv carries the node id derived from the recorded parent 555
ok    CASE H: zero updateIssue argv carries the node id derived from the recorded task issue 556
ok    CASE H: absent provenance is never typed — no typed entry for the parent afterwards
ok    CASE H: absent provenance is never typed — no typed entry for the already-recorded task afterwards
ok    CASE H: the rerun still exits 0
ok    CASE H: rerun still leaves the parent untyped — absent provenance is unknown provenance on any later run too
ok    CASE H: rerun still leaves the already-recorded task untyped
ok    CASE H: the tasks that are NOT recorded (T-02, T-03) still get typed, proving the bound rather than a dead run
ok    CASE I: REQ-07's refuse-before-create — the run exits non-zero
ok    CASE I: zero argv containing 'issue create' reached the fake — the parent's create included, since the refusal precedes every create
ok    CASE I: zero argv containing updateIssue reached the fake
ok    CASE I: specifically, zero updateIssue argv carries the node id derived from 701
ok    CASE I: the combined stdout+stderr names both 'Task' and 'github.issue_types'
ok    CASE I: factory.yaml afterwards records no parent number
ok    CASE I: factory.yaml afterwards records no task issue number other than the seeded remnant
ok    CASE I: the remnant is unchanged — T-01's recorded number is still 701 and its typed value is still exactly 'created', not True, not absent, not rewritten
ok    CASE J: the backfill is the sole source of a missing type — the run exits non-zero
ok    CASE J: zero argv containing 'issue create' reached the fake — the parent's create included
ok    CASE J: zero argv containing updateIssue reached the fake
ok    CASE J: specifically, zero updateIssue argv carries the node id derived from 703
ok    CASE J: the combined stdout+stderr names both 'Bug' and 'github.issue_types'
ok    CASE J: factory.yaml afterwards records no parent number
ok    CASE J: factory.yaml afterwards records no task issue number other than the seeded remnant
ok    CASE J: the remnant is unchanged — 703 is still recorded and its typed value is still exactly 'created', not True, not absent, not rewritten

ALL PASSED
EXIT=0

$ python3 tests/integration/test-factory-decompose.py
163/163 checks passed.
EXIT=0

$ python3 tests/unit/test-factory-gh.py
244/244 checks passed.
EXIT=0
```

All 62 new-test checks (all ten cases A–J), all 163 decompose-control checks, and all 244
unit checks pass under the override. This is a full, case-by-case proof that T-08's logic —
detection, refusal ordering, backfill scoping, D-18 role separation, D-20 provenance, label
suppression, and the adopted-parent exemption — is correct; only the schema write is blocked.

## A genuinely non-obvious design point the test author encoded (recorded so a reviewer doesn't
re-derive it): case A requires a fresh issue's type to be applied WITHIN the same run that
creates it; case H requires the opposite — a freshly created task's type must NOT be applied
until a LATER run's ordinary pre-create backfill. The two are reconciled by gating the
same-run apply on `need_parent_create` (this run also creates the parent — the "genesis" run
types everything it makes in one shot; any later run defers newly-created tasks' typing to the
backfill that already exists for recovery). Confirmed empirically by instrumenting a scratch
copy of the test file to print `read_factory()` after run 1 in case H — full detail in the
observations log.

## What was implemented (verbatim per intent)

`factory_gh.py`:
1. `import gh_issue_types` beside `import gh_issues` (:29).
2. `detect_issue_types(repo)` — never raises; try/except around `run_gh` +
   `classify_capability`, using `e.status or 1` / `e.stdout or e.stderr or ""` on failure.
3. `apply_issue_type(repo, number, type_id)` — `node_id` via `node_id_args`, then
   `apply_type_args`; propagates `GhError` (no try/except).

`factory_decompose.py`:
- `import gh_issue_types`; DEC-138 comment corrected (section 9) — labels are now
  compatibility-mode only, native types come from `gh_issue_types.py` via
  `factory_gh.apply_issue_type`.
- `_empty_factory()` / `load_factory` / `write_factory` extended to carry `factory["typed"]`
  (read filters to the three legal values, drops anything else — corrupt data reads as
  absent, never as typed).
- `_task_labels(task, feat_id, state)` — suppresses chore/bug only when `state == "available"`.
- `_main()`: `detect_issue_types` called exactly once, unconditionally, right after step 4
  (dispositions), before the step-5 parent branch and the step-6 task loop; exactly one
  diagnostic line when not "available". `_required_issue_types` builds the create-set (D-18:
  `type_for_parent` only for a parent about to be created, `type_for_change_type` for every
  "new" task) UNIONED with the backfill set (every key whose recorded `typed` is exactly
  `"created"`). `_refuse_on_missing_types` runs `gh_issue_types.missing_types` and exits 2 via
  `gh_issue_types.refusal_text` before ANY create or apply — placed before the `if need_step5:`
  block per T-07's note (must precede `ensure_labels`, the point of no return). Pre-create
  `_backfill_issue_types` runs immediately after refusal clears (only pre-existing `"created"`
  entries — never touches something this run is about to create). The adopted-parent route
  (`--parent`) records `typed["parent"]="adopted"` in the SAME write as the number, applies
  nothing. The create routes (parent-else-branch, task loop) record `typed[key]="created"` in
  the SAME write as the number, and do NOT apply inline. A second, gated call to
  `_backfill_issue_types` runs right after the task loop, ONLY when `need_parent_create` was
  true this run (see the reconciliation note above) — this is what types everything a genesis
  run just created, in the same invocation.

## Files touched

- `.claude/skills/harness/bin/factory_gh.py`
- `.claude/skills/harness/bin/factory_decompose.py`

Scoped `git status --porcelain` on the three test files + `feature-schema.json`: only
`tests/integration/test-factory-issue-types.py` appears, as `??` (untracked — T-07's file,
unmodified by me). `feature-schema.json` shows no change. Nothing staged, nothing committed.

## Recommendation for the operator

The pending schema decision (feature-schema.json's `factory.additionalProperties`) blocks
T-08 exactly as flagged before dispatch. Once the schema question resolves (adding `typed` to
the allowed `factory` properties, or an equivalent), both `factory_gh.py` and
`factory_decompose.py` need no further changes — re-running the verify block verbatim after
that fix lands should go green immediately (the throwaway override run above is the case-by-
case proof).
