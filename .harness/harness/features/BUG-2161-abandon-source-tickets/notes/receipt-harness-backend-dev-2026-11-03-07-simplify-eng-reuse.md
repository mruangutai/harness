# REUSE reader — BUG-2161-abandon-source-tickets (read-only, no checks run)

Diff inspected: `git -C <PRODUCT> diff 5094e854 21bfa01d` limited to
`.claude/skills/harness/bin/gh-sync.py`, `tests/integration/test-gh-sync-abandon.py`,
`tests/unit/test-gh-sync-abandon-sources.py`. Angle: `angle-reuse.md` (code surface).

## BLUF
Production code: **empty result**. Tests: two low-severity, flag-only duplication candidates; no apply authorized.

## Production reuse (gh-sync.py) — confirmed reused, nothing re-implemented
- Sources come from existing `parse_source_issues` (gh-sync.py:474), not a new reader.
- Re-entry guard reuses `_feature_station` (gh-sync.py:318); no new station reader.
- Close/backlog/label for sources goes through the existing `close_and_reseat` closure (kind `"source"` beside `"parent"`), and the comment through existing `_post_abandon_reason` (parameterized with `what`), `_abandon_plan`/`_apply_abandon_plan` extended in place — no parallel plan/apply path.
- `--close-sources` parse is a second copy of the `--yes` boolean-flag idiom (main(), ~L2502-2511). Two copies of a 4-line idiom with 6 sibling value-flag copies of the same family; costed alternative (a boolean-flag helper) touches 8 sites for no behaviour gain. Not a finding.

## Findings (flag-only, low)
1. **tests/integration/test-gh-sync-abandon.py:831 `_fail_on`** — a third spelling of the "inject a failing `case "$*"` into FAKE_GH_STATIONS" `.replace(...)`; the earlier two are inline at :37 (`FAKE_GH_STATIONS_LABEL_FAILS`) and :796 (comment-fails). Cost: the `case "$1 $2" in` anchor string is restated in three places; a change to the fake gh script's dispatch head must be edited in lockstep, and the forgotten one silently stops injecting (the failure-path cases then pass vacuously). Alternative: define `_fail_on` once at the top of `main()` (or in `gh_sync_support.py`) and express :37 and :796 through it. kind=reuse, scope=test, severity=low.
2. **tests/integration/test-gh-sync-abandon.py:870 `_all_writes`** vs :681 `_remote_writes` — same filter (`state=closed`, `issue comment`, `issue edit`, `item-edit`), the new one adding `label create`. Cost: two write-classifier predicates must agree on what counts as a GitHub write; a new write verb added to one leaves the other's "zero writes" assertions blind. Alternative: one predicate, with `label create ` included (`_remote_writes` callers at :702/:772 assert on closes/edits and would be unaffected unless they equality-compare — verify before any apply). kind=reuse, scope=test, severity=low.

## Considered and not flagged
- Unit file `test-gh-sync-abandon-sources.py` redefines `check`, `feat_dir`, importlib loader, `write_plan`: matches the sibling `tests/unit/test-gh-sync-build-entry.py:27-45` (its docstring says so); tests/unit has no shared support module, and `gh_sync_support.py` lives under tests/integration with a different `check` output format. Importing it across suites would add a new cross-dir coupling — convention, not a finding.
- `_src_fixture` reuses `stage_station`, `install_gh`, `write_feature_json`, `read_plan_station`, `calls`, `run` from `gh_sync_support`.

## Settled set respected
D-01/D-02/D-03 behaviours not re-reviewed.

## Principles applied
- Delete First (`delete-first.md`, read): preferred collapsing duplicated fixtures/predicates over a new helper layer; no new seam proposed.

files_touched: [] (receipt excluded). No verification claimed; signed verify command not run.
