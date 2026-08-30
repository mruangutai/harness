# T-02 c1 receipt

## Conclusion

The cycle-0 failure was solely the selected Python environment. With `/opt/homebrew/bin` first on `PATH`, the signed unit verifier exits 0; it includes `PASS test-code-grade.py` (T-02), `PASS test-gate-policy.py` (T-07), and the prior T-01/T-07 unit registrations remain intact.

## Environment preparation

Separate preparation was performed before the signed command:

```text
export PATH=/opt/homebrew/bin:"$PATH"
command -v python3
python3 --version
```

Observed selected interpreter:

```text
/opt/homebrew/bin/python3
Python 3.14.5
```

The signed command was then invoked unchanged in that prepared environment:

```text
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```

Exit status: 0.

## Complete observed test outcome

```text
ok    every shipped YAML parses (38 files across 2 roots: .harness=36, .claude/skills/harness/teams=2)
ok    the corpus under .harness is not empty (a scan that matches nothing passes vacuously)
ok    the corpus under .claude/skills/harness/teams is not empty (a scan that matches nothing passes vacuously)
ok    .claude/skills/harness/teams holds exactly 2 team definitions (SC-05)
ok    detects ` #` opening a comment inside a flow sequence (the team-config.yaml bug)
ok    detects `: ` inside a multi-line plain scalar (the FEAT-04/05 bug)
ok    detects a sequence item opening with a backtick (the FEAT-03 bug)
ok    detects an unclosed flow sequence
ok    detects a DUPLICATED top-level key (safe_load accepts these; the harness does not)
ok    detects a duplicated key NESTED in a block (column-0 scans cannot see these)
ok    a malformed YAML in a feature's notes/ is EXEMPT (issue #628's recovered draft)
ok    the IDENTICAL body one directory up, as plan.yaml, is still flagged -- so the exemption is scoped and the scan is not simply dead
ok    a notes/ NOT under features/<id>/ is still covered
ok    a correctly quoted/folded file is NOT flagged
ok    detects a broken team definition under .agents/skills/harness/teams (SC-06)
ok    a finding names file:line:column, not just 'invalid'

16/16 checks passed.
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
ok    project_item_stations: made exactly ONE gh api graphql call
ok    project_item_stations: a stationed item maps to its station string
ok    project_item_stations: a stationed item's content carries the issue number and repo
ok    project_item_stations: a null fieldValueByName item maps to station None and is present in the output
ok    project_item_stations: two-page response makes exactly TWO calls
ok    project_item_stations: the second call carries the first page's endCursor
ok    project_item_stations: two-page response is fully accumulated (3 items)
ok    project_item_stations: the second page's items appear in the output
ok    project_item_stations: accumulated count below totalCount raises GhError
ok    project_item_stations: truncation message names both totals
ok    project_item_stations: a response missing totalCount raises GhError, never defaults it to 0
ok    project_item_stations: a null user (organization-owned board) raises GhError, never returns an empty list
ok    project_item_stations: argv passes owner/number/field/cursor as -F and query as -f
ok    project_item_stations: query has no widened plural fieldValues connection
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
ok    project_resolve: returns the project id and title when it exists
ok    project_resolve: sends owner and number as GraphQL variables
ok    project_resolve: an absent project (owner resolves, projectV2 null) returns None, raises nothing
ok    project_resolve: an unresolvable owner raises GhError naming the owner
ok    project_resolve: an organization-owned login raises GhError with the organization message
ok    project_resolve: the organization case sends no mutation
ok    project_resolve: organization and owner-absent messages differ
ok    project_create: returns the new project's id and number
ok    project_create: first call resolves the owner id
ok    project_create: second call sends the resolved owner id and the title as variables
ok    project_create: second call's query mutates createProjectV2
ok    project_create: an unresolvable owner raises GhError before any create call
ok    project_create: a null projectV2 in the create response raises GhError naming owner+title
ok    project_link_repository: returns None on success
ok    project_link_repository: resolves owner/name split from the repo string
ok    project_link_repository: second call sends the resolved project and repository ids
ok    project_link_repository: an unresolvable repository raises GhError before linking
ok    project_link_repository: an already-linked failure returns None, raises nothing
ok    project_link_repository: an UNRELATED link failure (not already-linked) still raises
ok    project_single_select_create: returns the new field's node id
ok    project_single_select_create: sends every option in the given order
ok    project_single_select_create: sends color: GRAY and description: "" for every option (GitHub rejects the mutation when either is omitted)
ok    project_single_select_create: sends the field name and project id as variables
ok    project_single_select_create: a null projectV2Field raises GhError naming the field
ok    project_single_select_extend: returns None
ok    project_single_select_extend: sends EVERY option — existing first, then additions — in the exact order given
ok    project_single_select_extend: sends color: GRAY and description: "" explicitly
ok    project_single_select_extend: sends the field id as a variable, not the project id
ok    project_single_select_extend: mutates updateProjectV2Field, never createProjectV2Field
ok    project_single_select_extend: a null projectV2Field raises GhError
ok    project_workflows: returns one dict per workflow with name/enabled/number
ok    project_workflows: sends owner and number as GraphQL variables
ok    project_workflows (user null): raises GhError rather than returning []
ok    project_workflows (projectV2 null): raises GhError rather than returning []
ok    project_workflows (workflows null): raises GhError rather than returning []
ok    default_branch_sha: returns the sha
ok    default_branch_sha: hits the ref/heads path
ok    file_at_ref: returns the decoded file body
ok    file_at_ref: hits the contents path with the ref
ok    file_at_ref: a missing file raises GhError naming repo, path and ref
ok    file_at_ref: undecodable content raises rather than returning empty
ok    file_at_ref: non-alphabet character in otherwise valid-length base64 raises
ok    file_at_ref: decodes GitHub's line-wrapped base64 content
ok    file_at_ref: an absent content field raises rather than defaulting
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
ok    run_gh: rate-limit failure raises GhError
ok    run_gh: budget message names GraphQL
ok    run_gh: budget message carries used and limit points
ok    run_gh: budget message carries the reset UTC ISO 8601 timestamp
ok    run_gh: budget remedy names REST's own usage
ok    run_gh: original gh stderr is preserved as detail
ok    run_gh: queried rate_limit exactly once, after the failing call
ok    run_gh: unrelated exit-1 raises a plain GhError, not a budget error
ok    run_gh: unrelated failure never contains the GraphQL budget headline
ok    run_gh: unrelated failure message preserves the original gh text
ok    run_gh: a rate-limit failure whose budget read also fails still raises GhError
ok    run_gh: budget-read failure names its own message, not the original rate-limit text
ok    run_gh: budget-read failure preserves the original rate-limit stderr as detail
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
ok    GhError invariant holds for 'project item stations truncated: owner project 3: totalCount'
ok    GhError invariant holds for 'project item stations response has no totalCount: owner proj'
ok    GhError invariant holds for 'project item stations unreadable: acmeorg project 3: user is'
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
ok    GhError invariant holds for 'project owner not found: nosuchowner — check the owner login'
ok    GhError invariant holds for 'organization-owned board not supported: acmeorg — run agains'
ok    GhError invariant holds for 'project owner not found: nosuchowner — check the owner login'
ok    GhError invariant holds for 'project not created: owner: t — createProjectV2 returned no '
ok    GhError invariant holds for 'repository not found: owner/nope — check the repository name'
ok    GhError invariant holds for 'gh api graphql failed: api graphql — gh: authentication requ'
ok    GhError invariant holds for 'project field not created: Status — createProjectV2Field ret'
ok    GhError invariant holds for 'project field not updated: PVT_1 field PVTSSF_1 — updateProj'
ok    GhError invariant holds for 'project owner not found: owner — check the owner login'
ok    GhError invariant holds for 'project not found: owner project 3 — check the board number'
ok    GhError invariant holds for 'project workflows unreadable: owner project 3 — unexpected G'
ok    GhError invariant holds for 'gh api contents failed: o/r missing/file.txt@release-branch '
ok    GhError invariant holds for 'file content could not be decoded: o/r path/x@main — gh retu'
ok    GhError invariant holds for 'file content could not be decoded: o/r path/lax@main — gh re'
ok    GhError invariant holds for 'file content missing from response: o/r adir@main — gh retur'
ok    GhError invariant holds for 'GraphQL budget exhausted: 5000 of 5000 points used, resets a'
ok    GhError invariant holds for 'gh issue view failed: o/nope — could not resolve to a Reposi'
ok    GhError invariant holds for 'gh reported a rate limit and the budget could not be read: a'

