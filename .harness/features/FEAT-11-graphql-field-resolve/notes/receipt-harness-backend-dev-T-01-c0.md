# Receipt — backend-dev — FEAT-11-graphql-field-resolve — T-01

## Cross-check of the relayed intent/verify against plan.yaml

Loaded `plan.yaml` with `harness_yaml.load_plan`, took `tasks[0]` (`id: T-01`), and diffed the
relayed intent and verify text byte-for-byte against `tasks[0]["intent"]` / `tasks[0]["verify"]`
(python-file-level diff, not eyeballing). Both matched exactly (only a trailing-newline artifact
from my own dump script, not a plan difference). Proceeded.

## RED — verbatim, against the UNCHANGED factory_gh.py

Invocation:
```
python3 .claude/skills/harness/bin/test-factory-gh.py
```

To make the RED run reach every rewritten/new case (the old code's first bare success-path call
would otherwise die with an unguarded exception mid-script, per the advisor's flag), the two bare
success-path calls in the rewritten test file are wrapped in `try/except` that reports through
`check(...)` instead of propagating — inert once GREEN.

Output (11 of 108 FAILING):
```
ok    run_gh: raises GhError when the binary is missing
ok    run_gh: missing-binary message carries a concrete value
ok    run_gh: raises GhError on non-zero exit
ok    run_gh: message carries the captured stderr
ok    run_gh: GhError message has an em dash, no class name, no traceback
ok    run_gh: FACTORY_GH set AFTER import changes the binary used
ok    run_gh: stdin is closed (DEVNULL)
ok    preflight: returns None on a zero exit
ok    preflight: runs `auth status`
ok    preflight: raises GhError telling the operator to run gh auth login
ok    create_issue: returns the number parsed from the URL
ok    create_issue: passes repo verbatim
ok    create_issue: passes every label
ok    create_issue: unparseable output raises GhError, never returns a default
ok    ensure_labels: raises GhError instead of swallowing a non-zero exit
ok    ensure_labels: stops at the failing label, does not run the remaining ones
ok    ensure_labels: each call uses --force
ok    ensure_labels: passes repo verbatim
FAIL  project_field_set: made no more and no fewer than TWO calls (graphql, then item-edit)
        exc=project field not found: Station — field-list for owner project 3 does not offer it, calls=[{'argv': ['gh', 'project', 'field-list', '3', '--owner', 'owner', '--format', 'json'], 'capture_output': True, 'text': True, 'stdin': -3}]
FAIL  project_field_set: raises GhError naming the option when it is not offered
        exc=project field not found: Station — field-list for owner project 3 does not offer it
ok    project_field_set: option-not-offered case makes ZERO item-edit calls
FAIL  project_field_set: option-not-offered message is the D-04-frozen rendered string
        exc=project field not found: Station — field-list for owner project 3 does not offer it
FAIL  project_field_set (--project-id case): did not raise
        exc=Expecting value: line 1 column 1 (char 0)
FAIL  project_field_set: exactly one item-edit call was made
        calls=[{'argv': ['gh', 'project', 'field-list', '3', '--owner', 'owner', '--format', 'json'], 'capture_output': True, 'text': True, 'stdin': -3}]
ok    project_field_set: a non-diagnosable transport failure raises GhError
ok    project_field_set: a transport failure makes ZERO item-edit calls (never falls back to the bare number)
FAIL  project_field_set: transport-failure message names owner + project number
        exc=Expecting value: line 1 column 1 (char 0)
ok    project_field_set: transport-failure message never carries the generic subcommand fallback
ok    unknown owner: raises GhError naming the owner
ok    unknown owner: makes ZERO item-edit calls
ok    unknown owner: message carries no generic subcommand fallback
ok    organization (exit-1 unreachable): raises GhError naming the owner
ok    organization (exit-1 unreachable): makes ZERO item-edit calls
ok    organization (exit-1 unreachable): message differs from the unknown-owner message
ok    organization (exit-1 unreachable): message carries no generic subcommand fallback
ok    organization (exit-0 reachable): raises GhError naming the owner
ok    organization (exit-0 reachable): makes ZERO item-edit calls
FAIL  organization (exit-0 reachable): message differs from the unknown-owner message
        org=project field not found: Station — field-list for owner project 3 does not offer it, unknown=project field not found: Station — field-list for owner project 3 does not offer it
ok    organization (exit-0 reachable): message carries no generic subcommand fallback
FAIL  board absent: raises GhError naming owner + project number
        exc=gh project field-list failed: owner — gh: not found
ok    board absent: makes ZERO item-edit calls
ok    board absent: message differs from the organization message
ok    board absent: message carries no generic subcommand fallback
ok    field not single-select (empty dict): raises the SAME field-not-found error as the field-absent case
ok    field not single-select: makes ZERO item-edit calls
ok    field not single-select: message carries no generic subcommand fallback
ok    issue_view: passes repo verbatim and comma-joins fields
ok    add_label: passes repo verbatim
ok    assign: passes repo and login verbatim
ok    project_item_add: returns the item id
ok    project_item_add: passes owner verbatim
ok    create_ref: returns True on a zero exit
ok    create_ref: returns False WITHOUT raising on the measured conflict
ok    create_ref: raises GhError on a failure carrying neither token (auth failure)
ok    create_ref: a 422 WITHOUT 'already exists' raises rather than reporting a lost race
ok    project_items: returns the items list
ok    project_items: omits --query when none is given
ok    project_items: passes the query string verbatim when given
ok    project_items: raises GhError when totalCount exceeds the returned items
ok    project_items: a missing totalCount raises rather than defaulting to 0
FAIL  project_field_options: returns the option names
        opts=None
FAIL  project_field_options: raises GhError naming the absent field
        exc=gh project field-list failed: owner — gh: not found
FAIL  project_field_options: absent-field message is the D-04-frozen rendered string
        exc=gh project field-list failed: owner — gh: not found
ok    default_branch_sha: returns the sha
ok    default_branch_sha: hits the ref/heads path
ok    delete_ref: hits the DELETE endpoint for the ref name
ok    internal_id: returns an int parsed from the output
ok    internal_id: the recorded argv's first element is never 'issue' (never issue view)
ok    internal_id: hits the REST path repos/<owner/name>/issues/<n> with --jq .id
ok    attach_sub_issue: argv path ends in /sub_issues
ok    blocked_by: argv path ends in /dependencies/blocked_by
ok    edge functions: all three route through run_gh and never reach gh_issues.gh_bin
ok    run_gh: writes nothing to stdout on success
ok    create_issue: writes nothing to stdout
ok    ensure_labels: writes nothing to stdout
ok    project_items: writes nothing to stdout
ok    project_field_options: writes nothing to stdout
ok    internal_id: writes nothing to stdout
ok    attach_sub_issue: writes nothing to stdout
ok    blocked_by: writes nothing to stdout
ok    create_ref: writes nothing to stdout on success
ok    create_ref: writes nothing to stdout on the measured conflict
ok    project_field_set: writes nothing to stdout
ok    issue_view: writes nothing to stdout
ok    add_label: writes nothing to stdout
ok    assign: writes nothing to stdout
ok    project_item_add: writes nothing to stdout
ok    default_branch_sha: writes nothing to stdout
ok    delete_ref: writes nothing to stdout
ok    GhError invariant: at least one case was collected
ok    GhError invariant holds for 'gh not found: gh — install gh, or point FACTORY_GH at its pa'
ok    GhError invariant holds for 'gh issue list failed: issue list — permission denied'
ok    GhError invariant holds for 'gh auth status failed: gh — run `gh auth login` to authentic'
ok    GhError invariant holds for 'gh issue create returned no issue number: o/r — output did n'
ok    GhError invariant holds for 'gh label create failed: o/r — already frozen'
ok    GhError invariant holds for 'project field not found: Station — field-list for owner proj'
ok    GhError invariant holds for 'project field not found: Station — field-list for owner proj'
ok    GhError invariant holds for 'project field not found: Station — field-list for owner proj'
ok    GhError invariant holds for 'gh project field-list failed: owner — gh: not found'
ok    GhError invariant holds for 'project field not found: Station — field-list for owner proj'
ok    GhError invariant holds for 'gh project field-list failed: owner — gh: not found'
ok    GhError invariant holds for 'project field not found: Station — field-list for owner proj'
ok    GhError invariant holds for 'gh api -X failed: o/r — gh: authentication required'
ok    GhError invariant holds for 'gh api -X failed: o/r — gh: Invalid request (HTTP 422)'
ok    GhError invariant holds for 'project item-list truncated: o project 3: totalCount=5 items'
ok    GhError invariant holds for 'project item-list response has no totalCount: o project 3 — '
ok    GhError invariant holds for 'project field not found: Station — field-list for owner proj'
ok    GhError invariant holds for 'gh project field-list failed: owner — gh: not found'

11 of 108 FAILING.
```

## Post-RED hardening (after advisor review, before final GREEN)

The advisor caught a fail-open gap in my own RED-capture scaffolding: two `except Exception`
guards (added only so the linear script would survive the RED run past the old code's unguarded
crashes) were still present after the rewrite, and one of them made
`"a non-diagnosable transport failure raises GhError"` pass for *any* exception, including the
`json.JSONDecodeError` the RED capture actually raised at that point (visible in the RED output
above: line "ok ... raises GhError" alongside the paired failing line reporting
`exc=Expecting value: line 1 column 1 (char 0)`). Both `except Exception` blocks are removed;
the transport-failure check is now `raised and isinstance(exc, fgh.GhError)`. Also added, per
the intent's "across every failing case in this path including the transport one" clause, two
`"api graphql" not in str(exc)` assertions that were present everywhere except the
option-not-offered case in `project_field_set` and the absent-field case in
`project_field_options` — added to both.

## GREEN — after Part A/C changes + post-RED hardening

`python3 .claude/skills/harness/bin/test-factory-gh.py` → `118/118 checks passed.` (net +27
`check(` calls over the pre-task file: 71 before, 98 after, per `grep -c '^check(\|    check('`
on each version).
`python3 .claude/skills/harness/bin/test-factory-integration.py` → `97/97 checks passed.`

## VERIFY — verbatim output (re-run after the post-RED hardening above)

Invocation: the exact 20-line `verify:` block from `plan.yaml`, run from the repo root via bash.

Output:
```
PASS
```
Exit code 0. (`run-unit-tests.sh --kind unit` and `test-factory-integration.py` both ran to
completion inside the block silently — only the final `echo PASS` prints, since every `test`
clause passed and none of the `||` failure branches fired.)

## Files edited

- `.claude/skills/harness/bin/factory_gh.py`
- `.claude/skills/harness/bin/test-factory-gh.py`
- `.claude/skills/harness/bin/test-factory-integration.py`

No other file was touched. `test-factory-decompose.py`, `test-factory-claim.py`,
`test-factory-land.py` untouched — confirmed by the verify block's own sha256 pins, all three
passing, plus a pre-flight grep before editing that found none of them monkeypatch `_field_list`
directly (only `project_field_options`/`project_field_set` at the module boundary), so deleting
`_field_list` could not have broken them.

## Out of scope, noted and NOT fixed

- `.harness/features/FEAT-11-graphql-field-resolve/STATE.md`,
  `.harness/features/FEAT-11-graphql-field-resolve/feature.yaml`, and
  `.harness/logs/2026-08-10.md` show as modified in `git status` but were **not touched by this
  run** — they were already modified in the working tree on arrival, before my first edit.
  Not mine to fix or explain.
- `dispatching_fake`'s docstring in `test-factory-gh.py` still gives `("project", "field-list")`
  as its illustrative example of an argv prefix. It is prose describing the helper's generic
  mechanism, not a fixture or an assertion, and the verify's quoted-token grep only scans
  `factory_gh.py` and `test-factory-integration.py` — this file is untouched by that check. Left
  as-is rather than rewording, since the example is still accurate for the helper in general.

## Clauses checked against the tree at 8dedeae

Directly grepped (not eyeballed) after the advisor flagged I hadn't: `run-unit-tests.sh` line 17
is `UNIT_SCRIPTS=(... "test-factory-gh.py" ...)`, line 18 is
`INTEGRATION_SCRIPTS=(... "test-factory-integration.py" ...)` — matches. All the
`test-factory-integration.py` anchors (178-188 field-list handler, 190-191 project-view handler,
196-199 the --project-id assertion/message, 200-202 the option-id-to-station mapping, 205 the
`api` block, 227 the unhandled-argv branch) matched the tree exactly before my edit.

One clause the dispatch stated is **false against the tree**: it says "`str(exc)` is built by
`factory_cli.body(what, value, next_step)` at `factory_gh.py:43`" and separately claims "line 43
is inside the `GhError` docstring" as the reason for the drift to line 45. I read
`factory_gh.py` directly: line 43 is `self.stdout = stdout` — ordinary `__init__` code, not a
docstring line. The call site itself is correctly at line 45
(`super().__init__(factory_cli.body(what, value, next_step))`), so the assertion the dispatch
was supporting (assert on `str(exc)`) is still correct — but the *reason given* for the 43→45
drift is wrong, not just the line number. No other clause of the intent was found false against
the tree.

## Non-blocking gap surfaced during work (not fixed — D-03's walk is signed, not mine to change)

`_project_field_resolve`'s exception-path fallthrough (D-03 step 3, factory_gh.py) treats any
`GhError` whose `e.stdout` parses as a mapping containing a `"data"` key as a genuine GraphQL
partial-failure envelope, and walks it exactly like a success response. If gh ever returns exit
1 with a **complete** `data` payload (no null anywhere) alongside a non-empty `errors` array —
GraphQL's "partial success" shape — the walk finds nothing wrong and the resolver returns success
for a call gh itself reported as failed. Every row in the measured transport table has a null
somewhere, so no fixture in this task's suite exercises that shape, and it is not testable from
the table as given. Implemented D-03 exactly as specified — this is a signed decision, not mine
to reinterpret — and flagging it here per the advisor's review rather than adding a defensive
re-raise that would silently diverge from what was signed.
