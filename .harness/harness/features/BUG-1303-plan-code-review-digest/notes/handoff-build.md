# Handoff — BUG-1303, build → validate — written at b9939139, seq-1

## Next

Get F-01 ruled before anything else: the main session puts the QA matrix-floor question to the
operator — sign a `_matrix_provenance.bugfix` carve-out, or rule the `unit` floor stands and this
feature is gated. It is not squad-routable (no lane may write `.harness/harness.json`) and no fix
cycle can close it. Immediately after the ruling, dispatch the review panel through
`harness-validator-lead` against `review_sha` b9939139, base 63404ef0 = merge-base(main,
review_sha), naming BRIEF SC-04, SC-06, SC-07 and SC-08 as the inspection criteria it grades; that
run reviews CODE, so its record omits `code_grade`. Do NOT re-run the plan panel — it closed at
cycle 3 with zero open findings.

## Trust

- Full digest-validator suite exits 0, zero `^FAIL ` lines, `ALL PASSED` in 19.0s, 156 ok lines,
  including 16 per-persona `ok [documented contract]` lines and both synthetic group lines —
  orchestrator ran it twice, before and after the DEC-216 apply — verified-at b9939139
- SC-04 structural: `git diff --name-only 63404ef0..b9939139` names zero files under
  `.claude/skills/harness/bin/`, so `validate-digest.py` is byte-unchanged — verified-at b9939139
- T-02, T-03 and T-04 `verify:` each pass verbatim from the worktree root, including
  `sync-agent-adapters.py --check` rc 0 (SC-08) and the index idempotence diff (SC-06) —
  verified-at b9939139
- F-01 is the matrix floor alone, not this change's tests: `test_matrix.bugfix.always` is `["unit"]`
  with no `_matrix_provenance.bugfix` carve-out — notes/qa-BUG-1303-build.md — verified-at b9939139
- Test-first ordering for T-01 rests on the main session's report; cdfce3cb bundles T-01, T-02 and
  T-03 in one commit, so no git artifact shows the declared 9-failure red state — UNVERIFIED

## Dead ends

- Editing `.claude/skills/harness/bin/validate-digest.py` to drop the `_required_contracts`
  hand-mirror — BRIEF.md SC-04 forbids any change to it — verified-at b9939139
- Writing a unit test to satisfy the matrix floor — the mechanism reads `.md` files across two
  trees — notes/qa-BUG-1303-build.md — verified-at b9939139
- Re-restructuring the new test helpers — 8596745f already split them and simplify refused a second
  pass as churn — runs/2026-09-05-1-eng/digest.md — verified-at b9939139
- `brief-sc:` and `plan-task:` authority pointers from inside this worktree — both resolve the
  feature dir against the MAIN checkout, where it does not exist — STATE.md open questions —
  verified-at b9939139

## Working set

- .harness/harness/features/BUG-1303-plan-code-review-digest/STATE.md
- .harness/harness/features/BUG-1303-plan-code-review-digest/BRIEF.md
- .harness/harness/features/BUG-1303-plan-code-review-digest/feature.json
- .harness/harness/features/BUG-1303-plan-code-review-digest/notes/qa-BUG-1303-build.md
- .harness/harness/features/BUG-1303-plan-code-review-digest/runs/2026-09-05-1-eng/digest.md

## Done when

Scope: F-01, the bugfix `unit` matrix floor, is ruled by the operator
Authority: finding:.claude/worktrees/harness/BUG-1303-plan-code-review-digest/.harness/harness/features/BUG-1303-plan-code-review-digest/STATE.md#F-01
