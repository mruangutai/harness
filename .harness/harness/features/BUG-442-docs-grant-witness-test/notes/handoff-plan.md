# Handoff — BUG-442-docs-grant-witness-test, plan → build — written at 6d969ed3, seq-1

## Next

Once the main session signs plan.yaml's `approval:`, dispatch `harness-eng-lead` with the
`build` team for the single task T-01 (station `ready`, agent harness-backend-dev),
handing it T-01's `intent:` verbatim — it is complete. Then qa, then SIMPLIFY, then pin
`review_sha`. Do not re-plan: the panel ran clean at cycle 0.

## Trust

- `.harness/*/docs/**` is held by exactly ONE persona, harness-documentor, and no other —
  grep `docs/\*\*` over `.harness/team-config.yaml`, 2 hits, both documentor (:143,:144) —
  verified-at 6d969ed3
- The manifest declares exactly 16 personas; symmetric difference against T-01's typed
  census is empty — `notes/research-BUG-442-goalcheck-plan-c0.md` — verified-at 6d969ed3
- `REPO_ROOT` feeds EXACTLY ONE thing, `MANIFEST_PATH` (test-harness-yaml.py:32); every
  other read uses `ROOT` from `__file__`, so a repointed subprocess perturbs only the
  manifest tests and cannot false-red — orchestrator grep of the whole file —
  verified-at 6d969ed3
- `main()` prints `ok   {name}` (3 spaces) and `FAIL {name}: {e}`, each test in its own
  try/except — test-harness-yaml.py:892-904 — verified-at 6d969ed3
- The bug reproduces: the M1 mutant lands rc=0 on the pre-change suite, confirmed by pm
  and independently by the fable-advisor reader — `runs/2026-09-07-03-validator/digest.md`
  — verified-at 6d969ed3
- T-01's `verify:` is RED-capable now: suite exits 0 but both new-test greps match 0 lines
  — orchestrator ran it from the worktree root — verified-at 6d969ed3

## Dead ends

- Do not edit `.harness/team-config.yaml`; the grant is CORRECT — `BRIEF.md ## Constraints`
  — verified-at 6d969ed3
- Do not rewrite or weaken `COLLECT_FIXTURE`, `SHARED_MANIFEST_PATHS` or the equivalence
  test; their literals prove a DIFFERENT thing — `plan.yaml` D-02 — verified-at 6d969ed3
- Do not add a persona enumerator to `harness_yaml.py`; refused as out-of-scope production
  change — `plan.yaml` D-01 — verified-at 6d969ed3
- Do not expect a RED-first commit; the grant is correct, so the three permanent mutation
  controls ARE the red evidence — `BRIEF.md ## Verification notes and gaps` —
  verified-at 6d969ed3

## Working set

- `.harness/harness/features/BUG-442-docs-grant-witness-test/plan.yaml`
- `.harness/harness/features/BUG-442-docs-grant-witness-test/BRIEF.md`
- `.harness/harness/features/BUG-442-docs-grant-witness-test/notes/intake-BUG-442.md`
- `tests/integration/test-harness-yaml.py`
- `.harness/team-config.yaml`

## Done when

Scope: T-01 built and its verify green
Authority: approval:.claude/worktrees/harness/BUG-442-docs-grant-witness-test/.harness/harness/features/BUG-442-docs-grant-witness-test/BRIEF.md#Approval
