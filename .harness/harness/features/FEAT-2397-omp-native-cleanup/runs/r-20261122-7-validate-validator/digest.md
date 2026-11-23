# c3 — ESCALATE: scoped regression checks pass; installed QA gate rejects the delegated carry

At `1133d63c55c8994f7c809f7be73616d049ab163b`, T-01's fixture repair is correct in kind. Fresh QA: omp-hooks **247/0 with override set and 247/0 unset**; no-distribution **ALL PASS**, including case6. These are not whole-matrix runner receipts. The installed gate refused QA's scoped PASS: “matrix_ok: true but the matrix floor requires integration (test_matrix.<change_type>.always for this plan's tasks) and kinds: does not report it satisfied.” QA correctly returns ESCALATE/matrix_ok false; no receipts were fabricated. Its durable note now records the final refusal.

**Decision needed:** the delegated narrow ruling carries c1 full suites, but the installed gate requires fresh matrix evidence. Recommend an explicit authorization to widen to DEC-255's unit/integration runner receipts, rather than waiving or misrepresenting the gate. Main/operator owns the conflict; no further code rework is indicated. Exact command template: `python3 <managed-pin-checkout>/.claude/skills/harness/bin/run-unit-tests.py --kind <unit|integration> --shard 1/1 --manifest <absolute-this-run>/qa/manifest-<kind>.json`. No broader verification was run by this lead.

**Assessment and carry:** code measured 15 changed paths: 14 feature-record/evidence paths plus 13 insertions/1 deletion in omp-hooks.test.ts; zero production/workflow/Python/SC changes. The three changed TS callbacks pass qualitative assessment; numeric TS grades are excluded by the grading rules. Save/delete/restore preserves absent, empty and set values; normal sequential execution supports suite-local isolation. The assembled key complies with case6's semantic exemption for resolver-seam test setup, not production root resolution. No claim of arbitrary concurrent-suite safety. c2 goalcheck and c1 security/UI PASS carry under the ruling; none was freshly dispatched. c1 full-suite evidence is historical assurance, not fresh c3 matrix satisfaction.

Natural red is pinned in `notes/fix-c2-evidence/red-ci-env.txt`: five matching host-core cases failed; QA measured its test blob identical to the pre-fix range base. No new mutation or cross-file env-leak probe was run.

**One deduplicated advisory:** code's low/form T-01 finding and QA's nonblocking question describe the same README claim. `notes/c1-evidence/README.md:75–77` asserts INV-29 base parity, but its cited `checks-job-local.txt` is head-only and untracked at the pin. Qualify that sentence; no re-gate needed. Both appended corrections correctly retract FEAT-2225's “host-environmental” label and the BUG-1290 supposed failures while preserving original text. The ship correction itself does not assert base parity. Source repair is not wrong in kind; no substantive must-fix exists.

**Attribution:** cycles_used **1**, for the post-c2 CI FAIL routed back (DEC-157), not for two readers or a third validate run. This is rework round 2/2; no additional code cycle is authorized. The unresolved issue is gate/scope compatibility. Reader artifacts: `notes/review-harness-qa-c3.md`, `notes/review-harness-code-reviewer-c3.md`; carried sources: c2 and c1 validator digests. Main was notified of the gate conflict and documentary qualification; no decision was available before return.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: 1133d63c fixture fix is correct and scoped checks pass; installed QA matrix
    gate rejects delegated carry, requiring a scope ruling.
  open_questions:
  - id: Q-GATE
    question: "QA's scoped PASS was refused: 'matrix_ok: true but the matrix floor\
      \ requires integration (test_matrix.<change_type>.always for this plan\u2019\
      s tasks) and kinds: does not report it satisfied.' The delegated ruling authorizes\
      \ only three scoped checks and carries c1 full suites, while the installed gate\
      \ requires fresh matrix evidence. Recommend explicitly authorizing DEC-255 production\
      \ unit/integration runners with this run's receipts; do not waive the refusal\
      \ or represent carried suites as fresh. Rework round 2/2 is exhausted; the repair\
      \ is not wrong in kind and no additional code cycle is indicated."
    blocking: true
  files_touched: []
  expertise_update: []
  team: validate
  steps_run: 2
  cycles_used: 1
  members:
  - step: qa
    persona: harness-qa
    verdict: ESCALATE
    headline: Scoped omp-hooks247/0 set and unset; no-distribution ALL PASS; installed
      gate refuses scoped matrix clearance.
    files_touched: []
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: T-01 repair correct in kind; zero production/SC delta; one low/form
      README evidence qualification.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: 'Carried c1 PASS under delegated ruling: zero production delta and no
      SC touched; not rerun.'
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Carried c1 PASS/scope-out under delegated ruling: zero production/UI
      delta and no SC touched; not rerun.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: 'Carried c2 goalcheck PASS under delegated ruling: zero production delta
      and no SC touched; not rerun.'
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'Exact delta eda06a685fe3aeb89a02d20cffd5a359b08d3c13..1133d63c55c8994f7c809f7be73616d049ab163b:
    code measured15 paths,14 feature-record/evidence paths and only tests/unit/omp-hooks.test.ts
    outside them,13 insertions/1 deletion. Zero production/workflow/Python/SC changes
    supports delegated carry.'
  - 'Fresh QA commands at pin: HARNESS_PROJECT_DIR="$PWD" bun test tests/unit/omp-hooks.test.ts
    and env -u HARNESS_PROJECT_DIR bun test tests/unit/omp-hooks.test.ts each247 pass/0
    fail/1575 assertions/exit0; python3 tests/unit/test-no-distribution.py ALL PASS,
    including all10 case6 lines.'
  - Natural fail-first red at e1cd52705ef20c2b36d38e00e3e9ad210ad93496:2 pass/5 fail/exit1,
    matching repaired host-core block. QA measured its test blob identical to range
    base. No rerun of reported red.
  - Code assessed all3 changed TS callbacks qualitatively pass; numerical TS grading
    excluded by governing examples, no changed Python functions. Undefined/empty/set
    values restore correctly; isolation claim is suite-local under ordinary sequential
    execution, not arbitrary concurrency.
  - 'Both record corrections append without rewriting history and accurately withdraw
    FEAT-2225''s host-environmental attribution and BUG-1290''s supposed failures.
    One duplicate advisory retained: README INV-29 base parity lacks paired evidence;
    ship correction does not itself assert parity. Main owns qualification, no re-gate
    needed.'
  - QA final ESCALATE overrides its earlier scoped PASS wording; artifact corrected
    to record actual refusal and matrix_ok:false. No fresh runner receipts exist and
    no whole-suite clearance is claimed.
  - cycles_used1 attributes the CI FAIL routed back per DEC-157 and delegated ruling,
    not reader count or run count. No additional source rework cycle occurred. No
    fix, merge, repin or verification by this lead.
  sc_status:
  - id: SC-04
    verdict: met
    method: inspection
    evidence: Carried c2 PM pinned provenance closure; no plan/SC/production delta
      in c3. Other SC and23 decision-disposition assessments likewise carry from c2/c1,
      not fresh goalcheck.
  needs_approval: true
  severity_max: low
  matrix_ok: false
  coverage_gaps:
  - No fresh full unit/integration runner receipts in c3; delegated carry conflicts
    with installed matrix floor. Three scoped commands cannot satisfy the fresh whole-matrix
    receipt gate.
  - No new delete-line mutation proof or cross-file environment-leak probe; natural
    red and set/unset green bracket this suite-local repair.
  findings:
  - kind: form
    scope: none
    severity: low
    reader: code-reviewer
    summary: 'T-01: README baseline-equivalence claim cites a head-only, untracked
      receipt.'
    why: "notes/c1-evidence/README.md:75\u201377 says both remaining host reds are\
      \ the same at base, but checks-job-local.txt records only c1eb9eaa. Its citation\
      \ cannot establish INV-29 baseline equivalence. Qualify the statement or cite\
      \ paired evidence; no re-gate needed. QA independently raised the same advisory;\
      \ consolidated as one finding."
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
    status: skipped
    persona: harness-security-reviewer
    reason: Carried c1 PASS under delegated ruling; measured zero production delta/no
      SC touched.
  - reader: ui
    status: skipped
    persona: harness-ui-reviewer
    reason: Carried c1 PASS/scope-out under delegated ruling; measured zero production/UI
      delta/no SC touched.
  - reader: goalcheck
    status: skipped
    persona: harness-pm
    reason: Carried c2 PASS under delegated ruling; measured zero production delta/no
      SC touched.
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2397-omp-native-cleanup/.harness/harness/features/FEAT-2397-omp-native-cleanup/runs/r-20261122-7-validate-validator/digest.md
```
