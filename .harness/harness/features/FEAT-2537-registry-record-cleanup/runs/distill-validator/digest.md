# FEAT-2537 distill — validator squad (run distill-validator) — PASS

**BLUF:** Distillation is complete, and no refusal is left. Members applied 5 ops in total. QA made 2 craft replaces and 1 repo replace, code-reviewer 1 craft replace, and security-reviewer 1 craft replace. UI judged and declined with a reason. I applied 3 craft replaces of my own. Every section is still at the same count it started with, so no cap was exceeded. This run reviewed no diff, ran no suite and committed nothing.

## Members (all ran in one turn; I checked each receipt against the resulting file)

| Step | Verdict | Accepted / declined | Batch · receipt | Counts before→after |
|---|---|---|---|---|
| distill-qa | PASS | **C-QA1 accepted** (the raw-bytes letter gap): craft O-04 replaced. **C-QA2 accepted** (a delta QA classified in-class itself): craft O-08 replaced. From its own log, it added the INV-26 live-board gotcha by replacing repo G-11. It rejected 5 other log bullets as already covered. | craft `3d2ce5f1…`, repo `e5afc9a5…` · `notes/expertise-receipt-b43237d2….json` | craft P15→15 G15→15 O10→10 Open0→0; repo G15→15 |
| distill-code | PASS | **C-CR1 accepted** (map each closure counterexample to its governing clause): O-08 replaced. C-CR2 declined as covered by P-08/O-04/P-03. C-CR3 declined because the ruling interpreted the scope and did not create a blanket exemption, which leaves P-16 standing. | `658ff3df…` · `notes/expertise-receipt-e944f97e….json` | P15→15 G15→15 O10→10 Open0→0 |
| distill-security | PASS | **C-SEC2 accepted** (fail-closed must not remove the last repair route): G-05 replaced. C-SEC1 declined as an application of P-09 and P-12. | `48f451ad…` · `notes/expertise-receipt-d44ec07c….json` | P15→15 G15→15 O10→10 Open0→0 |
| distill-ui | PASS | No candidates were relayed. It judged and declined, because its measured scope-out is already covered by P-01, O-01 and O-05. | none | unchanged |

I did not dispatch pm. The product squad already distilled its goalcheck lesson into pm craft P-11 (`runs/distill-product/digest.md`), and that lesson is not validator-specific.

## Lead's own (craft, batch `7db13f2c…`, receipt `notes/expertise-receipt-4690f7e8….json`)
- **P-07 replaced:** hand a signoff's characterization of a delta to a reader as a falsifiable claim, to be checked with a base-vs-pin probe on data-carrying instances. The row erasure surfaced only because readers ran that probe; no criterion witnessed it.
- **P-12 sharpened:** a must-fix also hands down the representation the clause names, and a mutant per representation. My r-2 must_fix said "exact bytes" without naming a mutant, the fix delivered a text-mode read, and closing that gap cost a completion round.
- **G-10 sharpened:** when a letter gap is cheap and inside a task's files, recommend the letter fix rather than an intent-met reading. The c1 ruling rejected my intent-met recommendation on exactly this ground.
- Counts: P15→15 G15→15 O10→10 Open0→0. I had no repository-tier lesson; the INV-26 fact belongs to QA's repo tier.

