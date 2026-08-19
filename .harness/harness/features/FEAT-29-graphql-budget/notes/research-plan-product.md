# Research — where the GraphQL budget actually goes — FEAT-29

## BLUF — the burn is attributed, and it is one line of a gate script

**`check-state.sh` costs 506 GraphQL points per run, measured.** CLAUDE.md's own conventions say
"Check `bin/check-state.sh` BEFORE committing, never after," so a session with ~9 commit-prep runs
spends ~4,550 points on nothing but the state gate. That accounts for the ~4,700 that #571 could
not attribute.

The cost is INV-26 (`check-state.sh:1174`), which calls `gh_board.board_stations()` ->
`factory_gh.project_items()` -> `gh project item-list --limit 500`. On board 3 (473 items) that
single call measures **608 points**, because cost is linear in items returned (~1.05-1.29 pts/item).

**Both of #571's named hypotheses died.** `gh issue create` costs **2** points (18 creations = ~36,
0.7% of the burn — do not build the REST migration). `gh pr checks` costs **2** points per poll —
real, worth a cheap fix, but it cannot carry 4,700.

**Branch chosen by the evidence: (a) a code fix, WITH (c) instrumentation. Not (b).** The dominant
term is harness code, not main-session behaviour. But the fix surface is `check-state.sh`, a
**DEC-174 carve-out file** — so that edit is `main-session-direct`, by a human, never dispatched.

## Rig validation — the instrument costs zero

`gh api rate_limit` is REST, so reading it must not move `graphql.used`. Proven three times, raw:

- Session open, two consecutive reads: `used=0`, then `used=0`. Delta **0**.
- Mid-session, three consecutive reads: `used=1057`, `1057`, `1057`. Delta **0**.
- Explicit no-op control (`true` between two reads): delta **0**, run twice.

REST `core.used` moved 15 -> 16 across the whole session, confirming `rate_limit` bills to core.

## Budget of this research

| Moment | UTC | graphql.used | remaining |
|---|---|---|---|
| Session start | 2026-08-19 13:43:03 | 0 | 5000 |
| After the decisive check-state.sh run | ~13:52 | 1683 | 3317 |
| Session end, after the targeted-query proof | ~13:58 | 1684 | 3316 |

The quoted 06:36 baseline had reset; it was re-derived, not inherited. Stopped above the 2000 floor.

**Contamination, recorded because it bounds the totals.** Between two of my measurements `used`
jumped 733 -> 1036 with no call of mine in between; FEAT-27 and FEAT-28 share this budget. Roughly
300 of the 1683 are not mine. Single-call deltas stay trustworthy — the no-op control read 0
immediately before and after — but any future measurement gate must run with nothing else in
flight, or it reads another agent's traffic as its own.

## Measurements — every number is a difference I took

Repo `mruangutai/harness` unless stated. Boards: 3 = "Harness", **473 items**, 18 fields;
2 = "kaya-ai", 212 items; 6 = "factory-smoke-a1", **4 items**. Board 3's count read 473 then 474
within the session; it is live.

| Call | Delta |
|---|---|
| no-op control | **0** |
| **`.claude/skills/harness/bin/check-state.sh` (whole run)** | **506** |
| **targeted `gh api graphql`, 100 nodes, number + repo + one field value** | **1** |
| `gh project item-list 3 --limit 500` | **608** |
| `gh project item-list 3 --limit 500 --query FEAT-29` (0 hits) | 102 |
| `gh project item-list 3 --limit 20` | 21 |
| `gh project view 3` | 2 |
| `gh search issues --limit 30` | 102 |
| `gh pr checks 564` | 2 (repeated: 2) |
| `gh issue create` (fixture repo) | 2 |
| `gh issue comment` (fixture repo) | 2 |
| `gh issue close` (fixture repo) | 2 |
| `gh issue list --limit 100 --json number` | 1 |
| `gh issue list --limit 600 --json number,createdAt` | 6 |
| `gh issue view --json state` | 1 |
| `gh pr view --json state` | 1 |
| `gh pr view --json statusCheckRollup` | 1 |
| `gh pr view --json files,commits,reviews,comments` | 1 |
| `gh pr list --limit 10 --json number,statusCheckRollup` | 1 |
| `gh run list --limit 20` | **0** (REST) |

