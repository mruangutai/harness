# Receipt — harness-backend-dev — T-01 — c1

FEAT-29-graphql-budget, task T-01: `project_item_stations(owner, number, field_name)` added to
`.claude/skills/harness/bin/factory_gh.py`, tests added to
`.claude/skills/harness/bin/test-factory-gh.py`.

## What it does

One `gh api graphql` call per page (100 items/page), paginated on `pageInfo.hasNextPage` /
`endCursor`, accumulating `{"content": {...} or {}, "station": str or None}` per node. Truncation
guard mirrors `project_items` at `factory_gh.py:193-197` (byte-identical argument shape). Missing
`totalCount` on page 1 raises rather than defaulting to 0. A null `user`/`projectV2`/`items` at any
level raises `"project item stations unreadable"` naming the null level — this is what makes an
organization-owned board (`user()` resolves null) fail loudly instead of returning `[]`.

No changes to `project_items` (factory_claim.py:304's caller untouched, out of scope per the task).

## Decision recorded — cursor-or-null argv form

`-F cursor=<cursor-or-null>` on the first page is passed as the literal string `"null"`
(`-F cursor=null`), which `gh api graphql -F` coerces to JSON `null`. Every subsequent page passes
the real `endCursor` string. Cheap, local, reversible — decided here, not escalated.

## RED-then-GREEN, and the Iron Law lapse mid-run

Wrote the implementation before the tests once (Iron Law violation). Caught it before any test
ran. Recovery, per `harness-backend-dev` P-13/P-09/G-13:
1. `git diff` captured the implementation as a patch to scratchpad, `git checkout --` reverted
   `factory_gh.py` to HEAD.
2. Wrote the 6 required test cases (plus 2 structural argv/query checks) against the now-absent
   function. Ran the suite: it crashed with
   `AttributeError: module 'factory_gh' has no attribute 'project_item_stations'` — RED, watched.
3. Reapplied the saved patch (`git apply`) — GREEN, 182/182.

**One genuine G-13 repeat mid-cycle**: during mutation-pair 1's restore I ran
`git checkout -- factory_gh.py`, which reset the file to HEAD (no T-01 code at all) rather than to
the post-mutation-1-revert state — exactly the gotcha this checkout skips. Caught immediately by
`git diff --stat` showing the file back to the pre-T-01 baseline and by
`grep -c project_item_stations` returning 0. Recovered by re-applying the saved
`git apply`-patch (sha256 `672834b3e0e8767081a386006b03332347b439ef938dd9c506111f6e19530a02`,
confirmed matching before continuing). From mutation-pair 2 onward, restores used a scoped Python
string-replace against the known-good text, never `git checkout`.

**One mutation-isolation defect found and fixed in the tests themselves, before any pair was
declared clean**: the first attempt at mutation 2 (drop items whose station is `None`) reddened
4 checks, not 1 — because the shared fixture used for the single-page "station string" test and
the truncation test also carried a null-station node, so dropping it tripped the truncation guard
as a side effect and crashed the unguarded call, taking out unrelated checks. Fixed by (a) giving
the presence test its own fixture (`STATION_PRESENCE_JSON`, `totalCount=1` deliberately, so
neither the correct 2-item output nor the mutated 1-item output trips the truncation guard) and
(b) removing the null-station node from every other fixture so only the presence test exercises
it. Also wrapped three previously-bare `project_item_stations(...)` calls in try/except (P-04) —
two-page, single-page, and the argv-shape check — since a pagination or drop mutation can turn any
of them into an uncaught raise that silently truncates the run.

## The six required mutation pairs — all six run and observed

Baseline hash before every mutation: `672834b3e0e8767081a386006b03332347b439ef938dd9c506111f6e19530a02`.
Restored and re-verified against that hash after each.

| # | Mutation | Reddened (exactly) |
|---|---|---|
| 1 | station always `None` (drop the `fieldValueByName` extraction) | `a stationed item maps to its station string` |
| 2 | drop items whose station is `None` instead of keeping them | `a null fieldValueByName item maps to station None and is present in the output` |
| 3 | force `break` after page 1, ignore `hasNextPage` | the 4 two-page-accumulation checks (calls count, cursor, count==3, page-2 items present) — one named assertion group, no unrelated check touched |
| 4 | remove the `len(items_out) < total` truncation raise | `accumulated count below totalCount raises GhError`, `truncation message names both totals` |
| 5 | default missing `totalCount` to `0` instead of raising | `a response missing totalCount raises GhError, never defaults it to 0` |
| 6 | remove the `user is None` guard (falls through to `AttributeError`) | `a null user (organization-owned board) raises GhError, never returns an empty list` |

6/6 pairs run, observed reddening exactly their target, reverted, hash-confirmed clean.

## task_verify

Command (verbatim from plan.yaml T-01):
```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```
Result: exit 0. `grep -c "^FAIL "` across the full run output: `0`. `grep -c "^PASS "`: `138`
scripts. `test-factory-gh.py` line: `182/182 checks passed.` / `PASS test-factory-gh.py`.

## Files touched
- `.claude/skills/harness/bin/factory_gh.py`
- `.claude/skills/harness/bin/test-factory-gh.py`
