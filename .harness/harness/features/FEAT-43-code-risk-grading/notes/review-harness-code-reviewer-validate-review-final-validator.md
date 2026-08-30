# FEAT-43 final pinned code review — FAIL

**BLUF:** Stage 1 fails, so the immutable range cannot ship and stage 2 was not entered. The real grader returns `code_grade: fail`; one changed test function is still grade 1, and the enforcement wiring also makes every below-bar grade 2 fail even after its required reason is written. Four additional signed inspection/automated criteria remain unproved. The exhausted 10/10 rework budget makes these final blockers.

## Pin, human edit, and complete census

Both objects resolve as commits: base `df63193f7ec9798d9660904e0e4e7c78d52358f5`; review pin `45328d7a280d251a94b09672a7b6724d55a79f83`. Reviewed exactly `df63193..45328d7a280d251a94b09672a7b6724d55a79f83`, never `HEAD`. The range contains three commits; `[harness:human]` commit `45328d7a280d251a94b09672a7b6724d55a79f83` is in scope. Its five paths—both reviewer agent definitions, `test-check-plan-routes.py`, `test-validate-digest.py`, and `validate-digest.py`—were reviewed as new work.

The exact complete `git diff --name-only` census is 48 files (6,865 insertions, 58 deletions), all inspected before scoping:

1. `.claude/agents/harness-ai-dev.md`
2. `.claude/agents/harness-backend-dev.md`
3. `.claude/agents/harness-code-reviewer.md`
4. `.claude/agents/harness-data-engineer.md`
5. `.claude/agents/harness-dev-ops.md`
6. `.claude/agents/harness-frontend-dev.md`
7. `.claude/skills/harness-code-review/SKILL.md`
8. `.claude/skills/harness-code-risk-grading/SKILL.md`
9. `.claude/skills/harness/bin/check-plan-routes.py`
10. `.claude/skills/harness/bin/code-grade.py`
11. `.claude/skills/harness/bin/code_grade.py`
12. `.claude/skills/harness/bin/gate_policy.py`
13. `.claude/skills/harness/bin/run-unit-tests.sh`
14. `.claude/skills/harness/bin/test-check-plan-routes.py`
15. `.claude/skills/harness/bin/test-code-grade-cli.py`
16. `.claude/skills/harness/bin/test-code-grade.py`
17. `.claude/skills/harness/bin/test-gate-policy.py`
18. `.claude/skills/harness/bin/test-validate-digest.py`
19. `.claude/skills/harness/bin/validate-digest.py`
20. `.harness/glossary.md`
21. `.harness/harness.json`
22. `.harness/harness/features/FEAT-43-code-risk-grading/answers/Q1-t09-owner-resolver.md`
23. `.harness/harness/features/FEAT-43-code-risk-grading/notes/qa-build-qa-rerun.md`
24. `.harness/harness/features/FEAT-43-code-risk-grading/notes/qa-build-qa.md`
25. `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-01-c0.md`
26. `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-01-c1.md`
27. `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-02-c0.md`
28. `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-02-c1.md`
29. `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-06-c0.md`
30. `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-07-c0.md`
31. `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-T-07-c1.md`
32. `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-simplify-apply.md`
33. `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-simplify-efficiency.md`
34. `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-simplify-reuse.md`
35. `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-T-03-c0.md`
36. `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-T-03-c1.md`
37. `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplify-altitude.md`
38. `.harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplify-simplification.md`
39. `.harness/harness/features/FEAT-43-code-risk-grading/notes/research-T-10-t10-product.md`
40. `.harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-t06-eng.html`
41. `.harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-t06-eng.md`
42. `.harness/harness/features/FEAT-43-code-risk-grading/plan.yaml`
43. `.omp/agents/harness-ai-dev.md`
44. `.omp/agents/harness-backend-dev.md`
45. `.omp/agents/harness-code-reviewer.md`
46. `.omp/agents/harness-data-engineer.md`
47. `.omp/agents/harness-dev-ops.md`
48. `.omp/agents/harness-frontend-dev.md`

