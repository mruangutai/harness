# T-07 complete ownership amendment research

## Conclusion

The live worktree still had executable ownership dependencies on all six legacy names. The pre-amendment T-07 file set covered the five already-repointed direct enforcement callers and four implementation-owner files, but omitted the remaining exception owners/catches, test calls, one live assignment patch, and one executed subprocess helper. T-07 now names 47 unique files, keeps its mechanical main-session-direct route and ready station, and makes the T-07 classification command a final-state contract over the fixed eleven-row historical attribution set. The controlled amendment reset plan approval from approved to pending, as required.

## Search evidence and boundaries

Read-only searches covered both live roots, `.claude/skills/harness/bin` and `tests`, with the exact-name expression `load_feature_json|FeatureJsonError|load_plan|manifest_domains|load_fleet|FleetError`, then owner-qualified and alias-qualified searches for `feature_json_write`, `harness_yaml` or `hy`, and `factory_config`, `fc`, `_fc26` or `fd.factory_config`. Separate searches covered quoted names and patch/setattr forms. The inventory below records executable Python, definitions, imports needed by those executable references, and executable strings launched as helper programs.

Comments and docstrings were not treated as executable references. The AST-detector vocabulary and synthetic raw-call source in `check-plan-routes.py` and `test-check-plan-routes.py` are recorded as `other` because they are executable audit data, but remain intentionally unchanged. Historical comparison corpus under `tests/integration/fixtures/prior-bash-write-guard.fixture`, `prior-check-domain.fixture`, `prior-check-plan-routes.py.fixture`, and `prior-harness_yaml.py.fixture` is non-live fixture data and remains unchanged. No live quoted `mock.patch` target named one of the six owners. The only live patch seam is direct attribute assignment of `harness_yaml.load_plan` in `tests/unit/test-factory-claim.py`. Every one of the six named owners had at least one external live reference; there was no symbol for which an external-reference absence had to be inferred.

“Previously named” below means present in T-07’s 18-entry file list before this amendment, not merely present in another task.

## Exact live legacy-reference inventory

### `feature_json_write.load_feature_json`

| Path and site | Class | Previously named |
|---|---|---|
| `.claude/skills/harness/bin/artifact_accessors.py:59-60`, lazy module import and delegation call | import, call | yes |
| `.claude/skills/harness/bin/feature_json_write.py:125-142`, owned definition and reader body | definition | yes |
| `.claude/skills/harness/bin/check-plan-routes.py:908`, forbidden-callee detector key | other, retained audit vocabulary | yes |
| `tests/integration/test-check-plan-routes.py:1937,1950`, synthetic source import alias and call supplied to the AST detector | other, retained raw-call mutant | yes |

There was no live production or test caller directly invoking `feature_json_write.load_feature_json` outside the `artifact_accessors` inward delegation. The external ownership dependency instead survived through `FeatureJsonError` catches and assertions below.

### `feature_json_write.FeatureJsonError`

| Path and site | Class | Previously named |
|---|---|---|
| `.claude/skills/harness/bin/feature_json_write.py:87-100`, owned exception definition; `128,132,150,160,164,181,189,196`, constructor/raise sites | definition, call | yes |
| `.claude/skills/harness/bin/factory_decompose.py:44`, module import; `119`, exception catch | import, catch | no |
| `.claude/skills/harness/bin/gh-sync.py:108`, module import; `548,773`, exception catches | import, catch | no |
| `tests/unit/test-feature-json-reader.py:19`, module import; `42,49,58,65,72,79,113,122,131,150,157,179,187,189`, exception assertions | import, catch | no |

### `harness_yaml.load_plan`

| Path and site | Class | Previously named |
|---|---|---|
| `.claude/skills/harness/bin/artifact_accessors.py:65-66`, lazy module import and delegation call | import, call | yes |
| `.claude/skills/harness/bin/harness_yaml.py:295-319`, owned definition | definition | yes |
| `.claude/skills/harness/bin/check-plan-routes.py:905`, forbidden-callee detector key | other, retained audit vocabulary | yes |
| `tests/integration/test-check-plan-routes.py:1935,1948`, synthetic source import alias and call; `1963-1965`, synthetic inward-primitive source | other, retained raw-call mutants | yes |
| `tests/integration/test-gh-sync-start-task.py:25`, module import; `555,562`, direct calls | import, call | no |
| `tests/integration/test-harness-yaml.py:814`, alias import; `817,854,887,928,972,992,1005,1029,1039`, direct calls | import, call | no |
| `tests/integration/test-plan-merge.py:2152,2456,2477`, direct calls through its existing `harness_yaml` import | call | no |
| `tests/unit/test-factory-claim.py:35`, module import; `941,949,956`, save/replace/restore assignment patch; `992,1000`, direct calls | import, patch, call | no |
| `tests/unit/test-plan-depends-on.py:171`, direct call through its existing `harness_yaml` import | call | no |

