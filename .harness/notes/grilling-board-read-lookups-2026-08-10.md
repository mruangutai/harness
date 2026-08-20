# Grilling — issue #217, the whole-board reads that answer single-issue questions — 2026-08-10

## Destination

The factory stops paying a whole-board read to answer a question about one issue. Every
single-issue item lookup resolves with one GraphQL call, and the only whole-board read left is the
one that genuinely wants a list.

## Settled

- **Scope is all THREE single-issue lookups, not the one the ticket names.** #217 was filed against
  `factory_decompose.py:454`. Grilling found the same shape twice more: `factory_land.py:32`
  (`_find_item_id`) and `factory_claim.py:227` (the `--issue` path, which reads the whole board and
  then filters to one issue in Python at `:228-230`). Same defect, same fix, one review instead of
  three. The operator ruled all three in scope. #217's body is to be widened to match.

- **The claim POLL at `factory_claim.py:238` is OUT OF SCOPE.** It asks "what work is claimable right
  now" — `<station>:"Ready" is:open` — which is a list by nature. No single-issue query substitutes.
  It keeps `project_items` and keeps costing what it costs. Narrowing it was offered and declined:
  it would add an unbounded research question to a feature that otherwise has a known fix.

- **`claim --issue` MUST STILL REFUSE A CLOSED ISSUE, and the refusal becomes explicit.** Today the
  protection is a side effect: `is:open` hides the item, `raw_items` comes back empty, and claim
  refuses with "issue not found on the board". The replacement query is closed-issue-safe, so that
  side effect disappears. Add a real check on the issue's state and refuse a closed one deliberately.
  The operator's reason: claiming a closed issue means an agent picks up finished work, and that
  protection should not rest on a cost decision nobody meant as a rule.

- **`land` KEEPS TODAY'S BEHAVIOR EXACTLY — it still refuses when the issue is closed.** This was
  offered as a fix and declined, deliberately. See `## Out of scope` for what that leaves standing.
  Practically: `land` needs the same explicit open-check `claim` gets, so the two agree.

- **`decompose` KEEPS its closed-issue-safe semantics, unchanged.** `factory_decompose.py:300-305`
  omits `query=` on purpose — an issue closed between a failed run and the recovery run would be
  missed, re-triggering the exact duplicate add `_find_existing_item_id` exists to prevent. The new
  query preserves this for free. **A fix that reintroduces an open-only filter here is wrong.**

- **Proof is a unit assertion plus one live spot-check.** Unit tests assert each of the three sites
  issues exactly one `gh api graphql` and zero `gh project item-list` calls — that is the claim that
  discriminates the fix from its absence. One live `rate_limit` difference on a single lookup
  confirms the 1-point figure. **No `factory_decompose` run, no fixture snapshot, no restore.**
  Explicitly chosen against a FEAT-11-style live measurement, which cost a full UAT script, a
  fixture-protection ruling, a board-mismatch trap and a criterion amendment to produce a number the
  call-shape assertion already implies.

## Not yet specified

- Where the shared helper lives and what it is called. `factory_gh.py` is the obvious home beside
  `project_items`, but whether the three call sites share one function or each gets its own is a
  cheap, reversible structure decision — pm and eng own it, not this artifact.
- Whether the truncation guard's intent needs a different expression for a single-item query.
  `project_items` raises when `totalCount > len(items)` so a truncated read is never reported as an
  empty column. A single-issue query has no pagination to truncate, but it can still return a shape
  the code does not recognize, and **returning `None` on an unrecognized shape is unsafe**: the
  caller reads `None` as "no existing item" and re-adds. It must fail loud. The exact mechanism is
  pm's to specify.

## Out of scope

- **The claim poll**, above.
- **`land`'s latent bug, which this grilling FOUND and the operator ruled out of scope.** `land`
  raises `GhError("issue not found on the board")` when `_find_item_id` returns `None`
  (`factory_land.py:92-98`). Because that lookup filters `is:open`, an issue closed before `land`
  runs makes land FAIL and the board item never moves to Review. The closed-issue-safe query would
  have fixed it incidentally; the operator chose to preserve today's behavior so this feature ships
  zero behavior change in `land`. **File this as its own ticket** — it is real, it is latent only
  because `land` normally runs while the issue is still open, and it now has nowhere else to live.
- Anything about `gh project item-list`'s cost model beyond the measurements below. It pages at
  ~102 points per 100 items; making that cheaper is GitHub's business, not this feature's.

## Facts I verified (so pm does not re-derive them)

All measured on 2026-08-10 against board 3 (163 items), differencing
`gh api rate_limit --jq .resources.graphql.used`. Board 3 is what `.harness/factory/fleet.yaml:4`
declares.

- `gh project item-list 3 --limit 500` — **203 points**, two consecutive runs, 203 both times.
- `gh project item-list 3 --limit 100` — **102 points**. Cost tracks PAGES, not the `--limit` value.
- `gh project item-list 3 --limit 500 --query "is:open"` — **102 points**.
- `repository.issue(number:).projectItems` returning `id` and `project.number` — **1 point**.
  Correctness confirmed, not just cost: for issue #216 it returned `PVTI_lAHOAAases4Bf5NHzg15...`
  — byte-identical to what `gh project item-add` returned when #216 was added to the board.
- The four call sites: `factory_decompose.py:454` (via `_find_existing_item_id` at `:299-310`),
  `factory_land.py:32`, `factory_claim.py:227` and `factory_claim.py:238`. The first three scan for
  one issue number; only `:238` consumes the list.
- `factory_claim.py:228-230` filters `raw_items` to `args.issue` in Python immediately after the
  read — the whole board is fetched and all but one row discarded.
- `factory_land.py:92-98` raises rather than degrading when the lookup returns `None`.
- **#217's own body cites 31 points for this call. That figure is stale** — it came from FEAT-11's
  briefing, measured when board 3 was smaller. 203 supersedes it. The BRIEF should not repeat 31.

  **CONDITION INCOMPLETE, DISCLOSED 2026-08-20 (FEAT-29 SC-08).** This note records 203 with its
  board and item count -- board 3, 163 items, 2026-08-10 -- but WITHOUT the commit it was measured
  at. That is two of the three conditions the recording rule requires. **The commit was never
  recorded and cannot now be recovered:** several commits landed on 2026-08-10 and nothing in this
  note narrows which was HEAD at the time. It is NOT invented here, and 203 is NOT re-measured.

  So 203 remains partially unfalsifiable, and this disclosure is the honest form of that rather
  than a fix. Anyone relying on 203 should re-measure it and record all three conditions.
