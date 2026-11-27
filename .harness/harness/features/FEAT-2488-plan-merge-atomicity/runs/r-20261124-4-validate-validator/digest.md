# Validate c3 (rework round c2 of 2, the last): FEAT-2488 plan-merge atomicity: ESCALATE

**BLUF.** At review_sha `2eab047b9971bc428db21d1527ce614826ebc692` (base `2491336e`), MF-8 is closed and MF-7's
exact case (a closed stderr) is closed. CI is green: the full unit kind (68 files) and the full integration kind
(95 files) pass, the canonical-reader audit reports 0 unresolved sites across 101 files, both literal verifies exit 0,
SC-01..SC-07 are met, and all three perspectives pass. Two new **high** findings still gate:

- **MF-9**, a T-02 defect: a landed amendment can exit 120 at interpreter shutdown.
- **MF-10**, a T-01 design gap: journal replay bypasses plan.yaml's single-writer rule.

The signed rework budget (2 rounds) is spent, and MF-10's likely remedy edits a file that no task owns. This goes to
the operator, not into a fix cycle. **No fix round remains under the signed ruling.**

Readers: qa PASS, goal-check PASS, ui PASS (scoped out after measuring 125 files base..pin and 24 in the delta),
code-reviewer FAIL, security-reviewer FAIL. The security reviewer's first dispatch failed on provider capacity before
doing any work. It was re-dispatched once at the same pin and ran to completion.

## Closure of the c2 must-fix items

|c2|Status at pin|Who measured|
|---|---|---|
|MF-8 (fstat on the opened fd)|**closed** on both routes (recover_journals(plan) and locked_update(feature.json)). FIFO, directory, /dev/null and socket descriptors are refused before any read; the FIFO is left in place with its bytes unread; the descriptor is closed exactly once|code (re-ran its own probe), security (type half), qa (red reproduced at 6/165 at 13500626), pm|
|MF-7 (closed-stderr ValueError)|**closed** for the measured case; **open** for buffered broken pipes, see MF-9|code, qa and pm mutants|
|G-b, F-2r, four hostile shapes|now suite tests. QA reports they are weakly discriminating (A3, advisory)|qa, pm|
|Amendments T-01 (4), T-02 (7)|ledgered; the signature stands, with no APPROVAL-RESET. pm judges both truthful. Code-reviewer shows that (7)'s "the verb still exits 0" is false under buffered stdio (MF-9)|pm, code|

## Must-fix (ranked)

1. **MF-10, T-01, high (security-reviewer), substance.** The orchestrator's domain grant `.harness/*/features/**`
   (`.harness/team-config.yaml:42`) covers `plan.yaml.harness-merge.journal`. check-domain's plan route denial
   (`check-domain.py:2540-2562`, `RE_PLAN_YAML`) matches only `plan.yaml` itself. A governed actor that may not
   Write plan.yaml can therefore Write a structurally valid journal, with before-hashes computed from the current
   members and arbitrary after images. The next legitimate plan-merge or feature.json write replays that journal
   into plan.yaml before its own transform runs (`harness_merge.py:423-479`). This defeats "plan.yaml has exactly
   ONE writer" (FEAT-41 REQ-05).

   I opened the grant and the denial and confirmed the static trace; nobody executed it. The mechanism was
   introduced by this feature (T-01 adds JOURNAL_SUFFIX; the base has no journal), so it is not pre-existing
   relative to FEAT-2488.

   **Retraction (O-04).** My c2 digest dismissed "the journal is unauthenticated" on the premise that "anyone able
   to plant a sidecar in the feature directory can write plan.yaml and feature.json directly". That premise is
   false for the orchestrator's Write route, and I retract it. The verdict that digest supported (FAIL on MF-7 and
   MF-8) stands on its own grounds.

   **Remedy options (operator's call):**
   - (a) Extend check-domain's denial to the journal sidecar names. This edits a harness bin gate (G-03,
     main-session-direct, DEC-174) that is outside both tasks' `files:`.
   - (b) Authorize replay inside T-01, for example by binding the journal to its producer or to plan-merge. This is
     a new journal surface, which C5 of the signoff ruling forbids without approval.
   - (c) Accept the risk and backlog it, as a recorded operator decision.

