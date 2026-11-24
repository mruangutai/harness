# Validate c1 — FEAT-2488 plan-merge atomicity — FAIL

**BLUF.** The run fails at review_sha `95606ddbaf9ab36f505328420159d97a10ad820d` (base `2491336e`). All SC suites are green, the
canonical-reader audit is clean, and SC-01..04, 06 and 07 are met as written. CI would still go red: the integration
kind fails on `test-checker-structure-locks.py`. Journal recovery also has four gating defects, all in hostile or
corrupted on-disk states that the tests never build, and SC-05 is partial. Six must-fix items, `severity_max: high`.
One decision has to come before the fix round: the signed task text requires the broad catches the CI census refuses.

Readers: qa FAIL, code-reviewer FAIL, security-reviewer FAIL, pm goal-check FAIL, ui-reviewer PASS (it scoped itself out
after measuring 68 changed files, none of them UI). Every reader ran in one wave at the same pin.

## Must-fix (ranked, de-duplicated)

1. **MF-1: CI integration is red** (qa; substance; high; T-01 and T-02). The FEAT-63 broad-catch census has a ceiling of 0. It
   fires on five new `except Exception` handlers: `harness_merge.py:364,464`, `plan_merge/amendments.py:199,235` and
   `plan_merge/guards.py:48`. The same test passes at base. `BROAD_CATCH_CEILINGS` lives in `check-plan-routes.py`, which
   the BRIEF forbids editing. That leaves narrowing the handlers as the only remedy, and the signed T-01 §6 and T-02
   items 2–3 spell out "any other Exception". Disclosure 1 ruled on BaseException versus Exception, not on this census.
   → OQ-1, blocking.
2. **MF-2: recovery is not bound to the authorized pair** (code-reviewer high + security-reviewer med; substance;
   T-01). Seen at `harness_merge.py:294–308,368–386`. A one-member record rewrites only the plan, and a sibling file can stand in
   as the second member (BRIEF.md, for example). A `feature.json`-primary journal takes `feature.json.lock` before
   `plan.yaml.lock`, which breaks the BRIEF's "no path acquires them reversed". **Rated high:** the lock-order clause is
   literal, and the writes land outside the pair. Security rated it lower because only a crafted sidecar triggers it, but
   the shipped code still has the reversed path.
3. **MF-3: a dangling or non-regular journal entry hangs writers instead of refusing** (code high + security med;
   substance; T-01). Seen at `harness_merge.py:282–291,311–336,372–378,409–414`. When the primary's own entry is a dangling symlink,
   `_journal_names` returns True but `os.path.exists` returns False, so `locked_update` loops forever. Code-reviewer
   measured 7 passes with no progress. A FIFO blocks on open. **Rated high:** the hang has no deadline and no diagnostic.
   Every feature.json writer (gh-sync, factory, rework) would hang, which is the opposite of "refused loudly".
4. **MF-4: a missing `before_sha256` key counts as a recorded absence** (code-reviewer; substance; high; T-01;
   `harness_merge.py:248–252`). It was measured recreating a removed ledger and deleting the journal. The module's own
   `_read_journal` contract calls any malformed record UNREADABLE (exit 5).
5. **MF-5: `amend --show` writes** (code-reviewer high + security-reviewer med; substance; T-02). `_resolve_plan` recovers
   before the show branch (`amend.py:211–221`, `guards.py:55–82`). Both reviewers measured a show call that
   rewrote both files and exited 0. **Rated med:** the state it reaches is the correct roll-forward that the next write
   would perform anyway, so nothing is corrupted. It is still must-fix because it breaks `plan-merge.py:252–253`'s
   read-only promise and D-02's limit of recovery to mutating verbs, and that breaks the operator's "behave as before".
6. **MF-6: SC-05 is partial** (pm low + code-reviewer med; substance; T-02; `tests/integration/test-plan-merge.py`). The
   `case_1985` successor never asserts that stderr names the failure. At `:4694–4697` the test accepts any pair refusal,
   and the snapshot at `:176–178` normalizes newlines, so its "byte-identical" check is not a raw-byte check. **Rated
   med:** the SC's literal terms "naming it" and "byte-identical" are both unmet, and no signed ruling narrows them.

**Fix order.** Get the OQ-1 ruling first, because it decides the shape of the except blocks that MF-2..MF-4 rewrite.
Then MF-2/3/4 in T-01. They change what recovery refuses, and MF-5 and the tests depend on that. Then MF-5, then MF-6
together with the advisory SC-01 assertions below. The whole feature is main-session-direct under DEC-174
(`harness_merge` is imported by validate-digest and dispatch-guard), so Main runs the fix round directly, inside the
signed rework budget of 2 rounds / 90 minutes.

## Assessed, not gating

