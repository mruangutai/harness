# T-03 receipt — BLOCKED

T-03 cannot safely migrate all 36 live classified rows with the existing public accessor interfaces: three checked-in remedies reject legitimate consumer payload shapes.

## Pre-edit classification predicate

- All 36 `task: T-03` rows are `disposition: migrate`, `execution_route: team`, name an existing source path, and have a T-03 plan target/test route.
- The signed amendment resolves `factory_config.product_config` specifically: `load_harness_json(text=<remote decoded text>, context=<remote location>)` is compatible with its input.
- The predicate fails for these existing rows:
  - `gh-sync.py::_record_pr::json_string#1`: its `gh pr list --json number` result is a JSON array, while `artifact_accessors.parse_gh_json` rejects every non-mapping at `artifact_accessors.py:128-130`.
  - `gh-sync.py::cmd_ship.first_open_child::json_string#1`: its `sub_issues` output is likewise a JSON array, rejected by that accessor.
  - `worktree_terminal.py::_read_landed_feature_json::json_string#1`: it has decoded in-memory `feature.json` text, while the assigned `load_feature_json` interface only accepts a path (`artifact_accessors.py:54-57`).

No compliant use of the listed remedies preserves these consumers' successful array/text behavior without expanding an accessor or adding an adapter, both outside the signed T-02/T-03 contract.

## Fail-first evidence

Command run before any production edit:

```sh
python3 tests/unit/test-factory-config.py
```

Exit status: `1`

Relevant verbatim failures from the focused run after adding the temporary consumer regression:

```text
FAIL  product_config refuses remote duplicate key through its harness.json boundary
        did not raise
FAIL  product_config refuses remote non-finite value through its harness.json boundary
        did not raise

2 of 117 FAILING.
```

The temporary test-only red change was removed after the predicate blocker; no production edit was made and the exact signed T-03 verify was not run because implementation cannot begin under the contract.

## Scope exclusions

No T-04/T-07 mechanical reader relocation, direct-enforcement work, classification data/machinery, formatter, linter, build, broad suite, or commit was performed.
