# Operator rulings on validate run 2026-11-27-04-validate-validator (ESCALATE)

Answered 2026-11-27 in conversation with the main session.

- **E-01 / OQ-01: accepted as is, not documented.** The baseline can be a non-content state: the hook file is absent, unreadable or not a regular file at module evaluation, or it is swapped between OMP's read and module evaluation. The operator judged this window next to impossible: it needs the hook file to change in the milliseconds of omp startup. Its outcome is the pre-feature behaviour (no detection), never a refusal bypass. The signed D-03 and T-01 stand unchanged, and SPEC §4.2 gets no sentence for it.
- **OQ-02: no PM-authored script.** The main session copies the SC-10 steps from the build receipt into `notes/uat.md`.
- **must_fix, inside the budget:**
  - The FIFO probe asserts `mkfifo` succeeded and the path is a FIFO.
  - `expectStale` asserts the reason names the path relative to the root.
