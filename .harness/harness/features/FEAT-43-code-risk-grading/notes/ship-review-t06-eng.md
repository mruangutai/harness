# FEAT-43 build is blocked before T-08

## Decision needed

T-06's implementation is present, and its new assertions pass, but its signed unit verifier exits 1.
Completed main-session-direct T-09 sets `HARNESS_PROJECT_DIR` exactly as its signed intent requires;
the existing no-distribution unit invariant forbids that retired chain outside the canonical resolver.
T-06 cannot honestly become done, so T-08 remains dependency-blocked.

Approve amending T-09's implementation direction so the route checker consults the owner checkout
without setting the retired variable. The direct correction must preserve owner-manifest parity and
must not weaken `test-no-distribution.py`. Then engineering reruns T-06's exact unit command. A zero
exit unlocks main-session-direct T-08.

## Current evidence

- T-05: all five canonical specialist frontmatters carry `harness-code-risk-grading`; adapter sync
  check exited 0.
- T-06: `test-code-grade.py` now checks every worked example, minimum/grade coverage, and all ten
  specialist/tree deliveries separately; that test passes.
- Required unit gate: exit 1 at `test-no-distribution.py` because
  `check-plan-routes.py:70` contains the retired environment variable.
- T-06 run used zero send-backs; feature rework remains 6/10.
- Goal-check, UAT, QA, SIMPLIFY, validation, and ship have not run.

No report round was spawned. This briefing was assembled from:

- `runs/plan-product/digest.md`
- `runs/t01-t07-eng/digest.md`
- `runs/t02-eng/digest.md`
- `runs/t03-eng/digest.md`
- `runs/t10-product/digest.md`
- `runs/t06-eng/digest.md`

## Continuation checkpoint

After the approved T-09 correction, route T-06 through `harness-eng-lead` and run
`.claude/skills/harness/bin/run-unit-tests.sh --kind unit` with `/opt/homebrew/bin` first on `PATH`.
Only after exit 0 mark T-06 done and return T-08 to the main session. T-08 depends on
`[T-03, T-05, T-06, T-07]`, owns the review skill, digest validator and test, and canonical reviewer
agent definition, and verifies with the signed integration command. Exact paths are in
`notes/handoff-build.md`.

## Proposed backlog

| ID | Nature | Residual finding |
|---|---|---|
| B-1 | bug | QA matrix unit/integration commands still name nonexistent `.agents/skills/.../run-unit-tests.sh`; correct before QA. |
| B-2 | chore | Shared guidance still contains stale `.agents/skills` paths identified by planning. |
| B-3 | bug | Route checking unions writers across task files without proving one execution agent owns every path. |
| B-4 | chore | Investigate the older signed lane claim that disagrees with the current `.harness/harness.json` domain grant. |
| B-5 | chore | Resolve or sign exclusions for component, UI, eval, and typecheck matrix states currently marked unresolved. |
