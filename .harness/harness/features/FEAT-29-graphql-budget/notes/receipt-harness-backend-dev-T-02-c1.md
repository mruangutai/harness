# Receipt — harness-backend-dev — T-02 — c1

FEAT-29-graphql-budget, task T-02: `board_stations(board, repo)` in
`.claude/skills/harness/bin/gh_board.py` now calls `factory_gh.project_item_stations` (T-01's
targeted, cost-1 GraphQL call) instead of `factory_gh.project_items` (the whole-board
`item-list` scan). Return shape is unchanged: `{int issue number: station string or None}`.

## What changed and why it preserves the contract

- The field-name lookup against the raw item dict (`if field in item: ... else item.get(field.lower())`)
  is removed — `project_item_stations` already returns `item["station"]` directly (`str` or `None`).
- `content = item.get("content") or {}` and the `content.get("repository") != repo` comparison are
  **unchanged in form**: `project_item_stations`'s own contract normalizes a null-content node to
  `content_out = {}` before it reaches `board_stations`, so this still compares
  `content.repository.nameWithOwner` (flattened by T-01 into a plain string), never the item's own
  `repository` key.
- No `--query` filter added anywhere.
- No try/except around the `factory_gh.project_item_stations` call — a `GhError` propagates
  unchanged, same as before.

## RED-then-GREEN

RED: rewrote the three existing `board_stations` assertions plus the one new content-null
assertion against the new GraphQL-envelope fixture shape (`{"data": {"user": {"projectV2":
{"items": {...}}}}}`, `pageInfo.hasNextPage: false` — required, since `fake_gh` answers every argv
identically and a `true` would loop `project_item_stations` forever), while `gh_board.py` still
called the OLD `project_items`. Ran `test-gh-board.py` against the unmodified `gh_board.py`:
4 FAIL, all four `board_stations` checks, each with `GhError('project item-list response has no
totalCount...')` (the old code called the flat-shape function against a GraphQL-envelope fixture)
— watched, confirms the tests exercise the real call. GREEN: rewrote `board_stations` per the
intent; re-ran, `all pass`.

## Fixture isolation (learned from T-01, applied preemptively)

Split into two `with tempfile.TemporaryDirectory()` blocks from the start: block 1 carries the
three original assertions (excluded-repo, stationed, no-status/None-not-dropped) against a
3-node fixture; block 2 is a single-node, `totalCount: 1` fixture carrying only a null-content
node, for the new content-null assertion. Both `board_stations` calls are wrapped in
try/except with an `isinstance(st, dict)` guard on every check (P-04) — a mutation that makes the
call raise reddens gracefully instead of crashing the whole test file mid-run.

## Mutation pairs — both required, both run and observed

Baseline hash before every mutation: `3f6ab632d3d076f3120e168f58827ddc6b1ee057626c06c824b0a7d79b7adb82`
(`.claude/skills/harness/bin/gh_board.py`). Restored and re-verified against that hash after each.

| # | Mutation | Reddened (exactly) |
|---|---|---|
| 1 | None-branch replaced with a drop (`if station is None: continue` before writing `out[int(num)]`) | `board_stations: item with NO status key is present with value None, not dropped` |
| 2 | content-null path: `content.get("repository")` → `content["repository"]` (bracket access) | `board_stations: item with content null does not crash and is not in output` |

**One dead end on the way to mutation 2, recorded because it matters**: the first attempt at
mutation 2 was removing the `or {}` from `content = item.get("content") or {}` (making it
`item.get("content")`). This reddened **nothing** — `factory_gh.project_item_stations` already
normalizes a null `content` node to `content_out = {}` before returning it, so `item.get("content")`
is never actually `None` inside `board_stations`; the `or {}` guard in `board_stations` is
defensive dead code against that specific input shape. Confirmed by re-running the full suite after
the mutation and seeing zero `FAIL` lines, not by inspection. Replaced it with the bracket-access
mutation above, which targets the real access pattern and reddened exactly the one target check.
No unrelated check touched by either accepted mutation — block 1 and block 2 fixtures are disjoint
(the content-null node fails the repository-equality check before the station lookup runs, so
mutation 1 never reaches it; the other three items carry real non-empty content dicts, so mutation
2's `[...]` vs `.get` distinction never reaches them).

`git diff --stat` on `gh_board.py` after the full restore cycle shows only the T-02 diff against
HEAD (the two mutations above, both reverted) — confirmed by re-running `test-gh-board.py` GREEN
and re-hashing.

## task_verify

Command (verbatim from plan.yaml T-02 / this dispatch):
```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```
Result: exit 0. `grep -c '^FAIL '` across the full captured output: `0`. Last lines of the run
(the LAST script's own summary, `test-inject-expertise.py`, per the runner's per-script-not-
whole-run summary shape):
```
19/19 cases passed.
PASS test-inject-expertise.py
```
`test-gh-board.py`'s own line in the same run: `PASS test-gh-board.py` (line 833 of the captured
log).

## Files touched
- `.claude/skills/harness/bin/gh_board.py`
- `.claude/skills/harness/bin/test-gh-board.py`
