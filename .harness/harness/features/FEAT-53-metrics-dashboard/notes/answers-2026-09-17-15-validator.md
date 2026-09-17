# Answers — FEAT-53 orchestrator escalation after validate 2026-09-17-15 — 2026-09-17

## Q1 — fixed-dark document state
Operator ruled: **in scope, under T-13's rework round.** DESIGN C-3 fixes the surface to dark only; a document whose computed `color-scheme` is `normal` and whose body is transparent does not satisfy that contract, so this is a defect against the signed design, not new scope. The frontend fix round that closes V-17 and V-18 also sets the document root's `color-scheme: dark` and the opaque Neutral dark ground (`rgb(27,27,27)`) on `body`, and the ui-reviewer re-measures both in the browser alongside V-03's live drill-down proof.

## Q2 — cycle budget
Operator ruled: **raise `max_total_cycles` to 40**, recorded through `feature-record.py raise-cycles` (this file is the decision). 28/30 at validate c1 with four must_fix open (V-02, V-03, V-17, V-18) plus the fixed-dark finding: one frontend fix round, one re-validate, and one contingency. The signed rework ruling (10 rounds / 450 min) is unchanged and still governs.

## Instruction
Resume: one frontend fix round (T-13/T-14/T-28 owners) closing V-02 evidence, V-03 live payload + browser drill proof, V-17 focus outline, V-18 body margin, and the fixed-dark document state together; then one re-validate. Do not open further scope. Return with the briefing, or awaiting_user only on a genuinely new finding class.
