# SIMPLIFICATION angle + J1 vacuity judgement — FEAT-24 (harness-dev-ops, 2026-08-18)

## BLUF

Two findings, both real. Highest-value one: T-02 item 6 (a per-process memoization cache for
`board_for`/`product_config`) is machinery no requirement forces, has zero test coverage, and is a
concrete correctness risk given the fixture convention this same suite already uses (identical
`owner/name` + `default_branch: "main"` across most cases). The second is a clause-level vacuity in
T-06's own `verify:` (my own dispatched task's file): the `_note` check is negative-only and does
not assert the replacement sentence is actually present.

J1: nine of the ten `verify:` blocks can genuinely fail; T-06's `_note` clause cannot fail on one
concrete input (see below). T-05's claimed positive control (`plan.yaml:697`, not :677 as the
dispatch approximated) does control — verified against the current `check-state.sh` INV-26 block,
which has no pre-existing `INV-26 BEGINS`/`ENDS` markers, so an unmarked or mis-marked block reds via
an empty slice failing the `derive_station` grep.

## Findings

### F1 — T-02 item 6 (memoization) is unforced machinery with no test coverage and a live collision risk
- file/line: `plan.yaml:403-405` (item 6, `product_config`/`board_for` memoisation)
- angle: SIMPLIFICATION — unnecessary machinery
- summary: T-02 requires a module-level `(repo_name, ref)` memo for remote board reads "so that a
  tool calling `board_for` twice makes one network call." No REQ or SC in BRIEF.md mentions call
  count or caching; SC-06 only forbids falling back to a cache **on failure**, which item 6 doesn't
  do. None of T-02's fifteen `has(...)` verify clauses (`plan.yaml:351-361`) name a memoisation case.
- cost if left: (a) the requirement can be silently dropped or wrongly built and nothing in T-02's
  own verify reds — it is unverified spec, the same class J1 is designed to catch, just in intent
  prose rather than in `verify:`. (b) worse, it is a live footgun for the suite T-02 itself adds:
  `test-factory-config.py` already fixtures nearly every case on the identical pair
  `owner/name` + `default_branch: "main"` (confirmed at `test-factory-config.py:410-413`, `:238`,
  `:48`). T-02 adds "product_config reads the remote... no checkout" and "board_for raises when the
  product config declares no board" as two separate new cases (`plan.yaml:357,361`) that plausibly
  stub different `product_config` outputs for the same `(repo_name, ref)` key in the same process —
  a memo that survives across `check()` calls would return the first case's stubbed value to the
  second, producing a false pass or a confusing false fail depending on execution order, with no
  visible cause in the diff.
- fix: either (1) drop item 6 — nothing traces to it, or (2) if kept, add one instruction: tests
  covering `product_config`/`board_for` must each use a distinct `(repo_name, ref)` pair, or the
  test file must reset the module-level memo dict between cases (e.g. `fc._PRODUCT_CONFIG_CACHE.clear()`
  in a `setup`), and add a verify clause asserting a second `board_for` call for the same pair does
  not re-invoke the monkeypatched `file_at_ref`.
- rank: would-cost-a-build-cycle

### F2 — T-06's `_note` verify clause is negative-only and cannot fail on a legitimate input
- file/line: `plan.yaml:790-792`
- angle: J1 vacuity (a plan-surface `verify:` clause), reported here because it is a task I am
  dispatched to execute
- summary: the clause checks only that the OLD sentences ("INV-26 is vacuous", "station writes are
  not attempted") are absent from `_note`. It asserts nothing about the replacement sentence intent
  item 4 requires (`plan.yaml:822-824`: the note must state that an incomplete board is now a loud
  error naming the offending key, and that only an explicit null means no board), and nothing about
  the retained sentences (no pinned ids; "PLACEMENT IS TEMPORARY").
- cost if left: **concrete input that should red but doesn't** — set `"_note": ""`, or delete the
  `_note` key entirely. Both banned substrings are trivially absent, every other T-06 check (stations
  map, `owner`/`number`/`station_field` survival) is independent of `_note` and stays green, so the
  whole clause passes while the task drops the note, the required replacement sentence, and the
  retained "PLACEMENT IS TEMPORARY" sentence — the exact "negative assertion scoped past the
  interface it names" vacuity shape named in the dispatch. Verified the live note (`.harness/harness.json`
  today) does contain both banned substrings verbatim, so the clause does catch a lazy
  keep-the-old-note-unchanged — it only fails to catch a note that's dropped or rewritten wrong.
  T-08's `_board_note` check (`plan.yaml:932-939`) is the correct pattern already in this same plan:
  positive term checks (`for term in (...)`) plus an explicit "loud"/"error" assertion.
- fix: add positive assertions mirroring T-08's pattern — e.g. `"loud" in note or "error" in note`
  and `"PLACEMENT IS TEMPORARY" in note` — alongside the existing negative check.
- rank: would-cost-a-build-cycle (a dropped or garbled `_note` would ship invisibly; the record it
  keeps is exactly the reasoning DEC-188 requires not be lost)

## J1 — can each task's `verify:` fail? (per-task table)

