# FEAT-43 final pinned UI/CLI review

**FAIL.** The CLI output presentation defects F-11 and F-12 are closed: every text record now names its bar and result and qualifies cognitive complexity as a Sonar-style approximation, while JSON carries the bar and the same qualification. The immutable grading run nevertheless reports one grade-1 function, and the fixture corpus still has only eleven written derivations for twelve fixtures. Those are final blockers because the rework budget is exhausted.

## Pin, census, and UI scope

Both objects resolve: base `df63193f7ec9798d9660904e0e4e7c78d52358f5`; pin `45328d7a280d251a94b09672a7b6724d55a79f83`. The exact `git diff --name-only df63193..45328d7a280d251a94b09672a7b6724d55a79f83` census is **48 files**, identical in membership and count to the prior panel census:

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

Extension census: 34 Markdown, 10 Python, one HTML, one JSON, one shell, and one YAML. Direct object lookup confirms no feature `DESIGN.md` exists at the pin, and no approved prototype exists under `notes/prototypes/FEAT-43-code-risk-grading/`. The lone HTML file is a generated internal ship-review reading view whose own footer declares the Markdown as the record; the BRIEF explicitly says this feature has no component/UI surface. It is therefore not a governed feature UI, so dark/light parity is not a gate here. The dispatch expressly puts the adjacent CLI/reviewer text surface in scope, making this a Mode B review.

The CLI uses labelled, non-colour-only text and has no focus, hit-target, or theme state. Long values are not truncated by the renderer. Records are sorted by repository-relative path then line (`code-grade.py:151`); source audit cannot prove rendered terminal/browser wrapping or size, so a human check would be required for those dimensions.

## Findings, ranked

### 1. F-01 — high — final blocker: the immutable grading run contains a grade-1 function

`/opt/homebrew/bin/python3 .claude/skills/harness/bin/code-grade.py --base df63193 --head 45328d7a280d251a94b09672a7b6724d55a79f83` exits **1** and reports:

- `.claude/skills/harness/bin/test-check-plan-routes.py:1399` — `case_27`; cyclomatic 6, cognitive 6 (Sonar-style approximation), ABC 50.0, grade 1, driver `abc`, test bar 3, `RESULT: FAIL`, severity `high`.

Concrete scenario: the final reviewer runs the required grader over the immutable change and receives a high grade-1 finding. REQ-06 and the existing high-severity gate forbid a passing ship decision; the output is actionable, but the code does not meet the gate.

### 2. F-07 — med — final blocker: twelve fixtures do not have twelve written derivations

`test-code-grade.py:19-44` now contains twelve fixtures and `:301` enforces the minimum. Eleven have an adjacent comment deriving A/B/C, cyclomatic, cognitive, ABC arithmetic, grade, and driver. `bindings-and-calls` at `:22-24` has only its source and expected tuple; it has no written derivation. SC-02 requires a derivation beside **every** expectation.

Concrete scenario: an independent reviewer audits the twelve-oracle corpus without executing the grader. At `bindings-and-calls`, they must reverse-engineer why the tuple is `(1, 1, 0, 2, 2, 0, 2.8, 5, ...)`, so the claimed hand-checkable twelve-fixture evidence is only eleven complete derivations.

## F-01 through F-12 disposition

| Prior finding | Final disposition | Independent pinned evidence |
|---|---|---|
| F-01 grade-1 gate | **OPEN — high blocker** | Real pinned CLI exits 1; `case_27` is grade 1/high with ABC 50.0. The prior three grade-1 records fell to one, not zero. |
| F-02 comprehension filters | **CLOSED** | `code_grade.py:201-209` increments cyclomatic once per comprehension generator and once per filter; the eight-filter fixture at `test-code-grade.py:40-44` expects cyclomatic 10/grade 3. |
| F-03 deletion behavior | **CLOSED** | `_diff_paths` uses NUL-delimited name-status and excludes `D` before any head parse (`code-grade.py:73-93`); the deletion fixture asserts no deleted path and no UNGRADED heading (`test-code-grade-cli.py:96-114`). |
| F-04 `n_a` diff basis | **CLOSED** | `reviewed_python_change` resolves the declared `base..head` and inspects NUL-delimited changed paths, independent of `files_touched` (`validate-digest.py:540-557,747-756`). |
| F-05 `info`/`none` vocabulary | **CLOSED** | Validator and both reviewer adapters use `none`; the policy test accepts `none` and rejects `info` (`test-validate-digest.py:1727-1739`). |
| F-06 true predecessor discrimination | **CLOSED** | Both predecessor helpers pin `PRE_FEATURE_REVISION = df63193...`, git-show that object, and execute the copied old code (`test-check-plan-routes.py:1379-1445`; `test-validate-digest.py:1741-1758`). |
| F-07 12 derived fixtures | **OPEN — med blocker** | Count/minimum is fixed at twelve, but `bindings-and-calls` has no written derivation; only eleven expectations satisfy SC-02. |
| F-08 adverse ordering | **CLOSED** | Two copied repositories create `zeta.py`/`alpha.py` in opposite orders and assert byte-identical stdout and exit (`test-code-grade-cli.py:115-130`); runtime sorting is `(path,line)`. |
| F-09 named metric movement | **CLOSED** | Six direction pairs name `cognitive`, `cyclomatic`, or `abc`; the assertion reads that exact attribute and checks its named direction (`test-code-grade.py:47-112,311-315`). |
| F-10 NUL-safe paths | **CLOSED** | Both diff readers use `-z`; tab/newline rename fixtures reach grading and text output (`code_grade.py:302-317`; `test-code-grade.py:207-230`; `test-code-grade-cli.py:98-113`). |
| F-11 approximation labeling | **CLOSED** | Text prints `COGNITIVE: N (Sonar-style approximation)` and JSON carries `cognitive_method` on every record (`code-grade.py:50-56,115-121`). The pinned text run visibly labels all 98 records; the JSON probe found the same exact value on every grade-1/2 record. |
| F-12 per-record bar/outcome | **CLOSED** | Text emits `BAR` and explicit `RESULT: PASS|FAIL` inside every function block (`code-grade.py:110-128`). The pinned report makes all 98 decisions locally readable; JSON carries each `bar` with `grade`, making its machine outcome deterministic. The targeted JSON projection found zero records missing a bar. |

