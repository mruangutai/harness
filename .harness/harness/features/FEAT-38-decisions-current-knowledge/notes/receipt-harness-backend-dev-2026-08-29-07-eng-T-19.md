# Receipt — harness-backend-dev — T-19 — run 2026-08-29-07-eng

## Task

Register `test-check-decision-anchors.py` and `test-check-decision-claims.py` (bare names) in
`INTEGRATION_SCRIPTS` in `.claude/skills/harness/bin/run-unit-tests.sh`. T-18 (harness.json
integration detect, 30 entries) had already landed.

## Change made

One line touched (`INTEGRATION_SCRIPTS` array), both names appended in the array's existing
bare-name style, nothing else in the file touched.

## Environment defect encountered and recovered

The FIRST edit attempt (via the edit tool, path `.claude/skills/harness/bin/run-unit-tests.sh`
relative to worktree cwd) landed in the MAIN checkout
(`/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/run-unit-tests.sh`), confirmed by
`git -C <main> diff` showing the change and `git -C <worktree> diff` showing nothing — exactly the
documented defect. Recovery: restored main via `git show HEAD:<path>` piped to a plain file copy
(md5sum-verified identical to HEAD, never a git write command), confirmed
`git -C <main> status --porcelain -- <path>` empty, then redid the edit with `python3` string-replace
against the fully-qualified absolute worktree path
(`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-38-decisions-current-knowledge/.claude/skills/harness/bin/run-unit-tests.sh`).
Confirmed after: `git -C <worktree> status --porcelain` shows the file modified,
`git -C <main> status --porcelain -- <path>` shows nothing.

## Verify block result: exit 1 — but the registration itself is correct

Ran the plan's verify block VERBATIM (cross-checked against plan.yaml T-19, no mismatch — quoted
text below matches). **Exit status: 1.** The failing branch was:

```
printf '%s\n' "$OUT" | grep -q 'KIND-DRIFT' && { echo 'KIND-DRIFT fired'; exit 1; }
```

**This is a false positive, not a real KIND-DRIFT.** Grepped the captured output for the literal
runtime drift message `^KIND-DRIFT:` (the format the runner's own cross-check prints to stderr on a
real mismatch) — zero matches. The real drift check ran clean; `run-unit-tests.sh` proceeded to
execute every script and printed hundreds of PASS lines, which could not happen had the actual
KIND-DRIFT exit-2 path fired (it exits before running any test). The literal substring `KIND-DRIFT`
that the naive `grep -q` matched instead comes from `test-run-unit-tests-kinds.py`'s OWN legitimate
test-description lines (it is the test suite that unit-tests the KIND-DRIFT detector itself), e.g.:

```
ok    case 2: a KIND-DRIFT line NAMES test-check-state.py
ok    case 3: a KIND-DRIFT line NAMES test-render-brief.py
ok    case 4: a missing config produces a KIND-DRIFT line naming the path
```

`test-run-unit-tests-kinds.py` was already in `INTEGRATION_SCRIPTS` before T-19 — this collision is
pre-existing in the verify block's construction and unrelated to T-19's own correctness; it will
recur on ANY `--kind integration` run, with or without my two-script registration. **Finding to
escalate, not mine to fix** (out of scope: the verify text lives in plan.yaml, not in my one file).

Both required PASS lines ARE present and both checkers actually ran and passed:
```
PASS test-check-decision-anchors.py
PASS test-check-decision-claims.py
```

## Every FAIL line, enumerated by script

Only one script produced FAIL lines: `test-gen-decisions-index.py` (script-level `FAIL
test-gen-decisions-index.py`, plus its three named sub-case failures). All three are the
**expected, known-red, T-11-owned** cases named in my dispatch:
- `test_committed_index_matches_a_fresh_regeneration`
- `test_committed_index_is_complete_and_within_budget`
- `test_root_resolves_through_harness_boundary_not_the_retired_variable`

No other script printed a FAIL line anywhere in the full output below (grepped `^(PASS|FAIL) `
across all 1967 lines — 584 PASS lines total, exactly 4 FAIL lines, all four listed above). Nothing
else to report upward from the suite body itself.

## Complete verbatim runner output (1967 lines, `bash run-unit-tests.sh --kind integration 2>&1`)

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
ok    an analysis dev -- task: none AND files_touched: [] -- may say suite: n/a with PASS
ok    task: none but files WERE touched -- suite: n/a with PASS is still REJECTED, because `task: none` is a claim and the edit is the fact
ok    a REAL task whose verify passed still owes a suite result -- suite: n/a with PASS is REJECTED even with nothing touched
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

