# Validate c2 (rework round c1 of 2): FEAT-2488 plan-merge atomicity: FAIL

**BLUF.** The c0 findings are closed at review_sha `c35841fe5511109dffb958eebe6dad86dbf654d7` (base `2491336e`), with one
exception: MF-3 is closed only for static entries. CI is now green. The full unit kind (68 files) and the full integration
kind (95 files, including `test-checker-structure-locks.py`) pass from QA's managed pin checkout. The canonical-reader
audit is clean, all seven SCs are met, and all three perspectives pass. The run still FAILs on two small must-fix items
in code the fix round shipped. One is high, so `severity_max: high`. Both are one-line fixes for rework round 2, the
last round in the budget.

Readers: qa PASS, goal-check PASS, security PASS (med advisories), ui PASS (scoped out after measuring 98 files, none
of them UI), code-reviewer FAIL. All five readers ran in one wave at the same pin.

## c0 closure

|c0|Status at pin|Who measured|
|---|---|---|
|MF-1 broad-catch census|closed: structure-locks green inside the full integration kind|qa (DEC-255 receipt)|
|MF-2 pair binding / lock order|closed as ruled: refusal at exit 5 before any *secondary* lock; the reversed primary takes zero locks|code (probes)|
|MF-3 dangling / non-regular|static cases closed; **open under a swap**, see MF-8|code + security|
|MF-4 before_sha256 key|closed; explicit null still means absence|code|
|MF-5 amend --show|closed; the full fixture snapshot is unchanged|code, pm (probe)|
|MF-6 SC-05 named failure, raw bytes|closed; still 8 checks|code, pm|
|G-a..G-d|G-a, G-c, G-d closed. G-b is covered only at the unit seam and by probe (advisory)|qa|

## Must-fix (ranked)

1. **MF-7, T-02, high (code-reviewer), substance.** `_relay_after_commit` (`plan_merge/amendments.py:195-205`) catches
   `(OSError, ValueError)` from the relay. Its fallback `print` to the same stream is wrapped in `suppress(OSError)`
   only, so on a closed stream the fallback raises `ValueError` again and that escapes. Code-reviewer measured the
   result: both members replaced, journal gone, then a traceback in place of receipts. A committed amendment is reported
   as a failure. That contradicts the docstring's "never a refusal" and the T-02 amendment's reason (2), which names
   exactly this class. I opened the site and confirmed it. My own read is that the trigger is improbable, because it
   needs an in-process closed `sys.stderr`; a broken pipe raises OSError, which is suppressed. That read is not a
   re-rating: the rating stays the reader's high. Fix: suppress `(OSError, ValueError)` and add a test with a real
   closed stream after commit.
2. **MF-8, T-01, med (code-reviewer and security-reviewer), substance.** `_journal_bytes`
   (`harness_merge.py:330-342`) never `fstat`s the opened descriptor. Code-reviewer swapped in a FIFO, already holding
   a valid record, after the `lstat`. Recovery read it, replayed both members and removed the FIFO. Security-reviewer
   reports the same gap as "lstat-to-open does not verify the opened journal's type or identity". This is one defect;
   I merged the two reports, and both rated it med. I confirmed the site. It gates because it falsifies T-01's ledgered
   amendment reason (4), "the journal is read only from a regular file", and MF-3's ruled "no open on a FIFO". Fix: run
   `S_ISREG(os.fstat(fd).st_mode)` after the open, refuse at exit 5 if it fails, and test a buffered FIFO swap.

**Fix order.** The two fixes are independent: do MF-8 (T-01 core), then MF-7 (T-02). Neither changes the journal schema
or the lock order, so both stay inside C5. Each lands red-first, and the full unit and integration kinds re-run before
the re-pin. If T-01's amendment reason (4) wording stays as it is, MF-8 makes it true again, and no further amendment
is needed.

## Assessed, not gating

- **Code Q1 / "before ANY lock" (code med).** Dismissed. The fix ruling's MF-2 threshold is "before any secondary lock"
  (`answers-2026-11-24-validate-c0.md`, C5 check), and the shipped code meets it. "Before any lock" came from the
  dispatch's paraphrase, not from the ruling. A 6 LOCKED under contention is ordinary lock behaviour, and the journal
  still refuses at 5 once the lock is free.
- **The journal is unauthenticated** (security med, already present at 987e57b9). Not gating: anyone able to plant a
  sidecar in the feature directory can write plan.yaml and feature.json directly. Security showed no sidecar-only route.
