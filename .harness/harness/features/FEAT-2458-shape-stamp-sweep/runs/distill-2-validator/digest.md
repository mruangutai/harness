# FEAT-2458 · distill-2-validator · replay re-judgment

**BLUF: BLOCKED. One of the two refused batches is superseded. The other cannot be superseded within this dispatch's rules.**

## 1. harness-validator-lead (craft): superseded, applied
- Refused batch `3786913f…` is superseded by **`d413ad93fa684e606906a5086ac24ed6d5a984fa0cfdf53f24a0fefda81611d4`**. Receipt: `notes/expertise-receipt-6c130f0c659e1b0d39f18babcd7db18ea763a99484ae789d2cdc225a4215f886.json`.
- G-06 replace: carried over unchanged, with the same op, target, section, entry and why.
- O-02 replace: re-judged and kept. Main has fixed the doubled `O-02: ` prefix, but the displaced text is still an implementation rule that other personas already hold, not a lead outcome. The entry is unchanged. Only the `why` was reworded to drop the "malformed" premise.
- Counts: Patterns 15→15, Gotchas 15→15, Outcomes 10→10, Open 0→0. I re-read the file: G-06 and O-02 hold the new text.

## 2. harness-qa (repository tier, segment harness): not superseded
- qa withdrew its G-13 replace. Main's G-13 already covers redirect, cp and rm with variable targets, and cleanup through a python driver.
- `expertise_apply` refused the verbatim `add G-15 Gotchas` with exit 7: `CONFLICT section=Gotchas id=G-15`. Nothing was written. The receipt for refused batch `64c836f8…` still stands.
- I checked the file myself. Main now holds a different G-15 (the check-integration-shards `discover_expected` tuple), and Gotchas is at 15/15. So even if the add were renumbered, it would hit the cap (exit 8).
- The dispatch said to carry the op verbatim and not to improvise around a refusal. Landing it would mean re-judging an op outside the refused one: either displacing a weaker gotcha or withdrawing the add. That decision needs authorization from the tier above.

```yaml
VERDICT: BLOCKED
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/distill-2-validator/digest.md
DIGEST:
  headline: 'Validator-lead''s refused batch 3786913f is superseded by d413ad93 (G-06
    carried over unchanged, O-02 kept). qa''s batch 64c836f8 is not superseded: the
    unchanged add G-15 was refused with exit 7 CONFLICT, and Gotchas is full at 15/15.
    qa withdrew its G-13 replace.'
  open_questions:
  - id: Q-1
    question: 'The superseding batch for qa''s 64c836f8a187d67f59ef7bbaf0e6416428db7e25ea767de1dd2a0aa8c5b5441c
      cannot carry its unchanged `add G-15 Gotchas`. The tool refused it with exit
      7 `CONFLICT section=Gotchas id=G-15`: main now holds a different G-15, the check-integration-shards
      discover_expected tuple. Gotchas in .harness/harness/expertise/harness-qa.md
      is also 15/15, so a renumbered add would fail on the cap with exit 8. qa withdrew
      G-13 because main''s G-13 already says it. To land, either (a) authorize qa
      to re-judge the G-15 add too, displacing a weaker gotcha or merging, or (b)
      authorize an empty withdrawal of the whole batch. Which one?'
    blocking: true
  files_touched:
  - .harness/expertise/harness-validator-lead.md
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/distill-2-validator/state.yaml
  expertise_update:
  - persona: harness-validator-lead
    op: replace
    target: G-06
    section: Gotchas
    entry: "WHEN a real finding's only remedy edits a file in no task's declared set,\
      \ or amends signed intent or criterion wording, DO route it up \u2014 ESCALATE\
      \ if it gates, an open question if not \u2014 never must_fix: no fix cycle may\
      \ legally apply it."
    why: Two cycle-1 reader findings were real but their remedies rewrote a signed
      task intent and a signed criterion's marker; routing them as open questions
      instead of must_fix kept the fix round on the test-only defects. Generalizes
      G-06's file-set case to signed-wording remedies.
  - persona: harness-validator-lead
    op: replace
    target: O-02
    section: Outcomes
    entry: "WHEN a must-fix restructures tests to clear a structural gate DO put 'every\
      \ predicate still rejects what it rejected before' in its acceptance \u2014\
      \ gate exit 0 and an unchanged PASS-name set both held while a string check\
      \ collapsed to truthiness, caught only a cycle later."
    why: 'The complexity-driven split cleared code-grade with identical PASS-name
      sets yet weakened a reason check to bool(); only the next panel''s code-reviewer
      probe found it. Re-judged against main: O-02''s doubled prefix is gone, but
      its content remains an implementation rule other personas already hold, not
      a lead outcome, so the displacement still stands.'
  team: validate
  steps_run: 2
  cycles_used: 0
  members:
  - step: rejudge-validator-lead
    persona: harness-validator-lead
    verdict: PASS
    headline: 'Superseding batch d413ad93fa684e606906a5086ac24ed6d5a984fa0cfdf53f24a0fefda81611d4
      applied (receipt notes/expertise-receipt-6c130f0c659e1b0d39f18babcd7db18ea763a99484ae789d2cdc225a4215f886.json).
      G-06 carried over unchanged. O-02 kept with a reworded why. Counts are unchanged:
      Patterns 15, Gotchas 15, Outcomes 10, Open 0.'
    files_touched:
    - .harness/expertise/harness-validator-lead.md
  - step: rejudge-qa
    persona: harness-qa
    verdict: BLOCKED
    headline: G-13 withdrawn because main already covers it. The unchanged add G-15
      was refused with exit 7 CONFLICT, so nothing was written and repository-tier
      harness-qa.md is unchanged (Gotchas 15/15).
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - "Validator-lead counts before\u2192after: Patterns 15\u219215, Gotchas 15\u2192\
    15, Outcomes 10\u219210, Open 0\u21920. I re-read the file and the receipt: G-06\
    \ and O-02 hold the new text."
  - 'I checked qa''s refusal account against the file myself (O-10): G-15 on main
    is a different entry and Gotchas is at its 15-entry cap, which is consistent with
    the CONFLICT. qa''s repository-tier counts are unchanged: Gotchas 15, other sections
    0.'
  - The skill says a replayed add with a colliding id is renumbered automatically.
    Even so, qa's G-15 add would overflow the Gotchas cap, so the replay would refuse
    it either way.
  - 'Approval needed (Q-1): whether qa may re-judge the G-15 add, or withdraw batch
    64c836f8 entirely.'
  sc_status: []
  needs_approval: true
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
  readers:
  - reader: rejudge-validator-lead
    status: ran
    persona: harness-validator-lead
    reason: none
  - reader: rejudge-qa
    status: ran
    persona: harness-qa
    reason: none
```