No scope leakage was found: implementation, generated adapters, signed plan status/correction, test registration, glossary, and durable build evidence all trace to REQ-01..11 or D-01..12.

## Stage 1 — spec compliance findings

### 1. HIGH · must_fix · grade-2 reasons cannot produce the promised passing outcome

`code-grade.py:131-134` returns exit 1 for **any** record below its surface bar, including grade 2, while `validate-digest.py:755-763` rejects `code_grade: fail` with `VERDICT: PASS`. The text report itself labels every current grade-2 record `RESULT: FAIL` (`code-grade.py:110-122`). Input/state: a production or test function grades 2 and the reviewer writes the required per-function reason. Wrong outcome: the CLI still returns fail and the digest validator still forbids PASS; there is no reason field or override in either seam. This contradicts REQ-06 and the shipped guidance at `harness-code-risk-grading/SKILL.md:169-170`, which say grade 2 proceeds with a written reason. It also makes the nine SC-15 reasons below unable to satisfy the actual enforcement path.

### 2. HIGH · must_fix · grade-1 gate remains open (prior F-01)

The exact pinned grader reports `.claude/skills/harness/bin/test-check-plan-routes.py:1399` `case_27` at cyclomatic 6, cognitive 6, ABC 50.0, grade 1, driver `abc`, bar 3, `RESULT: FAIL`, severity high. Input/state: merge this pinned range. Wrong outcome: the range introduces a worst-grade function, so REQ-06's explicit cannot-merge rule fires. This is the sole current grade-1 outcome; the three earlier grade-1 functions were reduced, but F-01 is not closed.

### 3. MED · must_fix · one of twelve fixtures still has no hand derivation (prior F-07)

`test-code-grade.py:22` contains `bindings-and-calls` and its expected tuple but no adjacent derivation; every other nearby fixture has the required `A/B/C`, cyclomatic, cognitive, and arithmetic comment (`:20-47`). Input/state: assignment/call counting changes and the tuple at line 22 is updated to the tool's output. Wrong outcome: the suite stays green with no independent oracle, recreating the check-only-against-itself shape SC-02 forbids. The minimum count is now 12 and its assertion exists at `:306`, so only the missing every-fixture derivation premise of F-07 remains.

Independent re-derivation at the pin confirms three other fixtures: `grade5-empty` (`:20-21`) has A/B/C 0, base cyclomatic 1, cognitive 0, ABC 0.0, grade 5; `control-basics` (`:23-24`) has A=3, B=0, C=3, cyclomatic 4, cognitive 2, ABC $\sqrt{18}=4.2$, grade 5; `comprehension-filters` (`:44-47`) has A=1, B=1, C=11, cyclomatic $1+1+8=10$, cognitive 0, ABC $\sqrt{123}=11.1$, grade 3. Those correct examples do not cure line 22.

### 4. MED · must_fix · SC-03 now checks metric movement but no longer checks grade movement

`test-code-grade.py:316-320` selects the named metric and asserts only that metric's numeric direction. It never compares `record.grade`. Input/state: a banding regression makes before/after grades equal while cognitive/cyclomatic/ABC still moves in the intended direction. Wrong outcome: all six direction checks stay green even though SC-03 requires four strict grade decreases and two strict grade increases. Prior F-09's named-metric premise is fixed, but the complementary grade discriminator was removed rather than retained.

### 5. MED · must_fix · the adverse-order proof still presents the same Git order (prior F-08)

`test-code-grade-cli.py:116-129` creates `zeta.py` then `alpha.py` in one repository and the reverse in the other, commits both, then compares diff-mode output. Git tree and `git diff --name-status` enumeration are path-canonical; filesystem creation order is not retained in either commit, so both invocations present the same ordered entries to the grader. Input/state: changed-file processing becomes order-sensitive. Wrong outcome: this SC-04 test remains green because it never supplies a differently ordered input, despite its two setup loops differing. F-08 therefore remains open.

