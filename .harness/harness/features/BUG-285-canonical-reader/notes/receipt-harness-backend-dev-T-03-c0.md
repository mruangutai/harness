# T-03 receipt — BLOCKED

T-03 cannot perform the required semantic cutover without a plan amendment. The checked-in complete classification assigns `.claude/skills/harness/bin/factory_config.py::product_config::json_string#1` to T-03 but names its remedy `documented source route` (`tests/integration/canonical-reader-classification.json:821-831`). That is not a public `artifact_accessors` accessor, while the signed task requires every assigned row to cross that seam using its row's named accessor.

Pre-edit checks completed: the T-03 id and verify chain in `plan.yaml:220-275` exactly match the dispatch; all 34 classified T-03 rows have existing source files; and their source files are listed under T-03. Classified IDs are the 34 `task == "T-03"` rows in `tests/integration/canonical-reader-classification.json`, including the blocking `factory_config.py::product_config::json_string#1`. No source or test files were edited and no tests were run because the mandatory pre-edit predicate failed; the exact signed verify command therefore has exit code n/a.

Required amendment: classify the remote `harness.json` payload with a concrete public accessor (and state its required contract), or explicitly exempt/reassign the row. Then redispatch T-03.
