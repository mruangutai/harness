# FEAT-2542 distill — product squad (run distill-product)

**BLUF: PASS.** The product-lead → code-reviewer distill dispatch with `HARNESS-MISSION: distill` was **not refused**, so #2532's fix holds in live use. The code-reviewer accepted both relayed candidates. pm accepted all three relayed candidates and one bullet from its own log. All writes are receipted and checked against the resulting files, and no section is over its cap.

## distill-pm (harness-pm): PASS
Artifact: `notes/research-FEAT-2542-dispatcher-placement-distill.md`. Receipt: `notes/expertise-receipt-3f4d42b5….json`, craft batch `87889658…`.
- **P-18 replaced (C1):** enumerate a producer's result fields by shape in successful rows too (null, empty, omitted, wrong type), and note what the producer normalizes to a default that must pass.
- **P-08 replaced (C2):** before signature, exercise each prescribed literal, verify and printed command against whatever consumes it. That covers the word-cap and unrunnable-command cases.
- **P-01 replaced (own bullet 4):** a plan predicts reds per assertion, and the gate is predicted set = observed set.
- **O-12 replaced (C3):** run an executable mutant claim before grading its severity. It displaces a narrow symlink recipe.
- No repository-tier ops. pm rejected its other six own-log bullets with reasons in its artifact.
- Craft counts: P 15→15, G 15→15, O 10→10, Open 0→0.

## distill-code-reviewer (harness-code-reviewer): PASS
Artifact: `notes/review-harness-code-reviewer-distill.md`. Receipt: `notes/expertise-receipt-9dd9fecf….json`.
- **Craft P-14 replaced (CR1), batch `49b600e9…`:** a contract or characterization keyed on producer outcomes needs an inventory of success-field shapes, not only of failure causes. It displaces the guarded-import exception-ownership pattern. Counts: P 15→15, G 15, O 10.
- **Repository G-12 added (CR2), batch `5d5e7b7d…`:** a consumer of find_run_claim must pass an omitted feature (`legacy`) and refuse null, empty or non-str. Counts: P 3, G 11→12, O 0; about 21 of 40 lines.
- **The member corrected my relay.** I passed on the ruling's gloss that the "writer at :870" normalizes falsy features. Line 870 sits in `release_cmd`, not in the claim writer; I confirmed this by reading the enclosing function. The member narrowed the entry to the verified read interface.
- Gate fields: `code_grade: n_a`, `reviewed: none`.

## Lead's own
- **Craft, batch `b0e300b7…`:**
  - P-02 replaced: when you assess or relay a cited line, open the enclosing function, not just the grep hit. This comes from the :870 correction above.
  - O-10 replaced: in an accept-as-applied signature question, name any applied literal or command text as unread. The signer's re-read graded substance, and validate c0 found the applied printed commands unrunnable.
  - The first attempt was refused with exit 14 because P-02 ran to 51 words. I trimmed it and re-applied; the refused attempt wrote nothing.
  - Counts: P 15, G 15, O 10, Open 0, unchanged.
- **Repository, batch `555a3fcf…`:** P-04 added: a product distill dispatches the borrowed code-reviewer with mission distill, and older digests recording that refusal are stale precedent. Counts: P 3→4.
- **Procedural miss:** my first dispatch carried a `name:` parameter, which harness-team already forbids, and dispatch-guard refused it before any spawn. I re-dispatched without it. No new entry: the rule already exists.

## Not dispatched
- **ui-reviewer:** the plan-team design reader. Its plan findings were semantic remedy gaps, and its craft already covers them (G-13, O-10). The unrunnable command rendering arrived at apply, after its read, so it has no plan-time lesson. Its validate-time copy-run lesson belongs to the validator squad's distill.
- **visual-designer and documentor:** did not run on this feature and kept no logs.
- **fable-advisor:** keeps no Expertise.