244/244 checks passed.
PASS test-factory-gh.py
ok    (1) load_fleet round-trips repos[0].name
ok    (1) load_fleet round-trips workspace_root
ok    (3) a repos entry has no board — this is the correct shape now
ok    (2) schema is not factory-fleet/1
ok    (2b) workspace_root is a filesystem root
ok    (8b) a leftover top-level board key raises FleetError
ok    (9) repos is missing
ok    (10) a repo entry lacks a slash in its name
ok    (11) workspace_root is not absolute
ok    (8b) a leftover top-level board key raises FleetError
ok    (8b) the message names key 'board' exactly
ok    (8b) the next_step names the whole-fleet key, not repos[].board
ok    (8b) the next_step points at github.board
ok    (8b) the next_step no longer points at repos[].board
ok    (12) repos is empty
ok    (13) repos is not a list
ok    (14) a repo entry lacks default_branch
ok    (14d) workspace_root is missing
ok    (14c) repos[].board.number is a bool, not an int
ok    (6)/(28b) validate_board coerces a digit string number to an int
ok    (15) at least 9 FleetError messages were collected
ok    (15) FleetError message obeys C-3: 'fleet schema invalid: schema — set schema: factory-fleet/1 in /var/fol'
ok    (15) FleetError message obeys C-3: "fleet key invalid: workspace_root — it is a filesystem root ('/') in /"
ok    (15) FleetError message obeys C-3: 'fleet key invalid: board — a whole-fleet board key is no longer read f'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos — set a non-empty list of repo entries in /va'
ok    (15) FleetError message obeys C-3: 'fleet repo entry invalid: repos[].name — each repo needs a name contai'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: workspace_root — set it to an absolute path in /var'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos — set a non-empty list of repo entries in /va'
ok    (15) FleetError message obeys C-3: 'fleet key invalid: repos — set a non-empty list of repo entries in /va'
ok    (15) FleetError message obeys C-3: 'fleet repo entry invalid: repos[o/r].default_branch — set a non-empty '
ok    (15) FleetError message obeys C-3: 'fleet key invalid: workspace_root — set it to an absolute path in /var'
ok    (16) repo_entry finds the listed repo
ok    (17) repo_entry raises FleetError for an unlisted name
ok    (17) the message names the unlisted name
ok    load_fleet rejects a repos entry carrying a board key
ok    load_fleet still requires repos[].name, repos[].default_branch and workspace_root
ok    validate_board accepts the six-key stations map: backlog
ok    validate_board accepts the six-key stations map: plan
ok    validate_board accepts the six-key stations map: ready
ok    validate_board accepts the six-key stations map: building
ok    validate_board accepts the six-key stations map: review
ok    validate_board accepts the six-key stations map: done
ok    validate_board rejects a stations map missing backlog
ok    validate_board rejects a stations map missing plan
ok    validate_board rejects a stations map missing ready
ok    validate_board rejects a stations map missing building
ok    validate_board rejects a stations map missing review
ok    validate_board rejects a stations map missing done
ok    (X) validate_board accepts a six-key map with all six non-empty values, and returns it
ok    (X) validate_board rejects the five-key map .harness/harness.json carried before this change
ok    (X) validate_board rejects a seven-key map that adds abandoned
ok    (X) _STATION_KEYS is exactly the six lowercase forms of feature-schema.json's status enum minus Abandoned
ok    board_for raises naming the file and the key: no board key
ok    board_for raises naming the file and the key: board is not a mapping
ok    board_for raises naming the file and the key: owner missing
ok    board_for raises naming the file and the key: number not an int
ok    board_for raises naming the file and the key: station_field missing
ok    board_for raises naming the file and the key: stations missing
ok    board_for raises naming the file and the key: stations key set wrong
ok    board_for raises naming the file and the key: a station value is empty
ok    board_for raises when the product config declares no board
ok    board_for resolves through product_config
ok    product_config reads the remote at default_branch with no checkout on disk
ok    product_config raises naming repo, path and ref when the remote read fails
ok    product_config raises naming repo, path and ref when the remote content is not JSON
ok    product_config raises naming repo, path and ref when the remote content is a JSON list, not a mapping
ok    product_config never falls back to a checkout
ok    product_config never falls back to a checkout on disk when the remote read fails
ok    product_config memoises a successful read: a second board_for makes no second remote read
ok    product_config memoisation: a failing read is not cached and the next call succeeds
ok    (29) board_station returns the per-repo ready option when the entry has its own board
ok    (30) board_station raises FleetError on an unknown key
ok    (31) board_for on an unlisted repository raises FleetError
ok    (31) the message names the unlisted repository
ok    (20) FLEET_PATH is an absolute path
ok    (21) a HARNESS_PROJECT_DIR with no MARKER is discarded
ok    (21) discarding it is announced on stderr
ok    (21) the returned root still carries harness_boundary.MARKER
ok    (21) it is the same root factory_config.FLEET_PATH was built from
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

