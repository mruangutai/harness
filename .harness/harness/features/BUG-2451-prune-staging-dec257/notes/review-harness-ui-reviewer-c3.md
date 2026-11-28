# BUG-2451 — Cycle 3 UI review

**PASS (Mode B, out of scope; severity n/a).** The pinned feature changes evidence retention, plain terminal output, tests, and ship instructions; it does not change a rendered or interactive UI. Pruning `runs/<id>/ui/` deletes stored evidence, not UI code.

Reviewed commit `a97dbc6a8337cfbe9402d2a727aa28797a1efaf8` in the feature worktree. The live `feature.json` points to that SHA. The pinned commit changes only `feature.json` relative to its parent, `6e8c8c58`. The merge base with `origin/main` is `bda4a7eb`.

`git diff origin/main...a97dbc6a --stat` restricted to T-01: **5 files, 385 insertions, 141 deletions**. The unrestricted name-status census adds **32 feature records** (37 paths total): brief, state, metadata, plan, notes, observation, and run records.

| Changed T-01 path | Lines +/− | Surface |
|---|---:|---|
| `.claude/skills/harness/bin/prune-run-evidence.py` | 20/46 | Filesystem pruning and preflight (`:146`, `:172`); removes index staging and its terminal messages. |
| `tests/unit/test-prune-run-evidence.py` | 344/69 | Filesystem, CLI, Git index, and restoration tests; the cycle 3 claim guard is at `:639`, `:724`. |
| `.omp/commands/harness-ship.md` | 6/9 | Ship runbook prose (`:38`), not a UI template. |
| `.harness/harness/docs/DECISIONS.md` | 6/8 | DEC-238 ship retention and refusal prose (`:8137`). |
| `.harness/harness/docs/DECISIONS-INDEX.md` | 9/9 | Generated decision line offsets. |

`git diff b7e1f26e a97dbc6a --stat`: **40 files, 4,717 insertions, 1,593 deletions** (14 feature records, 11 `.claude` paths, 11 test paths, and 4 other `.harness` paths). Among T-01 paths, this range changes the unit test (+54/−18), decisions (+11/−26), and decision index (+51/−51). The range spans upstream merge `6e8c8c58`; `git diff b7e1f26e c9596b9a --stat` measures 15 files (+4,465/−27), with the unit test the only changed path outside feature records.

Neither range contains a visual source, asset, design, or prototype path. The pinned tree has no feature `DESIGN.md`, prototype, or tracked feature `runs/*/ui/` files. Rendered layout, visual fidelity, focus, accessibility, and light/dark parity are **not applicable**, not visually verified. MF-2R test behavior is for code review and QA; no runtime checks run. No UI findings or open questions.
