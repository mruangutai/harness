# Research — plan-product — FEAT-29 — cycle 1

Cycle 0's evidence stands unchanged in `notes/research-plan-product.md`. This file records only what
cycle 1 changed and the one measurement it took.

## BLUF

All three send-back defects are closed. SC-03 now grades a measurement the plan produces (new task
**T-09**), and the discriminating number was taken live this cycle: **the same four-item board 6
costs 102 points through the current read and 1 point through the new read shape.** Same board, same
item count, same session — so the saving cannot be attributed to a shrunken board, which was the
whole point of SC-03.

## The measurement taken this cycle (raw, with conditions)

Owner `mruangutai`, board 6 (`factory-smoke-a1`), **4 items**, station field `Station`, 2026-08-19,
tree at `6bbd706`, nothing else of mine in flight. Counter read via
`gh api rate_limit --jq .resources.graphql.used` (REST, costs zero GraphQL).

| Read | before | after | delta |
|---|---|---|---|
| `gh project item-list 6 --owner mruangutai --limit 500 --format json` (today's shape) | 1790 | 1892 | **102** |
| targeted `gh api graphql` single page, `content{number,repository}` + `fieldValueByName` only | 1789 | 1790 | **1** |

Both returned 4 items, `totalCount: 4`.

**What this settles.** Cycle 0 established cost rises with item count; it did not separate *shape*
from *size*. At 4 items the old read still costs 102, so the dominant term is the field selection —
`item-list` pulls the whole `fieldValues` connection per item — not the node count. 102 → 1 on an
unchanged board is the falsifier SC-03 needed. Caveat kept explicit: 102 on 4 items and ~490-506 per
`check-state.sh` run on 473 items are not the same call path (the run does more than one thing), so
these numbers bound the shape claim, not the total-saving claim, which stays with T-06/T-07.

## What changed, defect by defect

**1 — SC-03 had no producer. Added T-09**, `main-session-direct` (feature `notes/` is granted to no
member domain), depends on T-01 and T-02, writes `notes/measurement-board6.md`. Its `verify:` fails
on a missing file, on `new_delta > 10`, on `board_items != 4`, and — the assertion that matters — on
`old_delta <= new_delta`, i.e. it refuses to pass if the old read was not actually more expensive.
Four paths exercised in-memory: green `OK`; `new_delta: 40` → ceiling breach; `board_items: 474` →
wrong fixture; `old_delta: 1` → "nothing is proven". SC-03 rewritten to name the file, both deltas
and the constant-item-count argument.

I chose the added task over rewriting SC-03 down to what T-06/T-07 already produce. Those two
measure board 3, whose item count is live and drifting (474 today, 473 at `6bbd706`), so a
board-3-only criterion cannot exclude "fewer items" as the cause. Board 6 is a retained fixture and
holds its count.

**2 — SC-06 had a trace but no producer.** T-03's intent now instructs a module-level
`COVERAGE_NOTICE` constant in `gh_cost_log.py`, written as the first JSON line
(`{"coverage": ...}`) of each new `.harness/logs/gh-cost-<date>.jsonl`, and explicitly forbids
putting the notice only in a comment or a README. Two test assertions added: a fresh file's first
line parses as JSON with a `coverage` key naming both `run_gh` and directly-typed `gh`; a second
append does not repeat it. SC-06 rewritten to name that location, so `verify: inspection` has a
file:line to land on.

**3 — 608 as "the corrected figure", removed from both places.** T-08's intent now writes the
490-506 range with its condition into CLAUDE.md and carries an explicit instruction *not* to write
608 there, naming why (contaminated sample, D-03's own failure mode). SC-08 now demands 490-506 with
its condition and permits 608 only as the labelled upper bound. While there I found the same bare
608 in the BRIEF's Problem section (line 14) and the bare `506` headline; both are now ranged and
conditioned. `grep -n 608` over both artifacts returns three hits, each of which labels it a
contaminated upper bound.

## Route check

`python3 .claude/skills/harness/bin/check-plan-routes.py .harness/harness/features/FEAT-29-graphql-budget/plan.yaml`
→ **exit 0, 0 violations**, 9 tasks. T-06, T-07 and T-09 report `DEVIATION` (feature `notes/` is
granted to `harness-orchestrator`, so declaring main-session-direct is stricter than necessary, not
a violation); that is intentional and matches T-06's existing treatment.

## Not changed

The 506/608 reconciliation logic itself, per the send-back. No task built. No git operation of any
kind. Writes confined to this feature folder. Both approvals remain `pending`.

## Open questions

- **Q1 (blocking, unchanged):** board 3 holds 474 items today and every cost here is linear in that
  count. Is pruning or archiving old cards in scope? A one-off prune beats any code change on its
  own and is not exclusive with it, but it changes the task set.
- **Q2 (non-blocking):** should the cost log be gitignored? `.harness/logs/` is tracked today, so a
  daily JSONL will show in every `git status` and interacts with the dirty-tree halt.
- **Q3 (non-blocking):** `factory_claim.py:304` also calls `project_items` at ~102 points per served
  repo. Out of scope here; worth a backlog item.
