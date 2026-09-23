# Research — FEAT-64 broad exception libraries and tools

## Scope reconciled

The settled grilling artifact divides wave 4 into FEAT-64 libraries and tools, then FEAT-65 hooks. At baseline `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983`, FEAT-64 owns 43 broad catches: 24 in the shared-library set and 19 in the tool set. `factory_gh.py` is the tenth shared library even though it has no broad handler: it must convert JSON and process failures into `GhError` so `board-station.py` can narrow its consumer catch.

GitHub backlog intake found no open issue that supplies this feature. Issue #1882 is explicitly excluded by the grilling ruling, so `source_issues` remains empty.

## Shared-library inventory

| File | Baseline broad catches | Boundary work |
|---|---:|---|
| `factory_decompose.py` | 1 | `extract_brief` keeps its never-block publishing contract for read/decode failures only. |
| `factory_gh.py` | 0 | `run_gh` converts subprocess and JSON-access failures to `GhError`, preserving its diagnostic text and exception chain. |
| `feature_schema.py` | 1 | `recovery_command_for` catches the plan accessor's typed parse/schema failure. |
| `gh_cost_log.py` | 2 | `_read_counter` narrows process and integer-parse failures; `record` narrows filesystem, encoding, and JSON-serialization failures while staying best-effort. |
| `handoff_done_when.py` | 2 | `_satisfied` and `_resolution_problems` catch only typed authority/read/parse failures; already parsed plan authority is carried forward instead of loaded again. |
| `handoff_policy.py` | 1 | `_plan_mapping` catches the plan loader's typed failure and preserves its parenthetical bytes. |
| `harness_boundary.py` | 6 | Narrow pointer, fleet, owner, and manifest reads; consolidate `load_repo_module` and `call_repo_module` through one `RepoModuleError` catch; add the second and only other broad catch in unwired `hook_guard`. |
| `harness_yaml.py` | 3 | `load_str` catches documented parser/runtime classes and rethrows `YamlParseError`; bootstrap helpers narrow root and courtesy-channel failures while retaining their silence rationales. |
| `run_identity.py` | 1 | `record_seed` catches only temp-file, filesystem, encoding, and JSON-serialization failures and keeps cleanup. |
| `worktree_terminal.py` | 7 | Git calls, fleet access, repo resolution, landed JSON/YAML parsing, and cross-repository classification catch the typed errors of their actual boundaries; delete the exception-type-name probe in favor of the exported YAML class. |

The final shared count is two, both in `harness_boundary.py`. The existing two repository-module catches become one shared execution wrapper rather than two residual allowances. `hook_guard` is added with success-result preservation, fail-open/fail-closed status selection, and `Exception` rather than `BaseException`; no hook caller changes in FEAT-64, so FEAT-65 retains ownership of exact per-hook rendered bytes.

## Tool inventory

| File | Baseline broad catches | Boundary work |
|---|---:|---|
| `board-station.py` | 1 | Catch `gh_board.BoardError` and `factory_gh.GhError` after the producer boundary is typed; keep the current best-effort exit and diagnostic. |
| `check-omp-port.py` | 4 | Narrow runtime-pin reads/parses, harness config access, frontmatter reads, and provider overlay reads to filesystem, Unicode, JSON/YAML, value, and accessor errors. |
| `check-plan-routes.py` | 2 | Narrow manifest comparison to typed config/access failures and stop `_is_shipped` reparsing a plan already available to discovery; it consumes the parsed status. |
| `check-skill-weight.py` | 1 | Narrow frontmatter reads to filesystem, Unicode, and accessor parse failures while retaining the per-agent error row. |
| `gh-sync.py` | 3 | Catch the board/GitHub/accessor typed errors in board station reads, child reads, and ship audit; preserve all card movement, error text, and exit behavior. |
| `post-merge-sweep.py` | 5 | Narrow main-checkout resolution, fleet lookup, receipt reads, and record handling to their process/accessor errors; unexpected programming defects leave the former outer success catch rather than being reported as an environmental skip. |
| `run-unit-tests.py` | 2 | Narrow root bootstrap and suite-layout rendering failures without changing the DEC-234 prologue or its reciprocal comment. |
| `upgrade-config.py` | 1 | Catch the config accessor's typed read/parse error and preserve the current exit-1 line. |

All eight tools end at zero broad catches. The hook scripts and `.omp/extensions/harness-hooks.ts` are deliberately absent from the plan.

## Verification topology

T-01 owns all ten libraries and their focused suites. T-02 depends on T-01, consumes the typed producers, and owns seven tools plus their focused suites. T-03 runs last and owns `check-plan-routes.py`, the unit census, integration mutants, and the two evidence ledgers. This ownership keeps every file in one task while allowing the final task to ratchet the scoped ceilings after the new boundary shape exists.

The receipt corpus is the named `test-harness-boundary`, both `test-harness-yaml` suites, `test-worktree-terminal`, `test-inflight-registry`, `test-post-merge-sweep`, six `test-gh-sync` suites, `test-check-omp-port`, both `test-run-unit-tests` suites, `test-check-plan-routes`, and each singleton's matching suite. The implementation records command, exit, stdout digest, and stderr digest for baseline and candidate. A difference not listed with exact old/new bytes in `notes/build-divergences.md` fails the task.

The red-first ledger must contain natural failing cases for each automated success criterion plus controlled catch-increase and duplicate-reparse mutants. The census changes only FEAT-64 entries: scoped library/tool files become zero, `harness_boundary.py` becomes two, and hook ceilings remain at their baseline until FEAT-65.

## Decisions carried into the plan

1. Typed producer boundaries precede consumer narrowing. This prevents consumers from reconstructing JSON, subprocess, fleet, or YAML failure taxonomies.
2. `harness_boundary.py` is the sole broad-catch home: one repository-module execution catch and one unwired hook guard. Consolidating load and call execution is required to reach exactly two.
3. Byte identity is the default. A behavioral difference is legal only after a failing test and a ledger entry with exact bytes and ruling.
4. The census ratchets only this feature's files. FEAT-65 hook ceilings stay unchanged, avoiding a gate that requires excluded work.

## Principles applied

- Outcome-Oriented Execution: tasks are sliced by independently verifiable outcomes and file ownership, not by generic coding phases. The producer boundary lands before consumer cutover, and the final census/receipt task can falsify the promised catch counts and byte identity without depending on a later hook feature.
- The plan uses the weakest sufficient specification: it fixes observable outputs, error types at named seams, catch counts, and mutation proofs while leaving FEAT-65's unsettled per-hook message formatting to the feature that wires those messages.
