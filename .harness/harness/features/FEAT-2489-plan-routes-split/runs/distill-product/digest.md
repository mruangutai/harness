# FEAT-2489 distill (product) — PASS: pm settled C7 and re-anchored refactor contracts; lead sharpened O-09; code-reviewer distill refused by dispatch-guard

**pm (batches `64d4da6b…` craft, `a04ac66d…` repository):** C7 is settled from the source. In `plan_merge/union.py`, `_carry_base_items` replaces a changed task or decision field and exits 0. Only `_merge_plain_key` still exits 7, when a plain top-level key carries two values. So repository P-04 was replaced with the correct rule, P-08 dropped (its amend guidance absorbed into P-04), and G-07 refreshed (panel still exits 7 under apply; record-panel is the writer). Repository O-02 added: a matched-tree base archive for gate-equivalence proofs. Craft P-14 replaced (candidate 3): a refactor contract is stated from the move's guarantee with a census before signature, not from an enumerated list of differences. Craft G-18 replaced: binding a receipt to a checkpoint needs resolve + ancestry + two-sided content. Candidate 2 (record-panel) rejected as the tool defect itself (backlog #2525). Counts: craft P15→15 G15→15 O10→10 Open0→0; repository P13→12 G15→15 O1→2 Open0→0.

**Lead (craft, batch `0c300e69…`):** O-09 replaced. O-09 as written was applied in this plan and did not terminate: SC-02 was restated as a class three times, each keyed on where effects surface. The new O-09 has pm key the class on what the change itself guarantees, backed by a census before signature. Counts P15→15 G15→15 O9→9 Open0→0.

**code-reviewer: not run.** dispatch-guard refused the distill dispatch: it reads any code-reviewer start from product-lead as the plan team's scope reader and demands `HARNESS-MISSION: plan`, while harness-distill requires `distill`. I did not relabel the mission. The candidate (enumerate every member of a class contract in one read, not one counterexample per cycle) is carried as an open question. ui-reviewer was not dispatched: its only plan note is a one-line self-scope-out with no lesson.

