# Security distillation — BUG-2161

PASS — two craft safety lessons applied by expertise-merge.py; both expertise files pass check-expertise.py. No new security audit or source changes.

## Evidence and judgment
Read only the named surviving evidence: notes/review-harness-security-reviewer-c0.md, notes/review-harness-security-reviewer-c1.md, and runs/2026-11-03-09-fix-c1-validator/digest.md. The c1 review supplies both lessons; the validator independently corroborates protected aliases, indirect parent detach, and station-refusal evidence preservation.

Accepted: self-derived 2; lead-relayed-only 0 (both accepted lessons also corroborated by the relayed digest). Rejected: separate relay copies of both lessons (2, duplicates); accepted-risk/operator-ownership lesson (1, already covered by O-05); integer-only/list-argv/reason-file implementation details (1 grouped candidate, no new durable rule); repository-specific copies (2, both lessons generalize to unfamiliar repositories). No survivor expansion.

## Counts and exact applied operations
Craft `.harness/expertise/harness-security-reviewer.md`: Patterns 15→15, Gotchas 15→15, Outcomes 10→10, Open 0→0.
Repository `.harness/harness/expertise/harness-security-reviewer.md`: Patterns 8→8, Gotchas 9→9, Outcomes 1→1, Open 0→0 (unchanged).

- replace / Patterns / P-16: WHEN an opt-in protects objects that can share identities across roles DO trace every direct and indirect mutation against protected identities, including relationship updates; filtering only the explicit disposal list does not establish zero writes.
  Displaced the narrower dependency-error-contract pattern at cap.
- replace / Gotchas / G-15: WHEN cleanup deletes recovery or audit evidence after recording a terminal state DO require confirmed persistence or an authoritative already-terminal read before deletion; attempted writes, missing records, and refused transitions must preserve the evidence.
  Displaced lower-value recommendation-consistency advice at cap.

Merge result: REPLACED P-16; REPLACED G-15; APPLIED. Refused operations: none. Repository operations: none.

## Checks and limits
Both per-file check-expertise.py commands returned OK (exit 0). Craft checker additionally reported existing G-01's DEC-100 repository-layer advisory; not a violation, unchanged because moving unrelated pre-existing doctrine is outside these two safety lessons. No suites, tests, builds, linters, formatters, grading, or diff review run. QA suite n/a; matrix_ok n/a; code_grade n_a; reviewed none.

Open questions: none.
