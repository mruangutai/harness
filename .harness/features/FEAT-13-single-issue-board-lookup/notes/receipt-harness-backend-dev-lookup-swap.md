# Receipt — T-01 targeted GraphQL board lookup — harness-backend-dev

## HALF A — the helper, RED then GREEN

RED, before `factory_gh.issue_board_item_id` existed (only the step-5 test block in
`test-factory-gh.py` had landed):

```
$ python3 .claude/skills/harness/bin/test-factory-gh.py; echo exit=$?
```
```
[... 33/33 pre-existing checks in this file passed unchanged ...]
Traceback (most recent call last):
  File ".../test-factory-gh.py", line 645, in <module>
    match_id = fgh.issue_board_item_id("acme/widget", 42, 9)
               ^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: module 'factory_gh' has no attribute 'issue_board_item_id'
exit=1
```
Date: 2026-08-10.

Full-suite RED confirming only this file broke:
```
$ bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit; echo exit=$?
```
```
[... every other suite: PASS ...]
FAIL test-factory-gh.py
exit=1
```
Date: 2026-08-10.

GREEN, after the helper landed (step 1 in `factory_gh.py`, nothing else touched):

```
$ bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit; echo exit=$?
```
```
PASS test-factory-cli.py
PASS test-factory-gh.py
PASS test-factory-config.py
PASS test-factory-workspace.py
PASS test-factory-decompose.py
PASS test-factory-claim.py
PASS test-factory-land.py
[... every other pre-existing suite: PASS ...]
exit=0
```
Date: 2026-08-10. `test-factory-gh.py` itself: 153/153 checks passed (22 of them the new
`issue_board_item_id` cases).

HALF A gate cleared — proceeding to HALF B (steps 2-4, the three call sites, plus the
integration stub).

## Deviation from the intent's verbatim step-5 wording (test shape, mine to decide)

