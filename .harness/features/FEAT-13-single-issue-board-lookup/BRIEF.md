# BRIEF — FEAT-13 Single-issue board lookup

## Problem

Three factory tools answer a question about **one** issue by downloading the **whole** project
board. `factory_decompose.py:454` (via `_find_existing_item_id` at `:299-310`) pays 203 GraphQL
points to learn whether one issue already has a board item. `factory_land.py:32` and
`factory_claim.py:227` pay 102 points each for the same shape — `factory_claim.py:228-230` fetches
every row and then discards all but one in Python. Measured 2026-08-10 against board 3 at 163
items; the cost tracks pages, so it grows ~102 points per additional 100 items and every factory
run gets more expensive as the board fills. A targeted `repository.issue(number:).projectItems`
query answers the same question for **1 point**, verified to return the identical item id.

Issue #217 filed one of these three. The grilling
(`.harness/notes/grilling-board-read-lookups-2026-08-10.md`) found the other two and the operator
ruled all three in scope — one review instead of three for the identical change.

## Goal

Every single-issue board lookup in the factory resolves with one targeted GraphQL call instead of a
whole-board read, and the only whole-board read left is the claim poll, which genuinely wants a
list. No tool changes what an operator observes, with one recorded exception noted below:
`decompose` still recovers a closed issue's existing item, `land` still refuses a closed issue, and
`claim --issue` still refuses one — the last two by a deliberate check rather than by the side
effect of a filter that is going away.

## Requirements

- REQ-01: Resolving one issue's board item does not read the whole board. All three single-issue
  lookups — decompose's recovery lookup, land's review-station move, and claim's `--issue` path —
  resolve through a targeted, repository-scoped query.
- REQ-02: Decompose's recovery lookup still finds the existing board item of an issue that was
  **closed** between the failed run and the recovery run, so it never re-adds an item that already
  exists.
- REQ-03: `claim --issue` refuses a closed issue, by an explicit check on the issue's state rather
  than as a side effect of a board filter — including when the issue is one this agent already
  owns.
- REQ-04: `land` behaves exactly as it does today, including refusing when the issue is closed and
  failing at the same point in its sequence, with the board item left unmoved.
- REQ-05: A lookup that finds no board item for the issue reports **no item** — decompose's signal
  to add one — while a response whose shape the code does not recognise, or one whose item list is
  truncated, fails loudly instead.
- REQ-06: The claim poll — "what work is claimable right now" — keeps reading the board as a list,
  unchanged in query and in cost.

## Success Criteria

- SC-01: One lookup emits exactly one `gh api graphql` invocation and zero `gh project item-list`
  invocations, asserted on the argv the helper actually builds.
  verify: automated      evidence: unit
- SC-02: Each of the three call sites performs its single-issue lookup with zero calls to
  `project_items`, asserted separately at each of the three sites.
  verify: automated      evidence: unit
- SC-03: The two no-item cases are told apart by separate assertions: a response carrying a
  recognised, non-truncated item list with no item on the board in hand yields "no item" and does
  **not** raise; a response whose shape is unrecognised raises.
  verify: automated      evidence: unit
- SC-04: A response whose reported item total exceeds the number of items returned raises rather
  than reporting "no item".
  verify: automated      evidence: unit
- SC-05: Decompose's recovery path resolves the existing item id for an issue whose state is closed,
  and issues no second board add for it.
  verify: automated      evidence: unit
- SC-06: `claim --issue` on a closed issue exits refused and makes zero mutating calls (no label, no
  assignment, no station set, no ref creation) — asserted both for a closed issue the agent does not
  own and for a closed issue carrying `factory:claimed` and this agent's assignment.
  verify: automated      evidence: unit
- SC-07: `land` on a closed issue fails after the branch push and the pull-request create, with the
  station never set — the same point in the sequence as today.
  verify: automated      evidence: unit
- SC-08: The end-to-end journey (decompose → claim → workspace → land) still passes against the
  forked stub `gh`, which answers the new query from the real argv the tools emit.
  verify: automated      evidence: integration
- SC-09: The claim poll still calls `project_items` with its station-and-open query, and its call
  shape is unchanged.
  verify: automated      evidence: unit
- SC-10: One live, read-only spot-check confirms the cost and the correctness of a single lookup:
  the GraphQL points consumed by one lookup against the live board is at most 5, and the item id it
  returns matches the id the board already holds for that issue.
  verify: inspection

## Verification gaps

None on this surface. Both kinds these criteria rest on have runners in
`.harness/harness.json`: `unit` detects `.claude/skills/harness/bin/test-*.py` and `integration`
names `.claude/skills/harness/bin/test-factory-integration.py` outright, and neither `cmd` is null.
No criterion here rests on `component`, `ui`, `eval` or `typecheck`, all of which are unresolved.

## Constraints

- **The claim poll at `factory_claim.py:238` is out of scope.** It asks "what is claimable now",
  which is a list by nature. Narrowing it was offered and declined. It keeps `project_items` and
  keeps costing what it costs.
- **`project_items` and its `totalCount` truncation guard stay.** After this feature the poll is
  their only remaining caller. Removing either as tidy-up would delete the poll's protection against
  a truncated read being reported as an empty column.
- **No open-only filter may be introduced into decompose's lookup.** `factory_decompose.py:300-305`
  omits `query=` deliberately; reintroducing `is:open` there re-triggers the exact duplicate board
  add the function exists to prevent.
- **`land`'s latent bug is out of scope and already filed as issue #238.** Because today's lookup
  filters `is:open`, an issue closed before `land` runs makes `land` fail and the board item never
  reaches Review. The operator chose to preserve today's behaviour so this feature ships zero
  behaviour change in `land`. No task here may fix it.
- **Proof is unit call-shape assertions plus one live read.** No `factory_decompose` run against the
  live board, no fixture snapshot, no restore — explicitly chosen against a FEAT-11-style live
  measurement.
- **One observable change is accepted, not prevented — the Goal's exception.** When the board holds
  the issue under a repository that is not in the fleet, or not the one `--repo` names,
  `claim --issue` today reports nothing to do (exit 1) and after this feature refuses (exit 2). The
  case cannot arise while `.harness/factory/fleet.yaml` declares a single repo, so the cost of
  preserving the old exit code was judged higher than the cost of recording the change. Nothing
  else about the case differs: no board write happens on either path.
- Nothing outside `.claude/skills/harness/bin/factory_*.py` and their `test-factory-*.py` siblings
  changes. None of the four DEC-174 carve-out scripts is in scope.
- Issue #217's body cites **31 points** for decompose's call. That figure is stale — it came from
  FEAT-11's briefing, measured when board 3 was smaller. 203 supersedes it and nothing here repeats
  31.

## Approval

status: approved
approved_by: operator
date: 2026-08-10

**Ratified by this signature — the amended Goal.** After the swap, `claim --issue` exits 2 (refused)
instead of 1 (nothing to do) when the board holds the issue under a repo outside the fleet. That is a
change in what an operator observes, so the Goal names it as one recorded exception rather than
claiming no tool changes behaviour. The case cannot arise while `fleet.yaml` declares a single repo.
