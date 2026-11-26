# FEAT-2542 distill — validator squad (run distill-validator)

**BLUF: PASS.** All three dispatched members accepted their relayed candidate. qa, security-reviewer and ui-reviewer applied 7 ops between them, and the lead applied 1. Each op shows up in its receipt and in the resulting file (I grepped the entry id and its distinctive text). Every section stays at its cap. pm and code-reviewer lessons were not repeated, because the product squad already distilled them.

## distill-qa (harness-qa): PASS
Artifact: `notes/qa-distill.md`. Receipt: `notes/expertise-receipt-001cffbe….json`, which records craft batch `fc3ec8ab…` and repository batch `3cad7c79…`.
- **Craft G-05 replaced (QA1, relayed from ui-reviewer):** consume operator-facing prose and printed commands the way the operator would. That means shell-splitting each command and running it verbatim with a fixture root that contains spaces. Substring and sweep gates only prove that text is present. The new entry also covers the prose-truth gotcha that G-05 held before.
- **Craft P-06 replaced:** each leg of a rule, and each ordering, needs a row that discriminates it. This comes from mutants g and n3 and from the n5 isinstance leg.
- **Craft P-07 replaced:** fixtures that copy the subject under test re-read it from disk, so a partial base swap still runs new code. This is why QA counted 110 base-red checks where the author counted 89.
- **Repository G-13 replaced:** bash-write-guard refuses `git checkout` even inside a /tmp clone, so QA used `git archive | tar -x` instead.
- Counts are unchanged and full: craft P 15, G 15, O 10; repository G 15.

## distill-security-reviewer (harness-security-reviewer): PASS
Artifact: `notes/review-harness-security-reviewer-distill.md`. Receipt: `notes/expertise-receipt-9bacb180….json`, batch `92ec21b5…`.
- **Craft P-14 replaced (S1, relayed from the lead and the ruler):** when a fail-open needs damaged state that the contract explicitly covers, do not lower the severity just because the state is abnormal. Report reachability separately. The new entry displaces a narrower heuristic about naming filesystem recovery files.
- Two candidates were declined, each with a reason:
  - The newline line-forging lesson is already covered by G-07.
  - The producer probe on temporary data is already covered by O-02 and O-04, and producer normalization was retained by the product squad.
- Counts are unchanged: craft P 15, G 15, O 10. No repository-tier ops.

## distill-ui-reviewer (harness-ui-reviewer): PASS
Artifact: `notes/review-harness-ui-reviewer-distill.md`. Receipt: `notes/expertise-receipt-fbf6bd30….json`, batch `c7e91a51…`.
- **Craft G-11 replaced (U1, relayed from security):** test the literal physical line a reader would copy, with a newline embedded in a dynamic value. The displaced generated-HTML heuristic survives in repository P-02.
- **Craft P-03 replaced:** copy-run each remedy command against a disposable target with a matching decoy at the default destination. A misrouted command can still exit successfully, so the exit status alone does not show which target it hit.
- Declined: an entry about signed wording, because G-08 already governs that case.
- Counts are unchanged: craft P 15, G 15, O 10.

## Lead's own lesson
Craft **P-12 replaced**, batch `d505408b…`, receipt `notes/expertise-receipt-b72364fe….json`. The new entry is about specifying a must-fix: hand down every state, predicate leg and representation; read how the producer normalizes each shape first; and require one discriminating mutant per leg.

Two things in this feature led to it:
- My c1 must_fix prescribed refusing both null and omitted features. The ruler corrected this: the producer turns an omitted feature into `legacy`, which must pass.
- The ruled check had three legs but fixtures for only two. The mutant for the third leg (n5) survived and fails open.

Counts are unchanged: P 15, G 15, O 10, Open 0. Considered and not written:
- An outcome confirming P-04, where the ruler upheld my non-gating rating on OQ-3. Outcomes is full, and no current entry is weaker.
- "Executed measurement beats reasoned trace." This was pm's lesson, already distilled as pm O-12.

## Not dispatched
- **pm and code-reviewer:** distilled by the product squad.
- **No other validator member ran on this feature.**

Send-back criteria (`sendback-criteria.md`, written before dispatch) are all met. There were no send-backs.

