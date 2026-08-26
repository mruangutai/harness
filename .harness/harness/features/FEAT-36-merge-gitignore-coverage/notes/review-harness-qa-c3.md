# QA gate — PASS

Review pin: `be27d99454352e581fdf7cbace20fb52d0f45133`. The committed behavioral coverage meets REQ-01..REQ-05 and SC-01..SC-06; no in-scope coverage gap remains.

```yaml
matrix_ok: true
severity_max: n/a
must_fix: []
coverage_gaps: []
commands:
  - cmd: "python3 .agents/skills/harness/bin/test-merge-gitignore.py && .agents/skills/harness/bin/run-unit-tests.sh --kind all"
    exit: 0
    result: "direct 7/7; all runner passed 46 registered scripts; no MISCONFIGURED or KIND-DRIFT output"
  - cmd: "python3 .agents/skills/harness/bin/test-merge-gitignore.py"
    exit: 0
    result: "7 named behavioral cases passed"
  - cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind unit"
    exit: 0
    result: "23 registered unit scripts passed"
  - cmd: ".agents/skills/harness/bin/run-unit-tests.sh --kind integration"
    exit: 0
    result: "23 registered integration scripts, including test-merge-gitignore.py, passed"
kinds:
  - {kind: unit, state: satisfied, discovery: "23 scripts"}
  - {kind: integration, state: satisfied, discovery: "23 scripts; explicit test-merge-gitignore.py registration"}
sc_evidence:
  - {id: SC-01, evidence: ".agents/skills/harness/bin/test-merge-gitignore.py:36-47"}
  - {id: SC-02, evidence: ".agents/skills/harness/bin/test-merge-gitignore.py:50-83"}
  - {id: SC-03, evidence: ".agents/skills/harness/bin/test-merge-gitignore.py:86-108"}
  - {id: SC-04, evidence: ".agents/skills/harness/bin/test-merge-gitignore.py:111-120"}
  - {id: SC-05, evidence: ".agents/skills/harness/bin/test-merge-gitignore.py:123-136"}
  - {id: SC-06, evidence: ".agents/skills/harness/bin/run-unit-tests.sh:18; .harness/harness.json test_kinds.integration.detect; git diff 0fa8f33..be27d99 -- merge-gitignore.sh (empty)"}
open_questions: []
files_touched:
  - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-qa-c3.md
```

The seven real-subprocess cases are `preserves_existing_content`, both complete/incomplete read-only check cases, absent and partial target cases, second-merge byte identity, and explicit-root/caller-CWD isolation. The incomplete-check assertion compares the emitted bullet set exactly to `RULES[1:]` (`test-merge-gitignore.py:71-82`); committed B-1 evidence records its intended superset mutant failing only that case (`notes/receipt-harness-dev-ops-fix-b1-eng.md:11-32`).

Test-first evidence is credible: the initial committed receipt records the new suite passing the untouched utility and the same SHA-256 before/after (`notes/receipt-harness-dev-ops-T-01-c0.md:7-59`); all feature history leaves the utility unchanged. Baseline and pin both hash to `86cfff73c88a2baa1c74d2e516e3608e38954fef1c9e4ef344113b011e425c12`. The substantive pin delta contains only the new suite plus its runner/config registration; the working tree separately has a modified `feature.json` bookkeeping trace, not attributed to this review.