**Assessment:** send-back criteria 1–5 (`sendback-criteria.md`, written before dispatch) are met for pm. I confirmed P-04, G-07, O-02, P-14 and G-18 are in the resulting files. Criteria 6–8 were not reached because code-reviewer was refused. This was a distillation only: no diff reviewed and no suite run.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/distill-product/digest.md
DIGEST:
  headline: 'Product distill done. pm checked C7 against the source: plan-merge apply
    now replaces changed task fields at exit 0, so repository P-04 was replaced, P-08
    dropped and G-07 refreshed. pm re-anchored refactor contracts on the move''s guarantee
    plus a census taken before signature (craft P-14). Lead sharpened O-09 the same
    way. The code-reviewer distill was refused by dispatch-guard (mission mismatch,
    harness defect).'
  open_questions:
  - id: OQ-D1
    question: "Possible harness defect: dispatch-guard refused a harness-product-lead\
      \ \u2192 harness-code-reviewer distill dispatch carrying 'HARNESS-MISSION: distill'.\
      \ It treats every code-reviewer start from product-lead as the plan team's scope\
      \ reader and requires 'HARNESS-MISSION: plan', while harness-distill requires\
      \ distill. I did not relabel the mission. Should the guard key the scope-reader\
      \ rule on the plan run or team rather than the persona pair?"
    blocking: false
  - id: OQ-D2
    question: "Undelivered candidate for harness-code-reviewer, whose own judgement\
      \ it needs. In plan-panel cycles c2\u2013c4 each re-read found exactly one more\
      \ forced member of SC-02's class, so each counterexample cost a full cycle.\
      \ Proposed lesson: WHEN a remedy states a class contract, enumerate its members\
      \ across every output channel (data-derived text, scanned values, runtime tracebacks)\
      \ in one read and report all counterexamples together. It could also sharpen\
      \ craft P-08 or O-04. Route it through the validator-lead's code-reviewer distill\
      \ dispatch, or have Main dispatch it?"
    blocking: false
  files_touched:
  - .harness/expertise/harness-pm.md
  - .harness/harness/expertise/harness-pm.md
  - .harness/expertise/harness-product-lead.md
  - .harness/harness/features/FEAT-2489-plan-routes-split/notes/research-FEAT-2489-plan-routes-split-distill.md
  - .harness/harness/features/FEAT-2489-plan-routes-split/runs/distill-product/state.yaml
  - .harness/harness/features/FEAT-2489-plan-routes-split/runs/distill-product/sendback-criteria.md
  - .harness/harness/features/FEAT-2489-plan-routes-split/runs/distill-product/digest.md
  expertise_update:
  - persona: harness-pm
    op: replace
    target: P-14
    section: Patterns
    entry: WHEN planning a semantics-preserving refactor DO record baseline exit,
      stdout and stderr receipts for its owning suites and state the contract from
      the move's guarantee (unchanged rules per physical file, real-tree equivalence),
      evidenced by a pre-signature census of per-file analysis state. Enumerated difference
      lists gain a member each cycle.
    why: A verbatim-move contract stated as an enumerated list of admitted output
      differences (field-keyed, then printed-locator, then first-site) missed one
      forced member per panel cycle through three reads and two post-signature amendments;
      it terminated only when re-anchored on what the move proves, with a per-file
      state census as evidence. The old P-14's 'permit only enumerated divergences'
      prescribed the failing shape.
  - persona: harness-pm
    op: replace
    target: G-18
    section: Gotchas
    entry: 'WHEN a verify binds a receipt to a checkpoint commit DO require the recorded
      commit to resolve, be an ancestor, and carry content excluding both the base
      and later commits: hash prefixes bind nothing, and ancestry alone admits every
      earlier and later state.'
    why: A receipt bound by HEAD/blob prefixes was ruled unbound by the panel and
      cost a cycle; the fix needed rev-parse plus ancestry plus a two-sided content
      predicate. Receipt-binding verifies recur in pm-authored plans far more often
      than installed-runtime provenance, the displaced entry's situation.
  - persona: harness-pm
    op: replace
    target: P-04
    section: Patterns
    entry: WHEN revising a field of an existing task or decision DO expect apply to
      replace it in place (REPLACED, exit 0); only a differing plain top-level key
      exits 7. For a signed task's intent, files or verify use amend --expect-sha256
      --reason, which ledgers the change INV-40 otherwise reports.
    why: 'C7 verify-or-drop: control-plane plan_merge/union.py _carry_base_items replaces
      differing task/decision fields field by field (comment: ''This was exit 7 CONFLICT'');
      _merge_plain_key raises exit 7 only for a top-level key with two values; amend.py
      requires --reason on a signed task''s intent/files/verify (INV-40 d). Old claim
      stale; absorbs P-08.'
  - persona: harness-pm
    op: drop
    target: P-08
    section: Patterns
    why: 'C7: its premise (apply exits 7 CONFLICT on any changed value) is false at
      union.py _carry_base_items; the surviving amend guidance is absorbed into P-04.'
  - persona: harness-pm
    op: replace
    target: G-07
    section: Gotchas
    entry: 'WHEN writing plan.yaml''s panel key DO use record-panel from the validator
      lead''s digest, never apply: panel is a plain top-level key, so apply exits
      7 CONFLICT on any differing value. set-panel is the validated hand route, for
      a ruled repair only.'
    why: 'C7 check of G-07: panel still routes through union.py _merge_plain_key (exit
      7 on differing value), confirmed. Its set-panel safe_dump byte-churn clause
      is stale (set-panel now keeps unchanged findings'' bytes per --help) and record-panel
      is the sanctioned writer (DEC-229).'
  - persona: harness-pm
    op: add
    target: O-02
    section: Outcomes
    entry: 'WHEN proving a harness bin gate behaves the same before and after a change
      DO run both sides from a git archive of the base, the candidate overlaying only
      HEAD''s bin and tests, with HARNESS_PROJECT_DIR set to each archive: identical
      plans and corpus leave only the code varying.'
    why: 'Measured this feature: the archive is a runnable matched tree for check-plan-routes.py
      in all modes, and it removed the corpus difference (the feature''s own plan
      exists only at pin) that otherwise polluted old-vs-new comparison. Equivalence
      proofs for gate refactors recur in this repo.'
  - persona: harness-product-lead
    op: replace
    target: O-09
    section: Outcomes
    entry: "WHEN a plan-time reader's repairs each surface one narrower failure in\
      \ one mechanism DO have pm key the class on what the change itself guarantees,\
      \ and commission a census of the affected state before signature \u2014 a class\
      \ keyed on where effects surface is still an enumeration."
    why: 'O-09 as written was applied here and did not terminate: SC-02 was restated
      as a class three times (by rewritten field, by printed locator, by first site),
      each still keyed on where effects surface, and each re-read found one more member;
      it terminated only when re-anchored on what the move proves, with a per-file
      census as evidence.'
  team: distill
  steps_run: 1
  cycles_used: 0
  members:
  - step: distill-pm
    persona: harness-pm
    verdict: PASS
    headline: 'C7 checked against the source: apply replaces changed fields at exit
      0, so repository P-04 was replaced, P-08 dropped, G-07 refreshed and O-02 added.
      Craft P-14 now states refactor contracts from the move''s guarantee plus a census,
      and G-18 covers receipt binding. Candidate 2 and 8 log bullets were rejected
      with reasons.'
    files_touched:
    - .harness/expertise/harness-pm.md
    - .harness/harness/expertise/harness-pm.md
    - .harness/harness/features/FEAT-2489-plan-routes-split/notes/research-FEAT-2489-plan-routes-split-distill.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'pm counts from tool results. Craft (batch 64d4da6bcbd2fb03b4556802d8f6122b5e34d8fea0ea7907fef96c87e4bf1aed):
    Patterns 15->15, Gotchas 15->15, Outcomes 10->10, Open 0->0. Repository harness
    (batch a04ac66d6ac13127fdad146ba185a9df6391c69cd01d5d0023659b465a7e7dda): Patterns
    13->12, Gotchas 15->15, Outcomes 1->2, Open 0->0.'
  - 'Lead craft (batch 0c300e6942e8b35ac95048607565393f2939edb86a7a5aef91681528ddf5d3e4):
    Patterns 15->15, Gotchas 15->15, Outcomes 9->9, Open 0->0 (O-09 replaced). Lead
    repository tier untouched (P 3, G 0, O 0, Open 0).'
  - 'Candidate dispositions for pm. (1) C7 applied: P-04 replaced, P-08 dropped, G-07
    refreshed. (2) record-panel rejected: it is the tool defect itself, backlog #2525,
    and the only possible lesson is a workaround that goes stale once the defect is
    fixed. (3) Applied as a replace of craft P-14, whose old ''permit only enumerated
    divergences'' wording prescribed the shape that failed.'
  - Send-back criteria 1-5 (runs/distill-product/sendback-criteria.md, written before
    dispatch) were met for pm. I confirmed P-04, G-07, O-02, P-14 and G-18 by grep
    in the resulting files. Criteria 6-8 were not reached because the code-reviewer
    dispatch was refused (OQ-D1, OQ-D2).
  - 'harness-code-reviewer was not run: dispatch-guard refused it before spawn on
    a mission mismatch, which I did not work around. harness-ui-reviewer was not dispatched
    because its only plan note is a one-line self-scope-out with nothing to distill.'
  - 'Lead dispatch error, my own: the first dispatch passed name: and the guard refused
    it. That rule is already in harness-team, so no Expertise entry.'
  - This was a distillation only. No diff was reviewed and no suite was run.
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
  readers: []
```