- **Replay after a failed initial directory fsync** (code-reviewer med; T-01). `_commit_published` hits EIO at :458,
  and the replay later rewrites both members without ever fsyncing the journal's directory. Q2(c) waived only the
  post-unlink fsync, so this case is not covered. Adding an fsync is a new journal surface under C5, so it goes to the
  advisor. The BRIEF puts OS-crash durability outside the guarantee. Non-gating → OQ-2.
- **Diagnostics echo raw journal field contents** (security low; T-01; `harness_merge.py:248–279,347–349`). Cheap to
  bound with `repr` truncation while MF-2/4 are open. Advisory.
- **SC-01 assertion gaps** (qa coverage gaps G-a..G-d; pm F-2 form/low). Nothing tests torn state (b) through
  `record-amendments`. Feature.json-write recovery is integration-tested only from state (a). Nothing tests exit 5 via
  `amend`. Nothing tests the re-run exit code in (d), and no test asserts that the exit-5 message names the journal.
  pm's executed probes P1–P3 show the behavior holds, so SC-01 is met. These clauses are unguarded against regression,
  though: add assertions in the MF-6 round. Advisory.
- **pm OQ-3** (unit test edited after its build receipt, no stdout receipt, C6). Dismissed: QA's DEC-255 unit run at
  the pin includes `test-harness-merge-journal.py`, and it passes; the receipt is `qa/manifest-unit.json`.
- **Disclosures 1–6.** Judged as ruled; no reader re-raised them. Host-known reds: QA names only
  `test-checker-structure-locks.py` as failing, and that file is green at base, so it is not one of them.

## Adequacy

- pm graded the operator perspective **pass**. P-06 changes that to **partial**, because two clauses of the operator
  "done when" fall outside pm's lens. "A state the tools cannot reconcile is refused loudly, never overwritten" is
  broken by MF-3 and MF-4. "Every other locked write behaves as before" is broken by MF-5. The SC rows are still met
  as written. The perspective text is what the gap breaks.
- QA reports `matrix_ok: true`, which only means both required kinds exist and bind the SC tests. `suite` is **fail**.
  A matrix that is present with a red suite is not assurance (G-01).
- CI checks-job audit: `check-plan-routes.py --canonical-reader-audit` reports 0 unresolved over 188 sites in 101 files,
  so the discovery count is non-zero (P-13). Pass.
- Code-reviewer measured MF-2..MF-5 with probes. Security reviewed by reasoning and did not execute (stated in its
  `scope_reason`). Its findings are covered by code-reviewer's measured probes.

## Open questions

- **OQ-1 (blocking).** Narrowing the five `except Exception` handlers to the real error classes deviates from signed
  T-01 §6 and T-02 items 2–3. Does fable-advisor approve that under C5, recorded as a ledgered amendment? The
  alternative, raising the census ceiling, edits `check-plan-routes.py`, which the BRIEF forbids and which is
  operator-only.
- **OQ-2 (non-blocking).** Should replay fsync the journal directory when the initial directory fsync failed? This is
  a new journal surface under C5.

Members' artifacts: `notes/review-harness-{qa,code-reviewer,security-reviewer,ui-reviewer}-c1.md`,
`notes/research-FEAT-2488-plan-merge-atomicity-goalcheck-validate-c1.md`. QA receipts: `qa/manifest-unit.json`
(runner exit 0) and `qa/manifest-integration.json` (runner exit 1).

