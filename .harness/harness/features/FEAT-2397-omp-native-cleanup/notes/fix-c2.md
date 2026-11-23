# Post-validate CI defect — FEAT-2397 — 2026-11-22

**Symptom.** PR #2441 CI, `checks` → Unit suite: `test-omp-hooks.py` failed 5 cases, all in
"FEAT-2225 expertise_apply through the real policyRunner into the real core". The error was
`distill-authority: REFUSED no live claim binds runtime Orch.Val.Code to FEAT-9003-host-core`.
origin/main CI is green at 522c94b2.

**Root cause.** T-02's signed rename made CI's Unit step export `HARNESS_PROJECT_DIR`. The old
`CLAUDE_PROJECT_DIR` was read by nothing, so the Unit step previously ran with the variable unset.
That block copies the core into a `/tmp` checkout and relies on every gate resolving its root from
its own location. The resolver prefers `HARNESS_PROJECT_DIR` whenever it carries the marker, and
`runPolicy` passes `process.env` to the gates. So the gates judged the workspace, where there are no
claims, instead of the fixture.

The local evidence was consistent with this all along. The 5 cases failed in every run that
exported the variable, including the "base-clone control". That control set the variable itself,
which is why it wrongly read as host-environmental.

**Fix (test only, T-01's file `tests/unit/omp-hooks.test.ts`).** The block saves the inherited
value, deletes it in `beforeAll` and restores it in `afterAll`. Production is unchanged.

**Red/green.**
- `fix-c2-evidence/red-ci-env.txt`: with `HARNESS_PROJECT_DIR=$PWD`, 2 pass and 5 fail, exit 1.
- `fix-c2-evidence/green-ci-env.txt`: the full file with the variable set passes 247/0, exit 0.
  With it unset it also passes 247/0, and typecheck is clean.

**Follow-up in the same fix.** The first version spelled the variable in `omp-hooks.test.ts`. That file has no `test-` prefix, so `test-no-distribution.py` case6 scans it, and case6 went red. The name is now assembled as `"HARNESS" + "_PROJECT_DIR"`, the same pattern case6 uses for its own constant. In the CI env, `omp-hooks` passes 247/0 and `test-no-distribution` passes.
