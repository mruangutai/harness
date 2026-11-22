# Operator ruling — FEAT-2229 after validate c4 (2026-11-22)

Answers Q1 and Q2 from `r-20261121-validate-c4-validator` (handoff-validate-c4.md).

**Q1 — ruling: one more round, adding the tilde tests and fixing SEC-C4-01.** This round is authorized beyond
the spent rework ruling (3/3 rounds, 53/90 min). It is not the test-only round and not the waiver.
Scope:
- the actual-CLI tilde-fence cases qa names in notes/review-harness-qa-c4.md, killing mutations M6
  (a backtick run closes a tilde fence and vice versa) and M8 (the no-backtick-in-info rule applied
  to tilde openers), each shown red by mutation and then green;
- SEC-C4-01: `## DEC-NNN` resolves only on the full identifier, so `## DEC-10x` (and any
  identifier continuation) never matches DEC-10, with a spoof test that is red first;
- then re-pin and a short re-validation.

**Q2 — confirmed for the proposed backlog:**
- the Unicode line-break/whitespace mismatch and list-container phantom fences (qa);
- the qa digest validator refusing FAIL for mandatory coverage gaps while the suite is green (C4-QA-CONTRACT);
- SIMPLIFY B-1 and B-2;
- the `plan-merge.py check` `create: true` "already exists" item.
