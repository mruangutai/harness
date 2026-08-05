# Answers — FEAT-07 plan gate, run plan-product — 2026-08-04

The user reviewed BRIEF and PLAN in ONE pass and raised everything below as one set.
This is one consolidated fix, not one fix per ruling — the batching rule this feature
installs, applied to itself. No further change requests are outstanding.

## Q1 — the ungameability residue: CLOSE IT. The receipt clause is IN scope.

RULING: T-02 gains the receipt clause. The self-reported field alone does not meet the
mandate, and the user accepts the scope addition.

What the clause requires, as explained to the user and agreed:
- The dev's B-7 verification receipt
  (`.harness/features/<FEAT>/notes/receipt-<agent-name>-<runid>.md`, defined at
  `harness-handoff/SKILL.md:71-73`, already granted per specialist at
  `team-config.yaml:144,158,171,184,199`) must carry the task's `verify:` command AND its
  verbatim output.
- No new artifact, no new grant, no new reader. The receipt already exists and is already read.
- Honest limit, stated to the user and not to be overclaimed in BRIEF or PLAN: this does not
  make skipping impossible — output can be fabricated. It makes skipping leave evidence in a
  file qa, the code reviewer and the user already open. The rejected alternative (the lead
  re-runs the command) is structurally impossible: leads hold no `Bash`.
- pm decides where the requirement is stated so it reaches all five specialists without an
  inline copy per agent (DEC-126). It needs a success criterion of its own.

## Q2 — the `suite: fail` + `VERDICT: PASS` fail-open: FOLD THE FIX INTO FEAT-07.

RULING: do NOT file it as a separate backlog issue. Fix it here, in T-01, alongside the new
`task_verify` fail-value gate. This REVERSES the plan's D-01 tradeoff sentence ("the identical
`suite: fail` + `PASS` fail-open on the dev persona stays open (Q2, out of scope here)") and
D-01 must be rewritten to record that the user ruled the other way, and why.

Independently re-measured by the main session at `3bfedc9` before this ruling was taken: a dev
digest with `suite: fail` + `VERDICT: PASS` returns `digest ok`, exit 0. Confirmed cause:
the `GATE_FIELDS` check at `validate-digest.py:481` is nested inside the
`field in NULLABLE and val in PLACEHOLDER_UNSET` branch at `:477`, so it can only ever see
placeholder values.

Requirements on the fold:
- The widened gate covers `suite` for the personas that already have it in `GATE_FIELDS` —
  `dev` and `qa` (`:73`). `qa` also carries `matrix_ok`, a bool: pm must decide explicitly
  whether the fail-value gate applies to it and say so, rather than leaving it implied.
- `dev-ops` must NOT gain `suite` in either gate structure. D-03 stands unchanged: `suite: n/a`
  + `PASS` remains legal for dev-ops because `test_matrix` maps config/scaffolding/docs to `[]`.
- BEHAVIOUR CHANGE, to be stated plainly in BRIEF: any return carrying `suite: fail` (or
  `matrix_ok: false`, if pm scopes it in) alongside `VERDICT: PASS` starts being REJECTED. That
  is currently accepted. This is a deliberate tightening, not a regression.
- It needs its own success criteria — at minimum: `suite: fail` + `PASS` rejected for `dev`,
  and the dev-ops `suite: n/a` + `PASS` acceptance still intact (the existing SC-04 already
  guards the second half; check it still discriminates once the gate widens).
- Still inside the DEC-174 carve-out. Direct execution, tests run explicitly, human reads the diff.

## Q3 — architecture review: DISPATCH IT.

RULING: eng-lead reviews the plan BEFORE the user signs. Run it AFTER this fix is applied, so
the review sees the plan the user will actually sign, not the superseded one. FEAT-06's
equivalent review returned six `must_fix` on a comparably sized plan; T-01 now touches five
structures in the enforcement layer rather than four.

## Q4 — the user's own change requests: NONE.

The user read BRIEF and PLAN and raised nothing beyond Q1 and Q2. Do not solicit again.

## Terminus for this fix

Return when BRIEF and PLAN are revised and the architecture review has been run and its
findings resolved. The signature is the user's and the main session's to take.
