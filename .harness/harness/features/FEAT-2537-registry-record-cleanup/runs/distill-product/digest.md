# FEAT-2537 distill — product squad (run distill-product)

**BLUF: PASS.** pm accepted all three relayed candidates. The writes were 2 craft replaces, plus 1 repository replace, 1 drop and 1 add. I applied 2 craft replaces of my own. There are no refusals left: pm's one exit-14 (an entry over 50 words) was trimmed and re-applied, and the refused attempt wrote nothing. No section is over its cap.

## Member — distill-pm (harness-pm): PASS
Artifact: `notes/research-FEAT-2537-registry-record-cleanup-distill.md`. Receipt: `notes/expertise-receipt-962af8f1….json`. The receipt holds both batches, and I checked them against the resulting files.

- **Repository (harness), batch `ad4e4eb5…`:**
  - G-05 replaced. It absorbs G-10, which covered the same `check-plan-routes.py` argument rule.
  - G-10 dropped.
  - G-16 added (C1): a `decisions_affected` clause must be an exact substring, so a wrapped clause needs a literal `\n`.
  - Counts: P 12→12, G 15→15, O 2→2, Open 0→0. The file is 34/40 lines.
- **Craft, batch `95fef527…`:**
  - P-11 replaced (C2): when a plan removes an input-accepting branch, enumerate what it actually accepted, including the vacuous and data-carrying instances, and give each signed delta a test witness. It displaces the old P-11, which duplicated a preloaded harness-brief red flag.
  - G-06 replaced (C3): a decoded or normalized comparison against a bytes clause grades partial.
  - Counts: P 15→15, G 15→15, O 10→10, Open 0→0.

**Assessment.** The send-back criteria (`sendback-criteria.md`, written before dispatch) are all met. Every entry is in WHEN/DO form, at most 50 words, and carries no IDs. Layers are correct. Each add displaced a named survivor.

One reservation, left standing under O-03. G-06 drops the original-entry passthrough sub-clause, and that is a small loss of specificity.

## Lead's own (craft, batch `712fa70f…`)
- **P-14 replaced.** It absorbs G-11; both are about grepping for a token rather than a phrase.
- **G-11 replaced with a new lesson.** When you characterize a behaviour delta in a signature question, test it on a data-carrying instance, not the minimal example. My plan digest called the malformed-v2 writer delta "stderr-only" from a rowless example. The signoff inherited that as "bytes identical", and the c0 ruling had to correct it.
- Counts: P 15→15, G 15→15, O 10→10, Open 0→0. Repository tier: nothing to add.

