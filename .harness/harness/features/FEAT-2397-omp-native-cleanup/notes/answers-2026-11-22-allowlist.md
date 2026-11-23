# Build ruling by delegated authority — FEAT-2397 T-01 — 2026-11-22 — self-grading allowlist

Authority: the operator's delegation (`notes/answers-2026-11-22-signoff.md`). Ruled by
`fable-advisor` (`AdvisorC7Allowlist`). Raised by the T-01 builder.

**Gap.** T-01's signed intent mandates splitting validate-digest test functions to meet the grade
bar. The builder split `tests/integration/test-validate-digest.py:run_t09`, moving it from grade
1 to grade 4. `python3 tests/unit/test-code-grade.py` then failed: "run_t09 allowlisted grade is
stale: expected 1, got 4". The allowlist's own contract (lines 214-215) says "an exemption must
not outlive the record it excused".

`tests/unit/test-code-grade.py` is in no task's `files:`, and CI's unit suite runs it.

**Ruling: A, a recorded deviation; no plan amendment.**
- Delete exactly `("test-validate-digest.py", "run_t09"): 1,` from `SELF_GRADING_ALLOWLIST`.
- Don't re-pin it to 4, and change nothing else in that file. This is a removal-only consequence
  of mandated work, not new work surface, and the gate becomes strictly stricter.
- The T-01 evidence note records the deviation with the failing check, the intent clause and the
  1 → 4 grades.
- Any other edit to `tests/unit/test-code-grade.py` would need a plan amendment.
