# Engineering build — T-01

**PASS — T-01's Expertise core receipts/replay implementation is committed at `ba3fab79`; the member reports literal verify exit 0, zero FAILs, 34 seconds.** No send-backs (`cycles_used: 0`), no amendments. This is the T-01 build assessment, not full-feature acceptance or ship approval.

## Evidence and assessment

- Member: `harness-backend-dev`, routed by backend business-logic/CLI consult-when and signed execution_agent. Receipt: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes/.harness/harness/features/FEAT-2225-member-expertise-writes/notes/receipt-harness-backend-dev-T-01-c1.md`.
- Literal verify: `python3 tests/unit/test-expertise-ops.py && python3 tests/integration/test-expertise-merge.py`. Member-reported executed checks: 194 unit + 355 integration; exit 0, 0 FAIL, 34 seconds. I read retained verify completion and red/mutant evidence under `/tmp/t01`; I did not rerun verification.
- Receipt maps destination validation (including legal-looking-tail symlinks), absent files, strict low-level ops, target-then-atomic-receipt persistence and fail-closed agreement to named tests. It maps read-only final-active-effect verification, current-PR selection, collision mapping, independent and changed-main replace/drop refusals, caps and repeated replay to named tests.
- Supersession evidence covers same-original-persona re-dispatch, whole-batch replacement, empty withdrawal, immutable history, replay idempotence, and unauthorized/ambiguous/cyclic/on-main reference refusal.
- Fail-first: pre-change unit/integration runs exited 1; receipt records 17 one-mechanism mutants. Retained M10/M16 results demonstrate repaired test blind spots (symlink destination and final receipt/file disagreement), rather than accepting the initially surviving mutants.
- Architecture assessment is receipt/interface-level: existing expertise-merge ops and harness_merge remain the seam and persistence mechanism; per-runtime receipts carry immutable facts, while replay reconstructs from an explicit base. No second writer, journal, queue or active-selection ledger is reported. Only the three T-01 source/test files changed; docs/enforcement remain explicitly assigned to T-02–T-04.

## Qualifications and downstream checks

Changed-Python `code-grade.py` and the independent source/diff review were not exercised here; the member explicitly records that limitation. The main session should run the configured changed-Python grade before source review, then downstream feature gates after the remaining tasks land. No SC-01–SC-05 end-to-end completion is claimed by this partial build segment.

## Principles applied

- Separate Before Serializing Shared State: receipt ownership is per runtime; the actual shared Expertise target retains harness_merge serialization.
- Make Operations Idempotent: replay restarts from the named base, and receipt persistence failures are fail-closed rather than a new recovery subsystem.

Open questions: none. `amendments: []`. `cycles_used: 0`.

```yaml
VERDICT: PASS
DIGEST:
  headline: T-01 core receipts/replay committed at ba3fab79; member reports literal
    verify exit 0, zero FAILs, 34 seconds.
  open_questions: []
  files_touched:
  - .claude/skills/harness/bin/expertise-merge.py
  - tests/unit/test-expertise-ops.py
  - tests/integration/test-expertise-merge.py
  expertise_update: []
  team: build
  steps_run: 1
  cycles_used: 0
  members:
  - step: T-01
    persona: harness-backend-dev
    verdict: PASS
    headline: Member-ops, read-only receipt verification and replay implemented; literal
      verify reported exit 0; commit ba3fab79.
    files_touched:
    - .claude/skills/harness/bin/expertise-merge.py
    - tests/unit/test-expertise-ops.py
    - tests/integration/test-expertise-merge.py
  must_fix: []
  branch: feat/FEAT-2225-member-expertise-writes
  escalations: []
  adequacy_notes:
  - 'Commit: ba3fab79. Member reports literal verify exit 0, zero FAILs, 194 unit
    checks plus 355 integration checks, 34 seconds; lead did not rerun verification.'
  - Receipt assessed against destination checks, atomic receipt/fail-closed agreement,
    read-only final active effects, replay collisions and conflicts, caps, supersession
    and fail-first evidence; retained red and mutant outputs inspected.
  - No amendments or send-backs; T-02/T-03/T-04 remain outside this segment.
  - Architecture assessment is receipt/interface-level. Changed-Python code-grade
    and independent source/diff review were not exercised; main should obtain grade
    evidence before source review.
  - PASS is limited to the T-01 build handoff, not full-feature SC completion or ship
    approval.
  sc_status: []
  needs_approval: none
  severity_max: none
  matrix_ok: none
  coverage_gaps:
  - Changed-Python code-grade and independent source/diff review remain downstream.
  - Full-feature host, receipt enforcement and merge behavior require T-04 and downstream
    gates.
  findings: []
  readers: []
  amendments: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes/.harness/harness/features/FEAT-2225-member-expertise-writes/runs/r-20261121-3-t01-eng/digest.md
```