---

# Resume after Q-1 answer · rejudge-qa-2

**BLUF: PASS. Both refused batches are now superseded. qa's 64c836f8 is superseded by an applied empty withdrawal; Q-1 is closed.**

- Superseding batch: **`966b4383daf79fd9e3605c2afcf8512f79f514a2212c81f36f6449b2775dd65e`**, `ops: []`, `supersedes: [64c836f8…]`. Receipt: `notes/expertise-receipt-6e31e6b949eacd165727608327c7e4c7db23614775a55af801abc54d0ccae126.json`. I read it: before_sha256 equals after_sha256 (`eacace99…`), so nothing was written.
- G-13 replace: still withdrawn. Main's G-13 already says it.
- Former `add G-15` (CANONICAL_READER_CASES self-test flag): qa judged that no current Gotchas entry is weaker, so the lesson dies under the distill skill's full-section rule. I checked qa's supporting claim: qa's craft P-14 in the feature tree already holds the flag-gated-registry rule ("a glob match or flag-gated registry reports satisfied while never running"). The lesson survives in craft form, so nothing is lost.
- I re-read `.harness/harness/expertise/harness-qa.md`. It is unchanged: Gotchas 15/15 (G-01..G-15, main's G-15 intact), Patterns 0, Outcomes 0, Open 0.
- Validator-lead batch d413ad93 stands as applied. It was not re-applied or re-judged.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2458-shape-stamp-sweep/.harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/distill-2-validator/digest.md
DIGEST:
  headline: 'Both refused batches are superseded. qa''s 64c836f8 is superseded by
    the applied empty withdrawal 966b4383: G-13 stays withdrawn, and the G-15 lesson
    dies because no Gotchas entry is weaker and qa''s craft P-14 already holds it.
    Validator-lead''s d413ad93 stands. Q-1 is closed.'
  open_questions:
  - id: Q-2
    question: 'The acceptance asked for this digest''s expertise_update to list my
      already-applied d413ad93 ops (G-06, O-02). The digest gate refuses them: they
      ''match no applied receipt of this run or its children'', because the gate binds
      to this resumed runtime and d413ad93 was applied by my earlier runtime. Those
      ops are recorded as applied in the earlier digest block of this run''s digest.md,
      and their receipt is notes/expertise-receipt-6c130f0c659e1b0d39f18babcd7db18ea763a99484ae789d2cdc225a4215f886.json.
      Should the distill record take them from there, or should the gate accept receipts
      from an earlier runtime of the same open run?'
    blocking: false
  files_touched:
  - .harness/harness/features/FEAT-2458-shape-stamp-sweep/runs/distill-2-validator/state.yaml
  expertise_update: []
  team: validate
  steps_run: 1
  cycles_used: 0
  members:
  - step: rejudge-qa-2
    persona: harness-qa
    verdict: PASS
    headline: "Applied empty withdrawal 966b4383daf79fd9e3605c2afcf8512f79f514a2212c81f36f6449b2775dd65e\
      \ superseding 64c836f8 (receipt notes/expertise-receipt-6e31e6b949eacd165727608327c7e4c7db23614775a55af801abc54d0ccae126.json).\
      \ Gotchas 15\u219215, other sections 0\u21920."
    files_touched: []
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - "I read qa's receipt 6e31e6b9\u2026: batch 966b4383 has ops [] and supersedes\
    \ [64c836f8a187d67f59ef7bbaf0e6416428db7e25ea767de1dd2a0aa8c5b5441c]. Its before_sha256\
    \ equals its after_sha256 (eacace99\u2026)."
  - 'I re-read .harness/harness/expertise/harness-qa.md. It is unchanged: Gotchas
    G-01..G-15 (main''s G-15 intact), and Patterns, Outcomes and Open are all 0.'
  - qa applied no ops (an empty withdrawal), so it contributes nothing to expertise_update.
  - "Validator-lead batch d413ad93fa684e606906a5086ac24ed6d5a984fa0cfdf53f24a0fefda81611d4\
    \ (G-06 replace, O-02 replace) stands as applied in the earlier block of this\
    \ run, receipt notes/expertise-receipt-6c130f0c\u2026.json. It was not re-applied.\
    \ The gate refused it in this return's expertise_update (see Q-2)."
  - Earlier step rejudge-qa (BLOCKED, exit 7) is resolved by rejudge-qa-2. Both are
    recorded in state.yaml.
  - 'I checked qa''s reason for letting G-15 die: P-14 in the qa craft file in the
    feature tree does cover flag-gated registries that never run. The lesson is kept
    in craft form.'
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
  readers:
  - reader: rejudge-qa-2
    status: ran
    persona: harness-qa
    reason: none
```
