# Q9 — SC-11 reads arm MAXIMA, and T-01's deviation is refused

**Two decisions issued by the operator on 2026-08-29**, answering Q2 and Q3 of
`notes/ship-review-validate-final-c24.md`. Recorded **before** the UAT runs, which is the point of
recording it at all.

## 1. SC-11 is decided on arm MAXIMA

SC-11's own words are "the worst cognitive complexity in the skill-loading arm", and the worst is the
**maximum**, not the mean. The BRIEF's probe citation reported arm means; that citation does not
govern the criterion's text.

`notes/uat-sc11-c21.md` already pins maxima. Its arithmetic stands unchanged and is now the ruled
method, not a proposal:

```
worst_A = max(a1, a2)        worst_B = max(b1, b2)
spread_A = |a1 - a2|         spread_B = |b1 - b2|
gap = worst_B - worst_A
```

**SC-11 is met when BOTH hold:** `worst_A < worst_B` **and** `gap > max(spread_A, spread_B)`.

The script's own consequences stand with it: a null result (`worst_A < worst_B` but the gap inside
the noise) is `not_met` and is **a finding against the skill, not a reason to re-run for a better
draw**; a reversed result is evidence the skill may be actively unhelpful. The pre-build A/B probe
does not discharge SC-11 — the draft it graded shares no non-blank line with the shipped skill.

The UAT has **not** been executed and SC-11 is **not** judged. Only the operator changes `status:` in
that file.

## 2. T-01's deviation is REFUSED — no exemption, fix it

The operator does **not** accept the two reasoned grade-2 functions in `code_grade.py`.
`_body_hashes.collect` and `gated_set` must reach **grade 4 or better**, so that T-01's unconditional
clause — "keep every function you write in `code_grade.py` at grade 4 or better… the tool must pass
its own bar" — is true as written rather than true-except-twice.

This is consistent with the operator's original cycle-14 ruling: remediate at the root, never exempt.
REQ-06 making a grade-2 function mergeable was never the question; the question was whether a
craftsmanship clause can be discharged by a mergeability requirement, and the answer is no.

**Cycle 25 is the final authorized rework cycle.** The budget is not raised again. A failure at cycle
25 is terminal `BLOCKED`, not a request for a twenty-sixth. No PR, merge, deploy, ship or issue
closure is authorized by this decision.
