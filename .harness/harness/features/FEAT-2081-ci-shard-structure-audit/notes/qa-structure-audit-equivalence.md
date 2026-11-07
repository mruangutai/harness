# QA — structure-audit equivalence and single-pass traversal (FEAT-2081 T-03, SC-06/SC-08/SC-10)

One-time local build evidence (plan amendment F1). Nothing here is a permanent test, suite helper
or CI step; the baseline checker was extracted only for this proof and its worktree removed after.

## Pins
- Baseline (pre-change) checker: `8e0b9e900986d4e0e07414ffedb1c09a2a6a7554`, provisioned with
  `git worktree add --detach /tmp/feat2081-base 8e0b9e90…` (removed afterwards with `git worktree remove`).
  `check-plan-routes.py` sha256 prefix `cfe27a19ad3e5156` (byte-identical to the worktree file at HEAD ad119cb8 before T-03).
- Post-change checker: worktree `feat/FEAT-2081-ci-shard-structure-audit` at HEAD `ad119cb8` + uncommitted T-03 diff,
  `check-plan-routes.py` sha256 prefix `608c6446013d6862`.
- Host: Apple M3 Pro, 12 cores, macOS, Python 3.14.5.

## Equivalence proof (old vs new, both entry paths, every input)
Instrument: `/tmp/feat2081-equiv/equiv.py` (throwaway). It loads the post-change
`tests/integration/test-checker-structure-locks.py`, replaces its `cpr()` with a proxy, and runs every
case in `CASES` (process pool, spawn). Every time a case hands a tree to `consolidation_findings` or
`feat62_findings`, the proxy audits that same tree with BOTH checkers through:
1. the in-process public calls (`consolidation_findings` → also `feat62_findings` and
   `broad_catch_findings`; `feat62_findings` → also `broad_catch_findings`), comparing the returned list
   (order included, or the raised exception) plus captured stdout and stderr;
2. the CLI `python3 check-plan-routes.py --consolidation-audit` with `HARNESS_PROJECT_DIR=<that tree>`
   (marker `.harness/team-config.yaml` added for the CLI run only when absent, then deleted), comparing
   exit status, stdout and stderr byte-for-byte.
The real source tree (the worktree root) is input #1. The proxy returns the post-change result to the
case, so the suite's own assertions also ran: `suite_failures=[]`.

Command: `WT=<worktree> BASE_BIN=/tmp/feat2081-base/.claude/skills/harness/bin/check-plan-routes.py python3 /tmp/feat2081-equiv/equiv.py records.json`
Result (run after the final code change): `inputs=53 non_identical=[] suite_failures=[]`, exit 0.

Columns: case (`<CASES function>#<nth call>`), entry the suite called, finding counts per in-process
call (identical old/new), CLI exit, CLI summary line, all-identical.

