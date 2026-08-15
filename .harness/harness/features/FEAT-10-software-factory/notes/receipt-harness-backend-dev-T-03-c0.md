# Receipt — harness-backend-dev — FEAT-10 T-03

## BLUF

`factory_gh.py` added: the single seam every factory tool talks to GitHub through (D-02, D-14).
Test-first: `test-factory-gh.py` was written and run RED (`ModuleNotFoundError: No module named
'factory_gh'`) before `factory_gh.py` existed, then implemented to GREEN. Registered in
`run-unit-tests.sh`'s `UNIT_SCRIPTS` (append only — T-11's `test-factory-cli.py` entry left
untouched). `--kind unit` is green, 5/5 PASS, including `test-factory-cli.py` (T-11's, not mine).

## RED (captured before implementation)

```
$ python3 .claude/skills/harness/bin/test-factory-gh.py
Traceback (most recent call last):
  File ".../test-factory-gh.py", line 16, in <module>
    import factory_gh as fgh
ModuleNotFoundError: No module named 'factory_gh'
EXIT=1
```

## GREEN (after implementation, plus the advisor-flagged coverage gaps closed)

`python3 .claude/skills/harness/bin/test-factory-gh.py` — 77/77 checks pass, exit 0. Closed after
the first green pass: (1) the plan's "every GhError raised" invariant is now asserted on all 11
caught exceptions via a `RAISED` collector, not just one; (2) the stdout-silence sweep now covers
every helper (`project_field_set`, `issue_view`, `add_label`, `assign`, `project_item_add`,
`default_branch_sha`, `delete_ref` added); (3) `preflight()` now has coverage — success (returns
None, calls `auth status`) and failure (raises GhError naming `gh auth login`).

## Verify — run verbatim, cross-checked against plan.yaml:388 (matches, no BLOCKED)

```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit > /tmp/v-t03.txt 2>&1; s=$?; grep -q "^PASS test-factory-gh.py$" /tmp/v-t03.txt && [ "$s" -eq 0 ]
```

Exit status of the compound command: `0`

### Full contents of `/tmp/v-t03.txt`

```
ok    every shipped YAML parses (115 files across 2 roots: .harness=113, .claude/skills/harness/teams=2)
ok    the corpus under .harness is not empty (a scan that matches nothing passes vacuously)
ok    the corpus under .claude/skills/harness/teams is not empty (a scan that matches nothing passes vacuously)
ok    .claude/skills/harness/teams holds exactly 2 team definitions (SC-05)
ok    detects ` #` opening a comment inside a flow sequence (the team-config.yaml bug)
ok    detects `: ` inside a multi-line plain scalar (the FEAT-04/05 bug)
ok    detects a sequence item opening with a backtick (the FEAT-03 bug)
ok    detects an unclosed flow sequence
ok    detects a DUPLICATED top-level key (safe_load accepts these; the harness does not)
ok    detects a duplicated key NESTED in a block (column-0 scans cannot see these)
ok    a correctly quoted/folded file is NOT flagged
ok    detects a broken team definition under .claude/skills/harness/teams (SC-06)
ok    a finding names file:line:column, not just 'invalid'

13/13 checks passed.
PASS test-harness-yaml-corpus.py
ok    hard-wrapped prose is ONE paragraph
ok    a blank line still separates paragraphs
ok    bold straddling a wrap boundary still renders
ok    a table becomes a table, in its own scroll container
ok    a RAGGED row is padded, never shifted left
ok    an over-long row is truncated to the header width
ok    a pipe line with NO separator row is prose, not a table
ok    asterisks inside backticks are not emphasis
ok    a bare underscore in an identifier is not emphasis
ok    a wrapped list item stays one item
ok    a numbered list is an ol
ok    an HTML comment is authoring metadata, not body prose
ok    a fenced block is escaped, not interpreted
ok    headings keep their level and get an anchor
ok    every emitted tag is balanced

15/15 checks passed.
PASS test-render-brief.py
ok    (1) review.yaml is {code, qa, security, ui} and qa is gate-only (persona: qa, mutates_repo: false) — SC-04, MF-1
ok    (2) build.yaml parses, name: build, lead: eng-lead — SC-07
ok    (3) build.yaml is hosted by a lead whose squad is Engineering, so the team is single-squad by construction — SC-07, DEC-118
ok    (4) the Engineering squad covers the personas FEAT-03's eng build runs actually used {dev-ops, backend-dev} — SC-08
ok    (5) harness/SKILL.md has a line naming both `build` and DEC-118 — SC-09
ok    (6) the placeholder literal occurs exactly once across bin/, and both consumers reference PLACEHOLDER_UNSET — SC-02
ok    (7) SPEC §13 has a `build` row whose conducted-by cell matches build.yaml's lead — SC-10
ok    (8) harness/SKILL.md names the blocking qa gate: `test_matrix` present and qa+validator+loop_back within 8 consecutive lines — SC-14, issue #24
ok    (9) the panel set agrees across SPEC's ship-feature row, SPEC's review row and the shipped review.yaml — SC-15
ok    (10) test-check-state.py still carries T-01's INV-6 fixtures (`review_sha: none` >= 2, `review_sha: 1ce886a` >= 1) — SC-01

10/10 checks passed.
PASS test-team-catalog.py
ok    run(): fn returning normally leaves exit 0
ok    run(): success writes nothing to stdout
ok    run(): success writes nothing to stderr
ok    run(): unhandled KeyError exits 2, not 1
ok    run(): unhandled KeyError leaves stdout empty
ok    run(): unhandled KeyError stderr mentions FACTORY_DEBUG
ok    run(): fn calling sys.exit(1) still exits 1
ok    run(): fn calling sys.exit(3) still exits 3
ok    run(): expected exception produces the preformed line, no prefix duplication
ok    run(): expected exception has no 'unexpected failure' text
ok    run(): expected exception exits 2
ok    run(): FACTORY_DEBUG=1 prints a traceback after the hint line
ok    run(): without FACTORY_DEBUG set, no traceback is printed
ok    message(): renders the five parts in order with the em dash
ok    body(): builds 'what: value — next_step'
ok    plan.yaml's D-08 intent actually uses U+2014 (source of truth for 'em dash')
ok    body(): the dash emitted is U+2014, not a hyphen or en dash
ok    payload(): writes exactly one stdout line
ok    payload(): that line parses as json.loads
ok    payload(): writes nothing to stderr
ok    payload(): a plain string raises TypeError
ok    nothing_to_do(): writes nothing to stdout
ok    nothing_to_do(): writes to stderr
ok    nothing_to_do(): exits 1 (EXIT_NOTHING), not an error
ok    EXIT_OK == 0
ok    EXIT_NOTHING == 1
ok    EXIT_REFUSED == 2
ok    EXIT_RACE == 3
ok    refuse(): exits EXIT_REFUSED
ok    refuse(): stdout stays empty
ok    refuse(): stderr carries message()
ok    lost_race(): exits EXIT_RACE
ok    lost_race(): stdout stays empty

ok: 0 failing check(s).
PASS test-factory-cli.py
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
ok    project_field_set: reads field-list before item-edit
ok    project_field_set: resolves the field id
ok    project_field_set: resolves the option id
ok    project_field_set: raises GhError naming the option when it is not offered
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
ok    project_field_options: returns the option names
ok    project_field_options: raises GhError naming the absent field
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
ok    GhError invariant holds for 'project field option not found: NotAnOption — field Station '
ok    GhError invariant holds for 'gh api -X failed: o/r — gh: authentication required'
ok    GhError invariant holds for 'gh api -X failed: o/r — gh: Invalid request (HTTP 422)'
ok    GhError invariant holds for 'project item-list truncated: o project 3: totalCount=5 items'
ok    GhError invariant holds for 'project item-list response has no totalCount: o project 3 — '
ok    GhError invariant holds for 'project field not found: NoSuchField — field-list for owner '

ok: 0 failing check(s).
PASS test-factory-gh.py
```

## Design notes recorded here (cheap/reversible, decided not asked)

- `GH` is not a frozen module-level constant. `_gh_binary()` reads `os.environ.get("FACTORY_GH",
  "gh")` inside `run_gh` at call time, so a test setting the env var after import is honoured —
  a module-level `GH = os.environ.get(...)` would freeze at import and silently fail that
  requirement.
- `GhError` attributes are named `argv`/`status`/`stdout`/`stderr` (never `args` — that name is
  `BaseException.args`, load-bearing for `repr`).
- `run_gh`'s failure message derives its `value` (repo/owner/subcommand) from argv via
  `_value_from_argv`, since the pinned `run_gh(args, json_out=False)` signature carries no
  separate repo parameter.
- `create_ref`'s conflict discriminator reads `exc.stdout`/`exc.stderr` (not `str(exc)`, which
  only carries the first stderr line) and requires **both** "422" and "already exists"
  case-insensitively — a lone "422" (e.g. a bad-sha validation error) raises rather than
  returning False, per the plan's "never widen that test" instruction.
- `project_items` raises on a missing `totalCount` as well as on `totalCount > len(items)` — a
  `.get("totalCount", 0)` default would make the truncation guard permanently silent on exactly
  the response shape it exists to catch.
- The three edge functions build argv via `gh_issues.internal_id_args` /
  `attach_sub_issue_args` / `blocked_by_args` and run it only through this module's `run_gh` —
  never `gh_issues.gh_bin()`. Tested by monkeypatching `gh_issues.gh_bin` to raise while calling
  all three edge functions through a `run_gh` recorder; none reached it.

## Attribution

`/tmp/v-t03.txt` shows `PASS test-factory-cli.py` (T-11's, unrelated to this task) alongside
`PASS test-factory-gh.py` (mine). No FAIL lines. `factory_cli.py` and `test-factory-cli.py` were
not touched.

## Open question for downstream tasks (non-blocking)

The plan's intent prose for this task literally writes `GH = os.environ.get("FACTORY_GH", "gh")`
as a module-level export. The implementation is deliberately `_gh_binary()`, a function, because
a real module-level constant assigned at import time would freeze before a test's
`os.environ["FACTORY_GH"] = ...` runs, contradicting the dispatch's own "resolved at call time"
requirement. T-04 through T-07 and T-12's implementers, reading the same intent text, may
reasonably try `from factory_gh import GH` and find no such symbol. Flagging so the naming
mismatch propagates rather than surprising a later task.

## Files touched

- `.claude/skills/harness/bin/factory_gh.py` (new)
- `.claude/skills/harness/bin/test-factory-gh.py` (new)
- `.claude/skills/harness/bin/run-unit-tests.sh` (appended `"test-factory-gh.py"` to
  `UNIT_SCRIPTS` only; no other line touched)