| Task | Can it red? | Concrete input that reds it |
|---|---|---|
| T-01 | yes | Drop the `undecodable content raises` case, or make `file_at_ref` return `""` on a bad `content` field instead of raising — the matching `has(...)` at `plan.yaml:293` finds no ok-line and exits 1. |
| T-02 | yes | Have `load_fleet` still accept a `repos[].board` key (no rejection) — `has "load_fleet rejects a repos entry carrying a board key"` (`plan.yaml:355`) finds nothing and exits 1. |
| T-03 | yes (once T-02 lands, by design) | Leave `test-factory-land.py`'s `good_fleet_dict` (`:51-61`) carrying a nested `board` key after T-02 has landed — `load_fleet` now raises `FleetError` on import/setup, the suite crashes before printing any `^ok` line, and the "$s produced no ok lines" branch (`plan.yaml:479`) reds. Ran all five listed suites this session: all five currently pass with 0 `^FAIL` lines and exit 0, matching the intent's own claim ("IT RUNS FIVE SUITES THAT PASS TODAY") — so the verify is not evergreen-pass by accident; it discriminates exactly once T-02's rejection is live, which is what `depends_on: [T-02]` encodes. |
| T-04 | yes | Leave `"Building"` as a string literal inside `derive_station` (don't parametrize on `board["stations"]`) — the file-wide grep at `plan.yaml:560` matches and exits 1. Positive control verified: `grep -qF "def derive_station" gh_board.py` (`:561`) currently succeeds, and no pre-existing false-positive quoted station name exists in the file today (checked directly — only the two intentional `"Building"`/`"Review"` literals at `:93,115,117` that this task removes). |
| T-05 | yes | Omit the `INV-26 ENDS` marker comment — the `sed -n '/INV-26 BEGINS/,/INV-26 ENDS/p'` either matches nothing (if `BEGINS` is also missing) and the positive control at `plan.yaml:697` reds, or (if only `ENDS` is missing) prints from `BEGINS` to EOF, which still contains `derive_station` so the positive control passes, but then the file-wide literal grep now scans code after INV-26 too — verified today's file has no `INV-26 BEGINS`/`ENDS` markers at all (`grep -n "INV-26\|_EXPECT\|derive_station"` above shows none), so this is a genuine, currently-absent anchor the task must add, and its absence is exactly what reds the slice. |
| T-06 | **no, for the `_note` clause alone** — the stations/owner/number/station_field checks CAN red (see F2 below for the vacuous clause and its concrete red input) | Ship `github.board.stations` with only four of the five keys, or a wrong value for one — `plan.yaml:783-787` iterates `want.items()` and fails per-key, and also checks `set(st) != set(want)`. But `"_note": ""` passes the note check unconditionally — see F2. |
| T-07 | yes | Leave `owner`/`number`/`station_field` inside the `mruangutai/kaya-ai` entry in `fleet.yaml` — `plan.yaml:850-851` checks `set(e) != {"name","default_branch"}` and the explicit `if "board" in e` check, either of which reds. |
| T-08 | yes | Fill in `github.board` with a half-populated object instead of keeping `null` — `plan.yaml:930` (`if g.get("board") is not None`) reds immediately. |
| T-09 | yes | Leave `project_id` on kaya's `master` `.harness/harness.json` — the `for dead in (...)` loop at `plan.yaml:991-993` catches it and fails. This is a live network check (`gh api ... ?ref=master`) so it also genuinely reds on a real config defect, not just a fixture. |
| T-10 | yes | Write the DEC-174 amendment text outside the `## DEC-174` … `## DEC-175` span (e.g. append it after DEC-175's heading by mistake) — `plan.yaml:1080-1083` computes `i174`/`i175` and asserts `"amendment 3" not in src[i174:i175]`, which reds. Independently, running `gen-decisions-index.py --stdout` and diffing against `DECISIONS-INDEX.md` (`plan.yaml:1092-1094`) reds on any hand-edit of the index that isn't regenerated. |

**J1 headline: one clause-level vacuity found (T-06's `_note` check, F2, negative-only) — every other
clause across all ten tasks can genuinely red**, including the rest of T-06's own verify.

## Not flagged (checked, found sound)

- T-10's `depends_on: [T-05, T-07]` looked at first glance like it should also name T-06 directly
  (DEC-196's amendment describes T-06's shipped change), but the graph enforces the ordering
  transitively: T-10 → T-05 (`plan.yaml:681`, `depends_on: [T-04]`) → T-04 (`plan.yaml:539`,
  `depends_on: [T-02, T-06]`). A redundant direct `T-10 → T-06` edge would be machinery this angle
  exists to flag, not a fix. Withdrawn.
- Repeated one-line rationale for `default_branch` staying in `fleet.yaml` (D-02, T-02 item 4, T-07
  item 2, T-09 item 4) — different executors reading different tasks; inside the stated duplication
  ceiling.
- D-06's five-key station set and D-07's explicit-null admission — both traced to concrete code
  readers / REQ-09, per the dispatch's settled-ground list; not re-litigated.
- `gen-decisions-index.py --check` non-existence — already logged as a must_fix per the dispatch;
  confirmed T-10's own `verify:` clause (`plan.yaml:1092`) correctly uses `--stdout`, not `--check`,
  so the verify itself is not affected by that defect (only the intent prose at `:1148` is, which is
  already reported).
- Anchor pre-existence, measured rather than assumed: `grep -nE '^- DEC-17[46]'
  DECISIONS-INDEX.md` shows the live DEC-174 row already spells its am-range as `am.1-am.2`
  (`:192`), confirming T-10's target anchor `am\.1-am\.3` (`plan.yaml:1095`) matches the generator's
  real row format rather than being a guessed spelling that could never green. Also grepped the four
  new-case ok-line texts (`file_at_ref:`, `validate_board accepts`, `load_board raises naming`,
  `INV-26 reports a violation`) against their target test files: zero pre-existing matches in any of
  the four, so none of the corresponding `has(...)` clauses can pass on text nobody wrote this
  feature.

## Open questions

None blocking. F1 and F2 are both flag-only, routed to `harness-pm` per the plan-surface rule.
