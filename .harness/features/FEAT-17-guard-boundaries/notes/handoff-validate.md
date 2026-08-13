# Handoff — FEAT-17-guard-boundaries, validate → ship — RECONSTRUCTED 2026-08-13, seq-1

**READ THIS FIRST. This is not the artifact INV-17 wants.** It was written on 2026-08-13 by the main
session, from records on disk, **after** the feature merged — not by the agent that crossed the
validate seam on 2026-08-12. No handoff was written at the crossing. Every line below is sourced to a
file that already existed; nothing is recalled and nothing is inferred. Treat it as a reconstruction
of what the successor needed, not as evidence that the seam was handed off properly.

## Next

**Nothing.** The ship decision was taken and executed: PR #298 merged as `a7c429c` on
2026-08-13T00:18Z, and #261 and #103 were closed by hand two minutes later. This handoff exists to
close a record gap, not to hand work forward.

## Trust

- **The panel returned a `high` and it was right: the fix had reinstalled #103's own failure
  direction inside #103's fix.** `worktree_owner()` returned `None` on every parse failure and every
  caller read `None` as *not a worktree*, so the write was allowed with no stderr. Appending one
  `\xff` byte to a valid `.git` pointer turned the identical write from exit 2 into a silent exit 0 —
  `notes/review-harness-code-reviewer-2026-08-12-panel.md`, `notes/ship-review-2026-08-12.md`
- Fixed with a third return state callers refuse rather than ignore, plus `MULTILINE` on the pointer
  regex — `$` had anchored at end-of-string, so any second line failed the whole match —
  `notes/ship-review-2026-08-12.md`
- **F-B [med]:** `check-state.sh` absorbed the `ImportError`, skipped every INV-25 branch, and printed
  *"all state invariants hold"* while exiting 0. The fourth import route and the only one that did not
  fail closed. Now a violation — `notes/ship-review-2026-08-12.md`
- **F-C [med, record]:** DEC-193's claim of preserved Bash-route behaviour was too wide by one column.
  Amended with the measured table — `notes/ship-review-2026-08-12.md`
- Ten of ten SCs met. **SC-07 was found `not_met` by the goal-check** — a missing test, not a broken
  guard — and closed with one case per route — `notes/research-FEAT-17-goalcheck.md`
- **SC-09 was amended by the operator, visibly, with the original struck beneath it.** It named two
  capture files that were never created and could not be; `git log --all` confirms neither ever
  existed on any branch — `BRIEF.md`, `notes/worktree-removal-receipt-2026-08-12.md`
- qa gate PASS at `c6a28bd`, `matrix_ok: true` — `notes/qa-FEAT-17-gate-2026-08-12.md`
- Six of seven tasks ran `main-session-direct` under the DEC-174 carve-out; only T-07 went through a
  squad — `plan.yaml`, `notes/receipt-harness-documentor-2026-08-12-07-t07-product.md`

## Dead ends

- **The target-side branch is NOT mutation-proved.** The mutation proof pins the session root inside
  the worktree, so it is direct evidence for the **root-side** check only. Neither half may be widened
  into the other — `notes/ship-review-2026-08-12.md`
- **The worktree-creation scan was never tested against evasion** — `sh -c`, `command git`, an alias,
  `xargs`. It is REQ-03's only mechanism — `notes/ship-review-2026-08-12.md`
- **`classify`'s `shared` outcome is unreachable**, so the branch handling it in `bash-write-guard.sh`
  is dead code new in that diff — `notes/ship-review-2026-08-12.md`
- **One unreproduced gate failure.** `run-unit-tests.sh` exited 1 once and returned 0 on the three
  runs after it. No cause found — `notes/ship-review-2026-08-12.md`
- **`--kind unit` runs neither guard suite nor `test-check-state.py`**, despite all three matching the
  unit detect glob. Backlog — `notes/ship-review-2026-08-12.md`

## Working set

- `.harness/features/FEAT-17-guard-boundaries/notes/ship-review-2026-08-12.md` — the whole picture
- `.harness/features/FEAT-17-guard-boundaries/notes/review-harness-code-reviewer-2026-08-12-panel.md`
- `.harness/features/FEAT-17-guard-boundaries/notes/qa-FEAT-17-gate-2026-08-12.md`
- `.claude/skills/harness/bin/harness_boundary.py` — the one boundary rule both guards import