Writes used the retained fixture repo `mruangutai/harness-factory-smoke-a1`; the probe issue (#9
there) was closed in the same breath and its body says why it exists. Nothing was created in
`mruangutai/harness`.

## The fix is validated by measurement, not by reasoning

The obvious worry is that GitHub scores GraphQL on NODES requested, in which case paginating 474
items costs whatever `item-list` costs and the fix is worthless. **Measured, and it is false.** The
exact query the plan specifies — `items(first: 100)` selecting only `content { number, repository
{ nameWithOwner } }` and `fieldValueByName(name:)` — costs **1 point for a 100-node page**
(1683 -> 1684). Five pages covers 474 items for about **5 points**, against 506 today.

So the driver is the SELECTION, not the node count: `gh project item-list` requests the full
`fieldValues` connection for every item, and that is what inflates it. The apparent per-item curve
(21 pts at 20 items, ~500-608 at ~473) is that expensive selection scaling, not an unavoidable
per-node floor.

## The attribution, and exactly how confident it is

- **Mine, measured:** `check-state.sh` = **506 points per run**, at `6bbd706`, board 3 at 473
  items, `gh` authenticated, `github.sync: true`. This is the authoritative figure.
- **The standalone `item-list` reading of 608 is an upper bound, not the number.** `check-state.sh`
  CONTAINS that call, so the call cannot exceed the run: the true cost is 490-506, and the 608 was
  almost certainly inflated by the concurrent traffic recorded above. Per-item works out at roughly
  1.05-1.29 pts/item; quote the range, never a single derived digit.
- **Mine, read from code:** INV-26 (`check-state.sh:1130-1176`) is the only live caller of
  `board_stations`. It is unconditional whenever `github.sync: true`, a repo is declared and
  `gh auth status` succeeds. `gh-sync.py` and `board-station.py` import `gh_board` but use
  `load_board` / `derive_station` / `set_station` only — they do NOT call `board_stations`.
- **Arithmetic, not measurement:** ~9 runs x 506 = ~4,550. The RUN COUNT is inferred from
  CLAUDE.md's before-every-commit convention and the session's commit activity; **nothing records
  it**, so treat the multiplier as an estimate and the per-run 506 as the fact.

`.github/workflows/tests.yml` does not run `check-state.sh` (grepped) — so CI is not a second
multiplier today.

## Why the recorded 31 was wrong, stated honestly

The 2026-08-10 grilling recorded `gh project item-list --limit 500` at **31 points** and scoped it
out of #211: "31 points once per invocation is not the burn ... Leave it." Today the same read costs 490-608, and the gate containing it measures 506.

I could not reconcile the 31, and I am not going to invent a story for it:
- **Not board 6.** Board 6 holds 4 items; at ~1.29 pts/item it would cost ~5, not 31.
- **Growth alone does not explain it either.** 31 at 1.05-1.29 pts/item implies a 24-30 item board. Of the repo's
  509 issues, 336 were created on or after 2026-08-10, leaving ~173 before it — so board 3 was
  plausibly ~140 items then, which predicts ~180 points, not 31.

What is certain is the shape of the defect, and it is the B-12 failure exactly: **the 31 was
recorded without its condition** — no board, no item count, no sha for the board's state. A bare
number is unfalsifiable, so nobody could notice it dying, and an exclusion decision was built on
it. Any cost number this feature records must carry its board and item count.

## Constraints the fix must respect

**`board_stations()` cannot be fixed by adding a station `--query`.** Its own docstring
(`gh_board.py:124-131`) states that an item with no status key is recorded as `None` rather than
dropped, *because dropping it would make an unstationed card indistinguishable from a card that is
not on the board*. A station-filtered query deletes precisely that guarantee. Viable shapes
instead: a targeted GraphQL query returning only issue number + status field (the cost-1
`ProjectV2.field(name:)` shape already proven at `factory_gh.py:297-316` under DEC-146), or
narrowing the read to the feature set INV-26 actually iterates.