No live production caller outside `artifact_accessors` still directly called `harness_yaml.load_plan`; Main’s mechanical caller edits had already repointed the production calls. The test calls and assignment patch remained live and had to be planned.

### `harness_yaml.manifest_domains`

| Path and site | Class | Previously named |
|---|---|---|
| `.claude/skills/harness/bin/artifact_accessors.py:154-156`, lazy module import and delegation call for explicit agents | import, call | yes |
| `.claude/skills/harness/bin/harness_yaml.py:466-519`, owned definition | definition | yes |
| `.claude/skills/harness/bin/check-plan-routes.py:907`, forbidden-callee detector key | other, retained audit vocabulary | yes |
| `tests/integration/test-harness-yaml.py:188`, alias import; `191,260,401`, direct calls | import, call | no |

No other live external production call remained; Main’s mechanical edits had already repointed `bash-write-guard.py` and `check-domain.py`. Historical prior-hook fixtures remain comparison data, not callers.

### `factory_config.load_fleet`

| Path and site | Class | Previously named |
|---|---|---|
| `.claude/skills/harness/bin/artifact_accessors.py:71-72`, lazy module import and delegation call | import, call | yes |
| `.claude/skills/harness/bin/factory_config.py:161-254`, owned definition, fleet validation, and error conversion | definition | yes |
| `.claude/skills/harness/bin/check-plan-routes.py:906`, forbidden-callee detector key | other, retained audit vocabulary | yes |
| `tests/integration/test-check-plan-routes.py:1936,1949`, synthetic source import alias and call | other, retained raw-call mutant | yes |
| `tests/integration/test-worktree-terminal.py:710-713`, string executed by a Python subprocess and directly calling `factory_config.load_fleet()` | other, executable helper call | no |
| `tests/unit/test-factory-config.py:36`, alias import; calls at `145,157,226,240,284,332,355,375,591,637,658,683,708,731,756,779,801,820,852,897,921,931,969,1204` | import, call | no |
| `tests/unit/test-fleet-product-config.py:31`, alias import; calls at `143,156,180,197` | import, call | no |

No live production caller outside `artifact_accessors` still directly called `factory_config.load_fleet`; Main’s mechanical caller edits had already repointed them. The two unit suites and executed helper remained live.

### `factory_config.FleetError`

| Path and site | Class | Previously named |
|---|---|---|
| `.claude/skills/harness/bin/factory_config.py:63-70`, owned definition; raises at `75,103,107,113,122,128,148,182,186,191,200,206,213,218,227,246,265,308,315,368,403,415`; catch at `344`; CLI expected tuple at `512` | definition, call, catch, other | yes |
| `.claude/skills/harness/bin/board-station.py:57`, module import; `144`, catch | import, catch | no |
| `.claude/skills/harness/bin/board_lifecycle.py:258`, module import; `1295`, expected-exception tuple | import, other | no |
| `.claude/skills/harness/bin/check-state.py:103`, module import and `2155` alias import path; `2188`, `isinstance` exception identity check | import, other | yes |
| `.claude/skills/harness/bin/factory_claim.py:33`, module import; `456`, expected-exception tuple | import, other | no |
| `.claude/skills/harness/bin/factory_decompose.py:41`, module import; `376`, catch; `688`, expected-exception tuple | import, catch, other | no |
| `.claude/skills/harness/bin/factory_land.py:23`, module import; `124`, expected-exception tuple | import, other | no |
| `.claude/skills/harness/bin/factory_workspace.py:45`, module import; `195`, expected-exception tuple | import, other | no |
| `.claude/skills/harness/bin/feature-worktree.py:82`, catch through its existing module import | catch | no |
| `.claude/skills/harness/bin/gh-sync.py:111`, module import; `1332,2327`, catches | import, catch | no |
| `.claude/skills/harness/bin/gh_board.py:22`, module import; `78,235,269`, raises | import, call | no |
| `.claude/skills/harness/bin/plan-merge.py:119`, module import; `231`, catch | import, catch | no |
| `tests/integration/test-factory-decompose.py:32`, alias import; `366,558,857`, expected-exception tuples through `fd.factory_config` | import, other | no |
| `tests/unit/test-factory-claim.py:32`, alias import; `461`, expected-exception tuple | import, other | no |
| `tests/unit/test-factory-config.py:36`, alias import; catches at `228,242,286,305,338,357,377,417,434,450,463,474,487,501,567,596,642,715,743,763,786,841,883,927,935,1206`; expected tuples at `986,1012` | import, catch, other | no |
| `tests/unit/test-factory-land.py:25`, alias import; `252`, expected-exception tuple | import, other | no |
| `tests/unit/test-factory-workspace.py:32`, alias import; `138`, expected-exception tuple | import, other | no |
| `tests/unit/test-gh-board.py:32`, module import; `90,400,489`, catches | import, catch | no |

