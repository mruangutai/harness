# Operator answers — 2026-09-15-t03-eng

## GitHub arrays and remote feature.json text

Question: The signed accessor contracts do not cover two live T-03 source shapes: GitHub list commands return valid JSON arrays while `parse_gh_json` requires a mapping, and `worktree_terminal._read_landed_feature_json()` receives decoded `feature.json` text from `git show` while `load_feature_json` accepts only a path. Should the existing accessors be generalized, separate shape/source accessors be added, or these readers be exempted?

Answer: Generalize the existing accessors. `parse_gh_json` must return any valid strict JSON value while each consumer validates the mapping, list, or scalar shape it requires. `load_feature_json` must gain an explicit keyword-only text source mode; path and text are mutually exclusive and use the same strict parser and typed-error contract. Do not add separate public accessors, exemptions, or temporary-file bridges.

Approved by: mruangutai
Date: 2026-09-14
