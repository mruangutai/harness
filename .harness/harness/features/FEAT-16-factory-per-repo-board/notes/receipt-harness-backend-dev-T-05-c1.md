# Receipt — harness-backend-dev — T-05 — c1

## BLUF
`test-factory-integration.py` migrated to the per-repo board shape. The file's ONE fleet fixture
builder (`fleet_dict`) now nests `board` under the single `repos[0]` entry instead of at
top-level; every case that calls it inherits the migration for free, since no other case in this
file builds its own fleet dict. Added the one new case the intent asks for: a fleet declaring two
repositories on two different board numbers, driven decompose -> claim -> land against one repo,
asserting every gh call carrying a board number names that repo's board and never the other's.
`106/106` checks pass, `PASS test-factory-integration.py`, and the full `--kind integration` run
is all-green.

## Fleet fixtures migrated: 1
`fleet_dict(workspace_root, repo, default_branch)` (line ~334) is the ONLY fleet-building function
in this file — every case (`A` through `G`) calls it, none builds a second one. Grepped for
`fleet_dict(` and for any other inline fleet dict literal before editing; found none besides the
new case's own two-repo dict, which is new code, not a migration. So "1 fleet fixture migrated"
is the correct count, verified by grep, not assumed.

Before:
```
{"schema": ..., "board": {owner, number: 9, station_field, stations}, "repos": [{name, default_branch}], "workspace_root": ...}
```
After:
```
{"schema": ..., "repos": [{name, default_branch, "board": {owner, number: 9, station_field, stations}}], "workspace_root": ...}
```
Same four values (`acme`, `9`, `Status`, `{ready: Ready, building: Building, review: Review}`) —
nothing changed but where they live. `9` is kept deliberately: the fake gh's
`issue_board_item_id` stub hardcodes `project.number: 9` on every synthetic node
(`_FAKE_GH_SRC` line ~209), so changing the number would have broken every existing targeted
board-item lookup for reasons unrelated to this task.

## The two non-fixture edits — exactly the two the intent names, no others
1. **(D-config) payload check**, was:
   `"board" in payload and "repos" in payload`
   now:
   `"repos" in payload and "board" not in payload and payload["repos"][0]["board"]["number"] == 9`
   Case name kept (`D-config`); message text now says "payload carries repos, each with its own
   board, and no fleet-level board".
2. **The `ready_option` reader** in case (F) (the decompose->claim->workspace->land happy path),
   was `fleet_data["board"]["stations"]["ready"]`, now
   `fleet_data["repos"][0]["board"]["stations"]["ready"]`. Pure reader change, no assertion touched.

No other assertion, expected exit code, or case name changed anywhere in the file. Every case from
(A) through (G) is otherwise byte-identical in its checks.

## Infrastructure addition (not one of the "two sites" — new code, not an existing-site change)
`_FAKE_GH_SRC` gained an opt-in call recorder, in the exact style `FACTORY_GIT_LOG` already uses
for the fake git: when env var `GH_CALL_LOG` is set, every call's raw argv is appended to that
path as one JSON array per line (not space-joined, because a graphql call's `query=` argument
embeds real newlines that would otherwise fragment one call across several lines). Unset for every
case except the new one, so no existing case's behaviour changed — confirmed by the full 106/106
pass with only case (H) setting the env var.

## New case (H) — the SC this task exists to add
Two-repo, two-board fleet (`acme/widget` on board 9 — the one already used everywhere else in this
file — and a new `acme/gadget` on board 42), driven `decompose --repo acme/widget` ->
`claim --repo acme/widget` -> `land --repo acme/widget --issue <n>`, with `GH_CALL_LOG` capturing
every gh call's argv. A helper, `_board_numbers_in_gh_call(argv)`, extracts a board number only
from the two positions that actually carry one — `project item-add`/`item-list`'s numeric
positional, and the field-resolve graphql call's `-F number=` (excluding the issue-item graphql
call's own `-F number=`, which is an ISSUE number, told apart by the same `projectV2(number:`
query-text check the fake gh's own dispatch already uses to distinguish the two graphql shapes).
Asserts: `42` never appears among recorded board numbers, and `9` does (anti-vacuous — proves the
first check has discriminating power, not just an empty set).

