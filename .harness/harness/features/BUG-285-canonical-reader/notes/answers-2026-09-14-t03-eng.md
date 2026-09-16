# Operator answers — 2026-09-14-t03-eng

## Remote harness.json source

Question: `factory_config.product_config()` receives a remote repository's `.harness/harness.json` as decoded text from GitHub's Contents API, while the signed `load_harness_json` contract accepts only a filesystem path. Should the plan add an in-memory route, add a separate accessor, or exempt this reader?

Answer: Amend T-02 and T-03 so `load_harness_json` accepts an explicit keyword-only in-memory text source mode. Path and text are mutually exclusive and use the same strict parser and error contract. Do not add a second public accessor and do not exempt the remote reader.

Approved by: mruangutai
Date: 2026-09-14