## Complete pinned grading outcome and grade-2 reasons

The real text run above produced **98 records**, **81 passing**, **17 below their surface bar**, **0 ungraded**, **one grade-1/high**, and **nine grade-2 `REASON REQUIRED` demands**. Therefore `code_grade: fail`. The JSON form independently returned the same 98/81/0 counts and the same grade-1/grade-2 identities.

Every emitted grade-2 demand is answered here:

| Demand | Written reason |
|---|---|
| `check-plan-routes.py:775 main` | Cohesive CLI orchestration owns root/manifest selection, plan processing, cross-feature checking, ordered findings, summary, and exit status; splitting it would scatter one command lifecycle and its fail-closed ordering. |
| `code-grade.py:137 main` | This is the single adapter boundary that validates mutually exclusive invocation modes, resolves the repository, selects text/JSON, sorts once, and returns the report status; keeping that lifecycle together makes both renderers consume the same records. |
| `code_grade.py:322 _body_hashes.collect` | The nested walker deliberately carries its lexical qualname prefix while handling nested functions/classes and docstring exclusion; the cognitive cost reflects the recursive AST shape rather than unrelated responsibilities. |
| `code_grade.py:350 gated_set` | This function is the authoritative changed-function attribution transaction: changed-file traversal, pre-image lookup, body-hash fallback, and gated/informational partition must remain in one ordered decision path to preserve D-01/D-03 semantics. |
| `test-code-grade-cli.py:96 test_diff_and_determinism` | One end-to-end fixture intentionally couples deletion, an odd-path rename, two absolute copies, and adverse enumeration order so it proves the subprocess output contract across those interacting Git states. |
| `test-code-grade.py:136 check_changed_function_resolution` | The seven-way fixture must set up and assess new, worsened, improved, renamed, reformatted, signature-only, moved, and already-bad functions together; separation would lose the shared two-commit attribution scenario. |
| `test-code-grade.py:296 main` | The script-level test runner coordinates the fixed fixture table, all-grade coverage, nested ordering, NUL safety, named metric directions, changed-function attribution, worked examples, and ten delivery assertions; its ABC size is assertion aggregation, not production branching. |
| `test-gate-policy.py:55 check_policy_loading` | One temporary configuration lifecycle exercises the valid four-key load and all invalid/missing/unreadable variants against the same fixture authority; keeping the variants together makes fallback drift visible. |
| `test-validate-digest.py:1760 run_code_grade_cases` | One temporary policy/digest scenario must vary `advisory_unless_high` versus `advisory`, `n_a` range basis, missing gates, and the pinned predecessor while holding the reviewer payload shape constant; the combined function proves policy-dependent discrimination. |

These reasons satisfy the output demands but cannot override the grade-1 blocker.

## Commands and adequacy

- `git rev-parse --verify 'df63193^{commit}'` and the equivalent pin lookup — both resolved to the full hashes above.
- `git diff --name-only df63193..45328d7a280d251a94b09672a7b6724d55a79f83` — 48 files, complete list above.
- Extension census pipeline — `34 md, 10 py, 1 html, 1 json, 1 sh, 1 yaml`.
- `git cat-file -e '45328d7...:.../DESIGN.md'` — exit 128, absent.
- Real pinned text CLI — exit 1; 98 records, 81 passing, 17 failing, no ungraded, one grade 1, nine grade 2.
- Real pinned JSON CLI projected with `jq` — 98 records, 81 passing, no ungraded; exact grade-1/2 identities above; all projected records carry `bar` and `cognitive_method`.

The already-recorded post-fix QA evidence says unit 29/29 and integration 28/28 passed under Homebrew Python; those broad suites were not duplicated. Its statement that all twelve fixtures are hand-derived is too broad: source reinspection shows the missing `bindings-and-calls` derivation. No formatter, linter, project-wide build/suite, goal-check, UAT, ship, merge, deployment, or implementation edit was performed.