65/65 CLI cases passed.
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
ok    1: a valid pm return exits 0
ok    1: and its claim is GONE from the registry
ok    2: an invalid digest still exits 2
ok    2: and the claim is STILL released, so a re-prompt can be re-dispatched
ok    3: stop_hook_active exits 0 with a claim present
ok    3: and prints no traceback
ok    4: the returning persona's own claim is released
ok    4: and an UNRELATED harness-pm claim is untouched
ok    5: a valid digest still exits 0 with inflight_registry absent
ok    5: and stderr NAMES the missing module
ok    6: a lead returning with children in flight exits 2
ok    6: stderr carries the children-in-flight refusal
ok    6: stderr names BOTH children
ok    6: stderr cites the issue
ok    6: the lead's OWN claim was released first
ok    7: a lead with NO children carries no children marker
ok    8: a member with a claim dispatched by itself still exits 0
ok    8: and no children marker
ok    9: stop_hook_active exits 0 WITH children still on disk (D-09's residual)
ok    9: and the child claim is still there, so the bound is real
ok    10: children_in_flight_stale_claim — a FOREIGN session's claim does not refuse this return
ok    10: children_in_flight_stale_claim — and no children marker is printed
ok    11: a SAME-session child still refuses, so case 10 is not a blanket pass
ok    11: and the refusal names the single-agent release command for that child

24/24 T-09 cases passed.
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
ok    T-01 issue create carries the exact title "FEAT-05-export-fix — T-01 — streaming export rebuild" (T-16)
ok    parent created and recorded
ok    parent title carries the H1 phrase
ok    every call pins --repo
ok    T-01 unlabeled beyond harness (feature)
ok    T-02 labeled chore (ci)
ok    T-03 labeled bug (bugfix)
ok    absorbs cited in T-01 body
ok    issue numbers recorded in feature.json
ok    created parent records its NUMBER and no origin key at all (DEC-203 item 4)
ok    three sub-issues attached to the parent
ok    attach uses internal id not number
ok    labels ensured before any issue create
ok    re-run open creates nothing
ok    close-task is not a subcommand any more
ok    ship PATCHes milestone closed
ok    backlog creates 3 issues, exit 0
ok    backlog natures label correctly
ok    backlog issues carry NO milestone
ok    malformed backlog item -> ERROR exit 1
ok    empty phrase titles the parent with no trailing em-dash
ok    --parent adopts
ok    an ADOPTED parent records its number and no origin key either — where a parent came from is not recorded on either path
ok    recorded-not-attached task is attached on re-run
ok    pre-existing parent survives per-task saves
ok    a github block written with the old origin key is read without crashing, and the key is not written back
ok    phrase containing an em-dash is taken whole
ok    failed attach is a SKIP, exit 0, for the new subcommand too (SC-12)
ok    issue recorded before the failed attach survives the crash
ok    abandon closes 3 subs not_planned
ok    abandon closes the milestone
ok    abandon posts via --body-file
ok    abandon closes an ADOPTED parent not_planned — origin decides nothing now
ok    abandon labels sub-issue #41 abandoned
ok    abandon labels sub-issue #42 abandoned
ok    abandon labels sub-issue #43 abandoned
ok    abandon labels the adopted parent it closed
ok    ensure_labels sends colour b60205 for the abandoned label
ok    abandon closes the parent not_planned, exactly once
ok    abandon labels sub-issue #41 abandoned
ok    abandon labels a created parent that closes
ok    abandon closes a parent that carries no origin at all — the leave-open default is gone, and the key is still absent from the saved block
ok    abandon without --reason-file exits 1
ok    abandon with an empty reason file exits 1
ok    abandon with a nonexistent reason path exits 1
ok    abandon with an unreadable reason file exits 1
ok    abandon with a BINARY reason file exits 1, not a traceback
ok    abandon with no recorded milestone never builds milestones/None
ok    abandon with no milestone but WITH issues still records status Abandoned
ok    abandon with sync disabled -> SKIP, exit 0
ok    ship closes NO issue, whatever the recorded parent_origin (DEC-203)
ok    ship with no board configured says so, in one line
ok    ship with no board configured STILL closes the milestone -- the issue lifecycle runs to completion
ok    ship with no board configured STILL records the terminal status
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
ok    start-task exits 0
ok    start-task sets T-02's OWN issue station to Building
ok    start-task then sets the PARENT's station to Building (distinct item id)
ok    exactly two field-sets, one per item id
ok    #642 replay: exits 0 (a refusal is not a failure, D-02/DEC-146)
ok    #642 replay: no station write of any kind reaches the fake
ok    #642 replay: refuses, naming the issue, the task id, the current station and why
ok    open at Backlog: exits 0
ok    open at Backlog: still writes the sub-issue's station to Building
ok    open at Backlog: still writes the parent's station too
ok    open but card at Done: exits 0
ok    open but card at Done: refused, no station write reaches the fake
ok    open but card at Done: refusal line printed
ok    closed but card at Building: exits 0
ok    closed but card at Building: refused, no station write reaches the fake
ok    closed but card at Building: refusal line printed
ok    guard read fails: exits 0 (a failed guard read is not a gate either)
ok    guard read fails: falls through and still writes the sub-issue's station
ok    guard read fails: falls through and still writes the parent's station
ok    guard read fails: one ERROR line printed, not a silent swallow
ok    custom stations: exits 0
ok    custom stations: sets the sub-issue's station to the DECLARED building option (OPT_DOING), not the hardcoded literal OPT_BUILDING
ok    custom stations: prints the declared name ("Doing"), never the literal "Building"
ok    every task done: exits 0
ok    every task done: the parent card is set to Review
ok    a Done feature exits 0
ok    a Done feature writes NO PARENT station — the terminal exemption
ok    loud pair (item-edit fails): process still exits 0
ok    loud pair (item-edit fails): stderr carries the gh-sync: ERROR line naming the card whose write failed
ok    loud pair (item-edit fails): a failed card write does not stop the write that follows it — the parent write was still attempted
ok    loud pair (gh absent): one SKIP line, exit 0
ok    loud pair (gh absent): no item-edit call is even attempted
ok    no board configured: open exits 0
ok    no board configured: prints the plain no-board line, not a SKIP
ok    no board configured: open still recorded T-02's issue — the lifecycle ran, not skipped
ok    no board configured: start-task exits 0
ok    no board configured: no item-edit call is ever made
ok    no board configured: the issue lifecycle still ran — T-01 and T-02 are recorded
ok    an unusable board config is a loud failure, not a skipped station write
ok    status: an unknown value is refused with exit 2
ok    status: the refusal names the offending value
ok    status: an unknown value writes no station of any kind
ok    status: an unknown value leaves feature.json's status unrecorded
ok    status Ready: exits 0
ok    status Ready: writes exactly the three sub-issues, never the parent
ok    status Ready: every write selects the declared Ready option
ok    status Ready: feature.json status recorded as Ready
ok    status Review: exits 0
ok    status Review: writes exactly the parent plus every sub-issue
ok    status Review: every write selects the declared Review option
ok    status Plan: exits 0
ok    status Plan: writes NO station at all
ok    status Plan: feature.json status recorded
ok    status Done: exits 0
ok    status Done: writes NO station at all
ok    status Done: feature.json status recorded
ok    status Abandoned: exits 0
ok    status Abandoned: writes NO station at all
ok    status Abandoned: feature.json status recorded
ok    status Ready, zero sub-issues: exits 0
ok    status Ready, zero sub-issues: no set_station call at all — no parent fallback
ok    status Ready, zero sub-issues: prints one line saying there is nothing to move
ok    status Ready, unsigned plan: refused with exit 2
ok    status Ready, unsigned plan: names the value Ready in the refusal
ok    status Ready, unsigned plan: no station write reaches the fake
ok    status Ready, unsigned plan: feature.json status is NOT recorded as Ready
ok    status Review, unfinished tasks: refused with exit 2
ok    status Review, unfinished tasks: names the value Review in the refusal
ok    status Review, unfinished tasks: no station write reaches the fake
ok    status Review, unfinished tasks: feature.json status is NOT recorded as Review
ok    status Ready, one write raises: process still exits 0
ok    status Ready, one write raises: ITEM_41's write was attempted (and is what failed)
ok    status Ready, one write raises: the REMAINING sub-issues were still written
ok    status Ready, one write raises: one stderr ERROR line naming the issue
ok    status Ready, one write raises: feature.json status still recorded as Ready
ok    migrated_depth: a segment-deep feature dir resolves the root rather than skipping
ok    not_onboarded: no harness.json above -> the fallback reaches skip() at exit 0
ok    ship records feature.json status Done
ok    abandon records feature.json status Abandoned
ok    ship leaves every other top-level key unchanged
ok    abandon leaves every other top-level key unchanged
ok    open records source_issues from plan.yaml
ok    source_issues survives every save during a full open run
ok    open on a plan with no source_issues records none and still succeeds
ok    save_recorded refuses when feature.json is absent
ok    record-pr writes the number when the branch has exactly one merged PR
ok    record-pr leaves pr null when the branch has no merged PR
ok    record-pr leaves pr null when the branch has two merged PRs
ok    record-pr never overwrites a pr that is already an integer
ok    record-pr --pr writes the number given without querying
ok    ship records the pr and then the status
ok    record-pr exits 0 on every branch case
ok    record-pr --pr abc exits non-zero with no traceback
ok    the closes subcommand exits non-zero and is named as unknown
ok    the closes subcommand renders NO Closes line — not even a deprecation notice carrying one
ok    no function in gh-sync.py emits a closing-keyword line
ok    cmd_open still mirrors plan.yaml's source_issues into feature.json, in order
ok    ship: exits 0
ok    ship: card #41 reaches the done station
ok    ship: card #42 reaches the done station
ok    ship: card #50 reaches the done station
ok    ship: card #40 reaches the done station
ok    ship: closes NO issue - no `issue close` argv anywhere in the run
ok    ship: closes NO issue - no state=closed PATCH against an ISSUE (the milestone PATCH is a milestone, not a card)
ok    ship: the milestone is still PATCHed closed
ok    ship: prints the all-clear line when nothing was held and nothing failed
ok    ship: prints NO HELD summary line when nothing was held
ok    ship: prints NO FAILED line when nothing failed
ok    ship: no line contains 'gh-sync: SKIP' - post-merge-sweep.sh's worktree gate greps that literal and a healthy run must not trip it
ok    ship: records the terminal status
ok    ship D-10: a task sub-issue reaches Done regardless of what sub_issues would say about it
ok    ship D-10: ship makes NO sub_issues read for a task sub-issue - the depth-1 exemption is a saved call, not just a skipped branch
ok    ship HELD: the parent is NOT moved to Done
ok    ship HELD: exactly ONE held line, naming the LOWEST-numbered open child
ok    ship HELD: the parenthetical distinguishes a stationed child from a missing one
ok    ship HELD: the summary line lists the held card and its child
ok    ship HELD: a run with holds and no failures prints NO FAILED line
ok    ship HELD: exit status is still 0 - a hold is a healthy outcome
ok    ship HELD: a child that is not on the board at all counts as OPEN, with its own parenthetical
ok    ship HELD: a child on the board with NO station set counts as OPEN, reported as not at Done rather than not on the board
ok    ship ORDERING: a parent whose only open children are cards THIS RUN lands reaches Done in that same run
ok    ship REFRESH: a source_issues entry that is itself a child of the parent, moved in step 5's own pass, still lets the parent land in the same run
ok    ship UNKNOWN: a sub_issues read that fails leaves the card UNMOVED - unknown is never childless
ok    ship UNKNOWN: it prints one stderr line naming the issue
ok    ship UNKNOWN: the miss is REPORTED on the FAILED line, so the sweep keeps the tree
ok    ship UNKNOWN: exit status is still 0
ok    ship FAILED: one card's failure does not stop the remaining child writes
ok    ship FAILED: the summary names exactly the card whose write failed
ok    ship FAILED: the FAILED line never covers a held card - this run held nothing
ok    ship FAILED: exit status is still 0 - best-effort per card (DEC-146)
ok    ship FAILED: no line carries 'gh-sync: SKIP'
ok    ship AUDIT: it runs, and every finding is printed under ship's own prefix
ok    ship AUDIT ORDERING: a card THIS RUN moved to Done produces no STATION finding - the audit runs after the writes, not before
ok    ship AUDIT: a summary line counts the findings
ok    ship AUDIT: no audit line carries 'gh-sync: SKIP' or 'gh-sync: FAILED'
ok    ship AUDIT: an audit that cannot run leaves the exit status 0
ok    ship AUDIT: it prints one stderr line saying the audit could not run
ok    ship AUDIT: the cards were still written and the status still recorded
ok    REQ-10 guard: status Review still writes the review station for #40
ok    REQ-10 guard: status Review still writes the review station for #41
ok    REQ-10 guard: status Review still writes the review station for #42
ok    SC-12: `status Ready` writes NO done station - ship is the only writer
ok    SC-12: `start-task` writes NO done station - ship is the only writer
ok    SC-12: `abandon` writes NO done station - ship is the only writer
ok    SC-12 (secondary): exactly one place BINDS the done station for writing, and it is cmd_ship's own local
ok    abandon dry run: exits 0
ok    abandon dry run: makes ZERO writes - no close, no label, no comment
ok    abandon dry run: one would-line per recorded sub-issue
ok    abandon dry run: the sub-issue line names all four acts — detach, close, label, and the return to the backlog — so the dry run and the real run diff by eye
ok    abandon dry run: the parent line says it returns to the backlog too
ok    abandon dry run: one would-line for the milestone
ok    abandon dry run: the parent is LABELLED as the parent, never as one more number - it now closes unconditionally, so a column of numbers would hide the epic
ok    abandon dry run: it says what the operator must do next
ok    abandon dry run: does NOT record the status
ok    abandon --yes: the numbers it actually closes, in order, equal the numbers the dry run listed - ONE renderer, so the operator confirms the list that executes
ok    abandon --yes: every sub-issue is closed not_planned
ok    abandon --yes: the PARENT is closed not_planned whatever its history - the confirmation replaces the old origin gate
ok    abandon --yes: everything it closed is labelled abandoned, parent included
ok    abandon --yes: the milestone is closed
ok    abandon --yes: records status Abandoned
ok    abandon --yes BEFORE the directory: does not die with 'is not a directory'
ok    abandon --yes BEFORE the directory: behaves identically - status recorded, parent closed
ok    --yes on ship exits 1 with a caller-error message naming the subcommand - a flag that silently does nothing teaches the operator it is harmless everywhere
ok    --yes on ship makes no gh call at all
ok    legacy origin key: abandon reads the block without crashing
ok    legacy origin key: the parent closes anyway - the key is read but decides nothing
ok    abandon: exits 0 with a board configured
ok    abandon: card #41 is returned to the BACKLOG station, not left at Done
ok    abandon: card #42 is returned to the BACKLOG station, not left at Done
ok    abandon: card #40 is returned to the BACKLOG station, not left at Done
ok    abandon: NO card is written to the done station
ok    abandon: the backlog write comes AFTER the close — a write before it would be overwritten by GitHub's Item-closed workflow
ok    abandon: sub-issue #41 is DETACHED from parent #40, so it cannot hold the parent open
ok    abandon: sub-issue #42 is DETACHED from parent #40, so it cannot hold the parent open
ok    abandon: the detach comes BEFORE the close — a detach is a write on the parent, and doing it first means a failed close cannot leave a half-detached child
ok    abandon: everything it closed still carries the abandoned label
ok    abandon: still records status Abandoned
ok    abandon: exits 0 even when a detach cannot be made
ok    abandon: the close still runs when the detach fails
ok    abandon exits 0
ok    abandon writes BACKLOG for the sub-issue's card, never the done station
ok    abandon writes BACKLOG for the parent's card too
ok    the close precedes the backlog write, because a close moves the card to done at t+0s and a write made before it would be silently overwritten
ok    a failing --add-label does not abort the run — no SKIP, exit 0
ok    a failing --add-label on the FIRST issue still leaves every later issue closed
ok    a failing --add-label still leaves the card in the BACKLOG, never at done — the cosmetic write cannot cost the state correction
ok    the label failure is REPORTED on stderr, naming the issue
ok    _record_status still runs — feature.json reaches Abandoned

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
ok - INV-28 warns on a Done feature whose pr is null
ok - INV-28 is silent on a Done feature whose pr is an integer
ok - INV-28 is silent on an Abandoned feature whose pr is null
ok - INV-28 is silent on a feature that is not terminal
ok - INV-28 names each offending feature on its own line
ok - INV-28 is silent when github.sync is off
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
ok - case (u.7) F-B: an unimportable harness_boundary.py is a REFUSAL that names it, not a silent skip of INV-25
ok - (v.1) a mis-columned card is a VIOLATION naming feature, task, plan status and column found
ok - (v.2) the corrected twin reports NOTHING
ok - (v.3) a feature whose status is Done is exempt even with every card wrong
ok - (v.4) tasks in flight with an EMPTY issues map is a violation
ok - (v.5) a recorded issue absent from the board is CANNOT VERIFY, not a clean pass
ok - (v.6) the parent card disagreeing with the derivation is a violation
ok - (v.7) a gh binary that does not exist records NO INV-26 finding
ok - (v.8) a mis-columned done card is reported even when the plan derives NO parent station
ok - (v.9) the corrected twin of v.8 reports NOTHING, and a None derivation raises no parent finding
ok - (v.10) an all-pending plan reports NOTHING even with every card wrong
ok - (v.11) a factory-published feature (factory.issues recorded, github.issues empty) raises NO mirror-never-ran violation
ok - (v.12) the same fixture with an EMPTY factory.issues still fires — the exemption keys on recorded issues, not the block
ok - INV-26 reports a violation when the board declaration is unusable
ok - INV-26 completes the gate rather than aborting on an unusable board
ok - (v.14) an explicit null board records NOTHING — not a violation, and no traceback
ok - (v.T22a) at status Review, a done task's card reading Review is ACCEPTED
ok - (v.T22b) at status Review, a done task's card reading Building is ACCEPTED
ok - (v.T22c) THE BOUND: at status Building, a done task's card reading Review is still a VIOLATION
ok - (v.T22d) the widening does NOT reach Backlog: a done task's card there is a VIOLATION even at status Review
ok - INV-26 expects the declared station for status: backlog
ok - INV-26 expects the declared station for status: building
ok - INV-26 expects the declared station for status: done
ok - (w.1) an Abandoned feature's unapproved BRIEF raises NOTHING
ok - (w.2) the same fixture at status Plan IS reported
ok - (x.1) a mixed tree -> exit 1, INV-27 names the reader, its form-set tag and the remedy
ok - (x.2) an unjudgeable tree -> exit 1, INV-27 CANNOT VERIFY
ok - (x.3) an applicable clean tree -> NO INV-27 line
ok - (x.4) no control-plane marker -> NO INV-27 line
ok - (x.5) unimportable layout_migration -> INV-27 CANNOT RUN, exit 1
ok - INV-29 (a.1) default branch Done + standing worktree -> one INV-29 at VIOLATION
ok - INV-29 (a.2) the SAME fixture at Review -> no INV-29 line at all
ok - INV-29 (b.1) the line NAMES the worktree directory found
ok - INV-29 (b.2) the line CARRIES the removal command
ok - INV-29 (b.3) the command carries THIS worktree's own repo and id
ok - INV-29 (b.4) and NOT the sibling worktree's identity
ok - INV-29 (b.5) the sibling worktree gets its own line with its own id
ok - INV-29 (c.1) working tree Done, default branch Review -> silent
ok - INV-29 (c.2) the INVERSE — default branch Done, working tree Review -> one line
ok - INV-29 (d.1) a dirty Done worktree still fires
ok - INV-29 (d.2) the message says the tree is DIRTY
ok - INV-29 (d.3) and says remove will DECLINE until the changes are dealt with
ok - INV-29 (e) a Done feature's worktree in a SECOND fleet-declared repository produces an INV-29 line from ONE run
ok - INV-29 (f.1) genuinely absent from the default branch -> SILENT
ok - INV-29 (f.2) a full-named Done sibling -> fires
ok - INV-29 (f.3) a SHORT-named worktree whose landed dir is full-named and Done -> fires
ok - INV-29 (f.4) the SHORT-named worktree's command carries its OWN directory name
ok - INV-29 (f.5) and NOT the landed full name
ok - INV-29 (f.9) SC-17(c): the printed script path resolves in a real checkout
ok - INV-29 (f.7) SC-17(c): the printed command RUNS and exits 0
ok - INV-29 (f.8) SC-17(c): and that worktree is GONE afterwards
ok - INV-29 (f.6) a landed feature.json that is present but UNPARSEABLE -> fires
ok - INV-30 fires at VIOLATION on a Done feature whose milestone is open, naming the feature, the number and the remedy
ok - INV-30 is silent when the SAME Done feature's milestone is closed (status is Done in both halves)
ok - INV-30 records nothing and raises no error when gh is unauthenticated
ok - INV-30 is silent on a Done feature whose recorded milestone is null
ok - INV-30 is silent on a non-terminal feature whose milestone is open
ok - case (t14-d): a non-seam stem missing a heading is reported by name (1 line(s))
ok - case (t14-e): a non-seam stem over the cap is reported (74 lines, 1 line(s))
ok - case (t14-f): a malformed seam-stem note is reported EXACTLY once, not twice (count 1)
ok - case (t14-g): a literal-exempt feature still has its EXISTING note shape-checked (1 shape) while missing notes stay suppressed (0 missing)
ok - case (t14-h): three well-formed notes, two seam stems and one non-seam, raise ZERO shape lines (0)
ok - case (t14-red): the pass is load-bearing — original reports 1, mutant reports 0
ok - case (t10-a): a handoff with a body under every heading raises no shape line (0)
ok - case (t10-b): the Next section emptied is reported as an empty section, not a missing one (1 line(s))
ok - case (t10-c1): the Trust section emptied is reported as an empty section, not a missing one (1 line(s))
ok - case (t10-c2): the Dead ends section emptied is reported as an empty section, not a missing one (1 line(s))
ok - case (t10-c3): the Working set section emptied is reported as an empty section, not a missing one (1 line(s))
ok - case (t10-red): the empty-body check is load-bearing — original 1, mutant 0
ok - INV-31 fires at VIOLATION when core.hooksPath is unset, saying so and carrying the fix command
ok - INV-31 fires when core.hooksPath names another directory, quoting the value found
ok - INV-31 is silent when an ABSOLUTE core.hooksPath names the same directory
ok - INV-31 reports a MISSING post-merge as its own finding, with its own fix, never as a tail on the config one
ok - INV-31 reports a NON-EXECUTABLE post-merge, naming the mode it found and the fix
ok - INV-31 is SILENT when the hook is installed and executable
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
ok    case1: token-present craft file exits 0
ok    case1: output contains ADVISORY
ok    case1: output names DEC-042
ok    case1: output still contains OK 
ok    case1: token-removed file produces NO ADVISORY line
ok    case2: token class DEC-\d+ produces an advisory naming 'DEC-042'
ok    case2: token class INV-\d+ produces an advisory naming 'INV-007'
ok    case2: token class FEAT-\d+ produces an advisory naming 'FEAT-12'
ok    case2: token class \.harness/ produces an advisory naming '.harness/'
ok    case2: token class \.claude/ produces an advisory naming '.claude/'
ok    case2: token class check-[a-z-]*\.sh produces an advisory naming 'check-foo-bar.sh'
ok    case2: token class factory_[a-z]*\.py produces an advisory naming 'factory_baz.py'
ok    case2: token class gh-sync produces an advisory naming 'gh-sync'
ok    case2: token class harness\.json produces an advisory naming 'harness.json'
ok    case2: token class team-config produces an advisory naming 'team-config'
ok    case3: token + real violation exits 1
ok    case3: token + no violation exits 0
ok    case4: repository-tier file with DEC-042 has no ADVISORY line
ok    case5: 41-line repository-form file over budget, names 40
ok    case5: 41-line craft-form file is NOT reported over budget
ok    case5: 151-line craft-form file over budget, names 150
ok    case6: bare-path invocation over the repository budget, names 40

(extra) 22/22 cases passed.
PASS test-check-expertise.py
ok - test_row_per_distinct_dec_matches_authority
ok - test_argv_is_validated_and_only_the_write_path_writes
ok - test_malformed_row_is_reported_not_silently_dropped
ok - test_refs_graph_omits_ids_with_no_live_heading
ok - test_preserves_hand_written_rulings_by_dec_number
ok - test_strips_inline_ok_stale_marker_on_a_row
FAIL - test_committed_index_matches_a_fresh_regeneration: generator exited 1 — the committed index cannot be reproduced: ORPHAN: DEC-19 'One shipped shell script, `check-domain.sh`, enforces per-agent `domain` path globs through a `PreToolUse` hook — the single deliberate exception to files-only delivery. — SUPERSEDED BY DEC-84 — SUPERSEDED BY DEC-85' has a ruling in the index but no live heading in .harness/harness/d
FAIL - test_committed_index_is_complete_and_within_budget: 3 row(s) in /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-38-decisions-current-knowledge/.harness/harness/docs/DECISIONS-INDEX.md exceed the 30-word ruling cap — shorten the ruling after ' :: ' on each listed row: DEC-92 (36), DEC-102 (34), DEC-37 (33)
ok - test_orphaned_ruling_is_reported_not_silently_dropped
FAIL - test_root_resolves_through_harness_boundary_not_the_retired_variable (a): a markerless HARNESS_PROJECT_DIR override exited 1: harness_boundary: discarding HARNESS_PROJECT_DIR='/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpnxg4mhug' — it does not carry .harness/team-config.yaml. Falling back to the derived root '/Users/
ok - test_no_amendment_construct_survives_in_the_authority
FAIL test-gen-decisions-index.py
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
ok    #556 control: from a clean cwd the out-of-domain shell write is REFUSED
ok    #556: a harness_boundary.py in the CWD does not become the guard's resolver

29/29 worktree-boundary cases passed.

ok    a granted path inside <segment>/<repo>/<id> is ALLOWED on the Bash route
ok    DEC-153 pinned: an UNGRANTED path at the same depth is ALSO allowed — the carve-out is blanket and depth-agnostic
ok    an out-of-place linked worktree is REFUSED on the Bash route, and the message names where worktrees belong

3/3 deep-layout Bash-route cases passed.

ok    1. SC-03 refuse: a governed agent checking out the default branch
ok    2. SC-03 refuse: harness-ORCHESTRATOR too — D-04 forbids exempting it, so this is asserted rather than assumed
ok    3a. SC-03 refuse: switching to the previous branch
ok    3b. SC-03 refuse: a hard reset one commit back
ok    3c. SC-03 refuse: a rebase onto the default branch
ok    3d. SC-03 refuse: a checkout carrying a leading -C directory option
ok    4a. SC-03 allow: restoring one file via a pathspec checkout
ok    4b. SC-03 allow: status moves nothing
ok    4c. SC-03 allow: staging one file
ok    4d. SC-03 allow: a reset naming one pathspec, no mode flag
ok    4e. SC-03 allow: `git show` NAMES a commit without moving to it — T-01's and T-02's verify blocks depend on this
ok    5. the main session is NOT governed: the same checkout with no agent_type exits 0
ok    6. the UNDECIDABLE case: a git call whose subcommand cannot be determined is refused, and says so
ok    7a. SC-07 Bash route refuse: a FORCED `git worktree remove` names the CLI
ok    7b. SC-07 Bash route refuse: a FORCED `git worktree prune` names the CLI
ok    8. SC-07 the PAIRED direction: the same removal WITHOUT --force is not refused here — git decides and refuses a dirty tree itself
ok    9a. the existing destination refusal is unchanged: an add OUTSIDE the segment still exits 2
ok    9b. ...and an add INSIDE the segment still exits 0
ok    10. RULING R-01: harness-DEV-OPS is refused a branch checkout — this FAILS against any build that places the rule after the dev-ops early return
ok    11. ...and the WRITE exemption is INTACT: dev-ops still writes a path it is not granted, exit 0. Without this half, case 10 is satisfied by deleting the exemption and removing DEC-151's recovery path.

20/20 HEAD-move and forced-removal cases passed.

PASS test-bash-write-guard.py
ok    a scratch script in /tmp
ok    /var/folders temp dir (macOS mktemp)
ok    an absolute path in another checkout
ok    documentor writing the moved harness docs
ok    documentor writing its own expertise
ok    a shared path in the harness base is now REFUSED (product-shaped target)
ok    documentor may not write source
ok    documentor may not write another agent's expertise
ok    documentor may not write bin/
ok    a repo path reached via .. still blocks
ok    a repo path reached via a long .. chain still blocks
ok    the pre-move docs path is REFUSED after the migration

12/12 cases passed.

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
ok    C harness base: explicit Harness entries resolve, including AGENTS.md, .agents/** and .omp/**
ok    C harness base: .harness/*/docs/** was NOT widened to docs/** — the same persona permitted .harness/harness/docs/guide.md is REFUSED docs/guide.md
ok    C product base: product README.md, docs/ and .github/ remain writable, while Harness grants to .agents/ and .omp/ stay checkout-local
ok    T-04 resolve PAIR: a product path names the src/** owner, the SAME path in the harness root resolves to NOBODY
ok    T-04 resolve: a path under workspace_root for an undeclared repo resolves to NOBODY, never silence
ok    T-04 resolve, LIVE tree: .harness/harness/docs/SPEC.md names harness-documentor — the named entries hold target-side
ok    SYMLINK PAIR: a link out of a granted directory is REFUSED at its real target, and the ordinary granted write still PASSES
ok    SYMLINK: the refusal names the REAL target, not the link path — an agent told it may not write the docs path would file a bug against the wrong file

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
ok    #556 control: from a clean cwd the out-of-domain write is REFUSED
ok    #556: a harness_boundary.py in the CWD does not become the gate's resolver

16/16 worktree-boundary cases passed.

ok    the fixture worktree is a REAL linked worktree, parsed and legitimate
ok    the roster walk finds exactly 16 agents carrying a name and a list domain
ok    harness-ai-dev: in-worktree grant equals root grant, and names harness-ai-dev
ok    harness-backend-dev: in-worktree grant equals root grant, and names harness-backend-dev
ok    harness-code-reviewer: in-worktree grant equals root grant, and names harness-code-reviewer
ok    harness-data-engineer: in-worktree grant equals root grant, and names harness-data-engineer
ok    harness-dev-ops: in-worktree grant equals root grant, and names harness-dev-ops
ok    harness-documentor: in-worktree grant equals root grant, and names harness-documentor
ok    harness-eng-lead: in-worktree grant equals root grant, and names harness-eng-lead
ok    harness-frontend-dev: in-worktree grant equals root grant, and names harness-frontend-dev
ok    harness-orchestrator: in-worktree grant equals root grant, and names harness-orchestrator
ok    harness-pm: in-worktree grant equals root grant, and names harness-pm
ok    harness-product-lead: in-worktree grant equals root grant, and names harness-product-lead
ok    harness-qa: in-worktree grant equals root grant, and names harness-qa
ok    harness-security-reviewer: in-worktree grant equals root grant, and names harness-security-reviewer
ok    harness-ui-reviewer: in-worktree grant equals root grant, and names harness-ui-reviewer
ok    harness-validator-lead: in-worktree grant equals root grant, and names harness-validator-lead
ok    harness-visual-designer: in-worktree grant equals root grant, and names harness-visual-designer
ok    SC-02c harness-ai-dev: DEEP-layout grant equals root grant, and names harness-ai-dev
ok    SC-02c harness-backend-dev: DEEP-layout grant equals root grant, and names harness-backend-dev
ok    SC-02c harness-code-reviewer: DEEP-layout grant equals root grant, and names harness-code-reviewer
ok    SC-02c harness-data-engineer: DEEP-layout grant equals root grant, and names harness-data-engineer
ok    SC-02c harness-dev-ops: DEEP-layout grant equals root grant, and names harness-dev-ops
ok    SC-02c harness-documentor: DEEP-layout grant equals root grant, and names harness-documentor
ok    SC-02c harness-eng-lead: DEEP-layout grant equals root grant, and names harness-eng-lead
ok    SC-02c harness-frontend-dev: DEEP-layout grant equals root grant, and names harness-frontend-dev
ok    SC-02c harness-orchestrator: DEEP-layout grant equals root grant, and names harness-orchestrator
ok    SC-02c harness-pm: DEEP-layout grant equals root grant, and names harness-pm
ok    SC-02c harness-product-lead: DEEP-layout grant equals root grant, and names harness-product-lead
ok    SC-02c harness-qa: DEEP-layout grant equals root grant, and names harness-qa
ok    SC-02c harness-security-reviewer: DEEP-layout grant equals root grant, and names harness-security-reviewer
ok    SC-02c harness-ui-reviewer: DEEP-layout grant equals root grant, and names harness-ui-reviewer
ok    SC-02c harness-validator-lead: DEEP-layout grant equals root grant, and names harness-validator-lead
ok    SC-02c harness-visual-designer: DEEP-layout grant equals root grant, and names harness-visual-designer
ok    the depth is not load-bearing: <segment>/a/b/c/<id> resolves like the root
ok    WORKTREE_REL_RE no longer exists on harness_boundary
ok    linked_worktrees returns [] for a checkout with no worktrees
ok    linked_worktrees returns exactly the two registered checkouts, as realpaths

38/38 worktree grant-parity cases passed.

ok    baseline: the main checkout refuses an over-budget STATE.md with the SHAPE reason naming DEC-150
ok    SC-09: at ONE level the shape refusal still names DEC-150 (it did at eeabc59 and must not regress)
ok    at TWO levels the write route refuses on SHAPE, naming DEC-150 — asserted on the WORDING, because the domain refusal also exits 2
ok    the sweep reaches a file inside a TWO-LEVEL registered worktree (invisible at eeabc59, and invisible SILENTLY)
ok    ...and the finding names the WORKTREE it came from, not the stripped path
ok    D-09's ACCEPTED COST, asserted: a directory under the segment with NO pointer pair is not swept
ok    SC-02b accept: a governed write inside <segment>/<repo>/<id> exits 0
ok    SC-02b refuse: a linked worktree OUTSIDE the layout is refused, and the message NAMES where worktrees belong

8/8 deep-layout shape cases passed.

ok    sweep/clean-tracked A: worktree creation reports nothing
ok    sweep/clean-tracked B: a modified file is still caught, exit 2
ok    sweep/clean-tracked C: an untracked file is still caught
      red proof: original reported 0 FEAT-OLD line(s), mutant 2
ok    sweep/clean-tracked RED: removing the skip makes case A red
      red proof: original denials 1, mutant 0 (exit 2 vs 0)
ok    SC-07 write path: the fixture feature is absent from the frozen exempt map
ok    SC-07 write path: a Write whose runs entry omits agent exits 2
ok    SC-07 write path: the denial names the key 'agent'
ok    SC-07 write path: the denial names the offending index
ok    SC-07 write path: the same Write CARRYING agent is permitted
ok    SC-07 write path RED: the positional rule is load-bearing at the hook
ok    1: a governed agent flipping approval.status is DENIED
ok    1: the denial names the approval mapping
ok    1: the denial names the plan-merge route
ok    2: adding a task with approval byte-identical is ALLOWED
ok    3: the orchestrator flipping approval is DENIED too
ok    4: the MAIN SESSION signing is ALLOWED, by the mechanism not a special case
ok    5a: a targeted Edit of the signature is DENIED
ok    5b: the mid-line-start evasion is DENIED
ok    5c: the accidental replace_all sweep is DENIED
ok    5d: an Edit INTRODUCING an approval block at column zero is DENIED
ok    5e: an Edit touching only a task body is ALLOWED
ok    6: a plan.yaml that does not exist yet is ALLOWED
ok    7: an unparseable proposal is ALLOWED
ok    7: and stderr SAYS the parse failed
ok    8: a whitespace-only reflow of the approval block is ALLOWED
ok    9: dropping the entry from main_session.writes STOPS the denial
ok    10a: no main_session key at all -> ALLOWED
ok    10a: and stderr says the exclusion list was unreadable
ok    10b: an empty writes list -> ALLOWED
ok    10b: and stderr says the exclusion list was unreadable
ok    11: a fragment-less entry (.harness/logs/**) contributes NO fragment denial
ok    12: flipping BRIEF.md's ## Approval body is DENIED
ok    12: the denial names the ## Approval heading
ok    12: changing only ## Goal, leaving ## Approval identical, is ALLOWED
ok    13: flipping PLAN.md's ## Approval body is DENIED
ok    14: the real record carries the plan.yaml approval: entry
ok    14: and still carries the BRIEF.md ## Approval entry
ok    14: and still carries the PLAN.md ## Approval entry

28/28 T-14 cases passed.
PASS test-check-domain.py
ok   test_merge_key_override_is_not_a_duplicate
ok   test_missing_pyyaml_is_reportable_not_a_second_crash
ok   test_duplicate_key_is_catchable_as_a_parse_error
ok   test_duplicate_key_raises
ok   test_nested_duplicate_key_raises
ok   test_bare_date_scalar_stays_str
ok   test_int_and_bool_resolvers_are_not_stripped
ok   test_manifest_domains_matches_the_regex_walk_on_the_real_manifest
ok   test_manifest_domains_excludes_non_canonical_read_true
PyYAML is not importable by this python3 interpreter; allowing this session once.
python3 -m pip install pyyaml
# if that fails with "externally-managed-environment" (PEP 668, e.g. Homebrew/Debian):
python3 -m pip install --user --break-system-packages pyyaml
{"systemMessage": "[harness] PyYAML is missing, so the write guards cannot read the domain manifest. This session is granted ONE bootstrap pass and later sessions will be blocked. Install it now:\npython3 -m pip install pyyaml\n# if that fails with \"externally-managed-environment\" (PEP 668, e.g. Homebrew/Debian):\npython3 -m pip install --user --break-system-packages pyyaml"}
PyYAML is not importable, and this session's one-time bootstrap grant was already used by an EARLIER session — failing closed. Install PyYAML to restore normal operation:
python3 -m pip install pyyaml
# if that fails with "externally-managed-environment" (PEP 668, e.g. Homebrew/Debian):
python3 -m pip install --user --break-system-packages pyyaml
PyYAML is not importable and the bootstrap marker at /var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpp1nh6coa/.harness/.pyyaml-bootstrap could not be written ([Errno 13] Permission denied: '/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmpp1nh6coa/.harness/.pyyaml-bootstrap'), so a one-time grant cannot be recorded — failing closed rather than granting one that never expires.
python3 -m pip install pyyaml
# if that fails with "externally-managed-environment" (PEP 668, e.g. Homebrew/Debian):
python3 -m pip install --user --break-system-packages pyyaml
ok   test_bootstrap_marker_lifecycle
ok   test_marker_self_unlinks_when_yaml_imports
ok   test_require_or_die_ignores_the_retired_project_dir_variable
ok   test_require_or_die_survives_a_missing_harness_boundary
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
ok    a new budgets key (orchestrator_context_warn_tokens) propagates from the template at the template's value, 200000

10/10 cases passed.
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
PASS case_19a3_argvless_reports_a_count_at_all
PASS case_19a3b_discovery_finds_the_live_plan_and_skips_the_shipped_one
PASS case_19a3c_the_examined_line_reports_dirs_entered_and_shipped_skipped
PASS case_19a3d_explicit_paths_print_no_examined_line
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
PASS case_20_board_station_py_probes_the_manifest
PASS case_20_gh_sync_py_probes_the_manifest
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
PASS case_25a_status_building_is_CLEAN
PASS case_25b_status_Building_capital_B_is_a_VIOLATION_naming_the_three_legal_values
PASS case_25c_status_in_progress_is_a_VIOLATION
PASS case_25d_no_status_at_all_is_CLEAN
PASS case_25e_status_done_and_status_pending_are_both_CLEAN
PASS case_26a_two_unbuilt_features_claiming_INV-9_is_a_VIOLATION_naming_both
PASS case_26b_distinct_INV_numbers_are_CLEAN
PASS case_26c_a_feature_with_a_BRIEF_and_NO_plan_still_collides
PASS case_26d_two_features_citing_a_LIVE_invariant_is_CLEAN
PASS case_26e_a_SHIPPED_feature_does_not_collide_with_a_live_one
PASS case_26f_a_DECLARATION_beats_a_prose_citation
PASS case_26g_two_features_DECLARING_the_same_number_still_collide

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
ok    (A) config: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (A) decompose: no arguments exits 2
ok    (A) decompose: no arguments never exits 1
ok    (A) decompose: no arguments writes nothing to stdout
ok    (A) decompose: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (A) claim: no arguments exits 2
ok    (A) claim: no arguments never exits 1
ok    (A) claim: no arguments writes nothing to stdout
ok    (A) claim: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (A) workspace: no arguments exits 2
ok    (A) workspace: no arguments never exits 1
ok    (A) workspace: no arguments writes nothing to stdout
ok    (A) workspace: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (A) land: no arguments exits 2
ok    (A) land: no arguments never exits 1
ok    (A) land: no arguments writes nothing to stdout
ok    (A) land: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (B) missing --fleet path: exits 2
ok    (B) missing --fleet path: nothing on stdout
ok    (B) missing --fleet path: stderr names the path
ok    (B): the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
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
ok    (D-config) success: payload carries repos, and no board on either the fleet or any repos entry
ok    (D-config): the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (D-decompose) success: exits 0
ok    (D-decompose) success: stdout is one JSON object
ok    (D-decompose) success: one issue recorded for T-1
ok    (D-decompose): the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (D-claim) success: exits 0
ok    (D-claim) success: stdout is one JSON object
ok    (D-claim) success: payload branch is factory/issue-600
ok    (D-claim) success: board item actually moved to Building
ok    (D-claim): the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (D-workspace) success: exits 0
ok    (D-workspace) success: stdout is one JSON object
ok    (D-workspace) success: payload path is under workspace_root
ok    (D-workspace) success: payload branch is factory/issue-800
ok    (D-workspace): the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (D-land) success: exits 0
ok    (D-land) success: stdout is one JSON object
ok    (D-land) success: payload carries a pull request url
ok    (D-land) success: board item actually moved to Review
ok    (D-land): the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (E) ref refused for every candidate: exits 1
ok    (E) ref refused for every candidate: writes nothing to stdout
ok    (E): the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (F) decompose exits 0
ok    (F) decompose: stdout is one JSON object
ok    (F) decompose: one issue per task
ok    (F) decompose: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (F) decompose: both board items boarded at the fleet's declared ready station
ok    (F) claim exits 0
ok    (F) claim: stdout is one JSON object
ok    (F) claim: claimed the T-1 issue (unblocked candidate)
ok    (F) claim: payload branch is factory/issue-<n>
ok    (F) claim: board item actually moved to Building
ok    (F) claim: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (F) workspace exits 0
ok    (F) workspace: stdout is one JSON object
ok    (F) workspace: payload path is under workspace_root
ok    (F) workspace: payload branch matches claim's branch
ok    (F) workspace: the payload path is an actual directory on disk
ok    (F) workspace: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (F) workspace: recorded git commands include a checkout of factory/issue-<n>
ok    (F) land exits 0
ok    (F) land: stdout is one JSON object
ok    (F) land: opened exactly one pull request
ok    (F) land: board item actually moved to Review
ok    (F) land: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (F) land: recorded git commands include a push of factory/issue-<n> to origin
ok    (G1) -b --track form: workspace exits 0 against real git
ok    (G1) -b --track form: HEAD equals origin's factory/issue-1
ok    (G1) -b --track form: local branch tracks origin/factory/issue-1
ok    (G1): the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (G2) fixture sanity: local factory/issue-2 differs from origin's before the run
ok    (G2) fixture sanity: local factory/issue-2 has no upstream before the run
ok    (G2) -B --track form: workspace exits 0 against real git
ok    (G2) -B --track form: HEAD force-aligned onto origin's factory/issue-2
ok    (G2) -B --track form: local branch now tracks origin/factory/issue-2
ok    (G2): the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (G) live-git smoke check ran against a real git binary (/usr/bin/git, git version 2.50.1 (Apple Git-155))
ok    (H) decompose against the two-board fleet exits 0
ok    (H) decompose: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (H) claim against the two-board fleet exits 0
ok    (H) claim: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (H) land against the two-board fleet exits 0
ok    (H) land: the root override was not silently discarded (no 'discarding HARNESS_PROJECT_DIR')
ok    (H) at least one gh call was recorded (anti-vacuum)
ok    (H) no recorded gh call names the other repository's board number
ok    (H) at least one recorded gh call names the served repository's own board number (proves the check above has power)
ok    (I) project_create: forked process exits 0
ok    (I) project_create: one call resolves the owner id, one call mutates createProjectV2
ok    (I) project_create: the title is sent verbatim as a GraphQL variable
ok    (I) project_link_repository: forked process exits 0
ok    (I) project_link_repository: resolves the repo id then mutates linkProjectV2ToRepository
ok    (I) project_link_repository: repo owner/name split sent verbatim
ok    (I) project_single_select_create: forked process exits 0
ok    (I) project_single_select_create: mutates createProjectV2Field, sends every option's color and description explicitly
ok    (I) project_single_select_extend: forked process exits 0
ok    (I) project_single_select_extend: mutates updateProjectV2Field, never createProjectV2Field, sending every option in the given order
ok    (J) board_lifecycle.py provision: forked process exits 0 against a complete board
ok    (J) board_lifecycle.py provision: reports its own verdict on stdout (anti-vacuum — an __main__ block that forgets to dispatch also exits 0 with an empty log, which would make the exit-0 and zero-mutations checks below pass for the wrong reason)
ok    (J) board_lifecycle.py provision: at least one gh call was actually recorded
ok    (J) board_lifecycle.py provision: performs ZERO mutations against a complete board
ok    (K) board_lifecycle.py audit: forked process exits 1 against a fixture carrying one finding (the EXIT STATUS, not an in-process SystemExit catch)
ok    (K) board_lifecycle.py audit: the finding's text appears on stdout
ok    (L) board_lifecycle.py audit STATUS: forked process exits 1 against a feature.json status disagreeing with its parent card (the EXIT STATUS, not an in-process SystemExit catch)
ok    (L) board_lifecycle.py audit STATUS: the finding names the feature dir, recorded status Done, and the actual column Backlog
ok    (M) board_lifecycle.py reconcile with NO flags: exits 0 (the dry-run default, even though a fixable REASON finding is present)
ok    (M) board_lifecycle.py reconcile with NO flags: the finding is previewed, not silently skipped (anti-vacuum)
ok    (M) board_lifecycle.py reconcile with NO flags: ZERO mutations reached the stub gh -- --apply was never defaulted to
ok    (N) board_lifecycle.py retitle with NO flags: exits 0 (the dry-run default, even though a pending rename is present)
ok    (N) board_lifecycle.py retitle with NO flags: the pending rename is previewed, not silently skipped (anti-vacuum)
ok    (N) board_lifecycle.py retitle with NO flags: ZERO rename calls reached the stub gh -- --apply was never defaulted to
ok    (N) board_lifecycle.py retitle with NO flags: the issue's title on the stub's own state is untouched by the preview

131/131 checks passed.
PASS test-factory-integration.py
PASS  GUARD: path --repo harness --id FEAT-90 resolves inside the fixture directory
PASS  create harness FEAT-90 succeeds
PASS  create harness FEAT-91 succeeds
PASS  create org/repoB FEAT-92 succeeds
PASS  create org/repoB FEAT-93 succeeds
PASS  SC-01 layout: FEAT-90 destination matches dest_for()
PASS  SC-01 layout: FEAT-91 destination matches dest_for()
PASS  SC-01 layout: FEAT-92 destination matches dest_for()
PASS  SC-01 layout: FEAT-93 destination matches dest_for()
PASS  SC-01 conflation guard: FEAT-90 not under workspace_root/.claude/worktrees
PASS  SC-01 conflation guard: FEAT-91 not under workspace_root/.claude/worktrees
PASS  SC-01 conflation guard: FEAT-92 not under workspace_root/.claude/worktrees
PASS  SC-01 conflation guard: FEAT-93 not under workspace_root/.claude/worktrees
PASS  SC-01 conflation guard: FEAT-92 is under workspace_root/repoB/.claude/worktrees/repoB
PASS  SC-01 conflation guard: FEAT-93 is under workspace_root/repoB/.claude/worktrees/repoB
PASS  SC-01 isolation: FEAT-90 sees its own marker file
PASS  SC-01 isolation: FEAT-90 does not see FEAT-91's marker file
PASS  SC-01 isolation: FEAT-90 does not see FEAT-92's marker file
PASS  SC-01 isolation: FEAT-90 does not see FEAT-93's marker file
PASS  SC-01 isolation: FEAT-91 sees its own marker file
PASS  SC-01 isolation: FEAT-91 does not see FEAT-90's marker file
PASS  SC-01 isolation: FEAT-91 does not see FEAT-92's marker file
PASS  SC-01 isolation: FEAT-91 does not see FEAT-93's marker file
PASS  SC-01 isolation: FEAT-92 sees its own marker file
PASS  SC-01 isolation: FEAT-92 does not see FEAT-90's marker file
PASS  SC-01 isolation: FEAT-92 does not see FEAT-91's marker file
PASS  SC-01 isolation: FEAT-92 does not see FEAT-93's marker file
PASS  SC-01 isolation: FEAT-93 sees its own marker file
PASS  SC-01 isolation: FEAT-93 does not see FEAT-90's marker file
PASS  SC-01 isolation: FEAT-93 does not see FEAT-91's marker file
PASS  SC-01 isolation: FEAT-93 does not see FEAT-92's marker file
PASS  SC-01 branch isolation: FEAT-90 HEAD names feat/FEAT-90
PASS  SC-01 branch isolation: FEAT-91 HEAD names feat/FEAT-91
PASS  SC-01 branch isolation: FEAT-92 HEAD names feat/FEAT-92
PASS  SC-01 branch isolation: FEAT-93 HEAD names feat/FEAT-93
PASS  SC-01 branch isolation: FEAT-90 branch differs from FEAT-91
PASS  SC-01 branch isolation: FEAT-90 branch differs from FEAT-92
PASS  SC-01 branch isolation: FEAT-90 branch differs from FEAT-93
PASS  SC-01 branch isolation: FEAT-91 branch differs from FEAT-92
PASS  SC-01 branch isolation: FEAT-91 branch differs from FEAT-93
PASS  SC-01 branch isolation: FEAT-92 branch differs from FEAT-93
PASS  SC-02 cut point: FEAT-90 merge-base with main equals its pre-create tip
PASS  SC-02 cut point: FEAT-91 merge-base with main equals its pre-create tip
PASS  SC-02 cut point: FEAT-92 merge-base with master equals its pre-create tip
PASS  SC-02 cut point: FEAT-93 merge-base with master equals its pre-create tip
PASS  SC-01b case A: all four concurrent committers succeed against their own worktree
PASS  SC-01b case A: all six pairwise write windows genuinely overlapped under contention
PASS  SC-01b case A: assert_commit_isolation holds across four concurrently-committed worktrees
PASS  SC-01b case A: no branch outside the four expected ones advanced (repoA main, repoB master unchanged)
PASS  SC-01b case A: FEAT-90 working directory is clean after concurrent commits (scoped to this case's own files)
PASS  SC-01b case A: FEAT-90 HEAD still names its own branch after concurrent commits
PASS  SC-01b case A: FEAT-91 working directory is clean after concurrent commits (scoped to this case's own files)
PASS  SC-01b case A: FEAT-91 HEAD still names its own branch after concurrent commits
PASS  SC-01b case A: FEAT-92 working directory is clean after concurrent commits (scoped to this case's own files)
PASS  SC-01b case A: FEAT-92 HEAD still names its own branch after concurrent commits
PASS  SC-01b case A: FEAT-93 working directory is clean after concurrent commits (scoped to this case's own files)
PASS  SC-01b case A: FEAT-93 HEAD still names its own branch after concurrent commits
PASS  SC-01b case B: the successful committers' write windows genuinely overlapped
PASS  SC-01b case B: the shared-checkout collision was detected (IsolationViolation raised, or a committer failure recorded)
PASS  REQ-07: workspace_root/repoB still exists
PASS  REQ-07: workspace_root/repoB still holds its .git directory
PASS  REQ-07: workspace_root/repoB still reports master as its own current branch
PASS  create refuses an existing destination: second create for repoA FEAT-90 exits 3
PASS  create refuses an existing destination: the first tree is untouched
PASS  list: repoA exits 0
PASS  list: repoA prints exactly two lines
PASS  list: FEAT-90 branch and path fields match the created worktree
PASS  list: FEAT-91 branch and path fields match the created worktree
PASS  undeclared --repo org/nope exits 2
PASS  undeclared --repo org/nope names fleet.yaml on stderr
PASS  SC-07 refuse (untracked): remove exits 4
PASS  SC-07 refuse (untracked): stdout names WOULD DISCARD untracked.txt
PASS  SC-07 refuse (untracked): the tree and the untracked file still exist on disk
PASS  SC-07 refuse (tracked): remove exits 4 on an otherwise fully landed tree
PASS  SC-07 refuse (tracked): stdout names WOULD DISCARD .harness/team-config.yaml
PASS  SC-04 refuse: remove exits 5 when the artifact is unmerged
PASS  SC-04 refuse: stdout names MISSING .harness/harness/features/FEAT-96/BRIEF.md
PASS  SC-04 refuse: the tree still exists on disk
PASS  SC-04 allow: remove exits 0 once the artifact is landed
PASS  SC-04 allow: stdout names VERIFIED .harness/harness/features/FEAT-96/BRIEF.md
PASS  SC-04 allow: the final line begins REMOVED
PASS  SC-04 allow: the destination directory no longer exists
PASS  SC-04 differs: remove exits 5 when worktree and default-branch blobs differ
PASS  SC-04 differs: stdout names DIFFERS .harness/harness/features/FEAT-97/BRIEF.md
PASS  SC-04 differs: the tree still exists on disk
PASS  no artifact directory at all: remove exits 5
PASS  no artifact directory at all: stdout names the directory .harness/harness/features/FEAT-98
PASS  no artifact directory at all: the tree still exists on disk
PASS  #726 fixture: the ignored run file leaves the tree CLEAN
PASS  #726: an IGNORED artifact does not block remove
PASS  #726: stdout never names the ignored path as MISSING
PASS  #726: the tracked artifact is still VERIFIED, so the check did not go blind
PASS  #726: the worktree is gone
PASS  #726 guard: an UNLANDED TRACKED artifact still refuses, exit 5
PASS  #726 guard: stdout names MISSING .harness/harness/features/FEAT-71/BRIEF.md
PASS  #726 guard: the tree survives the refusal
PASS  #727: a SHORT --id resolves to the one matching feature directory
PASS  #727: the resolved artifact is verified — .harness/harness/features/FEAT-72-a-slugged-name/BRIEF.md
PASS  #727: the worktree is gone
PASS  #727 guard: an AMBIGUOUS short id refuses, exit 5
PASS  #727 guard: the refusal names BOTH candidates so the operator can disambiguate
PASS  #727 guard: the tree survives the refusal
PASS  behind: a freshly cut worktree is current, exit 0
PASS  behind: two commits behind main exits 6
PASS  behind: the refusal names the count, not just that it is behind
PASS  behind: the refusal lists each missing commit's subject
PASS  behind: the refusal names the merge command that fixes it
PASS  behind: the refusal states it compared against LOCAL main
PASS  behind: after the printed merge command, it is current again, exit 0
PASS  behind: an absent worktree exits 3, never 6
PASS  behind RED: original refuses (rc=6) where the mutant passes (rc=0), so CASE B discriminates
PASS test-feature-worktree.py
PASS test-feature-worktree.py
PASS  case1: naive last-writer-wins loses P-02
PASS  case1: naive last-writer-wins loses P-03
PASS  case2: apply A exits 0
PASS  case2: apply B exits 0
PASS  case2: P-01 present after both applies
PASS  case2: P-02 present after both applies
PASS  case2: P-03 present after both applies
PASS  case2: P-04 present after both applies
PASS  case2: check-expertise.sh still accepts the merged file
PASS  case3: 20 concurrent trials admit only the union outcome or the lock outcome
PASS  case4: divergent text exits 7
PASS  case4: existing text appears in stdout
PASS  case4: proposed text appears in stdout
PASS  case4: file is byte identical to before
PASS  case4: a following apply still exits 0
PASS  case5: cap overflow exits 8
PASS  case5: stdout names the section
PASS  case5: stdout names the cap
PASS  case5: file is byte identical to before
PASS  case5: a following apply still exits 0
PASS  case6: target file absent before apply
PASS  case6: exits 0
PASS  case6: file created
PASS  case6: proposed entry present
PASS  case6: a following apply still exits 0
PASS  case9: a non-Expertise --file is REFUSED with exit 9
PASS  case9: ...and the refused file is UNTOUCHED
PASS  case9: a `..` escape carrying a legal tail is REFUSED — the match is on the realpath, not the argument
PASS  case9: the project tier is ALLOWED — exit 0
PASS  case9: the repository tier is ALLOWED — exit 0
PASS  case8: CAPS mapping found in expertise-merge.py
PASS  case8: CAPS mapping found in check-expertise.sh
PASS  case8: Patterns cap agrees between expertise-merge.py and check-expertise.sh
PASS  case8: Gotchas cap agrees between expertise-merge.py and check-expertise.sh
PASS  case8: Outcomes cap agrees between expertise-merge.py and check-expertise.sh
PASS  case8: Open cap agrees between expertise-merge.py and check-expertise.sh
PASS  case10: a following apply exits 0 after the lock holder is SIGKILLed
PASS  case10: the proposed entry is on disk after recovery
PASS test-expertise-merge.py
PASS test-expertise-merge.py
ok    CASE 1 pre-check: naive peak and corrected peak differ on this fixture
ok    CASE 1: CLI exits 0 on a fully-measured, non-warning fixture
ok    CASE 1: the CLI's row carries current=/peak=/entries= fields
ok    CASE 1: CLI peak equals the independent recomputation, to the token
ok    CASE 1: CLI current equals the independent recomputation, to the token
ok    CASE 1: CLI entries equals the independent recomputation, to the token
ok    CASE 2: --resolve-dir prints the exact worktree slug
ok    CASE 2 setup: the mutant target text is found verbatim in the real script
ok    CASE 2 red proof: the mutation actually applied (mutant text differs from original)
ok    CASE 2 red proof: the mutant's output differs from the expected literal
10 of 10 cases passed
PASS test-context-watch-cli.py
     red proof: original warning lines 1, mutant 0 (exit 2 vs 0)
ok    case 1: a crossing orchestrator gets exit 2
ok    case 1: stderr carries the warning
ok    case 1: the text names the CURRENT figure
ok    case 1: the text names the THRESHOLD figure
ok    case 1: the text names the remedy (handoff)
ok    case 1: stderr OPENS with the reassurance, on the real stderr channel
ok    case 1: the reassurance precedes the CURRENT figure on stderr
ok    case 1: stdout stays EMPTY, so the channel really is stderr
ok    case 1: the text claims nothing was blocked, stopped or refused
ok    case 2: below the threshold exits 0
ok    case 2: below the threshold says NOTHING on stderr
ok    case 3: a non-orchestrator crossing the threshold exits 0
ok    case 3: and says nothing
ok    case 4 RED: the threshold comparison is load-bearing
ok    case 5: a payload that is not JSON exits 0
ok    case 5: a payload that is not JSON prints no traceback
ok    case 5: an empty payload exits 0
ok    case 5: an empty payload prints no traceback
ok    case 5: a payload missing agent_id exits 0
ok    case 5: a payload missing agent_id prints no traceback
ok    case 5: a payload that is a JSON list, not an object exits 0
ok    case 5: a payload that is a JSON list, not an object prints no traceback
22 of 22 cases passed
PASS test-context-watch-hook.py
ok    case 1: --check-kinds on the real tree exits 0
ok    case 1: and reports EXACTLY zero KIND-DRIFT lines
ok    case 1: --check-kinds ran no test
ok    case 2: the mutation changed the detect string
ok    case 2: the removed path is present in the ORIGINAL
ok    case 2: and absent from the MUTANT
ok    case 2: a KIND-DRIFT line NAMES test-check-state.py
ok    case 2: exactly one KIND-DRIFT line, strictly more than case 1's baseline
ok    case 2: the message says INTEGRATION_SCRIPTS, the direction of this drift
ok    case 3: the mutation changed the detect string
ok    case 3: the appended path was absent from the ORIGINAL
ok    case 3: and is present in the MUTANT
ok    case 3: a KIND-DRIFT line NAMES test-render-brief.py
ok    case 3: the message says UNIT_SCRIPTS, the opposite direction
ok    case 4: a missing config produces a KIND-DRIFT line naming the path
ok    case 4: and a non-zero exit
ok    case 4: an unparseable config produces a KIND-DRIFT line naming the path
ok    case 4: and a non-zero exit
ok    case 5: --kind nonsense still exits 2
ok    case 5: and the message names the legal kinds
ok    case 5: an unknown flag still exits 2 with the usage line
ok    case 5: the usage line advertises --check-kinds
ok    case 5: --check-kinds runs no test, so no PASS or FAIL line appears
23 of 23 cases passed
PASS test-run-unit-tests-kinds.py
PASS - case1: transform receives None for missing file
PASS - case1: file created with transform output
PASS - case2: transform receives original bytes
PASS - case2: result is exactly transform's bytes
PASS - case3: MergeRefusal propagated
PASS - case3: file byte-identical to before
PASS - case3: no tempfile left behind
PASS - case4: locked_update returned normally after stale lock killed
PASS - case4: transform output is on disk
PASS - case5: contention admits only the two legal outcomes over 20 trials
PASS - case6: no torn read observed by concurrent reader
PASS - case6: reader observed at least one read
PASS - case6: reader observed both the short and long body while racing the writer
PASS - case7: matching resolved path is accepted
PASS - case7: non-matching path raises MergeRefusal(9)
PASS - case7: symlink escape (literal ends in matching tail via symlinked 'mydir', realpath resolves outside and does not match) raises MergeRefusal(9)
PASS - case8: acquire raises MergeRefusal(6) against a live holder
PASS - case8: refusal lines name the lock path
PASS - 18/18 checks passed
PASS test-harness-merge.py
PASS  case1: naive whole-file write loses T-02
PASS  case1: naive whole-file write loses T-03
PASS  case1: naive whole-file write loses T-04
PASS  case1: naive whole-file write loses T-05
PASS  case1: naive whole-file write loses T-06
PASS  case1: naive whole-file write loses T-07
PASS  case1: naive whole-file write loses T-08
PASS  case1: naive whole-file write loses T-09
PASS  case1: naive whole-file write loses T-10
PASS  case1: naive whole-file write loses T-11
PASS  case1: naive whole-file write loses T-12
PASS  case1: naive whole-file write loses T-13
PASS  case1: naive whole-file write loses T-14
PASS  case2: first apply exits 0
PASS  case2: T-01 present after first apply
PASS  case2: T-02 present after first apply
PASS  case2: T-03 present after first apply
PASS  case2: T-04 present after first apply
PASS  case2: T-05 present after first apply
PASS  case2: T-06 present after first apply
PASS  case2: T-07 present after first apply
PASS  case2: T-08 present after first apply
PASS  case2: T-09 present after first apply
PASS  case2: T-10 present after first apply
PASS  case2: T-11 present after first apply
PASS  case2: T-12 present after first apply
PASS  case2: T-13 present after first apply
PASS  case2: T-14 present after first apply
PASS  case2: second apply exits 0
PASS  case2: T-01 present after second apply
PASS  case2: T-02 present after second apply
PASS  case2: T-03 present after second apply
PASS  case2: T-04 present after second apply
PASS  case2: T-05 present after second apply
PASS  case2: T-06 present after second apply
PASS  case2: T-07 present after second apply
PASS  case2: T-08 present after second apply
PASS  case2: T-09 present after second apply
PASS  case2: T-10 present after second apply
PASS  case2: T-11 present after second apply
PASS  case2: T-12 present after second apply
PASS  case2: T-13 present after second apply
PASS  case2: T-14 present after second apply
PASS  case2: T-15 present after second apply
PASS  case3: exit 0
PASS  case3: the exact byte slice of the base's approval block occurs verbatim in the result
PASS  case3: number of hash-comment lines in the whole file is unchanged
PASS  case3: stdout carries IGNORED-APPROVAL
PASS  case4: 20 concurrent trials admit only the union outcome or the lock outcome
PASS  case4: informational — the exit-6 lock branch was taken in 0/20 trials
PASS  case5: conflict exits 7
PASS  case5: stdout names the id
PASS  case5: stdout carries both values
PASS  case5: file is byte identical to before
PASS  case5: no stray tempfile left behind after the refusal
PASS  case6: first apply exits 0
PASS  case6: second apply exits 0
PASS  case6: file is byte identical after the second, idempotent apply
PASS  case7: a source path is REFUSED with exit 9
PASS  case7: ...and the refused file is untouched
PASS  case7: the escape's literal argument ends in the matching tail
PASS  case7: a symlink escape whose LITERAL argument matches but RESOLVES elsewhere is REFUSED with exit 9
PASS  case7: ...and the file behind the symlink is untouched
PASS  case7: a legitimate fixture plan.yaml is ALLOWED — exit 0
PASS  case8: unparseable proposal exits 5
PASS  case8: stdout/stderr names the proposal side
PASS  case8: base file is byte identical to before
PASS  case9: the template's leading block is all comment lines
PASS  case9: exit 0
PASS  case9: template comment line 1 survives byte identical
PASS  case9: template comment line 2 survives byte identical
PASS  case9: template comment line 3 survives byte identical
PASS  case9: template comment line 4 survives byte identical
PASS  case9: template comment line 5 survives byte identical
PASS  case9: template comment line 6 survives byte identical
PASS  case9: template comment line 7 survives byte identical
PASS  case9: template comment line 8 survives byte identical
PASS  case9: template comment line 9 survives byte identical
PASS  case9: template comment line 10 survives byte identical
PASS  case9: template comment line 11 survives byte identical
PASS  case9: template comment line 12 survives byte identical
PASS  case9: template comment line 13 survives byte identical
PASS  case9: template comment line 14 survives byte identical
PASS  case9: template comment line 15 survives byte identical
PASS  case9: template comment line 16 survives byte identical
PASS  case9: template comment line 17 survives byte identical
PASS  case9: template comment line 18 survives byte identical
PASS  case9: template comment line 19 survives byte identical
PASS  case9: T-15 was added
PASS  case10a: differing approval exits 8
PASS  case10a: stdout/stderr names the approval mapping and both loaded values
PASS  case10a: file is byte identical to before (nothing applied)
PASS  case10a: T-15 is absent, asserted by id
PASS  case10b: proposal with no approval key exits 0
PASS  case10b: T-15 is present
PASS  case10c: loaded-equal-but-reflowed approval exits 0
PASS  case10c: T-15 is present
PASS  case11a: base file does not exist before apply
PASS  case11a: create with no approval key exits 0
PASS  case11a: the file now exists
PASS  case11a: T-01 present in the created file
PASS  case11a: T-02 present in the created file
PASS  case11a: T-03 present in the created file
PASS  case11b: base file does not exist before apply
PASS  case11b: create with an approval key exits 8
PASS  case11b: no file was created by the refused apply
PASS  case11b: stdout/stderr names the approval mapping
PASS  case11b: stdout/stderr names the main session as the signer
PASS  case11b: no stray tempfile/plan.yaml left behind after the refusal
PASS test-plan-merge.py
PASS test-plan-merge.py
PASS  case1: naive whole-file write loses bullet B
PASS  case2: apply exits 0
PASS  case2: bullet A present
PASS  case2: bullet B present
PASS  case2: bullet C present
PASS  case2: A appears before B, and both remain in base order
PASS  case3: apply exits 0
PASS  case3: exactly one copy of the byte-identical record
PASS  case4: apply exits 0
PASS  case4: normalised-identical record (wrapping/trailing-space) not duplicated
PASS  case4b: apply exits 0
PASS  case4b: record differing only in trailing blank-line count dedups as one copy
PASS  case5: two different records both kept, exit 0 (no conflict exit exists)
PASS  case5: bullet A present
PASS  case5: bullet B present
PASS  case6: apply exits 0
PASS  case6: the exact multi-line record text survives
PASS  case7: 20 concurrent trials admit only the union outcome or the lock outcome
PASS  case7: informational — the exit-6 lock branch was taken in 0/20 trials
PASS  case8: base file does not exist before apply
PASS  case8: create exits 0
PASS  case8: the file now exists
PASS  case8: bullet A present
PASS  case8: a generated title line beginning with a hash is present
PASS  case9: a source path is REFUSED with exit 9
PASS  case9: ...and the refused file is untouched
PASS  case9: the escape's literal argument ends in the full legal-looking tail
PASS  case9: a symlink escape whose LITERAL argument looks legal but RESOLVES elsewhere is REFUSED with exit 9
PASS  case9: ...and the file behind the symlink is untouched
PASS  case9: an Expertise file path is REFUSED with exit 9 — it belongs to a different tool
PASS  case9: ...and the Expertise file is untouched
PASS  case9: a legitimate observations path is ALLOWED — exit 0
PASS test-observations-merge.py
PASS test-observations-merge.py
PASS - case1: claim returns True
PASS - case1: live_claim returns a claim
PASS - case1: recorded dispatcher matches
PASS - case1: recorded cwd matches
PASS - case2: first pm claim succeeds
PASS - case2: second pm claim is refused (single-flight)
PASS - case2: stored started_at is still the FIRST claim's
PASS - case2: first backend-dev claim succeeds
PASS - case2: second backend-dev claim ALSO succeeds (parallel squad is legal)
PASS - case2: registry holds two claims for backend-dev
PASS - case2: both started_at values are present
PASS - case2b: eng-lead children include backend-dev
PASS - case2b: eng-lead children include frontend-dev
PASS - case2b: eng-lead children exclude pm
PASS - case2b: eng-lead children exclude qa
PASS - case2b: product-lead children include pm
PASS - case2b: product-lead children include qa
PASS - case2b: product-lead children exclude backend-dev
PASS - case2b: product-lead children exclude frontend-dev
PASS - case2c: stale child is not returned
PASS - case2c: stale claim is gone from the file afterwards
PASS - case3: stale claim is treated as absent
PASS - case3: live_claim reports one expired
PASS - case3: a following claim succeeds after staleness expiry
PASS - case4: release removes the SOLE claim and returns True
PASS - case4: no live claim remains
PASS - case4: releasing an absent claim returns False
PASS - case4: releasing an absent claim does not create the file
PASS - case5: harness-pm is single-flight
PASS - case5: harness-backend-dev is not single-flight
PASS - case6: first line begins with the dispatch-guard marker
PASS - case6: the agent name appears
PASS - case6: an ISO-8601 timestamp appears
PASS - case6: #628 is referenced (issue #551 moved here, item 6)
PASS - case6: the original #551 single-flight report is still noted
PASS - case6: the plan.yaml-overwrite sentence is NOT tagged #551 (it is #628's issue now)
PASS - case6: the release command appears byte-for-byte
PASS - case6b: first line begins with the check-digest marker
PASS - case6b: the returning agent is named
PASS - case6b: the first child is named
PASS - case6b: the second child is named
PASS - case6b: two ISO-8601 timestamps appear
PASS - case6b: #551 is referenced
PASS - case6b: the message prescribes ending the turn again
PASS - case7: 20 trials each produce exactly one successful claim() and one stored claim
PASS - case7: informational — a LOCKED-style split-decision outcome was admitted 0/20 times
PASS - case8: claim against a corrupt registry does not raise
PASS - case8: claim succeeds, treating the corrupt file as empty
PASS - case8: a message naming the file appears on stderr
PASS - case9: release_all returns 3
PASS - case9: the registry is empty afterwards
PASS - case9: CLI list exits 0
PASS - case9: CLI list prints NO CLAIMS
PASS - case10: no fcntl usage
PASS - case10: no O_EXCL usage
PASS - case10: no os.replace usage
PASS - case10: calls harness_merge.locked_update
PASS - case11: ttl_shorter_than_cycle - CLAIM_TTL_SECONDS is one cycle (1200s), not the old 3600s
PASS - case12: claim() accepts a session= keyword
PASS - case12: foreign_session_expired - a claim from a DIFFERENT session reads as absent though fresh
PASS - case12: foreign_session_expired - a session mismatch is not counted as TTL expiry
PASS - case12: foreign_session_expired - the entry remains on disk for its OWN session to find
PASS - case12: the SAME session still finds its own live claim
PASS - case13: release_refuses_ambiguous - two live claims are refused, not oldest-popped, and 0 is returned
PASS - case13: release_refuses_ambiguous - both claims remain on disk untouched
PASS - case13: release_refuses_ambiguous - stderr says how many were left
PASS - case14: remedy_is_absolute - release_cmd(root, agent) exists
PASS - case14: remedy_is_absolute - the remedy is rooted at the checkout, not a relative CLI path
PASS - case14: remedy_is_absolute - a featureless remedy cannot be composed at all
PASS - case14: remedy_is_absolute - the remedy names ONE agent, never release-all
PASS - case15: pm claims for different features run together
PASS - case15: a second pm for the same feature is refused
PASS - case16: an old OMP claim stays live while its supervisor lives
PASS - case16: the live OMP claim is not counted expired
PASS - case16: an OMP claim is stale immediately when its supervisor dies
PASS - case16: the dead-supervisor claim is counted expired
PASS - case17: targeted feature release removes one claim
PASS - case17: targeted feature release leaves the other feature live
PASS - case18: legacy claim remains readable during cutover
PASS - case18: every subsequent write uses schema version 2
PASS - case18: schema version 2 stores one claims list
PASS - case18: legacy persona keys are not written back
PASS - case19: OMP identity attaches to the pending claim
PASS - case19: terminal OMP identity releases only its claim
PASS - case19: released OMP claim is gone
PASS - case20: targeted recovery removes one dead-supervisor claim
PASS - case20: targeted recovery leaves another feature untouched
PASS - case21: queried dead claim expires
PASS - case21: unrelated dead feature is left for targeted reconciliation
PASS - case22: the claim pins the supervisor start time
PASS - case22: a live pid with a foreign start time is expired, not trusted
PASS - case22: reconcile also clears it, so recovery does not need the operator
PASS - case23: a verified supervisor keeps its claim at any age
PASS - case24: an unverifiable claim is still live inside the backstop
PASS - case24: past the backstop it expires even though the pid is alive
PASS - case25: a genuinely live child DOES hold its parent
PASS - case25: a stranded child no longer holds its parent
PASS - case26: the ps read is the only subprocess in the module
PASS - case26: the ps child is pinned to the C locale
PASS - case26: our own start time still reads under a non-English LC_TIME
PASS - case27: NaN survives json.loads, so the corruption guard misses it
PASS - case27: a NaN start time is read without raising
PASS - case27: and past the backstop it clears, so NaN cannot strand
PASS - case27: Infinity survives json.loads, so the corruption guard misses it
PASS - case27: a Infinity start time is read without raising
PASS - case27: and past the backstop it clears, so Infinity cannot strand
PASS - case27: -Infinity survives json.loads, so the corruption guard misses it
PASS - case27: a -Infinity start time is read without raising
PASS - case27: and past the backstop it clears, so -Infinity cannot strand
PASS - case28: a featureless claim still composes a remedy
PASS - case28: and the selector it prints actually matches that claim
PASS - 111/111 checks passed
PASS test-inflight-registry.py
PASS  case 1: a governed agent passing a model exits 2
PASS  case 1: stderr carries the BLOCKED marker
PASS  case 1: stderr names the model value that was passed
PASS  case 1: stderr names the agent that passed it
PASS  case 2: a governed agent with no model exits 0
PASS  case 2: and says nothing
PASS  case 3: a non-harness agent_type exits 0 even with a model
PASS  case 3: and says nothing
PASS  case 4: an unreadable payload exits 0
PASS  case 4: and says so on stderr
PASS  case 5: the main session is never governed
PASS  case 5: and says nothing
PASS  case 6: a second single-flight dispatch exits 2
PASS  case 6: stderr names the single-flight refusal
PASS  case 6: stderr carries the RECORDED started_at, so the claim was really read
PASS  case 6: stderr names the RECORDED dispatcher
PASS  case 6: stderr carries the SINGLE-AGENT release command, never release-all
PASS  case 6: it cites the issue so the reader can find out why
PASS  case 7: the FIRST single-flight dispatch is allowed
PASS  case 7: exactly one harness-pm claim was recorded
PASS  case 7: the claim names the DISPATCHER from agent_type
PASS  case 8: two parallel non-single-flight dispatches BOTH exit 0
PASS  case 8: BOTH claims are on disk
PASS  case 8: each claim names the dispatcher from agent_type
PASS  case 9: a claim past its TTL does NOT refuse the dispatch
PASS  case 9: and stderr SAYS it expired, so the leak is visible
PASS  case 10: the refusal payload is ALLOWED when the library is gone
PASS  case 10: and stderr NAMES the module, so the gap is not silent
PASS  case 11 missing_feature_line_refused: a governed dispatch with no HARNESS-FEATURE line exits 2
PASS  case 11 missing_feature_line_refused: stderr NAMES the missing field
PASS  case 12 claim_lands_in_declared_worktree: the dispatch is allowed
PASS  case 12 claim_lands_in_declared_worktree: the claim lands in the DECLARED worktree
PASS  case 12 claim_lands_in_declared_worktree: and the main checkout registry is untouched
PASS  case 13: a later HARNESS-FEATURE line is refused
PASS  case 13: a malformed flow id is refused
PASS  case 14: different features may each hold a pm claim
PASS  case 14: a duplicate pm for one feature is refused
PASS  case 15: OMP governed dispatch is allowed
PASS  case 15: claim records OMP runtime and supervising pid
PASS  case 15: stdout returns a machine-readable claim receipt
PASS  case 16: macOS system Python can run the dispatch guard
PASS  case 16: system-Python path still returns a claim receipt
42 of 42 cases passed
PASS test-dispatch-guard.py
PASS preserves_existing_content
PASS check_complete_is_read_only
PASS check_incomplete_reports_missing_and_is_read_only
PASS absent_target_receives_each_rule_once
PASS partial_target_retains_present_rule_and_adds_missing_once
PASS second_merge_is_byte_identical
PASS explicit_project_root_ignores_caller_cwd
7 passed; 0 failed
PASS test-merge-gitignore.py
PASS: (a) landed Done, exact name -> terminal
PASS: (b) landed Review -> omitted from the returned list
PASS: (d) never landed -> exempt_absent
PASS: (e) short-named prefix of one landed Done dir -> terminal, NOT exempt_absent
PASS: (f) landed feature.json unparseable -> unresolved
PASS: ambiguous prefix (matches 2 landed dirs) -> unresolved, never exempt_absent
PASS: (h) uncommitted change in a Done worktree -> terminal with dirty True
PASS: every returned record carries exactly the six documented keys, klass is always one of CLASSES
PASS: records are sorted by path
PASS: root itself is never a returned record
PASS: (c) landed Review, working copy Done -> NOT terminal (omitted)
PASS: (c) inverse: landed Done, working copy Review -> terminal regardless
PASS: (c) red proof, forward: working-tree-reading stub wrongly says terminal for a landed-Review worktree
PASS: (c) red proof, inverse: working-tree-reading stub wrongly says omitted for a landed-Done worktree
PASS: (a) red-proof stub PASSES: exact-match Done -> terminal
PASS: (d) red-proof stub PASSES: truly absent -> exempt_absent
PASS: (e) red-proof stub FAILS: short-named prefix wrongly folded into exempt_absent instead of terminal
PASS: (f) red-proof stub FAILS: unparseable landed JSON wrongly folded into exempt_absent instead of unresolved
PASS: (g) real second git repo, fleet-resolved default branch, real worktree add, landed Done -> terminal
PASS: (i) classify_all(probe_root) includes the harness half's own terminal record
PASS: (i) classify_all(probe_root) includes the second repository's terminal record
PASS: (i) RED PROOF: classify(probe_root) alone (classify_all==classify) never returns a record for the second repository's worktree
PASS: (j) real second repository's terminal record is unaffected by an absent declared repo alongside it
PASS: (j) absent checkout: no record for the never-created directory, and classify_all does not raise
PASS: (k) present-but-unenumerable: exactly one repository-level record, klass unresolved
PASS: (k) present-but-unenumerable: record path equals the declared directory
PASS: (j)/(k) RED PROOF: a stub skipping every non-enumerable declared repo passes (j) but fails (k) — emits no record at all for unenum-repo
PASS: (j)/(k) RED PROOF: a stub reporting every non-enumerable declared repo passes (k) but fails (j) — wrongly emits a record for absent-repo too
PASS: (l) fleet.yaml unloadable: classify_all returns an unresolved record whose path is the fleet path
PASS: (l) fleet.yaml unloadable: classify_all still returns the harness root's own records
PASS: (l) RED PROOF: a stub that swallows the fleet-load exception (catches it, returns only the harness half's own records) never emits a fleet-path record, while the real classify_all against the SAME unloadable fleet.yaml does
PASS: (m) classify(<linked worktree as root>) never returns a record for the main checkout
PASS: (m) the linked worktree passed as root IS itself classified (landed Done -> terminal), not silently skipped
PASS: (n) repository with no linked worktrees yields no records and does not raise
PASS test-worktree-terminal.py
PASS: --dry-run exits 0
PASS: --dry-run SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: --dry-run leaves the terminal worktree standing
PASS: --dry-run mentions the feature id in its output
PASS: --dry-run makes no `gh` invocation
PASS: (a) fast-forward merge succeeds
PASS: (a) MEASURED: fast-forward fires post-merge with hook arg 0
PASS: (a) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (a) the Done feature's worktree is gone after the merge
PASS: (b) squash merge succeeds
PASS: (b) MEASURED: squash fires post-merge with hook arg 1
PASS: (b) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (b) the Done feature's worktree is gone after the merge
PASS: (c) sweep run from inside its own eligible worktree exits 0
PASS: (c) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (c) SELF-EXCLUSION: that worktree is still standing afterwards
PASS: (c) SELF-EXCLUSION: stdout states the sweep declined because it is running inside the worktree
PASS: (c) RED PROOF: with the self-exclusion guard removed, an unguarded sweep DELETES the worktree it is running inside — demonstrating the guard was load-bearing
PASS: (d) sweep over two terminal features exits 0
PASS: (d) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (d) SC-11: milestone close call logged for FEAT-30-two-a's OWN milestone (801), checked on its own
PASS: (d) SC-11: milestone close call logged for FEAT-31-two-b's OWN milestone (802), checked separately from FEAT-30's
PASS: (d) both worktrees removed after their own record succeeded
PASS: (e) sweep exits 0 even though the `gh` write for one feature failed
PASS: (e) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (e) D-04 ORDER: the feature whose write failed keeps its worktree standing — removal never runs ahead of a confirmed record
PASS: (e) D-04 ORDER: the OTHER feature, whose write succeeded, has its worktree removed
PASS: (f) sweep exits 0 on an unresolved record
PASS: (f) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (f) the unresolved record is printed
PASS: (f) the unresolved record's worktree is left standing
PASS: (g) sweep exits 0 even though ship SKIPped
PASS: (g) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (g) SKIP IS NOT SUCCESS: a feature whose ship exited 0 but printed `gh-sync: SKIP` keeps its worktree standing
PASS: (g) no milestone-close call was ever made for this feature (ship SKIPped before reaching gh() for the write)
PASS: (g) RED PROOF: gated on exit code alone, the sweep DELETES a worktree whose ship only SKIPped — the destructive fail-open D-04's comment warns about
PASS: (g2) sweep exits 0 even though ship reported FAILED
PASS: (g2) FAILED IS NOT SUCCESS: a ship that exited 0 but printed `gh-sync: FAILED` keeps its worktree standing
PASS: (g2) the declined removal PRINTS a reason naming FAILED, rather than silently leaving the tree
PASS: (g2) HELD IS STILL SUCCESS: a ship that only held cards has its worktree removed as usual
PASS: (g2) RED PROOF: with only the SKIP half of the gate, the sweep DELETES the worktree of a ship that reported FAILED
PASS: (h) fixture precondition: outside_cwd is not inside any git repository
PASS: (h) sweep exits 0 when invoked with cwd outside any git repository
PASS: (h) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (h) MEASURED DEFECT PROOF: the sweep still finds and sweeps the repository's terminal worktree despite cwd being OUTSIDE it
PASS: (h) the milestone close call reached gh for this feature's own milestone (999), proving the record-then-remove flow actually ran
PASS: (i) sweep exits 0 when invoked from inside a linked worktree
PASS: (i) BIN_DIR-derived root resolves to the LINKED WORKTREE it actually runs from, not the main checkout
PASS: (i) RESOLVED-PATH PROOF: the main-checkout root used for feat_dir is R, the ACTUAL main checkout — never WT_CALLER, the linked worktree the script happens to run from
PASS: (i) the milestone close call reached gh for R's LANDED milestone (810)
PASS: (i) DIVERGENCE PROOF: WT_CALLER's own divergent milestone (811) was NEVER closed — the sweep did not write into the wrong copy
PASS: (i) the terminal worktree under R was removed, proving feat_dir was found and ship succeeded against the correct main-checkout copy
EXIT=0
PASS test-post-merge-sweep.py
PASS: commands verbatim: step 1's command string is present in SKILL.md
PASS: commands verbatim: step 2's set command is present in SKILL.md
PASS: commands verbatim: step 2's get command is present in SKILL.md
PASS: (a) SC-08 first half: before the setup step, core.hooksPath does not resolve to the tracked hooks directory
PASS: setup step exits 0 on a fresh clone
PASS: (b) SC-08 second half #1: after the setup step, core.hooksPath resolves to the tracked hooks directory
PASS: (b) SC-08 second half #2: the post-merge file there is executable
PASS: (c) SC-13 clause 1: both runs exit 0
PASS: (c) SC-13 clause 1: value after the second run equals the first
PASS: (d) SC-13 clause 2: the step's stdout carries the value it found
PASS: (d) found value reported equals the pre-set unrelated value
PASS: (d) SC-13 clause 3: no run leaves the clone pointing at a directory the harness did not write without having said so — value is unchanged and the report above proves it was said
PASS: (d) RED PROOF precondition: unconditional variant still passes clause one (idempotence)
PASS: (d) RED PROOF: unconditional variant FAILS clause 2 — it never reports the value it found
PASS: (d) RED PROOF: unconditional variant also silently overwrites the unrelated value (clause 3 violation) without having said so
PASS: (e-green) setup step exits 0
PASS: (e-green) core.hooksPath points at the tracked dir after setup
PASS: (e-green) real merge succeeds
PASS: (e-green) SAFETY: sweep resolved its root inside this fixture, never the real harness checkout
PASS: (e-green) SC-14: the terminal feature's worktree is gone after a real merge, with NOTHING hand-installed into .git/hooks/
PASS: (e) RED PROOF still passes (a): before setup, not installed
PASS: (e) RED PROOF still passes (b): after setup, resolves + executable
PASS: (e) RED PROOF still passes (c): idempotent
PASS: (e) RED PROOF still passes (d): reports the unrelated value found
PASS: (e-red) setup step exits 0
PASS: (e-red) core.hooksPath points at the tracked dir after setup
PASS: (e-red) real merge succeeds
PASS: (e-red) RED PROOF: the shim reports the missing sweep rather than silently doing nothing
PASS: (e-red) RED PROOF: with the shim repointed at a nonexistent sweep, the worktree SURVIVES the merge
EXIT=0
PASS test-hooks-install.py
ok    gh issue close is DENIED, as a structured permissionDecision at exit 0
ok    clause 1 — the FINISHED route comes first, and its answer is to type nothing
ok    clause 2 — the DROPPED route is a RUNNABLE command, not a bare name: interpreter, path, feature dir, the mandatory --reason-file, and --yes
ok    clause 3 — the UNTRACKED escape, because this gate cannot resolve an issue number and a false deny is only acceptable if the refusal says how to recover
ok    gh api state=closed is DENIED
ok    the two denials return the IDENTICAL reason string — asserted by equality, so a second wording cannot drift into existence
ok    denied in position: 'cd /tmp && gh issue close 728'
ok    denied in position: 'FOO=1 gh issue close 728'
ok    denied in position: 'echo hi | gh issue close 728'
ok    denied in position: 'true; gh issue close 728'
ok    denied whatever the argument order: 'gh api -f state=closed -X PATCH repos/o/r/issues/9'
ok    denied whatever the argument order: 'gh api repos/o/r/issues/9 -X PATCH -f state=closed'
ok    allowed, with NO output at all: 'gh issue view 728'
ok    allowed, with NO output at all: 'gh issue list --repo o/r --state closed'
ok    allowed, with NO output at all: 'git status'
ok    allowed, with NO output at all: 'python3 .claude/skills/harness/bin/gh-sync.py abandon d --reason-file r --yes'
ok    allowed, with NO output at all: 'python3 .claude/skills/harness/bin/gh-sync.py ship d'
ok    allowed, with NO output at all: 'gh api repos/o/r/issues/9'
ok    a compound command carrying BOTH a close and a gh-sync.py call is still denied
ok    evasion denied — a quote inside the subcommand: 'gh "issue" close 5'
ok    evasion denied — single quotes on every word: "gh 'issue' 'close' 5"
ok    evasion denied — an absolute path to the same binary: '/opt/homebrew/bin/gh issue close 5'
ok    evasion denied — reached through env: '/usr/bin/env gh issue close 5'
ok    evasion denied — a backslash, which defeats an alias not a gate: '\\gh issue close 5'
ok    evasion denied — a whole command line inside one eval token: 'eval "gh issue close 5"'
ok    evasion denied — a whole command line inside one bash -c token: "bash -c 'gh issue close 5'"
ok    evasion denied — the same through sh: 'sh -c "gh issue close 5"'
ok    evasion denied — command substitution in an assignment: 'x=$(gh issue close 5)'
ok    evasion denied — the binary produced by a substitution: '$(echo gh) issue close 5'
ok    evasion denied — a quoted state value: 'gh api -X PATCH repos/o/r/issues/5 -f state="closed"'
ok    evasion denied — the state hidden in a JSON body on stdin, invisible to the command string: 'gh api --method PATCH repos/o/r/issues/5 --input -'
ok    evasion denied — the GraphQL mutation, which never spells state=closed: 'gh api graphql -f query="mutation{closeIssue(input:{issueId:"x"}){clientMutationId}}"'
ok    an unbalanced quote still DENIES when the line is genuinely a close
ok    an unlexable line carrying a real close is caught by the text fallback
ok    an unlexable line that closes NOTHING is allowed — an English contraction
ok    an unlexable line that closes NOTHING is allowed — a possessive in a commit message
ok    an unlexable line that closes NOTHING is allowed — a possessive inside a heredoc, ahead of a legitimate gh issue comment
ok    a close inside a quoted string DENIES, as the header commits to — the gate cannot distinguish echo from eval without running the shell
ok    KNOWN BLIND SPOT — a binary that exists only after shell expansion is NOT caught, and the gate is a guardrail against habit rather than a security boundary
ok    every evasion route returns the IDENTICAL reason string, so the operator learns one answer to one question
ok    tokenizing does not widen the refusal to: 'gh pr close 5'
ok    tokenizing does not widen the refusal to: 'gh issue close-milestone 5'
ok    tokenizing does not widen the refusal to: 'gh api repos/o/r/issues/5 --jq .state'
ok    tokenizing does not widen the refusal to: 'gh api -X GET repos/o/r/issues/5'
ok    tokenizing does not widen the refusal to: "git commit -m 'closes the loop'"
ok    tokenizing does not widen the refusal to: 'gh issue edit 5 --add-label wontfix'
ok    github.sync false: the gate exits 0 with no output, even for gh issue close — it costs nothing where the mirror is off
ok    no harness.json at all: the gate exits 0 with no output

ALL PASSED
PASS test-gh-close-gate.py
ok - test_in_range_anchor_reports_nothing_and_exits_zero
ok - test_missing_file_is_reported_and_exits_one
ok - test_out_of_range_line_is_reported_and_exits_one
ok - test_zero_anchors_exits_zero_and_says_so
ok - test_unreadable_target_exits_two_not_zero
ok - test_default_file_is_dev_null_readable_zero_anchors
PASS test-check-decision-anchors.py
ok - test_matching_claim_exits_zero
ok - test_mismatching_claim_reports_heading_and_exits_one
ok - test_disallowed_first_token_is_refused_and_exits_one
ok - test_zero_markers_exits_zero_and_says_so
ok - test_nonexistent_path_in_command_is_a_failure_not_a_crash
ok - test_unreadable_target_exits_two_not_zero
ok - test_checker_source_never_uses_shell_true
PASS test-check-decision-claims.py

## `git -C <worktree> diff -- .claude/skills/harness/bin/run-unit-tests.sh` (verbatim)

```diff
diff --git a/.claude/skills/harness/bin/run-unit-tests.sh b/.claude/skills/harness/bin/run-unit-tests.sh
index 4d048cb..ec12b83 100755
--- a/.claude/skills/harness/bin/run-unit-tests.sh
+++ b/.claude/skills/harness/bin/run-unit-tests.sh
@@ -28,7 +28,7 @@ BIN_DIR=".claude/skills/harness/bin"
 # #160 records is one populated kind doing two jobs while test_kinds.integration sat null,
 # so INV-20 could never see the hole and the qa matrix could not tell the two apart.
 UNIT_SCRIPTS=("test-harness-yaml-corpus.py" "test-render-brief.py" "test-team-catalog.py" "test-factory-cli.py" "test-factory-gh.py" "test-factory-config.py" "test-factory-workspace.py" "test-factory-decompose.py" "test-factory-claim.py" "test-factory-land.py" "test-no-distribution.py" "test-validate-feature-json.py" "test-gh-board.py" "test-branch-create-gate.py" "test-layout-migration.py" "test-board-station.py" "test-inject-expertise.py" "test-gh-cost-log.py" "test-context-watch.py" "test-board-lifecycle.py" "test-orchestrator-playbook.py" "test-lead-stop-and-wake.py" "test-omp-hooks.py" "test-check-omp-port.py" "test-sync-agent-adapters.py" "test-harness-boundary.py" "test-wayfind.py")
-INTEGRATION_SCRIPTS=("test-validate-digest.py" "test-gh-sync.py" "test-check-state.py" "test-check-expertise.py" "test-gen-decisions-index.py" "test-bash-write-guard.py" "test-check-domain.py" "test-harness-yaml.py" "test-upgrade-config.py" "test-check-plan-routes.py" "test-merge-settings.py" "test-factory-integration.py" "test-feature-worktree.py" "test-expertise-merge.py" "test-context-watch-cli.py" "test-context-watch-hook.py" "test-run-unit-tests-kinds.py" "test-harness-merge.py" "test-plan-merge.py" "test-observations-merge.py" "test-inflight-registry.py" "test-dispatch-guard.py" "test-merge-gitignore.py" "test-worktree-terminal.py" "test-post-merge-sweep.py" "test-hooks-install.py" "test-gh-close-gate.py")
+INTEGRATION_SCRIPTS=("test-validate-digest.py" "test-gh-sync.py" "test-check-state.py" "test-check-expertise.py" "test-gen-decisions-index.py" "test-bash-write-guard.py" "test-check-domain.py" "test-harness-yaml.py" "test-upgrade-config.py" "test-check-plan-routes.py" "test-merge-settings.py" "test-factory-integration.py" "test-feature-worktree.py" "test-expertise-merge.py" "test-context-watch-cli.py" "test-context-watch-hook.py" "test-run-unit-tests-kinds.py" "test-harness-merge.py" "test-plan-merge.py" "test-observations-merge.py" "test-inflight-registry.py" "test-dispatch-guard.py" "test-merge-gitignore.py" "test-worktree-terminal.py" "test-post-merge-sweep.py" "test-hooks-install.py" "test-gh-close-gate.py" "test-check-decision-anchors.py" "test-check-decision-claims.py")
 
 # --kind DEFAULTS TO all, so every existing caller — harness.json, a human, a QA agent —
 # keeps the behaviour it had before this split.
```

Only the two array additions — nothing else in the file touched.

## Main checkout confirmation

`git -C /Users/molchairuangutai/GitHub/harness status --porcelain -- .claude/skills/harness/bin/run-unit-tests.sh`
prints nothing — main carries none of this change (verified after the mid-task recovery described
above, and again at receipt time).

## Verdict rationale

The file change is complete, correct, and scoped to exactly the array (confirmed by diff above).
Both named checkers ran and printed `PASS`. `task_verify` is reported `fail` because the verify
command as literally written exits 1 on a pre-existing false-positive substring match unrelated to
this task's correctness (see above) — reported per DEC-173/contract discipline rather than silently
marked pass.
