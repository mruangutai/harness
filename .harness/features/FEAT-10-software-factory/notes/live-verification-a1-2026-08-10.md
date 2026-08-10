# FEAT-10 live verification — A1 against the real GitHub API — 2026-08-10

Run by a subagent under operator instruction, on a throwaway repo and a throwaway board. No
harness code modified, nothing pushed, board 3 and board 2 untouched.

**Headline: A1 is closed against the live API — both halves, discriminatingly proved.**

## Phases

| Phase | Command | Exit | Result | Verdict |
|---|---|---|---|---|
| A — typo `Redy` | `factory_decompose` | 2 | 0 items, 0 issues, no labels, no feature.yaml | PASS |
| B — re-run, typo still in | same | 2 | still 0 and 0 (exit 0 here was the original defect) | PASS |
| C — station corrected | same | 0 | 4 items all Ready; issues #2-#5; parent #1 holds all four as sub-issues | PASS |
| C2 — orphan recovery | ledger `items.T-03` deleted, republish | 0 | exact original item id recovered | PASS |
| D — claim | `factory_claim --as mruangutai` | 0 | #2 -> Building, assigned, `factory:claimed` | PASS |
| D — workspace | `factory_workspace --issue 2` | 0 | branch `factory/issue-2` | PASS |
| D — land | `factory_land --issue 2` | 0 | #2 -> Review, PR #6 open | PASS |
| E1 — republish after success | `factory_decompose` | 0 | ledger byte-identical, #2 stayed Review | PASS |
| E2 — re-claim self-owned | `factory_claim --issue 2 --as mruangutai` | 0 | identical payload, zero mutation | PASS |
| E3 — re-claim, other login | `--as someone-else` | 1 | unchanged | PASS |
| E4 — claim blocked issue | `--issue 5` | 2 | named the unfinished dependency | PASS |
| E5 — poll again | `factory_claim --as mruangutai` | 0 | skipped blocked #3, claimed #4 | PASS |

## Why A1 is defensible

**Change #2 — `_validate_stations`.** Phases A and B. Exit 2 on both runs, naming `ready='Redy'`
and listing the board's real options, with nothing created. The old signature — run 2 exits 0 over
a broken board — did not occur.

**Change #1 — item id recorded only after `project_field_set`.** Phase C2 alone was NOT
discriminating: `gh project item-add` on an already-added issue is idempotent (same id, no
duplicate), so 4->4-with-the-same-id looks identical whether the lookup matched or returned None
and fell through. Closed by direct call instead: `_find_existing_item_id` returns the correct id
for all four issues, `_item_repo` resolves the right repo for every raw item, and a bogus repo
returns None. The repo comparison is load-bearing, not vacuously true. No false MISS — the
specific fail-open the commit prevents.

**`--project-id` class confirmed fixed.** Every `project_field_set` succeeded live across C, C2, D
and E, so the node-id-vs-number resolution at `factory_gh.py:263-265` holds against the real API.

## Probes

- `content.repository` is present as a bare `owner/name` string, so `_item_repo`'s primary path is
  what runs live. Top-level `repository` is also present as a URL, so the fallback is reachable.
- `--query` genuinely field-filters server-side, and `totalCount` reflects the filtered set, so
  `project_items`' truncation guard does not false-raise. `factory_claim`'s poll is sound.

## Findings

**New defect the stubs cannot surface — filed as #211.** `project_field_set` costs 104 GraphQL
points per issue moved (`field-list` 102 + `project view` 2), uncached, inside the per-task loop.
The run exhausted the 5000-point hourly budget: `used 4987/5000, remaining 13` on graphql while
REST core was untouched at 4982/5000. A single-field GraphQL query returns the same three ids at
cost 1. Loud failure (exit 2), not silent.

**B-4 (#209) — live evidence added, not refuted.** A re-claim by the same login exits 0 and
mutates nothing, confirming the short-circuit at `factory_claim.py:270-274`. The scenario #209 is
about — a re-run after a FAILED station set — was never exercised. Commented on the issue.

**Settled, not a defect.** The T-04 commit calls re-adding an already-added issue "UNVERIFIED to
be idempotent". It is idempotent. `_find_existing_item_id` is belt-and-braces rather than
load-bearing — correct to keep, but the stated risk does not exist.

## Deviations

1. `gh project create` gives a `Status` field of Todo/In Progress/Done, so the run created a new
   `Station` field with Ready/Building/Review and pointed `board.station_field` at it. The journey
   passed because that key is configurable. Items carry a stray `status: "Todo"` from the untouched
   default field.

## Cleanup owed — the token lacks `delete_repo`, not attempted

`mruangutai/harness-factory-smoke-a1` (private): issues #1-#5, branches `factory/issue-2` and
`factory/issue-4`, PR #6 OPEN and unmerged, labels `harness` / `feature:ZZ-THROWAWAY-a1-smoke` /
`chore` / `factory:claimed`, #2 and #4 assigned to `mruangutai`. Projects v2 board 6
`factory-smoke-a1` with an added `Station` field and 4 items.

Untouched: board 2 (kaya-ai), board 3, `mruangutai/harness`, `mruangutai/harness-factory-smoke`.
