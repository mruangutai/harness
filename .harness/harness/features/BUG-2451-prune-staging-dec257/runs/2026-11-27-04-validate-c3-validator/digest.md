# BUG-2451 · validate c3 — FAIL (one med must-fix, MF-3R; MF-2R's four acceptance lines met on their ordinary probes; A-3 resolved)

**Reviewed SHA:** a97dbc6a8337cfbe9402d2a727aa28797a1efaf8 (feature.json pin), worktree copy. Code-reviewer measured `b7e1f26e..c9596b9a` as product path `tests/unit/test-prune-run-evidence.py` only. Merge 6e8c8c58 resolved only the index conflict, and the feature's diff against origin/main is still T-01's five files. cycles_used 0. severity_max **med**.

**BLUF.** The c2 fix works on every probe the ruling named:
- **L1:** a capitalised claim reds the check, including one wrapped across a line break.
- **L2:** a changed DEC-257 claim reds the check.
- **L3:** the current five files are green.
- **L4 / A-3:** an unrelated `git add` in DEC-100 stays green.

Each line was measured by mutation, and on each the b7e1f26e test behaves the opposite way. Both perspectives, SC-01..SC-04, the DEC-238 amend and all five keep rows are met.

The verdict is still FAIL on one NEW defect the fix introduced, **MF-3R**. `section()` returns `''` when its literal `"## DEC-257 "` / `"## DEC-238 "` anchor is absent, and an empty scan counts as clean. A heading the index generator still accepts (`HEADING_RE = ^##\s+(DEC-(\d+))\b`, gen-decisions-index.py:28) therefore empties the scan without any signal. An example is two spaces after `##`. With such a heading, a forbidden claim added inside DEC-257 passes both the five-file check and the signed verify's index diff, so ruling L2 fails for that representation. The shipped text is correct today. In this repo the review gate is `advisory_unless_high`, and no rework is authorised, so the operator decides (OQ-B).

## Per-reader verdicts

| Step | Persona | Verdict | Note |
|---|---|---|---|
| qa | harness-qa | PASS | `notes/review-harness-qa-c3.md`; unit 68/68, receipt `qa/manifest-unit.json`; verify exit 0; prune test 52/0; L1 red, L4 green |
| code | harness-code-reviewer | FAIL | `notes/review-harness-code-reviewer-c3.md`; L1–L4 met on ordinary probes, A-3 resolved; MF-3R med |
| security | harness-security-reviewer | PASS | `notes/review-harness-security-reviewer-c3.md`; pruner and ship caller byte-unchanged since c2; no new surface |
| ui | harness-ui-reviewer | PASS (scoped out) | `notes/review-harness-ui-reviewer-c3.md`; measured census of both diff ranges, no rendered UI |
| goalcheck | harness-pm | PASS | `notes/research-BUG-2451-prune-staging-dec257-goalcheck-validate-c3.md`; all SCs, perspectives and dispositions met |

## MF-2R disposition — per acceptance line

Measurements are against the pin's test, with the b7e1f26e test as the control.

| Line | Disposition | Measured by |
|---|---|---|
| L1 capitalised claim fails | **met.** `Force-stage retained records.`, including the variant wrapped across a line break, goes RED in the ship intro and in the pruner docstring. The old test is GREEN on the same mutants. | code, qa |
| L2 changed DEC-257 claim fails | **met on ordinary headings.** `no`→`No` and an added broad-ignore claim both go RED, and the old test is GREEN. **Residual:** a heading-whitespace variant goes GREEN (MF-3R). | code |
| L3 no false failure | **met.** The unmutated files give exit 0 and 52 PASS / 0 FAIL (qa, pm, code). The verify prints 55 PASS lines because three are reprinted. | qa, code, pm |
| L4 / A-3 unrelated `git add` | **met; A-3 resolved.** A `git add` or broad-ignore phrase planted in DEC-100 stays GREEN, and the old test goes RED. | code, qa, pm |

The red-first `## c2 fix` claims reproduced, including the hashes, the c1 probes still being red and the corrected 52 (code). One exception: the census at `notes/red-first-T-01.md:174` says only `FORBIDDEN` holds denylisted text, but the `DEC_257` literal does too. That is form/low.