The intent's SC-01 phrasing — "ZERO calls whose `argv[:2] == ["project", "item-list"]`" — is
vacuous against this file's `dispatching_fake`/`recorder` argv shape: `argv[0]` is always the gh
binary (see `dispatching_fake`'s own docstring), so `argv[:2]` is `[binary, "project"]` and can
never equal `["project", "item-list"]`. Every existing assertion in this file scopes on
`argv[1:3]` for exactly this reason (e.g. the `project_field_set` item-edit checks). Wrote the
new assertion as `argv[1:3] == ["project", "item-list"]` instead — this is the form that
actually discriminates a helper that still shells out to `project item-list`.

## HALF B — call sites, tests, integration stub

Order followed exactly: tests for steps 2/3/4 written and watched RED per file (production code
unchanged at each RED point), then the matching production edit, then GREEN per file, then the
integration stub branch, then the task's full `verify:`.

- `test-factory-decompose.py`: written first (Recorder `issue_board_item_id` method, D4-3/D4-3b
  rewritten off `item_by_issue`, D4-3c repurposed for the closed-issue case). Moved straight to
  the production edit without pausing to capture RED at that point — caught in review before
  landing this receipt, so RED was reconstructed after the fact: took a sha256 of the
  already-edited `factory_decompose.py`
  (`adc0640f26ece1d132a059ef6882e0f3f2edca2856e55e1c8a98caa7d06dba24`), swapped
  `git show HEAD:.../factory_decompose.py` in over it, re-ran the test file, confirmed 12 `FAIL`
  lines against the pre-task production code (D4-3/D4-3b/D4-3c), restored the edited file from a
  saved copy, and re-hashed it: **sha256 matches**
  (`adc0640f26ece1d132a059ef6882e0f3f2edca2856e55e1c8a98caa7d06dba24`) — the restore lost nothing.
  Confirmed the full unit suite still 10/10 `PASS` afterward. `factory_decompose.py` step 2
  landed (`_find_existing_item_id` delegates to `factory_gh.issue_board_item_id`; `_item_repo`
  deleted; docstrings reworded per the intent's three/four verdicts). GREEN: 175/175 checks
  passed.
- `test-factory-land.py`: RED confirmed — 9 `FAIL` lines (the M1 lookup-argument checks, the new
  M7 closed-issue block). `factory_land.py` step 3 landed (`_find_item_id` delegates to
  `factory_gh.issue_board_item_id`; call site reordered to `(args.repo, args.issue,
  board_number)`; `issue_view` widened to `["title", "state"]`; explicit open-check raising
  `factory_gh.GhError(what="issue is not open", value=args.issue)` immediately before the
  lookup, after the push and the pull-request create). GREEN: 56/56 checks passed.
- `test-factory-claim.py`: RED confirmed — 6 `FAIL` lines (R4's new lookup-shape checks, R6a/R6b
  closed-issue refusal). `factory_claim.py` step 4 landed (`--issue` branch iterates
  `fleet["repos"]`, filtered to `--repo`, calling `factory_gh.issue_board_item_id` per repo,
  first non-None id wins, synthetic single-row `raw_items`; the closed-issue refusal
  (`factory_cli.refuse(..., "issue is not open", ...)`) inserted immediately before 5a
  self-ownership, with 5a's own comment reworded). GREEN: 95/95 checks passed.
- `test-factory-integration.py`: added a query-text-keyed branch inside the existing
  `["api", "graphql"]` dispatch, ahead of the field-resolve fallback, answering
  `repository.issue.projectItems` from `state["items"]`/`state["issues"]`. Synthetic node's
  `project.number` is hardcoded `9`, matching `fleet_dict`'s `board.number`. GREEN: 97/97 checks
  passed (same count as the pre-task baseline).

Full unit run after all of HALF B: `bash .claude/skills/harness/bin/run-unit-tests.sh --kind
unit` — exit 0, every one of the 10 suites `PASS`.

## Task verify — exact invocation, verbatim tail, exit status

```
$ bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit &&
  python3 .claude/skills/harness/bin/test-factory-integration.py &&
  grep -q 'def issue_board_item_id' .claude/skills/harness/bin/factory_gh.py &&
  ! grep -q 'factory_gh\.project_items' .claude/skills/harness/bin/factory_decompose.py &&
  ! grep -q 'factory_gh\.project_items' .claude/skills/harness/bin/factory_land.py &&
  test "$(grep -c 'factory_gh\.project_items' .claude/skills/harness/bin/factory_claim.py)" = 1
$ echo exit=$?
```
```
[... all 10 unit suites: PASS ...]
[... test-factory-integration.py: 97/97 checks passed ...]
exit=0
```
Date: 2026-08-10. Directly measured: `grep -c 'factory_gh\.project_items'` reports 0 in
`factory_decompose.py`, 0 in `factory_land.py`, 1 in `factory_claim.py` (the surviving poll
call at `factory_claim.py:238`, untouched).

## Test-shape deviations recorded (mine to decide — reversible)

1. The zero-item-list assertion in `test-factory-gh.py` — see HALF A note above
   (`argv[1:3]`, not the intent's literal `argv[:2]`, which is vacuous against this file's fake).
2. `test-factory-decompose.py`'s D4-3c slot was repurposed. Its original subject
   (`_item_repo`'s URL-form fallback) no longer exists — step 2 deletes `_item_repo`, and the new
   lookup is repository-scoped server-side, so a URL-form-repository fixture would be
   byte-identical to D4-3's own fixture and assert nothing new. Repurposed the same slot for the
   REQ-02/SC-05-mandated case instead: a partial-disposition task whose issue is CLOSED still
   resolves via the lookup and issues no second `project_item_add`. Not a test edited to pass —
   the code the old case exercised was deleted by the task's own step 2.
3. R7 (`rec.items = []`, `--issue` on an issue absent from the board entirely) pins the
   not-found-on-the-board-at-all path at exit 2, which is unchanged from today's behaviour under
   both the old and the new code. This is NOT the D-02 accepted-behaviour-delta case named in the
   plan's Goal exception (the board holds the issue under a repo outside the fleet or not
   matching `--repo`) — that case is deliberately untested here, by the plan's own choice not to
   pin the old exit code with an assertion (D-02's `because:`). R7 only guards the ordinary miss.

## Honesty notes

- `_find_existing_item_id`'s rewritten docstring carries the sentence "Confirmed live on
  2026-08-10, read-only, against board 3: the targeted repository.issue.projectItems query
  returned the board item for an issue in the CLOSED state." That sentence is **transcribed from
  T-01's own intent text**, not independently measured by this run. This task's harness-only
  T-01 did no live gh call; T-02 (out of this task's scope) is where SC-10's live spot-check
  actually happens. Flagging this so it is not read as this run's own observation.
- `factory_decompose.py:282` still contains the literal substring `is:open`, inside the KEPT
  clause of `_find_existing_item_id`'s docstring ("factory_claim.py's `is:open` scoping serves a
  different purpose…") — the intent explicitly ordered this sentence's MEANING kept. It is prose
  naming a DIFFERENT function's behaviour for contrast, not scoping introduced into this
  function's own query. Grepping `is:open` in this file will hit it; grepping the file's actual
  GraphQL/query construction path will not, and the task's verify does not grep for `is:open` at
  all.
- `STATE.md` and `feature.yaml` under this feature's `.harness/` directory arrived already
  modified before this run's first edit (visible in the very first `git status` of this session)
  — not touched by this task, not counted in `files_touched` below.

## Open questions

- Q1: SC-05 ("Decompose's recovery path resolves the existing item id for an issue whose state is
  closed… verify: automated, evidence: unit") cannot be encoded as a unit-layer distinction:
  `factory_gh.issue_board_item_id`'s new query carries no issue-state input at all, and the test
  Recorder never models state, so decompose's own code path takes no state signal either way. The
  D4-3c unit test (`test-factory-decompose.py`) proves only that the call carries no state-scoping
  argument — the same assertion for an open OR closed issue. The one additional unit-layer
  assertion available, not yet added, is on the query TEXT in `test-factory-gh.py`: that
  `_ISSUE_ITEM_QUERY` selects `issue(number: ...)` with no state/`query=` filter argument at all —
  that is the mechanism REQ-02 actually rests on. Real closedness coverage is T-02's live
  spot-check (SC-10), out of this task. Does SC-05's `evidence: unit` still read as satisfied by
  the call-shape assertion plus the query-text guarantee, or does the lead want the query-text
  assertion added here before this counts as done?

## Files touched

- `.claude/skills/harness/bin/factory_gh.py`
- `.claude/skills/harness/bin/factory_decompose.py`
- `.claude/skills/harness/bin/factory_land.py`
- `.claude/skills/harness/bin/factory_claim.py`
- `.claude/skills/harness/bin/test-factory-gh.py`
- `.claude/skills/harness/bin/test-factory-decompose.py`
- `.claude/skills/harness/bin/test-factory-land.py`
- `.claude/skills/harness/bin/test-factory-claim.py`
- `.claude/skills/harness/bin/test-factory-integration.py`
