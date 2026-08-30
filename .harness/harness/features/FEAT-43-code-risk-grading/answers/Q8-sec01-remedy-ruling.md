# Q8 — SEC-01 remedy selection (answers `validate-regate-c18-validator` Q1 and Q2)

**Ruling by the orchestrator, 2026-08-29. This is an execution-time technical choice between two
implementations of an already-signed acceptance, not a plan change and not an operator question.**

## The answer

**Neither of the two options as posed. Stop consuming the digest's `base` for the `n_a` decision.**

Reject the minimal `base == head` remedy, and do not take the `feature.json` schema change either.

## Why the cheap remedy is refused

QA's own adequacy note contains the refutation. Rejecting `base == head` blacklists **one shape**
out of an unbounded family: `<review_sha>~1..<review_sha>` is the variant QA already constructed,
and any ancestor pair ending at the pin whose diff happens to contain no `.py` file is another. The
digest still *chooses* the base, so the reviewer still chooses the answer. A gate whose walk-around
is already written down in the note recommending it is the "gate that reports success" the cycle-13
ship review said is worse than no gate. Q6's second conjunct — "a self-named no-op range must not
buy `n_a`" — is about the class, not about the one instance the security reviewer happened to
demonstrate.

## Why the schema change is not needed either

QA's premise is that binding `base` needs a recorded predecessor that `feature.json` does not carry.
**Measured, in this worktree, rather than reasoned about:**

```
$ git merge-base main 34a49c4b78c74cac6676ec91d7cb7f262abf19e7
7ccfae8dd7644bc3aaea612dabf4317c0d804f99
$ git symbolic-ref refs/remotes/origin/HEAD
refs/remotes/origin/main
```

That is **exactly** the base the cycle-13 panel reviewed, derived from the repository with no new
field and no digest input. The predecessor is already in the system of record; it simply was not
being read.

## What to build

Compute "did Python change" from the **derived** range, not from the range the digest names:

- Keep the existing `head` binding: `reviewed`'s head must resolve to `feature.json`'s `review_sha`.
  It is correct and it stays.
- For the `code_grade: n_a` decision, diff `merge-base(<default branch>, review_sha)..review_sha`.
  The digest's `base` becomes a reported value that is cross-checked, never an input that decides.
- **Fail closed, narrowly.** If the default branch or the merge base cannot be resolved, the system
  of record cannot confirm the absence of a Python change, so `n_a` is REFUSED with a named error.
  The failure mode degrades a claim of "no Python changed" into a rejection — never into an
  acceptance. `pass`, `fail` and `grade_2` digests are not gated on base derivation; they keep the
  head binding only, so an unresolvable default branch cannot brick reviewer validation generally.

## Consequences for the two open questions

- **Q1 — answered.** Neither ranked option; the derived-base rule above.
- **Q2 — closed, not backlogged.** The `<review_sha>~1..<review_sha>` variant is inside the class
  this rule closes. It does not become a backlog row.
- **Q3 — accepted.** The validator lead's reframe is correct: grade-2 records are gated by
  construction and are the designed non-blocking carve-out, so a non-empty intersection between the
  allowlist and the gated set is the steady state, not a finding. Note also that CR-01's closure
  does not rest on the allowlist at all — `code-grade.py` never reads it. The independent proof is
  the tool's own exit 0 over `7ccfae8d..34a49c4b`, which reports zero blocking records in the gated
  set regardless of what any test-side allowlist says.

## Attempt budget

This is **repair attempt 3 of 3 on SEC-01**. Attempt 1 was `validate-remediate-c14-eng` step S3,
attempt 2 its S3b send-back. If this attempt does not close the class under a discriminating QA
re-run, the blocker is escalated to the operator rather than attempted a fourth time.