**`--query` caps rather than cheapens.** 608 -> 102 for a query returning ZERO items: the filter
changes the query shape, it does not avoid pagination. `factory_claim.py:304` runs one queried call
per served repo, so that site is ~102N — worth knowing, not the burn.

**The fix surface is a DEC-174 carve-out.** `check-state.sh` is named in the carve-out. Editing
INV-26's call site is `execution_mode: main-session-direct`. `gh_board.py` and `factory_gh.py` are
NOT carve-out files, so the cheaper read can be built and unit-tested by the team; only the gate's
call site is a human edit.

## Instrumentation — what it can and cannot see

`factory_gh.run_gh` (`factory_gh.py:79`) shells every harness `gh` subcommand and is not a
carve-out file — the best single choke point. `gh-sync.py` has its OWN wrapper (`:114`), so a
complete counter needs both. **Neither sees a `gh` command the main session or an agent types
directly into Bash**, and that is where #571's `gh issue view --json state` traffic lived. Say this
coverage limit out loud rather than implying the instrument sees everything.

No call-count source exists today. Verified: `.claude/settings.json` registers five hook scripts
and the two Bash-matcher ones write no log; `.harness/logs/<date>.md` is narrative; no file under
`.claude/skills/harness/bin/` references `rate_limit`.

## Grading a cost criterion — how, and how it goes red

**A cost gate must not run the 608-point call.** Board 6 (4 items) is the deterministic fixture: a
whole-board read there is ~5 points, and its item count is stable. Grade the shape against board 6
plus a unit test of the query builder; grade the real saving as a ONE-SHOT differenced measurement
on board 3, recorded with raw before/after, verified by `inspection`.

Proving the assertions can go red:
- **Cost:** point the differencing harness at today's `check-state.sh` before the fix — it must
  report ~506 and fail a 100-point threshold. That red state is observable right now.
- **Absence:** avoid both broken idioms. `test "$(git grep ... | wc -l)" = 0` passes when the
  search ERRORS (#248), and `git grep -E` does not honour `\b` (#249). Use `git grep -q ...; test
  $? -eq 1`, or a python scan that asserts the file was opened.
- **Budget error:** stub an exhausted `rate_limit` response and assert the message names the
  budget. Red state is today's raw `gh` error text.

`test_kinds` in `.harness/harness.json`: only `unit` and `integration` have runners. `component`,
`ui`, `eval`, `typecheck` are `cmd: null` and soft-skip; `functional` is excluded under DEC-187.
Every `verify: automated` here rests on `unit` or `integration`.

## Coverage limit of the planned instrument, stated once

`factory_gh.run_gh` and `gh-sync.py`'s wrapper cover harness code. **Neither sees a `gh` command
typed directly into Bash by the main session or an agent** — and that is almost certainly where the
confusing raw-error incident happened, since #571's `gh issue view --json state` traffic was
main-session typing. So both the cost record and the budget-error message are partial by
construction, and both must say so.

## The plan's verify commands were smoke-tested, and one was already dead

Every inline `verify:` in `plan.yaml` was executed against today's tree. All four report red with a
specific reason, which is the proof they can go red. **One was born non-discriminating and was
fixed:** the T-05 check searched for "31 points once per invocation is not the burn", but that
sentence WRAPS across two lines in the grilling note, so the substring could never match and the
check would have passed on day one against an uncorrected file. It now matches the unwrapped
fragment and requires a strike marker. This is P-01 caught in the act — a `verify:` that would have
passed before the change proves nothing.

## Open questions

- Q1 (blocking): board 3 holds 473 items and every cost here is linear in that. Is board pruning or
  archiving in scope, or only the call shape? Pruning to ~50 cards is a one-off that beats any code
  change; the two are not exclusive, and the answer changes the task set.
- Q2 (non-blocking): the ~9-run multiplier behind the ~4,550 attribution is inferred from
  convention, not recorded. It is exactly what the instrumentation exists to fix, and it cannot be
  recovered for this incident.
- Q3 (non-blocking): `factory_claim.py:304` costs ~102 per served repo. Fleet size was not
  measured, so that is a shape, not a number.
