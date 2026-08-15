# T-08 receipt — require a per-repo board, reject a leftover fleet-level board

## Precondition check (verified myself before starting)

Read `.harness/factory/fleet.yaml` at this HEAD: **no top-level `board:` key** present, and the
`mruangutai/kaya-ai` repos entry carries its own `board:` block with `number: 2`. Matches the
lead's stated precondition exactly. Proceeded. `fleet.yaml` was never written by me — confirmed
below (git status, git diff --stat) it carries zero diff throughout this task.

## What changed

`.claude/skills/harness/bin/factory_config.py`:
- `load_fleet`: a top-level `board` key is now an immediate `FleetError` (`what="fleet key
  invalid"`, `value="board"`, `next_step` says the board is per-repository now and to move it
  under `repos[].board`) — no longer validated-then-accepted, no longer silently ignored.
- `load_fleet`: every `repos[]` entry MUST carry its own `board`; absence raises `FleetError`
  with key `f"repos[{name}].board"` naming the repository. `_validate_board` is now called only
  for the per-repo block.
- `board_for`: returns `entry["board"]` unconditionally — no fleet-level fallback.
- Deleted the two-argument `station(fleet, key)` (was `factory_config.py:202-208`).
- `_main`'s `--show`: removed the `if "board" in fleet: payload["board"] = ...` conditional;
  payload is always `{"repos": fleet["repos"]}`.

`.claude/skills/harness/bin/test-factory-config.py`:
- `good_fleet_dict()` moved to the per-repo shape (no top-level `board`, `repos[0]` carries its
  own).
- Round-trip case (1) now reads `fleet["repos"][0]["board"]["owner"]`.
- The six board-field mutation cases (owner empty, number not int, station_field empty,
  stations wrong keys, board not a mapping, board missing) retargeted from `d["board"]` to
  `d["repos"][0]["board"]`.
- Added case (8b): a fleet carrying a top-level `board` key raises `FleetError` with key
  `"board"` and a `next_step` mentioning `repos[].board` — its own inline fixture
  (`good_fleet_dict()` + a top-level `board` block), not a read of the live `fleet.yaml`. The
  two sub-assertions are tightened to discriminating substrings (`"invalid: board —"` and
  `"repos[].board"`) rather than bare `"board"`/`"repos"` — see "Mutation proof" below for why
  and how that was verified.
- Case (27) — a `repos[]` entry with no board raises `FleetError` naming that repository — kept
  (it already used an inline `two_repo_fleet_dict()` fixture and already asserted the required
  key), renamed to drop the now-meaningless "and no top-level board" qualifier.
- Deleted the fleet-level-fallback case: "board_station returns the fleet-level ready option
  when the entry has none" (previously at `test-factory-config.py:359-366`).
- Deleted the two-argument-`station()` cases (18)/(19); left a comment pointing at
  `board_station`.
- `(23) --show's payload has 'board' and 'repos'` → `(23) --show's payload has 'repos' and no
  top-level 'board'`.
- Swept stale docstrings on `per_repo_fleet_dict`/`two_repo_fleet_dict` that described "no
  top-level board" as if it were an optional/special case — it is now the only case.

TDD: test file edited first (RED — ran, watched exactly 2 failures, both from the new case
(8b), everything else green because it was unaffected by the fixture-shape change); then
production code (GREEN — 75/75).

## Mutation proof for case (8b) — the two sub-assertions actually discriminate

First-pass sub-assertions (`"board" in str(e)`, `"repos" in str(e)`) were vacuous — nearly every
`FleetError` this loader raises contains both substrings somewhere, so they would stay green
even if the raised key were wrong. Tightened to `"invalid: board —" in str(e)` (pins the KEY to
exactly `board`, em dash U+2014 matching `factory_cli.body`'s format and the file's own C-3
checks) and `"repos[].board" in str(e)` (appears only in this one next_step — the sibling
repos-entry-missing-board error says `repos[<name>].board`, never the bracket-empty form).

Proved with a real mutant: recorded `sha256sum factory_config.py` = `5cb072cc02...`, mutated the
raise's key from `"board"` to `"repos[].board"` in place, re-ran the suite:

```
ok    (8b) a leftover top-level board key raises FleetError
ok    (8b) a leftover top-level board key raises FleetError
FAIL  (8b) the message names key 'board' exactly
ok    (8b) the next_step mentions repos[].board
1 of 75 FAILING.
```

