# FEAT-2397 c1 fix — T-05 doctrine — FixC1_Doctrine — 2026-11-22

Contract: `notes/answers-2026-11-22-c0-escalations.md` (Q1(a), Q2, the c1 batch item 1), code reviewer c0 finding 2.

| Finding | Before | After |
|---|---|---|
| SC-08 index tails (reviewer #2) | 23 amend/strike tails kept Claude `skills:`, `hookSpecificOutput.additionalContext`, concurrency 20, `settings.json`/INV-9, dispatch-guard model refusal, `non-omp claims expire`; DEC-111 unmarked; no plan-local successor | All 23 rewritten to the native contract, ≤30 words each (max checked with `awk NF`), every D-NN row cites `FEAT-2397-omp-native-cleanup, .harness/harness/features/FEAT-2397-omp-native-cleanup/plan.yaml, decisions[id=D-NN]`; DEC-111 = "STRUCK under DEC-188 … successor DEC-233". No cite had to be dropped. |
| SPEC §4 spawn policy (808-813) | dispatch-guard "checks … model and name overrides" | checks `name:`, authored lineage fields, feature marker, run/claim state; per-call `model` refused natively by `task.perCallModel: "off"` (DEC-155) |
| DEC-214 (7117-7118) | `dispatch-guard.py:77-79` … `tool_input.prompt` | `dispatch-guard.py`'s feature-marker comment … the task text, `tool_input.task` (what `dispatch-guard.py:243` reads) |
| Q1(a) bin comments | spelled the project-root variable | "the Harness project-root environment override" (check-plan-routes.py:718, check_state/ctx.py:295, check_state/worktrees.py:112); comments only |
| Q2 `.omp/commands/harness.md` §3 | "One blocking `task` call … holds until the orchestrator returns" | one `task` call with `agent: harness-orchestrator` running in the background (DEC-204); Main ends its turn, result injected; rest unchanged |
| t05-doctrine.md | false completion claims | dated correction section appended |

Evidence (run with HARNESS_AGENT_TYPE/CLAUDE_PROJECT_DIR unset, in W):
- `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md`: empty.
- `check-plan-routes.py --canonical-reader-audit`: 0 unresolved across 101 files, exit 0.
- `check-instruction-paths.py --root $PWD`: 68 files, 0 violations, exit 0.
- `bun run typecheck`: `tsc --noEmit` clean.
- grep for the cited stale phrases (index, DEC-214 `tool_input.prompt`, SPEC "model and name", harness.md "blocking `task`", variable name in the three bin files): no hits.
