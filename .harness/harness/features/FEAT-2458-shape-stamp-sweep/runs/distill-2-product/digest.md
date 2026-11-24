# distill-2-product — FEAT-2458 replay-refusal re-judgment (harness-pm)

**BLUF:** Refused batch 67633e70… is superseded by applied batch
`5db615d7d9e6ecda94347a7df7bdd14f31f6a4bb635b5cf6c2b05ae6fd188d3c` (supersedes recorded). pm carried
`replace Gotchas G-14` verbatim and **withdrew** `replace Patterns P-12`; main's P-12 (class-scoped
receipt grading) stands untouched.

- Receipt: `notes/expertise-receipt-717da46e3f400b6f5fc68e86bf172fe8842ee1b0093cc6754fc0ffcffe8eb407.json`
  — one op (G-14 replace), original = the `wc -l` zero-count gotcha, `supersedes: [67633e70…]`.
- Resulting file `.harness/expertise/harness-pm.md`: G-14 holds the receipt text exactly; P-12 is main's text.
- Counts (read from the file; pm did not relay the tool's count object): Patterns 15→15, Gotchas 15→15,
  Outcomes 10→10, Open 0→0.
- The tool did not refuse G-14.

**Reservation (not a send-back, O-03):** pm gave no reason for the withdrawal. The old "unresolved
operator-facing contract" lesson no longer exists under any Patterns id, so withdrawing it drops the
lesson from the file entirely rather than finding it covered. That is a legitimate displace-or-die
outcome at a full section, and the call is pm's.

No diff reviewed, no suite run (distill).

```yaml
VERDICT: PASS
DIGEST:
  headline: 'Refused pm batch 67633e70 superseded by applied batch 5db615d7: G-14
    replace carried verbatim, P-12 replace withdrawn (main''s P-12 kept); counts unchanged
    P 15/15, G 15/15'
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/expertise/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/notes/expertise-receipt-717da46e3f400b6f5fc68e86bf172fe8842ee1b0093cc6754fc0ffcffe8eb407.json
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
  team: product
  steps_run: 1
  cycles_used: 0
  members:
  - step: distill-rejudge
    persona: harness-pm
    verdict: PASS
    headline: 'Re-judged batch 5db615d7 supersedes 67633e70: G-14 replace applied
      verbatim, P-12 replace withdrawn'
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/expertise/harness-pm.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - "New batch id 5db615d7d9e6ecda94347a7df7bdd14f31f6a4bb635b5cf6c2b05ae6fd188d3c;\
    \ receipt notes/expertise-receipt-717da46e\u2026.json records supersedes [67633e70ab0f6a91afa2ccf6aaf5cf181594921125ba5df91e072b62a0029339]\
    \ and one op, with the original G-14 (wc -l zero-count gotcha) matching the earlier\
    \ receipt."
  - 'I read the resulting file: G-14 equals the receipt text; P-12 is still main''s
    ''class-scoped criterion from a receipt'' entry.'
  - "Per-section counts before\u2192after: Patterns 15\u219215, Gotchas 15\u219215,\
    \ Outcomes 10\u219210, Open 0\u21920. I counted these from the file and the one-replace\
    \ receipt because pm did not pass on the tool's count object."
  - 'Reservation, not a send-back: pm gave no reason for withdrawing P-12. The old
    ''unresolved operator-facing contract'' lesson is under no Patterns id, so it
    has been dropped, not found already covered. That is a valid outcome under the
    rule that an entry in a full section either displaces another or is dropped, and
    the call is pm''s.'
  - 'Distill only: no diff was reviewed and no suite was run.'
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/distill-2-product/digest.md
```
