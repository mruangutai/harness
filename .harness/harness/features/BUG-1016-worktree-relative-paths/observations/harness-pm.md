# Observations — harness-pm — BUG-1016-worktree-relative-paths

- 2026-10-04: inflight_registry.py.feature_root catches AmbiguousWorktree and falls back to owner_root, while _feature_root_command reports ambiguity and exits 1. Relative-path planning must specify the CLI through PolicyRunner and refusal on its reason, not the convenience helper; source anchors inflight_registry.py#feature_root and inflight_registry.py#_feature_root_command. The OMP PolicyRunner maps exit 1 to blocked false with a reason, so testing blocked alone would accept an ambiguous lookup.