Exactly the predicted check reddened (`the message names key 'board' exactly`) and no other —
proving that assertion, specifically, is load-bearing. Restored the file and re-verified the
hash: `sha256sum factory_config.py` = `5cb072cc02...` (matches), and
`git status --porcelain .claude/skills/harness/bin/factory_config.py` shows no diff from the
final GREEN state at the time this receipt was written (confirmed again in the final
`git status --porcelain` below). **Correction on process**: my first restore attempt used
`git checkout -- factory_config.py`, which reverted the WHOLE file to HEAD (undoing all of
T-08's implementation, not just the mutation) — caught immediately via `git status --porcelain`
showing zero diff where GREEN work should have been, and via re-running the suite. Re-applied
the T-08 production changes by hand and re-verified GREEN (75/75) and both full verify clauses
before finalizing this receipt.

## The `station(` caller grep

**Before deletion** (run against `bin/*.py`, filtered to exclude the unrelated three-argument
`board_station(` so only genuine two-argument callers/defs show):
```
$ grep -rn "station(" .claude/skills/harness/bin/*.py | grep -v "board_station("
.claude/skills/harness/bin/factory_config.py:202:def station(fleet, key):
.claude/skills/harness/bin/test-factory-config.py:212:          fc.station(fleet, "ready") == "Ready")
.claude/skills/harness/bin/test-factory-config.py:214:        fc.station(fleet, "nonexistent")
```
Three genuine hits: the definition itself, and two test callers — cases (18)/(19), the only
in-tree callers of the two-argument form. Both were in `test-factory-config.py`, my own file, so
both were deleted along with the function (replaced by a comment pointing at `board_station`).
No caller outside this file, so no shim was needed anywhere else.

**After deletion** (unfiltered, for full classification):
```
$ grep -n "station(" .claude/skills/harness/bin/*.py
.claude/skills/harness/bin/factory_config.py:212:def board_station(fleet, repo_name, key):
.claude/skills/harness/bin/factory_decompose.py:399:    ready_option = factory_config.board_station(fleet, args.repo, "ready")
.claude/skills/harness/bin/test-factory-config.py:246:# NOTE: the two-argument station(fleet, key) was deleted in FEAT-16 T-08 — board_station is now
.claude/skills/harness/bin/test-factory-config.py:362:          "board", fc.board_station(fleet, "mruangutai/kaya-ai", "ready") == "Todo")
.claude/skills/harness/bin/test-factory-config.py:367:        fc.board_station(fleet, "mruangutai/harness", "nonexistent")
```
All five remaining hits are `board_station(` — the different, three-argument function (T-03's,
unaffected) — or the retiring comment I left in its place. `grep -n 'def station('` on
`factory_config.py` (SC-11 grep 2, below) confirms the two-argument definition itself is gone.
No caller I did not expect.

## SC-11 grep 1 — after the change (must be empty)

```
$ grep -rnE "fleet[A-Za-z_]*\[['\"]board['\"]\]|fleet[A-Za-z_]*\.get\(['\"]board['\"]\)" .claude/skills/harness/bin/
(no output — exit 1)
```
All four baseline sites from the lead's table are closed:
`test-factory-config.py:72` (round-trip reads off `repos[0]["board"]` now),
`factory_config.py:204` (inside the deleted two-arg `station()`),
`factory_config.py:218` (`board_for`'s deleted fleet-level fallback),
`factory_config.py:250` (`_main --show`'s removed guard). **No fifth site appeared.**

## SC-11 grep 2 — after the change (must be empty)

```
$ grep -n 'def station(' .claude/skills/harness/bin/factory_config.py
(no output — exit 1)
```

## Verify — clause 1: `run-unit-tests.sh --kind unit`

Invocation:
```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```

Verbatim output (final run, on the final files, after the mutation-proof restore):
```
ok    every shipped YAML parses (195 files across 2 roots: .harness=193, .claude/skills/harness/teams=2)
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

33/33 checks passed.
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
ok    project_field_set: made no more and no fewer than TWO calls (graphql, then item-edit)
ok    project_field_set: first call is gh api graphql
ok    project_field_set: second call is gh project item-edit
ok    project_field_set: resolves the field id
ok    project_field_set: resolves the option id
ok    project_field_set: query selects exactly one field by name
ok    project_field_set: query has no plural field-connection selection
ok    project_field_set: query carries no connection argument (first:/last:)
ok    project_field_set: raises GhError naming the option when it is not offered
ok    project_field_set: option-not-offered case makes ZERO item-edit calls
ok    project_field_set: option-not-offered message is the D-04-frozen rendered string
ok    project_field_set: option-not-offered message carries no generic subcommand fallback
ok    project_field_set (--project-id case): did not raise
ok    project_field_set: exactly one item-edit call was made
ok    project_field_set: --project-id is present in the item-edit argv
ok    project_field_set: --project-id carries the GraphQL node id, NOT the bare board number
ok    project_field_set: a non-diagnosable transport failure raises GhError
ok    project_field_set: a transport failure makes ZERO item-edit calls (never falls back to the bare number)
ok    project_field_set: transport-failure message names owner + project number
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
ok    organization (exit-0 reachable): message differs from the unknown-owner message
ok    organization (exit-0 reachable): message carries no generic subcommand fallback
ok    board absent: raises GhError naming owner + project number
ok    board absent: makes ZERO item-edit calls
ok    board absent: message differs from the organization message
ok    board absent: message differs from the unknown-owner message
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
ok    issue_board_item_id: made exactly ONE call
ok    issue_board_item_id: that one call is gh api graphql
ok    issue_board_item_id: ZERO calls hit project item-list
ok    issue_board_item_id: argv carries the issue number
ok    issue_board_item_id: argv carries both repository halves
ok    issue_board_item_id: returns the matching node's id when project.number == board_number
ok    issue_board_item_id: _ISSUE_ITEM_QUERY's issue(...) selection takes exactly the argument {number} — no state/filter argument of any spelling
ok    issue_board_item_id: an item on a DIFFERENT project number returns None, does not raise
ok    issue_board_item_id: empty nodes list with totalCount 0 returns None, does not raise
ok    issue_board_item_id: repository.issue explicitly null returns None, does not raise
ok    issue_board_item_id: repository dict with NO 'issue' key at all RAISES (distinct from the explicit-null case above)
ok    issue_board_item_id: issue with no 'projectItems' key RAISES
ok    issue_board_item_id: projectItems.nodes not a list RAISES
ok    issue_board_item_id: projectItems with no 'totalCount' key RAISES (never defaults to 0)
ok    issue_board_item_id: a string totalCount raises GhError, NOT a bare TypeError
ok    issue_board_item_id: totalCount 3 with one node RAISES
ok    issue_board_item_id: truncation message names the totals
ok    issue_board_item_id: a node missing 'id' RAISES
ok    issue_board_item_id: a node missing 'project' RAISES
ok    issue_board_item_id: a null repository RAISES, naming the repository, not the generic graphql-call-failed text
ok    issue_board_item_id: a non-diagnosable transport failure raises GhError
ok    issue_board_item_id: transport-failure message names the repo and issue number
ok    issue_board_item_id: a malformed repository string raises before any call
ok    issue_board_item_id: malformed-repository message names the repository
ok    project_field_options: returns the option names
ok    project_field_options: raises GhError naming the absent field
ok    project_field_options: absent-field message is the D-04-frozen rendered string
ok    project_field_options: absent-field message carries no generic subcommand fallback
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
ok    GhError invariant holds for 'gh graphql call failed: owner project 3 — re-run after check'
ok    GhError invariant holds for 'project owner not found: acmeuser — check the owner login'
ok    GhError invariant holds for 'organization-owned board not supported: acmeuser — run again'
ok    GhError invariant holds for 'organization-owned board not supported: acmeuser — run again'
ok    GhError invariant holds for 'project not found: acmeuser project 3 — check the board numb'
ok    GhError invariant holds for 'project field not found: Station — field-list for owner proj'
ok    GhError invariant holds for 'gh api -X failed: o/r — gh: authentication required'
ok    GhError invariant holds for 'gh api -X failed: o/r — gh: Invalid request (HTTP 422)'
ok    GhError invariant holds for 'project item-list truncated: o project 3: totalCount=5 items'
ok    GhError invariant holds for 'project item-list response has no totalCount: o project 3 — '
ok    GhError invariant holds for 'gh graphql call failed: acme/widget issue 42 — re-run after '
ok    GhError invariant holds for 'gh graphql call failed: acme/widget issue 42 — re-run after '
ok    GhError invariant holds for 'gh graphql call failed: acme/widget issue 42 — re-run after '
ok    GhError invariant holds for 'issue projectItems missing totalCount: acme/widget issue 42 '
ok    GhError invariant holds for 'issue projectItems totalCount is not an integer: acme/widget'
ok    GhError invariant holds for 'issue projectItems truncated: acme/widget issue 42: totalCou'
ok    GhError invariant holds for 'issue projectItems node has unrecognised shape: acme/widget '
ok    GhError invariant holds for 'issue projectItems node has unrecognised shape: acme/widget '
ok    GhError invariant holds for 'repository not found: acme/widget — check the repository nam'
ok    GhError invariant holds for 'gh graphql call failed: acme/widget issue 42 — re-run after '
ok    GhError invariant holds for 'malformed repository: not-a-valid-repo — expected owner/name'
ok    GhError invariant holds for 'project field not found: NoSuchField — field-list for owner '

154/154 checks passed.
PASS test-factory-gh.py
ok    (1) load_fleet round-trips board.owner
ok    (1) load_fleet round-trips repos[0].name
ok    (1) load_fleet round-trips workspace_root
ok    (2) schema is not factory-fleet/1
ok    (2b) workspace_root is a filesystem root
ok    (3) a repos entry has no board
ok    (4) repos[].board is not a mapping
ok    (5) repos[].board.owner is empty
ok    (6) repos[].board.number is not an int
ok    (7) repos[].board.station_field is empty
ok    (8) repos[].board.stations does not carry exactly ready/building/review
ok    (8b) a leftover top-level board key raises FleetError
ok    (9) repos is missing
ok    (10) a repo entry lacks a slash in its name
ok    (11) workspace_root is not absolute
ok    (8b) a leftover top-level board key raises FleetError
ok    (8b) the message names key 'board' exactly
ok    (8b) the next_step mentions repos[].board
ok    (12) repos is empty
ok    (13) repos is not a list
ok    (14) a repo entry lacks default_branch
ok    (14b) repos[].board.stations carries an empty value
ok    (14c) repos[].board.number is a bool, not an int
ok    (14d) workspace_root is missing
ok    (15) at least 9 FleetError messages were collected
ok    (15) FleetError message obeys C-3: 'fleet schema invalid: schema — set schema: factory-fleet/1 in /var/fol'
ok    (15) FleetError message obeys C-3: "fleet key invalid: workspace_root — it is a filesystem root ('/') in /"
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos[mruangutai/harness].board — give mruangutai/h'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos[mruangutai/harness].board — set repos[mruangu'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos[mruangutai/harness].board.owner — set it to t'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos[mruangutai/harness].board.number — set it to '
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos[mruangutai/harness].board.station_field — set'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos[mruangutai/harness].board.stations — set exac'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: board — the board is per-repository now — move it u'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos — set a non-empty list of repo entries in /va'
ok    (15) FleetError message obeys C-3: 'fleet repo entry invalid: repos[].name — each repo needs a name contai'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: workspace_root — set it to an absolute path in /var'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos — set a non-empty list of repo entries in /va'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos — set a non-empty list of repo entries in /va'
ok    (15) FleetError message obeys C-3: 'fleet repo entry invalid: repos[o/r].default_branch — set a non-empty '
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos[mruangutai/harness].board.stations — set exac'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos[mruangutai/harness].board.number — set it to '
ok    (15) FleetError message obeys C-3: 'fleet key invalid: workspace_root — set it to an absolute path in /var'
ok    (16) repo_entry finds the listed repo
ok    (17) repo_entry raises FleetError for an unlisted name
ok    (17) the message names the unlisted name
ok    (25) a fleet whose single repos entry carries its own board loads
ok    (25) 'board' is absent from the loaded fleet — there is no top-level block
ok    (26) board_for returns repos[0]'s own board number
ok    (26) board_for returns repos[1]'s own board number
ok    (27) a repos entry with no board raises FleetError
ok    (27) the message names the repository missing its board
ok    (28a) repos[].board.owner is empty
ok    (28b) repos[].board.number is not an int
ok    (28c) repos[].board.station_field is empty
ok    (28d) repos[].board.stations does not carry exactly ready/building/review
ok    (29) board_station returns the per-repo ready option when the entry has its own board
ok    (30) board_station raises FleetError on an unknown key
ok    (31) board_for on an unlisted repository raises FleetError
ok    (31) the message names the unlisted repository
ok    (20) FLEET_PATH is an absolute path
ok    (21) a CLAUDE_PROJECT_DIR with no probe file is discarded
ok    (21) discarding it is announced on stderr
ok    (21) the returned root still has a readable probe file
ok    (22) workspace_path joins workspace_root with the name after the slash
ok    (22) workspace_path does not use the owner-prefixed name
ok    (23) --show over a good fleet exits 0 (or None)
ok    (23) --show's stdout parses as a single json.loads
ok    (23) --show's payload has 'repos' and no top-level 'board'
ok    (24) --show over an invalid fleet writes nothing to stdout
ok    (24) --show over an invalid fleet writes exactly one stderr line
ok    (24) --show over an invalid fleet exits 2
ok    (X) sanity: factory_*.py enumeration is non-empty and includes factory_config.py, and _find_fleet_reads self-test finds both the module-scope read and the function-scope assign-chain read in a throwaway fixture, and reports nothing else (the negative os.path.join shape is not a hit)
ok    (X) SC-18: exactly one scope, anywhere in factory_*.py (module scope or any function), opens/parses the fleet file
ok    (X) SC-18: that one reader is factory_config.py's load_fleet — no other tool bypasses it

75/75 checks passed.
PASS test-factory-config.py
ok    (A) missing checkout: exits 0
ok    (A) missing checkout: first call is clone
ok    (A) missing checkout: some later call checks out the issue branch
ok    (A) missing checkout: no fetch
ok    (B) existing checkout: exits 0
ok    (B) existing checkout: fetch is called
ok    (B) existing checkout: clone is never called
ok    (C) missing checkout: final command checks out the issue branch
ok    (C) existing checkout: final command checks out the issue branch
ok    (D) origin carries the ref: final checkout tracks origin
ok    (D) origin carries the ref: no command names both the issue branch and origin/<default_branch> together (the T-07 divergence bug)
ok    (E) origin has no ref: final checkout is created off origin/<default_branch>
ok    (F) existing local branch tracking origin: checked out as-is, not recreated with -b
ok    (F2) local branch diverges from origin (cut from default_branch): NOT a bare checkout (the fail-open shape)
ok    (F2) local branch diverges from origin (cut from default_branch): final command force-aligns onto origin/factory/issue-42
ok    (F2) local branch diverges from origin (cut from default_branch): still exits 0 (repaired, not refused)
ok    (F2) local branch diverges from origin (no upstream at all): NOT a bare checkout (the fail-open shape)
ok    (F2) local branch diverges from origin (no upstream at all): final command force-aligns onto origin/factory/issue-42
ok    (F2) local branch diverges from origin (no upstream at all): still exits 0 (repaired, not refused)
ok    (G) unlisted repo: exits 2
ok    (G) unlisted repo: zero git calls
ok    (H) a failing git command exits non-zero
ok    (I) happy path: stdout is exactly one JSON object
ok    (I) happy path: payload has path and branch
ok    (I) happy path: payload path is absolute
ok    (J) unlisted repo refusal: nothing on stdout
ok    (J) unlisted repo refusal: exactly one stderr line
ok    (J) unlisted repo refusal: that line names the repository
ok    (J) unlisted repo refusal: exits 2
ok    (K) a plain RuntimeError from run_git exits 2, not 1

30/30 checks passed.
PASS test-factory-workspace.py
factory: decompose: unexpected failure: RuntimeError: boom, kill before any edge — re-run with FACTORY_DEBUG=1 for a traceback
ok    (1) unsigned plan: exits 2
ok    (1) unsigned plan: nothing on stdout
ok    (1) unsigned plan: names the plan path on stderr
ok    (1) unsigned plan: zero mutating calls
ok    (2) signed two-task plan: exits 0
ok    (2) two issues created
ok    (2) two board items added
ok    (2) two stations set
ok    (2) both stations set to the fleet's ready option
ok    (2) feature.json records two issue numbers
ok    (2) feature.json records two item ids
ok    (3) second publish: exits 0
ok    (3) second publish: zero calls of any kind on the mutating/board/edge/id surface (preflight is expected and excluded from this list)
ok    (3) second publish: zero internal_id calls specifically
ok    (4) unlisted repo: exits 2
ok    (4) unlisted repo: zero calls of any kind
ok    (5) config task carries chore
ok    (5) feature task does not carry chore
ok    (5) neither carries bug
ok    (6) a raising board add exits 2
ok    (6) feature.json still carries the created issue number
ok    (7) precondition: one issue recorded, zero items recorded
ok    (7) resume: exits 0
ok    (7) resume: zero create_issue calls
ok    (7) resume: project_item_add IS called
ok    (7) resume: the item's station is set to the ready option
ok    (7) resume: feature.json now carries an item id
ok    (8) ensure_labels runs before the first create_issue
ok    (8) ensure_labels' argument set contains factory:claimed
ok    (8) created issue 'T-01 do the thing' carries harness
ok    (8) created issue 'T-01 do the thing' carries feature:FEAT-99-fixture
ok    (8) created issue 'T-01 do the thing' never carries factory:claimed
ok    (8) created issue 'T-02 do the thing' carries harness
ok    (8) created issue 'T-02 do the thing' carries feature:FEAT-99-fixture
ok    (8) created issue 'T-02 do the thing' never carries factory:claimed
ok    (9) keys outside the factory block round-trip unchanged
ok    (9) the github block survives
ok    (9) a factory key was written
ok    (10) unsigned-plan refusal: zero mutating calls over the FULL call list
ok    (11) body has exactly two blank-line-separated parts (intent, then meta)
ok    (11) intent appears first, verbatim
ok    (11) change_type line present
ok    (11) traces line is comma-separated on one line
ok    (12) exits 0
ok    (12) parent carries exactly harness + feature:<FEAT>
ok    (12) parent body is problem, blank line, **Goal:** line
ok    (12) parent body carries no change_type/traces line
ok    (12) feature.json records parent_origin created
ok    (13) exits 0
ok    (13) no issue is created for the adopted parent
ok    (13) feature.json records parent 777 with parent_origin adopted
ok    (13) feature:<FEAT> label applied to the adopted parent
ok    (13) no call edits the adopted parent's title or body
ok    (14) the parent's number appears in NO project_item_add call
ok    (15) exactly two attach calls, one per task
ok    (15) attach ('attach_sub_issue', ('acme/widget', 1, 900101)) carries the INTERNAL id, not an issue number
ok    (15) attach ('attach_sub_issue', ('acme/widget', 1, 900101)) targets parent 1
ok    (15) attach ('attach_sub_issue', ('acme/widget', 1, 900102)) carries the INTERNAL id, not an issue number
ok    (15) attach ('attach_sub_issue', ('acme/widget', 1, 900102)) targets parent 1
ok    (16) exits 0
ok    (16) exactly six blocked_by calls for T-12
ok    (16) each names a distinct resolved blocker id
ok    (17) no edge call precedes the last create_issue call
ok    (18) exits 0
ok    (18) stderr names both task ids
ok    (18) no blocked_by call was made for the missing blocker
ok    (18) payload edges_skipped is exactly 1
ok    (18) payload edges_drawn counts only edges actually written
ok    (19) precondition: two issues, two items, empty edges
ok    (19) run 2: exits 0
ok    (19) run 2: zero create_issue calls
ok    (19) run 2: zero project_item_add calls
ok    (19) run 2: draws every parent and blocked_by edge
ok    (19) run 3: draws nothing at all
ok    (20a) already-drawn blocked_by: exits 0
ok    (20a) feature.json records the edge exactly as a successful call would
ok    (20a) a stderr line names both task ids
ok    (20a) the run continues to draw every later edge (both attaches present)
ok    (20b) the attach twin STAYS FATAL: exits 2
ok    (20b) feature.json records NO parent receipt for that task
ok    (21) a non-already-drawn GhError on blocked_by stays fatal: exits 2
ok    (21) no receipt recorded for that edge
ok    (22) os.replace was called at least once
ok    (22) feature.json WAS opened for reading at least once (anti-vacuum)
ok    (22) feature.json was opened only for reading, never in a truncating mode
ok    (SC-20) plan.yaml is byte-identical
ok    (SC-20) BRIEF.md is byte-identical
ok    (SC-20) feature.json is the only file whose hash changed
ok    (C-3a) unsigned-plan refusal: nothing on stdout
ok    (C-3a) unsigned-plan refusal: exactly one stderr line
ok    (C-3b) happy path stdout is exactly one JSON object
ok    (C-3b) payload carries the expected keys
ok    (C-3c) a plain KeyError from create_issue exits 2, not 1
ok    (S2-missing) exits exactly 2 (EXIT_REFUSED, not 1/'nothing to do')
ok    (S2-missing) nothing on stdout
ok    (S2-missing) stderr names the plan path
ok    (S2-missing) stderr names the missing/unusable field: 'feature'
ok    (S2-missing) zero mutating gh calls — no remote write at all
ok    (S2-missing) preflight itself never ran either — refused before step 3
ok    (S2-missing) no 'feature:None' label anywhere in what reached gh
ok    (S2-missing) no bare 'feature:' label anywhere in what reached gh either
ok    (S2-empty) exits exactly 2 (EXIT_REFUSED, not 1/'nothing to do')
ok    (S2-empty) nothing on stdout
ok    (S2-empty) stderr names the plan path
ok    (S2-empty) stderr names the missing/unusable field: 'feature'
ok    (S2-empty) zero mutating gh calls — no remote write at all
ok    (S2-empty) preflight itself never ran either — refused before step 3
ok    (S2-empty) no 'feature:None' label anywhere in what reached gh
ok    (S2-empty) no bare 'feature:' label anywhere in what reached gh either
ok    (S2-whitespace) exits exactly 2 (EXIT_REFUSED, not 1/'nothing to do')
ok    (S2-whitespace) nothing on stdout
ok    (S2-whitespace) stderr names the plan path
ok    (S2-whitespace) stderr names the missing/unusable field: 'feature'
ok    (S2-whitespace) zero mutating gh calls — no remote write at all
ok    (S2-whitespace) preflight itself never ran either — refused before step 3
ok    (S2-whitespace) no 'feature:None' label anywhere in what reached gh
ok    (S2-whitespace) no bare 'feature:' label anywhere in what reached gh either
ok    (D4fix-1) run 1 exits 2
ok    (D4fix-1) run 1: project_item_add WAS called (proves the run reached step 7)
ok    (D4fix-1) run 1: issue recorded
ok    (D4fix-1) run 1: item NOT recorded as complete (the orphan does not land in the ledger)
ok    (D4fix-2) run 2, same persistent failure: exits non-zero
ok    (D4fix-2) run 2: item STILL not recorded as complete
ok    (D4-3) precondition: issue recorded, item not recorded
ok    (D4-3) resume with existing board item: exits 0
ok    (D4-3) project_item_add was NOT called on the recovery run
ok    (D4-3) project_items was called ZERO times — the whole-board scan is gone
ok    (D4-3) issue_board_item_id was called EXACTLY ONCE (the targeted read-before-write)
ok    (D4-3) issue_board_item_id called with (repo, issue_number, board_number)
ok    (D4-3) project_field_set called with the RESOLVED existing item id
ok    (D4-3) feature.json records the resolved existing item id
ok    (D4-3b) resume with a board lookup miss: exits 0
ok    (D4-3b) issue_board_item_id WAS called (the lookup happened)
ok    (D4-3b) project_item_add IS called on a lookup miss (the fallback)
ok    (D4-3c) resume with a closed issue: exits 0
ok    (D4-3c) project_item_add was NOT called on the recovery run
ok    (D4-3c) the lookup call args are exactly (repo, issue_num, board_number) — NOT the no-state-scoping property, which this check cannot exercise (see comment above)
ok    (D4-3c) project_field_set called with the RESOLVED existing item id
ok    (D4-4) typo fleet: exits 2
ok    (D4-4) typo fleet: zero mutating calls
ok    (D4-4) typo fleet: the validation read itself happened
ok    (D4-4) typo fleet: stderr names the offending station key
ok    (D4-4) typo fleet: stderr names the configured (wrong) value
ok    (D4-4) typo fleet: stderr names the board's real options
ok    (D4-4) typo fleet: nothing on stdout
ok    (T-03) two-repo fleet, --repo A: exits 0
ok    (T-03) project_item_add called at least once, all against A's board (acme, 3)
ok    (T-03) project_item_add issues no call against B's board (other-org, 7)
ok    (T-03) project_field_set called at least once, all against A's board (acme, 3)
ok    (T-03) project_field_set issues no call against B's board (other-org, 7)
ok    (T-03) the station set to A's own ready option (Ready), never B's (Other-Ready)
ok    (T-03) the station-validation read is against A's board and field, never B's

181/181 checks passed.
PASS test-factory-decompose.py
ok    (M1) empty ready column exits 1
ok    (M1) stdout is empty
ok    (M2) repo not in fleet exits 1 (no candidate)
ok    (M2) issue_view never called for it
ok    (M3/M6) happy path exits 0
ok    (M3/M6) stdout parses as one JSON payload
ok    (M6) branch is factory/issue-42
ok    (M6) station set to Building exactly once
ok    (M7) feature key equals label value with prefix stripped
ok    (M8) project_items called with a query naming the ready option
ok    (M7) harness-only issue claims normally, exit 0
ok    (M7) feature is null for an issue with no feature: label
ok    (M4) lowest issue number wins
ok    (M5) missing station option exits 2
ok    (M5) no board read happened
ok    (M5) stderr names the missing option, the field and the fleet file
ok    (C1) exit 1
ok    (C1) stdout is EMPTY
ok    (C1) stderr carries 'no work available'
ok    (C2) whole stdout parses as one JSON object
ok    (C2) exit 0
ok    (C2) issue_view's requested fields include "state"
ok    (C3) exit 2, not 1
ok    (C3) stdout empty
ok    (C3) exactly one stderr line
ok    (C3) stderr names a concrete value
ok    (R1) exit 0 with payload
ok    (R1) label/assign/field_set all happen AFTER create_ref
ok    (R2 route1) exit 1
ok    (R2 route1) stdout empty
ok    (R2 route1) zero mutating calls
ok    (R2 route1) 'no claimable work' present, 'no work available' absent
ok    (R2 route1) names all three issue numbers with ref-already-exists
ok    (R2 route2) exit 1
ok    (R2 route2) stdout empty
ok    (R2 route2) zero mutating calls
ok    (R2 route2) no create_ref attempted at all
ok    (R2 route2) 'no claimable work' present, 'no work available' absent
ok    (R2) route1 and route2 stderr are NOT equal
ok    (R3 closed) exits 0 and claims #92
ok    (R3 already-labelled) exits 0 and claims #92
ok    (R3 already-assigned) exits 0 and claims #92
ok    (R3 ref-refused) exits 0 and claims #92
ok    (R4) --issue lost race exits 3
ok    (R4) zero mutating calls
ok    (R4) --issue resolves via issue_board_item_id EXACTLY ONCE, zero project_items calls
ok    (R4) issue_board_item_id called with the fleet repo entry's own name, then args.issue, then the board number
ok    (R4) --issue self-owned re-entry exits 0
ok    (R4) self-owned re-entry payload
ok    (R4) self-owned re-entry never calls create_ref
ok    (R4) self-owned re-entry resolves via issue_board_item_id, zero project_items calls
ok    (R4) same issue in POLL mode is skipped (exit 1), not re-emitted
ok    (R5) exits 2, not 3
ok    (R5) loop stopped — #66 was never reached (issue_view called once)
ok    (R6a) --issue on a closed, unowned issue exits 2 (refused)
ok    (R6a) zero mutating calls
ok    (R6a) zero create_ref calls
ok    (R6a) stdout empty
ok    (R6a) stderr names the issue
ok    (R6b) --issue on a closed, self-owned issue exits 2 (refused), NOT re-emitted at exit 0
ok    (R6b) zero mutating calls
ok    (R6b) zero create_ref calls
ok    (R6b) stdout empty
ok    (R7) --issue found on no fleet repo exits 2 (refused)
ok    (R7) zero mutating calls
ok    (R7) stderr names the issue
ok    (R8) poll mode calls project_items EXACTLY ONCE
ok    (R8) poll query names the ready station and is:open, unchanged
ok    (R8) poll mode never calls issue_board_item_id
ok    (B1) exits 0
ok    (B1) create_ref called EXACTLY ONCE, with the CLEAR candidate (#720)
ok    (B1) blocked candidate's skip reason on stderr, distinct from labelled/assigned reasons
ok    (B2) exits 1
ok    (B2) zero mutating calls, including create_ref
ok    (B2) 'no claimable work' present, 'no work available' absent
ok    (B3) all blockers closed: candidate IS claimed
ok    (B4) mixed: skipped, create_ref called once with the clear candidate (#721)
ok    (B4) stderr names the LAST (open) blocker: T-04 / #603
ok    (B4) same fixture, last blocker closed too: candidate IS now claimed
ok    (B5) unresolvable blocker: skipped, not claimed
ok    (B5) distinct stderr reason naming T-99
ok    (B5-bis) edge (i): lost task identity is BLOCKED, not claimed
ok    (B5-bis) edge (i) reason distinct from open-blocker and unresolvable-blocker reasons
ok    (B6) feature: null claims normally
ok    (B6) no plan file was consulted for it
ok    (B7) fresh --issue on a blocked issue exits 2 (never 3, never 0)
ok    (B7) zero mutating calls and no create_ref
ok    (B7) stderr names the blocking T-02
ok    (B7) --issue on an issue this agent already owns exits 0, gate never blocks re-entry
ok    (X) sc13b fixture: exits 1, nothing claimable
ok    (X) sc13b fixture: stdout empty
ok    (X) sc13b fixture: zero mutating calls
ok    (X) sc13b fixture: exactly seven skip lines fired (fixture didn't silently short-circuit)
ok    (X) sc13b fixture: the seven skip lines are for exactly issues 901..907
ok    (X) SC-13(b): all seven skip reasons are pairwise distinct after normalising every embedded issue number, not just a leading one
ok    (X) SC-13(b) bonus: still pairwise distinct after ALSO normalising T-NN task ids
ok    (P1) poll mode queries both boards, not just one
ok    (P1) board A's query is built from board A's own field and ready option
ok    (P1) board B's query is built from board B's own field and ready option, not board A's
ok    (P2) claims #200 on repository A, exit 0
ok    (P2) exactly one project_field_set call, addressed to A's board and never B's
ok    (P3) exits 2 (refused)
ok    (P3) refusal names board B's board number
ok    (P3) refusal does NOT name board A's board number
ok    (P4) --repo REPO exits 1, no work on that repo's board
ok    (P4) --repo filters the served set: every board read names A's board, none names B's
ok    (P5) claims #300 exactly once, exit 0
ok    (P5) both fleet entries query the shared board (two project_items calls recorded)
ok    (P5) issue_view runs exactly once for #300 — the duplicate never entered the candidate loop
ok    (P5) exactly one project_field_set call despite the duplicate
ok    (P6) SC-13: --repo on the sole served repository's empty ready station: stdout is empty
ok    (P6) SC-13: stderr carries 'no work available'
ok    (P6) SC-13: exit code is EXIT_NOTHING (1), not a silent 0

113/113 checks passed.
PASS test-factory-claim.py
ok    (M1) exits 0
ok    (M1) pushes exactly one branch
ok    (M1) push args are --set-upstream origin <branch>
ok    (M1) push runs against workspace_path's cwd
ok    (M1) creates exactly one pull request
ok    (M1) pr create base is the fleet's default_branch
ok    (M1) pr create head is the branch
ok    (M1) pr create body contains closes #<n>
ok    (M1) issue_board_item_id was called EXACTLY ONCE — the targeted lookup replaces the whole-board scan (FEAT-13, D-01)
ok    (M1) project_items was called ZERO times
ok    (M1) issue_board_item_id's first argument is the repository string (args.repo), NOT the bare board-owner login
ok    (M1) issue_board_item_id's first argument is explicitly NOT the board-owner login (the mis-wire this assertion exists to catch)
ok    (M1) issue_board_item_id called with (repo, issue, board_number)
ok    (M1) sets the station to Review
ok    (M1) issue_view's requested fields include "state"
ok    (M1) payload url is the created pull request url
ok    (M1) payload carries repo, issue, branch
ok    (M1-json) stdout is a single json.loads-able stream
ok    (M2) still exits 0
ok    (M2) still sets the station
ok    (M2) payload carries the existing pr's url
ok    (M2) stderr mentions the url
ok    (M2b) a non-already-open GhError stays fatal: exits 2
ok    (M2b) the station is never set on an unopened pull request
ok    (M2b) stdout empty
ok    (M2c) a missing board item exits 2, not 0 or 1 (fail-closed on the miss)
ok    (M2c) the station is never set when no item was found
ok    (M2c) stdout empty
ok    (M2c) the pull request WAS already created before the miss was discovered
ok    (M3) exits 2
ok    (M3) zero git calls
ok    (M3) zero gh calls
ok    (M3) stdout empty
ok    (M3) stderr names the branch
ok    (M4) exits 2
ok    (M4) zero git calls
ok    (M4) zero gh calls
ok    (M4) stdout empty
ok    (M4) stderr names the repository
ok    (M5) at least one git call was recorded (anti-vacuum)
ok    (M5) no recorded git call pushes the default branch
ok    (M6) at least one gh call was recorded (anti-vacuum)
ok    (M6) no recorded gh call contains a merge subcommand
ok    (M7) a closed issue exits 2 (refused), not 0
ok    (M7) stdout empty
ok    (M7) stderr names the issue
ok    (M7) the push already happened before the closed-issue refusal
ok    (M7) the pull request WAS already created before the closed-issue refusal
ok    (M7) the station is never set on a closed issue (field_set_calls == [])
ok    (C1) code is 0
ok    (C1) whole stdout stream is one JSON object
ok    (C2) exit 2
ok    (C2) stdout empty
ok    (C2) exactly one stderr line
ok    (C2) that line names the branch
ok    (C3) exits 2, not 1
ok    (C3) stdout empty
ok    (T04-1) exits 0
ok    (T04-1) issue_board_item_id called with A's (repo, issue, board_number)
ok    (T04-1) project_field_set called exactly once
ok    (T04-1) project_field_set carries A's owner, board number, station_field and Review option name
ok    (T04-1) issue_board_item_id's call carries none of B's board markers
ok    (T04-1) project_field_set's call carries none of B's board markers
ok    (T04-1) no gh call of any kind was recorded against B's board number

64/64 checks passed.
PASS test-factory-land.py
PASS case1_absence_no_deploy_sh_tracked_anywhere
PASS case1_absence_no_harness_deploy_command
PASS case1_presence_six_other_command_doors_survive
PASS case1_presence_check_plan_routes_survives
PASS case1_presence_factory_workspace_survives
PASS case2_absence_no_unswept_distribution_tokens
PASS case2_presence_scan_reached_the_tree
PASS case3_presence_fleet_yaml_safe_loads
PASS case3_presence_fleet_has_exactly_one_repo
PASS case3_absence_harness_is_not_a_fleet_member
PASS case3_presence_kaya_default_branch_is_master
PASS case3_absence_no_registry_json_under_harness
PASS case4_absence_no_dec12_heading
PASS case4_absence_no_stale_marker_reintroduced
PASS case4_presence_exactly_one_dec113_heading
PASS case4_presence_dec113_precedence_rule_survives
PASS case4_absence_no_dec12_references_under_docs
PASS case4_presence_exactly_one_dec113_index_row
PASS case4_absence_no_dec12_index_row
PASS board_lives_per_repo_not_fleet_level
PASS every_repo_declares_its_own_board
PASS kaya_ai_is_paired_with_board_2

ALL PASS
PASS test-no-distribution.py
PASS accepted_all_eleven_keys
PASS accepted_only_eight_required_keys
PASS accepted_omitting_optional_max_total_runs
PASS accepted_omitting_optional_github
PASS accepted_omitting_optional_factory
PASS rejected_omitting_required_feature_id
PASS rejected_omitting_required_branch
PASS rejected_omitting_required_pr
PASS rejected_omitting_required_status
PASS rejected_omitting_required_review_sha
PASS rejected_omitting_required_cycles_used
PASS rejected_omitting_required_max_total_cycles
PASS rejected_omitting_required_runs
PASS accepted_status_Backlog
PASS accepted_status_Plan
PASS accepted_status_Ready
PASS accepted_status_Building
PASS accepted_status_Review
PASS accepted_status_Done
PASS rejected_phase_undeclared
PASS rejected_undeclared_top_level_key
PASS rejected_undeclared_runs_item_key
PASS rejected_undeclared_github_sub_key
PASS rejected_prose_key_runs_item
PASS rejected_status_shipped
PASS rejected_status_lowercase_done
PASS rejected_pr_string_none
PASS cli_clean_file_exit_exactly_0
PASS cli_invalid_file_exit_exactly_1
PASS cli_invalid_file_stderr_names_branch
PASS cli_jsonschema_unavailable_exit_exactly_3
PASS cli_jsonschema_unavailable_not_0_or_1
PASS cli_jsonschema_unavailable_stderr_names_required
PASS json_extension_rejects_yaml_content
PASS yaml_extension_accepts_same_content
PASS problems_for_text_at_least_two_problems
PASS problems_for_text_display_path_in_every_line
PASS forced_unavailable_returns_non_empty
PASS forced_unavailable_single_line
PASS forced_unavailable_names_required
PASS forced_unavailable_names_install_command

ALL PASS
PASS test-validate-feature-json.py
```

Exit code: 0

## Verify — clause 2: `run-unit-tests.sh --kind integration`

Invocation:
```
.claude/skills/harness/bin/run-unit-tests.sh --kind integration
```

Verbatim output (final run, on the final files, after the mutation-proof restore):
```
ok    lead, block-style members + bare empty key
ok    lead, fully inline lists
ok    nested must_fix must NOT satisfy the top-level one
ok    three fields on one line loses two
ok    doer, inline — unchanged behaviour
ok    drifted key spelling is caught
ok    enum near-miss is caught, not normalized
ok    open_questions as a count, not a list
ok    bare key followed by nothing is an empty list
ok    inline # comments are stripped, not parsed
ok    # inside a quoted value survives
ok    no VERDICT at all
ok    PASS over a failing member is rejected
ok    FAIL over an escalating member is rejected
ok    lead may report worse than its members
ok    a members entry with no verdict is rejected
ok    DIGEST: with a trailing comment is still recognized
ok    block-mapping member entries spanning lines are accepted
ok    a member's nested headline does not satisfy the top-level one
ok    an int does not satisfy a str-typed field
ok    a bare NULLABLE scalar key must not silently become an empty list
ok    a nested open_questions count must not trip the top-level check
ok    drift in a UNIVERSAL field is caught, not just schema fields
ok    orchestrator digest with the reconciled schema
ok    orchestrator briefing is NULLABLE — `none` when nothing was written
ok    echo shadow: valid real FAIL after a template echo still validates
ok    echo shadow: missing matrix_ok in the real block is not masked by the echo
ok    echo shadow: lead roll-up must read the real members, not the echo
ok    dev refusing an under-specified task can say suite: n/a
ok    suite: n/a with VERDICT PASS is a fail-open and is REJECTED
ok    qa that cannot run the suite can say matrix_ok: n/a
ok    matrix_ok: n/a with VERDICT PASS is REJECTED — the gate did not run
ok    reviewer scoping out of a non-UI diff may PASS with severity_max: n/a
ok    visual-designer deciding no DESIGN.md is needed may say contract: n/a
ok    pm blocked before sizing may say surface: n/a and risk: n/a
ok    matrix_ok: mostly is STILL rejected after n/a became legal
ok    severity_max: medium is STILL rejected after n/a became legal
ok    dev-ops suite: n/a still accepted (it had the value before DEC-173)
ok    dev missing task_verify under a real task is rejected
ok    dev task_verify: fail + PASS is rejected
ok    dev task_verify: n/a + PASS is rejected
ok    dev-ops task_verify: fail + PASS is rejected — no carve-out on this value either
ok    dev-ops task_verify: n/a + PASS is rejected — no carve-out
ok    dev task_verify: n/a + BLOCKED is the honest refusal, accepted
ok    dev task_verify: n/a + FAIL is accepted — the same refusal, other verdict
ok    dev-ops task_verify: n/a + BLOCKED is accepted — refusal, not the carve-out
ok    dev-ops task_verify: n/a + FAIL is accepted
ok    qa carries neither new field and is still accepted
ok    dev task: none with task_verify omitted is accepted — D-07's escape hatch
ok    dev-ops task: none with task_verify omitted is accepted
ok    dev task: bogus is rejected — the field is constrained
ok    dev omitting task entirely is rejected — the field is required
ok    dev task: none + task_verify: fail is rejected as a contradiction
ok    dev task: none + task_verify: n/a is accepted — the honest DEC-121 spelling
ok    dev suite: fail + PASS is rejected — the fail-value gate
ok    qa suite: fail + PASS is rejected
ok    qa matrix_ok: false + PASS is rejected — the BOOLEAN half
ok    dev-ops suite: fail + PASS stays accepted — D-03 ruling, not a claim it is right
ok    a documentor digest carries neither new field and is still accepted
ok    a reviewer digest carries neither new field and is still accepted
ok    task_verify's missing-field hint names its real values, not the none wording
ok    task's missing-field hint names a task id, not the list wording

62/62 CLI cases passed.
ok    joint hint followability — both licensed repairs validate
ok    [hook] F1.1 quoted headline text must not satisfy the verdict lookup
ok    [hook] F1.2 multi-line inline members list is followed to its close
ok    [hook] F1.3 unquoted apostrophe must not fuse list entries
ok    [hook] F1.4 empty members against a nonzero steps_run is rejected
ok    [hook] fail-open crash: list-valued enum is a reported violation, not a crash
ok    [hook] pass-through: non-harness agent_type is not governed
ok    [hook] pass-through: stop_hook_active avoids the infinite-block loop
ok    [hook] pass-through: empty last_assistant_message passes with a stated reason
ok    [hook] DEC-156: narrative digest.md with no contract block is exit 2
ok    [hook] DEC-156: digest.md carrying the same valid block is exit 0
ok    [hook] DEC-156: missing file fails OPEN with the INV-15 pointer, not a block
ok    [hook] DEC-156: file check governs leads only — a dev's artifact is not read
ok    [hook] F6 missing agent_type key is loud, not silent
ok    [hook] echo shadow [hook]: missing matrix_ok behind an echo is exit 2

14/14 hook cases passed.
ok    [template] SPEC §10.4
ok    [template] harness-team "Reporting up"

2/2 template cases passed.

ALL PASSED.
PASS test-validate-digest.py
ok    gh missing -> SKIP, exit 0
ok    sync disabled -> SKIP, exit 0
ok    repo unpinned -> SKIP, exit 0
ok    bad feature dir -> ERROR, exit 1
ok    open exits 0
ok    milestone created with SC checklist
ok    3 issues created
ok    parent created and recorded
ok    parent title carries the H1 phrase
ok    every call pins --repo
ok    T-01 unlabeled beyond harness (feature)
ok    T-02 labeled chore (ci)
ok    T-03 labeled bug (bugfix)
ok    absorbs cited in T-01 body
ok    issue numbers recorded in feature.json
ok    created parent records origin created
ok    three sub-issues attached to the parent
ok    attach uses internal id not number
ok    labels ensured before any issue create
ok    re-run open creates nothing
ok    close-task closes exactly one issue
ok    absorbed #12 #14 NOT closed
ok    ship PATCHes milestone closed
ok    backlog creates 3 issues, exit 0
ok    backlog natures label correctly
ok    backlog issues carry NO milestone
ok    malformed backlog item -> ERROR exit 1
ok    empty phrase titles the parent with no trailing em-dash
ok    --parent adopts
ok    adopted parent records origin adopted
ok    recorded-not-attached task is attached on re-run
ok    pre-existing parent survives per-task saves
ok    parent_origin survives per-task saves
ok    phrase containing an em-dash is taken whole
ok    failed attach is a SKIP, exit 0, for the new subcommand too (SC-12)
ok    issue recorded before the failed attach survives the crash
ok    abandon closes 3 subs not_planned
ok    abandon closes the milestone
ok    abandon posts via --body-file
ok    abandon leaves an adopted parent open
ok    abandon closes a created parent not_planned
ok    abandon leaves a parent with no recorded origin open
ok    abandon without --reason-file exits 1
ok    abandon with an empty reason file exits 1
ok    abandon with a nonexistent reason path exits 1
ok    abandon with an unreadable reason file exits 1
ok    abandon with a BINARY reason file exits 1, not a traceback
ok    abandon with no recorded milestone never builds milestones/None
ok    abandon with sync disabled -> SKIP, exit 0
ok    ship closes a created parent completed
ok    ship leaves an adopted parent open
ok    ship closes the milestone regardless of parent origin
ok    ship leaves a parent with no recorded origin open
ok    ship --body-file posts once
ok    ship without --body-file posts nothing
ok    ship with an empty body file exits 1
ok    (eleven-key) open exits 0
ok    (eleven-key) every non-github key survives untouched
ok    (eleven-key) a github block was written
ok    T-06C: a populated github: block loads, quoted milestone coerced by _opt_int
ok    T-06C: a feature.json with no github: block returns the default, does not raise
ok    fix1 B row1a: absent feature.json returns the default rec, does not raise
ok    fix1 B row1b: dict present with no github key returns the default rec
ok    fix1 B row2: 0 bytes on disk
ok    fix1 B row2: a 0-byte feature.json raises SystemExit, never loads as empty
ok    fix1 B row2 (a_list): a non-mapping document raises SystemExit
ok    fix1 B row2 (a_scalar): a non-mapping document raises SystemExit
ok    fix1 B row4 (github=a_string): a non-mapping github: value raises SystemExit
ok    fix1 B row4 (github=a_list): a non-mapping github: value raises SystemExit
ok    fix1 A: a failed save_recorded leaves feature.json byte-identical, never truncated
ok    fix1 A: no leftover temp file after a failed save_recorded
ok    finding 2: save_recorded round-trips a feature.json with no github block yet
ok    finding 2: save_recorded round-trips a feature.json with an existing github block
ok    finding 2: save_recorded round-trips a feature.json with other keys present

ALL PASSED
PASS test-gh-sync.py
ok - case (a): INV-21 note appears when parent is unrecorded
ok - case (b): no INV-21 note when parent is recorded
ok - case (c): no INV-21 note when github.sync is false
ok   case (d): settings.local.json does not hide settings.json's hooks
ok - case (e): issue #11 — a commented squad:/id: line still yields the run, so INV-6 fires
ok - case (f): an unparseable feature.json is reported and exits 1 (got exit 1)
ok - case (g.1): INV-17 RAISES on Review with handoff-build.md absent, and names it
ok - case (g.2): INV-17 stays quiet for the literal exemption set (FEAT-01 at Done, no notes)
ok - case (g.3): INV-17 RAISES at Done when handoff-validate.md is absent
ok - case (g.4): INV-17 raises nothing at Plan with no notes at all
ok - case (g.5): all-main-session-direct at Done raises NO handoff violation AND reports the exemption by name
ok - case (g.6): a plan with NO execution_mode keys still RAISES and reports no exemption
ok - case (g.7): an empty tasks: list and an absent tasks: key BOTH raise, never vacuously exempt
ok - case (h): issue #16 — `review_sha: none` is a placeholder, not a pin, so INV-6 fires
ok - case (i): a pinned SHA does not trip INV-6
ok - case (j): no validator run, so INV-6 stays silent even on a placeholder
ok - case (k) no cost: block: no cost violation
ok - case (k) with a cost: block: no cost violation
ok - case (l1) 21 runs against a 20 budget is NOTED
ok - case (l2) exactly 20 does NOT fire — the boundary is >, not >=
ok - case (l3) a per-feature max_total_runs: 30 silences it
ok - case (l4) INV-22 NEVER gates — exit code identical over and under budget
ok - case (l5) the CONFIGURED value is read — budget 5 with 7 runs names 5, not 20
ok - case (l6) budgets present but key missing is REPORTED INACTIVE, never silent
ok - case (l7) no budgets block at all (the shipped kaya example) is REPORTED INACTIVE
ok - case (l8) a boolean budget is REJECTED, not treated as an int (bool subclasses int)
ok - case (m): INV-9 catches a MISSING PostToolUse check-domain while the PreToolUse one is present
ok - case (m2): INV-9 rejects a NARROWED PostToolUse matcher, naming the missing tools
ok - case (m3): a decoy entry does not let a narrowed PostToolUse registration through INV-9
ok - case (n/feature.json over): at 301 feature.json / 120 STATE.md lines, INV-23 fires on [feature.json] — wanted [feature.json]
ok - case (n/STATE.md over): at 300 feature.json / 121 STATE.md lines, INV-23 fires on [STATE.md] — wanted [STATE.md]
ok - case (n/both within): at 300 feature.json / 120 STATE.md lines, INV-23 fires on [nothing] — wanted [nothing]
ok - case (o): check-domain.sh, check-state.sh and HANDOFF.md agree on every duplicated budget, key and heading
ok - case (p/over): CLAUDE.md at 81 lines -> INV-23 fires (want fires)
ok - case (p/at the budget): CLAUDE.md at 80 lines -> INV-23 silent (want silent)
ok - case (p/warn): the CLAUDE.md finding is a `note`, not a `VIOLATION` — warn level, so it cannot halt /harness entry
ok - case (q/approved): INV-3 is silent on plan.yaml
ok - case (q/pending): INV-3 notes on plan.yaml
ok - case (q/malformed): a plan.yaml that does not load is reported, not skipped
ok - case (q/inv5): STATE.md naming a task the plan.yaml lacks is a violation
ok - case (r): no harness.json is DIAGNOSED, not a crash (a crash prints nothing to stdout)
ok - case (s) INV-24: a listed repository passes
ok - case (s) INV-24: an UNLISTED repository is a violation naming the repo
ok - case (s) INV-24: two features recording one repo+issue names BOTH
ok - case (s) INV-24: one feature's PARENT equal to another's issue names BOTH
ok - case (s) INV-24: two features sharing one PARENT names BOTH
ok - case (s) INV-24: a block with NO parent key is silent
ok - case (s) INV-24: factory state with NO fleet file names the FLEET as the problem
ok - case (s) INV-24: a null factory.repo is a violation, not a silent pass (C1)
ok - case (s) INV-24: a null issue number is named, not treated as a collision (C1)
ok - case (s) INV-24: a feature whose own parent equals its own task issue fires, and names BOTH sides (C2)
ok - case (s) INV-24: a quoted issue number is a number here, as it is for INV-21 (D-03)
ok - case (s) INV-24: a quoted number still collides across features (D-03 does not weaken the check)
ok - case (s) INV-24: an issues block that is neither a mapping nor a list is reported, not skipped
ok - case (s) INV-24: a tree with no factory blocks at all is silent
ok - case (t1): an invalid hook matcher is REPORTED, not raised (empty stdout means the checker crashed)
ok - case (t2): a plain file named `runs` does not crash INV-18 (empty stdout means the checker crashed)
ok - case (u.1) a worktree UNDER .claude/worktrees/ is silent
ok - case (u.2) a sibling worktree is a VIOLATION, not a note
ok - case (u.3) the not-my-root branch DOES carry `git worktree remove`
ok - case (u.4) a session ROOTED in an out-of-place worktree is a VIOLATION too — severity does not branch
ok - case (u.5) the LEGITIMATE worktree under the main checkout is silent even from an out-of-place root
ok - case (u.6) the own-root line names .claude/worktrees and does NOT say `git worktree remove`
ok - case (u.7) F-B: an unimportable harness_boundary.py is a VIOLATION, not a silent skip of INV-25
ok - exit code unchanged by INV-21 (a: 1, b: 1)
PASS test-check-state.py
ok    clean file passes
ok    MISSING title is a violation
ok    WRONG-NAME title is a violation — an agent must not be handed another's memory
ok    wrong title WORDING is a violation
ok    title not on line 1 is a violation
ok    non-canonical section is a violation
ok    over the 50-word cap is a violation
ok    a feature token is a violation
ok    entry without the XX-NN prefix is a violation
ok    no argument is a usage error (exit 2)

10/10 cases passed.
PASS test-check-expertise.py
ok - test_row_per_distinct_dec_matches_authority
ok - test_argv_is_validated_and_only_the_write_path_writes
ok - test_malformed_row_is_reported_not_silently_dropped
ok - test_supersession_declared_in_body_prose_is_harvested
ok - test_preserves_hand_written_rulings_by_dec_number
ok - test_strips_inline_ok_stale_marker_on_a_row
ok - test_committed_index_matches_a_fresh_regeneration
ok - test_committed_index_is_complete_and_within_budget
ok - test_orphaned_ruling_is_reported_not_silently_dropped
PASS test-gen-decisions-index.py
ok    mandated commit trailer (angle brackets in a quoted string)
ok    an arrow inside a quoted string
ok    an HTML comment inside a quoted string
ok    a heredoc delimiter is not a redirect target
ok    input redirection is a READ, not a write
ok    a quoted string mentioning a redirect
ok    stderr redirection is not the cp destination
ok    stderr redirection is not an rm target
ok    a redirect after cp still blocks, glued
ok    a redirect after cp still blocks, spaced
ok    an out-of-domain cp destination still blocks
ok    rm -f does not hide its target
ok    rm -r -f does not hide its target
ok    rm -rf still blocks, unchanged
ok    sed -i -f still names the target, not the script
ok    awk -i inplace -f still names the target
ok    rm -f in-domain passes
ok    sed -i -f in-domain passes
ok    plain read commands pass
ok    a comparison operator inside a python heredoc body
ok    a redirect-shaped line inside a CAT heredoc body is inert text
ok    an unquoted heredoc tag is still a heredoc
ok    rm in-domain followed by another command
ok    mv within domain followed by another command
ok    in-domain redirect followed by a read command
ok    a heredoc fed to bash still blocks its redirect
ok    a heredoc fed to sh still blocks its redirect
ok    a redirect on the heredoc command line still blocks
ok    an out-of-domain redirect in the SECOND segment still blocks
ok    an out-of-domain rm in the second segment still blocks
ok    an out-of-domain write after && still blocks
ok    a cat heredoc PIPED to bash still blocks its redirect
ok    a heredoc piped to sh -s still blocks its redirect
ok    an unbalanced quote does not crash the hook
ok    output redirect to an out-of-domain path
ok    append redirect to an out-of-domain path
ok    QUOTED redirect target still blocks
ok    sed -i in place
ok    perl -pi in place
ok    tee to an out-of-domain path
ok    rm of an out-of-domain path
ok    mv onto an out-of-domain path

42/42 cases passed.

ok    SC-06 pair: permitted bash write allowed AND forbidden blocked
ok    a MALFORMED manifest blocks the bash write (fail closed)
ok    a DUPLICATE key in the manifest blocks the bash write
ok    an ABSENT manifest still fails OPEN (DEC-151 carve-out intact)
ok    both write surfaces agree on .harness/allowed/x.txt (D-03, one shared rule)
ok    both write surfaces agree on src/main.py (D-03, one shared rule)
ok    both write surfaces agree on forbidden/x.txt (D-03, one shared rule)

7/7 T-14 cases passed.
ok    a shell write INTO an out-of-place worktree is REFUSED
ok    the same session's in-domain shell write still PASSES
ok    a session ROOTED in an out-of-place worktree is refused its own in-domain shell write
ok    the ROOT-SIDE bash verdict names .claude/worktrees and does NOT say `git worktree remove`
ok    a read-only command from an out-of-place root is ALSO refused (the check is not behind the no-findings exit)
ok    a session rooted in a LEGITIMATE worktree is unaffected
ok    SC-07: the legitimate worktree is writable FROM OUTSIDE it on the Bash route (granted independently by BOTH the carve-out and the stripping)
ok    F-A: a .git pointer that is not valid UTF-8 REFUSES the shell write
ok    F-A: a .git pointer that is a bare word, no gitdir: REFUSES the shell write
ok    F-A: a .git pointer that is an empty file REFUSES the shell write
ok    F-A: with the pointer restored, the in-domain shell write still PASSES
ok    a MISSING harness_boundary.py blocks the bash write and NAMES the module
ok    one-implementation baseline: both routes ALLOW the legitimate worktree write
ok    the mutation targeted the constant BY NAME (not the bare literal)
ok    ONE IMPLEMENTATION: mutating WORKTREES_SEGMENT flips BOTH routes 0 -> 2
ok    worktree creation — an absolute destination outside .claude/worktrees
ok    worktree creation — a value-taking flag cannot hide the destination
ok    worktree creation — a value-taking flag whose VALUE is a legal path still cannot hide it
ok    worktree creation — a RELATIVE destination is refused — it cannot be resolved
ok    worktree creation — a .. traversal out of .claude/worktrees
ok    worktree creation — `git worktree move` out of .claude/worktrees
ok    worktree creation — a destination INSIDE .claude/worktrees
ok    worktree creation — the same, with a flag that consumes nothing
ok    worktree creation — ordinary git: status
ok    worktree creation — ordinary git: worktree list
ok    worktree creation — ordinary git: commit
ok    worktree creation — the relative refusal NAMES relativity as the reason

27/27 worktree-boundary cases passed.

PASS test-bash-write-guard.py
ok    a scratch script in /tmp
ok    /var/folders temp dir (macOS mktemp)
ok    an absolute path in another checkout
ok    documentor writing docs/
ok    documentor writing its own expertise
ok    a shared path in the harness base is now REFUSED (product-shaped target)
ok    documentor may not write source
ok    documentor may not write another agent's expertise
ok    documentor may not write bin/
ok    a repo path reached via .. still blocks
ok    a repo path reached via a long .. chain still blocks

11/11 cases passed.

ok    SC-05 pair: permitted allowed AND forbidden blocked, one manifest
ok    a MALFORMED manifest blocks the write (fail closed, not half-enforced)
ok    a DUPLICATE key in the manifest blocks the write
ok    an ABSENT manifest still fails OPEN, loudly (DEC-101 carve-out intact)
ok    F-01: a manifest that is not valid UTF-8 BLOCKS (was exit 1 = fail open)
ok    M-02: a manifest that parses to a non-mapping (empty) BLOCKS, not crashes
ok    M-02: a manifest that parses to a non-mapping (bare scalar) BLOCKS, not crashes
ok    M-02: a manifest that parses to a non-mapping (bare list) BLOCKS, not crashes
ok    F-01: a manifest that is a DIRECTORY does not crash the guard
ok    a well-formed state.yaml with checkpoint keys passes
ok    a DUPLICATE top-level key is blocked with the DEC-156 message
ok    a NESTED duplicate key is blocked (column-0 regex could not see it)
ok    MALFORMED state.yaml is blocked with a parse-error message
ok    a non-checkpoint top-level key is still blocked (DEC-154 vocabulary intact)
ok    a YAML-truthy key (`on:`) beside a string key denies cleanly, no raise
ok    ...and the denial explains the unquoted-key cause, not just 'True'
ok    SC-08: with PyYAML missing, the FIRST hook invocation PERMITS the write
ok    [partial SC-08] the install command reaches stderr (NOT proof the user sees it — D-14b)
ok    SC-08: the install command reaches a channel the user SEES (systemMessage)
ok    SC-08: ...and records the marker
ok    SC-08: a SECOND write in the SAME session is permitted, silently
ok    SC-09 mechanism: a DIFFERENT session is BLOCKED while PyYAML is missing
ok    D-14a: the block SAYS WHY and carries the install command
ok    grant: a malformed state.yaml is ALLOWED (no fallback — BRIEF Goal :20-21)
ok    grant: a well-formed state.yaml is allowed too (the grant is not selective)
ok    with a parser, the shape gate still BLOCKS the same content
ok    the marker self-unlinks once PyYAML imports again

27/27 T-12 cases passed.
--- FEAT-15 T-01..T-04 + symlink escape: fleet, bases, mirror, resolve ---
ok    (a)+(b) PAIR: with no fleet the owned write passes; with a broken fleet the SAME write is refused
ok    (a) with no fleet, a scratch path outside the root still gets no verdict
ok    (c) a fleet that parses but omits workspace_root refuses the owned write
ok    (d) PAIR: a well-formed fleet leaves both verdicts unchanged
ok    (e) the lazy factory_config import leaks nothing to stderr on a passing write
ok    (f) PAIR: in a product checkout, src/** grants the owner and refuses a persona without it
ok    (g) PAIR: src/** refuses <root>/src/main.py and permits <workspace>/widget/src/main.py
ok    (h) PAIR: a .harness/** grant permits it in root and refuses it in a product checkout
ok    (i) a path under workspace_root for an undeclared repo is refused, naming the fleet
ok    (j) a scratch path outside both bases still gets no verdict
ok    A PAIR: a product-shaped glob is REFUSED in the harness root and PERMITTED in the product checkout
ok    B PAIR: a control-plane glob is PERMITTED in the harness root and REFUSED in the product checkout
ok    C harness base: all four named entries resolve — docs/harness/**, docs/PRINCIPLES.md, README.md, .github/**
ok    C harness base: docs/harness/** was NOT widened to docs/** — the same persona permitted docs/harness/guide.md is REFUSED docs/guide.md
ok    C product base: a product checkout keeps its OWN README.md, docs/ and .github/ — the named entries are target-side only and must not refuse them
ok    T-04 resolve PAIR: a product path names the src/** owner, the SAME path in the harness root resolves to NOBODY
ok    T-04 resolve: a path under workspace_root for an undeclared repo resolves to NOBODY, never silence
ok    T-04 resolve, LIVE tree: docs/harness/SPEC.md names harness-documentor — the named entries hold target-side
ok    SYMLINK PAIR: a link out of a granted directory is REFUSED at its real target, and the ordinary granted write still PASSES
ok    SYMLINK: the refusal names the REAL target, not the link path — an agent told it may not write docs/… would file a bug against the wrong file

20/20 fleet cases passed.

ok    (a) --resolve: a singly-granted path returns exactly one agent
ok    (b) --resolve: a doubly-granted path returns both grantees
ok    (c) --resolve: an ungranted path prints the literal NOBODY
ok    (d) --resolve: the ungranted call exits 0 and stdout is not empty
ok    (e) --resolve: an open pipe on stdin still answers within 10s
ok    (f) --resolve: closed stdin is byte-identical to an open pipe
ok    (g) no --resolve: an out-of-domain Write still exits 2
ok    (h) no --resolve: an in-domain Write still exits 0
ok    (i) VF-1: HARNESS_RESOLVE_PATH set in the env does NOT disable the hook
ok    (j) VF-1: an EMPTY HARNESS_RESOLVE_PATH does NOT disable the hook

10/10 --resolve cases passed.

--- #132: shape coverage on all four write routes ---
ok    route 2 — post Edit on an over-budget file exits 2
ok    route 2 — the PRE hook reports NO shape finding on that same Edit
ok    route 3 — post Bash sweeps and finds the over-budget file
ok    route 4 — the MAIN SESSION is no longer exempt from the shape gate
ok    feature.json at 301 lines IS over the 300 budget
ok    feature.json at 300 lines is NOT over the 300 budget
ok    the SWEEP reaches and enforces handoff cap (DEC-159)
ok    the SWEEP reaches and enforces handoff missing sections
ok    the SWEEP reaches and enforces state.yaml checkpoint keys (DEC-154)
ok    the SWEEP reaches and enforces STATE.md sections (SPEC 2)
ok    the sweep reaches a file inside .claude/worktrees/ (and was silent before it)
ok    a reported file is NOT re-reported on the next sweep
ok    CLAUDE.md at 81 lines IS over the 80 budget, on Write AND Edit
ok    CLAUDE.md at 80 lines is NOT over the 80 budget, on Write AND Edit
ok    the SWEEP reaches CLAUDE.md (route 3)
ok    post Edit on a worktree file names the WORKTREE it came from
ok    post Edit (state file) on a worktree file names the WORKTREE it came from
ok    pre Write on a worktree file names the WORKTREE it came from
ok    the sweep still names the worktree it came from
ok    a WITHIN-budget file exits 0 on post Edit
ok    a WITHIN-budget file exits 0 on post Bash
ok    post mode does NOT re-run the domain check
ok    the PRE hook still blocks that same ungranted path
ok    the sweep skips an over-budget file older than SWEEP_WINDOW_S
ok    the same file, freshly touched, IS found
ok    the mark records the sweep's START, not its finish (the race window)
ok    an unreadable candidate leaves the mark unadvanced (no permanent blind spot)
ok    a sweep finding names the file it is about
ok    a post payload with NO agent_type still gets the shape gate
ok    hook_event_name alone selects post mode (no --post flag)

30/30 post-mode cases passed.

ok    schema/a legal eleven-key document is ALLOWED
ok    schema/an illegal document is DENIED and the offending key is NAMED
ok    schema/a CRASHING schema module DENIES the write rather than letting it through
ok    schema/probe restored feature_schema.py byte-identically
ok    a write INTO an out-of-place worktree is REFUSED, and the verdict names where worktrees belong
ok    the same session's in-domain write still PASSES
ok    a session ROOTED in an out-of-place worktree is REFUSED its own in-domain write
ok    the ROOT-SIDE verdict names .claude/worktrees and does NOT say `git worktree remove`
ok    a session rooted in a LEGITIMATE worktree is unaffected
ok    SC-07: the legitimate worktree is writable FROM OUTSIDE it, through DEC-143's prefix stripping
ok    a scratch path outside any worktree still PASSES
ok    F-A: a .git pointer that is not valid UTF-8 REFUSES the write (it must not read as not-a-worktree)
ok    F-A: a .git pointer that is a bare word, no gitdir: REFUSES the write (it must not read as not-a-worktree)
ok    F-A: a .git pointer that is a gitdir: that is not a worktrees entry REFUSES the write (it must not read as not-a-worktree)
ok    F-A: a .git pointer that is an empty file REFUSES the write (it must not read as not-a-worktree)
ok    F-A: with the pointer restored, the in-domain write still PASSES
ok    a MISSING harness_boundary.py blocks the write and NAMES the module
ok    with the module absent AND no manifest, DEC-101 still fails OPEN, loudly

14/14 worktree-boundary cases passed.

PASS test-check-domain.py
PyYAML is not importable by this python3 interpreter; allowing this session once.
python3 -m pip install pyyaml
# if that fails with "externally-managed-environment" (PEP 668, e.g. Homebrew/Debian):
python3 -m pip install --user --break-system-packages pyyaml
PyYAML is not importable, and this session's one-time bootstrap grant was already used by an EARLIER session — failing closed. Install PyYAML to restore normal operation:
python3 -m pip install pyyaml
# if that fails with "externally-managed-environment" (PEP 668, e.g. Homebrew/Debian):
python3 -m pip install --user --break-system-packages pyyaml
PyYAML is not importable and the bootstrap marker at /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpv4brnmz2/.harness/.pyyaml-bootstrap could not be written ([Errno 13] Permission denied: '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpv4brnmz2/.harness/.pyyaml-bootstrap'), so a one-time grant cannot be recorded — failing closed rather than granting one that never expires.
python3 -m pip install pyyaml
# if that fails with "externally-managed-environment" (PEP 668, e.g. Homebrew/Debian):
python3 -m pip install --user --break-system-packages pyyaml
ok   test_merge_key_override_is_not_a_duplicate
ok   test_missing_pyyaml_is_reportable_not_a_second_crash
ok   test_duplicate_key_is_catchable_as_a_parse_error
ok   test_duplicate_key_raises
ok   test_nested_duplicate_key_raises
ok   test_bare_date_scalar_stays_str
ok   test_int_and_bool_resolvers_are_not_stripped
ok   test_manifest_domains_matches_the_regex_walk_on_the_real_manifest
ok   test_manifest_domains_excludes_non_canonical_read_true
{"systemMessage": "[harness] PyYAML is missing, so the write guards cannot read the domain manifest. This session is granted ONE bootstrap pass and later sessions will be blocked. Install it now:\npython3 -m pip install pyyaml\n# if that fails with \"externally-managed-environment\" (PEP 668, e.g. Homebrew/Debian):\npython3 -m pip install --user --break-system-packages pyyaml"}
ok   test_bootstrap_marker_lifecycle
ok   test_marker_self_unlinks_when_yaml_imports
ok   test_exactly_one_guarded_import_in_the_tree
ok   test_c_loader_is_used_when_libyaml_is_available
ok   test_load_plan_accepts_a_well_formed_plan
ok   test_every_required_task_field_is_actually_required
ok   test_load_plan_rejects_the_shapes_that_broke_PLAN_md
ok   test_load_plan_backticked_path_is_not_silently_cleaned
ok   test_load_plan_reports_line_and_column_on_malformed_yaml
ok   test_the_shipped_template_and_the_SPEC_example_both_satisfy_load_plan
PASS test-harness-yaml.py
ok    the script RUNS as a subprocess (F-03: NameError on every invocation)
ok    it reads a real manifest without raising
ok    a malformed manifest does not pass silently
ok    a QUOTED schema_version behaves like a bare one (was read as absent)
ok    prose containing `name:` is not harvested as an agent
ok    Q2: a YAML-truthy name (`- name: no`) does not vanish from the roster
ok    missing-templates message points at an incomplete checkout, not the retired command
ok    unparsable shipped template message points at a complete checkout, not the retired command
ok    --check never rewrites team-config.yaml (safe_dump would strip its comments)

9/9 cases passed.
PASS test-upgrade-config.py
PASS case_01_ungranted_undeclared_exits_nonzero
PASS case_02_output_has_task_id
PASS case_03_output_has_offending_path
PASS case_04_all_granted_exits_0
PASS case_05_ungranted_declared_main_session_exits_0
PASS case_06_wildcard_produces_unresolved_glob
PASS case_07_wildcard_exit_status_matches_task_removed
PASS case_08_source_mentions_check_domain_sh
PASS case_09_source_has_no_fnmatch
PASS case_16_source_has_no_glob_to_re
PASS case_10_template_has_lanes_section
PASS case_11_template_has_team_token
PASS case_12_template_has_main_session_direct_token
PASS case_13_runner_lists_this_test
PASS case_14_granted_but_main_session_produces_deviation
PASS case_15_deviation_plan_still_exits_0
PASS case_17_midpattern_wildcard_grant_no_violation
PASS case_17_midpattern_wildcard_grant_reports_ok
PASS case_17_midpattern_wildcard_grant_exits_0
PASS case_17b_ok_line_names_the_exact_granting_set
ok case_18a_block_form_first_entry_not_falsely_rejected
ok case_18b_block_form_LATER_entry_is_checked_the_fail_open
ok case_18d_block_form_OK_line_names_the_UNION_of_granted_sets
ok case_18e_wrapped_same_line_continuation_is_read
ok case_18f_unparseable_files_value_is_reported_not_silent
ok case_18c_same_line_form_still_parsed
PASS case_19a_argvless_output_is_independent_of_cwd
PASS case_19a3_argvless_actually_finds_the_plans
PASS case_19a2_argvless_names_the_root_it_scanned
PASS case_19b_unresolvable_root_exits_2_not_0
PASS case_19b2_unresolvable_root_says_why_on_stderr
PASS case_19b3_unusable_project_dir_is_reported_not_silently_replaced
PASS case_19b4_a_valid_project_dir_is_not_warned_about
PASS case_19b5_an_unset_project_dir_is_not_warned_about
PASS case_19a4_discovery_finds_exactly_the_feature_plans
PASS case_19a5_the_scan_line_matches_the_glob_that_ran
PASS case_19c_zero_feature_project_is_not_an_error
PASS case_19c2_zero_feature_project_scans_the_declared_root
PASS case_19d_explicit_path_unaffected_by_the_root_guard
PASS case_19d2_explicit_path_with_no_tasks_still_exits_0
PASS case_20_bash_write_guard_sh_probes_the_manifest
PASS case_20_check_domain_sh_probes_the_manifest
PASS case_20_check_plan_routes_py_probes_the_manifest
PASS case_20_the_detector_is_not_blind
PASS case_21_a_bare_harness_dir_is_not_a_project_root
PASS case_22a_unreadable_feature_dir_exits_2
PASS case_22b_unreadable_plan_file_exits_2
PASS case_22c_broken_symlink_plan_is_reported_not_skipped
PASS case_22d_a_readable_tree_is_not_flagged
PASS case_23a_plan_yaml_granted_path_is_OK
PASS case_23b_plan_yaml_ungranted_path_is_a_VIOLATION
PASS case_23c_an_annotated_path_resolves_to_NOBODY_not_silently_cleaned
PASS case_23d_a_malformed_plan_yaml_exits_2_not_1
PASS case_23e_the_per_task_machine_budget_fires
PASS case_23f_the_budget_stays_silent_on_a_normal_task
PASS case_23h_an_over_budget_task_sets_the_EXIT_CODE_not_just_stdout
PASS case_23i_the_budget_boundary_is_exact
PASS case_23j_every_budgeted_field_counts_exactly_once
PASS case_23j2_BUDGETED_FIELDS_is_still_the_eleven_this_case_pins
PASS case_23g_both_plan_yaml_and_PLAN_md_is_refused
PASS case_24_Backlog_is_checked
PASS case_24_Plan_is_checked
PASS case_24_Ready_is_checked
PASS case_24_Building_is_checked
PASS case_24_Review_is_checked
PASS case_24_Done_is_skipped
PASS case_24_done_is_checked
PASS case_24_FINISHED_STATUSES_is_a_subset_of_the_schema_status_enum
PASS case_24_no_feature_yaml_is_checked_not_skipped
PASS case_24_feature_yaml_a_sequence_is_checked_not_crashed
PASS case_24_feature_yaml_a_bare_scalar_is_checked_not_crashed
PASS case_24_feature_yaml_status_is_a_list_is_checked_not_crashed
PASS case_24_feature_yaml_a_mapping_with_no_status_is_checked_not_crashed
PASS case_24_eleven_key_feature_json_Done_is_skipped_end_to_end

ALL PASS
PASS test-check-plan-routes.py
ok   - ours, verbatim: present=True, want=True
ok   - three separate per-tool entries: present=True, want=True
ok   - matcher key absent (matches every tool): present=True, want=True
ok   - matcher '.*': present=True, want=True
ok   - matcher '(Write|Edit|Bash)': present=True, want=True
ok   - matcher '^(Write|Edit|Bash)$': present=True, want=True
ok   - a SUPERSET matcher: present=True, want=True
ok   - reordered alternation: present=True, want=True
ok   - an unparseable matcher is not evidence of absence: present=True, want=True
ok   - registered via an absolute path: present=True, want=True
ok   - NARROWED to 'Write' (the live F-01 attack): present=False, want=False
ok   - narrowed to 'Write|Edit': present=False, want=False
ok   - right tools, WRONG script: present=False, want=False
ok   - right tools, missing --post: present=False, want=False
ok   - '--posture' must not satisfy '--post': present=False, want=False
ok   - nothing registered: present=False, want=False
ok   - agent-name spec accepts matcher 'harness-.*'
ok   - agent-name spec accepts matcher 'harness-qa|harness-pm'
ok   - agent-name spec accepts matcher '.*'
ok   - agent-name spec accepts matcher None
ok   - a split-across-entries registration is NOT duplicated by a merge (3 -> 3 entries, exit 0)
ok   - and --check calls that project correct (exit 0)

ALL PASS
PASS test-merge-settings.py
ok    (A) config: no arguments exits 2
ok    (A) config: no arguments never exits 1
ok    (A) config: no arguments writes nothing to stdout
ok    (A) config: harness_root probe was not silently discarded (no 'IGNORING it')
ok    (A) decompose: no arguments exits 2
ok    (A) decompose: no arguments never exits 1
ok    (A) decompose: no arguments writes nothing to stdout
ok    (A) decompose: harness_root probe was not silently discarded (no 'IGNORING it')
ok    (A) claim: no arguments exits 2
ok    (A) claim: no arguments never exits 1
ok    (A) claim: no arguments writes nothing to stdout
ok    (A) claim: harness_root probe was not silently discarded (no 'IGNORING it')
ok    (A) workspace: no arguments exits 2
ok    (A) workspace: no arguments never exits 1
ok    (A) workspace: no arguments writes nothing to stdout
ok    (A) workspace: harness_root probe was not silently discarded (no 'IGNORING it')
ok    (A) land: no arguments exits 2
ok    (A) land: no arguments never exits 1
ok    (A) land: no arguments writes nothing to stdout
ok    (A) land: harness_root probe was not silently discarded (no 'IGNORING it')
ok    (B) missing --fleet path: exits 2
ok    (B) missing --fleet path: nothing on stdout
ok    (B) missing --fleet path: stderr names the path
ok    (B): harness_root probe was not silently discarded (no 'IGNORING it')
ok    (C) decompose: auth failure exits 2
ok    (C) decompose: auth failure never exits 1
ok    (C) decompose: auth failure writes nothing to stdout
ok    (C) decompose: auth failure writes to stderr
ok    (C) claim: auth failure exits 2
ok    (C) claim: auth failure never exits 1
ok    (C) claim: auth failure writes nothing to stdout
ok    (C) claim: auth failure writes to stderr
ok    (C) land: auth failure exits 2
ok    (C) land: auth failure never exits 1
ok    (C) land: auth failure writes nothing to stdout
ok    (C) land: auth failure writes to stderr
ok    (D-config) success: exits 0
ok    (D-config) success: stdout is one JSON object
ok    (D-config) success: payload carries repos, each with its own board, and no fleet-level board
ok    (D-config): harness_root probe was not silently discarded (no 'IGNORING it')
ok    (D-decompose) success: exits 0
ok    (D-decompose) success: stdout is one JSON object
ok    (D-decompose) success: one issue recorded for T-1
ok    (D-decompose): harness_root probe was not silently discarded (no 'IGNORING it')
ok    (D-claim) success: exits 0
ok    (D-claim) success: stdout is one JSON object
ok    (D-claim) success: payload branch is factory/issue-600
ok    (D-claim) success: board item actually moved to Building
ok    (D-claim): harness_root probe was not silently discarded (no 'IGNORING it')
ok    (D-workspace) success: exits 0
ok    (D-workspace) success: stdout is one JSON object
ok    (D-workspace) success: payload path is under workspace_root
ok    (D-workspace) success: payload branch is factory/issue-800
ok    (D-workspace): harness_root probe was not silently discarded (no 'IGNORING it')
ok    (D-land) success: exits 0
ok    (D-land) success: stdout is one JSON object
ok    (D-land) success: payload carries a pull request url
ok    (D-land) success: board item actually moved to Review
ok    (D-land): harness_root probe was not silently discarded (no 'IGNORING it')
ok    (E) ref refused for every candidate: exits 1
ok    (E) ref refused for every candidate: writes nothing to stdout
ok    (E): harness_root probe was not silently discarded (no 'IGNORING it')
ok    (F) decompose exits 0
ok    (F) decompose: stdout is one JSON object
ok    (F) decompose: one issue per task
ok    (F) decompose: harness_root probe was not silently discarded (no 'IGNORING it')
ok    (F) decompose: both board items boarded at the fleet's declared ready station
ok    (F) claim exits 0
ok    (F) claim: stdout is one JSON object
ok    (F) claim: claimed the T-1 issue (unblocked candidate)
ok    (F) claim: payload branch is factory/issue-<n>
ok    (F) claim: board item actually moved to Building
ok    (F) claim: harness_root probe was not silently discarded (no 'IGNORING it')
ok    (F) workspace exits 0
ok    (F) workspace: stdout is one JSON object
ok    (F) workspace: payload path is under workspace_root
ok    (F) workspace: payload branch matches claim's branch
ok    (F) workspace: the payload path is an actual directory on disk
ok    (F) workspace: harness_root probe was not silently discarded (no 'IGNORING it')
ok    (F) workspace: recorded git commands include a checkout of factory/issue-<n>
ok    (F) land exits 0
ok    (F) land: stdout is one JSON object
ok    (F) land: opened exactly one pull request
ok    (F) land: board item actually moved to Review
ok    (F) land: harness_root probe was not silently discarded (no 'IGNORING it')
ok    (F) land: recorded git commands include a push of factory/issue-<n> to origin
ok    (G1) -b --track form: workspace exits 0 against real git
ok    (G1) -b --track form: HEAD equals origin's factory/issue-1
ok    (G1) -b --track form: local branch tracks origin/factory/issue-1
ok    (G1): harness_root probe was not silently discarded (no 'IGNORING it')
ok    (G2) fixture sanity: local factory/issue-2 differs from origin's before the run
ok    (G2) fixture sanity: local factory/issue-2 has no upstream before the run
ok    (G2) -B --track form: workspace exits 0 against real git
ok    (G2) -B --track form: HEAD force-aligned onto origin's factory/issue-2
ok    (G2) -B --track form: local branch now tracks origin/factory/issue-2
ok    (G2): harness_root probe was not silently discarded (no 'IGNORING it')
ok    (G) live-git smoke check ran against a real git binary (/usr/bin/git, git version 2.50.1 (Apple Git-155))
ok    (H) decompose against the two-board fleet exits 0
ok    (H) decompose: harness_root probe was not silently discarded (no 'IGNORING it')
ok    (H) claim against the two-board fleet exits 0
ok    (H) claim: harness_root probe was not silently discarded (no 'IGNORING it')
ok    (H) land against the two-board fleet exits 0
ok    (H) land: harness_root probe was not silently discarded (no 'IGNORING it')
ok    (H) at least one gh call was recorded (anti-vacuum)
ok    (H) no recorded gh call names the other repository's board number
ok    (H) at least one recorded gh call names the served repository's own board number (proves the check above has power)

106/106 checks passed.
PASS test-factory-integration.py
```

Exit code: 0

Both clauses ran (not collapsed to `--kind all`). `test-check-domain.py` and
`test-factory-integration.py` (both migrated by earlier tasks, run in the integration kind) are
in the output above with no FAIL lines: `PASS test-check-domain.py`, `PASS
test-factory-integration.py`. `test-factory-decompose.py`, `test-factory-claim.py`,
`test-factory-land.py`, `test-factory-workspace.py` also PASS unchanged — none of my edits
reddened them.

## Files touched — only the two listed in T-08's `files:`, plus this receipt

- `.claude/skills/harness/bin/factory_config.py`
- `.claude/skills/harness/bin/test-factory-config.py`

`git status --porcelain` also shows `.claude/skills/harness/bin/test-no-distribution.py` as
modified and an untracked T-09 receipt — both are T-09's, landed immediately before this
dispatch in the same run, and neither was touched here.

## Mixed-invocation / one-way-schema note (for whoever hits this next)

After this task the schema is one-way, in one narrow way. `fleet.yaml` is tracked and every
checkout carries its own copy of it **and** its own `factory_config.py`, so `git` alone cannot
pair an old loader with a new fleet. What *can* is a **mixed invocation** — a `factory_config.py`
from before FEAT-16 T-01 resolving a fleet path that lands on a post-T-07 `fleet.yaml`, whether by
an explicit `--fleet` flag or by running the tool from one checkout against another checkout's
tree. There, `load_fleet` raises and `check-domain.sh` fails CLOSED on every governed write in
that checkout. **This is expected, not a defect.** The recovery is to rebase that checkout past
this task (T-08) — never to edit the fleet back to carrying a top-level `board:` block, which
T-08 now rejects outright. If you hit a fail-closed guard here, diagnose it as a stale checkout
first, not a broken guard.
