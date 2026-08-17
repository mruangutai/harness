# Distillation — harness-code-reviewer — FEAT-22, D-02-code

**No observations log exists for this persona on this feature** (checked: only
`observations/harness-qa.md` and `observations/harness-validator-lead.md` exist under
`.harness/harness/features/FEAT-22-docs-layout-migration/observations/`). This distillation rests
entirely on a cold skim of two digests and my own two review notes. Cost: no mid-run detail — false
starts, retries, things tried and abandoned — survived to be distilled; only what made it into the
final written notes was available. For this feature that cost was small: both notes are already
dense with counts and file:line citations, not narrative, so little was lost by skipping a hot log
that never existed.

## Sources read

- `runs/2026-08-16-13-panel-validator/digest.md` (the post-build panel I sat in)
- `runs/2026-08-15-5-validator/digest.md` (the pre-build plan-quality panel I sat in)
- `notes/review-harness-code-reviewer-2026-08-16-13-panel-validator.md` (my own)
- `notes/review-harness-code-reviewer-2026-08-15-planpanel.md` (my own)

## Ops applied

1. **replace P-06** (Patterns, full at 15/15, so this is a sharpening not a growth). Old: "report
   deviation from signed text regardless of merit." New folds in C-1's finding technique — re-run
   the signed verify clause itself against HEAD, don't just read the code — because that is how the
   deviation was actually found (`0140dce` silently broke T-03's own signed verify by changing one
   word in a comment; reading the code alone reads as correct). Same slot, same duty-to-report
   clause retained, technique added.
2. **add G-13** (Gotchas 12/15 → 13/15). C-2: a membership assertion (`x in list.split()`) proves
   presence, never exhaustiveness — an extra/unexpected member passes undetected. Judged distinct
   from G-11 (which is about a diff that *replaces* one assertion with several, losing adjacency):
   G-11 is a diff-shape defect, G-13 is a standing property of any membership check regardless of
   how it got there. Both are worth keeping.
3. **add G-14** (Gotchas 13/15 → 14/15). C-3: record an anomalous, unreproducible test result
   rather than smooth it away — recording is what let two independent unreproducible reports (mine
   and security's, same run window, neither aware of the other) converge into one confirmed
   harness-infrastructure defect. Judged distinct from P-15 (dismissing a *candidate finding* you've
   concluded is a non-issue): C-3 is about recording an *observation* you cannot even classify yet,
   before any dismiss/keep judgment is possible.

## Rejected

None of the three relayed candidates were rejected — all three passed the six-spawns-from-now test
and were judged non-redundant against the existing file after direct comparison (see above). No
candidate of my own beyond the three relayed ones surfaced from the skim; the two source notes
were already written for the express purpose of being read later, so they contained little beyond
what the digests already captured.

## Section counts

| Section | Before | After |
|---|---|---|
| Patterns | 15/15 (full) | 15/15 (P-06 replaced, not grown) |
| Gotchas | 12/15 | 14/15 |
| Outcomes | 3/10 | 3/10 (unchanged) |
| Open | 0/5 | 0/5 (unchanged) |

## Verification

`bash .claude/skills/harness/bin/check-expertise.sh .harness/expertise/harness-code-reviewer.md`
→ `OK   .harness/expertise/harness-code-reviewer.md`, exit **0**. No advisory flags.

## Not proposed for repository layer

Nothing in the three candidates turns on a path, file, decision or invariant unique to this one
repository — all three generalize (signed-verify staleness, membership-vs-exhaustiveness, recording
unreproducible anomalies) to any codebase with signed checks, set-membership tests, or flaky
suites. No repository-layer proposal.
