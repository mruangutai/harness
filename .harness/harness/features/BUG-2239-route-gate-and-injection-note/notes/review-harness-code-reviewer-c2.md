# PASS — compliance preserved; blocking complexity and both advisory tests remediated

Reviewed `594af2a8123771da1a5290942400f4f8a064656f..a986d0896fb28f4722acd1e66b1eea14f1fbef2c`. Actual origin/main merge-base is 594af2a8; tracked status clean; no `[harness:human]` commits. Live feature.json and dispatch agree on a986d089 (the committed historical feature.json retains the prior pin). Fix-cycle range: `0646be23..a986d089`. No source changes or T-01 suite execution by this reviewer.

## Stage 1 — compliance

- SC-01/SC-03 **inspection**: `.claude/skills/harness/bin/plan_merge/check.py:196-233` calls the existing processor once on the target, using root and routes.manifest_root. The ordered comprehension preserves complete VIOLATION text and duplicates; `_report` counts the entire concatenated failure list, prints failures then overlaps then summary. Preface remains deviation then missing BRIEF; task faults precede shared findings. None exits 5 before `_check_all`; processor exceptions cannot reach successful reporting. No shared rules copied or changed.
- SC-02/SC-05: `.omp/extensions/harness-hooks.ts:373-374,1224-1232,1331-1336` returns the exact injection sentence with revised task input only, with refusal taking priority. Bash revisions leave schemasInjected false. Flat/batch positive assertions and scout negatives are in `tests/unit/omp-hooks.test.ts:1629-1684`; non-Harness targets are unchanged by withDigestSchemas. Refusal text unchanged in the actual diff.
- SC-04: `tests/integration/test-plan-merge.py:3007-3058,3110-3249` exercises real budget/status rules, valid acceptance beside an invalid sibling, None refusal, sentinel delegation and served-root/manifest arguments. Both legacy `_route_faults` NOBODY and shared VIOLATION are explicitly asserted, with exactly eight failure lines. `_gate_rejections` derives budget and validates the illegal status; `_GateSpy` delegates unrelated attributes; `_spied_check` restores the replaced loader in finally and returns None on unexpected fallthrough, which fails the positive exit assertion. No hidden success fallback found.
- SC-06: `tests/integration/test-check-skill-weight.py:127-148` runs actual JSON/plain subprocesses and checks literal report values; production change is solely import json. Preserve `notes/review-harness-qa-c1.md` as authentic independent immutable-base red/fix green evidence; do not replace it with author receipt `green-cycle1.txt`.
- Only six source/test paths changed; remaining paths are this feature's records. No build-lead amendments or developer principle receipt found. Product docs/spec.md, docs/decisions.md, docs/architecture.md absent at the pin; no main-checkout substitutes used.

## Stage 2 — independently measured grading

Command, from PRODUCT checkout: `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/code-grade.py --base 594af2a8123771da1a5290942400f4f8a064656f --head a986d0896fb28f4722acd1e66b1eea14f1fbef2c`; **exit 0; PASSING: 15; no SEVERITY or REASON REQUIRED records; code_grade pass**.

Independent AST comparison of both immutable versions found **17 changed/new functions**, all extracted by grade_source. CLI intentionally excludes two same-grade existing functions, not extraction misses: cmd_check remains grade 4 (ABC 19.5 → 13.6); existing F59 remains grade 2 (ABC 34.9 → 36.8). The latter is inherited same-band debt, not a gated grade-2 finding. check-skill-weight.py has an import-only change and no changed function.

| Path / line / function | Cyclomatic | Cognitive | ABC | Grade |
|---|---:|---:|---:|---:|
| check.py:196 _route_gate_failures | 4 | 1 | 4.7 | 5 |
| check.py:210 _preface | 4 | 1 | 2.2 | 5 |
| check.py:215 _report | 2 | 2 | 5.5 | 5 |
| check.py:223 cmd_check (informational) | 2 | 1 | 13.6 | 4 |
| test-check-skill-weight.py:127 WeightTests.test_cli_json_and_plain_modes | 1 | 0 | 17.7 | 4 |
| test-plan-merge.py:3007 case_f59_check_lists_each_failure_on_its_own_line (informational) | 5 | 2 | 36.8 | 2 |
| test-plan-merge.py:3110 _gate_plan | 3 | 2 | 4.7 | 5 |
| test-plan-merge.py:3123 _gate_rejections | 3 | 0 | 9.2 | 4 |
| test-plan-merge.py:3137 case_2239_check_runs_ci_per_plan_route_gate | 3 | 4 | 9.4 | 4 |
| test-plan-merge.py:3153 case_2239_check_accepts_a_gate_clean_plan_beside_a_violating_one | 3 | 2 | 12.7 | 4 |
| test-plan-merge.py:3170 case_2239_check_refuses_a_plan_the_route_gate_cannot_load | 3 | 2 | 9.5 | 4 |
| test-plan-merge.py:3190 _GateSpy.__init__ | 1 | 0 | 0.0 | 5 |
| test-plan-merge.py:3193 _GateSpy.__getattr__ | 1 | 0 | 1.0 | 5 |
| test-plan-merge.py:3196 _GateSpy.process_plan_yaml | 1 | 0 | 2.0 | 5 |
| test-plan-merge.py:3202 _spied_check | 2 | 2 | 12.1 | 4 |
| test-plan-merge.py:3219 case_2239_check_delegates_to_the_shared_processor | 3 | 2 | 11.5 | 4 |
| test-plan-merge.py:3234 case_2239_check_asks_a_served_plan_with_root_and_manifest | 3 | 2 | 18.6 | 4 |

Production rows use `.claude/skills/harness/bin/plan_merge/`; test rows use `tests/integration/`. New helpers localize reporting and spy restoration without introducing another rule source. Static inspection, not executed mutant testing, establishes ordering/duplicate preservation.

## Historical dispositions and remaining assurance limits

- **High substance T-01 cmd_check complexity: CLOSED**, now grade 4; prior shared-rule and root-delegation **med substance advisory grade-2 tests: CLOSED**, split cases now grades 4/5 with coherent fixture/finally ownership.
- **SCOPE-01: VOID**, wrong prior base. Executed `git diff 594af2a8 a986d089 -- .harness/harness/features/BUG-2171-task-structured`: empty. Executed `git diff --stat 594af2a8 926383ae`: exactly the three BUG-2171 records, 22 insertions/1 deletion. `git diff --quiet 594af2a8 926383ae -- .claude .omp tests`: exit 0. Historical route/hook reds therefore still bind identical baseline code; no foreign-record restoration/authorization needed.
- Prior **low form T-01 SC-06 provenance gap: CLOSED** by retained QA c1 reproduction, preserving original raw receipts and failure history. Test identity and JSON/plain test bytes are unchanged by the fix cycle.
- Still disclosed: bash-revision no-note branch lacks dedicated regression; typecheck runner unresolved; original route/hook receipts remain output-only (semantic red evidence, not recovered execution provenance). These are not newly manufactured findings.
- Prior unattributed digest-gate suite failure remains unexplained. Its off-pin retry at 964d63bd is excluded; no whole-suite clearance or flake diagnosis claimed. QA owns final exact T-01 verification at this pin; this review does not substitute for it.

## Principles applied

- Delete First: assessed local orchestration simplification, not speculative interfaces or rule duplication.
- Type System Discipline / Model the Domain: traced schema-revision state to its sole assignment and refusal-first return; no new unsafe cast or contradictory state introduced.

Open question GATE-01 (nonblocking): can the owning lead attribute the historical digest-gate failure from existing logs? No rerun or diagnosis was attempted here.
