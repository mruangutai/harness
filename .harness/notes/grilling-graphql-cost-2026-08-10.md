# Grilling — the GraphQL cost fix in factory_gh.py (issue #211) — 2026-08-10

## Destination

`factory_decompose` on a four-task feature costs single-digit GraphQL points instead of roughly
500, and the factory stops exhausting the 5000-point hourly budget. The station-name and
option-name error paths behave exactly as they do today.

## Settled

- **Organization-owned boards → out of scope, but fail loudly.** Support user-owned boards only.
  If the board owner resolves to an organization, refuse with a named error rather than letting a
  GraphQL null surface as a confusing message. No org board exists in the fleet today.
- ~~**`project_items` (`gh project item-list`) → out of scope.** 31 points once per invocation is not
  the burn, and it is never called in a loop. Leave it on `gh project item-list`, whose `--query`
  server-side filter and `totalCount` truncation guard were validated live on 2026-08-10.~~
  **STRUCK 2026-08-19 (#571).** `check-state.sh` INV-26 calls this read once per run, and the whole
  run measures **506 GraphQL points, on board 3 with 473 items, at commit `6bbd706`**, measured by
  differencing `gh api rate_limit --jq .resources.graphql.used`. The standalone read read 608 in one
  sample, but `check-state.sh` CONTAINS it, so the call cannot exceed the run: quote **490 to 506**
  and treat 608 as a contaminated upper bound. Per item that is roughly **1.05 to 1.29 points**.
  **It IS the burn.** The `--query` and `totalCount` observations still stand; only the exclusion
  does not.
- **The write stays on `gh project item-edit`.** Measured, not assumed: it costs **1 point**. There
  is nothing to gain from `updateProjectV2ItemFieldValue`, and `item-edit` is proven live across
  every phase of the A1 verification run.
- **No caching.** With the read at 1 and the write at 1, a station move costs 2 points against
  today's 105. Caching was the earlier recommendation and the measurements retired it.
- **No fallback to `gh project field-list`.** Keeping the 102-point path in the tree as a fallback
  preserves the thing being removed — the same reasoning the project applied to the hand-rolled
  YAML parser under DEC-171.
- **Verification runs live against board 6**, the throwaway that already exists and is already owed
  cleanup. Difference `gh api rate_limit` across a real `factory_decompose`. No new repo, no new
  board, so this adds no undeletable resource. Stub-only assertions were rejected: they prove the
  code changed, not that the cost fell, and cost is the entire point.

## Not yet specified

- Whether one function can serve both `project_field_options` (which needs option **names**) and
  `project_field_set` (which needs the **ids**), given the single query returns both. A shape
  question for whoever writes it, not a decision the operator owes.

## Out of scope

- Organization-owned board support — no consumer exists, and the test cannot be run against this
  account.
- ~~`project_items` / `gh project item-list` — wrong order of magnitude, and never looped.~~
  **STRUCK 2026-08-19 (#571).** The order of magnitude was wrong by a factor of about 20, and cost
  per call is what matters here, not whether it is looped.
- The `updateProjectV2ItemFieldValue` mutation — measurement removed the reason to want it.

## Facts I verified (so pm does not re-derive them)

All at `3ecaf8c`, before the FEAT-10 merge. Costs measured by differencing
`gh api rate_limit --jq .resources.graphql.used` across each call.

- `gh project field-list 3 --owner mruangutai --format json` costs **102** points. With
  `--limit 5` it still costs **102** — the cost is in the query shape `gh` sends, not the number of
  fields returned. An earlier reading, that 102 scaled with board 6's 13 fields, is **wrong**:
  board 3 costs the same.
- `gh project view 3` costs **2**. ~~`gh project item-list --limit 500` costs **31**.~~
  **STRUCK 2026-08-19 (#571) — and NOT reconciled.** The 31 could not be explained: board 6 holds 4
  items and would cost about 5; board 3 was plausibly around 140 items on 2026-08-10, which predicts
  about 150 to 180. Neither figure explains 31. No reconciliation is invented here — recording it as
  unreconciled is the honest entry, and it is the reason the recording rule below exists.
  `gh project item-edit` costs **1** (measured on board 6).
- `project_field_set` (`factory_gh.py:240-278`) therefore costs **104** per issue moved, in two
  uncached reads — `_field_list` at `:196-198` and `gh project view` at `:268-271`. The comment at
  `:266` states the second is uncached "for parity" with the first.
- A single GraphQL query returns the project node id, the field id and every option id at
  **cost 1**, using `ProjectV2.field(name:)`. Run live against board 3 with `field=Status`, it
  returned `PVT_kwHOAAases4BfZ9Z`, `PVTSSF_lAHOAAases4BfZ9ZzhZtFWg` and all five options.
- **`project_field_set` is the only call inside a loop** — `factory_decompose.py:444-458`.
  `factory_claim.py:330` and `factory_land.py:99` fire once per issue.
- `project_field_options` runs once per invocation, at `decompose:261` and `claim:214`.
  `project_items` has four call sites, none looped.
- `factory_gh.py` uses **no GraphQL today**; `run_gh` (`:79`) shells `gh` subcommands only.
- Every board in play is **user-owned**: `gh api users/mruangutai --jq .type` returns `User`, and
  boards 2, 3 and 6 all sit under `mruangutai`.
- The two error paths that must survive are `factory_gh.py:251-262` — field not offered, and option
  not offered. `_validate_stations` and the `Redy` typo case depend on them.
- The stub tests asserting the current call shape are `test-factory-gh.py:260-318`.

## Recording rule, learned here

**Every GraphQL cost figure recorded anywhere in this repository must carry three conditions: the
board it was measured on, that board's item count, and the commit it was measured at.** The 31
carried none of them. That is why it could never be shown to be wrong, and an exclusion decision was
built on top of it and survived nine days.

**A figure taken while another agent run is in flight is an upper bound, and must be recorded as a
range.** On 2026-08-19 the shared account counter moved roughly 300 points with no call from the
measuring session in between — later in the same session it moved about 1,605. A single number
implies a precision the shared counter cannot provide.