- **Case-insensitive alias; discovered filenames are not escaped** (security low ×2, already present). Advisory.
- **G-b, and four hostile journal shapes covered only by QA probes** (qa low). **F-2r, re-run after route (e) carried
  only by a probe** (pm form/low). Advisory, and cheap to fold into the round-2 test edits.
- Disclosures (the throwaway-clone grading, bun install #2474) are noted as stated. No reader re-raised them.

## Adequacy

- QA's `suite: pass` rests on DEC-255 receipts `qa/manifest-unit.json` (68 files) and `qa/manifest-integration.json`
  (95 files, the full kind). The discovery counts are non-zero (P-13).
- The fix-delta reds are receipts at 987e57b9. QA reproduced the unit red independently (30/142 in-process). G-a, G-c
  and G-d were added as assertions only and were green before the fix, so they do not show that they discriminate.
- Both remaining defects come from concurrency or stream state that no test builds. The green suite does not cover them.

Members' artifacts: `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c2.md`,
`notes/research-FEAT-2488-plan-merge-atomicity-goalcheck-validate-c2.md`.

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'FAIL at c35841fe: the c0 findings are closed, CI is green (unit 68 files
    plus the full integration kind of 95 files, structure-locks included, canonical-reader
    audit clean), and SC-01..07 are met. Two small items in the fix-round code are
    still must-fix: MF-7 (high), where a closed stderr fails an amendment that has
    already committed, and MF-8 (med), where a FIFO swapped in after lstat gets replayed
    because the opened fd is never fstat''d.'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Unit (68 files) and the full integration kind (95 files) both pass at
      the pin, structure-locks included. MF-2..MF-5 are asserted by tests. G-b and
      four hostile journal shapes are covered by probes only (advisory).
    files_touched:
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-3-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-3-validate-validator/qa/manifest-integration.json
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: A committed amendment can still report failure, and recovery accepts
      a buffered FIFO swapped in after lstat.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: The repair closes journal-selected sibling writes, static-entry hangs
      and the --show mutation. The provenance and pathname-race findings remain as
      advisories.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B is out of scope: none of the 98 changed files is UI, a component
      or a stylesheet.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: SC-01..SC-07 are met and all three perspectives pass. The c0 SC-05 partial
      and the operator-clause breaks are closed, confirmed by executed probes.
    files_touched: []
  must_fix:
  - 'MF-7 (T-02, high, code-reviewer): _relay_after_commit (plan_merge/amendments.py:195-205)
    wraps its fallback stderr print in suppress(OSError) only. On a closed stream
    that print raises ValueError, which escapes after both members have committed
    and the journal has been removed, so a landed amendment is reported as a traceback.
    Suppress (OSError, ValueError) and add a test with a real closed stream after
    commit.'
  - 'MF-8 (T-01, med, code-reviewer+security-reviewer): _journal_bytes (harness_merge.py:330-342)
    never checks the type of the opened descriptor. A FIFO swapped in after lstat,
    already holding a valid record, was read and replayed. Check S_ISREG(os.fstat(fd).st_mode)
    after the open, refuse at exit 5 if it fails, and test a buffered FIFO swap. Until
    then, T-01 amendment reason (4) and MF-3''s ''no open on a FIFO'' are false.'
  files_touched:
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-3-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-3-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-3-validate-validator/state.yaml
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  adequacy_notes:
  - 'c0 closure: MF-1 is closed (QA DEC-255 integration receipt). MF-2 is closed as
    ruled: refusal at exit 5 before any secondary lock, and the reversed primary takes
    zero locks. MF-4, MF-5 and MF-6 are closed (code-reviewer probes; pm probe for
    MF-5). MF-3 is closed for static entries but open under a swap, which is MF-8.'
  - Code-reviewer's Q1 (and its med finding that MF-2 does not meet 'before ANY lock')
    is dismissed. The ruling's threshold is 'before any secondary lock' and the code
    meets it. 'Before any lock' came from the dispatch's paraphrase. A 6 LOCKED under
    contention is ordinary lock behaviour.
  - MF-7 keeps code-reviewer's high rating. My own read is that the trigger is improbable,
    because it needs an in-process closed sys.stderr; a broken pipe raises OSError,
    which is suppressed. The fix is still one line, and the defect contradicts the
    docstring and T-02 amendment reason (2).
  - 'MF-8 was reported by both code-reviewer and security-reviewer, both at med. It
    is one defect, merged here. The two fixes are independent and stay inside C5:
    do MF-8, then MF-7, each red-first, then re-run the full unit and integration
    kinds before the re-pin. This is the last round in the budget.'
  - 'Security advisories, not gating: journals are unauthenticated (med, already at
    987e57b9; anyone able to plant a sidecar can write the pair directly), a case-insensitive
    alias (low), and unescaped discovered filenames (low).'
  - 'Test-gap advisories, cheap to fold into the round-2 test edits: G-b and four
    hostile journal shapes are covered by probes only (qa low), and the further re-run
    after route (e) is covered by a probe only (pm F-2r, form/low).'
  - G-a, G-c and G-d were added as assertions only and were already green before the
    fix, so they do not show that they discriminate. Both remaining defects come from
    stream or concurrency states that no test builds.
  - 'C4 forbidden surfaces were reported untouched base..pin. QA''s receipts bind
    to this run: manifest-unit.json covers 68 files and manifest-integration.json
    covers 95, so discovery is non-zero.'
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: test-plan-merge.py case_2488_* including G-a/c/d, green in QA manifest-integration.json
      at c35841fe; red at base in notes/red-t02-plan-merge-base.txt
  - id: SC-02
    verdict: met
    method: inspection
    evidence: no mkstemp/os.replace/journal in plan_merge/; one locked_pair_update
      call (amendments.py:240)
  - id: SC-03
    verdict: met
    method: inspection
    evidence: 'harness_merge.py:516-541: journal fsync, publish, directory fsync,
      then member replace, then unlink'
  - id: SC-04
    verdict: met
    method: automated
    evidence: case_2488_amend_stdout_is_unchanged green at base and at the pin
  - id: SC-05
    verdict: met
    method: inspection
    evidence: case_1985 successor asserts PermissionError; raw-byte _bytes snapshots;
      8 checks (test-plan-merge.py:181-183,4679-4791)
  - id: SC-06
    verdict: met
    method: inspection
    evidence: docstrings, lock order and exit-5 clause present; no reset path in amend.py
  - id: SC-07
    verdict: met
    method: automated
    evidence: the seven suites pass in the QA manifests at the pin; their diffs since
      base are unchanged apart from the strengthened SC-05 cases
  needs_approval: false
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - No test closes the stderr stream after commit (MF-7)
  - No test swaps a buffered FIFO in after lstat (MF-8)
  - 'G-b: feature.json-write recovery from torn states (b) and (c) is tested only
    at the unit seam'
  - 'Four hostile journal shapes are covered only by QA probes: directory, dangling-via-feature.json,
    missing key via feature.json, and feature.json-primary via plan.yaml'
  - 'pm F-2r: no suite assertion covers the further re-run after route (e)'
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'MF-7 T-02: the closed-stream ValueError from the fallback print escapes
      _relay_after_commit after commit'
    why: 'Measured: plan=new, ledger=new, journal gone, then a ValueError traceback;
      the fallback print suppresses only OSError (amendments.py:201-205)'
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer, harness-security-reviewer
    summary: 'MF-8 T-01: a buffered FIFO swapped in after lstat is read and replayed'
    why: 'Measured by code-reviewer: recovery returned True, wrote both members and
      removed the FIFO. No fstat on the opened fd (harness_merge.py:330-342)'
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-01: malformed-content journals take plan.yaml.lock before refusing
      (dismissed)'
    why: 'Dismissed: the ruled threshold is before any secondary lock and the code
      meets it; ''before any lock'' was a dispatch paraphrase'
  - kind: substance
    scope: none
    severity: med
    reader: harness-security-reviewer
    summary: 'T-01: the journal authenticates neither its producer nor its after images
      (advisory)'
    why: 'Already present at 987e57b9. Not gating: an actor able to plant a sidecar
      can write the pair directly, and no sidecar-only route was shown'
  - kind: substance
    scope: none
    severity: low
    reader: harness-security-reviewer
    summary: 'T-01: case-insensitive journal alias can evade discovery (advisory)'
    why: Already present; reproduced (measured) on a case-insensitive temp filesystem
  - kind: substance
    scope: none
    severity: low
    reader: harness-security-reviewer
    summary: 'T-01: discovered journal filenames are not escaped in diagnostics (advisory)'
    why: Already present; the 80-char repr bound covers field values, not paths
  - kind: substance
    scope: none
    severity: low
    reader: harness-qa
    summary: G-b and four hostile journal shapes are probe-only (advisory)
    why: A later narrowing to the tested routes would ship green
  - kind: form
    scope: none
    severity: low
    reader: harness-pm
    summary: 'F-2r: the further re-run after route (e) is carried by a probe only
      (advisory)'
    why: The SC-01 clause has no suite assertion
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-3-validate-validator/digest.md
```
