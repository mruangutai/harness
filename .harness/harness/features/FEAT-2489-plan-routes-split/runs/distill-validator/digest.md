# Distill (validator squad) — FEAT-2489-plan-routes-split

**PASS. All four members that carried validate lessons distilled, and so did the lead. 12 ops were applied in 7 batches. No suite was run and no diff was reviewed.** The ui-reviewer was not dispatched: it self-scoped out in every cycle and has no lesson.

## Per member (counts before → after, from the tool results)

| Member | Ops | Craft P/G/O/Open | Repo (harness) | Batch(es) |
|---|---|---|---|---|
| harness-qa | G-04, G-02 replaced; Open Q-01 dropped; repo G-13 replaced; repo G-15 added | 15/15/10/1 → 15/15/10/0 | G 14 → 15 | c486b80f…, f3f4dcdf… |
| harness-code-reviewer | P-08 replaced (class census across outputs, scoped state, prefilters; report together) | 15/15/10/0 unchanged | untouched | b5a4fb48… |
| harness-security-reviewer | P-02 replaced (compare the least-privileged editor's existing capability before rating) | 15/15/10/0 unchanged | untouched | c0351e31… |
| harness-pm (goalcheck) | P-12 replaced (grade met only if the receipt or a census reaches the class) | 15/15/10/0 unchanged | untouched | d250d3fb… |
| harness-validator-lead (self) | P-14 = old P-13 + P-14 merged; P-13 new; O-02 form fix | 15/15/10/0 unchanged | P-02 form fix; 2/4/0/0 unchanged | 7496a7ee…, 911f64c3… |

## How each relayed candidate was disposed

- **QA.**
  - Pristine-runner concealment: applied as G-04.
  - Archive-tree method: rejected as already covered.
  - Log items:
    - bash-write-guard `$VAR` targets: repo G-13, with Open Q-01 resolved and dropped.
    - Stale helper call shape: repo G-15, written as a pointer to the live call site.
    - Phantom CI step: folded into G-02.
    - Bare-CR probe: rejected.
- **Code-reviewer.** Candidates 1 and 2 were merged into one rule, P-08. The temp-replay refusal was rejected because O-11 already covers it.
- **Security.** The SEC-1 trust-domain reasoning was kept, in a guarded direction: equal capability under the same controls means hardening, but a different identity, target or bypassed approval can still cross a boundary. The checkout-path advisory was rejected.
- **pm.** The goalcheck rule is new beyond P-14 (pm's reason: no existing entry ties a verdict to how much of the class the receipt reaches). It displaces P-12, which the handoff skill's decide-or-ask scoping already covers.
- **Lead.**
  1. Post-PASS upstream merge covered mechanically: **rejected as Expertise.** It was one advisor ruling under delegated approval, and the advisor itself noted that no doctrine rules the post-PASS-merge case. Encoding it would adopt unsigned policy, so it goes to open_questions instead.
  2. Dual severities under P-04: **no op.** This is a confirmation, and adding it would only add an instance. I applied an unrelocated lesson instead: rate refactor-induced divergences by direction against the truth (new P-13). Both validate escalations and the c3 census note turned on that direction.

## Open questions

- OQ-1 (non-blocking, harness owner): no decision rules whether an upstream merge landing after a validate PASS needs a re-pin or re-validation. This feature's answer came from a one-off advisor ruling (`notes/answers-2026-11-24-merge-ship.md` Q1).

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/distill-validator/digest.md
DIGEST:
  headline: 'Validator distill PASS: 12 ops applied across qa (5), code-reviewer (1),
    security (1), pm goalcheck (1) and the lead (4). Craft counts are unchanged at
    the caps, except that qa''s Open went 1->0 and its repository Gotchas went 14->15.
    The post-PASS-merge candidate was routed to open_questions as an unruled doctrine
    gap.'
  open_questions:
  - id: OQ-1
    question: 'Harness owner: no decision rules whether an upstream merge that lands
      after a validate PASS needs a re-pin or re-validation. This feature relied on
      a one-off advisor ruling (notes/answers-2026-11-24-merge-ship.md Q1). Should
      it become a decision?'
    blocking: false
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/distill-validator/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/expertise/harness-validator-lead.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/expertise/harness-validator-lead.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/expertise/harness-qa.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/expertise/harness-qa.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/expertise/harness-code-reviewer.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/expertise/harness-security-reviewer.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/expertise/harness-pm.md
  expertise_update:
  - persona: harness-validator-lead
    op: replace
    target: P-14
    section: Patterns
    entry: "WHEN a gate or sweep reports zero or a small count DO confirm both that\
      \ it discovered a non-zero set and that its pattern matches a known positive\
      \ before accepting it \u2014 an empty sweep and a mis-anchored pattern both\
      \ exit like cleanliness, and nobody re-runs your sweep."
    why: 'Merges old P-13 (non-zero discovery count) and P-14 (pattern matches a known
      positive): one situation, a zero that reads as clean, two causes. Frees P-13
      for a new rule; no longer than the longer input.'
  - persona: harness-validator-lead
    op: replace
    target: P-13
    section: Patterns
    entry: "WHEN rating a divergence a refactor introduces into a gate's output DO\
      \ classify its direction against the truth \u2014 fail-open, fail-closed, or\
      \ more accurate than base \u2014 before severity; confining base's own imprecision\
      \ is no regression, while hiding a real defect is one at any size."
    why: 'Across three validate cycles of a gate-module split, every divergence on
      perturbed trees was rated by direction: no more fail-open (per-file counts),
      more accurate than base (per-file alias map), fail-open false negative (raw-text
      prefilter). That axis set the operational rating carried under P-04; no member
      rates it. Displaces old P-13, now absorbed into P-14.'
  - persona: harness-validator-lead
    op: replace
    target: O-02
    section: Outcomes
    entry: "WHEN a stricter lock exposes a real production site DO derive that site\
      \ from the governing authority rather than exempt it \u2014 exemptions preserve\
      \ the parallel source of truth the lock exists to remove."
    why: 'Form fix: the entry carried a duplicated ''O-02:'' prefix inside its text.
      Content unchanged.'
  - persona: harness-validator-lead
    op: replace
    target: P-02
    section: Patterns
    entry: WHEN this repository's plan carries a change_type absent from harness.json's
      test_matrix vocabulary DO treat the plan as malformed and correct the record;
      never add a synonymous mapping to legitimize it.
    why: 'Form fix: the entry carried a duplicated ''P-02:'' prefix inside its text.
      Content unchanged.'
  - persona: harness-qa
    op: replace
    target: G-04
    section: Gotchas
    entry: "WHEN measuring base-versus-head equivalence of a refactor DO run each\
      \ side whole-process through its own entry, and attribute any difference by\
      \ swapping only the code over one fixed tree \u2014 a substituted or shared\
      \ runner hides load-shape differences such as added import-traceback frames."
    why: 'Validate c2: a seam receipt that ran a pristine entry against perturbed
      trees concealed 4 added traceback lines; own-entry whole-process runs revealed
      it, and c3''s fixed-tree code swap attributed a route-mode difference to data
      not code. Displaces old G-04, now redundant because DEC-255 runner receipts
      already force a full per-kind run.'
  - persona: harness-qa
    op: replace
    target: G-02
    section: Gotchas
    entry: "WHEN the repository's CI runs gates the QA matrix omits DO enumerate CI's\
      \ required steps at the reviewed tip, run or name each omitted one, and confirm\
      \ any gate a dispatch names actually exists there \u2014 a green matrix is not\
      \ CI-green, and a phantom gate gets cited as coverage."
    why: Dispatch named a CI consolidation gate that the workflow never had; reporting
      it as CI-run would have falsified coverage. Same situation as G-02, sharpened
      at equal length.
  - persona: harness-qa
    op: drop
    target: Q-01
    section: Open
    why: 'Resolved this feature: bash-write-guard''s allow/deny for cp/redirect turns
      on a literal versus shell-variable target (literal allowed, $VAR blocked), which
      explains the earlier inconsistent sessions; recorded in repository G-13.'
  - persona: harness-qa
    op: replace
    target: G-13
    section: Gotchas
    entry: "WHEN writing, copying or deleting under bash-write-guard DO use literal\
      \ absolute target paths \u2014 a redirect, cp or rm target containing a shell\
      \ variable is blocked even under /tmp or the feature's notes/; do temp cleanup\
      \ inside a python driver and pipe rather than redirect in loops."
    why: Reconfirmed across validate c1-c3 for cp and rm, not only redirects; widens
      G-13 to the measured class at the same length.
  - persona: harness-qa
    op: add
    target: G-15
    section: Gotchas
    entry: "WHEN calling check-integration-shards helpers directly to check a runner\
      \ receipt DO copy the call shape from validate-digest.py's own call site \u2014\
      \ discover_expected returns a (paths, error) tuple, and a stale call yields\
      \ a misleading wall of unexpected/omitted defects, not a real receipt defect."
    why: Every validate run checks receipts with these helpers; a stale 2-arg call
      produced a false defect wall this feature. Pointer to the living call site,
      not an inlined recipe.
  - persona: harness-code-reviewer
    op: replace
    target: P-08
    section: Patterns
    entry: WHEN reviewing a class-wide contract or fix DO trace every output to its
      source across phases and inventory boundary-scoped state, aggregates, and prefilters.
      Probe excluded exception families and one reachable case beyond the boundary;
      report counterexamples together rather than stopping at the first.
    why: Plan reviews found successive missed output producers; validation found separately
      scoped audit mechanisms. Both reward an up-front census, not another instance
      replay.
  - persona: harness-security-reviewer
    op: replace
    target: P-02
    section: Patterns
    entry: "WHEN grading a new injection or traversal path DO verify the least-privileged\
      \ input editor\u2019s existing capabilities in the same execution context before\
      \ rating severity. Equal or greater capability under the same controls makes\
      \ it hardening; a different identity, target, or bypassed approval can still\
      \ cross a boundary."
    why: "The review rated a new write sink before comparing the inventory editor\u2019\
      s rights with the executable code already run by the same suite. This replaces\
      \ the overbroad assumption that controlling a value implies holding the privilege\
      \ it grants."
  - persona: harness-pm
    op: replace
    target: P-12
    section: Patterns
    entry: WHEN grading a class-scoped criterion from a receipt DO first read what
      its own disclosure and the signed gaps say it omits; grade met only if the receipt
      or a census reaches every class member, else partial naming the unsampled states.
      A ruling prescribing that evidence does not widen it.
    why: 'Two consecutive goal-check cycles graded a class criterion met from a receipt
      that the brief''s own gaps (and in the second cycle my own note) said sampled
      only illustrations; both grades were superseded by measured counterexamples
      in the unsampled remainder. P-03/P-04/P-05/P-13/P-14 did not stop it: none ties
      the verdict to receipt reach. Displaces P-12, the weakest Pattern: its ask-before-choosing-reserved-contract
      rule is already carried by the handoff skill''s decide-or-ask scoping (changes
      to scope or approved contracts always go to the operator).'
  team: distill
  steps_run: 4
  cycles_used: 0
  members:
  - step: distill-qa
    persona: harness-qa
    verdict: PASS
    headline: 5 ops. Craft P15/G15/O10/Open 1->0 (batch c486b80f). Repository Gotchas
      14->15 (batch f3f4dcdf). Archive-tree method and bare-CR probe rejected as already
      covered.
    files_touched:
    - .harness/expertise/harness-qa.md
    - .harness/harness/expertise/harness-qa.md
  - step: distill-code-reviewer
    persona: harness-code-reviewer
    verdict: PASS
    headline: Both class-census candidates merged into a replacement of craft P-08.
      Temp-replay lesson rejected (covered by O-11). Counts unchanged at 15/15/10/0
      (batch b5a4fb48).
    files_touched:
    - .harness/expertise/harness-code-reviewer.md
  - step: distill-security-reviewer
    persona: harness-security-reviewer
    verdict: PASS
    headline: SEC-1 trust-boundary reasoning kept as a replacement of craft P-02,
      in the guarded direction. Path-metadata advisory rejected. Counts unchanged
      at 15/15/10/0 (batch c0351e31).
    files_touched:
    - .harness/expertise/harness-security-reviewer.md
  - step: distill-pm-goalcheck
    persona: harness-pm
    verdict: PASS
    headline: Receipt-reach grading rule replaces craft P-12. It is new beyond P-14.
      Counts unchanged at 15/15/10/0 (batch d250d3fb).
    files_touched:
    - .harness/expertise/harness-pm.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'ui-reviewer was not dispatched: it self-scoped out in every validate cycle and
    has no lesson.'
  - Lead candidate 1 (post-PASS merge covered mechanically) was rejected as Expertise
    because it was a one-off advisor ruling with no governing decision. It is raised
    as OQ-1.
  - Lead candidate 2 (dual severities under P-04) was a confirmation, so no op was
    made. The new lead P-13 (rate divergence direction before severity) is the unlogged
    lesson those escalations rested on.
  - 'Lead batches: craft 7496a7ee (P15/G15/O10/Open0 unchanged); repository 911f64c3
    (P2/G4/O0/Open0 unchanged). I re-read my own file at write time before displacing
    anything.'
  - 'Read-only distillation: no suite was run and no diff was reviewed.'
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
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
  - reader: goalcheck
    status: ran
    persona: harness-pm
    reason: none
  - reader: ui
    status: skipped
    persona: harness-ui-reviewer
    reason: self-scoped out in every cycle; no lesson
```