## Must-fix (one, against T-01)

1. **MF-3R · substance · med (code-reviewer; the lead confirmed it at source, test:623–627 and test:653–657 against gen-decisions-index.py:28).** It violates ruling L2 and T-01 intent, which says verification must reject forbidden positive claims in changed current text.
   - **Failure scenario:** edit DEC-257's heading to `##  DEC-257 —` (or to any form the generator accepts that lacks the literal `## DEC-257 `), then add `force-stage` text inside the section. The unit test gives 52/0 and the index regenerates equal. The same applies to DEC-238: the bullet check is a global text search, so a claim elsewhere in DEC-238 escapes.
   - **Direction:** fail-open. A missing anchor reads as a clean section.
   - **Remedy (test-only, inside T-01's files):** treat a missing section as a failure, or locate sections with the generator's own heading pattern. The DEC-257 spacing-plus-claim mutant must go red while the DEC-100 probe stays green.
   - No rework is authorised, so this goes to the operator (OQ-B), not to a fix run.

## New at c3 — advisory, not gating (ranked by irreversibility, then severity)

1. **Code, substance, folded into scope:** a ship-pruner claim placed inside another decision goes GREEN, as does one in that decision's hand-written index ruling. The measured case is DEC-250. This is the scope trade the operator ordered in L4 ("unrelated … elsewhere"). A keyword scan cannot tell related prose from unrelated prose, so the lead dismisses it as a gate. It is recorded so the operator sees what L4 bought.
2. **Code, substance, low:** co-editing DEC-257 and the `DEC_257` constant keeps a claim GREEN. This needs an edit to DEC-257 itself, which is out of T-01's authorised patch. It is not a separate gate.
3. **Code, substance, low, inherited:** `Force-` + newline + `stage` is a split-token miss, and it is GREEN on both the old and the new test.
4. **Code, informational:** a CRLF-only rewrite of DEC-257 goes GREEN with no new claim, because `read_text` normalises newlines. This is not a defect.
5. **Code, form, low:** the red-first census omits the `DEC_257` literal.

## Carried operator-kept rows — still true at the pin (pruner unchanged since c2)

- **A-1:** a listable but non-searchable recorded `ui/` leaf can be partially pruned (code).
- **A-2:** an unreadable `ui/` in an unrecorded run is not pre-walked (code).
- **SEC:** unreadable `ui/` directory names reach stderr unescaped (prune-run-evidence.py:179–180, 212–215). It still refuses before mutation (security).

Struck rows (C2-F1, C2-F2, QA-F2, OQ-1, OQ-2) were not re-raised.

## Open question

- **OQ-B (lead, blocking):** MF-3R is med, test-only and inside T-01's files, and no rework is authorised. The options are:
  - (a) accept it as a recorded residual, backlog it, and ship (review gate `advisory_unless_high`; the shipped text is correct);
  - (b) grant one more test-only round, with acceptance that the DEC-257 heading-spacing-plus-claim mutant goes red, an absent DEC-238/DEC-257 section fails the check, and L1–L4 still hold.

```yaml
VERDICT: FAIL
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257/.harness/harness/features/BUG-2451-prune-staging-dec257/runs/2026-11-27-04-validate-c3-validator/digest.md
DIGEST:
  headline: 'BUG-2451 at a97dbc6a fails on one new med must-fix, MF-3R. MF-2R''s four
    acceptance lines are met on their ordinary probes, A-3 is resolved, and every
    SC, both perspectives and all dispositions are met. MF-3R: a DEC-238/DEC-257 heading
    the index generator accepts (e.g. ''##  DEC-257'') empties the claim scan, so
    a changed DEC-257 claim stays green (fail-open against ruling L2). No rework is
    authorised, so the operator decides (OQ-B); the review gate is advisory_unless_high.'
  team: validate
  steps_run: 5
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: 'Unit 68/68 at the pin with receipt qa/manifest-unit.json, and T-01
      verify exits 0. The prune test gives 52/0. Fail-first still holds: SC-01 is
      red on 47d6c54d (40/12) and SC-02 on b2c1f55e (48/4). L1 measured red, and L4/A-3
      green.'
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257/.harness/harness/features/BUG-2451-prune-staging-dec257/runs/2026-11-27-04-validate-c3-validator/qa/manifest-unit.json
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257/.harness/harness/features/BUG-2451-prune-staging-dec257/observations/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: FAIL
    headline: A-3 is resolved, but a valid heading-spacing change lets a new DEC-257
      claim pass both the five-file check and the index diff.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: No new security surface at a97dbc6a. The pruner and ship caller are
      byte-unchanged since c2, and SEC stays backlog-only.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Mode B scoped out after a measured census of both diff ranges: no rendered
      or interactive UI.'
    files_touched: []
  - step: goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Both perspectives are discharged and SC-01..SC-04 are met. The DEC-238
      amend and all five keep rows are met, and the merge left T-01's surfaces intact.
      A-3 is resolved by measurement.
    files_touched: []
  must_fix:
  - 'MF-3R (T-01, substance, med per harness-code-reviewer; violates operator ruling
    L2 ''a changed DEC-257 claim fails the check'' and T-01 intent ''verification
    must reject forbidden positive claims in changed current text''). In tests/unit/test-prune-run-evidence.py,
    section() (test:623-627) returns '''' when the literal ''## DEC-257 '' or ''##
    DEC-238 '' anchor is absent, and current_texts() (test:653-657) scans that ''''
    as clean. The index generator still accepts such a heading (HEADING_RE ''^##\s+(DEC-(\d+))\b'',
    gen-decisions-index.py:28). Failure scenario: change DEC-257''s heading to ''##  DEC-257
    ...'' and add a force-staging claim in the section; the unit test gives 52/0 and
    the index diff matches, while the b7e1f26e test goes RED. The same applies to
    a claim in DEC-238 outside the ship bullet. This is fail-open; the lead confirmed
    it at source. Test-only remedy inside T-01''s files: fail on a missing section,
    or locate sections with the generator''s heading pattern; the spacing-plus-claim
    mutant must go red while the DEC-100 probe stays green. No rework is authorised,
    so it goes to the operator (OQ-B), not to a fix run.'
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257/.harness/harness/features/BUG-2451-prune-staging-dec257/runs/2026-11-27-04-validate-c3-validator/qa/manifest-unit.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257/.harness/harness/features/BUG-2451-prune-staging-dec257/observations/harness-qa.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2451-prune-staging-dec257/.harness/harness/features/BUG-2451-prune-staging-dec257/runs/2026-11-27-04-validate-c3-validator/state.yaml
  branch: none
  open_questions:
  - id: OQ-B
    question: '(lead) MF-3R is a new c3 defect: med, test-only and inside T-01''s
      files. A heading the generator accepts, such as ''##  DEC-257'', empties the
      DEC-238/DEC-257 claim scan, so a changed DEC-257 claim stays green. That breaks
      ruling L2 for this representation. No rework is authorised. Option (a): accept
      it as a recorded residual, backlog it and ship; the review gate is advisory_unless_high
      and the shipped text is correct. Option (b): grant one more test-only round,
      with acceptance that the spacing-plus-claim mutant goes red, an absent DEC-238/DEC-257
      section fails the check, and L1-L4 still hold. Which does the operator choose?'
    blocking: true
  escalations: []
  expertise_update: []
  adequacy_notes:
  - 'Reviewed SHA: a97dbc6a8337cfbe9402d2a727aa28797a1efaf8, worktree copy. Code-reviewer
    measured b7e1f26e..c9596b9a: among product paths, only tests/unit/test-prune-run-evidence.py
    changed. Merge 6e8c8c58 resolved only the DECISIONS-INDEX.md conflict. Against
    origin/main, the five paths keep the same feature content as c2 (code, pm, security).'
  - 'MF-2R L1 met: ''Force-stage retained records.'', including the variant wrapped
    across a line break, goes RED in the ship intro and in the pruner docstring. The
    b7e1f26e test is GREEN on the same mutants (code; qa also measured the ship-intro
    case).'
  - 'MF-2R L2 met for ordinary headings: a DEC-257 ''no''->''No'' edit and an added
    broad-ignore claim each go RED, and the old test is GREEN (code). The residual
    is MF-3R (heading-whitespace variant).'
  - 'MF-2R L3 met: the unmutated pin gives exit 0 and 52 PASS / 0 FAIL, measured independently
    by qa, pm and code. T-01 verify exits 0; it prints 55 PASS lines because three
    of the 52 are reprinted, so the red-first note''s corrected 52 is right.'
  - 'MF-2R L4 met and A-3 resolved: a ''git add'' or broad-ignore phrase planted in
    DEC-100 stays GREEN on the new test and goes RED on the old one (code, qa, pm).'
  - 'Dismissed as a gate by the lead: a ship-pruner claim inside DEC-250, or in its
    hand-written index ruling, goes GREEN (code measured one site). This is the scope
    trade the operator ordered in L4: a keyword scan cannot tell ''unrelated'' prose
    from related prose. It is recorded so the operator sees what L4 bought.'
  - 'Red-first ''## c2 fix'' claims reproduced (code). One exception: the census at
    notes/red-first-T-01.md:174 omits that the DEC_257 literal also holds denylisted
    text (form, low).'
  - 'Operator-kept rows still true at the pin, because the pruner is unchanged since
    c2: A-1 (listable but non-searchable ui/ leaf gives a partial prune), A-2 (unrecorded
    run''s ui/ is not pre-walked) and SEC (ui/ directory names reach stderr unescaped,
    prune-run-evidence.py:179-180,212-215). Struck rows were not re-raised.'
  - 'ui-reviewer ran and scoped out after a measured census: there is no user-facing
    surface.'
  - QA receipts come from this host's interpreter, not CI. The SC-02 exit-2 legs have
    no natural RED and rest on the c1/c2 mutation evidence; the c3 delta touches neither
    those legs nor the pruner.
  - 'Gate: FAIL because must_fix is non-empty (lead rule). In this repo, harness.json
    gates.review is advisory_unless_high, so a med-only must_fix does not by itself
    block ship at the review gate. Every SC and both perspectives are met; the FAIL
    rests on the ruling''s L2 acceptance and T-01''s verification intent, not on shipped
    behaviour.'
  - T-01 is main-session-direct (DEC-174, DEC-179). Nothing was sent back from this
    run.
  sc_status:
  - id: PERSPECTIVE-operator
    verdict: met
    method: inspection
    evidence: SC-02 and SC-03 are met. The restored DEC-238 bullet and the ship paragraph
      equal their 5e51124e text plus the one refusal sentence, and that sentence is
      true of the unchanged pruner (pm, code).
  - id: PERSPECTIVE-code-maintainer
    verdict: met
    method: automated
    evidence: 'SC-01 and SC-04 are met. The test is red on 47d6c54d (40/12) and b2c1f55e
      (48/4) and green at the pin (52/0) (qa, pm, code). Qualification: MF-3R, the
      forbidden-claim guard fails open on a heading-whitespace variant.'
  - id: SC-01
    verdict: met
    method: automated
    evidence: 'qa ran the pin''s test with PRUNE_RUN_EVIDENCE_BIN set to the 47d6c54d
      bin tree (sha256 55df0581...): exit 1, 40 PASS / 12 FAIL by assertion. The failures
      include ''pruner invokes no git subprocess'' and the index byte-identity checks.
      Green at the pin; receipt runs/2026-11-27-04-validate-c3-validator/qa/manifest-unit.json.'
  - id: SC-02
    verdict: met
    method: automated
    evidence: 'With the b2c1f55e bin tree (sha256 0237578f...), all four unreadable_ui_cases
      legs fail by assertion: exit 1, 48/4 (qa). The pruner and refusal tests have
      0 diff lines from b7e1f26e to the pin (pm, security).'
  - id: SC-03
    verdict: met
    method: inspection
    evidence: DECISIONS.md:8137 and harness-ship.md:47 each equal the 5e51124e text
      plus exactly one refusal sentence, and the index regenerates byte-identically
      (pm, code). The guard residual is tracked separately as MF-3R.
  - id: SC-04
    verdict: met
    method: inspection
    evidence: harness-ship.md is byte-identical to b7e1f26e, so the step position,
      both invocations and the commit name are unchanged. The pruner is unchanged
      since c2, so the CLI, keep, UI-only and symlink behaviour is unchanged (pm,
      code).
  - id: DEC-238
    verdict: met
    method: inspection
    evidence: The amend matches D-01. The bullet at DECISIONS.md:8137 equals 5e51124e
      plus one sentence, and it is the feature's only DECISIONS.md hunk against origin/main.
      The index row regenerates. Owner T-01 (pm).
  - id: DEC-174
    verdict: met
    method: inspection
    evidence: 'keep: the section at DECISIONS.md:4521 is byte-equal to origin/main
      (pm).'
  - id: DEC-179
    verdict: met
    method: inspection
    evidence: 'keep: the section at DECISIONS.md:4851 is byte-equal to origin/main
      (pm).'
  - id: DEC-225
    verdict: met
    method: inspection
    evidence: 'keep: the section at DECISIONS.md:7496 is byte-equal to origin/main
      (pm).'
  - id: DEC-254
    verdict: met
    method: inspection
    evidence: 'keep: the section at DECISIONS.md:8408 is byte-equal to origin/main
      (pm).'
  - id: DEC-257
    verdict: met
    method: inspection
    evidence: 'keep: the section at DECISIONS.md:8651 is byte-equal to origin/main
      and to b7e1f26e, and it equals the test''s DEC_257 constant (pm, code).'
  needs_approval: true
  severity_max: med
  matrix_ok: true
  coverage_gaps:
  - 'MF-3R: the DEC-238/DEC-257 claim scan is silently empty when its literal heading
    anchor is absent. A heading-whitespace mutant plus a claim stays green.'
  - A ship-pruner claim placed in another decision (DEC-250 measured), or in its index
    ruling, is not scanned. This is by the operator's L4 scope.
  - '''Force-'' + newline + ''stage'' split-token is not matched (inherited; green
    on both the old and the new test).'
  - The SC-02 exit-2 legs have no natural RED; they rest on c1/c2 mutation evidence
    (qa).
  findings:
  - kind: substance
    scope: none
    severity: med
    reader: harness-code-reviewer
    summary: 'T-01 / ruling L1-L2 (MF-3R): the narrowed decision scan fails open on
      valid headings.'
    why: With a second space after '##' in DEC-238 or DEC-257 and a forbidden claim
      in that same section, the unit test reports 52 PASS / 0 FAIL and index regeneration
      matches. The old test goes RED. The generator accepts the whitespace, but the
      literal lookup silently returns empty (tests/unit/test-prune-run-evidence.py:653-657,693-701).
      Gating; the lead confirmed it at source.
  - kind: form
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: T-01 red-first census omits the DEC_257 literal; non-gating.
    why: The raw test source contains denylisted text in both assignments, not just
      FORBIDDEN as stated at notes/red-first-T-01.md:174. The filtered text has no
      hits, and the recorded runs and counts reproduced.
  - kind: substance
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: 'T-01: a ship-pruner claim inside another decision (DEC-250) or its index
      ruling goes green; assessed and dismissed as a gate by the lead.'
    why: This is the consequence of the operator's L4 scoping ('unrelated ... elsewhere
      in DECISIONS.md'). A keyword scan cannot separate related prose from unrelated
      prose. Recorded, not gating.
  - kind: substance
    scope: none
    severity: low
    reader: harness-code-reviewer
    summary: 'T-01: co-editing DEC-257 and the DEC_257 constant keeps a claim green;
      split-token ''Force-''/newline/''stage'' is missed (inherited).'
    why: The first case requires editing DEC-257 itself, which is outside T-01's authorised
      patch. The second is green on both the old and the new test. Neither gates.
  - kind: substance
    scope: none
    severity: low
    reader: harness-security-reviewer
    summary: SEC still true at the pin (operator-kept backlog; non-gating).
    why: A local writer controlling the name of an unreadable directory in a recorded
      ui/ tree can embed a newline to spoof a status line on stderr. The unchanged
      pruner still exits 1 before mutation (prune-run-evidence.py:179-180,212-215).
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
```