Note: QA's digest did not list its receipt or artifact in `files_touched`. They are listed in the team union below.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/runs/distill-validator/digest.md
DIGEST:
  headline: 'FEAT-2542 validator distill is complete. qa, security-reviewer and ui-reviewer
    each accepted their relayed candidate: copy-run printed commands, use a decoy
    target with a newline in a value, and do not discount a fail-open because its
    damaged-state precondition is one the contract covers. Members applied 7 ops and
    the lead replaced P-12. Every write is receipted, verified in its file, and within
    cap.'
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/expertise/harness-qa.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/expertise/harness-qa.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/expertise/harness-security-reviewer.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/expertise/harness-ui-reviewer.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/expertise/harness-validator-lead.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/notes/qa-distill.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/notes/review-harness-security-reviewer-distill.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/notes/review-harness-ui-reviewer-distill.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/runs/distill-validator/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/runs/distill-validator/sendback-criteria.md
  expertise_update:
  - persona: harness-qa
    op: replace
    target: G-05
    section: Gotchas
    entry: "WHEN output is operator-facing prose or a printed command DO consume it\
      \ as the operator would \u2014 read prose for truth; shell-split each printed\
      \ command with a spaced fixture root, run it verbatim, and assert it reaches\
      \ the intended target. Substring and sweep gates prove presence, never truth\
      \ or runnability."
    why: 'Relayed QA1 accepted: my green c1 suite asserted printed-command substrings
      while every command was unrunnable (glued punctuation, unquoted root, bare script);
      only verbatim copy-running caught it. Merged with G-05''s prose-truth rule,
      same root: token gates cannot prove what the text does.'
  - persona: harness-qa
    op: replace
    target: P-06
    section: Patterns
    entry: "WHEN a rule has several legs or orders its checks DO give each leg its\
      \ own discriminating row, and each ordering a row where both checks fire asserting\
      \ which cause wins \u2014 a memoized, lazily re-invoked check, or inputs tripping\
      \ one check, leave narrowing and reorder mutants green."
    why: Two ordering mutants survived across cycles (placement after preflight hidden
      by a lazily re-invoked memoized check; feature check after persona check) plus
      a dropped isinstance leg; P-06 covered legs but not order.
  - persona: harness-qa
    op: replace
    target: P-07
    section: Patterns
    entry: "WHEN fail-first needs a pre-fix red and source edits are refused DO load\
      \ the old blob into a fresh in-process module, or run the new tests in a whole\
      \ old-SHA tree \u2014 subprocess cases and fixtures copying the subject re-read\
      \ disk, so partial swaps run new code."
    why: 'My whole-tree base reproduction found 110 reds against the author''s 89:
      fixtures copying bin/ still ran the live guard. Sharpens P-07''s why to cover
      fixture copies, not only subprocess re-imports.'
  - persona: harness-qa
    op: replace
    target: G-13
    section: Gotchas
    entry: "WHEN writing, copying or deleting under bash-write-guard DO use literal\
      \ absolute targets \u2014 variable-bearing redirect, cp or rm targets are blocked\
      \ even under /tmp or notes/; clean up inside a python driver. `git checkout`\
      \ is refused even in a /tmp clone: use `git archive <sha> | tar -x`."
    why: 'Observed this feature: git checkout refused inside a /tmp clone; git archive
      gave a source-identical tree without moving HEAD. Same guard as G-13, so merged
      rather than displacing another entry.'
  - persona: harness-security-reviewer
    op: replace
    target: P-14
    section: Patterns
    entry: WHEN grading a fail-open that requires damaged or tampered state DO check
      whether the security contract explicitly covers that state. If it does, grade
      the lost protection without discounting merely because the state is abnormal;
      report actor access and reachability separately.
    why: The lead and ruler upheld high because the guard existed to refuse damaged
      state. P-12 covers capability delta, P-17 irreversibility, and O-04 evidence
      provenance; none tests whether the precondition is the threat the control promises
      to handle. This broader grading rule displaces the narrower filesystem recovery
      naming heuristic.
  - persona: harness-ui-reviewer
    op: replace
    target: G-11
    section: Gotchas
    entry: "WHEN certifying a printed shell command as copy-runnable DO include an\
      \ embedded newline in a dynamic fixture value and test the literal physical\
      \ line a reader would copy \u2014 whole-command argv round-tripping can pass\
      \ while the printed line splits or a value looks like a separate instruction."
    why: U1 adds a physical-line probe missing from O-10 (operator outcome), G-14
      (source search) and O-08 (exact prior repro). Displaces a narrower generated-HTML
      heuristic retained in harness repository Patterns and covered generally by the
      changed-object census.
  - persona: harness-ui-reviewer
    op: replace
    target: P-03
    section: Patterns
    entry: WHEN a printed remedy command selects a target DO copy-run it against a
      disposable intended target with a matching decoy at the default destination;
      verify which target was read or changed and that the decoy was untouched. Exit
      status alone cannot distinguish successful misrouting.
    why: The c2 decoy made a successful operation on the wrong target detectable,
      more specific than general pre-signature literal execution or O-08. Displaces
      markdown-specific scope guidance already substantially covered by the changed-object
      census and direct contract checks.
  - persona: harness-validator-lead
    op: replace
    target: P-12
    section: Patterns
    entry: "WHEN specifying a must-fix against a defect class DO hand down every state,\
      \ predicate leg and representation the decision consumes, reading how the producer\
      \ normalizes each shape first, and require a discriminating mutant per leg \u2014\
      \ a defaulted shape must pass, and an unwitnessed leg's mutant can fail open."
    why: My c1 must_fix prescribed refusing both null and omitted features; the ruler
      found the producer normalizes omitted to a legitimate default that must pass,
      so my fixture spec would have forced a regression. The ruled check then had
      three legs but fixtures only for two; the isinstance leg's mutant survived c2
      and fails open. Sharpens P-12 (states/representation) with legs and producer
      normalization; same length class.
  team: distill (validator squad)
  steps_run: 3
  cycles_used: 0
  members:
  - step: distill-qa
    persona: harness-qa
    verdict: PASS
    headline: QA1 accepted and merged into craft G-05. Craft P-06 and P-07 and repository
      G-13 were replaced from QA's own log and notes. All sections stay full.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/expertise/harness-qa.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/expertise/harness-qa.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/notes/qa-distill.md
  - step: distill-security-reviewer
    persona: harness-security-reviewer
    verdict: PASS
    headline: 'S1 accepted as a craft P-14 replace: do not discount a fail-open because
      its damaged-state precondition is one the contract covers. The newline and producer-probe
      lessons were declined because G-07, O-02 and O-04 already cover them.'
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/expertise/harness-security-reviewer.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/notes/review-harness-security-reviewer-distill.md
  - step: distill-ui-reviewer
    persona: harness-ui-reviewer
    verdict: PASS
    headline: U1 accepted as a craft G-11 replace (newline in the copied physical
      line), and the decoy-target copy-run became a craft P-03 replace. A signed-wording
      entry was declined because G-08 already governs it.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/expertise/harness-ui-reviewer.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/notes/review-harness-ui-reviewer-distill.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'Distill dispatch: no diff was reviewed and no suite was run.'
  - "I checked every member op against its receipt and the resulting file by grepping\
    \ the entry id and its text. qa: expertise-receipt-001cffbe\u2026.json, craft\
    \ batch fc3ec8ab\u2026 and repository batch 3cad7c79\u2026 (G-13 is repository\
    \ tier, segment harness). security: expertise-receipt-9bacb180\u2026.json, batch\
    \ 92ec21b5\u2026. ui: expertise-receipt-fbf6bd30\u2026.json, batch c7e91a51\u2026\
    . lead: expertise-receipt-b72364fe\u2026.json, batch d505408b\u2026. Every send-back\
    \ criterion is met and there were no send-backs."
  - Section counts stay at cap for every craft file (P 15, G 15, O 10, Open 0) and
    for qa's repository Gotchas (15). Every op was a replace, so no op displaced an
    entry without naming it.
  - 'Not dispatched: pm and code-reviewer, because the product squad already distilled
    them (runs/distill-product). No other validator member ran on this feature.'
  - Lead considered and did not write two entries. One was an outcome confirming P-04
    (the ruler upheld my non-gating rating on OQ-3); Outcomes is full and no current
    entry is weaker. The other was 'executed measurement beats reasoned trace', which
    is already pm's O-12.
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
  readers: []
```
