# FEAT-71 code review — fix-c1

**PASS with two unchanged med/substance advisories. CR-01 resolved: the exact-pin grader exits 0 and every original T-06 assertion survives. No regression found in the remediation delta.**

Reviewed `4a05030d401593003209f525fd06e00802eccd36..5a2edb72a220efd4a44cda6f512ec5697c0f37e0`; remediation delta `3e6add2af05f5b801afec1ef69440fe54e1529a4..5a2edb72a220efd4a44cda6f512ec5697c0f37e0`. Read actual git diff and full commit list; no `[harness:human]` commits. Current feature.json agrees with assigned pin. Dirty files are only orchestration-owned feature.json/plan.yaml; source was inspected in an isolated managed checkout at the immutable pin, subsequently removed.

## Stage 1 — specification

BRIEF, plan `decisions: []`, prior validator assessment and DEC-220 receipt rules read before quality assessment. This delta serves SC-02/03 assertion-preserving fixture simplification plus verification evidence; no scope creep, omission or mismatch identified. SC-01/04/05 inspection dispositions from c0 remain unchanged: delta contains no corpus deletion, probe implementation, config, authority-document or pruning changes. SC-04 inspection: `tests/manual/probe-omp-session-accessor.py:79` remains the retained reproduction path; new live receipt is evidence only, not a probe behavior change. No dev receipt/amendment is introduced; main is the DEC-174 author.

## CR-01 — resolved, assertions preserved

`tests/integration/test-check-state-records.py:795-874` preserves fixture JSON/YAML, default done station and unset task status. Direct old/new diff establishes:
- `:846-849`: BOTH FEAT-9001-fixture and BUG-9-x still require their feature id AND recover-terminal in the first INV-37 line when the receipt is absent.
- `:834-853`: all FOUR identical receipt rows survive: opened/no violation; recovered-terminal/no violation; unbound sync-off/no violation; factory issue without receipt/violation. `bool(first matching line)` is equivalent to original `"INV-37" in out`, including a missing match.
- `:868-874`: building/no started work still requires literal `open`; review/no task status and building/done each require literal `recover-terminal`. List equality preserves both trigger checks, with both calls evaluated.
- Discovery: `run-unit-tests.py:207-224,318-321` selects this integration script; its `main():1061-1062` appends BOTH replacement cases and `:1071` fails if either returns false. Removed case has no remaining test/skill callers. These are real checker/recovery calls, not fixture-only assertions.

Measured independently in the managed exact tree: `python3 .claude/skills/harness/bin/code-grade.py --base 4a05030d --head 5a2edb72`, **exit 0**, PASSING 32, no high records, two med/reason-required records. T-06 records: `_t06_inv37_line` CC3/cognitive0/ABC6.7 grade5; `case_t06_inv37_receipt` CC4/cognitive4/ABC13.5 grade4; `_t06_recovery` CC1/cognitive0/ABC4.2 grade5; `case_t06_recovery_command` CC2/cognitive1/ABC6.6 grade5. Original blocking grade-1 function is deleted. `code_grade: grade_2` reflects the remaining advisories, not a blocking failure.

## Current advisories — remeasured and inspected

- **CR-02 open, not regressed — med/substance:** `tests/integration/test-check-state-handoff.py:489`, `case_t14_exempt_shape`: CC13/cognitive8/ABC30.6, grade2, cyclomatic+ABC driver. An exemption edit requires tracking existing-note rejection, missing-note suppression and named notice together. Grade-2 reason: all three deliberately observe the SAME synthetic feature state; splitting risks losing that shared-state contrast. Not must-fix.
- **CR-03 open, not regressed — med/substance:** `tests/integration/test-post-merge-sweep.py:974`, `_t07_sweep`: CC4/cognitive3/ABC26.6, grade2, ABC driver. Extending receipt setup requires tracing repo creation, receipt mutation, commit, worktree and process lifecycle. Grade-2 reason: one disposable real-git fixture is reused by the retention matrix and uniform-id probes so their setup stays identical. Not must-fix.

## Evidence bounds

No suites/build/lint/formatter/live probes executed by this reviewer. Supplied `notes/merge-5a2edb72a220efd4a44cda6f512ec5697c0f37e0.log:3839-3872` separately records both cases' eight successful assertion messages and script exit 0 at the correct pin; final receipt reports 141 files. This is builder evidence read, not independent execution. Accessor receipt explicitly records a baseline-equivalent case3 FAIL, not a green live probe; QA/lead owns that policy disposition. Withdrawn/dismissed QA allegations are not revived.

## Principles applied

- **Migrate Callers, Then Delete Legacy APIs:** verified the old combined case was removed and both new cases replaced its main registration in the same change, without a shim.

Open questions: none. Must-fix: none. Source changes: none.
