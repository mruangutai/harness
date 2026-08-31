# FEAT-43 close — harness-ui-reviewer distillation

**Landed in both copies, including a Patterns displacement.** Four entries applied to
`.harness/expertise/harness-ui-reviewer.md`: G-11, G-12, O-05 (pure adds) and a P-09 displacement.
`check-expertise.sh` exits 0 on both the durable main-checkout copy
(`/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-ui-reviewer.md`) and the
worktree copy; a raw `diff` between the two absolute paths is empty (byte-identical).

## Durability correction (mid-run)

I originally wrote only to the worktree copy, per this dispatch's explicit instruction not to
write to main. Lead `Feat43ValidationDistill` flagged that `.harness/expertise/**` is git-tracked,
so the worktree (slated for removal) and the main checkout are two independent copies — a
worktree-only write is lost when the worktree goes. Verified via `git ls-files` (tracked, not
ignored) and a raw diff of both absolute paths. Re-ran `expertise-merge.py apply` against the
absolute main-checkout path with the identical scratch entries — exit 0, 3 ADDED / 29 PRESERVED.

## Relay candidates (both accepted, six-spawns test)

- **C1 → Gotcha G-11.** Generalizes the lead's discriminator ("the only HTML in the feature is a
  generated ship-review report, not product UI") past this feature: a raw extension census
  over-counts generated report/reading-view HTML as in-scope UI. My own two prior notes this
  feature already used the identical footer check to correctly scope these files out.
- **C2 → Outcome O-05.** The lead's stated reason for not spawning — cost of a guaranteed
  "not in scope" spawn — is cheapest when a prior artifact already publishes the census in
  citable form; both source digests show the lead citing exactly this. Distinct from O-01, which
  is about a scoped-out verdict surviving cross-review scrutiny, not about enabling a non-spawn.

## Own candidates

- **Accepted → Gotcha G-12.** Computing exact contrast ratios (WebAIM), not eyeballing hex
  proximity, is what found a real WCAG AA failure in `validate-review-validator.md`; no existing
  entry covered this.
- **Accepted → Patterns P-09 (displaced).** The F-UI-01 lesson — enumerate every outcome bucket a
  status/severity computation can produce, not just the labeled ones, since an unlabeled bucket
  can silently share blocking behaviour with a labeled one — judged stronger and more generally
  applicable than the displaced P-09 (a narrow, single-incident "rewritten error message diagnoses
  a state the feature just made normal" rule). Landed via the apply-to-confirm route: proposing
  the same id with new text against the live file first (exit 7 CONFLICT, nothing applied,
  confirming exact existing text), then a single-line targeted edit of only that bullet (not a
  whole-file rewrite) on both copies, then `check-expertise.sh` on both — exit 0 both times.
- **Rejected (own).** The duplicated `validate-digest.py` binding-error line (two call paths
  converging on one error producer) sits in code-reviewer's call-path-tracing lens, not this
  role's remit; a narrow one-off unlikely to recur unchanged across repos.

## Section counts (both copies, identical)

| Section | Before | After |
|---|---|---|
| Patterns | 15 | 15 (P-09 text replaced, count unchanged) |
| Gotchas | 10 | 12 |
| Outcomes | 4 | 5 |
| Open | 0 | 0 |

37/150 lines. Repository-layer file untouched — nothing distilled this feature turns on this one
repository rather than the craft.

## Commands run

- Read own three named notes plus both relay digests in full.
- `expertise-merge.py apply` (worktree, then main) — exit 0 each, 3 ADDED (G-11, G-12, O-05).
- `expertise-merge.py apply` (main, P-09 same-id-new-text) — exit 7 CONFLICT, confirmed, nothing
  applied (apply-to-confirm step).
- Targeted single-line edit of the P-09 bullet only, on both absolute copies.
- `check-expertise.sh` on both copies — exit 0 each; raw `diff` of both — empty.
- One throwaway empirical test (created and deleted, never tracked) confirming `apply`'s
  same-id-different-text behaviour before the apply-to-confirm route was relayed by the lead.
