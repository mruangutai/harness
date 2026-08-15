# Distillation — harness-code-reviewer — FEAT-20-migration-detector — c0

Cold pass over my own panel note (`notes/review-harness-code-reviewer-c0.md`) plus three
lead-relayed candidates. I am sole judge; the caller applies the ops verbatim.

## Section fill

| Section | Before | After |
|---|---|---|
| Patterns | 15/15 | 15/15 (unchanged) |
| Gotchas | 7/15 | 8/15 |
| Outcomes | 0/10 | 2/10 |
| Open | 0/5 | 0/5 (unchanged) |

## Accepted

**O-01 (Outcomes, source: relay, candidate 1 — mutant-liveness proof).** Six-spawns test: yes —
any future coverage-gap claim built on a hand-constructed mutant benefits from the same discipline.
Placed in Outcomes, not Patterns: this is a validated *methodology for the reviewer's own
demonstration*, the shape every populated Outcomes section in the tree already holds (orchestrator,
qa, validator-lead — event-confirmed practices), not a rule about what to check in reviewed code.
No overlap with P-12: P-12 governs judging whether a *test in the codebase under review* has
discriminating proof; O-01 governs how *I* prove my own mutant is live before using it as evidence.
Complementary, not duplicate — no displacement needed.

**O-02 (Outcomes, source: relay, candidate 3 — trace a false claim to its origin before
attributing).** Six-spawns test: yes — generalizes past this feature's DEC-194/plan-text specifics.
Considered as a Pattern first, since it touches verification-against-source like P-03; rejected that
placement because P-03 already fully covers "verify the record against the code it names" and
adding a second entry for the same act would be padding, not sharpening — condensing candidate 3
into P-03 would also lose its distinct payload (once falsified, the remedy's *scope* depends on
where the error originates, and an independent cross-check from a different role can confirm that
scope). That payload is event-validated, not a general verification rule, so it belongs in Outcomes.
No existing Pattern is weaker than P-03 in a way that candidate 3 could displace — this is a
placement judgment, not a displacement one.

**G-08 (Gotchas, source: relay, candidate 2 — line-anchor drift from own notes).** Six-spawns test:
yes — this is a habit correction distinct from G-01 (G-01 is about reading pinned-SHA bytes over
working-tree state; G-08 is about my own recall drifting from what I originally read, independent of
which SHA). Under cap, no displacement needed.

## Rejected — with reasons

- **F3 (duplicated blame-selection logic across two call sites), source: own-artifact.** Not added.
  "Copy-paste divergence" is already named explicitly as a Stage 2 hunting target in
  `harness-code-review` itself — the observation is a correct application of an already-preloaded
  rule, not a new one. An Expertise entry restating a rule already in the skill is padding.
- **F4 (first-match-wins cause priority can mask a co-occurring second cause), source: own-artifact,
  also implicitly considered as relay since the lead's dispatch read my full note.** Not added. My
  own note filed it "info, not actionable" and tied it to a signed design bound (D-03's per-file
  residual), and the lead's relay list did not surface it independently. The evidence supports only
  "this occurred once and did not change the verdict" — not a rule that would change future behavior.
  Recording the weakest statement the evidence supports here means: no entry.
- **Q1 (bash-write-guard blocked scratchpad shell writes contrary to the dispatch's SHELL NOTE),
  source: own-artifact.** Not added. This is a harness defect — a tool that behaved differently from
  what the dispatch promised — which `harness-expertise` places in `open_questions`, never Expertise,
  because a workaround recorded here outlives the fix. Already correctly routed as Q1 in the prior
  panel digest; no further action here.

## Ops

```yaml
expertise_update:
  - op: add
    section: Outcomes
    entry: "WHEN reporting a coverage gap via a hand-built mutant DO add one non-shipped probe case that fails on it before reporting the shipped suite passes — an executed failing probe distinguishes a real gap from an unexecuted claim, usually a broken harness."
    why: "relay candidate 1 — self-demonstrated methodology, six-spawns test passes, no overlap with P-12 (which governs judging reviewed-code tests, not the reviewer's own mutant)."
  - op: add
    section: Outcomes
    entry: "WHEN a downstream artifact states something false DO trace it to its authoring source before attributing the error — the nearest producer may have faithfully reproduced an upstream defect, and the correct remedy fixes the origin too, not just the surface where it was found."
    why: "relay candidate 3 — event-validated by an independent cross-check (a separate role reached the same root cause), distinct payload from P-03 (verify-against-code) which already covers detection; this covers remedy scope after detection."
  - op: add
    section: Gotchas
    entry: "WHEN citing file:line anchors from memory or your own notes DO re-verify each against source before publishing rather than trust recall — anchors can drift several lines even when the underlying claim is correct, so mark all approximations consistently or verify every one."
    why: "relay candidate 2 — distinct failure mode from G-01 (pinned-SHA vs working tree); this is recall drift independent of which SHA was read."
```

```yaml
VERDICT: PASS
DIGEST:
  headline: "Distilled 3 accepted ops (2 Outcomes, 1 Gotcha) from 3 lead-relayed candidates; rejected 3 candidates with reasons; Patterns left untouched at 15/15."
  severity_max: n/a
  findings: 0
  must_fix: []
  spec_violations: []
  reviewed: "none"
  human_commits_in_scope: []
  open_questions: []
  files_touched: [.harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-distill-c0.md]
  expertise_update:
    - op: add
      section: Outcomes
      entry: "WHEN reporting a coverage gap via a hand-built mutant DO add one non-shipped probe case that fails on it before reporting the shipped suite passes — an executed failing probe distinguishes a real gap from an unexecuted claim, usually a broken harness."
      why: "relay candidate 1 — self-demonstrated methodology, six-spawns test passes, no overlap with P-12 (which governs judging reviewed-code tests, not the reviewer's own mutant)."
    - op: add
      section: Outcomes
      entry: "WHEN a downstream artifact states something false DO trace it to its authoring source before attributing the error — the nearest producer may have faithfully reproduced an upstream defect, and the correct remedy fixes the origin too, not just the surface where it was found."
      why: "relay candidate 3 — event-validated by an independent cross-check (a separate role reached the same root cause), distinct payload from P-03 (verify-against-code) which already covers detection; this covers remedy scope after detection."
    - op: add
      section: Gotchas
      entry: "WHEN citing file:line anchors from memory or your own notes DO re-verify each against source before publishing rather than trust recall — anchors can drift several lines even when the underlying claim is correct, so mark all approximations consistently or verify every one."
      why: "relay candidate 2 — distinct failure mode from G-01 (pinned-SHA vs working tree); this is recall drift independent of which SHA was read."
  cycles: 0
artifact: .harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-distill-c0.md
```
