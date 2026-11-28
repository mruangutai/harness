# plan-product cycle 1 — reader fan-in (lead)

Three readers ran on the same draft in one wave. scope (harness-code-reviewer) returned FAIL with
7 findings (4 high substance, 1 med substance, 2 med form); should-not-exist (fable-advisor)
returned 2 findings (1 med proportionality scope task, 1 low substance); design
(harness-ui-reviewer) self-scoped out — no user-facing surface — with no findings. Severities and
kinds are the readers' own, transcribed unchanged; no PF- ids assigned here. Reader notes:
`notes/review-harness-code-reviewer-plan-c1.md`, `notes/review-harness-ui-reviewer-plan-c1.md`;
fable-advisor has no write grant, so its block is transcribed here from its return.

```yaml
DIGEST:
  readers:
    - reader: scope
      status: ran
      persona: harness-code-reviewer
      reason: plan scope and architecture reader; VERDICT FAIL, 7 findings, note notes/review-harness-code-reviewer-plan-c1.md
    - reader: should-not-exist
      status: ran
      persona: fable-advisor
      reason: resolved and ran; VERDICT PASS with 2 findings, transcribed by the lead (no write grant)
    - reader: design
      status: ran
      persona: harness-ui-reviewer
      reason: Mode A self-scoped out, no user-facing surface; PASS, 0 findings, note notes/review-harness-ui-reviewer-plan-c1.md
  findings:
    - reader: scope
      summary: T-03 excludes a real copied-bin CLI invocation from SC-05.
      severity: high
      kind: substance
      scope: none
      why: test-feature-record.py:1402–1422 runs mbin/feature-record.py, outside the checkout-path selector in plan.yaml:204. Both ledgers can omit the same invocation and pass; capturing it exposes a deliberate traceback whose moved frames are not a root-only difference.
    - reader: scope
      summary: T-03 accepts PASS text without binding measured evidence to the review pin.
      severity: high
      kind: substance
      scope: none
      why: plan.yaml:184–196 accepts hand-written PASS markers and any qualifying ancestor with a bin diff. It checks no measurements or unresolved divergence and stops its tree comparison at the receipt commit. The receipt cannot exist at the earlier implementation SHA; distinguish it from review_sha and verify measured inputs through review time.
    - reader: scope
      summary: T-01 leaves INV-40’s registration observer on the old load seam.
      severity: high
      kind: substance
      scope: none
      why: test-check-state-feat59.py:612–623 replaces plan-merge.py and asserts the absence of an import failure. Once Ctx imports plan_merge.approval, the assertion can pass even though the observer never runs and stale registration is no longer tested.
    - reader: scope
      summary: D-02’s diagnostic exception is not operator-authorized or exhaustive.
      severity: high
      kind: substance
      scope: none
      why: Accurate paths are warranted but literal wording is a choice, and the settled rule keeps differences red pending a ruling. INV-7 and harness_config also render RepoModuleError, whose embedded module name changes automatically; the five named branches and their literals do not bound the output delta.
    - reader: scope
      summary: T-01’s directed module map omits spend_for’s dependency on _runs.
      severity: med
      kind: substance
      scope: none
      why: feature-record.py:124,708 puts a live helper in runs.py while the plan disallows spend importing it. A literal move breaks spend with NameError; sharing the record-read helper through read.py preserves locality without duplication.
    - reader: scope
      summary: T-01’s verify block is a smoke check, not a structural or corpus proof.
      severity: med
      kind: form
      scope: none
      why: It never binds argparse handlers to package imports, misses from artifact_accessors import load_feature_json, and runs two test files rather than the baseline-passing corpus. Keep the live audit and grade commands; strengthen the structural predicate and distinguish smoke from full evidence.
    - reader: scope
      summary: decisions_affected omits rules governing the checker, schema, and signed-hash surfaces.
      severity: med
      kind: form
      scope: none
      why: DEC-180, DEC-190/191, and DEC-229/230 govern mechanisms T-01 touches; declare keep for the operative rules. DEC-259’s layout rule survives removal of its exception, so amend rather than strike; the DEC-150/220 pointer amendments are also justified.
    - reader: should-not-exist
      summary: T-03's bun leg (omp-hooks.test.ts run plus a --preload patching node mkdtempSync) adds near-zero discriminating power and should be dropped from the CLI ledger.
      severity: med
      kind: proportionality
      scope: task
      why: The bun test's real feature-record.py spawns (omp-hooks.test.ts:3341, 3487, 3539) exercise only spend, stamp-tokens and run-end — verbs the Python corpus already ledgers — and the TS hook code building their argv is byte-identical on both sides, so the leg only reproduces divergences the Python ledger catches while adding the untried bun mkdtempSync preload, whose leaked temp paths would each be a spurious red divergence. Does not reverse Settled Q3 (a) if 'the test corpus' means the Python suites; if the operator meant to include the TS suite, this asks the operator to narrow it.
    - reader: should-not-exist
      summary: The second normalization token (fixture root alongside checkout root) should not exist; use one shared fixed fixture root on both sides, as FEAT-70 did.
      severity: low
      kind: substance
      scope: task
      why: FEAT-70's driver used one identical fixture path on both sides, cleared per execution, so only checkout-root bytes were normalized. T-03's extra fixture-root substitution is a channel where a real byte difference can be silently rewritten before comparison, which Settled Q3 (a) exists to forbid; a shared fixed root removes it at zero cost.
```
