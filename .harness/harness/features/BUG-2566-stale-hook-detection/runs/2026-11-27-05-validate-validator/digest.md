# Validate c2 — BUG-2566-stale-hook-detection — PASS

**BLUF.** At `f4048ad3` both of run 04's must_fix items are closed, and the closure was measured by mutation, not just read. `must_fix` is empty and `severity_max` is low. The only open item is SC-10, the operator's UAT, which stays pending; its steps are in `notes/uat.md`.

Reviewed range: `87efcd8a..f4048ad3f9fbe9326d9799485fb97d87547d27be`. The fix-round delta `8e18c053..f4048ad3` is test-only plus notes; the code reviewer confirmed this. All five readers returned PASS: qa, code-reviewer, security-reviewer (in scope), ui-reviewer (scoped out after a 48-path census) and pm.

## Run 04 must_fix: closure evidence

1. **FIFO probe.** The FIFO case now goes red when no FIFO is created; it no longer passes as the deletion case.
   - qa made `mkfifo` fail and got probe status 3, with the test red.
   - pm removed `mkfifo` from PATH and got status 3, with the test red.
   - qa also ran the pre-fix test as a control. It stays green under the same perturbation, so the old test really was vacuous and the new one is not.
   - The code reviewer, who raised the finding, closed it at source.
2. **`expectStale` root.** Mutant M3 (`process.cwd()` as the reason root) now fails 6 of the 13 fingerprint cases. qa raised F-1 and measured this itself; pm reproduced it. The pre-fix test stays green under M3. The code reviewer closed item 2.

## Advisory (not gating; repo gate is `advisory_unless_high`)

- **Exact-`BLOCKED` carve-out has no test witness.** Raised by qa (F-2) and the code reviewer as low, carried from c1 and re-measured at this pin: mutant M6 still survives (34/34). SC-06 pins the predicate by inspection, and validate-digest still judges such a yield. **Repair, if wanted:** add refused rows for `{VERDICT:"blocked"}` and `{DIGEST:{VERDICT:"BLOCKED"}}` near `tests/unit/omp-hooks.test.ts:2504-2518`.
- **No fixture teardown.** Raised by the code reviewer as low. `staleTree()` at `tests/unit/omp-hooks.test.ts:4458-4465` never removes its mkdtemp trees, so each full run leaves 13 trees (FIFO and probe included) in the OS temp dir. This is hygiene only and has no effect on correctness. **Repair:** `afterEach` → `rmSync(root, {recursive:true, force:true})`.
- **SC-05.** The median is 0.063 ms against the 5 ms bound. The threshold's discrimination is still not shown, and the number holds for this test host only (a signed gap).
- **Natural fail-first for SC-01, SC-04 and SC-05 is signature-absent.** That means those tests fail at 87efcd8a only because the export is missing. The semantic proof comes from mutants M1, M3 and L and the FIFO perturbations.

## Assurance

