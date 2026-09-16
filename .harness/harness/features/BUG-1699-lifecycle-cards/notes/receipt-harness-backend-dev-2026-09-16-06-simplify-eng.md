# REUSE inspection — BUG-1699 lifecycle cards

## Conclusion

No substantive newly introduced reimplementation has an importable existing authority in committed product diff `60b8d4d99f50edab6a63352ea43ebbc4ffc09750..212ad9ca`.

## Findings

[]

## Inspection pointers

- The active-card placement policy is centralized in `gh_board.project` (`.claude/skills/harness/bin/gh_board.py:126-150`); its new consumers delegate to it in `gh-sync.py:1304-1342, 1527-1529`, `board_lifecycle.py:488-529`, and `check-state.py:2323-2328` rather than reconstruct it.
- Lifecycle vocabulary uses the existing `factory_config` authority where a complete vocabulary is required (`gh_board.py:133`, `gh-sync.py:138`, `board_lifecycle.py:466-483`, `check-state.py:105-106`); the active-phase subsets are context-specific filters, not duplicate vocabulary authorities.
- Resume classification is a single local policy in `plan-merge.py:843-865`, reused by its reset path (`plan-merge.py:903-922`); signing only reads and validates its recorded result (`plan-merge.py:2027-2038, 2115-2134`).
- The paired `.omp` command sources and generated `.claude` adapters are documented generated artifacts, not separately importable implementations (`.omp/commands/harness-plan.md`, `.omp/commands/harness-patch.md`, `.claude/commands/harness-plan.md`, `.claude/commands/harness-patch.md`).

Settled lifecycle decisions and the sanctioned digest-contract repair were not assessed as REUSE findings.