## Not dispatched
visual-designer and documentor did not run on this feature, so they have no logs and no lessons.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/runs/distill-product/digest.md
DIGEST:
  headline: FEAT-2537 product distill is complete with no refusal remaining. pm accepted
    all 3 relayed candidates (craft P-11 and G-06 replaced; repo G-05/G-10 merged
    and G-16 added). The lead merged P-14/G-11 and added a gotcha on testing a delta's
    characterization against a data-carrying instance. All sections are within cap.
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/expertise/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/expertise/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/expertise/harness-product-lead.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/notes/research-FEAT-2537-registry-record-cleanup-distill.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/runs/distill-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/runs/distill-product/sendback-criteria.md
  expertise_update:
  - persona: harness-pm
    op: replace
    target: G-05
    section: Gotchas
    entry: 'WHEN running check-plan-routes.py DO pass your own plan.yaml FILE: with
      no argument it reports every live plan, so other features'' DEVIATION lines
      read as yours, and handed a directory it raises IsADirectoryError and exits
      1, which reads as a gate failure rather than a bad argument.'
    why: Merges G-10 into G-05 (same script, same argument rule) to free a Gotchas
      slot; no longer than the longer input.
  - persona: harness-pm
    op: drop
    target: G-10
    section: Gotchas
    why: Absorbed into G-05.
  - persona: harness-pm
    op: add
    target: G-16
    section: Gotchas
    entry: 'WHEN quoting a decisions_affected clause that wraps across a DECISIONS.md
      line break DO write it as a double-quoted scalar with a literal \n at the break:
      plan-merge check requires the clause as an exact substring of the decision''s
      section, newlines included, so a space-joined wrap fails as not verbatim.'
    why: Own log bullet 1; confirmed at control plane plan_merge/check.py _rows_faults
      (str(clause) not in section). Repository-specific gate behaviour.
  - persona: harness-pm
    op: replace
    target: P-11
    section: Patterns
    entry: WHEN a plan removes a branch that accepts a class of inputs DO enumerate
      what its predicate actually accepted, including the vacuous instance and data-carrying
      instances, not only the minimal example, and require a case-level test witness
      per signed behaviour delta before signature; otherwise deltas surface only by
      validation probes.
    why: 'Own log bullets 2-3 and both rulings'' Gap: the empty instance was caught
      at intake, the row-carrying foreign-version instance escaped to validate untested.
      Displaces P-11, which duplicates the preloaded harness-brief red flag (an SC
      quantifying over more than the work can touch).'
  - persona: harness-pm
    op: replace
    target: G-06
    section: Gotchas
    entry: 'WHEN a predicate or criterion names raw input, bytes or exact output DO
      treat decoded, parsed, trimmed or newline-normalized forms as a different clause:
      specify which form is contractual, require a case where normalization changes
      the outcome, and grade a normalized comparison partial, never adequate by argument.'
    why: My goal-check called a json.loads comparison 'adequate' for a bytes clause;
      the c1 ruling found a text-mode read let a CRLF mutant pass, costing an escalation.
      Sharpens G-06 to cover grading as well as specifying; drops its narrow passthrough
      sub-clause; same length.
  - persona: harness-product-lead
    op: replace
    target: P-14
    section: Patterns
    entry: "WHEN checking whether a member folded your instructions in DO grep one\
      \ distinctive token of the fact each names \u2014 the cited line, the identifier\
      \ \u2014 never your own wording or a multi-word phrase: members rephrase and\
      \ line wraps split phrases, so either grep reports absent what is there."
    why: 'Absorbs G-11 (line-wrapped phrase grep) into P-14 (phrasing grep): same
      check, same failure, one rule; no longer than the longer input. Frees a Gotchas
      slot.'
  - persona: harness-product-lead
    op: replace
    target: G-11
    section: Gotchas
    entry: "WHEN you characterize a behaviour delta in a signature question DO test\
      \ the claim on a data-carrying instance of the shape, not only the minimal example\
      \ \u2014 a delta reasoned from an empty instance reads as harmless, and the\
      \ signer inherits the overgeneralization as a ruling."
    why: My plan digest called the malformed-v2 writer delta stderr-only from a rowless
      example; the signoff repeated it as bytes-identical, and the c0 ruling had to
      correct it after row-carrying envelopes were shown to lose live rows. Old G-11
      is absorbed into P-14.
  team: distill (product squad)
  steps_run: 1
  cycles_used: 0
  members:
  - step: distill-pm
    persona: harness-pm
    verdict: PASS
    headline: "Accepted C1\u2013C3. Repo: G-05 absorbed G-10 and G-16 was added (P\
      \ 12\u219212, G 15\u219215, O 2\u21922, Open 0\u21920; 34/40 lines). Craft:\
      \ P-11 and G-06 replaced (P 15\u219215, G 15\u219215, O 10\u219210, Open 0\u2192\
      0). One exit-14 refusal (P-11 over 50 words) was trimmed and re-applied. No\
      \ diff reviewed and no suite run."
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/expertise/harness-pm.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/expertise/harness-pm.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/notes/research-FEAT-2537-registry-record-cleanup-distill.md
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - 'Distill dispatch: no diff was reviewed and no suite was run.'
  - "I checked every pm op against receipt expertise-receipt-962af8f1\u2026json (batches\
    \ ad4e4eb5\u2026 and 95fef527\u2026) and against both resulting files. All 6 send-back\
    \ criteria, written before dispatch, are met."
  - "Lead's own craft batch is 712fa70f\u2026 (receipt expertise-receipt-2c4347df\u2026\
    json). Counts are P 15\u219215, G 15\u219215, O 10\u219210, Open 0\u21920. There\
    \ was no lead repository-tier lesson."
  - 'Reservation, left standing per O-03: pm''s G-06 replacement drops the original-entry
    passthrough sub-clause.'
  - visual-designer and documentor did not run on FEAT-2537 and kept no logs, so neither
    was dispatched.
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
  readers: []
```
