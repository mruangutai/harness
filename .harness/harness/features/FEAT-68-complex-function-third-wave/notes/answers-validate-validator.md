# FEAT-68 — operator rulings for validate c0 (fix-c0-main-direct)

- A-1 (VF-01, the per-run lines): the three `mkdtemp()` directory names and the unittest
  wall-clock that differ between any two runs — at the base as at the pin — are accepted as
  divergences of run-to-run nondeterminism, not code. They are ledgered individually
  (`build-divergences.md` D-02..D-05) with exact old/new bytes; no substitution masks them.
  Recommended by the main session 2026-09-27; the operator was asked in-session and did not
  overrule.
- A-2 (VF-01, the baseline capture): the baseline is recaptured in the clean detached
  checkout `feat68-base-e655f14a`; the worktree capture is superseded and kept only at
  `/tmp/feat68-baseline-worktree.json` outside the record.
- A-3 (VF-02): the implementation pin is `9ab1813e`; `0c15bad6` was a superseded candidate
  (D-13). The red-first receipt and the clean-pin receipt say so.
- A-4 (validate c2, VF-04-C2): the operator authorised one additional evidence-only fix round
  beyond the signed 2 rounds / 90 min ("yes", 2026-09-27) — rework raised to 3 rounds / 120 min
  in feature.json with this file as the decision. Scope: the two reproduction paths and the
  grade-script staging in the preserved `feat68-cleanpin.py`; nothing else.
