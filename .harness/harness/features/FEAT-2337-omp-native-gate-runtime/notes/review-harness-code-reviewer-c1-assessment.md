# FEAT-2337 c1 — assessment completion

**FAIL — canonical Python grading passes; T-03's normative clean-tree contract still omits the approved exception.** This supersedes the prior note's unconditional compliance PASS, not its unchanged T-01/T-02 quality observations. No new quality audit, remediation or re-pin occurred.

## Scope and reconciliation

Reviewed `0d7326e40137dfce63f5b7b33af95ee126f90971..6143625f5262f246d51d642662899a44a8d545d9`, excluding feature records. Direct pinned `git show`/diff and commit chronology are the evidence below. Working-tree dirt was confined to this feature's records; no human-tagged commits were found. No managed pin was created, so none needs cleanup. Prior review and PM goalcheck were read as durable handoffs.

- **GC-01: reject the claimed conditional-ruling violation.** `answers-2026-11-22-grading-base.md:18–19` requires movement only if another main merge lands **before T-03's tip is committed**. T-03 committed as `352ceebe` at 12:52:25 -0800; merge `27f8d569` occurred at 13:06:39 -0800, importing `0d7326e4`. Thus this merge does not meet that condition. Later `a6750a34` simplification did not change `test-code-grade.py`; the final build seam is not a new T-03 implementation commit. Retain the narrower conclusion that `d04c765a` was an authorized task-time base. Withdraw any implication that it equals the final review merge-base or excludes all subsequently imported work. Over-inclusion is real, but SC-08 requires every feature test to grade at least 3, not an explicit prohibition on grading additional tests. Neither that criterion nor the conditional ruling establishes PM's requested mandatory base change. The canonical review range below independently excludes that upstream work.
- **GC-02 retained — substance / med / T-03 / SC-09, D-02; must fix.** At the pin, `DECISIONS.md:8428–8433` requires a clean working tree without qualification; `SPEC.md:1604–1606`, `.claude/skills/harness/teams/fix.yaml:90`, `.omp/agents/harness-qa.md:60` and `.omp/agents/harness-validator-lead.md:101` repeat that contract. The approved follow-up in `answers-2026-11-22-fix-run-receipts.md:44–51` expressly permits tracked/untracked dirt inside the trusted feature directory. `_fix_lineage` at `.claude/skills/harness/bin/validate-digest.py:2576–2589` implements that exception; `tests/integration/test-validate-digest.py:2372–2373` asserts acceptance of a feature-local uncommitted note. **Scenario:** a live fix run has its normal dirty feature.json/notes; a maintainer following the standing clean-tree requirement treats the run as ineligible even though the approved verifier accepts it. This is a conflicting normative eligibility rule, not formatting or digest shape. Land the settled exception in the decision and shorthand; do not tighten the code or seek a new approval. Withdraw prior SC-09 full-compliance claim. SC-09 inspection is therefore partial at these exact pinned sites; SC-10's earlier inspection remains unchanged.

## Canonical changed-Python grading — measured

Executed once from the feature checkout (grader source identical to the pin), selecting committed objects with:

`python3 .claude/skills/harness/bin/code-grade.py --base 0d7326e40137dfce63f5b7b33af95ee126f90971 --head 6143625f5262f246d51d642662899a44a8d545d9`

Canonical terminal output: **`PASSING: 152`**; tool returned successfully in 1.16 seconds. Every emitted record was `RESULT: PASS`; no `SEVERITY: high` or `REASON REQUIRED` record. Therefore **code_grade: pass**, replacing the prior inference. Lowest emitted production grade: 4. Grade-3 test records (all `BAR: 3`, `DRIVER: abc`, `RESULT: PASS`):

| Path / function (line) | Cyclomatic | Cognitive | ABC | Grade |
|---|---:|---:|---:|---:|
| integration/test-integration-shard-aggregation.py / repository (63) | 3 | 2 | 21.0 | 3 |
| integration/test-omp-native-gate-runtime.py / run_composition (515) | 6 | 4 | 25.1 | 3 |
| integration/test-validate-digest.py / _rx_shim_cases (2260) | 1 | 0 | 21.8 | 3 |
| integration/test-validate-digest.py / run_bug919_qa_matrix_cases (2511) | 1 | 1 | 22.1 | 3 |
| integration/test-validate-digest.py / _qa_unknown_authorization_case (3922) | 3 | 4 | 20.6 | 3 |

Paths in the table are under `tests/`; cognitive values are the tool's Sonar-style approximation. No suites, benchmark, builds, lint, formatters or mutants were rerun. Existing QA runner-exit failure and owner-manifest escalation are not reclassified by this grading pass. No open question remains for this bounded reconciliation; the existing T-03 owner can land GC-02 under the approved ruling.
