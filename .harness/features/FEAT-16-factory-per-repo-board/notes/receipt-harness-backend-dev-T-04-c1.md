# Receipt — harness-backend-dev — T-04 — c1

## BLUF
`factory_land.py` step 5 now resolves the board it lands into per repository:
`factory_config.board_for(fleet, args.repo)` replaces the four direct reads of `fleet["board"]`
(owner, number, station_field, and `stations["review"]`). Nothing else changed: the default-branch
guard, the push, the pull-request create-or-adopt path and the explicit open-check keep their
current order and their current messages, including the known out-of-scope #238 behaviour on a
closed issue.

## Files touched
- `.claude/skills/harness/bin/factory_land.py`
- `.claude/skills/harness/bin/test-factory-land.py`

## The idiom split (deliberate, recorded per the task's intent)
`factory_land.py` still indexes `board["stations"]["review"]` directly — one lookup deep — rather
than calling `factory_config.board_station`, which is what `factory_decompose.py` (T-03) uses. A
comment beside the read in `factory_land.py` states why both are safe and only for one reason:
`load_fleet` validates every board's `stations` mapping to a key set of exactly `ready`,
`building` and `review`, so the direct index cannot miss. If that validation is ever relaxed, this
direct index is the call site that breaks first.

## Test changes (T-04's own scope)
- `good_fleet_dict` migrated: the top-level `board` block moved into the single `repos[0]` entry's
  own `board` mapping (no fleet-level board left in this fixture).
- Added `two_repo_fleet_dict`: two `repos[]` entries, no fleet-level board, on two different board
  numbers/owners/station fields/option names (A: `acme`/`3`/`Status`/Ready·Building·Review; B:
  `other-org`/`7`/`Stage`/Other-Ready·Other-Building·Other-Review).
- Added one new case block `(T04-1)`: landing `--repo` A against the two-repo fleet, asserting on
  the recorded gh call arguments (never a count alone) — `issue_board_item_id` is called with A's
  `(repo, issue, board_number)`; `project_field_set` is called exactly once, carrying A's owner,
  board number, station_field and the `Review` option name; and neither recorded call carries any
  of B's board markers (`BOARD_B`, `OWNER_B`, `STATION_FIELD_B`, `"Other-Review"`).

## RED, watched before GREEN
Ran the newly-written `test-factory-land.py` against the pre-edit `factory_land.py` (production
code was not touched until after the test file was written and run red). It failed with
`json.decoder.JSONDecodeError` on the M1 payload parse, plus explicit `FAIL` lines on
`(M1) exits 0` (code 2), `(M1) issue_board_item_id was called EXACTLY ONCE`, `(M1) sets the
station to Review`, and the `issue_board_item_id` argument-shape checks — the migrated fixture
dropped the top-level `board` key, so `fleet["board"]["owner"]` raised `KeyError` at step 5. Real
RED: the fixture is unloadable by the old direct reads, not a vacuous pass. Then edited
`factory_land.py` to use `factory_config.board_for` and reran GREEN: `test-factory-land.py` at
64/64.

## HARD BOUNDS respected
- `.harness/factory/fleet.yaml` not touched.
- `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`, `check-state.sh` not touched.
- Two-argument `factory_config.station(fleet, key)` left exactly as defined — not touched.
- `factory_config.py`, `factory_claim.py`, `factory_decompose.py` not touched.

## Verify — exact command, VERBATIM output, in full

Command:
```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```

Verbatim stdout+stderr (captured to a file, `EXIT=0` appended as the last line — no lines edited,
curated, or removed):

```
ok    every shipped YAML parses (194 files across 2 roots: .harness=192, .claude/skills/harness/teams=2)
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
ok    (3) board is missing
ok    (4) board is not a mapping
ok    (5) board.owner is empty
ok    (6) board.number is not an int
ok    (7) board.station_field is empty
ok    (8) board.stations does not carry exactly ready/building/review
ok    (9) repos is missing
ok    (10) a repo entry lacks a slash in its name
ok    (11) workspace_root is not absolute
ok    (12) repos is empty
ok    (13) repos is not a list
ok    (14) a repo entry lacks default_branch
ok    (14b) board.stations carries an empty value
ok    (14c) board.number is a bool, not an int
ok    (14d) workspace_root is missing
ok    (15) at least 9 FleetError messages were collected
ok    (15) FleetError message obeys C-3: 'fleet schema invalid: schema — set schema: factory-fleet/1 in /var/fol'
ok    (15) FleetError message obeys C-3: "fleet key invalid: workspace_root — it is a filesystem root ('/') in /"
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos[mruangutai/harness].board — give mruangutai/h'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: board — set board: {...} as a mapping in /var/folde'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: board.owner — set it to the GitHub owner or org in '
ok    (15) FleetError message obeys C-3: 'fleet key invalid: board.number — set it to the Projects v2 board numb'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: board.station_field — set it to the Projects v2 fie'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: board.stations — set exactly ready, building and re'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos — set a non-empty list of repo entries in /va'
ok    (15) FleetError message obeys C-3: 'fleet repo entry invalid: repos[].name — each repo needs a name contai'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: workspace_root — set it to an absolute path in /var'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos — set a non-empty list of repo entries in /va'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos — set a non-empty list of repo entries in /va'
ok    (15) FleetError message obeys C-3: 'fleet repo entry invalid: repos[o/r].default_branch — set a non-empty '
ok    (15) FleetError message obeys C-3: 'fleet key invalid: board.stations — set exactly ready, building and re'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: board.number — set it to the Projects v2 board numb'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: workspace_root — set it to an absolute path in /var'
ok    (16) repo_entry finds the listed repo
ok    (17) repo_entry raises FleetError for an unlisted name
ok    (17) the message names the unlisted name
ok    (18) station returns the configured option name
ok    (19) station raises FleetError on an unknown key
ok    (25) a fleet whose single repos entry carries its own board and no top-level board loads
ok    (25) 'board' is absent from a fleet with no top-level board
ok    (26) board_for returns repos[0]'s own board number
ok    (26) board_for returns repos[1]'s own board number
ok    (27) a repos entry with no board and no top-level board raises FleetError
ok    (27) the message names the repository missing its board
ok    (28a) repos[].board.owner is empty
ok    (28b) repos[].board.number is not an int
ok    (28c) repos[].board.station_field is empty
ok    (28d) repos[].board.stations does not carry exactly ready/building/review
ok    (29) board_station returns the per-repo ready option when the entry has its own board
ok    (29) board_station returns the fleet-level ready option when the entry has none
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
ok    (23) --show's payload has 'board' and 'repos'
ok    (24) --show over an invalid fleet writes nothing to stdout
ok    (24) --show over an invalid fleet writes exactly one stderr line
ok    (24) --show over an invalid fleet exits 2
ok    (X) sanity: factory_*.py enumeration is non-empty and includes factory_config.py, and _find_fleet_reads self-test finds both the module-scope read and the function-scope assign-chain read in a throwaway fixture, and reports nothing else (the negative os.path.join shape is not a hit)
ok    (X) SC-18: exactly one scope, anywhere in factory_*.py (module scope or any function), opens/parses the fleet file
ok    (X) SC-18: that one reader is factory_config.py's load_fleet — no other tool bypasses it

73/73 checks passed.
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
EXIT=0
```

Note: the `RuntimeError: boom, kill before any edge` line mid-run is expected stderr from a
fault-injection fixture inside `test-factory-decompose.py` — unrelated to this task's changes,
present in the file before T-01/T-02/T-03 too — not a failure; the script reports
`PASS test-factory-decompose.py` immediately after, and no `FAIL <script>` line appears anywhere
in the output above.
