# FEAT-29 T-09 — the saving is the query SHAPE, measured on one four-item board

Measured by the main session directly, 2026-08-19, with no agent run in flight. The counter is
`gh api rate_limit --jq .resources.graphql.used`, differenced immediately either side of each
call. That endpoint is REST and costs zero GraphQL points, so the instrument does not move the
figure it reports.

Board 6 (owner `mruangutai`, title `factory-smoke-a1`) is a retained smoke fixture holding four
items. Both reads ran against it, back to back, in the same session.

old_before: 25
old_after: 127
old_delta: 102
new_before: 127
new_after: 128
new_delta: 1
board_items: 4
sha: 8c2c24d

Measurement A is the OLD read shape, `gh project item-list 6 --owner mruangutai --limit 500
--format json`. Measurement B is the NEW one, `factory_gh.project_item_stations("mruangutai", 6,
"Station")`, which returned **4 entries** — the whole fixture, not a truncated page.

These are my own numbers, re-taken here rather than carried over. The plan records a prior
Measurement A at commit `6bbd706` of before 1790, after 1892, delta 102. My re-take landed on
102 as well. That agreement was not engineered and nothing was adjusted to produce it; had it
differed, the number above would be mine and the difference would be stated.

## What is held constant, and what therefore follows

Same board, same four items, same session, same minute, nothing else in flight. Item count
cannot explain a 102-versus-1 difference, because the item count is identical on both sides.
Neither can board size, network conditions, nor a concurrent agent's traffic. The only variable
is which fields the query selects.

That is the point of measuring here rather than only on board 3. On the real board the new read
cost 5 points against 506, but board 3 also has 473 items, so a sceptic could argue the saving
came from reading fewer cards. On a four-item board there are no fewer cards to read, and the
old shape still costs 102 while the new costs 1. **The saving is the query selection — the old
shape pulls the expensive `fieldValues` connection per item, the new one asks for the single
station field.**

The 10-point ceiling the plan sets for `new_delta` is met with nine points to spare. The
projected value was 1 and the measured value is 1.
