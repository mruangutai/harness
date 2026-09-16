# Code review c0 — BUG-1716-build-amendments

**BLUF: FAIL.** Stage 1 passes at the pinned range: every changed path traces to SC-01..SC-07 and D-01..D-08, the feature contains no build-lead amendment to assess, and the three inspection criteria are satisfied. Stage 2 then fails on one cross-file atomicity defect and the pinned code-grade result (`fail`: six high records and seven grade-2 records).

## Stage 1 — spec compliance: PASS

Reviewed exactly `33f45262..c2bf2f3a2ffba5faf243867a915f082da17f387d` (32 changed paths; no `[harness:human]` commit). The implementation, tests, operating prose, signed feature records, and decision/index updates trace to T-01..T-09 and hence SC-01..SC-07 / D-01..D-08. No unowned change or task-text amendment was found; therefore compliance was anchored only on the BRIEF and decisions, not task text.

Inspection evidence:
- SC-05: the amended review rule explicitly makes amendments the departure map and BRIEF plus decisions the only Stage-1 anchor, while keeping Stage 2 pinned-diff based (`.claude/skills/harness-code-review/SKILL.md:34-46`).
- SC-06: all three BUG-285 specimens are present as accepted amendment fixtures (`tests/integration/test-validate-digest.py:597-604`; the command-level replay is `tests/integration/test-plan-merge.py:3671-3725`).
- SC-07: DEC-23 preserves approval-gated SC/task-set/decision authority (`.harness/harness/docs/DECISIONS.md:255-263`); DEC-157 records same-run/no-cycle semantics (`:3629-3634`); DEC-229 records byte-preserving transcription, hashes, and approval survival (`:7415-7430`); DEC-230 records the exhaustive six-kind ledger and independent review checks (`:7460-7471`). The ledger reference agrees (`.claude/skills/harness/references/ledger.md:35-58,84-86`).

`spec_violations: []`.

## Stage 2 — code quality: FAIL

### Ranked substantive finding

1. **High · substance · T-04 · cross-file atomicity can leave a fabricated amendment record.** `cmd_record_amendments.transform` writes amendment judgements to `feature.json` before `locked_update` commits the plan (`.claude/skills/harness/bin/plan-merge.py:2251-2278`). If the final plan replacement fails after the ledger write (for example an I/O or atomic-rename failure), `feature.json` says the signed task was amended while `plan.yaml` retains the old text. INV-40 then treats the ledger entry as coverage for any later text mismatch, and the operator audits a departure that never landed. This violates SC-02/D-04/DEC-229's all-or-nothing requirement. The shipped test only simulates failure acquiring the ledger lock before the ledger write (`tests/integration/test-plan-merge.py:3804-3830`), not failure after it.

### Pinned code-grade evidence

Command run against the required pinned range:

`python3 .claude/skills/harness/bin/code-grade.py --base "$(git merge-base origin/main c2bf2f3a2ffba5faf243867a915f082da17f387d)" --head c2bf2f3a2ffba5faf243867a915f082da17f387d`

It exited 1. The required high findings (unchanged severity) are:

2. **High · substance · T-03** — `.claude/skills/harness/bin/feature-record.py:208`, `_select_amendment`: cyclomatic 9, cognitive 5, ABC 19.9; grade 3, cyclomatic driver, production bar 4. A future selection-rule edit can omit the ambiguous-timestamp or non-amendment refusal in this dense selector and overrule the wrong ledger entry.
3. **High · substance · T-04** — `.claude/skills/harness/bin/plan-merge.py:2228`, `cmd_record_amendments`: cyclomatic 7, cognitive 7, ABC 25.9; grade 3, ABC driver, production bar 4. A change to one preflight/write step can skip a destination check and partially mutate one of the two records.
4. **High · substance · T-05** — `tests/integration/test-check-state-feat59.py:415`, `case_inv40_signed_text`: cyclomatic 12, cognitive 6, ABC 77.7; grade 1, ABC driver, test bar 3. Adding or changing an INV-40 case in this monolithic accumulator can bind the assertion to the wrong fixture/output and let an unledgered edit pass.
5. **High · substance · T-04** — `tests/integration/test-plan-merge.py:3633`, `case_b1716_sign_writes_deterministic_task_hashes`: cyclomatic 14, cognitive 10, ABC 54.2; grade 1, ABC driver, test bar 3. A hashing regression can be masked by stale shared fixture state or an assertion accidentally reading the result of a different signing step.
6. **High · substance · T-04** — `tests/integration/test-plan-merge.py:3671`, `case_b1716_record_amendments_applies_the_bug285_three`: cyclomatic 20, cognitive 11, ABC 63.7; grade 1, ABC driver, test bar 3. A splice, approval, or ledger regression can be obscured when one long scenario reuses and mutates the same plan/ledger across all assertions.
7. **High · substance · T-03** — `tests/integration/test-validate-feature-json.py:810`, `main`: cyclomatic 2, cognitive 1, ABC 48.0; grade 1, ABC driver, test bar 3. Adding a schema case to the large manual runner can omit or mis-register it, leaving an invalid `overruled`/hash shape unexecuted while the runner stays green.