The behavior suites added for these production references, even where the suite did not itself spell the old owner, are `tests/integration/test-board-station.py`, `test-board-lifecycle.py`, `test-check-state-inv26.py`, `test-feature-worktree.py`, `test-gh-sync-open.py`, `test-gh-sync-record.py`, and `test-gh-sync-start-task.py`. They protect exception routing, diagnostics, bootstrap behavior, and exact caller outcomes during the mechanical owner swap.

## Fixed T-07 classification terminal set

The live classification contained eleven T-07-attributed historical rows, all of which must remain present and attributed to T-07. Their exact remedies are:

- `.claude/skills/harness/bin/bash-write-guard.py::<module>::manifest_domains#1` → `artifact_accessors.manifest_domains`
- `.claude/skills/harness/bin/check-domain.py::<module>::manifest_domains#1` → `artifact_accessors.manifest_domains`
- `.claude/skills/harness/bin/check-domain.py::domain_check::manifest_domains#1` → `artifact_accessors.manifest_domains`
- `.claude/skills/harness/bin/check-plan-routes.py::process_plan_yaml::load_plan#1` → `artifact_accessors.load_plan`
- `.claude/skills/harness/bin/check-plan-routes.py::_task_files::load_plan#1` → `artifact_accessors.load_plan`
- `.claude/skills/harness/bin/check-state.py::<module>::load_plan#1` → `artifact_accessors.load_plan`
- `.claude/skills/harness/bin/factory_config.py::load_fleet::harness_yaml_file#1` → `artifact_accessors.load_fleet`
- `.claude/skills/harness/bin/feature_json_write.py::load_feature_json::json_string#1` → `artifact_accessors.load_feature_json`
- `.claude/skills/harness/bin/harness_yaml.py::load_plan::harness_yaml_file#1` → `artifact_accessors.load_plan`
- `.claude/skills/harness/bin/harness_yaml.py::manifest_domains::harness_yaml_file#1` → `artifact_accessors.manifest_domains`
- `.claude/skills/harness/bin/post-merge-sweep.py::_repo_arg_for_segment::load_fleet#1` → `artifact_accessors.load_fleet`

The last four implementation-relocation identities remain historical rows rather than being deleted, re-keyed, or reassigned when their bodies move. The terminal checker must independently pin this eleven-row id/remedy map and reject missing rows, attribution drift, disposition/remedy drift, partial canonical/raw state, and extra raw or unresolved T-07 rows. The full audit remains the independent zero-drift check and retains raw-category, alias, unmatched-file, second-state-reader, routing, removed-scanned-file, and narrowed-discovery mutants.

## Plan amendment and controlled-writer receipts

Precondition checked before mutation: the live T-07 `verify` value exactly matched the supplied baseline:

```text
test ! -e tests/integration/canonical-reader-enforcement-baselines.json && ! grep -q -- '--verify-enforcement-bytes' tests/integration/test-check-plan-routes.py && python3 tests/integration/test-check-plan-routes.py --classification-task T-07 && python3 tests/integration/test-check-plan-routes.py && python3 .claude/skills/harness/bin/check-plan-routes.py --canonical-reader-audit && python3 tests/unit/test-artifact-accessors.py
```

One narrow `plan-merge.py apply` proposal named only `T-07.files`, `T-07.verify`, and `T-07.intent`; it carried neither task status nor approval. Exact receipt sequence and affected field identities:

```text
REPLACED T-07.files
REPLACED T-07.verify
REPLACED T-07.intent
APPROVAL-RESET: the plan was approved and its task set or a task field changed; approval.status is pending until the main session signs again
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader/.harness/harness/features/BUG-285-canonical-reader/plan.yaml
```

The three `REPLACED` stdout lines also printed the complete prior and replacement loaded values; their authoritative replacement values are the corresponding final fields in `plan.yaml`. No other task id, decision, lane, panel, feature station, or task station was named by the proposal.

The single permitted plan check exited 0 with this exact output:

```text
OK T-01 3 anchor(s) resolved
OK T-02 13 anchor(s) resolved
OK T-03 39 anchor(s) resolved
OK T-04 22 anchor(s) resolved
OK T-05 21 anchor(s) resolved
OK T-06 28 anchor(s) resolved
OK T-07 47 anchor(s) resolved
OK T-08 2 anchor(s) resolved
OK T-09 1 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader/.harness/harness/features/BUG-285-canonical-reader/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-canonical-reader: 9 task(s), 176 anchor(s) resolved, 0 failure(s)
```

## Final plan state

Post-amendment read: `approval.status` is `pending` with `reset_reason: apply T-07`; feature status remains `building`; T-07 remains `status: ready`, `change_type: bugfix`, `execution_mode: main-session-direct`, and depends only on T-06. Its 47 file anchors are unique. The original final-state verify prefix is byte-preserved and only the newly affected behavior/test dependencies were appended. The intent explicitly requires all six legacy definitions and owners to disappear without aliases, re-exports, forwarders, duplicate bodies, stale patches, or stale catches; preserves the temporary byte comparison then retirement order; and makes both the terminal T-07 contract and permanent zero-drift audit explicit.