90/90 checks passed.
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
ok    (12) feature.json records the created parent and no parent_origin (DEC-203)
ok    (13) exits 0
ok    (13) no issue is created for the adopted parent
ok    (13) feature.json records parent 777 and no parent_origin (DEC-203)
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
factory: decompose: unexpected failure: RuntimeError: boom, kill before any edge — re-run with FACTORY_DEBUG=1 for a traceback
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
ok    (C-3b) payload carries no parent_origin (DEC-203)
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
ok    (T-03) the station set to A's own ready option (Promoted), never B's (Other-Ready)
ok    (T-03) the station-validation read is against A's board and field, never B's

182/182 checks passed.
PASS test-factory-decompose.py
ok    the unpatched FEATURES_ROOT default is the migrated harness features tree
ok    the unpatched FEATURES_ROOT default names a directory that exists
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
ok    factory_claim reads default_branch from the fleet entry before any clone exists
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
ok    (B5-ter) absent features root: the reason names the absolute path that was tried
ok    (B5-ter) absent features root: the reason does not use the edge (i) text
ok    (B5-ter) absent features root: nothing claimed, zero mutating calls, stdout empty
ok    (B5-ter) plan present, task id absent: still the edge (i) text
ok    (B6) feature: null claims normally
ok    (B6) no plan file was consulted for it
ok    (B7) fresh --issue on a blocked issue exits 2 (never 3, never 0)
ok    (B7) zero mutating calls and no create_ref
ok    (B7) stderr names the blocking T-02
ok    (B7) --issue on an issue this agent already owns exits 0, gate never blocks re-entry
ok    (X) sc13b fixture: exits 1, nothing claimable
ok    (X) sc13b fixture: stdout empty
ok    (X) sc13b fixture: zero mutating calls
ok    (X) sc13b fixture: exactly eight skip lines fired (fixture didn't silently short-circuit)
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

120/120 checks passed.
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
PASS case1_presence_four_other_command_doors_survive
PASS case1_presence_check_plan_routes_survives
PASS case1_presence_factory_workspace_survives
PASS case2_absence_no_unswept_distribution_tokens
PASS case2_presence_scan_reached_the_tree
PASS case3_presence_fleet_yaml_safe_loads
PASS case3_presence_fleet_is_exactly_the_declared_set
PASS case3_absence_harness_is_not_a_fleet_member
PASS case3_presence_kaya_default_branch_is_master
PASS case3_absence_no_board_in_fleet
PASS case3_absence_no_registry_json_under_harness
PASS case4_absence_no_dec12_heading
PASS case4_absence_no_stale_marker_reintroduced
PASS case4_presence_exactly_one_dec113_heading
PASS case4_presence_dec113_precedence_rule_survives
PASS case4_absence_no_dec12_references_under_docs
PASS case4_control_docs_walk_reached_decisions
PASS case4_presence_exactly_one_dec113_index_row
PASS case4_absence_no_dec12_index_row
PASS board_lives_per_repo_not_fleet_level
PASS case6_absence_the_env_chain_occurs_nowhere
PASS case6_presence_the_resolver_defines_all_four
PASS case6_presence_sixteen_files_reach_the_resolver
PASS case6_absence_harness_root_is_gone
PASS case6_absence_repo_root_from_script_is_gone
PASS case6_absence_root_from_is_gone
PASS case6_absence_resolve_repo_root_is_gone
PASS case6_absence_wayfind_defines_no_root_of_its_own
PASS case6_presence_worktree_owner_survives
PASS case6_presence_main_checkout_resolver_survives
PASS case7_scripts_found
PASS case7_every_python_launch_isolates_the_cwd
PASS case7_the_scan_can_see_the_invocations

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
PASS case_749a: a key declared in the WRITTEN tree's schema is accepted
PASS case_749b: an UNDECLARED key is still rejected against the written tree
PASS case_749c: with no tree schema, the module's own schema still governs
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
PASS case_migrated_depth: the sweep reports ONE file, not zero
PASS case_migrated_depth: the scanning line names the migrated glob
PASS case_root_resolves: CLAUDE_PROJECT_DIR alone does not redirect the sweep (scans the real repo root, not the tmp fixture with its single file)
PASS case_root_resolves: HARNESS_PROJECT_DIR + team-config.yaml IS honoured
PASS accepted_source_issues_list_of_integers
PASS rejected_source_issues_non_integer
PASS rejected_source_issues_quoted_number
PASS rejected_undeclared_sibling_of_source_issues
PASS accepted_github_block_without_source_issues
PASS t15_unknown_feature_really_is_absent_from_the_map
PASS t15_a_entry_without_agent_is_refused_and_names_index_and_key
PASS t15_b_all_legacy_entries_validate_with_no_agent
PASS t15_c_the_rule_bites_at_index_equal_to_the_exempt_count
PASS t15_d_a_new_entry_naming_its_agent_validates
PASS t15_d_an_empty_agent_string_is_refused_so_the_check_is_on_the_value
PASS t15_e_the_positional_rule_is_load_bearing
     (red proof counts: original 1, mutant 0)

ALL PASS
PASS test-validate-feature-json.py
PASS  load_board: an explicit null board is accepted and returns None
PASS  load_board raises naming the file and the key: no board key
PASS  load_board raises naming the file and the key: board is not a mapping
PASS  load_board raises naming the file and the key: owner missing
PASS  load_board raises naming the file and the key: number not an int
PASS  load_board raises naming the file and the key: station_field missing
PASS  load_board raises naming the file and the key: stations missing
PASS  load_board raises naming the file and the key: stations key set wrong
PASS  load_board raises naming the file and the key: a station value is empty
PASS  load_board: digit string '3' -> int 3
PASS  derive_station: one building among three -> Building
PASS  derive_station: three of three done -> Review
PASS  derive_station: two done one pending -> None
PASS  derive_station: empty task list -> None
PASS  derive_station: task with NO status key counts as pending -> None
PASS  derive_station returns the declared building station
PASS  derive_station returns the declared review station
PASS  board_stations: item from another repository is EXCLUDED
PASS  board_stations: item with a station is present with its value
PASS  board_stations: item with NO status key is present with value None, not dropped
PASS  board_stations: item with content null does not crash and is not in output
PASS  read_station: on the board with a station -> (station, None)
PASS  read_station: absent from the mapping -> (None, 'not on the board')
PASS  read_station: present with a None value -> (None, 'no station set')
PASS  set_station: a failing gh raises BoardError
PASS  set_station: the raised error NAMES the issue number and the station attempted

all pass
PASS test-gh-board.py
ok    the four config keys and the item-edit call are absent from the script
ok    DENY: a branch naming a flow that does not exist on disk
ok    ALLOW: a branch naming a flow that DOES exist on disk
ok    self-gate: no github block at all -> exit 0, no stdout
ok    self-gate: github.sync false -> exit 0, no stdout
ok    self-gate: github.sync true, repo unpinned ("-" sentinel) -> exit 0, no stdout
ok    form 1 (flow id) parses: deny names the exact flow id extracted
ok    form 2 (issue number) parses: 'gh' not installed deny names issue #123

8/8 cases passed.
PASS test-branch-create-gate.py
ok   - case 1: real root exits 0
ok   - case 1: non-zero feature-dir count
ok   - case 1: non-zero doc-root count
ok   - case 1: non-zero reader-file count
ok   - case 1: X+Y+Z == 2 — every declared surface judged, none skipped
ok   - case 2: split features evidence -> exit 1, FEATURES named
ok   - case 3: migrated evidence, one legacy reader -> exit 1, named, tagged [legacy]
ok   - case 4: split docs evidence -> exit 1, DOCS named
ok   - case 5a: migrated docs, one legacy reader -> exit 1, tagged [legacy] (FINISH it)
ok   - case 5b: legacy docs, one migrated reader -> exit 1, tagged [migrated] (REVERT it)
ok   - case 6: fully migrated, both surfaces -> exit 0
ok   - case 7: FEATURES migrated, DOCS legacy -> exit 0
ok   - case 8: DOCS migrated, FEATURES legacy -> exit 0
ok   - case 9: a reader carrying NEITHER form -> exit 2, named, tagged [neither]
ok   - case 10: an unreadable reader -> exit 2, tagged [unreadable], distinct in text
ok   - case 11: no disk evidence of either shape -> exit 2, exact phrase present
ok   - case 12: a reader carrying BOTH forms -> exit 1, named, tagged [both]
ok   - case 13: MIXED on one surface, CANNOT_VERIFY on the other -> exit 2 (CV outranks)
ok   - case 14: readers present but no fleet marker -> exit 0, NOT APPLICABLE
ok   - case 14: both trailer lines print with all counts zero
ok   - case 15: marker added, legacy everywhere -> CLEAN with non-zero counts (case 14 passed because of the marker, not an empty scan)
ok   - case 16: zero rows for a surface -> CANNOT_VERIFY, exit 2, exact phrase, surface still reported
ok   - case 17: a row keyed to a non-enum surface is a LOUD error
ok   - case 18: scan() prints nothing and does not exit
ok   - case 18: clean -> exit_code 0
ok   - case 18: mixed -> exit_code 1
ok   - case 18: cannot-verify -> exit_code 2
ok   - case 19: evidence under an UNDECLARED segment -> exit 2, phrase + path named
ok   - case 19: the same shape under a DECLARED segment stays ordinary evidence
ok   - case 20 parity: MIXED, one migrated reader on legacy evidence — real gate and render name the same reader set
ok   - case 20 parity: CANNOT_VERIFY neither — real gate and render name the same reader set
ok   - case 20 parity: CANNOT_VERIFY neither — the cause clause is identical in both
ok   - case 20 parity: CANNOT_VERIFY unreadable — real gate and render name the same reader set
ok   - case 20 parity: CANNOT_VERIFY unreadable — the cause clause is identical in both
ok   - case 20 parity: CANNOT_VERIFY no-evidence — real gate and render name the same reader set
ok   - case 20 parity: CANNOT_VERIFY no-evidence — the cause clause is identical in both
ok   - case 20 parity: CANNOT_VERIFY undeclared-segment (carries detail) — real gate and render name the same reader set
ok   - case 20 parity: CANNOT_VERIFY undeclared-segment (carries detail) — the cause clause is identical in both
ok   - case 20 parity: CLEAN names nobody at either site — real gate and render name the same reader set
ok   - case 21: real root's harness/docs surface is CLEAN with migrated evidence
ok   - case 22: real root's harness/features surface is CLEAN with migrated evidence
PASS test-layout-migration.py
PASS  board-station moves the named issue to the named station
PASS  the field-set invocation actually carries the issue number and the station
PASS  an explicitly null board still exits 0 having written nothing
PASS  an unusable board config exits 2 with one line naming the key
PASS  board-station reports a BoardError on stderr naming issue and station and exits 0
PASS  board-station rejects a missing argument with exit 2
PASS  board-station rejects a UNICODE-digit argument with exit 2, not a traceback
PASS  board-station rejects a Unicode digit int() ACCEPTS, so no card moves silently
PASS  board-station rejects an over-cap digit string with exit 2, not a traceback
PASS  board-station outside a harness root writes nothing and exits 0
PASS  board-station with github.sync false writes nothing and exits 0
PASS  board-station exits 0 when set_station raises a non-BoardError exception

all pass
PASS test-board-station.py
PASS case1: both tiers present, precedence rule stated once
PASS case2: two repository segments sorted, precedence line exactly once
PASS case3: craft only, no repository text of any kind
PASS case4: nothing on disk -> exit 0, empty/no hookSpecificOutput
PASS case5a: missing agent_type -> exit 0, no traceback
PASS case5b: invalid JSON payload -> exit 0, no traceback
PASS case6: non-harness agent -> exit 0, empty stdout
PASS case7a: 41-line repository file truncates at 40, not 150
PASS case7b: 41-line craft file (no repo tier) — no truncation notice
PASS case8: 151-line craft file truncates at 150
PASS case10: repository tier, no craft tier at all
PASS case11: unparseable team-config.yaml, no fleet.yaml -> unaffected, no traceback
PASS case12: agent_type='harness-' -> exit 0, empty stdout, no leaked body
PASS case12: agent_type='harness-qa/../../etc' -> exit 0, empty stdout, no leaked body
PASS case12: agent_type='harness-*' -> exit 0, empty stdout, no leaked body
PASS case12: agent_type='harness-qa;id' -> exit 0, empty stdout, no leaked body
PASS case13: dangling symlink in repository tier -> unreadable guard skips it, no leak, clean stderr

17/17 cases passed.
PASS test-inject-expertise.py
PASS  redirect took effect before any assertion about content
PASS  fresh log file's FIRST line is JSON carrying a coverage key
PASS  coverage value mentions run_gh
PASS  coverage value mentions gh typed directly into Bash
PASS  a successful invocation writes exactly one invocation line
PASS  recorded line has all six required keys
PASS  cost equals after minus before
PASS  before/after/rc are recorded verbatim
PASS  appending a second invocation does not rewrite the coverage line
PASS  appending a second invocation adds exactly one more line
PASS  a failing invocation (rc=1) is still recorded
PASS  the failing invocation's line carries rc 1
PASS  the failing invocation's line carries its real cost
PASS  a -f value longer than 80 chars is truncated with an ellipsis
PASS  a short -F value is left untouched
PASS  HARNESS_GH_COST_LOG=0 writes no line at all
PASS  a counter read that raises does not propagate out of measured()
PASS  a counter-read failure records null before/after/cost
PASS  a counter-read failure still records the real returncode
PASS  measured() never records a line for the counter's own argv
PASS  with HARNESS_GH_COST_LOG unset, a successful invocation creates no log file
PASS  with HARNESS_GH_COST_LOG unset, a successful invocation writes no line
PASS  with HARNESS_GH_COST_LOG unset, a FAILING invocation creates no log file
PASS  with HARNESS_GH_COST_LOG unset, a FAILING invocation writes no line
PASS  factory_gh.run_gh wrap site, ON: one line written for the wrapped invocation
PASS  factory_gh.run_gh wrap site, ON: three subprocess calls (counter, real, counter)
PASS  factory_gh.run_gh wrap site, OFF: no line written
PASS  factory_gh.run_gh wrap site, OFF: exactly one subprocess call (the real call only)
PASS  gh-sync.py gh() wrap site, ON: one line written for the wrapped invocation
PASS  gh-sync.py gh() wrap site, ON: three subprocess calls (counter, real, counter)
PASS  gh-sync.py gh() wrap site, OFF: no line written
PASS  gh-sync.py gh() wrap site, OFF: exactly one subprocess call (the real call only)
PASS  factory_gh.run_gh wrap site, FAILING: GhError was raised
PASS  factory_gh.run_gh wrap site, FAILING: one line written for the wrapped invocation
PASS  factory_gh.run_gh wrap site, FAILING: the recorded rc equals the real exit code (1)
PASS  OFF, FAILING: GhError was still raised (the wrapper does not swallow the real error)
PASS  OFF, FAILING: no log file is created
PASS  OFF, FAILING: no line is written
PASS  OFF, FAILING: exactly one subprocess call (the real call only, neither counter read)

39/39 checks passed
PASS test-gh-cost-log.py
ok    A1: one row discovered
ok    A2: peak equals the corrected per-iteration MAX 747992 exactly
ok    A3: peak does not equal the naive top-level sum 1494870
ok    A-RED anchor: the iterations branch text is present in context-watch.py
ok    A-RED: mutation actually changed the source text
ok    A-RED: with the branch deleted the mutant reports the naive sum 1494870
ok    B1: exactly one row survives the agentType filter
ok    B2: the surviving row is the orchestrator's
ok    C1: row count equals the number of sidecar files found by globbing
ok    C2: exactly 2 rows are unmeasured
ok    C3: the invalid-JSON sidecar's unmeasured row names its own absolute path
ok    C4: the missing-.jsonl sidecar's unmeasured row names its own absolute path
ok    C5: the exit path is non-zero when any row is unmeasured
ok    C-RED: mutation actually changed the source text
ok    C-RED: with unmeasured rows dropped, the mutant's row count is 2, not 4
ok    D1: below-threshold config produces exactly 1 warning line
ok    D2: below-threshold config exits non-zero
ok    D3: above-threshold config produces exactly 0 warning lines
ok    D4: above-threshold config exits zero
ok    E1: a config with the key deleted never raises
ok    E2: the default-used line is present in stdout
ok    E3: the effective threshold applied is the DEFAULT 200000
ok    E4: resolve_threshold names a reason when the key is absent
ok    F-anchor: the threshold-comparison line is present in context-watch.py
ok    F-RED: the mutant copy's text differs from the original
ok    F1: the mutant, run against the below-threshold fixture, warns 0 times
ok    F2: the real script, run against the SAME fixture, warns 1 time
ok    F3: the mutant and real warning counts actually differ (mutation applied)
ok    G1: current=150000 against threshold=200000 carries the figure 50000
ok    H1: warn_for_agent returns non-None text when current is at or above threshold
ok    H2: the text carries the agent's current figure
ok    H3: the text carries the threshold figure
ok    H4: the text contains the substring handoff
ok    H5: the text contains none of blocked/stopped/refused/prevented
ok    H6: --warn-for exits 2 when the function returns text
ok    H7: --warn-for stdout is non-empty when it exits 2
ok    H8: --warn-for stdout carries the current figure
ok    H9: --warn-for stdout carries the threshold figure
ok    H10: --warn-for stdout carries the substring handoff
ok    H11: --warn-for stdout contains none of blocked/stopped/refused/prevented
ok    H12: the text OPENS with the reassurance -- the write already landed
ok    H13: the reassurance precedes the CURRENT figure, not merely co-occurs with it
ok    H14: the reassurance states no retry or undo is needed, without the word revert
ok    H15: --warn-for stdout OPENS with the same reassurance (the hook's real channel)
ok    H16: --warn-for stdout's reassurance precedes its CURRENT figure
ok    I1: warn_for_agent returns None when current is below threshold
ok    I2: --warn-for exits 0 when the function returns None
ok    I3: --warn-for stdout is EMPTY when it exits 0
ok    J-anchor: the threshold-comparison line is present in context-watch.py
ok    J-RED: the mutant copy's text differs from the original
ok    J1: the mutant's text differs from the original's text on the SAME crossing fixture
ok    J2: real warning count is 1 on the crossing fixture
ok    J3: mutant warning count is 0 on the SAME crossing fixture (fail-open silenced)
ok    K1: an absent transcript returns None rather than raising
ok    K2: --warn-for on an absent transcript exits 0
ok    K3: --warn-for on an absent transcript prints nothing
ok    K4: an absent config returns text (not None) rather than raising, because the DEFAULT 200000 is still below this fixture's current
ok    K5: --warn-for on an absent config exits 2 (falls back to DEFAULT, still crosses)
ok    K6: an absent config, with current below the DEFAULT, returns None rather than raising
ok    K7: --warn-for on an absent config, below the DEFAULT, exits 0 and prints nothing
ok    L1: at the CORRECT two-level depth, row count equals the sidecar count found by glob
ok    L2: at the WRONG one-level depth, discovery finds ZERO rows
ok    L-RED anchor: the two-level discovery block is present in context-watch.py
ok    L-RED: mutation actually changed the source text
ok    L-RED: the flattened-to-one-level mutant finds 0 rows on the correct two-level fixture
ok    L-RED: the real script's count on the same fixture is not 0 (mutation is observable)
ok    N1a: current is the last MEASURED member (300), not the last line's implied 0
ok    N1b: current is not 0
ok    N1c: entries is the measured set's cardinality (2), not the line count (3)
ok    N1d: peak is still the measured max (300)
ok    N1-RED anchor: the corrected _build_row body is present in context-watch.py
ok    N1-RED: mutation actually changed the source text
ok    N1-RED: the reverted mutant reports current=0 on this fixture
ok    N1-RED: the real script's current (300) differs from the mutant's (0)
ok    N2a: an empty measured set produces an UNMEASURED row, never current=0/peak=0
ok    N2b: the unmeasured row names the transcript path
ok    M0: exactly 3 blind-spot lines are printed
ok    M1: blind spot 1 (compaction) reports 1 measured row with a later-lower entry
ok    M2: blind spot 2 (retention) reports log_retention_days=45 as read from config_m
ok    M3: blind spot 3 (window) reports the largest peak this run saw, 100,000
ok    M4: the footer names 1 row it could not see into (the unmeasured sidecar)
81 of 81 cases passed
PASS test-context-watch.py
PASS  complete board: exits 0
PASS  complete board: performs ZERO mutations (not merely exit 0)
PASS  complete board: reports nothing to do
PASS  complete board: a second consecutive run also performs zero mutations
PASS  missing options: exits 0 and calls updateProjectV2Field exactly once
PASS  missing options: sends existing options first, in existing order, then the additions, and never touches createProjectV2Field
PASS  SC-08: no argv the fake receives contains the string 'Abandoned'
PASS  field absent: exits 0 and calls createProjectV2Field exactly once
PASS  field absent: sends all six declared options in declared order
PASS  field absent (disaster guard i): factory_gh.project_create was NOT called
PASS  field wrong type (disaster guard ii): exits 2
PASS  field wrong type (disaster guard ii): names the field and its actual data type
PASS  field wrong type (disaster guard ii): ZERO mutations of any kind reached the fake
PASS  no project: exits 3
PASS  no project: creates the project and links the repository
PASS  no project: reports the new project number
PASS  SC-01: no project: createProjectV2Field is called exactly ONCE in the SAME run -- the field never waits for a second run
PASS  SC-01: no project: the field is created ON THE NEWLY CREATED project (projectId=PVT_NEW, the id createProjectV2 returned) and is named Status
PASS  SC-01: no project: all six declared station names go over the wire BYTE FOR BYTE, in declared order, in the singleSelectOptions literal
PASS  no project: still exits 3 AFTER the field creation -- the operator must record the new number, and 3 is that signal (its meaning is unchanged)
PASS  no project: updateProjectV2Field is STILL never called -- extend must never run on a board whose field was just created with all six options
PASS  no project: reports the field it created on stdout
PASS  c4: the probe on the field-absent create branch is sent for the CREATED number (42), never the DECLARED 9
PASS  SC-01: field-create failure after a successful create+link exits 4, never 2 or 3
PASS  SC-01: the field-create failure names the CREATED project's number on stderr -- a retry that cannot see it would create a second board
PASS  SC-01: the field-create failure names the field it failed to create
PASS  SC-01: create and link really did happen before the field failure
PASS  SC-01: the field-create was actually attempted (the failure is a real call's, not a gap in the branch)
PASS  c3: fresh board whose Status field ALREADY EXISTS as single-select: still exits 3 -- the operator must record the new number, and 3 is that signal
PASS  c3: fresh board with a pre-existing Status: updateProjectV2Field is called EXACTLY once
PASS  c3: fresh board with a pre-existing Status: createProjectV2Field is NEVER called -- that is the call the real API rejected with 'Name has already been taken'
PASS  c3: the option list sent over the wire is EXACTLY the six declared, in declared order, BYTE FOR BYTE -- nothing appended, nothing preserved from GitHub's default
PASS  c3: the exact replace targets the DEFAULT field's id, the one _field_probe read off the just-created project
PASS  c3: GitHub's undeclared defaults are GONE from the payload -- Todo and In Progress appear in NO argv the fake received
PASS  c3: stdout names the options it REMOVED, so the operator sees Todo and In Progress went
PASS  c4: the fresh-board probe is sent for the CREATED project number (42), never the DECLARED 9 -- the declared number is the one that did not resolve
PASS  c4: the fresh-board options read is sent for the CREATED number (42) too -- reading the declared board's options would compute the removal set off the WRONG project
PASS  c3: an extend failure on a just-created board exits 4, never 2 or 3
PASS  c3: the extend failure names the CREATED project's number on stderr -- a retry that cannot see it would create a second board
PASS  c3: the extend failure names the field it could not set
PASS  c3: the extend really was attempted (the failure is a real call's, not a gap)
PASS  c3: a fresh board whose field is not single-select exits 4 (a project WAS created), never 2
PASS  c3: that refusal names the created number and the type it found
PASS  c3: it converts nothing -- no field mutation of any kind reached the fake
PASS  c4: a NON-GhError (ValueError from run_gh's json.loads) in the field work after a successful create+link exits 4, NEVER 2 -- 2 would claim nothing was written
PASS  c4: that unexpected failure still names the CREATED project's number on stderr -- a retry that cannot see 42 re-enters the create branch and duplicates the board
PASS  c4: it says plainly that the failure was UNEXPECTED and names the exception class, rather than dressing a ValueError up as a gh error
PASS  c4: it still tells the operator to record the number now
PASS  c4: create and link really did land before the unexpected failure
PASS  c4: a NON-GhError in the LINK call after a successful create exits 4, never 2 -- the same hole lived in that block too
PASS  c4: the link's unexpected failure names the created number and the exception class
PASS  c4: no field work was attempted after the link failed
PASS  c3 regression: an EXISTING board with an undeclared column still exits 0 and extends exactly once
PASS  c3 regression: the payload is BYTE FOR BYTE existing + missing -- the undeclared Icebox survives, in its existing position
PASS  c3 regression: the payload is NEVER the bare declared six -- that is the column-deletion disaster, and no existing-board path may reach it
PASS  c3 regression: Icebox is still in the argv the fake received -- the operator's column was not deleted
PASS  MUST-FIX 2: create-then-link failure exits 4, never 2 (this module's own 'nothing mutated' code) or 3 (the clean-success race code) -- this run DID create a real project
PASS  MUST-FIX 2: the created project's number reaches stdout BEFORE the link failure -- a retry must be able to see it and record it rather than create a duplicate
PASS  MUST-FIX 2: createProjectV2( was actually called -- the project really was created, so 'nothing mutated' would be false
PASS  MUST-FIX 2: the stderr failure names the created project's number and the repo it failed to link
PASS  linkage guard (MUST-FIX 1): refuses exit 2 when the resolved project is not linked to the served repo
PASS  linkage guard: performs ZERO mutations -- the confused-deputy write never reaches the fake
PASS  linkage guard: the refusal names the project (owner and number), the repo, and why
PASS  null board: exits 0 silently, no gh call at all
PASS  unknown --repo: exits 2, naming the repo, with no gh call at all
PASS  audit clean board: exits 0
PASS  audit clean board: reports zero findings
PASS  audit clean board: no finding-class marker on stdout
PASS  audit DECLARATION: exits 1
PASS  audit DECLARATION: names the missing key and value on stdout
PASS  audit STATION: exits 1
PASS  audit STATION: names the issue, its actual and expected station
PASS  audit REASON: exits 1
PASS  audit REASON: names the issue
PASS  audit LABEL: exits 1
PASS  audit LABEL: names the issue
PASS  audit LABEL: a not_planned issue carrying the abandoned label is NOT a finding
PASS  audit WORKFLOW (renamed/absent): exits 1
PASS  audit WORKFLOW (renamed/absent): reports 'Pull request merged' MISSING
PASS  audit WORKFLOW: the header names detection-by-name, once, on every run
PASS  audit WORKFLOW (disabled): exits 1
PASS  audit WORKFLOW (disabled): reports 'Auto-close issue' disabled
PASS  audit WORKFLOW (disabled): says no API can enable it, only the web UI can
PASS  audit STATUS (FEAT-32 shape): exits 1
PASS  audit STATUS (FEAT-32 shape): names the feature dir, recorded status, expected column and actual column
PASS  audit STATUS (FEAT-08 shape): exits 1
PASS  audit STATUS (FEAT-08 shape): names the feature dir, status Done, expected Done, actual Backlog -- no Done exemption
PASS  audit STATUS (FEAT-09 shape): exits 1
PASS  audit STATUS (FEAT-09 shape): names the feature dir, status Done, expected Done, actual Backlog
PASS  audit STATUS: a matching status and card is NOT a finding
PASS  audit STATUS: exemption 1 -- Abandoned is exempt, no STATUS finding
PASS  audit STATUS: exemption 2 -- no recorded parent is exempt, no STATUS finding
PASS  audit STATUS: exemption 3 -- factory.issues (product board) is exempt, no STATUS finding
PASS  audit #783: cross-repo audit exits 0 -- STATUS never fires for a repo that is not this checkout's own
PASS  audit #783: no STATUS finding at all -- only the skip line, never a 'records status' finding
PASS  audit #783: STATUS reports itself skipped, naming both repos, rather than silently omitting the class
PASS  audit GhError: exits 4, never 0 or 1
PASS  audit GhError: prints nothing that looks like a finding or a clean report
PASS  audit GhError: the failure is on stderr, one line
PASS  reconcile GhError: exits 4, never 0 or 1
PASS  reconcile --dry-run: exits 0 even with fixable findings present
PASS  reconcile --dry-run: performs ZERO mutations (not merely exit 0)
PASS  reconcile --dry-run: previews every fixable finding as a would-fix line
PASS  reconcile --dry-run: never writes feature.json
PASS  reconcile --apply (one of each): exits 0 once every fixable finding is resolved
PASS  reconcile --apply (one of each): STATION -- set_station moves issue #10 to Done
PASS  reconcile --apply (one of each): STATUS -- set_station moves the PARENT #40 to Building, never the issue's own number
PASS  reconcile --apply (one of each): REASON -- PATCHes issue #20 to state_reason=completed (it carries no abandoned label)
PASS  reconcile --apply (one of each): LABEL -- creates the abandoned label with b60205 directly, then adds it to issue #30
PASS  reconcile --apply (one of each): STATUS never rewrites feature.json -- the card moves, the recorded status does not
PASS  reconcile --apply (one of each): the residual report says zero fixable findings remain
PASS  reconcile (partial failure): the run continues past issue #50's failed write to issue #51 -- #51's item lookup was actually sent
PASS  reconcile (partial failure): issue #50's failure is reported on stderr
PASS  reconcile (partial failure): #50 survives as a residual STATION finding, #51 does not
PASS  reconcile (partial failure): exits 1 -- a bulk fix that stops at the first error must never report a zero exit with the board half migrated
PASS  reconcile (unfixable residuals): DECLARATION and WORKFLOW both survive on stdout
PASS  reconcile (unfixable residuals): exits 0 anyway -- neither class is ever attempted or counted
PASS  reconcile (unfixable residuals): performs zero mutations -- neither class is a write this tool can make
PASS  reconcile (Done exemption): the STATUS finding survives --apply untouched
PASS  reconcile (Done exemption): exits 0 anyway -- Done is excluded from the exit-code count the SAME way DECLARATION and WORKFLOW are (never attempted, never counted); counting it would permanently gate exit 0 on a class this tool never fixes by design, the identical reasoning the module docstring gives for excluding WORKFLOW
PASS  reconcile (Done exemption): never calls set_station for issue #85
PASS  reconcile #783: cross-repo dry-run exits 0 with zero fixable findings previewed -- STATUS never fires for a repo that is not this checkout's own
PASS  reconcile #783: never previews a write against issue #960
PASS  reconcile #783: performs zero mutations -- dry-run never writes regardless
PASS  reconcile (clean board): exits 0
PASS  reconcile (clean board): performs ZERO mutations
PASS  reconcile (clean board): re-running it again also exits 0 with zero mutations
PASS  reconcile (clean board, second run): idempotent -- exits 0, zero mutations
PASS  retitle (has milestone): exits 0
PASS  retitle (has milestone): the summary line reports it renamed
PASS  retitle (has milestone): exactly one rename call reaches the fake, for issue 101, carrying the new title verbatim in its argv
PASS  retitle (no milestone): exits 0 -- a per-ticket refusal never fails the whole run
PASS  retitle (no milestone): the refusal names issue #202 (SC-18)
PASS  retitle (no milestone): NO rename call is issued for it
PASS  MUST-FIX 3: ticket #401's rename was attempted and failed, but the run continues -- ticket #402 is still renamed rather than the run stopping at #401
PASS  MUST-FIX 3: ticket #401's failure is reported on stderr, per-ticket
PASS  MUST-FIX 3: exits 1 -- a partial failure must be signalled honestly, never exit 2's caller/declaration meaning and never a silent exit 0
PASS  MUST-FIX 3: the summary reports both the renamed and the failed count
PASS  retitle (already correct): exits 0
PASS  retitle (already correct): NOT reported as refused or renamed
PASS  retitle (already correct): the summary counts it already correct
PASS  retitle (already correct): NO rename call is issued for it
PASS  retitle (truncated enumeration): exits 2
PASS  retitle (truncated enumeration): names the returned count and the limit
PASS  retitle (truncated enumeration): NO rename call is issued -- the refusal is before any write is attempted
PASS  retitle (--dry-run default): exits 0
PASS  retitle (--dry-run default): previews the pending rename on stdout
PASS  retitle (--dry-run default): performs ZERO write calls -- not merely exit 0
PASS  retitle unknown --repo: exits 2, naming the repo, with no gh call at all
PASS  audit_findings: returns the same STATION finding cmd_audit prints
PASS  audit_findings: returns a LIST, not an exit code -- the caller decides what to do
PASS  audit_findings: prints NOTHING -- no workflow header
PASS  audit_findings: prints NOTHING -- no finding line of its own, and no count line
PASS  audit_findings: writes nothing to stderr either
PASS  audit_findings: cmd_audit's own output is UNCHANGED by the move -- it still prints the workflow header before its findings
PASS  audit_findings: a failed read raises GhError -- it never calls sys.exit
PASS  audit_findings: no board declared returns an EMPTY LIST, not an error
PASS  audit_findings: no board declared prints nothing -- cmd_audit keeps that line
PASS  audit_findings: cmd_audit STILL prints its own no-board line
PASS  audit_findings: cmd_audit STILL refuses when github.repo is not declared -- the exit stays inside the subcommand

all checks passed.
PASS test-board-lifecycle.py
reading playbook from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading/.agents/skills/harness/SKILL.md
PASS case1_absence_receive_the_team_digest
PASS case2_absence_loop_until_done
PASS case4_presence_context_watch_py
PASS case5_presence_orchestrator_context_warn_tokens
PASS case6_presence_orchestrator_context_warn_tokens_exists_at_all
PASS case6_absence_context_warn_tokens_never_reads_as_a_refusal_trigger
PASS case7_absence_record_your_phase_in
PASS case8_presence_record_your_status_in

ALL PASS
PASS test-orchestrator-playbook.py
reading playbook from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading/.claude/skills/harness-team/SKILL.md
PASS case0_region_markers_present
PASS case1_stop_half
PASS case2_wake_half
PASS case3_halves_adjacent
PASS case4_refusal_expected
PASS case5_stop_again
PASS case6_refusal_recurs
PASS case7_overrides_tool_text
PASS case8_loop_spans_turns
PASS case9_collect_on_waking
reading bound site from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading/.harness/harness/docs/DECISIONS.md
reading bound site from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading/.claude/skills/harness/bin/inflight_registry.py
PASS case_floor_DECISIONS.md
PASS case_occurrence_DECISIONS.md_6876_1
PASS case_occurrence_DECISIONS.md_6878_2
PASS case_occurrence_DECISIONS.md_6880_3
PASS case_floor_inflight_registry.py
PASS case_occurrence_inflight_registry.py_339_1
reading coverage index from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading/.harness/harness/docs/DECISIONS-INDEX.md
reading coverage entry from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading/.harness/harness/docs/DECISIONS.md
PASS case_index_row
PASS case_entry_heading
PASS case_entry_scope

ALL PASS
PASS test-lead-stop-and-wake.py
bun test v1.3.14 (0d9b296a)

 15 pass
 0 fail
 20 expect() calls
Ran 15 tests across 1 file. [14.00ms]
PASS test-omp-hooks.py
ok    Claude skills remain a real directory
ok    Agent Skills path links to Claude skills
ok    live provider-neutral tree passes
ok    missing AGENTS.md fails
ok    missing guidance is named
ok    concrete model in canonical agent fails
ok    provider coupling is named
ok    stale Claude adapter fails
ok    adapter drift is named

9/9 cases passed
PASS test-check-omp-port.py
ok    bootstrap exits 0
ok    bootstrap creates OMP canonical agent
ok    name preserved
ok    colon-bearing description preserved
ok    tools normalize to OMP names
ok    model becomes provider-neutral alias
ok    thinking level preserved
ok    skills become autoloadSkills
ok    leaf spawn policy is explicit
ok    body gains a stable identity marker
ok    Claude adapter apply exits 0
ok    Claude model mapping restored
ok    Claude effort restored
ok    Claude tools restored
ok    Claude skills restored
ok    Claude body matches canonical
ok    check accepts synchronized adapters
ok    check rejects drift
ok    drift output names adapter

18/18 cases passed
PASS test-sync-agent-adapters.py
PASS marker_constant_exact_value
PASS root_from_script_four_levels_up_no_marker
PASS root_from_script_unchanged_when_marker_exists
PASS resolve_root_strict_override_with_marker_honoured
PASS resolve_root_strict_bad_override_falls_through_to_derived
PASS resolve_root_strict_bad_override_reported_on_stderr
harness_boundary: discarding HARNESS_PROJECT_DIR='/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpdcsv9rj6' — it does not carry .harness/team-config.yaml. Falling back to the derived root '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpqdc1uaf5'.
PASS resolve_root_strict_neither_carries_marker_raises
PASS resolve_root_override_relative_normalises_to_same_absolute_path
PASS root_above_finds_marker_walking_up
PASS root_above_bare_dot_harness_does_not_satisfy
PASS root_above_nothing_above_returns_none

ALL PASS
PASS test-harness-boundary.py
PASS case_1_wayfind_directory_probe_resolves_real_root
PASS case_2_wayfind_no_marker_dies_nonzero

ALL PASS
PASS test-wayfind.py
PASS test-code-grade
PASS test-code-grade.py
ok    loader resolves qa_gate by name from fixture
ok    loader resolves review by name from fixture
ok    loader resolves uat by name from fixture
ok    loader resolves merge by name from fixture
ok    unrecognised qa_gate policy: names qa_gate
ok    unrecognised qa_gate policy: carries offending value
ok    non-string qa_gate policy: names qa_gate
ok    non-string qa_gate policy: carries offending value
ok    absent gates block: names gates
ok    absent gates block: carries offending value
ok    absent named gate: names merge
ok    absent named gate: carries offending value
ok    unparseable configuration: names config
ok    unparseable configuration: carries offending value
ok    unreadable configuration: names config
ok    unreadable configuration: carries offending value
ok    review blocks must_fix even without a severity escalation
ok    review passes a clean medium-severity report
ok    review blocks high severity
ok    blocking review blocks findings
ok    advisory review always passes
ok    unknown review severity raises loudly: names severity_max
ok    unknown review severity raises loudly: carries offending value
ok    blocking QA does not fail skipped suite
ok    QA detail reports skipped suite
ok    blocking QA blocks failed suite
ok    advisory QA always passes
PASS test-gate-policy.py
```

No T-02 production or test code changed in cycle 1. T-02 files across the task remain:

- `.claude/skills/harness/bin/code_grade.py`
- `.claude/skills/harness/bin/test-code-grade.py`

This receipt is the only cycle-1 file changed. `run-unit-tests.sh` was not edited. No formatter, linter, integration suite, project-wide build/suite, or unrelated task was run.