Send-back criteria (`sendback-criteria.md`, written before dispatch): all met. Reservation, left standing per O-03: pm's P-01 displaced the role-identity protection pattern.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'FEAT-2542 product distill is complete. The product-lead to code-reviewer
    distill dispatch was not refused, so the #2532 fix works in live use. code-reviewer
    accepted both candidates (craft P-14, repository G-12). pm accepted C1-C3 and
    own bullet 4 (4 craft replaces). The lead replaced P-02 and O-10 and added repository
    P-04. All writes are receipted and within cap.'
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/expertise/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/expertise/harness-code-reviewer.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/expertise/harness-code-reviewer.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/expertise/harness-product-lead.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/expertise/harness-product-lead.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/notes/research-FEAT-2542-dispatcher-placement-distill.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/notes/review-harness-code-reviewer-distill.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/runs/distill-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/runs/distill-product/sendback-criteria.md
  expertise_update:
  - persona: harness-pm
    op: replace
    target: P-18
    section: Patterns
    entry: 'WHEN a criterion keys on a producer''s result or payload DO enumerate
      each field the decision reads by shape, in successful results too, not only
      per failure cause: null, empty, omitted, wrong type, plus related objects''
      identity binding. Note what the producer normalizes to a default that must pass.'
    why: 'C1 accepted as a sharpening of P-18: my characterization enumerated a producer''s
      outcomes by cause and missed an ok row with a null field that failed open, while
      the omitted shape is normalized by the producer to a legitimate default that
      must pass. Old P-18 was scoped to external payloads and container shapes; same
      length class, broader trigger.'
  - persona: harness-pm
    op: replace
    target: P-08
    section: Patterns
    entry: 'WHEN intent prescribes a literal, verify or printed command DO exercise
      each against its consumer before signature: verify against the completion state
      intent predicts, literal through every gate reading it, command pasted verbatim
      into a fresh shell. Where intent predicts a case still fails, ALL-PASSED is
      unsatisfiable: split the task.'
    why: 'C2 accepted as a generalization of P-08: signed intent dictated an index
      ruling over its own verify''s word cap and printed repair commands that were
      not runnable as printed (bare script name, punctuation adjoining a path, unquoted).
      P-08 already covered verify-vs-intent; its task-boundary remedy is kept.'
  - persona: harness-pm
    op: replace
    target: P-01
    section: Patterns
    entry: WHEN a plan predicts which checks a change turns red at base DO name each
      predicted check per assertion, separating cause text from exit and side effect,
      and gate on predicted set equal to observed set. A prose prediction is unfalsifiable
      and silently mispredicts rows the census never listed.
    why: 'Own log bullet 4: a prose fail-first prediction was wrong and ungradeable;
      per-assertion names with predicted_red = observed_red set equality held at validate
      twice (97=97, 110=110) and made mispredictions loud. Patterns full; displaces
      P-01, the narrowest pattern (role-identity protection), judged weaker.'
  - persona: harness-pm
    op: replace
    target: O-12
    section: Outcomes
    entry: WHEN asserting what a mutation or malformed input would do (fail open,
      crash, misroute) and the case is executable DO run it and cite the measured
      exit and output before grading severity; a reasoned trace through quoting or
      exception paths can miss where the code already fails closed.
    why: 'C3 accepted: my goal-check reasoned a swapped-check mutant fails open; QA
      executed it and measured fail-closed exit 2, and my reasoning was dismissed.
      O-06/O-07 concern harness validity and free mutants, not executing a severity
      claim. Outcomes full; displaces O-12, a narrow Python symlink recipe.'
  - persona: harness-code-reviewer
    op: replace
    target: P-14
    section: Patterns
    entry: WHEN a contract or characterization keys on producer outcomes DO inventory
      success-field shapes as well as failure causes. Trace null, empty, omitted,
      and wrong-type values through producer normalization before predicting consumer
      behavior.
    why: 'CR1 accepted: the cause matrix appeared complete but omitted a successful
      row that reached an unintended fallback. P-08 traces scope and sources and P-07
      compares predicates after refactoring; neither asks for this inventory at plan
      time. Patterns was full (15/15); this check applies more broadly than the guarded-import
      exception-ownership rule it displaces.'
  - persona: harness-code-reviewer
    op: add
    target: G-12
    section: Gotchas
    entry: WHEN reviewing a consumer of inflight_registry.py's find_run_claim DO expect
      an omitted feature to pass the feature-validity check as LEGACY_FEATURE, not
      be refused. An explicit null, empty string, or non-string reaches the consumer
      unchanged and must fail that check.
    why: 'CR2 accepted: find_run_claim defaults only a missing key; a consumer review
      would otherwise conflate valid legacy placement with malformed stored values.
      Narrowed the candidate to the verified read interface: the cited falsy normalization
      is in release_cmd, not the claim writer.'
  - persona: harness-product-lead
    op: replace
    target: P-02
    section: Patterns
    entry: "WHEN assessing or relaying a cited line DO open the enclosing function,\
      \ not just the grep hit \u2014 a pointer can be sound while its prose gloss\
      \ is wrong, and a grep hit confirms the text but not which code path owns it."
    why: I relayed a ruling's gloss 'writer at :870' after grepping the line; the
      member opened it and found it inside release_cmd, not the claim writer, and
      narrowed the entry. Old P-02 already said open a cited line; the grep-hit-vs-enclosing-function
      gap is the sharper rule.
  - persona: harness-product-lead
    op: replace
    target: O-10
    section: Outcomes
    entry: "WHEN apply remediates a high plan-reader finding and the team runs no\
      \ re-read step DO put it to the operator as one blocking signature question\
      \ with a recommendation, naming applied text that prescribes literal commands\
      \ or gate-read literals as unread \u2014 a signer's re-read grades substance,\
      \ not rendering."
    why: 'Outcome of following O-10: the signer accepted the applied remediations
      as re-read, and validate later found the applied printed repair commands unrunnable
      as printed (bare script, punctuation adjoining a path, unquoted). The question
      had not flagged literal text as the unread risk.'
  - persona: harness-product-lead
    op: add
    target: P-04
    section: Patterns
    entry: "WHEN a product distill run must reach a borrowed plan reader DO dispatch\
      \ harness-code-reviewer with HARNESS-MISSION: distill \u2014 dispatch-guard\
      \ now places the lead by its own registered distill run, so older distill digests\
      \ recording that refusal are stale precedent, not a reason to skip the reader."
    why: The product-lead to code-reviewer distill dispatch ran without refusal in
      this run; earlier product distill digests record it as refused and the reader's
      lesson undelivered.
  team: distill (product squad)
  steps_run: 2
  cycles_used: 0
  members:
  - step: distill-pm
    persona: harness-pm
    verdict: PASS
    headline: "C1, C2, C3 and own bullet 4 accepted; craft P-18, P-08, P-01 and O-12\
      \ replaced (P 15\u219215, G 15\u219215, O 10\u219210); no repository ops; the\
      \ other 6 own bullets rejected with reasons."
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/expertise/harness-pm.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/notes/research-FEAT-2542-dispatcher-placement-distill.md
  - step: distill-code-reviewer
    persona: harness-code-reviewer
    verdict: PASS
    headline: The distill dispatch was not refused. CR1 replaced craft P-14; CR2 added
      repository G-12, narrowed after the member corrected the lead's :870 gloss.
      code_grade n_a, reviewed none.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/expertise/harness-code-reviewer.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/expertise/harness-code-reviewer.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/notes/review-harness-code-reviewer-distill.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'Distill dispatch: no diff was reviewed and no suite was run.'
  - 'The product-lead to harness-code-reviewer dispatch with HARNESS-MISSION: distill
    was NOT refused. There is no refusal text to report.'
  - 'My first task call carried a name: parameter, which harness-team already forbids.
    dispatch-guard refused it before any spawn: ''harness-product-lead passed name:
    ... Re-dispatch without the name parameter.'' I re-dispatched without it.'
  - "I checked every member op against its receipt and the resulting file. pm: expertise-receipt-3f4d42b5\u2026\
    .json, batch 87889658\u2026. code-reviewer: expertise-receipt-9dd9fecf\u2026.json,\
    \ batches 49b600e9\u2026 (craft) and 5d5e7b7d\u2026 (repository). All send-back\
    \ criteria are met."
  - "The lead's own ops: craft batch b0e300b7\u2026 and repository batch 555a3fcf\u2026\
    \ (receipt expertise-receipt-e3f969bf\u2026.json). The first craft attempt was\
    \ refused with exit 14 (P-02 at 51 words). I trimmed it and re-applied; the refused\
    \ attempt wrote nothing. Counts: craft unchanged at 15/15/10/0; repository Patterns\
    \ 3\u21924."
  - 'Reservation, left standing per O-03: pm''s P-01 replacement displaced its role-identity
    protection pattern.'
  - 'Not dispatched: ui-reviewer (its plan read predates the applied command text,
    its craft covers the remedy lessons, and its validate lessons are the validator
    squad''s), visual-designer and documentor (did not run, no logs), fable-advisor
    (keeps no Expertise).'
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2542-dispatcher-placement/.harness/harness/features/FEAT-2542-dispatcher-placement/runs/distill-product/digest.md
```