2. **MF-9, T-02, high (code-reviewer), substance.** `guards._print_receipts` and `_relay_after_commit`
   (`plan_merge/guards.py:271-297`) catch the first write or flush error. CPython keeps the unflushed buffer and
   retries the flush at finalization, so a process without `PYTHONUNBUFFERED` prints `Exception ignored while
   flushing sys.stdout` and exits **120**. Code-reviewer measured this for amend and record-amendments with a
   broken stdout, and for a real pair write with feedback sent to a broken fd 2. In each case both files landed
   once, no journal was left, and the exit code was 120. With `PYTHONUNBUFFERED=1` the exit code is 0. I read the
   site and its docstring promises "the verb still exits 0".

   This falsifies T-02 amendment (7) and SC-01's advisory-after-commit outcome.

   **Why the suite missed it.** The review shell exports `PYTHONUNBUFFERED=1` and `test-plan-merge.py:5189-5229`
   inherits it, so 2488/l never exercises the buffered path. QA's and pm's green results were therefore unable to
   see this (P-06).

   **Fix shape.** On a caught stdout/stderr failure, redirect the broken stream's fd to devnull, the documented
   SIGPIPE idiom. Add a test whose child runs with `PYTHONUNBUFFERED` unset. This is inside T-02 and inside C5, but
   no round remains.

**Fix order, if the operator grants a round.** MF-10's ruling comes first, because option (b) changes the T-01
journal read path. MF-9 is independent and is a one-site change in T-02.

## Assessed, not gating

- **QA A1, write_feature_json relay (low, advisory).** The relay at `:227` is unguarded, and non-amendment verbs
  use bare receipt prints. Both are pre-existing at base and outside MF-7's amendment scope: backlog. If MF-9 is
  fixed, the same helper should cover them; that is the operator's scoping call.
- **QA A2 (info, form).** `_require_regular`'s lstat is now redundant with the fstat. A mutant that turns it into a
  no-op stays green, and the docstring's "a FIFO standing at the name is never opened" has no test.
- **QA A3 (info).** F-2r and 2488/e/c do not discriminate independently.
- **Code grade 2 ×3 (med, non-gating).** Three grade-2 test functions, with the reasons recorded in the code note.
  The diff-mode grade is otherwise 145 passing.
- **pm F-3 (form advisory).** See the goal-check note.
- Previously ruled backlog items were not re-raised: case-insensitive alias, unescaped filenames, FEAT-63 census
  loophole, member-path FIFO.

## Adequacy

- QA's `suite: pass` rests on the DEC-255 receipts `qa/manifest-unit.json` (68 files) and
  `qa/manifest-integration.json` (95 files). Both discovery counts are non-zero and unchanged from c2.
- Fail-first evidence for MF-8 is a real red (6/165 at 13500626, reproduced by QA and by pm). For MF-7 it is the
  receipt `03-red-integration-plan-merge-mf7.txt` plus mutants from QA and pm.
- The suite runs under the review shell's `PYTHONUNBUFFERED=1`, so green results cannot show anything about buffered
  stdio. That gap is how MF-9 got past three green readers.

Members' artifacts: `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c3.md` and
`notes/research-FEAT-2488-plan-merge-atomicity-goalcheck-validate-c3.md`.

