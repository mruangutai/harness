# Fail-first receipt — BUG-1716 T-05 (INV-40 signed-text trigger)

case_inv40_signed_text run against the parent commit's check-state.py (699510f3; T-04's plan-merge.py hashes ARE present there, so the fixture signs with real hashes and only the checker is pre-change). Captured 2026-09-16T06:14Z by Main.

```
ok - case (40d.a) a freshly signed plan is silent — the hashes agree with sign-approval
FAIL - case (40d.b) an unledgered intent change is ONE violation naming the task and the remedy
ok - case (40d.c) the matching amendment judgement silences it
ok - case (40d.d) an OVERRULED matching amendment still covers — the ledger is the record
FAIL - case (40d.e) an amendment for ANOTHER task does not cover
FAIL - case (40d.f) another judgement kind naming the task does not cover
FAIL - case (40d.g) a files change is caught
FAIL - case (40d.h) a verify change is caught, on the task it belongs to
FAIL - case (40d.i) two independently changed tasks are two violations
ok - case (40d.j) a presentation-only rewrite (quoting, list form) hashes the same — silent
ok - case (40d.k) a plan with no signed_task_hashes (signed before BUG-1716) is not graded
ok - case (40d.l) a pending approval is not graded by this trigger
FAIL - case (40d.m) the text trigger reports beside, not instead of, the other triggers
```

The silent cases (a, c, d, j, k, l) are green pre-change by absence of the trigger; every detection case is red.