The seven grade-2 records (unchanged **med** severity; each requires redesign justification) are:

8. **Med · substance · T-05** — `check-state.py:2904`, `_unledgered_task_edits`: 14/19/33.1, all metrics drive grade 2. It coherently computes one invariant, but combines eligibility, coverage extraction, iteration, hashing, and diagnostic construction; changing coverage semantics can silently suppress a real mismatch.
9. **Med · substance · T-04** — `plan-merge.py:2088`, `_amendment_entry`: 18/21/36.4, all metrics drive grade 2. It is one closed-entry validator, but field-specific validation and diagnostics are intertwined; adding a legal field/value shape can accept the wrong type on one branch.
10. **Med · substance · T-04** — `plan-merge.py:2251`, `cmd_record_amendments.transform`: 8/8/26.6, ABC driver, grade 2. It is the locked transaction body, but validation, splice verification, schema checks, approval preservation, and ledger mutation in one closure make ordering failures easy—the atomicity defect above is the concrete instance.
11. **Med · substance · T-02** — `validate-digest.py:402`, `_amendment_entry_errors`: 20/27/42.8, all metrics drive grade 2. It is one closed-contract validator, but a new validation branch can report yet fail to reject the corresponding malformed member.
12. **Med · substance · T-05** — `test-check-state-feat59.py:385`, `_signed`: 4/7/27.6, ABC driver, grade 2. It is a fixture constructor, but sign/mutate/ledger phases share one helper; a future case can mutate before signing and falsely prove post-signature detection.
13. **Med · substance · T-04** — `test-plan-merge.py:3769`, `case_b1716_approval_survives_amendment_and_resets_only_on_task_set_change`: 9/6/42.4, ABC driver, grade 2. Three verbs share mutable state; an earlier reset can change the precondition of the later assertion.
14. **Med · substance · T-04** — `test-plan-merge.py:3804`, `case_b1716_record_amendments_is_all_or_nothing`: 6/5/27.8, ABC driver, grade 2. The scenario proves lock refusal but not commit-after-ledger failure, so it can remain green while the cross-file transaction is not atomic.

No formatter, linter, project-wide test, or unrelated command was run.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Stage 1 passes, but Stage 2 finds a cross-file atomicity defect and pinned code-grade fails."
  severity_max: high
  findings:
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "T-04 record-amendments can append ledger entries before a failed plan commit, violating all-or-nothing semantics.", why: ".claude/skills/harness/bin/plan-merge.py:2251-2278; final plan-write failure leaves a fabricated amendment record." }
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "T-03 _select_amendment is production grade 3 below bar 4.", why: "feature-record.py:208; 9/5/19.9, cyclomatic driver." }
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "T-04 cmd_record_amendments is production grade 3 below bar 4.", why: "plan-merge.py:2228; 7/7/25.9, ABC driver." }
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "T-05 case_inv40_signed_text is test grade 1 below bar 3.", why: "test-check-state-feat59.py:415; 12/6/77.7, ABC driver." }
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "T-04 deterministic-hash scenario is test grade 1 below bar 3.", why: "test-plan-merge.py:3633; 14/10/54.2, ABC driver." }
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "T-04 BUG-285 amendment scenario is test grade 1 below bar 3.", why: "test-plan-merge.py:3671; 20/11/63.7, ABC driver." }
    - { kind: substance, scope: task, severity: high, reader: code-reviewer, summary: "T-03 feature-schema runner main is test grade 1 below bar 3.", why: "test-validate-feature-json.py:810; 2/1/48.0, ABC driver." }
    - { kind: substance, scope: task, severity: med, reader: code-reviewer, summary: "Seven pinned functions require grade-2 reasons and retain concrete maintenance risks.", why: "check-state.py:2904; plan-merge.py:2088,2251; validate-digest.py:402; test-check-state-feat59.py:385; test-plan-merge.py:3769,3804." }
  must_fix:
    - "T-04: make record-amendments genuinely all-or-nothing across plan.yaml and feature.json, including failure after ledger transformation but before plan commit, and prove that failure mode."
    - "Resolve all six pinned high code-grade records; rerun code-grade against the same pinned-review procedure."
  spec_violations: []
  code_grade: fail
  reviewed: "33f45262..c2bf2f3a2ffba5faf243867a915f082da17f387d"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - .harness/harness/features/BUG-1716-build-amendments/notes/review-harness-code-reviewer-c0.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1716-build-amendments/.harness/harness/features/BUG-1716-build-amendments/notes/review-harness-code-reviewer-c0.md
```