```yaml
VERDICT: ESCALATE
DIGEST:
  headline: 'ESCALATE at 2eab047b: MF-8 and MF-7 (closed stderr) are closed. CI is
    green (unit 68 files, integration 95 files, audit 0 unresolved across 101 files)
    and SC-01..07 are met. Two new HIGH findings gate: MF-9 (T-02) makes a landed
    amendment exit 120 when a buffered pipe breaks, and MF-10 (T-01) lets an orchestrator-written
    journal sidecar replay into plan.yaml past its single-writer denial. The rework
    budget is spent, and MF-10''s remedy is an operator decision.'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Unit (68 files) and integration (95 files) green at the pin with DEC-255
      receipts. The MF-8 red is reproduced at 6/165; MF-7 is re-proved with mutants;
      the SC-04 lock and both literal verifies are green; the audit reports 0 unresolved.
      3 advisories.
    files_touched:
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-4-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-4-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: MF-8 and MF-7's exact closed-stream case are closed. A landed amendment
      exits 120 when the buffered stdout or stderr pipe is broken. Code grade is grade_2
      (3 non-gating).
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: MF-8's descriptor-type check is closed. The governed orchestrator's
      sidecar Write grant bypasses the protected plan.yaml edit route through journal
      replay.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B out of scope: none of 125 files base..pin or 24 files in the
      delta is UI.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: 3 perspectives pass and SC-01..07 are met. MF-7 and MF-8 are closed
      by mutant measurement. Both ledgered amendments match the code and the signature
      stands. F-2r is closed.
    files_touched: []
  must_fix:
  - 'MF-10 (T-01, high, security-reviewer): the orchestrator''s domain grant .harness/*/features/**
    (team-config.yaml:42) covers plan.yaml.harness-merge.journal, while check-domain.py:2540-2562
    denies Write only on plan.yaml itself. A governed actor can Write a valid journal
    (before-hashes from the current members, arbitrary after images), and the next
    legitimate write replays it into plan.yaml before its own transform (harness_merge.py:423-479).
    That bypasses the single-writer rule (FEAT-41 REQ-05). The journal is introduced
    by this feature. Remedy needs an operator ruling: (a) deny the journal names in
    check-domain.py (a harness bin gate outside every task''s files; DEC-174/G-03),
    (b) authorize replay in T-01 (a new journal surface under C5), or (c) accept the
    risk and backlog it.'
  - 'MF-9 (T-02, high, code-reviewer): guards._print_receipts and _relay_after_commit
    (plan_merge/guards.py:271-297) catch the first stdout or stderr failure, but CPython
    retries the buffered flush at finalization. Measured: amend, record-amendments
    and a pair write with feedback each commit once and leave no journal, then exit
    120 when PYTHONUNBUFFERED is unset. This falsifies T-02 amendment (7)''s ''the
    verb still exits 0'' and SC-01''s advisory-after-commit outcome. Fix: on a caught
    failure, dup2 devnull over the broken fd; add a child test that runs with PYTHONUNBUFFERED
    unset.'
  files_touched:
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-4-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-4-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/observations/harness-qa.md
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-4-validate-validator/state.yaml
  branch: none
  open_questions:
  - id: OQ-1
    question: 'The signed rework budget (2 rounds) is spent, and two high findings
      remain at 2eab047b: MF-9 (T-02, exit 120 on a buffered broken pipe after commit)
      and MF-10 (T-01, an orchestrator-written journal replays past plan.yaml''s single-writer
      denial). Does the operator grant a further rework round? If not, does the feature
      ship with these recorded as accepted risk, or stop?'
    blocking: true
  - id: OQ-2
    question: 'MF-10 remedy: (a) extend check-domain.py''s plan.yaml route denial
      to the *.harness-merge.journal sidecars (a harness bin gate, main-session-direct
      under DEC-174 and outside every task''s files), (b) authorize replay inside
      T-01 (a new journal surface that C5 of the signoff ruling forbids without approval),
      or (c) accept the risk and backlog it?'
    blocking: true
  - id: OQ-3
    question: 'QA A1: write_feature_json''s post-commit relay (:227) and the non-amendment
      verbs'' bare receipt prints are pre-existing at base and outside MF-7''s scope.
      Backlog them, or fold them into MF-9''s fix if a round is granted?'
    blocking: false
  escalations:
  - id: E-1
    raised_by: harness-security-reviewer
    question: Journal replay bypasses check-domain's plan.yaml single-writer denial
      for a governed Write-only actor; the remedy edits check-domain.py or adds a
      journal-authorization surface
    domain: harness enforcement (check-domain.py) / signed C5 journal surface
    routed_to: harness-orchestrator -> main session (operator)
    resolution: pending
    decided_by: pending
    recorded_as: runs/r-20261124-4-validate-validator/digest.md MF-10
  expertise_update: []
  adequacy_notes:
  - MF-8 is closed on both routes. Code-reviewer re-ran its own c2 probe; security
    measured the FIFO, directory, character device and socket cases; QA and pm reproduced
    the red at 13500626 (6/165).
  - MF-7's exact case is closed (closed TextIO stderr), measured by code-reviewer
    and by the QA and pm mutants. The broader post-commit stream failure is MF-9.
  - 'Retraction (O-04): the c2 digest dismissed the unauthenticated journal on the
    premise that ''anyone able to plant a sidecar can write the pair directly''. That
    premise is false for the orchestrator''s Write route (team-config.yaml:42 vs check-domain.py:2540-2562),
    and I verified both sites. The c2 FAIL verdict stands on MF-7 and MF-8.'
  - MF-10 is a static trace that I confirmed at source; no reader executed it. It
    is feature-introduced (the base has no journal), not pre-existing.
  - 'Three green readers could not see MF-9: the review shell exports PYTHONUNBUFFERED=1
    and test-plan-merge.py''s 2488/l inherits it, so the buffered finalization path
    was never exercised.'
  - 'QA''s suite: pass rests on DEC-255 receipts manifest-unit.json (68 files) and
    manifest-integration.json (95 files). Both discovery counts are non-zero and unchanged
    from c2. Both literal verify: blocks exit 0, and the canonical-reader audit reports
    0 unresolved across 101 files.'
  - Security's first dispatch failed on provider capacity (turn_rate_limit_exceeded)
    before doing any work. It was re-dispatched once at the same pin and completed.
  - 'Advisories (not gating): QA A2, the lstat in _require_regular is now redundant
    with the fstat and a FIFO-at-name-never-opened test is missing (info). QA A3,
    F-2r and 2488/e/c are weakly discriminating (info). Code: three grade-2 test functions
    (med, non-gating; diff-mode grade otherwise 145 passing). pm F-3 (form).'
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: test-plan-merge.py 2488/a-l and test-harness-merge-journal.py 165/165
      green in QA manifest-integration.json at 2eab047b. MF-9 shows the advisory-after-commit
      clause fails under buffered stdio, which the suite does not exercise.
  - id: SC-02
    verdict: met
    method: inspection
    evidence: No mkstemp, os.replace or journal names under plan_merge/ at the pin;
      a single locked_pair_update call (pm git grep rc 1)
  - id: SC-03
    verdict: met
    method: inspection
    evidence: harness_merge.py:535-560 runs journal fsync, publish, directory fsync,
      member replace, then unlink
  - id: SC-04
    verdict: met
    method: automated
    evidence: 2488/g green at the pin; regression lock baseline in red-t02-plan-merge-base.txt:892-895
  - id: SC-05
    verdict: met
    method: inspection
    evidence: 'The SC-05 successors are untouched in the delta: 8 checks, the named
      failure, raw bytes'
  - id: SC-06
    verdict: met
    method: inspection
    evidence: Docstrings were updated for the fstat; amend.py has no APPROVAL_RESET
  - id: SC-07
    verdict: met
    method: automated
    evidence: The seven suites are green in QA manifest-integration.json at the pin
      and their pre-existing assertions are unedited
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - No test runs a CLI child with PYTHONUNBUFFERED unset and a broken stdout or stderr
    after commit (MF-9)
  - No test plants a journal through a governed Write and checks that replay is refused
    or authorized (MF-10)
  - No test covers a FIFO standing at the journal name that is never opened; the lstat
    is redundant with the fstat (QA A2)
  - F-2r and 2488/e/c do not discriminate independently (QA A3)
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-security-reviewer
    summary: 'MF-10 T-01: a journal sidecar written by the governed orchestrator replays
      into plan.yaml, bypassing check-domain''s single-writer denial'
    why: team-config.yaml:42 grants .harness/*/features/**; check-domain.py RE_PLAN_YAML
      matches only plan.yaml; replay validates hashes, not provenance (harness_merge.py:423-479).
      Static trace, confirmed at source by the lead.
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'MF-9 T-02: a landed amendment exits 120 when a buffered stdout or stderr
      pipe is broken (guards.py:271-297)'
    why: 'Measured: both files land once and no journal is left, then ''Exception
      ignored while flushing sys.stdout'' and rc 120 without PYTHONUNBUFFERED; rc
      0 with it. This contradicts T-02 amendment (7).'
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: 'A1: write_feature_json post-commit relay and the non-amendment verbs''
      receipt prints are unguarded (pre-existing, advisory)'
    why: 'Measured: a ValueError after cycles_used landed. Present at base :210, outside
      MF-7''s scope.'
  - kind: form
    scope: none
    severity: info
    reader: harness-qa
    summary: 'A2: the _require_regular lstat is redundant with the fstat; the docstring
      promise has no test (advisory)'
    why: A no-op mutant stays green on all 43 FIFO and hostile checks
  - kind: substance
    scope: none
    severity: info
    reader: harness-qa
    summary: 'A3: F-2r and 2488/e/c do not discriminate independently (advisory)'
    why: Under M5, F-2r reddens only alongside 2488/e/b
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: Three grade-2 test functions (case_2488_a_closed_stderr_after_the_commit_is_advisory,
      case_missing_before_key_refuses, case_fifo_swapped_after_lstat_refuses) (non-gating)
    why: The grader's grade_2 reasons are recorded; each keeps a needed contrast in
      one matrix
  - kind: form
    scope: none
    severity: low
    reader: harness-pm
    summary: F-3 goal-check form advisory (see goal-check note)
    why: Advisory only; does not affect any SC verdict
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-4-validate-validator/digest.md
```
