# Operator rulings: FEAT-2423 plan run 01 (2026-11-28)

Run `2026-11-28-01-plan-product` returned ESCALATE. These are the operator's rulings on its open questions, plus one direction of the operator's own. Together they are one revision.

- **org.html (operator direction).** Delete `.harness/harness/docs/org.html` in T-04; don't rewrite it. Drop it from SC-10's grep and from T-04's verify. Nothing in the repository links to it. With it gone, the design reader has no surface in this feature.
- **Q-05.** Check the plan against the main checkout (`plan-merge.py check --root <main checkout>`), where it resolves 78/78. Keep the worktree sparse; the sparse checkout is NOT widened (FEAT-1559). The gap is filed as a separate issue: a plan can't own other features' files while `check --root <worktree>` reads only the sparse disk.
- **LEAD-01: re-panel.** The three high remedies applied at apply were never re-read by a reader. They are T-01 (catalogue `rows[-8]`, the rename witness, the INV-2/5 grep), T-05 (the Amended-by ban scoped to DEC-129/150) and the T-06/T-07 `set -e -o pipefail` deletion sweep. The scope reader re-reads those tasks, together with every task this revision changes, in a new run.
- **Q-01.** The build starts after FEAT-2643 merges, rebased first.
- **Q-02.** No new gate. Whichever of FEAT-2641, FEAT-2688 or BUG-2524 merges after this feature runs `git rm` on its own STATE.md; review catches any leftover.
- **Q-03.** Delete `.harness/kaya/features/FEAT-01-kaya-platform/STATE.md` in T-07, as drafted.
- **Q-04: a ship condition.** Expertise entries harness-validator-lead G-01 and harness-code-reviewer G-05 must be dropped before this feature ships. That happens through this feature's distillation, since build tasks can't edit expertise (DEC-145/253). State it as an SC or a ship gate.
- **Q-06: rejected.** No test exceptions. Remove `case_stray_status_file_is_inert` and `run_retired_status_file_is_ungated` from the plan; no test names the file. SC-03, SC-05 and SC-06 lose those exemptions.
- **GC-03: accepted.** Historical mentions stay (DEC-205): old decision narrative, shipped runs, notes and plans, and BUILD.md. The destination means no live mention.
- **Q-07.** `plan-merge.py apply` accepting an empty proposal is filed as a bug.
