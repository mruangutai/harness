# FEAT-63 plan goal-check against operator intent

Authority: `/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-broad-exception-sweep-2026-09-21.md`.

> does this plan deliver the operator's stated intent?

Yes. The current cycle-1 plan delivers the operator's stated intent: all three declared perspectives pass, every settled ruling has an ordered carrier, and T-03 now ends in an executable three-command proof chain.

## Perspective grades

- **operator — pass — SC-01, SC-02; carriers T-01, T-02.** T-02 preserves the eight established checker-suite receipts against `950b2f04` and permits only the ruled, red-first INV-23 CANNOT RUN divergence; T-01 puts all twelve subprocess calls behind quiet `Ctx.spawn`, caches `gh_ok`, and reuses `git_top`. Together they cover the authority's output-stability, loud INV-23, and quiet environmental-unavailability promises.
- **code maintainer — pass — SC-03, SC-04; carriers T-01, T-02, T-03.** T-01 introduces the typed repository-module boundary and consolidates subprocess and parsed-source access; T-02 narrows every checker handler to its documented boundary and reaches zero broad catches; T-03 supplies one AST-based, per-file enforcement path that rejects increases while accepting reductions.
- **reader — pass — SC-05, SC-06; carriers T-01, T-02, T-03.** T-01 removes checker reparses and moves the DEC-138 silence rationale to the single environmental boundary; T-02 requires every other silence rationale to move byte-for-byte beside its narrowed handler; T-03 names both shared-source loaders and records the per-file broad-catch ceilings enforced by the consolidation audit.

Because every declared perspective is `pass`, the plan-exit goal-check is **PASS**. Approval remains pending, so this verdict does not authorize implementation.

## T-03 executable proof chain

T-03's `verify` is ordered by `&&` and provides the required executable proof:

1. `python3 tests/integration/test-check-state-table.py` runs the ninth checker table suite.
2. `python3 tests/integration/test-check-plan-routes.py` runs the ordinary integration suite without passing it an audit flag.
3. `python3 .claude/skills/harness/bin/check-plan-routes.py --consolidation-audit` invokes the live checker audit against the resulting tree.

Each later command runs only after the preceding command succeeds. The third command is therefore a real audit invocation, distinct from the ordinary integration suite, rather than an ignored `--consolidation-audit` argument sent to the test runner.

These planned gates and their ordering were inspected, not executed. No implementation, test, or audit result is claimed here.

## Settled-item task-graph audit

Each row below corresponds to one and only one bullet under the authority's `## Settled`; a row may need more than one task where the boundary implementation and caller cutover are necessarily separated.

| # | Settled ruling | Task-graph carrier |
|---|---|---|
| 1 | Scope is the 47 checker sites; legacy sites and hook contracts wait for wave 4. | T-02 owns all checker handlers; T-03 explicitly refuses legacy-site narrowing and hook scanning. |
| 2 | Delete invariant-body feature/harness JSON reparses and consume `Ctx` documents without a second finding. | T-01 deletes the eleven reparse sites, uses `ctx.record(feat)` and `ctx.config`, and preserves the context's single parse finding. |
| 3 | Put twelve subprocess calls behind quiet `Ctx.spawn`, cache `gh_ok`, and reuse `git_top`. | T-01 specifies all twelve calls, the two typed subprocess failures, the single DEC-138 rationale, cached auth, and removal of the second `git rev-parse`. |
| 4 | Keep INV-26 board-read silence but catch `gh_board.BoardError`. | T-02 names `board_stations_for` and `gh_board.BoardError`. |
| 5 | Convert all repository-module load failures to `RepoModuleError` while process-control exceptions propagate. | T-01 defines and tests the boundary; T-02 migrates every checker caller and preserves CANNOT RUN rendering. |
| 6 | Narrow module-level `handoff_done_when` import handling to `ImportError` while retaining the INV-17 context-load finding. | T-02 states both the exception type and retained finding. |
| 7 | Make an unavailable INV-23 `feature_schema` import report CANNOT RUN instead of using budget 300. | T-02 requires the red-first case, new line, and removal of the fallback grade. |
| 8 | Narrow `read()` to `OSError` without changing its `None` contract. | T-02 names `OSError`; T-01 separately preserves the absent-or-unreadable contract during consolidation. |
| 9 | Keep `_resolve_root`'s clean-interpreter probe and narrow it to `ImportError`. | T-02 names `ImportError`; T-01 preserves the probe behavior. |
| 10 | Make `station_of` consume the parsed plan while preserving all empty-string cases. | T-01 states both the source change and byte-for-byte semantics. |
| 11 | Narrow loud reporters to each loader or sibling module's typed boundary. | T-02 enumerates the shared error classes and requires every loud reporter to be checked against its called boundary rather than an ungrounded tuple. |
| 12 | Freeze legacy broad catches with the corrected durable census rule. | T-03 owns the single AST census and the per-file ceilings described below. |
| 13 | Preserve the sequence wave 3, then wave 4, then grader/review-skill work. | T-01 → T-02 → T-03 is explicit in `depends_on`; T-03 forbids legacy rewrites, hooks, grader rules, and review-skill changes. |
| 14 | Add both the shared-source-loader lock and the zero checker broad-catch lock, red-first with mutants. | T-03 adds both loader names, one zero checker entry in the common census, and isolated mutants for both handler syntaxes and both loaders. |
| 15 | Hold eight suite receipts byte-identical except the ruled INV-23 divergence; no newly visible skip is allowed. | T-02 records baseline command/status/stream digests, compares post-change receipts, and fails any unruled difference or disappeared row. |
| 16 | Move silence comments with their code without rewording. | T-01 moves the DEC-138 rationale byte-for-byte to `Ctx.spawn`; T-02 moves every remaining rationale byte-for-byte with its handler. |
| 17 | Execute the build main-session-direct under DEC-174. | T-01, T-02, and T-03 all declare `execution_mode: main-session-direct` with DEC-174 reasons. |

## Durable AST census ruling

The authoritative baseline is **118** broad handlers outside `check-state.py` at `950b2f04`, counted by AST as handlers typed exactly `Exception` or bare `except:`. The earlier **121** was a superseded text-grep count that included comment mentions and is not a planning input.

T-03 correctly implements the durable form rather than pinning a stale aggregate: unchanged non-check-state `bin/` scripts receive their authoritative per-file `950b2f04` ceilings; `check-state.py` receives a zero ceiling; `harness_boundary.py` receives the count observed from the **post-T-01** tree when the lock lands; absent or new scripts receive zero; decreases pass and per-file increases fail. It explicitly does not force `harness_boundary.py` to four and does not assert a fixed aggregate total after T-01.

## Remaining authority checks

The two items left open during grilling are resolved without changing scope: T-01 leaves each command's timeout at its call site, and D-02/T-01 make `RepoModuleError` retain and render the original exception type and text where receipts require it. The plan also preserves all three exclusions: it does not narrow the 118 legacy sites, does not turn environmental silence into findings, and does not extend the grader or review-skill rubric.