| input | suite entry | in-process findings (old = new) | CLI exit | CLI summary | identical |
|---|---|---|---|---|---|
| real_tree | consolidation_findings | consolidation_findings=0, broad_catch_findings=0, feat62_findings=0 | 0 | 0 consolidation finding(s) under bin/ | yes |
| case_feat61_station_lock#1 | consolidation_findings | consolidation_findings=0, broad_catch_findings=0, feat62_findings=0 | 0 | 0 consolidation finding(s) under bin/ | yes |
| case_feat61_station_lock#2 | consolidation_findings | consolidation_findings=1, broad_catch_findings=0, feat62_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat61_station_lock#3 | consolidation_findings | consolidation_findings=2, broad_catch_findings=0, feat62_findings=0 | 1 | 2 consolidation finding(s) under bin/ | yes |
| case_feat61_station_lock#4 | consolidation_findings | consolidation_findings=0, broad_catch_findings=0, feat62_findings=0 | 0 | 0 consolidation finding(s) under bin/ | yes |
| case_feat61_loader_lock#1 | consolidation_findings | consolidation_findings=1, broad_catch_findings=0, feat62_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_module_body_lock#1 | feat62_findings | feat62_findings=0, broad_catch_findings=0 | 0 | 0 consolidation finding(s) under bin/ | yes |
| case_feat62_module_body_lock#2 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_module_body_lock#3 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_module_body_lock#4 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_module_body_lock#5 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_module_body_lock#6 | feat62_findings | feat62_findings=2, broad_catch_findings=0 | 1 | 2 consolidation finding(s) under bin/ | yes |
| case_feat62_reads_lock#1 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_reads_lock#2 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_reads_lock#3 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_reads_lock#4 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_reads_lock#5 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_reads_lock#6 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_reads_lock#7 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_reads_lock#8 | feat62_findings | feat62_findings=0, broad_catch_findings=0 | 0 | 0 consolidation finding(s) under bin/ | yes |
| case_feat62_reads_lock#9 | feat62_findings | feat62_findings=2, broad_catch_findings=0 | 1 | 2 consolidation finding(s) under bin/ | yes |
| case_feat62_authority_audit#1 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_authority_audit#2 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_authority_audit#3 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_authority_audit#4 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_changed_posture#1 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat62_changed_posture#2 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat63_reparse_lock_covers_both_json_loaders#1 | feat62_findings | feat62_findings=2, broad_catch_findings=0 | 1 | 2 consolidation finding(s) under bin/ | yes |
| case_feat63_reparse_lock_covers_both_json_loaders#2 | feat62_findings | feat62_findings=2, broad_catch_findings=0 | 1 | 2 consolidation finding(s) under bin/ | yes |
| case_feat63_broad_catch_census#1 | feat62_findings | feat62_findings=0, broad_catch_findings=0 | 0 | 0 consolidation finding(s) under bin/ | yes |
| case_feat63_broad_catch_census#2 | feat62_findings | feat62_findings=1, broad_catch_findings=1 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat63_broad_catch_census#3 | feat62_findings | feat62_findings=1, broad_catch_findings=1 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat63_broad_catch_census#4 | feat62_findings | feat62_findings=1, broad_catch_findings=1 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat63_broad_catch_census#5 | feat62_findings | feat62_findings=0, broad_catch_findings=0 | 0 | 0 consolidation finding(s) under bin/ | yes |
| case_feat63_broad_catch_census#6 | feat62_findings | feat62_findings=1, broad_catch_findings=1 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat63_broad_catch_census#7 | feat62_findings | feat62_findings=1, broad_catch_findings=1 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat63_broad_catch_census#8 | feat62_findings | feat62_findings=1, broad_catch_findings=1 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat64_broad_catch_census_wave4#1 | feat62_findings | feat62_findings=1, broad_catch_findings=1 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat64_broad_catch_census_wave4#2 | feat62_findings | feat62_findings=1, broad_catch_findings=1 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat64_broad_catch_census_wave4#3 | feat62_findings | feat62_findings=1, broad_catch_findings=1 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat64_broad_catch_census_wave4#4 | feat62_findings | feat62_findings=1, broad_catch_findings=1 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat64_broad_catch_census_wave4#5 | feat62_findings | feat62_findings=1, broad_catch_findings=1 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat64_broad_catch_census_wave4#6 | feat62_findings | feat62_findings=0, broad_catch_findings=0 | 0 | 0 consolidation finding(s) under bin/ | yes |
| case_feat69_package_lock#1 | feat62_findings | feat62_findings=0, broad_catch_findings=0 | 0 | 0 consolidation finding(s) under bin/ | yes |
| case_feat69_package_lock#2 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat69_package_lock#3 | feat62_findings | feat62_findings=2, broad_catch_findings=0 | 1 | 2 consolidation finding(s) under bin/ | yes |
| case_feat69_package_lock#4 | feat62_findings | feat62_findings=2, broad_catch_findings=0 | 1 | 2 consolidation finding(s) under bin/ | yes |
| case_feat69_package_lock#5 | feat62_findings | feat62_findings=5, broad_catch_findings=0 | 1 | 5 consolidation finding(s) under bin/ | yes |
| case_feat69_package_lock#6 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat69_package_lock#7 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat69_package_lock#8 | feat62_findings | feat62_findings=1, broad_catch_findings=0 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat69_package_lock#9 | feat62_findings | feat62_findings=1, broad_catch_findings=1 | 1 | 1 consolidation finding(s) under bin/ | yes |
| case_feat69_package_lock#10 | feat62_findings | feat62_findings=1, broad_catch_findings=1 | 1 | 1 consolidation finding(s) under bin/ | yes |

