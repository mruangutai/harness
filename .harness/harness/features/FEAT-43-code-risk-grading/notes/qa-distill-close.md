# QA Expertise distillation — feature close, FEAT-43

**BLUF:** Two of three relay candidates accepted, both by displacing a weaker capped entry (P-15,
O-05); the third accepted as a strengthening merge into its target (G-15). All three sections
(Patterns/Gotchas/Outcomes) were already at cap, so `expertise-merge.py apply` correctly refused
each with exit 7 (same id, different text) — nothing applied by the tool, as designed. Resolved
per the documented exit-7 path: since the tool has no replace/drop primitive (confirmed by reading
`compute_union` — it only unions, never removes), the deliberate displacement was applied as a
targeted single-line `edit` on each of the three named lines, not a whole-file write. No own-note
candidate beyond the three relayed ones passed the six-spawns test without duplicating existing
entries (checked against qa-delta-c29/mergedelta/c28/c27/c26 — c29's and mergedelta's own lessons
are exactly C3 and C1 respectively, already covered by the accepted entries below; c28/c27/c26
sampled and found already subsumed by existing Patterns/Gotchas, e.g. P-06/P-09/G-13).

## Candidates judged

- **C1 (relay) — ACCEPTED, replaces P-15.** Merge-regression attribution must be measured per
  parent commit in an isolated clone, never inferred from a test file's byte-identity across refs.
  Generalizable (no repo token), high-value: this is exactly the failure my own `qa-mergedelta.md`
  made and had to send back. P-15 (a narrow matrix-floor procedural note) judged weaker — single
  scenario, lower recurrence value than a core attribution methodology error.
- **C2 (relay) — ACCEPTED via merge into G-15.** "Green re-run is not proof of a fix when the
  threshold is live-tree state" sharpens G-15's existing "flag it as a latent flake" framing with
  the actionable corrective (verify the changed assertion's logic directly, not the rerun). Kept
  under G-15's id since it strengthens the same rule rather than introducing a distinct one — a
  true `add` would have duplicated G-15's scope.
- **C3 (relay) — ACCEPTED, replaces O-05.** A callsite where only the target guard fires proves the
  guard load-bearing; a site with a second independent failure proves nothing about the guard
  specifically — this is my own `qa-delta-c29.md` Mutation-B finding, generalized. O-05 (Phase-1
  coverage-match anti-bias check) judged weaker — narrower applicability (fires only when Phase 1
  happens to match the built suite almost exactly) than a general mutation-interpretation rule.

## Mechanism note

`expertise-merge.py apply --file .harness/expertise/harness-qa.md --entries <scratch>` was run
first with all three proposed replacement texts under their existing ids; it correctly reported
three `CONFLICT` lines and exited 7, applying nothing (confirmed: file unchanged before the
resolve). Read `compute_union` in `expertise-merge.py` — it is additive-only, no replace/drop op
exists in the tool, so exit 7 for an intentional distillation-time displacement is the documented
"resolve it yourself" case, not a concurrent-writer accident. Resolved with a single-line `edit`
per target (P-15, G-15, O-05), never a whole-file write. `check-expertise.sh` confirms the result
is well-formed.

```yaml
VERDICT: PASS
DIGEST:
  headline: Distilled 3 relay candidates into harness-qa craft Expertise (2 replace, 1 merge), all sections at cap resolved via targeted single-line edits after the merge tool's documented exit-7 refusal; check-expertise.sh exits 0.
  expertise_update:
    - { op: replace, target: P-15, section: Patterns, entry: "WHEN attributing a failing test as a merge regression DO run it at each parent commit in an isolated clone or worktree, not infer from the test file's byte-identity across refs — a test whose subject is the surrounding tree regresses with no change to its own source.", why: "relay C1 — a real attribution error in my own mergedelta review; generalizable methodology, displaces a narrower single-scenario matrix-floor note" }
    - { op: merge, target: G-15, section: Gotchas, entry: "WHEN a verify clause asserts a property against a live, mutable corpus rather than a pinned fixture DO treat a green re-run as no proof of a fix — the threshold can flip from unrelated state changes alone — and instead verify the changed assertion's logic directly.", why: "relay C2 — sharpens G-15's existing flake-flagging framing with the actionable corrective; same rule, not a distinct one" }
    - { op: replace, target: O-05, section: Outcomes, entry: "WHEN a mutation trips two independent failures at one callsite DO identify the site where only the target guard fires — a callsite where the guard is the sole detector proves it is load-bearing; a site with a second independent failure proves nothing about the guard specifically.", why: "relay C3 — my own delta-c29 Mutation-B finding, generalized; displaces a narrower Phase-1-match-only anti-bias check" }
  candidates_accepted: { relay: 3, own: 0 }
  candidates_rejected:
    relay: []
    own: []
  section_counts_before:
    .harness/expertise/harness-qa.md: { Patterns: 15, Gotchas: 15, Outcomes: 10, Open: 1 }
  section_counts_after:
    .harness/expertise/harness-qa.md: { Patterns: 15, Gotchas: 15, Outcomes: 10, Open: 1 }
  check_expertise:
    .harness/expertise/harness-qa.md: 0
  open_questions: []
  files_touched: [.harness/expertise/harness-qa.md]
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-distill-close.md
```
</content>
