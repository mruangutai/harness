# Post-validate CI defect — delegated ruling — FEAT-2397 — 2026-11-23

Authority: the operator's delegation (`notes/answers-2026-11-22-signoff.md`). Ruled by
`fable-advisor` (`AdvisorC13PostValidateFix`).

**Facts.**
- PR #2441's CI failed `test-omp-hooks.py` ×5 after c2 PASSed at `eda06a68`. The cause: T-02's
  CI export of the project-root override reaches the gates through `process.env` in a
  fixture-copy test.
- The fix (`dfe27d14` + `c1eb9eaa`) is test-only, in T-01's file `tests/unit/omp-hooks.test.ts`.
  Production code is unchanged. Root cause and evidence: `notes/fix-c2.md`.
- PR CI is green at `c1eb9eaa`.

**Ruling.**

1. **Rework round 2 of 2, with a narrow re-validate.** Main authored the code change and its
   evidence, so Main cannot judge it. qa and code review cover `eda06a68..<pin>`; the c2 goalcheck
   and c1 security/UI verdicts carry over (DEC-230). Ledger steps:
   - a `continue` judgement, with no `--regate` (the CI FAIL is not a ledger FAIL run);
   - `run-start --succession continue`, which seq-6's handoff makes owed;
   - close-run attributing 1 cycle.

   If c3's code reader finds the fix wrong in kind, the budget is spent and the question goes to
   the operator.
2. **Corrections are appended, never rewritten.** They go into `notes/c1-evidence/README.md` and
   the ship briefing. The PR body is edited in place.
   - Withdrawn: test-omp-hooks as "host-environmental". The control exported the variable itself.
   - Withdrawn: "the BUG-1290 lines". They are the expected mutation-proof output of
     `test-factory-claim-mutation.py`, which passes.

   `notes/answers-2026-11-22-ship.md` stands as written. This ruling supersedes its item 5 first
   row and its "don't file the hermetic sanitizers" clause.
3. **Backlog, three rows:**
   - `test-factory-config.py` (21) fails on macOS because the temp path realpaths from `/var` to
     `/private/var`;
   - gate-runtime headroom: 41 s observed against the 45 s per-script timeout;
   - test helpers that execute gates must pin or scrub the project-root override, not hand gates
     raw `process.env`. One site existed and is fixed; this row is insurance, priority low.