Error/early-return branches covered by these inputs include: the absent decisions index (authority
CANNOT RUN), struck and unresolvable authorities, mutant-only findings for every lock family (station
literal, drifted bucket, second loader, module body, reparse ×3 loaders, undeclared reads ×N, family
placement/alias/unclaimed, posture workflow/hook, broad-catch ceilings for check-state, family module,
harness_boundary up/down, newcomer, hook, wave-4 zero-ceiling files).

## Traversal counts (instrumented; same fixture tree)
Instrument: `tests/integration/test-structure-audit-single-pass.py` (`Traversal` wraps `ast.parse` and
`ast.iter_child_nodes`; expected visits = node occurrences in every parsed tree). Fixture: isolated copy
of the checked-out bin/, decisions index, workflows, hooks, marker, plus one embedded-program fixture.

| entry path | checker | parsed trees | node occurrences | child-node visits | nodes not visited exactly once | re-parsed sources |
|---|---|---|---|---|---|---|
| in-process `consolidation_findings` | pre (8e0b9e90) | 210 | 432491 | 557328 | 30442 | check-state.py + all 12 check_state/*.py, embedded ×2 |
| in-process `consolidation_findings` | post | 99 | 202781 | 202781 | 0 | none |
| in-process `feat62_findings` | pre | 113 | 229815 | 333251 | 17327 | embedded ×2 |
| in-process `feat62_findings` | post | 99 | 202781 | 202781 | 0 | none |
| in-process `broad_catch_findings` | pre | 100 | 202779 | 202786 | 7 | embedded ×2 |
| in-process `broad_catch_findings` | post | 99 | 202781 | 202781 | 0 | none |
| CLI `--consolidation-audit` | pre | 210 | 432491 | 557328 | 30442 | check-state.py + check_state/*, embedded ×2 |
| CLI `--consolidation-audit` | post | 99 | 202781 | 202781 | 0 | none |

(Pre-change: the reader census, the FEAT-62 checker surface and the broad-catch census each parse their
own copy, so check-state.py and check_state/*.py are parsed three times per consolidation call and every
other bin/ file twice; each copy is then walked by several rules. Both runs audit the worktree's own
bin/ copied into the fixture — the fixture is independent of CHECK_PLAN_ROUTES_BIN — and the red run was
taken before the final index optimisation edit, so the audited tree's node total differs by 2.)

## Red-first receipt — permanent single-pass check against the pre-change checker
`CHECK_PLAN_ROUTES_BIN=/tmp/feat2081-base/.claude/skills/harness/bin/check-plan-routes.py python3 tests/integration/test-structure-audit-single-pass.py` → **exit 1**, 9 failures:
```
COUNTS in_process_consolidation_findings {"embedded": 2, "foreign": 0, "nodes": 432491, "not_once": 30442, "reparsed": [".claude/skills/harness/bin/check-state.py", ".claude/skills/harness/bin/check_state/__init__.py", ".claude/skills/harness/bin/check_state/board.py", ".claude/skills/harness/bin/ch
FAIL in_process_consolidation_findings_every_node_visited_exactly_once 30442 node(s) not visited once; 557328 visits over 432491 nodes
FAIL in_process_consolidation_findings_parses_no_source_twice .claude/skills/harness/bin/check-state.py, .claude/skills/harness/bin/check_state/__init__.py, .claude/skills/harness/bin/check_state/board.py, .claude/skills/harness/bin/check_state/brief.py, .claude/skills/harness/bin/check_state/ctx.py
COUNTS in_process_feat62_findings {"embedded": 2, "foreign": 0, "nodes": 229815, "not_once": 17327, "reparsed": ["<unknown>", "<unknown>"], "trees": 113, "visits": 333251}
FAIL in_process_feat62_findings_every_node_visited_exactly_once 17327 node(s) not visited once; 333251 visits over 229815 nodes
FAIL in_process_feat62_findings_parses_no_source_twice <unknown>, <unknown>
COUNTS in_process_broad_catch_findings {"embedded": 2, "foreign": 0, "nodes": 202779, "not_once": 7, "reparsed": ["<unknown>", "<unknown>"], "trees": 100, "visits": 202786}
FAIL in_process_broad_catch_findings_every_node_visited_exactly_once 7 node(s) not visited once; 202786 visits over 202779 nodes
FAIL in_process_broad_catch_findings_parses_no_source_twice <unknown>, <unknown>
FAIL in_process_broad_catch_findings_parses_the_overlapping_checker_sources .claude/skills/harness/bin/check-state.py, .claude/skills/harness/bin/check_state/table.py
COUNTS cli_consolidation_audit {"embedded": 2, "exit": 0, "foreign": 0, "nodes": 432491, "not_once": 30442, "reparsed": [".claude/skills/harness/bin/check-state.py", ".claude/skills/harness/bin/check_state/__init__.py", ".claude/skills/harness/bin/check_state/board.py", ".claude/skills/harness/bin/c
FAIL cli_consolidation_audit_every_node_visited_exactly_once 30442 node(s) not visited once; 557328 visits over 432491 nodes
FAIL cli_consolidation_audit_parses_no_source_twice .claude/skills/harness/bin/check-state.py, .claude/skills/harness/bin/check_state/__init__.py, .claude/skills/harness/bin/check_state/board.py, .claude/skills/harness/bin/check_state/brief.py, .claude/skills/harness/bin/check_state/ctx.py, .claude/
```
Green against the post-change checker: `python3 tests/integration/test-structure-audit-single-pass.py` → **exit 0**, ALL PASS:
```
COUNTS in_process_consolidation_findings {"embedded": 1, "foreign": 0, "nodes": 202781, "not_once": 0, "reparsed": [], "trees": 99, "visits": 202781}
COUNTS in_process_feat62_findings {"embedded": 1, "foreign": 0, "nodes": 202781, "not_once": 0, "reparsed": [], "trees": 99, "visits": 202781}
COUNTS in_process_broad_catch_findings {"embedded": 1, "foreign": 0, "nodes": 202781, "not_once": 0, "reparsed": [], "trees": 99, "visits": 202781}
COUNTS cli_consolidation_audit {"embedded": 1, "exit": 0, "foreign": 0, "nodes": 202781, "not_once": 0, "reparsed": [], "trees": 99, "visits": 202781}
```

## Controlled wall time (same host, same corpus, 3 alternating runs; SC-10 timing is a separate record)
`/tmp/feat2081-equiv/timing.sh`: baseline commands run inside the 8e0b9e90 worktree (its own tree,
its own pre-change test file WITH the test-only `_PARSED` cache); post commands inside the feature worktree.

| command | pre runs | pre median | post runs | post median |
|---|---|---|---|---|
| `check-plan-routes.py --consolidation-audit` | 0.68 / 0.66 / 0.66 s | 0.66 s | 0.38 / 0.39 / 0.38 s | 0.38 s |
| `tests/integration/test-checker-structure-locks.py` | 3.16 / 3.33 / 3.09 s | 3.16 s | 4.42 / 4.35 / 4.26 s | 4.35 s |

**Open issue (SC-10):** the CLI median drops 42%, but the structure-locks test is SLOWER after the
plan-mandated removal of its test-only `_PARSED/_cached_parse` cache. That cache shared every parsed tree
across the ~50 mutant copies inside a worker, so the old suite paid parsing once per worker; production
now parses each file once per invocation (≈0.14 s of a ≈0.32 s consolidation call; the index itself is
≈0.10 s, within 30% of a bare `ast.walk`). A lower locks-test median would need either keeping a
cross-invocation parse cache (forbidden by the plan) or not parsing files the census must count (forbidden).
Decision for Main/PM: SC-10's locks-test threshold vs T-03's cache-removal clause.