### 6. MED · must_fix · SC-17's four boundary discriminators are absent

The implementation currently selects bar 4 for production and 3 for test from configured active `test_kinds` (`code-grade.py:42-56`), but `test-code-grade-cli.py:51-81` exercises only production grade 2/1 failures and a test grade 3 pass. It does not assert production grade 4 passes, production grade 3 fails, or test grade 2 fails. Input/state: the bars relax to production 3 and test 2. Wrong outcome: every shipped assertion still passes—production grade 2 still fails and test grade 3 still passes—so the exact SC-17 thresholds can drift silently.

These six items are substantive. The first two are high; all six are final blockers because the rework budget is exhausted.

## Pinned code grade and all SC-15 reasons

Exact command:

```text
/opt/homebrew/bin/python3 .claude/skills/harness/bin/code-grade.py --base df63193 --head 45328d7a280d251a94b09672a7b6724d55a79f83
```

Outcome: exit 1, `PASSING: 81`, `code_grade: fail`; one grade-1 outcome is recorded above. The command emitted nine grade-2 reason demands. Each current demand has a written per-function answer here:

1. `check-plan-routes.py:775` `main` — cyclomatic 10, cognitive 13, ABC 30.9, driver `abc`. **Reason:** it owns one route-check transaction: mode/root selection, owner-manifest resolution, plan processing, deviation/invariant accumulation, reporting, and exit status; keeping that lifecycle together preserves one auditable outcome.
2. `code-grade.py:137` `main` — cyclomatic 9, cognitive 11, ABC 27.3, driver `abc`. **Reason:** it is the single CLI lifecycle joining argument validation, path-versus-diff report selection, deterministic sorting, text/JSON serialization, and process status.
3. `code_grade.py:322` `_body_hashes.collect` — cyclomatic 9, cognitive 18, ABC 17.3, driver `cognitive`. **Reason:** the recursive internal AST walk keeps qualification, docstring exclusion, body hashing, and nested traversal local to one pre-image identity algorithm.
4. `code_grade.py:350` `gated_set` — cyclomatic 8, cognitive 25, ABC 22.6, driver `cognitive`. **Reason:** it is the core ordered pre-image-resolution transaction (same name, body hash, rename path) and the single partition into gated versus informational records.
5. `test-code-grade-cli.py:96` `test_diff_and_determinism` — cyclomatic 3, cognitive 3, ABC 29.2, driver `abc`. **Reason:** one integrated repository fixture deliberately couples deletion behavior, odd-path rename handling, diff gating, copied checkout paths, CWD variation, and determinism assertions.
6. `test-code-grade.py:136` `check_changed_function_resolution` — cyclomatic 5, cognitive 0, ABC 33.3, driver `abc`. **Reason:** SC-07 requires one seven-way repository transition and exact-set plus individual-exclusion assertions; one fixture keeps that cross-case invariant visible.
7. `test-code-grade.py:296` `main` — cyclomatic 8, cognitive 11, ABC 35.7, driver `abc`. **Reason:** the test entry point deliberately orchestrates fixture bands, nested qualification, NUL-safe paths, direction pairs, change attribution, worked examples, and ten delivery checks as one suite outcome.
8. `test-gate-policy.py:55` `check_policy_loading` — cyclomatic 1, cognitive 0, ABC 36.1, driver `abc`. **Reason:** the cases share one temporary configuration lifecycle and collectively prove four named gate reads plus loud invalid-shape, missing, malformed, and unreadable failures.
9. `test-validate-digest.py:1760` `run_code_grade_cases` — cyclomatic 11, cognitive 16, ABC 38.1, driver `cyclomatic+cognitive+abc`. **Reason:** this is one integration transaction for the reviewer cutover: required grade, reviewed-diff `n_a`, severity/policy outcomes, missing gates, and predecessor discrimination under controlled fixture configuration.

The reasons satisfy SC-15's inspection requirement but cannot override the `code_grade: fail` or the grade-2 enforcement contradiction in finding 1.

