# Code review — FEAT-2257 — c0

PASS: no substantive or spec-compliance defects in implementation `bda50269..45626d7964e732e8e21b594a78dcbed8fa0494a7`. Spec compliance preceded quality review. Mechanical grade range: `0d7326e40137dfce63f5b7b33af95ee126f90971..45626d7964e732e8e21b594a78dcbed8fa0494a7`; earlier commits add this feature's planning records only. No human-attributed commits; only feature.json was dirty. This is code clearance, not remote-CI/ship clearance.

## Stage 1 — pinned inspection

- SC-02: package.json:5 supplies the command; package.json:8 and bun.lock:8 supply matching exact dev-only pins; tsconfig.json:6 supplies strict/noEmit. Owner T-01.
- SC-03: .github/workflows/tests.yml:74 supplies frozen install before compilation; .github/workflows/tests.yml:389 installs before integration tests. Current pinned remote logs remain QA/PM-owned. Owner T-03.
- SC-04: .gitignore:3 ignores dependencies. Manifest/lock/config remain tracked; the sole tracked node_modules cache is deleted. notes/receipts/T-01-verify.txt:1 records the ignore/untrack verification. Ledgered amendment serves this criterion. Owner T-01.
- SC-05: .github/dependabot.yml:5 selects root Bun updates on a weekly schedule. Owner T-03.
- SC-06: .github/workflows/tests.yml:77 supplies unconditional typecheck; the unchanged aggregator retains needs and explicit result validation. No added condition, fallback or PR path filter. Current pinned remote results remain QA/PM-owned; earlier different-SHA evidence is insufficient. Owner T-03.
- SC-07: .harness/harness.json:201 activates the observed command, deletes _reason, preserves detect/exclude and sets false classification. .claude/skills/harness/templates/harness.json:138 retains null command and false classification. .harness/harness/docs/DECISIONS.md:6960 permits manual-source static reading without execution; .harness/harness/docs/DECISIONS.md:6977 documents default-true classification and both consumers. Capability-green and real-compiler-pre-activation receipts record ordering/source identity. Owner T-04.
- SC-08: .harness/harness.json:201 is the only changed kind in the diff against immutable 0bdcabbf; test_matrix and _matrix_provenance remain unchanged. Owner T-04.
- SC-10: tests/unit/omp-hooks.test.ts:1657 preserves generic payload types; tests/unit/omp-hooks.test.ts:2152 annotates comparison output unknown; tests/unit/omp-hooks.test.ts:2912 narrows the literal. Production pi/ctx typing is untouched, existing assertion values remain, and package.json:7 introduces only the two approved dev dependencies. No linter/formatter. Owner T-02, with dependency scope T-01.
- SC-11: README.md:214 documents installation, command, coverage, API limitation and reviewed updates. .harness/harness/docs/SPEC.md:1021 narrows the gap without claiming real-host API typing. `bun update --latest` correctly clarifies exact-pin upgrades; the build narrative records its measured rationale. Owners T-01/T-04.
- SC-12: .harness/harness/features/FEAT-2257-typescript-typecheck/plan.yaml:207 declares main-session-direct execution; notes/build-T-01-T-02.md:1 and notes/build-T-03-T-04.md:1 record direct execution. Both code_grade spellings share the pinned .agents/skills symlink. Owners T-01..04.

## Stage 2 — quality

- T-02 deviation accepted: unknown mapper retains exact runtime equality and expected member-ops arrays without array-to-record casting. The recorder mirrors the pre-existing production Dict contract; widening it is unnecessary for assertion behavior. Generic filtering retains payload information elsewhere. Existing assertions/expected values remain intact.
- T-04 classifier (code_grade.py:458-487) preserves active/locally_run, default-true and excludes. Synthetic fixtures independently cover false/absent/true, status and exclusion. Offenders/control candidate inherit the matcher; hygiene shares its predicate instead of duplicating policy.
- T-04 integration regression (tests/integration/test-typescript-typecheck.py:51-135) independently enumerates every tracked source and compares with compiler enumeration. Pinned Git enumeration contains the four settled TS sources; tsconfig includes hidden .omp sources. Suppression is rejected; clean copy must pass before its poisoned version must fail with a real diagnostic naming the source. Missing tools/config, Git failure and timeout cannot return success; failed assertions accumulate independently of diagnostic text. Earlier receipts distinguish compiler red-first, runtime non-regression and classifier behavioral reds.
- Required read-only Python risk grading ran once against the canonical pinned range: exit 0, 13 passing records, no severity/reason-required records. _classifies_tests grade 5; poison helper grade 3 meets the test bar; remaining reported functions grade 4/5. No builds, tests, lint, formatters or mutants executed by this reviewer.

## Principles applied

- Type System Discipline: generic/literal narrowing and unknown retain concrete equality rather than introducing an unsafe cast.
- Delete First: shared classification removes duplicate policy without another registration system or adapter layer.

Open questions: none for code review. Final pinned compiler/CI evidence remains QA/PM-owned. Findings and must-fix: none.