```yaml
VERDICT: FAIL
DIGEST:
  headline: 'FAIL at 95606ddb: the SC suites and the canonical-reader audit are green,
    but CI integration is red. The broad-catch census refuses 5 new `except Exception`
    handlers, and the signed text requires them, so a ruling is needed. Journal recovery
    has 4 gating defects: it accepts misbound or reversed-lock pairs, hangs on a dangling
    entry, recreates on a missing before key, and lets `amend --show` write. SC-05
    is partial.'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: FAIL
    headline: unit green; integration red at pin only on test-checker-structure-locks.py
      (5 new broad catches vs ceiling 0), green at base; canonical-reader audit 0
      unresolved/188 sites
    files_touched:
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-2-validate-validator/qa/manifest-unit.json
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-2-validate-validator/qa/manifest-integration.json
    - .harness/harness/features/FEAT-2488-plan-merge-atomicity/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: Recovery can replay the wrong files, reverse the lock order, or spin
      instead of refusing; amend --show also writes.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: FAIL
    headline: Journal replay trusts unapproved sibling destinations, can hang on non-regular
      entries, and mutates through amend --show.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B out of scope: none of the 68 changed files is UI, component
      or style.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: FAIL
    headline: SC-01..04, 06, 07 met; SC-05 partial (case_1985 successor never asserts
      the failure is named); dispositions all keep, no DECISIONS.md landing.
    files_touched: []
  must_fix:
  - 'MF-1 (T-01+T-02, high, qa): CI integration red. test-checker-structure-locks.py
    census (ceiling 0) fires on except Exception at harness_merge.py:364,464, plan_merge/amendments.py:199,235
    and guards.py:48. Narrow the handlers to the real error classes once OQ-1 is ruled;
    check-plan-routes.py is forbidden.'
  - 'MF-2 (T-01, high, code+security): bind recovery to the authorized amendment pair.
    Refuse one-member, misbound-sibling and feature.json-primary (reversed lock order)
    journals at exit 5 before taking any secondary lock or writing (harness_merge.py:294-308,368-386).'
  - 'MF-3 (T-01, high, code+security): refuse dangling-symlink and non-regular journal
    entries at exit 5 naming the journal, instead of spinning in locked_update or
    blocking on a FIFO (harness_merge.py:282-291,311-336,372-378,409-414).'
  - 'MF-4 (T-01, high, code): require the before_sha256 key; only an explicit null
    records an absence (harness_merge.py:248-252).'
  - 'MF-5 (T-02, med, code+security): keep amend --show read-only with a pending journal;
    recovery must not run before the show branch (amend.py:211-221, guards.py:55-82).'
  - 'MF-6 (T-02, med, pm+code): SC-05 successors must assert the specific named failure
    (case_1985 asserts none; :4694-4697 accepts any refusal) and compare raw bytes,
    without the newline normalization at test-plan-merge.py:176-178.'
  files_touched:
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-2-validate-validator/qa/manifest-unit.json
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-2-validate-validator/qa/manifest-integration.json
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/observations/harness-qa.md
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-2-validate-validator/state.yaml
  branch: none
  open_questions:
  - id: OQ-1
    question: "Narrowing the five new `except Exception` handlers (MF-1) to clear\
      \ the FEAT-63 broad-catch census deviates from signed T-01 \xA76 and T-02 items\
      \ 2-3, which spell out 'any other Exception'. Does fable-advisor approve the\
      \ narrowing under C5 as a ledgered amendment? The only alternative is raising\
      \ BROAD_CATCH_CEILINGS, which means editing check-plan-routes.py; the BRIEF\
      \ forbids that and it is operator-only. Needed before the fix round touches\
      \ the recovery except blocks."
    blocking: true
  - id: OQ-2
    question: When _commit_published's initial directory fsync fails (EIO, harness_merge.py:458)
      and the journal is already published, replay later rewrites both members without
      ever fsyncing the journal directory. Q2(c) waived only the post-unlink fsync.
      Should replay add that fsync? It is a new journal surface under C5 (code-reviewer
      med, non-gating; the BRIEF excludes OS-crash durability).
    blocking: false
  escalations: []
  expertise_update: []
  adequacy_notes:
  - 'Operator perspective re-graded from pm''s pass to partial: MF-3/MF-4 break ''refused
    loudly, never overwritten'' and MF-5 breaks ''every other locked write behaves
    as before''. The SC rows are still met as written.'
  - matrix_ok true only means both required kinds exist and bind the SC tests; the
    integration suite is red (runner exit 1).
  - 'CI canonical-reader audit at the pin: 0 unresolved over 188 sites in 101 files
    (non-zero discovery).'
  - SC-01 behavior is confirmed by pm's executed probes P1-P3, but several clauses
    have no test asserting them (qa G-a..G-d, pm F-2). Add those assertions in the
    MF-6 round (advisory).
  - 'Security low (raw journal fields echoed in diagnostics, harness_merge.py:248-279,347-349):
    advisory; cheap to bound while MF-2/MF-4 are open.'
  - 'pm OQ-3 dismissed: QA''s DEC-255 unit run at the pin (manifest-unit.json, exit
    0) includes test-harness-merge-journal.py.'
  - 'Fix order: OQ-1 ruling, then MF-2/3/4 (T-01), then MF-5, then MF-6 plus the SC-01
    assertions. Main runs the round directly under DEC-174, within the 2 rounds /
    90 min rework budget.'
  - 'Disclosures 1-6 judged as ruled; no reader re-raised them. The red structure-locks
    test is not one of the disclosed host-known reds: it is green at base.'
  - Security reviewed by reasoning only; its three overlapping findings are backed
    by code-reviewer's measured probes.
  sc_status:
  - id: SC-01
    verdict: met
    method: automated
    evidence: test-plan-merge.py case_2488_* green at pin; red at base (red-t02-plan-merge-base.txt:706,889);
      pm probes P1-P3. Some clauses are unasserted (advisory).
  - id: SC-02
    verdict: met
    method: inspection
    evidence: t02-build/03-sc02-grep-and-sc05-count.txt; one locked_pair_update call
      in amendments.py#write_plan_and_ledger
  - id: SC-03
    verdict: met
    method: inspection
    evidence: harness_merge.py _publish_journal fsync+rename, _commit_published dir
      fsync (458) before the member loop, unlink after; locked_update has no fsync
  - id: SC-04
    verdict: met
    method: automated
    evidence: case_2488_amend_stdout_is_unchanged passes at base (red-t02:892-895)
      and at pin; two-shape narrowing accepted by signoff Q2(b)
  - id: SC-05
    verdict: partial
    method: inspection
    evidence: 8 checks present, but the case_1985 successor never asserts the failure
      is named and snapshots normalize newlines (test-plan-merge.py:176-178,4694-4697)
      -> MF-6
  - id: SC-06
    verdict: met
    method: inspection
    evidence: 'pm goal-check note: docstrings, lock order and exit-5 contract present;
      no APPROVAL_RESET in amend.py'
  - id: SC-07
    verdict: met
    method: automated
    evidence: the seven named suites pass at the pin (manifest-integration.json) with
      unchanged assertions; the separate red structure-locks test is MF-1
  needs_approval: true
  severity_max: high
  matrix_ok: true
  coverage_gaps:
  - 'integration suite red: test-checker-structure-locks.py (MF-1)'
  - 'SC-01: torn state (b) not re-run through record-amendments at integration'
  - 'SC-01: feature.json-write recovery integration-tested only from torn state (a)'
  - 'SC-01: diverged exit 5 not tested via amend'
  - 'SC-01: re-run exit code in (d) not asserted; no test asserts the exit-5 message
    names the journal'
  - no test constructs a malformed, misbound, dangling or non-regular journal (MF-2..MF-4)
  - no test runs amend --show with a pending journal (MF-5)
  findings:
  - kind: substance
    scope: none
    severity: high
    reader: harness-qa
    summary: 'MF-1 T-01/T-02: 5 new except Exception handlers turn CI integration
      red (FEAT-63 census, ceiling 0)'
    why: test-checker-structure-locks.py FAILs at pin, PASSes at base; the census
      ceiling lives in forbidden check-plan-routes.py
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer, harness-security-reviewer
    summary: 'MF-2 T-01: recovery accepts one-member, misbound-sibling and reversed-lock-order
      journals'
    why: 'Reconciled to high over security''s med: the BRIEF''s ''no path acquires
      them reversed'' is literal, and the writes land outside the pair'
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer, harness-security-reviewer
    summary: 'MF-3 T-01: dangling or non-regular journal entry hangs writers instead
      of refusing at exit 5'
    why: 'Reconciled to high over security''s med: the hang has no deadline or diagnostic
      and wedges every writer of that file; measured 7 passes with no progress'
  - kind: substance
    scope: none
    severity: high
    reader: harness-code-reviewer
    summary: 'MF-4 T-01: missing before_sha256 key authorizes recreating a missing
      member'
    why: 'Measured: a removed ledger was recreated and the journal deleted; this contradicts
      _read_journal''s UNREADABLE contract'
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer, harness-security-reviewer
    summary: 'MF-5 T-02: amend --show performs recovery and writes both files'
    why: 'Reconciled to med below code''s high: it reaches the correct roll-forward
      state, so nothing is corrupted; still breaks the CLI''s read-only promise and
      D-02''s limit to mutating verbs'
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer, harness-goalcheck
    summary: 'MF-6 T-02: SC-05 successors do not assert the named failure or raw-byte
      identity'
    why: 'Reconciled to med above pm''s low: both literal SC-05 terms are unmet and
      no signed ruling narrows them'
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-01: replay after a failed initial directory fsync never fsyncs the
      journal directory'
    why: Not covered by Q2(c); the remedy is a C5 journal surface; non-gating -> OQ-2
  - kind: substance
    scope: none
    severity: low
    reader: harness-security-reviewer
    summary: 'T-01: refusal diagnostics echo raw journal field contents unbounded'
    why: Advisory; bound repr while MF-2/MF-4 are open
  - kind: form
    scope: none
    severity: low
    reader: harness-goalcheck
    summary: 'T-02: SC-01 ''names the journal'' and the ''further invocation changes
      neither file'' clauses have no suite assertion'
    why: Behavior confirmed by probes; guard it against regression in the MF-6 round
  readers:
  - reader: qa
    status: ran
    persona: harness-qa
    reason: none
  - reader: code
    status: ran
    persona: harness-code-reviewer
    reason: none
  - reader: security
    status: ran
    persona: harness-security-reviewer
    reason: none
  - reader: ui
    status: ran
    persona: harness-ui-reviewer
    reason: none
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/r-20261124-2-validate-validator/digest.md
```
