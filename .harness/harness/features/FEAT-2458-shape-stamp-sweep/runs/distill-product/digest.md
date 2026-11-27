# Team digest — FEAT-2458 distill, run distill-product

**PASS: pm applied 2 craft replaces (G-14, P-12) and rejected 1 candidate; product-lead added 1 craft Outcome (O-10). No refusal remains.** All 3 accepted entries come from the skim. None come from a log, because neither pm nor the lead logged observations for this feature (observations/ holds only harness-qa.md, re-checked).

## harness-pm (craft, `.harness/expertise/harness-pm.md`)

Receipt: `notes/expertise-receipt-e318d6ec8d67bb5c5d04005604e0e0edc819bffeb7aca7a436fc991ecf56de99.json`, batch `67633e70…9339`. The lead checked the receipt ops against lines 12 and 26 of the file, and they match.

| Candidate | Source | Result |
|---|---|---|
| 1. The plan's fixture ids contained the asserted token `absent` | plan.yaml:194,245-253; review-harness-qa-c1.md:105-114 | **Accepted.** Replace G-14 (widened into a text-search-discrimination rule) |
| 2. The plan replaced a mechanism the operator named | goalcheck-plan note §fleet-lookup; approval Q-03 | **Accepted.** Replace P-12 (widened from unresolved contracts to named mechanisms) |
| 3. A shared-seam remedy reached the INV-29 callers | goalcheck-plan note §Departures 1; approval Q-04 | **Rejected** "as covered". pm named no covering entry; the lead suspected overlap with P-16 when relaying it |

Counts are P 15→15, G 15→15, O 10→10, Open 0→0. The two replaces do not change any count. pm did not report the counts, so the lead derived them from the file and the ops.

## harness-product-lead (craft, `.harness/expertise/harness-product-lead.md`)

Receipt: `notes/expertise-receipt-809844b7ed6cd572a910334dea7da2be8a33274fa28fda71ba77254c6363bdc4.json`, batch `8e5ad48a…022f`. The add is O-10: when a high plan-reader finding has been applied but never re-read, put it to the operator as a blocking signature question instead of re-spawning the reader. Counts are P 15→15, G 15→15, O 9→10, Open 0→0.

The first attempt was refused (exit 14) because the entry was 51 words. It was shortened and re-applied, and nothing was written by the refused call.

## Not distilled

B-9 (a main-session-direct fix round cannot reach `cycles_used`) is a harness defect, not Expertise (DEC-145). It is already in the ship-review backlog.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/distill-product/digest.md
DIGEST:
  headline: 'Product distill PASS: pm accepted 2 of 3 relayed lessons, both as craft
    rule rewrites (G-14, P-12), and rejected 1; product-lead added craft O-10; all
    3 accepted entries came from the artifact read, none from a log; no refusal remains'
  team: distill
  steps_run: 1
  cycles_used: 0
  members:
  - step: distill-pm
    persona: harness-pm
    verdict: PASS
    headline: pm distill applied 2 craft replaces (G-14 widened to fixture-token collisions,
      P-12 widened to named operator mechanisms); obs 3 rejected as covered; counts
      unchanged at caps
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/expertise/harness-pm.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'harness-pm craft: replace G-14 (Gotchas) and replace P-12 (Patterns), as applied
    in receipt notes/expertise-receipt-e318d6ec8d67bb5c5d04005604e0e0edc819bffeb7aca7a436fc991ecf56de99.json,
    batch 67633e70ab0f6a91afa2ccf6aaf5cf181594921125ba5df91e072b62a0029339. The lead
    checked both entries against lines 12 and 26 of the file, and they match.'
  - 'harness-pm counts: Patterns 15->15, Gotchas 15->15, Outcomes 10->10, Open 0->0.
    pm did not report the counts. The lead derived them from the file and from the
    fact that both ops are replaces.'
  - 'harness-pm rejection: candidate 3 (a panel fix in a shared reader changed behaviour
    for the INV-29 gate callers) was rejected ''as covered''. pm named no covering
    entry; the lead had flagged a likely overlap with P-16 when relaying it. This
    is recorded as given and was not sent back (O-02/O-03).'
  - 'harness-product-lead craft: added O-10 (Outcomes), receipt notes/expertise-receipt-809844b7ed6cd572a910334dea7da2be8a33274fa28fda71ba77254c6363bdc4.json,
    batch 8e5ad48ac8dc4948c675b3124d21a9fe7d080adf1c8e8a4e0957f66e6d24022f. Counts:
    Patterns 15->15, Gotchas 15->15, Outcomes 9->10, Open 0->0. The first apply was
    refused at exit 14 (51 words, over the 50-word cap); the shortened entry was re-applied,
    and the refused call wrote nothing.'
  - 'Accepted entries by source: from an observations log 0 (pm 0, product-lead 0);
    from the artifact read 3 (pm 2, product-lead 1). observations/ holds only harness-qa.md,
    re-checked.'
  - Two of the three relayed candidates restated pm's own plan goal-check note; this
    was flagged to pm in the dispatch (P-04).
  - No repository-tier ops. B-9 (a main-session-direct fix round cannot reach cycles_used)
    is a harness defect already in the ship-review backlog, so it was not distilled
    (DEC-145).
  - 'Files written: craft expertise files .harness/expertise/harness-pm.md and .harness/expertise/harness-product-lead.md;
    their two receipts; runs/distill-product/state.yaml, acceptance.md and digest.md.'
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/expertise/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/expertise/harness-product-lead.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/notes/expertise-receipt-e318d6ec8d67bb5c5d04005604e0e0edc819bffeb7aca7a436fc991ecf56de99.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/notes/expertise-receipt-809844b7ed6cd572a910334dea7da2be8a33274fa28fda71ba77254c6363bdc4.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/distill-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/distill-product/acceptance.md
  expertise_update:
  - persona: harness-pm
    op: replace
    target: G-14
    section: Gotchas
    entry: 'WHEN a verify asserts by text search DO make the match discriminate: a
      fixture id containing the asserted token matches whatever reason prints, and
      an erroring search passes a zero-count test. Name fixtures free of asserted
      tokens; assert the search''s exit status or pair it with a positive control.'
    why: Plan authored fixture ids containing the asserted token; a reason-dropping
      mutant stayed green until validate. Same blind-match family as G-14 (search
      passes regardless), so merged into it rather than displacing a survivor at a
      full section.
  - persona: harness-pm
    op: replace
    target: P-12
    section: Patterns
    entry: "WHEN a task departs from an operator-facing contract \u2014 implementing\
      \ one the operator left unresolved, or swapping a mechanism the operator named\
      \ \u2014 DO keep the settled contract or put the choice, with its measured effect,\
      \ to the operator before signature; otherwise the plan silently overrides the\
      \ operator."
    why: Applied plan replaced the operator's named mechanism with an equivalent walk;
      only goal-check surfaced it as a choice. P-12 covered unresolved contracts only;
      widened to named ones at the same length.
  - persona: harness-product-lead
    op: add
    target: O-10
    section: Outcomes
    entry: "WHEN apply remediates a high plan-reader finding and the team runs no\
      \ re-read step DO put it to the operator as one blocking signature question\
      \ with a recommendation instead of re-spawning the reader \u2014 an overrule-as-applied\
      \ costs no spawn, and the run's FAIL still records the unread gap."
    why: Plan run closed FAIL on an applied-but-unread high finding; the operator
      overruled it as applied at signature and validation later confirmed the remedy
      by execution, so no reader re-spawn was needed.
```
