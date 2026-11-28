# BUG-2451 — Cycle 2 UI review

**PASS (Mode B, out of scope; severity n/a).** T-01 changes how ship checks and prunes stored run evidence, not how any UI renders or behaves.

Census from `git diff --name-status -M` at `e83c4e207f2d6f110692e37452054bae6923857a..b7e1f26ecfdff7683d25009435a30098c5580c52`: 5 modified task files and 22 added feature records. The records are four root documents/metadata files, ten notes, one observation and seven run records; none is UI source or assets. The operator signoff (`055a7d0d`) touches feature records only. The full diff has zero visual-source or asset extension matches. The c1-to-c2 diff changes only the pruner and its unit test outside the feature directory; the delta after `10823d58` changes only `feature.json` and `plan.yaml`.

| Changed task file | Lines +/− | Surface |
|---|---:|---|
| `.claude/skills/harness/bin/prune-run-evidence.py` | 20/46 | Filesystem preflight, removal of index staging, and plain terminal diagnostics. At `:57–65` it reads `ui/results.json` as retention metadata; at `:128–156` it removes a stored evidence directory, not a served bundle; at `:172–188,212–216` c2 includes those directories in the preflight. |
| `tests/unit/test-prune-run-evidence.py` | 308/69 | Filesystem, CLI, Git index and document assertions. `:122–123` writes sample screenshot bytes and results metadata, and `:379–409` tests filesystem permissions and refusal, not a renderer. |
| `.omp/commands/harness-ship.md` | 6/9 | Ship runbook prose (`:51–56`), not a UI template. |
| `.harness/harness/docs/DECISIONS.md` | 6/8 | DEC-238 retention and refusal prose (`:8156–8161`). DEC-257 classifies the stored `ui/` files as screenshots and traces. |
| `.harness/harness/docs/DECISIONS-INDEX.md` | 9/9 | Nine line-offset updates, no ruling text changes. |

Direct pin checks found no feature `DESIGN.md`, prototype, or tracked feature `runs/*/ui/` files. Product `docs/spec.md`, `docs/decisions.md`, and `docs/architecture.md` are absent at the pin, as scoped in the brief. Visual fidelity, rendered layout, accessibility and dark/light parity are not applicable, not visually verified. MF-1's `ui/` reference is storage only; adjudicating the refusal and MF-2/QA-F1–F3 test mechanics belongs to the code, security and QA lenses. No UI findings or open questions; no runtime checks run.