## Prior findings F-01..F-12 at the new pin

- **F-01 grade-1 gate — OPEN:** reduced from three functions to one, but `case_27` remains grade 1/high as finding 2.
- **F-02 comprehension filters — CLOSED:** `_visit_comprehension` counts every `for` and every `if` at `code_grade.py:201-209`; the eight-filter fixture derives cyclomatic 10 at `test-code-grade.py:44-47`; focused grader tests pass.
- **F-03 deletion behavior — CLOSED:** diff enumeration skips `D` statuses before head reads at `code-grade.py:73-92`; the real CLI fixture deletes `src/deleted.py` and asserts it is neither output nor ungraded at `test-code-grade-cli.py:96-115`.
- **F-04 `n_a` diff basis — CLOSED:** `reviewed_python_change` uses the required `reviewed` range and NUL-separated Git output (`validate-digest.py:540-556`), not reviewer `files_touched`; the targeted Python-range probe was rejected with the exact `only valid when the reviewed diff has no Python file` message.
- **F-05 `info`/`none` vocabulary — CLOSED:** reviewer adapters, validator, and `gate_policy.SE​​VERITIES` use `none`; a targeted `severity_max: info` probe returned a clean contract violation, not `GatePolicyError` or traceback.
- **F-06 true predecessor — CLOSED:** both tests pin `PRE_FEATURE_REVISION` to `df63193...` (`test-check-plan-routes.py:1379-1397`; `test-validate-digest.py:18,1741-1758`); focused route and digest scripts pass, including predecessor discrimination.
- **F-07 twelve derived fixtures — PARTLY OPEN:** twelve/count assertion and all five grades are present (`test-code-grade.py:19-48,306-307`), but line 22 remains underived as finding 3.
- **F-08 adverse ordering — OPEN:** creation order differs, but actual Git enumeration does not; finding 5.
- **F-09 named metric movement — CLOSED AS TO ITS PREMISE:** lines `316-320` now read and compare the named metric. SC-03 nevertheless remains unmet because grade movement is no longer asserted; finding 4.
- **F-10 NUL-safe paths — CLOSED:** both diff readers use `--name-status -z` (`code-grade.py:73-92`; `code_grade.py:302-316`), and tab/newline rename reaches the grading record at `test-code-grade.py:207-229`.
- **F-11 approximation label — CLOSED:** JSON carries `cognitive_method`, text labels `COGNITIVE` with it (`code-grade.py:50-56,110-118`), and both are asserted at `test-code-grade-cli.py:64-78`.
- **F-12 per-record bar/outcome — CLOSED:** text emits `BAR` and `RESULT` per function at `code-grade.py:113-123`; mixed production/test values are asserted at `test-code-grade-cli.py:64-69`.

## Requirements, decisions, and success criteria

