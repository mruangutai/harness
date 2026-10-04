# BUG-2003 c0 — pinned code review

FAIL: the URI boundary is correct by inspection, but SC-03's automated preservation coverage omits main-session edits and write refusal before execution. Stage 2 was not entered because Stage 1 has an acceptance-evidence omission.

Reviewed `b8e9f9c8f451cfe4b4e211eb97093525b7872c1b..85038f8c1acbb38e2b6f758540941bc5cfdaf1ba`, using committed source/tests (`git show`), not working-copy source. No human-tagged commits; only tracked dirt was feature.json. The `.omp`/`tests` diff from code parent `f9e23bcb` to pin is empty. No Python changes: code_grade n_a. Ancestor e0bb9814 carries FEAT-495 station bookkeeping (PR/status), not a new implementation surface.

## Stage 1 — SC-01..05

- SC-01: allowed routes/stages asserted at `tests/unit/omp-hooks.test.ts:1055`; fail-first receipt names the failing case.
- SC-02: refused destinations, exact xd suffix, write/edit and post errors asserted at `tests/unit/omp-hooks.test.ts:1067`; MV refusal at :1083. Named receipt cases were red before the fix.
- SC-03: mixed forbidden-file edit refusal is preserved at `tests/unit/omp-hooks.test.ts:1093`; ordinary write payload control at :1113. **Incomplete controls**, detailed below.
- SC-04 inspection PASS: committed `.omp/extensions/harness-hooks.ts:272` makes the sole scheme decision; :289-313 classifies write.path and every extractEditPaths section/MV result separately; preDomain :325-328 and postDomain :339-340 both delegate to it. URI branches precede the runner, do not resolve paths, and cannot exempt sibling files. Main-session early returns and lineage/claim checks are unchanged.
- SC-05: tests execute registered production callbacks; committed `notes/receipt-t01-fail-first.txt` names four discriminating failures (102 pass / 4 fail), and `notes/receipt-t01-pass.txt` records 106 pass / 0 fail and literal verify exit 0. These are supplied receipts, not checks executed by this reviewer.

## Finding — T-01

**R1 · substance · med · reader: code-reviewer · SC-03 omission** — `tests/unit/omp-hooks.test.ts:1125-1134` exercises only main-session write/pre; no main-session edit or write/edit post control exists. The forbidden-file fixture at :1031 is exercised only through mixed edit (:1096), never a governed forbidden write/pre. Consequently [INFERENCE, not executed] a regression that blocks main-session edits, adds main-session post-write URI errors, or skips the governed ordinary-write pre gate is not distinguished by the required preservation controls. The allowed ordinary write test checks payloads, not the refusal path; the older advisory refusal test (:1462) covers write/post only.

Must fix: extend the existing callback tests with main-session write/edit pre/post controls (including non-allowlisted URIs), and a governed forbidden-file write/pre refusal/payload assertion. Preserve the mixed-edit refusal tests and record the full literal verify receipt. This closes SC-03's required automated evidence, without changing the inspected production behavior. No additional runtime defect is alleged.

Stage 2: not performed. Builds, tests, grading tools, linters, formatters and mutants: not run, per assignment. Open questions: none. Source/test/config changes: none.
