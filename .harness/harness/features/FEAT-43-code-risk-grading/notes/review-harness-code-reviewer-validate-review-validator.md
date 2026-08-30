# FEAT-43 pinned code review — FAIL

**BLUF:** The immutable range cannot ship. The pinned grader returns `code_grade: fail`, including three gated grade-1 functions, and stage 1 found seven additional spec defects. Most seriously, comprehension filters are undercounted into a passing production grade, deleted Python files are rejected as unreadable, and a reviewer can bypass grading with `code_grade: n_a`. Spec compliance failed, so stage-2 code-quality review was not entered.

## Pin and complete scope

Both objects resolve as commits: base `df63193f7ec9798d9660904e0e4e7c78d52358f5`; review `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`. Reviewed `df63193..1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`. The sole commit is `1ac1bd03 feat: add code risk grading gate`; no `[harness:human]` commit is in scope.

The exact `git diff --name-only df63193..1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c` set is 48 files:

- `.claude/agents/harness-ai-dev.md`
- `.claude/agents/harness-backend-dev.md`
- `.claude/agents/harness-code-reviewer.md`
- `.claude/agents/harness-data-engineer.md`
- `.claude/agents/harness-dev-ops.md`
- `.claude/agents/harness-frontend-dev.md`
- `.claude/skills/harness-code-review/SKILL.md`
- `.claude/skills/harness-code-risk-grading/SKILL.md`
- `.claude/skills/harness/bin/check-plan-routes.py`
- `.claude/skills/harness/bin/code-grade.py`
- `.claude/skills/harness/bin/code_grade.py`
- `.claude/skills/harness/bin/gate_policy.py`
- `.claude/skills/harness/bin/run-unit-tests.sh`
- `.claude/skills/harness/bin/test-check-plan-routes.py`
- `.claude/skills/harness/bin/test-code-grade-cli.py`
- `.claude/skills/harness/bin/test-code-grade.py`
- `.claude/skills/harness/bin/test-gate-policy.py`
- `.claude/skills/harness/bin/test-validate-digest.py`
- `.claude/skills/harness/bin/validate-digest.py`
- `.harness/glossary.md`
- `.harness/harness.json`
- `.harness/harness/features/FEAT-43-code-risk-grading/answers/Q1-t09-owner-resolver.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/qa-build-qa-rerun.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/qa-build-qa.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-01-c0.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-01-c1.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-02-c0.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-02-c1.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-06-c0.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-07-c0.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-07-c1.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-simplify-apply.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-simplify-efficiency.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-simplify-reuse.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-T-03-c0.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-T-03-c1.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplify-altitude.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplify-simplification.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/research-T-10-t10-product.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-t06-eng.html`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-t06-eng.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/plan.yaml`
- `.omp/agents/harness-ai-dev.md`
- `.omp/agents/harness-backend-dev.md`
- `.omp/agents/harness-code-reviewer.md`
- `.omp/agents/harness-data-engineer.md`
- `.omp/agents/harness-dev-ops.md`
- `.omp/agents/harness-frontend-dev.md`

## Stage 1 — ranked must-fix findings

1. **HIGH · must_fix · grade-1 gate:** `.claude/skills/harness/bin/test-check-plan-routes.py:1379` introduces `case_27` at cyclomatic 8, cognitive 11, ABC 57.3, grade 1, driver `abc`. Input/state: merging this pinned range introduces that gated test function; wrong outcome: REQ-06's worst-grade prohibition fires, so the change cannot merge. **Owner route:** main session, T-09 enforcement-layer test.
2. **HIGH · must_fix · grade-1 gate:** `.claude/skills/harness/bin/test-gate-policy.py:55` introduces `main` at cyclomatic 1, cognitive 0, ABC 58.0, grade 1, driver `abc`. Same pinned-merge scenario violates REQ-06. **Owner route:** harness-backend-dev via engineering lead, T-07.
3. **HIGH · must_fix · grade-1 gate:** `.claude/skills/harness/bin/test-validate-digest.py:1723` introduces `run_code_grade_cases` at cyclomatic 15, cognitive 22, ABC 49.9, grade 1, driver `abc`. Same pinned-merge scenario violates REQ-06. **Owner route:** main session, T-08 enforcement-layer test.
4. **HIGH · must_fix · exact-grading fail-open:** `.claude/skills/harness/bin/code_grade.py:201-209` increments cyclomatic for each comprehension `for` but not each comprehension `if`, contradicting D-04/T-01's authoritative counting rule; the shipped fixture explicitly encodes the wrong result at `test-code-grade.py:35-36`. Input: a production function with one comprehension `for` and eight `if` clauses. Correct cyclomatic is 10 (grade 3, below the production bar); shipped code reports cyclomatic 2 and ABC 8.1 (grade 4), so it sails through. **Owner route:** harness-backend-dev via engineering lead, T-01. Refs: REQ-03/05/06, D-04, SC-01.
5. **HIGH · must_fix · false rejection/non-ratchet mismatch:** `.claude/skills/harness/bin/code-grade.py:72-87` gets changed names without status and tries `git show <head>:<path>` for deletions. Input: delete any Python file. Wrong outcome: the deleted path is reported as `PARSE ERROR`/`UNGRADED` and exits 3, although no head function exists to grade; the change is blocked for removing code. **Owner route:** harness-dev-ops via engineering lead, T-03. Refs: REQ-04/07, D-01/D-09.
6. **HIGH · must_fix · grading gate bypass:** `.claude/skills/harness/bin/validate-digest.py:735-739` decides whether `code_grade: n_a` is legal from the reviewer's `files_touched`, which is necessarily `[]` for this read-only persona, rather than from the reviewed diff. Input: any Python diff plus a reviewer return containing `code_grade: n_a`, `files_touched: []`, `VERDICT: PASS`. Wrong outcome: the validator accepts without grading. A targeted pinned probe returned `digest ok`. **Owner route:** main session, T-08. Refs: REQ-05/06, D-10, SC-19.
7. **HIGH · must_fix · configured-review crash:** reviewer schema accepts `severity_max: info` at `validate-digest.py:35,193`, but `gate_policy.py:11,64-65` rejects `info`; the reviewer branch invokes it at `validate-digest.py:743-748`. Input: a clean/advisory reviewer return with `severity_max: info`. Wrong outcome: validation raises `GatePolicyError` instead of accepting or returning a contract error. Targeted pinned probe reproduced the traceback. **Owner route:** main session T-08 with harness-backend-dev T-07. Refs: REQ-10/11.
8. **HIGH · must_fix · prior-revision discrimination lost at the immutable pin:** `test-check-plan-routes.py:1417-1435` and `test-validate-digest.py:1765-1775` extract `git show HEAD:...`; after the feature is committed, `HEAD` is the implementation under test, not its predecessor. Input: run the tests at review pin `1ac1bd03`. Wrong outcome: SC-16's “prior checker reports OK” case fails (targeted pinned run: `case_27b_prior_revision_false_ok`, current checker exits 1), while SC-20's copied current validator imports dependencies the “prior” directory does not contain and cannot prove predecessor acceptance. **Owner route:** main session, T-09 and T-08. Refs: SC-16/20.
9. **MED · must_fix · fixture acceptance omitted:** `test-code-grade.py:19-41` contains 11 fixtures, not SC-01's minimum 12; `bindings-and-calls` at line 22 has no written derivation, violating SC-02's “every fixture” rule. The comprehension fixture at lines 35-36 also derives the contradicted cyclomatic rule. Input: delete or misimplement an uncovered construct. Wrong outcome: the suite remains green without meeting the signed independent-oracle floor. **Owner route:** harness-backend-dev via engineering lead, T-01. Refs: SC-01/02.
10. **MED · must_fix · determinism proof omitted:** `test-code-grade-cli.py:104-110` copies the same repository twice but grades one explicit path in each; it never presents directory entries in a different order. Input: introduce order-sensitive changed-file enumeration. Wrong outcome: the required SC-04 discriminator stays green because neither invocation varies entry order. **Owner route:** harness-dev-ops via engineering lead, T-03. Ref: SC-04.

## Required grade-2 findings and written reasons (advisory, not must-fix)

- **MED:** `check-plan-routes.py:775` `main` — grade 2, cyclomatic 10, cognitive 13, ABC 30.9, driver `abc`. **Reason:** this entry point owns one route-check transaction—mode/root selection, owner-manifest resolution, plan processing, reporting, and exit status—so keeping the lifecycle together preserves one auditable outcome.
- **MED:** `code-grade.py:117` `main` — grade 2, cyclomatic 9, cognitive 11, ABC 27.3, driver `abc`. **Reason:** this is the single CLI lifecycle joining argparse validation, one of two report modes, deterministic serialization, and the process status.
- **MED:** `code_grade.py:319` `_body_hashes.collect` — grade 2, cyclomatic 9, cognitive 18, ABC 17.3, driver `cognitive`. **Reason:** the recursive internal AST walk keeps qualification, docstring exclusion, body hashing, and nested traversal local to the pre-image identity algorithm.
- **MED:** `code_grade.py:347` `gated_set` — grade 2, cyclomatic 8, cognitive 25, ABC 22.6, driver `cognitive`. **Reason:** this is the core ordered pre-image-resolution transaction (same name, same-body hash, rename path) and the single partition into gated versus informational records.
- **MED:** `test-code-grade.py:111` `check_changed_function_resolution` — grade 2, cyclomatic 5, cognitive 0, ABC 33.3, driver `abc`. **Reason:** SC-07 requires one integrated seven-way repository fixture and exact-set/individual-absence assertions; keeping its setup and checks together makes that cross-case invariant visible.
- **MED:** `test-code-grade.py:245` `main` — grade 2, cyclomatic 8, cognitive 11, ABC 30.0, driver `abc`. **Reason:** the test entry point deliberately orchestrates the fixture table, band coverage, nested-name check, direction pairs, diff-resolution fixture, worked examples, and delivery checks as one suite result.

These written reasons satisfy SC-15's inspection obligation but do not override the overall `code_grade: fail` or the three grade-1 high findings.

## Requirement, decision, and success-criterion disposition

- **REQ-01..11:** REQ-01/02/08 are met by the skill and ten agent injections; REQ-07 is met for ordinary head-side syntax/read errors; REQ-09's production owner-manifest resolution is present. REQ-03/05/06 fail on wrong exact grades and the grading bypass; REQ-04 fails for deletions; REQ-10/11 fail on the `info` vocabulary crash. The SC-16 proof for REQ-09 is not stable at the pin.
- **D-01..12:** D-02/03/05/06/07/08/12 match committed production content. D-01/D-09 mismatch on deletions; D-04 mismatches comprehension-if counting; D-10 is bypassable through `files_touched: []`; D-11's production resolution is present but its required prior-revision proof fails at the pin.
- **SC-01..20:** SC-01, SC-02, SC-04, SC-16, SC-19, and SC-20 are not met for the reasons above. SC-03 and SC-05..10 and SC-12..14/17 are represented by the pinned implementation/tests and the already-passed QA evidence. SC-11 is `verify: uat` and was not run in this prohibited-UAT review; no code-review finding is substituted for that separate gate. SC-15 is met by the six named reasons above.

### Inspection citations

- **SC-02:** independently re-derived and correct: empty fixture `test-code-grade.py:20-21` (base cyclomatic 1; all other counts zero); five-operand BoolOp `:25-26` (four extra operands, cyclomatic 5, cognitive 1, ABC 4.0); compare/not fixture `:33-34` (C = if 1 + compare operators 2 + `not` 1, cyclomatic 2, cognitive 1, ABC 4.0). Criterion still fails because line 22 has no derivation and lines 35-36 derive the wrong approved rule.
- **SC-15:** six reason demands and answers are recorded above from the pinned grading run.
- **SC-18:** the guidance states the cognitive score is a Sonar-style approximation and not SonarSource at `harness-code-risk-grading/SKILL.md:162-163`, excludes shell and TypeScript at `:163`, and states pre-existing below-bar code is not fixed/no ratchet at `:164-165`.

## Targeted evidence

- `/opt/homebrew/bin/python3 .claude/skills/harness/bin/code-grade.py --base df63193 --head 1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c` → exit 1; `PASSING: 77`; three grade-1 highs and six `REASON REQUIRED` lines listed above.
- Validator probe with Python diff semantics represented by the reviewer's normal `files_touched: []`, `code_grade: n_a`, and `VERDICT: PASS` → `digest ok` (bypass reproduced).
- Validator probe with `severity_max: info` → uncaught `GatePolicyError: invalid gate policy for severity_max: 'info'`.
- Targeted pinned `test-check-plan-routes.py` run reproduced `case_27b_prior_revision_false_ok`; unrelated `/usr/bin/python3 -P` failures in that run are the disclosed environment mismatch and are not source findings here.
