# T-15's verify was unsatisfiable — COVERED by the existing signature, fixed with one character

**Verdict: covered.** No new operator signature needed. One character removed at
`plan.yaml:2033`; `approval:` and `BRIEF.md ## Approval` untouched. The verify now exits 0.

## The principle that decided it

**A correction to signed text needs no new signature only when the signed artifact itself forces the
one right answer — no judgement is exercised and no acceptance moves. If the correction requires
choosing among readings the artifact does not settle, it is new content and needs the operator.**

- Applied here: T-15's own `intent:` (plan.yaml:2085) mandates the grant string
  `.harness/*/features/*/plan.yaml approval:` verbatim, and the two sibling clauses at :2043-2044
  fix the clause grammar (`endswith`, no leading character, trailing fragment intact). Between them
  the signed text determines the edit completely. Nothing external was consulted, and no criterion,
  intent sentence, or task boundary changed. **Covered.**
- Applied to the #551 occurrence count earlier today: the plan said one, measurement said eight.
  The signed text did not contain the number — it had to be measured outside the artifact, and the
  correction changed what the task asserts about the world. **Not covered; it went to the operator.**

The discriminator is *where the answer comes from*, not how large the diff is. A one-character edit
that requires an external measurement would still need a signature; a multi-line edit fully
determined by the signed text would not.

## What I observed

Verify extracted from `plan.yaml` T-15 by `yaml.safe_load` (not retyped) and run from the worktree
root at `4673d0b`.

- **Before:** exit 1, single failure —
  `AssertionError: main_session is still granted no plan.yaml approval mapping:
  ['.harness/*/features/*/BRIEF.md ## Approval', '.harness/*/features/*/PLAN.md ## Approval',
  '.harness/*/features/*/plan.yaml approval:', '.harness/logs/**']`.
  The grant it is looking for is present in the list it prints — the assertion is unsatisfiable, not
  unsatisfied.
- **Only that reason:** the assert aborts the heredoc, so I ran a corrected copy in the scratchpad
  (plan untouched) to reach every later clause. It exited **0**: both greps clean, the
  glob-space-fragment check, the three DEC-120 exclusion comment lines, both sibling grants, and
  `check-plan-routes.py` (0 violations) all pass. So the failure had exactly one cause.
- **After the edit:** the verify, re-extracted from disk, exits **0**.

The `DEVIATION` lines from `check-plan-routes.py` are advisory; the checker exits 0 and the verify
gates on its exit code only.

## The diff

`.harness/harness/features/FEAT-32-concurrent-write-merge/plan.yaml:2033`, one character:

    -      hit = [g for g in w if g.endswith(" plan.yaml approval:")]
    +      hit = [g for g in w if g.endswith("plan.yaml approval:")]

Kept as an `endswith`, deliberately: the clause exists to pin the grant's grammar, and an `in` test
stops discriminating it. `approval.status` remains `approved` / `operator` / `2026-08-22`; no task
`status:` changed; `BRIEF.md ## Approval` untouched.

## Open questions

None blocking. Out of scope by dispatch and not reopened: SC-14 / the 221 figure, the #551
occurrence count (settled at eight), and T-15's `status:`.
