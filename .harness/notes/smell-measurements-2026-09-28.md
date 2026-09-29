# Smell measurements — `.claude/skills/harness/bin/` at e6f8493b — 2026-09-28

Re-measurement of `smell-measurements-2026-09-25.md` (4e4e50bd) after FEAT-66/67/68 (complex-function
evaluators) and #1870 (skills pass; adds `check-skill-refs.py`). Same purpose: pick the next family from
data. Script: `/tmp/smell-measure.py` (one-off; AST + `code_grade.grade_source`, bar 4). Deltas are
against the 09-25 note.

Scope: 68 `bin/*.py` (−1: render-brief.py deleted), 40,340 lines (+779).

## Long file
| lines | Δ | file |
|---|---|---|
| 4,975 | 0 | check-state.py |
| 3,854 | +116 | plan-merge.py |
| 2,872 | +288 | validate-digest.py |
| 2,631 | +237 | check-domain.py |
| 2,498 | 0 | gh-sync.py |
| 2,398 | +36 | check-plan-routes.py |
| 1,258 | +29 | board_lifecycle.py |
| 1,198 | +31 | harness_boundary.py |

11 files over 1,000 (+1); 18 over 500; top six 19,228 lines = 47% (unchanged share). The complex-function
waves **grew** the long files: decomposing a grade-1 evaluator into a driver plus named rules adds
def lines, docstrings and the rule table; nothing moved out of a file. Long-file is untouched by the
work so far.

## Long / complex function
1,891 functions (+175). Grades: 5 → 870 (+71), 4 → 892 (+114), 3 → 51 (0), 2 → 59 (+2), **1 → 19 (−12)**.
70 below bar 4 and not grade 2 (−12). 41 functions exceed 60 lines (−11); 13 exceed 100 (−10).

Grade-1 concentration (cyc / cog / abc — lines):
- factory_claim.py `_main` 41 / 74 / 107.6 — 199
- factory_decompose.py `_main` 37 / 71 / 117.2 — 225
- feature-worktree.py `cmd_remove` 27 / 50 / 75.4 — 109
- gh-sync.py `main` 39 / 50 / 104.4 — 111
- factory_gh.py `issue_stations` 16 / 47 / 35.9 — 66
- factory_gh.py `issue_board_item_id` 33 / 43 / 70.9 — 110
- check-plan-routes.py `discover_plans` 21 / 41 / 48.8 — 180
- factory_decompose.py `load_factory` 23 / 40 / 49.8 — 53
- upgrade-config.py `main` 30 / 40 / 86.6 — 129
- check-skill-refs.py `scan` 21 / 37 / 59.2 — 42 (new with #1870)
- factory_gh.py `project_item_stations` 13 / 36 / 39.4 — 79
- gh-sync.py `cmd_ship` 23 / 30 / 74.3 — 236
- wayfind.py `main` 21 / 29 / 66.2 — 95
- validate-digest.py `hook_mode` 18 / 24 / 48.5 — 129
- board-station.py `main` 20 / 23 / 55.0 — 107
- board_lifecycle.py `cmd_retitle` 14 / 21 / 47.3 — 83
- gh-sync.py `_record_pr` 19 / 21 / 47.3 — 89
- gh-sync.py `load_recorded` 19 / 20 / 47.9 — 89
- feature-record.py `main` 1 / 0 / 79.4 — 94 (ABC only: an argparse table)

10 of the 19 are CLI `main`/`_main`/`cmd_*` dispatchers (was 12); the 9 others are light
functions in factory_gh / gh-sync / check-plan-routes / validate-digest. The eleven evaluators
FEAT-66/67/68 targeted are all gone from this list; `hook_mode` dropped from 30/58 to 18/24 through
FEAT-67's `parse_digest` work without being a target.

Below-bar by file: plan-merge 8 (−1), factory_gh 6, gh-sync 5, wayfind 5, check-domain 4 (−3),
board_lifecycle 3 (−1), factory_decompose 3, observations-merge 3, validate-digest 3 (−2),
bash-write-guard 2.

## Duplicated code
Unchanged: `bash-write-guard._root` / `check-domain._root` (DEC-234 lock) and
`check-omp-port.frontmatter` / `check-skill-weight._frontmatter`. Waves 1–4 and 66–68 added none.

## Stringly-typed navigation
918 string-keyed `.get("…")` (+12); 22 nested chains. Heaviest files unchanged in order: check-state 146,
check-plan-routes 91, plan-merge 69, validate-digest 67, factory_gh 60, inflight_registry 60.
Distinct-key and top-key counts are **not** like-for-like with 09-25 (that pass also counted
`x["k"]` subscripts; this one counts `.get` only — 245 keys, top `id` 48 / `status` 45 / `github` 33).
Direction is flat: nothing landed against this family, nothing made it worse.

## Comments
5,381 lines / 40,340 = 13% (−113 lines; render-brief.py's went with it). Excluded from the pick by rule.

## Reading
- Complex-function: the evaluator half is closed; what remains is 10 dispatchers + 9 light functions,
  all in the GitHub/CLI seam (`factory_*`, `gh-sync`, `wayfind`, `board-station`), and none in an
  enforcement path. Smaller and less risky than the evaluators — but also lower value: a dispatcher's
  branches are already one-subcommand-each.
- Long-file is the family the work so far has not touched and has slightly worsened. The six files at
  47% are also the ones that carry the stringly-typed load, so a split by concept (e.g. check-state's
  invariant groups; plan-merge's subcommand families) is where "long file" and "primitive obsession"
  meet.
- Duplication is not a family here.

## Re-check at 0e03dad4 (2026-09-28, after FEAT-69 and #1967/#1976)
Same measurements, `bin/*.py` plus `bin/*/*.py` (the new `check_state/` package): 80 files, 41,085
lines (+745, of which the package split adds def/import/docstring lines only).

- Long file: check-state.py 4,975 → a 97-line entry + 12 modules (5,065 lines total, largest 927).
  Largest file is now plan-merge.py 3,854; files over 1,000: 11 → 10; top-six share 47% → 39%.
  Meanwhile validate-digest.py 2,872 → 3,120 (+248, #1967), check-domain.py 2,631 → 2,750,
  check-plan-routes.py 2,398 → 2,483 (+85, FEAT-69's package-aware lock). The observation that
  decomposition grows files still holds; only a split reverses it.
- Complex function: 1,945 functions; 5 → 891, 4 → 929, 3 → 50, 2 → 56, 1 → 19. The grade-1 list is
  unchanged in membership (`check-skill-refs.scan` 21/37/59 → 23/37/60). 40 exceed 60 lines, 13
  exceed 100. Below bar 4 including grade 2, by file: plan-merge 12, gh-sync 9, factory_gh 8,
  bash-write-guard 7, inflight_registry 7, check-domain 6, validate-digest 6.
- Duplication, stringly-typed navigation, comments: not re-measured; nothing landed against them.

Reading: wave 2 is plan-merge.py (the largest file, and the most below-bar functions). Wave 3 should
wait for FEAT-1928, which deletes validate-digest.py's text parsing and will change its size by itself.
