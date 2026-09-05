# STATE

## Current

- feature: BUG-1303-plan-code-review-digest
- run: .harness/harness/features/BUG-1303-plan-code-review-digest/runs/2026-09-05-12-product/state.yaml
- squad: product
- status: build-complete, awaiting-user on the QA matrix floor

Build phase closed. All four tasks are at station `done`: T-01/T-02/T-03 landed main-session-direct
(cdfce3cb, plus the main session's own complexity split at 8596745f), T-04 landed as DEC-216 with its
hand-written index row (b724a0f4), corrected at b9939139 to name `_required_contracts` — the mirror
site 8596745f created — after the simplify pass caught the stale identifier. `review_sha` is pinned at
b9939139. The full digest-validator suite exits 0 with zero `^FAIL ` lines and `ALL PASSED` in 19.0s,
carrying 16 per-persona `ok [documented contract]` lines plus both synthetic group lines;
`validate-digest.py` is absent from `63404ef0..b9939139`, which is SC-04's structural evidence.
Simplify ran all four angles: one fix applied (the DEC-216 pointer), efficiency and altitude clean.
QA returned FAIL on the test matrix only — F-01 below; the change's own tests are green and proven
red-capable. Handoff: notes/handoff-build.md. cycles_used 4 of 8.

## Open Questions

- F-01 — BLOCKING, operator only: `test_matrix.bugfix.always` is `["unit"]` and `gates.qa_gate` is
  `blocking`, but this bugfix's entire test surface is a contract guard over `.md` files across two
  trees — integration-shaped by construction, and no team lane may write `.harness/harness.json`.
  BUG-1128 raised the identical gap (`notes/qa-c1.md:22-46`) and it was never ruled. Either sign a
  `_matrix_provenance.bugfix` carve-out or rule that the floor stands and this feature is gated.
  Evidence: notes/qa-BUG-1303-build.md.
- Non-blocking, for the ship briefing: DEC-216's body now deliberately diverges from T-04's signed
  intent text, which still dictates the pre-8596745f identifier `required_by_persona`. The plan
  records what was asked; DECISIONS.md records what is true. No re-signature sought.
- Harness defect, not a BUG-1303 finding: inside a worktree, `handoff_done_when` authority pointers
  and a panel reader's structured `yield` both resolve against the MAIN checkout, because
  check-domain strips the `.claude/worktrees/<seg>/` prefix for glob matching and then reuses the
  stripped path for resolution. Measured again this run: `brief-sc:` and `plan-task:` are therefore
  UNUSABLE from a worktree — both derive the feature dir from the stripped path — leaving only
  `finding:` and `approval:`, which take a path that can be spelled through `.claude/worktrees/`.
  Blocked on: infra-tier attention.
- Harness defect: bash-write-guard.sh parses the whole command line textually, so plan-merge.py's
  sanctioned `apply --proposal -` stdin route is refused when the proposal body contains an angle
  bracket; and `amend --value-file -` is not wired to stdin although `apply --proposal -` is.
- Harness defect, observed this run: both the validator lead and the eng lead each created two
  identical run directories for one segment (01/02-validator, 1/2-eng). Harmless — `runs/` is
  gitignored — but the duplicate is bookkeeping noise no lead reported.
