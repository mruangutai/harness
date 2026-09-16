# Code review c2 — BUG-1716-build-amendments

**BLUF: PASS.** Stage 1 and Stage 2 pass for exactly `33f45262a9346b62a0e81d3a21786ab2b761cf4e..e348b40d5bba915a6131be37de728947da990deb`. V-01 is closed: every exception from the post-splice ledger write now enters rollback while the plan lock remains held, and the retained PermissionError case binds both files' byte identity. No blocking finding remains.

## Stage 1 — spec compliance: PASS

The complete pinned range contains 45 changed paths. Every product path traces through T-01..T-09 to SC-01..SC-07 and D-01..D-08; the remaining paths are this feature's signed plan, receipts, review records, and run records. The c2 product fix is limited to T-04's atomic `record-amendments` route and its focused integration case (`.claude/skills/harness/bin/plan-merge.py:2239-2271`; `tests/integration/test-plan-merge.py:3933-3960`). No scope creep, omission, mismatch, or `[harness:human]` commit appears.

Inspection criteria remain satisfied at the pin:

- **SC-05:** Stage 1 is anchored on BRIEF success criteria and decisions, while Stage 2 and code-grade use the pinned diff (`.claude/skills/harness-code-review/SKILL.md:34-50`).
- **SC-06:** all three BUG-285 recommendations remain represented and applied as eligible amendments (`tests/integration/test-plan-merge.py:3699-3730`).
- **SC-07:** DEC-23, DEC-32, DEC-157, DEC-229, and DEC-230 consistently state authority, approval survival, run-not-cycle accounting, six-kind ledger semantics, DEC-226 precedent, and the three task-text-independent checks (`.harness/harness/docs/DECISIONS.md:255-270,360-371,3613-3635,7415-7499`).

`spec_violations: []`.

## Stage 2 — code quality: PASS

### V-01 closure

`_record_amendments_locked` replaces the plan, then handles both `MergeRefusal` and every other exception from `_record_amendment_judgements`; both handlers call `_restore_plan` before leaving the plan-lock scope (`plan-merge.py:2250-2271`). `_restore_plan` either restores the exact captured bytes or adds an explicit, actionable failed-restore line (`plan-merge.py:2239-2247`). Thus an ordinary lock-open, tempfile-write, fsync, or replace error no longer sails through the old exception-class gap.

The new case makes `feature.json.lock` unopenable so `PermissionError` occurs only after the plan splice, then asserts a nonzero diagnostic without traceback, the explicit restore message, and byte equality for both `plan.yaml` and `feature.json` (`tests/integration/test-plan-merge.py:3933-3960`). This directly answers c1 V-01's requested ordinary post-plan-write I/O arm. The test has both presence assertions and the paired absence assertion; changing the production catch back to `MergeRefusal` makes its subprocess return with a traceback and leaves the plan changed.

### Prior-finding dispositions

- **V-01: CLOSED** — broad rollback boundary plus ordinary-I/O byte-identity evidence above.
- **V-02: CLOSED** — feature-record selection remains decomposed and above the production grade bar.
- **V-03: CLOSED** — record-amendments preflight/locked/command stages remain decomposed and above the bar.
- **V-04: CLOSED** — INV-40 helpers and focused scenarios remain above their respective bars.
- **V-05: CLOSED** — deterministic-hash scenarios remain focused and above the test bar.
- **V-06: CLOSED** — BUG-285 splice, isolation, ledger, validity, and replay scenarios remain split and passing-grade.
- **V-07: CLOSED** — the feature-schema runner remains data-driven, with no grade-1 accumulator.
- **V-08: CLOSED** — `amendment_contract.py` remains the single closed-shape authority shared by both consumers.

The earlier security advisories do not become code-review gates: task-level amendment coverage is the explicit SC-03/D-04 contract, and hashless legacy behavior is outside the signed-hash contract rather than a regression introduced by c2. No new fail-open or silent-failure path was found in the c2 change.

### Pinned code grade

Ran exactly `python3 .claude/skills/harness/bin/code-grade.py --base origin/main --head e348b40d5bba915a6131be37de728947da990deb`: exit 0, `PASSING: 89`, with no `SEVERITY:` or `REASON REQUIRED` records. Therefore `code_grade: pass`. No suite, formatter, linter, or build was run.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Stage 1 and Stage 2 pass at e348b40d; V-01 is closed by all-exception rollback and ordinary-I/O byte-identity evidence."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: pass
  reviewed: "33f45262a9346b62a0e81d3a21786ab2b761cf4e..e348b40d5bba915a6131be37de728947da990deb"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - .harness/harness/features/BUG-1716-build-amendments/notes/review-harness-code-reviewer-c2.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1716-build-amendments/.harness/harness/features/BUG-1716-build-amendments/notes/review-harness-code-reviewer-c2.md
```
