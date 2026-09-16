# Fail-first receipt — BUG-1723 T-02 (INV-43)

case_inv43 run against check-state.py at 69ebcefd (pre-change; cases added, invariant absent). Captured 2026-09-16T05:10Z by Main.

```
FAIL - case (43.a) succession recorded AFTER run 2 started is a VIOLATION naming both
ok - case (43.b) succession recorded before run 2 started is silent
ok - case (43.c) succession at exactly run 2's start is silent (no later than)
FAIL - case (43.d) an unparseable succession `at` is CANNOT VERIFY naming the field
FAIL - case (43.e) a successor run with no started_at is CANNOT VERIFY naming started_at
ok - case (43.f) a MISSING succession is INV-40's finding, not INV-43's
ok - case (43.g) a handoff with no successor run yet has nothing to grade
FAIL - case (43.h) two handoffs match two successions in order; only the second is retrospective
ok - case (43.i) a legacy record is never graded by INV-43
```

The four positive cases (retrospective, unparseable `at`, missing `started_at`, second-of-two) are red; the five silent controls pass vacuously at the parent and discriminate through the positives beside them.

## Grade 2, reason (harness-code-risk-grading)

`case_inv43_chronology` grades 2 on ABC (27.2, bar 3 for tests): four checks — after, before, equal, and the two-handoff ordering — over one fixture helper. Splitting the ordering case out would make a one-assertion function whose name adds nothing the `(43.h)` label does not already say; kept as one case per the skill's "not a licence for meaningless helpers".
