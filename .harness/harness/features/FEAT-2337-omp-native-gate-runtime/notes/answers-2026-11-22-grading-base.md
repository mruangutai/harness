# Build ruling by delegated authority — FEAT-2337 — 2026-11-22 — T-03 grading base

Authority: the operator's delegation, recorded in `notes/answers-2026-11-22-signoff.md`.
Ruled by `fable-advisor` (`AdvisorB2GradeBase`).

**Question.** T-03's intent pins the cumulative self-grading check
(`tests/unit/test-code-grade.py --feat2337`) to the fixed base `dd04e52a`. After signature, build
entry merged origin/main (BUG-2328, #2338) as `d04c765a`, the recorded pre-edit baseline (commit
`76f8b26e`). That merge changed `tests/integration/test-check-domain-post.py`, another feature's
functions. It is the only Python test file in `dd04e52a..d04c765a`.

**Ruling: A.** Use `d04c765a` as the fixed grading base. It is `dd04e52a` plus that upstream merge
only, so the check grades exactly this feature's own new and changed test functions, which is
what SC-08 requires. A recorded deviation is sufficient; no plan amendment is needed.

- The deviation applies only to the grading base. The intents' other `dd04e52a` references
  ("product docs absent at base …") are unchanged and must not be rewritten.
- If another main merge lands before T-03's tip is committed, the same reasoning applies (the base
  moves to that merge). No machinery is to be built for it in advance.