### RED proof (P-07/P-09): the new case actually catches the defect it's named for
Hashed `factory_claim.py` first: `5d02c4c4a45ed4f246fe7adb2a9064979e4ea2ea7e62240b478061cc16eccb50`.
Mutated line 226 from `factory_config.board_for(fleet, repo_name)` to
`factory_config.board_for(fleet, fleet["repos"][-1]["name"])` (always resolve the LAST repo's
board, ignoring which repo is actually being served). Ran the file standalone: exactly one check
reddened —
`FAIL  (H) no recorded gh call names the other repository's board number` with detail `['42', '9']`
— predicted by name before running. All 105 other checks stayed green. Reverted the mutation and
re-hashed: `5d02c4c4a45ed4f246fe7adb2a9064979e4ea2ea7e62240b478061cc16eccb50` — unchanged, matching
the pre-mutation hash. `git status --porcelain` on `factory_claim.py` shows only the pre-existing
uncommitted T-02 diff (this task never had a grant to touch that file and didn't).

## Verify — exact command, VERBATIM output, in full

Command:
```
.claude/skills/harness/bin/run-unit-tests.sh --kind integration
```

**Correction on the exit code.** The first run captured output through `| tee <file>; echo "EXIT=$?"`
— in this shell that reports `tee`'s own exit status, not the runner's, so `EXIT=0` from that run
was not an observed measurement of the thing that matters. Re-ran as
`run-unit-tests.sh --kind integration > <file> 2>&1; echo "REAL_EXIT=$?"` — the redirect form,
where `$?` is the runner's own status — and got `REAL_EXIT=0`, observed directly this time.

Verbatim stdout+stderr in full, exit code appended as the last line — no lines edited, curated, or
removed:

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
PyYAML is not importable and the bootstrap marker at /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpl9zaozme/.harness/.pyyaml-bootstrap could not be written ([Errno 13] Permission denied: '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpl9zaozme/.harness/.pyyaml-bootstrap'), so a one-time grant cannot be recorded — failing closed rather than granting one that never expires.
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
REAL_EXIT=0
```

(Case (G)'s live-git smoke check ran against the real system git — `/usr/bin/git, git version
2.50.1 (Apple Git-155)` — an environment fact, reported here the same way T-01's receipt reported
environment facts.)

## Diff scope, verified — exactly five hunks, matching the five intended edits
```
git diff --stat .claude/skills/harness/bin/test-factory-integration.py
 .../skills/harness/bin/test-factory-integration.py | 148 +++++++++++++++++++--
 1 file changed, 140 insertions(+), 8 deletions(-)

git diff .claude/skills/harness/bin/test-factory-integration.py | grep "^@@"
@@ -88,6 +88,14 @@ import sys                              <- stub call-recorder (infra for case H)
@@ -334,11 +342,13 @@ DEFAULT_BRANCH = "main"                 <- fleet_dict migration (the 1 fixture)
@@ -478,8 +488,10 @@ with tempfile.TemporaryDirectory() as td:   <- site 1: (D-config) payload check
@@ -642,7 +654,7 @@ with tempfile.TemporaryDirectory() as td:   <- site 2: ready_option reader
@@ -953,5 +965,125 @@ else:                                       <- new case (H)
```
Five hunks, five intended edits, nothing else touched — confirmed by command, not asserted from
memory.

## HARD BOUNDS respected
- `.harness/factory/fleet.yaml` not touched.
- `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`, `check-state.sh` not touched.
- No source module and no other test file changed — the write set is exactly
  `.claude/skills/harness/bin/test-factory-integration.py`. `factory_claim.py`'s mutation was
  applied, verified, and reverted within this session for the RED proof only, confirmed by hash
  equality above.
- Two-argument `factory_config.station(fleet, key)` not touched (T-08's).
- No case name, no expected exit code, and no assertion changed anywhere except the two sites the
  intent names.

## Files touched
- `.claude/skills/harness/bin/test-factory-integration.py`
