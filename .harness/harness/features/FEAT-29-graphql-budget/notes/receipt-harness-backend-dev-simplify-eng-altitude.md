# ALTITUDE angle — FEAT-29-graphql-budget

Scope: `git diff bee6234..8c7d7bc` (feat/FEAT-29-graphql-budget, HEAD `8c7d7bc`), read-only.

## Finding A-1: three independent hand-rolled truncation guards for the same invariant, and they already disagree

- **File/line**: `.claude/skills/harness/bin/factory_gh.py:249-261` (`project_items`, pre-existing),
  `factory_gh.py:340-370` (`project_item_stations`, **new in this diff**), and
  `factory_gh.py:565-582` (the issue `projectItems` lookup, pre-existing).
- **Summary**: the rule "never trust a GraphQL page whose `totalCount` exceeds the item count
  returned — raise loud, never default missing `totalCount` to 0" is the load-bearing invariant
  this whole feature exists to keep (it is what stops a truncated board read from reporting as an
  empty column). It is asserted three separate times in the same module, each its own copy of the
  compare-and-raise logic, and this diff's new `project_item_stations` (T-01/T-02) is a third
  restatement rather than a call into a shared check. They have already drifted: the third site
  (`:572`) validates `isinstance(total, int)` before comparing; the other two do not.
- **Cost**: a future fix to this guard — e.g. handling a non-int `totalCount`, or a GraphQL
  response that returns `totalCount` as a string — has to be found and applied in three places by
  hand. It already wasn't: the type-check present at `:572` is absent from both `:249` and
  `:340`, so a `totalCount` shaped as `"12"` currently passes the guard silently in two of the
  three call sites and is caught in the third. That is the drift the "one authoritative
  statement" test exists to catch, observed in progress, not hypothetical.
- **Alternative**: a private helper, e.g.
  `_raise_if_truncated(total, count, argv, what, value_fmt, next_step)`, called from all three
  sites, so the type check and the missing-`totalCount` check exist once.
- **Recommendation**: **briefing-row.** The full fix touches `project_items` and the issue
  `projectItems` lookup, both pre-existing code **outside this diff** — folding it in now would
  reach past the reviewed scope per this pass's own bound. The new site
  (`project_item_stations`) alone could be pointed at a new helper without touching the other two,
  but that would leave the asymmetry (2 old copies, 1 new-but-different copy) rather than remove
  it, which is worse than leaving all three as they are pending a real consolidation pass.

## Checked and cleared (no finding)

- `gh_cost_log.py`'s three wrap sites (`factory_gh.run_gh`, `gh-sync.py`'s `gh()`, and
  `measured()` itself) pass all four `harness-codebase-design` tests: deletion test (both callers
  break on import if the module goes, and the module is the sole home for opt-in gating, log-path
  resolution, argv sanitization, and the counter-read recursion guard — real, non-trivial
  behaviour, not a pass-through); no seam without variation (the two callers have genuinely
  different subprocess-call shapes — `gh-sync.py`'s omits `stdin=subprocess.DEVNULL`); tests cross
  the interface (`test-gh-cost-log.py` monkeypatches `subprocess.run` and
  `factory_config.harness_root`, never gh_cost_log internals; `test-factory-gh.py` monkeypatches
  `subprocess.run` too); adapter lifetime is explicit (`_Measurement` is `__slots__`-scoped to the
  `with` block, `.returncode` set by the caller before the `finally` reads it).
- `factory_gh.py`'s two recursion guards (`_is_rate_limit_query` for the budget-error path,
  `gh_cost_log.is_counter_call` for the counter-read path) look structurally similar but are not
  the same rule restated — different exact argv shapes (`["api","rate_limit"]` vs
  `["api","rate_limit","--jq",...]`), different modules, different purposes (constructing a loud
  GhError vs opt-in cost logging). No drift risk: consolidating them would add indirection without
  removing duplicated logic.
- The rate-limit detection markers (`_RATE_LIMIT_MARKERS`) and the budget-error construction
  (`_rate_limit_budget_error`) have exactly one call site each in `run_gh` — the right home, since
  `run_gh` is already the single place every gh failure becomes a `GhError`. `gh-sync.py`'s own
  `gh()` wrapper does not get the same enhancement, but that is pre-existing, deliberate design
  (`gh-sync.py` swallows failures into `skip()`, never raises `GhError`) untouched by this diff —
  not a bolted-on special case.
- `gh_board.py:142`'s `or {}` guard: independently reached the same conclusion as B-2 (already
  recorded) — it is unreachable from `project_item_stations`, its only producer, which always
  emits `"content": {}` never `None`. Judged, not re-flagged, per the dispatch.
- `gh_board.py:135-150`'s rewrite from raw item-dict field lookup (`field in item` /
  `field.lower()`) to `item.get("station")` removes a special case (the field-name-casing
  workaround) rather than adding one — this is the right direction, no finding.
- The COVERAGE_NOTICE-as-accepted-residual (`gh_cost_log.py:8-19,40-44`) already names its own
  compensating control (the notice is written into every log file, not just the docstring) and its
  scope is explicit (opt-in, blind to direct-Bash gh calls). Right to accept as documented; no
  deeper fix exists that doesn't reopen the "make it always-on" question already settled by
  approval amendment 5.

## Hard-bound confirmations

- Read-only: no source file edited.
- No live `gh` call made; `check-state.sh` not run; suite not run with `HARNESS_GH_COST_LOG=1`.
- `.harness/logs/gh-cost-2026-08-19.jsonl` confirmed byte-identical: `wc -c` → 39504.
- No test-file finding raised; both cited T-03 receipts (`-c3.md`, `-c4.md`) were read before
  scanning test files, per the dispatch's requirement, though this angle produced no test-file
  finding to gate against them.

## DIGEST

```yaml
VERDICT: PASS
DIGEST:
  headline: "one altitude finding — a truncation-guard invariant now hand-rolled three times in factory_gh.py, already visibly drifted (type-check present at one site, absent from the other two) — briefing-row; everything else on this angle checked clean"
  tests_added: 0
  suite: n/a
  task: none
  open_questions: []
  files_touched: []
  expertise_update: []
  findings:
    - file: ".claude/skills/harness/bin/factory_gh.py"
      lines: "249-261, 340-370, 565-582"
      summary: "the totalCount-vs-returned-count truncation guard is hand-rolled three times (project_items pre-existing, project_item_stations new in this diff, the issue projectItems lookup pre-existing); the three copies have already drifted — only the third validates isinstance(total, int)"
      cost: "a fix to the guard (e.g. handling a non-int totalCount) must be found and applied by hand in three places; it already wasn't — two of three silently accept a string totalCount"
      alternative: "extract a shared _raise_if_truncated(total, count, argv, ...) helper used by all three call sites"
      recommendation: briefing-row
      disposition: BACKLOG
      reason_out_of_bounds: "the full consolidation touches project_items and the issue projectItems lookup, both pre-existing code outside bee6234..8c7d7bc — reaches past this diff's reviewed scope"
artifact: ".harness/harness/features/FEAT-29-graphql-budget/notes/receipt-harness-backend-dev-simplify-eng-altitude.md"
```
