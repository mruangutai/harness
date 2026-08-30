# FEAT-43 pinned UI/CLI surface review

**FAIL.** The pinned range adds one rendered HTML report with sub-AA small-text contrast in both theme paths, and the new CLI text report hides the per-function bar/result and omits the mandated Sonar-style qualification. All three are actionable presentation defects.

## Pin and complete-set scope

Both objects resolve: base `df63193f7ec9798d9660904e0e4e7c78d52358f5`; review pin `1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c`. The required `git diff --name-only df63193..1ac1bd03fc73c004fdde4b684ac8a18d3bd43f2c` returns exactly these 48 files:

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

The extension census is 34 Markdown, 10 Python, one HTML, one JSON, one shell, and one YAML file. No `DESIGN.md` exists for FEAT-43 at the review pin (direct object check). The approved BRIEF says component/UI runners cover no feature surface, but the dispatch expressly includes adjacent CLI presentation and the complete set contains an added rendered HTML reading view. Those two surfaces therefore remain in scope; agent/skill prose, implementation internals, tests, config, receipts, and plan metadata do not add another rendered interaction surface.

## Findings

### UI-01 — High · must fix · small report text fails contrast in both theme paths

- **Pinned evidence:** `.harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-t06-eng.html:3-4,20-21,30-31,55-56`.
- **Actual:** light theme uses `#7d8b99` for 10–11px text: contrast is 3.39:1 on `#fbfcfd` and 3.15:1 on table-header `#f1f4f7`. Dark table headers use `#77869a` on `#182029`, only 4.43:1. These sizes are not large text, so all cited combinations miss WCAG AA's 4.5:1 minimum. (Ratios independently checked with WebAIM's contrast API.)
- **Specified:** accessible presentation in both themes; the source itself provides distinct light/dark tokens and applies `--quiet` to the eyebrow and table headings.
- **Concrete scenario → wrong outcome:** a low-vision reader opens the committed ship-review reading view in either light mode or dark mode; the section label/table headings are materially harder to read, and in light mode every `--quiet` label is below AA.
- **Owner route:** `harness-visual-designer` to correct the shared report palette, then the report-producing/documentation route to regenerate this changed artifact. This palette recurs in existing ship-review HTML, so changing only the prose will not fix the source of drift.

### UI-02 — Med · must fix · the text report does not identify which functions failed their bar

- **Pinned evidence:** `.claude/skills/harness/bin/code-grade.py:50-55` computes and stores each record's `bar`, but `:92-104` prints grade/driver and only an aggregate `PASSING` count; it emits neither `BAR` nor a per-record `PASS`/`FAIL` state. `.harness/harness/features/FEAT-43-code-risk-grading/plan.yaml` T-03 specifies production bar 4 versus test bar 3; the BRIEF Definition of Done requires rejection output an author can act on without opening tool source or guessing.
- **Actual probe:** at the pinned HEAD, running the real CLI over `gate_policy.py` exits 1 and prints five function blocks plus `PASSING: 3`; `load_policy` and `evaluate_qa` each show grade 3 with no severity, bar, or failure label. The hidden records classify both as production with bar 4.
- **Concrete scenario → wrong outcome:** a report contains grade-3 production and grade-3 test functions. The same displayed grade is a failure for one and a pass for the other, while the aggregate only says how many passed. A human cannot map the failed status back to a function from the text output alone.
- **Owner route:** `harness-dev-ops` (signed T-03 owner) to expose the already-computed bar and per-function outcome in the text surface and cover the mixed production/test case.

### UI-03 — Med · must fix · reported cognitive values omit the mandated approximation label

- **Pinned evidence:** `.claude/skills/harness/bin/code-grade.py:53-55,95-98,133-136` emits the unqualified labels/key `cognitive` / `COGNITIVE`; `plan.yaml` D-05 requires the cognitive metric to be named a Sonar-style approximation wherever it is reported, explicitly including tool output.
- **Actual:** both human text and JSON present the number without qualification. The pinned CLI smoke output, for example, prints `COGNITIVE: 11` with no indication that this is not SonarSource's algorithm.
- **Concrete scenario → wrong outcome:** an engineer compares the value with a Sonar report and treats the mismatch as a grader defect or as an equivalent Sonar score; the exact confusion D-05 was adopted to prevent remains possible at the point of use.
- **Owner route:** `harness-dev-ops` (T-03 CLI owner) to qualify the human-readable field and make the JSON contract unambiguous without changing the metric itself.

## Other audited dimensions

- **CLI states:** deterministic labelled blocks, repository-relative paths, parse-error naming, ungraded listing, grade-2 reason prompt, and non-colour status signaling are present. There is no interactive focus or theme behavior in this plain-text CLI. Long paths/qualnames are not truncated by the program.
- **HTML structure/theme:** document language, title, heading order, semantic table elements, focus-visible styling, reduced-motion handling, responsive width, horizontal overflow containment, and both light/dark token sets are present. The contrast failure above breaks theme parity despite those tokens.
- **Known source-audit limit:** rendered size, wrapping, and narrow-terminal/browser layout were not visually verifiable from source; human eyes would still be required for those dimensions. No UAT was run, per dispatch.
