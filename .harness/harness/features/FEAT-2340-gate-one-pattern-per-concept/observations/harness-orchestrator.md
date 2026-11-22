# Observations — harness-orchestrator — FEAT-2340-gate-one-pattern-per-concept

- 2026-11-22: First-cycle instantiation: templates copied via cp are refused by bash-write-guard (outside domain by shell); the Write tool with the template content lands, and the template's branch value must be corrected to feat/<FEAT> through feature_json_write.write_feature_json since feature-record.py has no branch verb.
- 2026-11-22: check-state.py --feature from a worktree cwd still resolves the project-root corpus and reports the worktree feature as absent at exit 0; the --changed feedback printed by feature-record.py/plan-merge.py is the usable per-write audit inside a worktree.
- 2026-11-22: handoff_done_when brief-sc: resolver only matches `SC-NN:` line starts; a by-perspective BRIEF writes `- SC-NN (perspective):`, so brief-sc pointers are unusable there — cite brief-perspective only.
- 2026-11-22: pin-review has a real verb now (feature-record.py pin-review --sha); the seam/pin/status-review/commit/re-pin/commit sequence held with an empty code diff between seam bca0980d and pin 125a04f8.
- 2026-11-22: a fully main-session-direct plan makes INV-17 exempt the feature from handoff notes; writing handoff-build seq-1 anyway was accepted and let run-start carry the succession judgement.
