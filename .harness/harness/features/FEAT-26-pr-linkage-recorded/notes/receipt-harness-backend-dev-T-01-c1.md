# Receipt — harness-backend-dev — T-01 — c1

## What changed

- `.claude/skills/harness/bin/feature-schema.json` — added `github.properties.source_issues`
  (`{"type": "array", "items": {"type": "integer"}, "description": ...}`), verbatim per the
  task intent. No `required` change, no `additionalProperties` change at any level, no other
  property touched.
- `.claude/skills/harness/bin/test-validate-feature-json.py` — added five `case_*` functions
  and registered them in `main()`, immediately after `case_migrated_depth_discovery_...` and
  before the FEAT-31 T-15 block.

## RED FIRST — run against the unmodified schema

Before touching `feature-schema.json`, ran the suite with the five new cases in place, schema
unmodified:

```
FAIL accepted_source_issues_list_of_integers ["sample.json: undeclared key 'source_issues' at /github. This file holds execution state only. An operator ruling goes in that feature's plan.yaml under approval.rulings; run narrative, findings and corrections go in that run's digest; current state and open questions go in STATE.md; measurements, research and receipts go in notes/."]
PASS rejected_source_issues_non_integer
PASS rejected_source_issues_quoted_number
PASS rejected_undeclared_sibling_of_source_issues
PASS accepted_github_block_without_source_issues
1 FAILURE(S): ['accepted_source_issues_list_of_integers']
```

Per new case, what the pre-change run actually shows:

- **`accepted_source_issues_list_of_integers`** — RED as expected. Failing assertion:
  `problems == []`. Observed: one problem, `"sample.json: undeclared key 'source_issues' at
  /github. ..."` — proves this case is not vacuous.
- **`rejected_source_issues_non_integer`** ([492.5]) — PASSED EARLY. Not a red I watched;
  the closed `github` block already rejects the unknown key `source_issues` itself
  (`additionalProperties: false`), before the array's item type is ever evaluated. Same
  reason as the sibling case the plan anticipated, but it applies to this case and the next
  one too, not only to the sibling case — worth flagging since the plan's own framing only
  named the sibling case as the one that might pass early.
- **`rejected_source_issues_quoted_number`** (`["492"]`) — PASSED EARLY, identical reason:
  undeclared key, never reaches item-type checking.
- **`rejected_undeclared_sibling_of_source_issues`** (`source_issue` + valid `source_issues`)
  — PASSED EARLY, exactly as the plan anticipated: the closed `github` block already rejects
  an unknown key (`source_issue`, singular) regardless of the new property's presence.
- **`accepted_github_block_without_source_issues`** — PASSED before the change too (correctly:
  omitting an as-yet-undeclared key was never a problem). This is expected and not a proof of
  vacuity for this case; the vacuity proof for the *other* accepting case
  (`accepted_source_issues_list_of_integers`) is the FAIL above.

So: only one of the five cases produced a red I actually watched. The three "rejecting" cases
all passed vacuously pre-change because `additionalProperties: false` on `github` already
rejects any undeclared key outright — adding the property changes WHY they pass (type/const
mismatch and sibling-key rejection, not "unknown key `source_issues`"), not WHETHER they pass.
This is the exact shape the plan flagged for the sibling case; it turned out to hold for all
three rejecting cases, not just that one.

## GREEN — after adding the schema property

Full suite run, all five new cases plus the pre-existing ones:

```
PASS accepted_source_issues_list_of_integers
PASS rejected_source_issues_non_integer
PASS rejected_source_issues_quoted_number
PASS rejected_undeclared_sibling_of_source_issues
PASS accepted_github_block_without_source_issues
...
ALL PASS
```

## Task `verify:` — run verbatim

```
out=$(python3 .claude/skills/harness/bin/test-validate-feature-json.py 2>&1) || { printf '%s\n' "$out"; exit 1; }
printf '%s\n' "$out" | grep -q '^PASS accepted_source_issues_list_of_integers$' || exit 1
printf '%s\n' "$out" | grep -q '^PASS rejected_source_issues_non_integer$' || exit 1
printf '%s\n' "$out" | grep -q '^PASS rejected_source_issues_quoted_number$' || exit 1
printf '%s\n' "$out" | grep -q '^PASS rejected_undeclared_sibling_of_source_issues$' || exit 1
printf '%s\n' "$out" | grep -q '^PASS accepted_github_block_without_source_issues$' || exit 1
printf '%s\n' "$out" | grep -q '^ALL PASS$' || exit 1
echo VERIFY-OK
```

Output: `VERIFY-OK`

## Full suite — `run-unit-tests.sh --kind all`

Ran to completion (exit 0). 41 scripts (19 unit + 22 integration), every one printed `PASS
<script>` — grep confirms 0 lines matching `^FAIL ` across the whole log. `test-validate-feature-json.py`
itself printed `ALL PASS` including all five new cases.

## Scope discipline

Touched only the two files named in the task (`feature-schema.json`,
`test-validate-feature-json.py`). Did not touch `gh-sync.py`, `check-state.sh`, any
`feature.json`, `harness.json`, or any file under the DEC-174 carve-out.