- **Executed tests:** qa and pm ran the tests. qa re-ran the verify blocks for T-01 and T-02, with unit 69/69 and omp-hooks 274/0. The receipt is `runs/2026-11-27-05-validate-validator/qa/manifest-unit.json`. It reflects this host's environment, not CI, and it stays untracked until main commits the closed run.
- **Static review only:** the code reviewer and the security reviewer reviewed without running anything.
- **Settled items:** none was re-raised (E-01, OQ-02, D-01..D-04).

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2566-stale-hook-detection/.harness/harness/features/BUG-2566-stale-hook-detection/runs/2026-11-27-05-validate-validator/digest.md
DIGEST:
  headline: 'BUG-2566 at f4048ad3 is ship-ready on the automated gates. Both run-04
    must_fix items are closed, measured by mutation: M3 now fails 6 of 13 fingerprint
    cases, and a failed mkfifo fails the FIFO case with probe exit 3. must_fix is
    empty, severity_max is low, and SC-10 UAT is pending with the operator.'
  open_questions: []
  files_touched:
  - .harness/harness/features/BUG-2566-stale-hook-detection/runs/2026-11-27-05-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/BUG-2566-stale-hook-detection/observations/harness-qa.md
  expertise_update: []
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'Matrix floor {unit} satisfied at f4048ad3: unit 69/69, omp-hooks 274/0,
      typecheck clean. Both run-04 must_fix items measured closed. The carried low
      mutant M6 still survives.'
    files_touched:
    - .harness/harness/features/BUG-2566-stale-hook-detection/runs/2026-11-27-05-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/BUG-2566-stale-hook-detection/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Both c1 must_fix items are closed at f4048ad3, and the fix range changed
      only the test file and feature records. Two low T-01 advisories.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: The fix round adds no security exposure, and no refusal bypass was found
      beyond the settled E-01.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B out of scope: none of the 48 changed paths renders UI.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: SC-01..SC-09 are met and both must_fix items close at the pin. The operator
      perspective is partial only because SC-10 UAT is pending. No amend or strike
      dispositions.
    files_touched: []
  must_fix: []
  branch: feat/BUG-2566-stale-hook-detection
  escalations: []
  adequacy_notes:
  - Both closures were measured by mutation, not just read. M3 (process.cwd() as the
    reason root) fails 6 of 13 cases (qa, reproduced by pm). Making mkfifo fail gives
    probe status 3 and a red FIFO test (qa and pm independently). In both cases the
    pre-fix test stays green under the same perturbation, so the old tests were vacuous
    and the new ones discriminate.
  - 'Advisory, carried from c1 and re-measured at this pin: mutant M6 still survives
    34/34, so the exact-BLOCKED carve-out is pinned by SC-06 inspection only (qa F-2,
    code-reviewer low). Optional repair: add refused rows for {VERDICT:''blocked''}
    and {DIGEST:{VERDICT:''BLOCKED''}} near tests/unit/omp-hooks.test.ts:2504-2518.'
  - 'Advisory, new (code-reviewer low): staleTree() at tests/unit/omp-hooks.test.ts:4458-4465
    never removes its mkdtemp trees, leaving 13 per run. Hygiene only. Repair: afterEach
    rmSync(root, {recursive:true, force:true}).'
  - SC-05 median is 0.063 ms against the 5 ms bound. That holds for this test host
    only (a signed gap), and threshold discrimination is still not shown.
  - Natural fail-first for SC-01, SC-04 and SC-05 at 87efcd8a is signature-absent.
    The semantic proof is mutants M1, M3 and L plus the FIFO perturbations.
  - The qa runner receipt reflects this host's environment, not CI. runs/** stays
    untracked until main commits the closed run record.
  - qa and pm executed tests. code-reviewer and security-reviewer reviewed statically.
    ui scoped out after measuring a 48-path census.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: omp-hooks.test.ts:4476ff green at the pin. Red at 87efcd8a, under M3
      (6 of 13) and when mkfifo fails (probe exit 3).
  - id: SC-02
    verdict: met
    method: automated
    evidence: 'omp-hooks.test.ts:2479ff: 13 refused rows red at 87efcd8a, 4 carve-out
      rows preserved, and the hook unchanged since c1''s mutants.'
  - id: SC-03
    verdict: met
    method: automated
    evidence: 'omp-hooks.test.ts:2527: 4 rows. The hook is byte-identical since the
      c1 mutants M7b and M8.'
  - id: SC-04
    verdict: met
    method: automated
    evidence: 'omp-hooks.test.ts:4525ff: 7/7 red at 87efcd8a. M1, retaken at f4048ad3,
      gives 9 pass / 4 fail.'
  - id: SC-05
    verdict: met
    method: automated
    evidence: omp-hooks.test.ts:4577 green, median 0.063 ms. This holds for the test
      host only.
  - id: SC-06
    verdict: met
    method: inspection
    evidence: 'pm, at f4048ad3: the fingerprint set comes from import.meta.url only,
      staleHookRefusal is the sole new export, the root is gateRoot(), and ls-tree
      lists only harness-hooks.ts.'
  - id: SC-07
    verdict: met
    method: automated
    evidence: test-omp-hooks.py gives 274/0 at the pin (runs/2026-11-27-05-validate-validator/qa/manifest-unit.json).
  - id: SC-08
    verdict: met
    method: automated
    evidence: bun run typecheck exits 0 at the pin and exits 1 (TS2554) at 87efcd8a
      with the pin's tests.
  - id: SC-09
    verdict: met
    method: inspection
    evidence: "SPEC.md \xA74.2 'Stale hook code (BUG-2566)' is byte-unchanged since\
      \ c1, and the T-02 verify gives 'SPEC 4.2 ok'."
  - id: SC-10
    verdict: pending
    method: uat
    evidence: The operator's UAT. The steps are in notes/uat.md (OQ-02), and no result
      is recorded yet.
  needs_approval: false
  severity_max: low
  matrix_ok: true
  coverage_gaps:
  - 'exact-BLOCKED carve-out unwitnessed by test (mutant M6 survives 34/34): advisory'
  - 'SC-05 threshold discrimination not shown: advisory'
  - SC-10 uat pending (operator)
  findings:
  - kind: substance
    scope: none
    severity: low
    reader: qa (F-2); code-reviewer
    summary: 'T-01 tests/unit/omp-hooks.test.ts:2467-2478,2504-2518: no test pins
      that the carve-out requires VERDICT to be exactly ''BLOCKED'' (mutant M6 survives).'
    why: This is carried from c1. SC-06 pins the predicate by inspection, and validate-digest
      still judges the yield. Advisory, not gating.
  - kind: substance
    scope: none
    severity: low
    reader: code-reviewer
    summary: 'T-01 tests/unit/omp-hooks.test.ts:4458-4465: staleTree() leaves its
      mkdtemp fixture trees behind with no teardown.'
    why: 'Hygiene only: about 13 temp trees accumulate per run, with no effect on
      correctness. Advisory. Repair with an afterEach rmSync.'
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
```
