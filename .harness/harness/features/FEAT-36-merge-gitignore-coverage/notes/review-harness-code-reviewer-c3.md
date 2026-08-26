# FEAT-36 code review — c3

**BLUF: PASS.** At `be27d99454352e581fdf7cbace20fb52d0f45133`, the committed implementation satisfies REQ-01..REQ-05 and SC-01..SC-06. Spec compliance passes, so Stage 2 was performed; it found no substantive defect, fail-open path, silent failure, or must-fix item.

## Review basis

- Reviewed `0fa8f336e55dc57bca09a9f7df0524a35195ee7e..be27d99454352e581fdf7cbace20fb52d0f45133` across the assigned test, both registries, unchanged production utility, and operator ruling.
- The assigned substantive paths have no working-tree delta from the pin. The only observed working-tree trace edit was `feature.json`, outside this review surface.
- No `[harness:human]` commit occurs in the reviewed range.
- The renderer contrast concern is excluded by `notes/operator-ruling-rendered-review-scope.md`; it is not counted as a FEAT-36 finding.

## Stage 1 — spec compliance: PASS

| Ref | Disposition and evidence |
|---|---|
| REQ-01 / SC-01 | PASS — the real subprocess starts with distinctive ordered bytes, then requires the merged file to retain those bytes as its exact prefix and every canonical rule once (`.agents/skills/harness/bin/test-merge-gitignore.py:35-47`). |
| REQ-02 / SC-02 | PASS — separate complete and incomplete `--check` cases require exit 0 and 1 respectively, compare each target byte-for-byte before/after, and compare the emitted bullet set exactly with the canonical missing-rule set (`test-merge-gitignore.py:50-83`). The exact-set comparison blocks both omitted and fabricated missing diagnostics. |
| REQ-03 / SC-03 | PASS — absent and partial targets are separate cases; both assert every canonical rule independently has count one, while the partial case also retains its unrelated line and pre-existing canonical rule (`test-merge-gitignore.py:86-111`). |
| REQ-04 / SC-04 | PASS — the case captures bytes after merge one and requires merge two to leave them byte-identical (`test-merge-gitignore.py:114-125`). |
| REQ-05 / SC-05 | PASS — the test invokes the absolute utility with an absolute project root from a temporary caller directory outside both utility and project, proves the project target is created, and proves the caller's pre-existing `.gitignore` is byte-identical (`test-merge-gitignore.py:128-143`; subprocess construction at `test-merge-gitignore.py:20-24`). |
| SC-06 / D-01 | PASS by inspection — the filename appears only in `INTEGRATION_SCRIPTS`, not `UNIT_SCRIPTS` (`.agents/skills/harness/bin/run-unit-tests.sh:17-18`), and its exact path appears in `test_kinds.integration.detect` while the unit catch-all remains (`.harness/harness.json:104-109,118-122`). This implements the explicit-integration-over-catch-all precedence required by DEC-197 and preserves the runner drift checks. |
| SC-06 / D-02 | PASS by inspection/history — `git diff 0fa8f336..be27d994 -- .agents/skills/harness/bin/merge-gitignore.sh` is empty. The initial implementation commit `ac853387` added the test and registrations without editing production; later strengthening commits `f494553` and `b3ea5e4` also changed only the test on the substantive surface. No production correction therefore needed a preceding real-utility failure. |

Every substantive code/config change traces to T-01, D-01, or its later authorized test-strengthening. The ruling note records operator scope rather than expanding product behavior. There is no omission, mismatch, or scope creep.

## Stage 2 — code quality: PASS

- **Realism/locality:** each case crosses the same process/filesystem interface users exercise; no filesystem or subprocess behavior is mocked (`test-merge-gitignore.py:20-24`). Canonical rules come from the shipped snippet and use the utility's blank/comment exclusion semantics (`test-merge-gitignore.py:9-15`).
- **Fail-open review:** return codes are asserted on every behavior where status is contractual; preservation, read-only behavior, exact diagnostics, rule multiplicity, root selection, and byte idempotence each have an observable state assertion. A missing target, missing diagnostic, fabricated diagnostic, duplicate rule, wrong root, or no-op merge becomes a failure rather than sailing through.
- **Silent failures:** case-level assertion, OS, and subprocess failures increment the failure count, remain visible by case name, and produce process exit 1 (`test-merge-gitignore.py:156-165`). Unexpected exceptions abort nonzero rather than being converted to a pass.
- **Red capability:** the pinned real suite ran directly and reported `7 passed; 0 failed`. Running the same pinned suite with `MERGE_GITIGNORE_BIN=/usr/bin/true` reported six named failures and exit 1. The committed B-1 receipt additionally records a discriminating fabricated-superset diagnostic mutant killed specifically by the exact-set assertion. The complete-read-only case remaining green against `/usr/bin/true` is correct: that isolated state already satisfies its contract; the mutant is rejected by the other six behaviors.

## Findings and disposition

- **severity_max:** info
- **findings:** 0
- **ranked must_fix:** none
- **advisory notes:** The full T-01 all-kinds command was intentionally not rerun; QA owns that matrix. This review ran only the focused behavioral program and inspected the registration/drift machinery.
- **open_questions:** none
- **files_touched:** `.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-c3.md`