- **REQ-01..11:** REQ-01/02/04/05/07/08/09/10/11 are implemented at the pinned bytes. REQ-03 is not fully proven because SC-04's adverse-order discriminator is ineffective. REQ-06 fails both because a grade-1 function remains and because grade 2 cannot proceed after a reason.
- **D-01..12:** D-01/02/03/05/07/08/09/10/11/12 match the implementation. D-04's counting implementation is pinned, but its required independent evidence is incomplete at fixture line 22. D-06's numeric bands and bar lookup match, but SC-17 does not discriminate all four settled bar boundaries and the hard exit conflicts with REQ-06's grade-2 exception.
- **SC-01 — MET:** 12 fixtures, all five bands, exact fields, and minimum/band assertions (`test-code-grade.py:19-48,299-307`).
- **SC-02 — NOT MET:** three independent re-derivations are recorded above, but `bindings-and-calls` has no written derivation (`:22`).
- **SC-03 — NOT MET:** six named metrics move, but no test asserts the required strict grade movement (`:316-320`).
- **SC-04 — NOT MET:** absolute path/CWD/output comparison exists, but the changed entries are not actually presented in adverse order (`test-code-grade-cli.py:116-129`).
- **SC-05 — MET:** each author field, plus cognitive qualification/bar/result, is asserted separately (`test-code-grade-cli.py:64-78`).
- **SC-06 — MET:** named ungraded syntax error, excluded passing count, and distinct exit 3 (`:85-93`).
- **SC-07/08 — MET:** exact gated set, each exclusion, informational old grade 1, moves, and retained paths (`test-code-grade.py:136-203`).
- **SC-09/10 — MET:** worked examples and ten per-agent/per-tree deliveries (`:233-286`).
- **SC-11 — PENDING UAT:** deliberately not run under this review's no-UAT constraint; no code-review claim substitutes for it.
- **SC-12/13 — MET:** configured review/QA evaluation and all four loud policy loads are in `gate_policy.py:33-87` and focused tests.
- **SC-14 — MET:** grade-2 demand presence and no-grade-2 absence are asserted (`test-code-grade-cli.py:64-81`).
- **SC-15 — MET BY INSPECTION:** all nine current reason demands are answered above.
- **SC-16 — MET:** owner-manifest control, pinned predecessor false-OK, and unreadable-owner refusal pass at `test-check-plan-routes.py:1399-1476`.
- **SC-17 — NOT MET:** correct current implementation, missing four signed boundary discriminators; finding 6.
- **SC-18 — MET BY INSPECTION:** approximation/not-SonarSource, shell/TypeScript exclusion, and no-ratchet limit appear together at `harness-code-risk-grading/SKILL.md:162-165`.
- **SC-19 — MET:** omission/fail enforcement is present and focused digest tests pass.
- **SC-20 — MET:** policy changes validator outcome, missing gates fail loudly, and the pinned predecessor accepts; focused digest script passes.

## Targeted commands and outcomes

- `git rev-parse --verify 'df63193^{commit}'`; `git rev-parse --verify '45328d7...^{commit}'`; exact `git diff --name-only` → both commits resolved; 48-file census above.
- Exact pinned grader command above → exit 1; `code_grade: fail`; `PASSING: 81`; one grade-1 and nine grade-2 demands.
- `/opt/homebrew/bin/python3 .../test-code-grade.py` → `PASS test-code-grade` (F-02/F-07/F-09/F-10 probe).
- `/opt/homebrew/bin/python3 .../test-code-grade-cli.py` → `PASS test-code-grade-cli` (F-03/F-08/F-11/F-12 probe).
- Two digest payload probes through `/opt/homebrew/bin/python3 .../validate-digest.py harness-code-reviewer` → Python-range `n_a` rejected exit 1; `severity_max: info` rejected exit 1 without traceback.
- `PATH=/opt/homebrew/bin:/usr/bin:/bin /opt/homebrew/bin/python3 .../test-check-plan-routes.py` → `ALL PASS`, including `case_27b_prior_revision_false_ok` (F-06). An initial invocation omitted the child-process PATH override and produced system-Python `-P` environment failures; it is discarded as source evidence and recorded here rather than hidden.
- `PATH=/opt/homebrew/bin:/usr/bin:/bin /opt/homebrew/bin/python3 .../test-validate-digest.py` → `ALL PASSED`, including `code-grade and review-policy gates` and predecessor acceptance (F-04/F-05/F-06).

No formatter, linter, project-wide build/suite, goal-check, UAT, ship, merge, deploy, or HEAD movement was performed.

## Stage 2 — code quality

Not entered. Stage 1 has six substantive spec violations, and the dispatch explicitly conditioned the full quality pass on stage 1 passing. This preserves the required stage order rather than spending a quality review on code that still builds the wrong enforcement contract.

## Review result

- Verdict: **FAIL**
- `severity_max`: **high**
- Ranked substantive findings: **6**
- Grade-2 advisory findings/reasons: **9**
- Total findings: **15**
- `must_fix`: **6 final blockers**
- Scope creep: none
- Open questions: none
- File written by reviewer: `.harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-code-reviewer-validate-review-final-validator.md`