## Reservations (left standing; members are sole judges)
- Code-reviewer's O-08 replacement removes the rule about the direction of a divergence (stricter code amends the text; weaker code gets fixed). Nothing else in its file carries that rule.
- QA's O-04 replacement keeps "route text-unmet upward" but drops the explicit "two distinct findings" wording. My G-10 still holds that rule at lead level.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/runs/distill-validator/digest.md
DIGEST:
  headline: FEAT-2537 validator distill is complete with no refusal left. qa accepted
    both relayed candidates and added a repo INV-26 gotcha; code-reviewer and security
    each accepted one candidate; ui judged and declined. The lead added a base-vs-pin
    characterization probe rule and sharpened P-12 and G-10. All sections are within
    cap.
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/expertise/harness-qa.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/expertise/harness-qa.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/expertise/harness-code-reviewer.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/expertise/harness-security-reviewer.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/expertise/harness-validator-lead.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/notes/qa-distill-validator.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/notes/review-harness-code-reviewer-distill.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/notes/review-harness-security-reviewer-distill.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/notes/review-harness-ui-reviewer-distill.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/runs/distill-validator/state.yaml
  expertise_update:
  - persona: harness-qa
    op: replace
    target: O-04
    section: Outcomes
    entry: "WHEN a criterion's literal wording is stricter than what its assertion\
      \ can see ('raw bytes' against a decoded or newline-normalized read) DO grade\
      \ the gap against the letter, not present equivalence; run the mutant it admits\
      \ and route text-unmet upward \u2014 today's equivalence is not what the test\
      \ pins."
    why: 'Sharper successor to O-04: I followed its route-up step yet rated a raw-bytes
      letter miss low on measured present equivalence; the ruler judged it the one
      real clause miss (CRLF writer passed every row) and it cost a completion round.'
  - persona: harness-qa
    op: replace
    target: O-08
    section: Outcomes
    entry: "WHEN a behaviour-delta probe finds a delta the signed decision covers\
      \ literally but the signoff or plan characterizes otherwise DO report it as\
      \ a finding for the ruler, naming the characterization it falsifies \u2014 classifying\
      \ it in-class yourself pre-empts the stop-and-rule clause that falsified characterization\
      \ triggers."
    why: I recorded a row-erasing fold as in-class; two reviewers escalated it and
      the ruler confirmed the signoff's 'bytes identical' was false, so the stop clause
      had fired. O-08 (mutate the real call site, not a passthrough accessor) is largely
      subsumed by O-06/O-10 and is the weakest Outcome.
  - persona: harness-qa
    op: replace
    target: G-11
    section: Gotchas
    entry: "WHEN check-state exits 1 on INV-26 at a review pin DO rerun it at the\
      \ feature tip before reporting a defect \u2014 INV-26 reads the live GitHub\
      \ board, so a pin predating a station-move commit shows a false projection mismatch."
    why: 'Measured this feature: INV-26 exited 1 at the pin and 0 at the tip, which
      differed only in feature-dir station records; recurs on every validate at a
      pin. G-11 (preserve output on discovery-count divergence) is generic hygiene
      and the weakest repo gotcha.'
  - persona: harness-code-reviewer
    op: replace
    target: O-08
    section: Outcomes
    entry: "WHEN grading a must-fix closure DO map each counterexample to the exact\
      \ criterion or ruling clause before rating the remaining gaps by consequence\
      \ \u2014 a prescribed representation is compliant if it proves the required\
      \ behavior, and witness hygiene beyond the governing requirements is advisory."
    why: The re-validation ruling separated one required byte-comparison gap from
      two advisory witness concerns. This changes future closure reviews more reliably
      than assuming stricter code should drive a specification amendment.
  - persona: harness-security-reviewer
    op: replace
    target: G-05
    section: Gotchas
    entry: "WHEN proposing fail-closed handling for damaged state DO check which supported\
      \ repair operations still work on that same state and weigh losing the last\
      \ repair route against the evidence recovery would discard \u2014 a safe refusal\
      \ can leave operators with only more destructive manual repair."
    why: G-15 protects evidence and P-11 traces enforcement consumers; neither tests
      repair availability. This is more actionable than G-05's fix-cost heuristic,
      which can cut reachability analysis short.
  - persona: harness-validator-lead
    op: replace
    target: P-07
    section: Patterns
    entry: "WHEN a signoff or plan characterizes a behaviour delta DO hand that characterization\
      \ to a panel reader as a falsifiable claim to probe base-vs-pin on data-carrying\
      \ instances \u2014 criteria witness only enumerated examples, so a false characterization\
      \ surfaces only if someone runs that probe."
    why: A signoff's 'bytes identical' account, generalized from a rowless example,
      was falsified only because readers spontaneously probed base vs pin with row-carrying
      shapes; no SC witnessed it and the c0 ruling's Gap names the missing witness.
      Displaces P-07, which the code-reviewer's own selection-rule gotcha already
      holds at reader level.
  - persona: harness-validator-lead
    op: replace
    target: P-12
    section: Patterns
    entry: "WHEN ruling a must-fix against a defect class DO hand down every state\
      \ the decision consumes and the representation the clause names, requiring a\
      \ discriminating mutant per state and per representation (a newline-normalizing\
      \ writer for bytes) \u2014 instance-scoped or normalized remedies close one\
      \ member per round, and rounds are budgeted."
    why: My must_fix said 'assert exact file bytes' without naming the mutant; the
      fix delivered a text-mode read a CRLF writer passed, and the c1 ruling had to
      grant a completion round. Sharpens P-12 to cover the representation axis; same
      length.
  - persona: harness-validator-lead
    op: replace
    target: G-10
    section: Gotchas
    entry: "WHEN a member reports a signed criterion met under a narrowed reading\
      \ DO record literal status and reading as two findings, route the reading up,\
      \ and recommend the letter fix when cheap and inside a task's files \u2014 a\
      \ ruler can prefer a small fix to a permanently contested criterion."
    why: I recommended accepting an intent-met reading of a bytes clause; the c1 ruling
      chose the ~10-line fix instead, reasoning an interpretive override leaves a
      contested record auditors read literally. Sharpens G-10 with which option to
      recommend.
  team: distill (validator squad)
  steps_run: 4
  cycles_used: 0
  members:
  - step: distill-qa
    persona: harness-qa
    verdict: PASS
    headline: "Accepted C-QA1 and C-QA2 (craft O-04 and O-08 replaced) and replaced\
      \ repo G-11 with the INV-26 gotcha. Rejected 5 log bullets as already covered.\
      \ Craft P15\u219215 G15\u219215 O10\u219210 Open0\u21920; repo G15\u219215."
    files_touched:
    - .harness/expertise/harness-qa.md
    - .harness/harness/expertise/harness-qa.md
  - step: distill-code
    persona: harness-code-reviewer
    verdict: PASS
    headline: "Accepted C-CR1 (O-08 replaced) and declined C-CR2 and C-CR3 with reasons.\
      \ P15\u219215 G15\u219215 O10\u219210 Open0\u21920."
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/expertise/harness-code-reviewer.md
  - step: distill-security
    persona: harness-security-reviewer
    verdict: PASS
    headline: "Accepted C-SEC2 (G-05 replaced) and declined C-SEC1 as covered by P-09\
      \ and P-12. P15\u219215 G15\u219215 O10\u219210 Open0\u21920."
    files_touched:
    - .harness/expertise/harness-security-reviewer.md
  - step: distill-ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: 'Judged and declined: the measured scope-out is already covered by its
      Expertise. No ops; counts unchanged.'
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'Distill dispatch: no diff was reviewed, no suite was run and nothing was committed.'
  - "I checked every member op against its receipt and the resulting file: qa b43237d2\u2026\
    json (batches 3d2ce5f1\u2026 and e5afc9a5\u2026), code e944f97e\u2026json (658ff3df\u2026\
    ), security d44ec07c\u2026json (48f451ad\u2026). The lead's own batch is 7db13f2c\u2026\
    , recorded in receipt 4690f7e8\u2026json."
  - pm was not re-dispatched. The product squad already distilled its goalcheck lesson
    (pm craft P-11, runs/distill-product), and that lesson is not validator-specific.
  - 'Reservation: code-reviewer''s O-08 replacement removes its rule on the direction
    of a divergence (stricter code amends the text; weaker code gets fixed). Left
    standing because the member is sole judge.'
  - 'Reservation: qa''s O-04 replacement drops the explicit ''two distinct findings''
    wording. Lead G-10 still holds that rule.'
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
  readers: []
```
