# Distillation receipt — harness-dev-ops — FEAT-24

## BLUF

Cold distillation. No observations log this feature — material is my own three prior artifacts plus
the T-06 verify-block receipt, all read before writing. Accepted 2 candidates as new Patterns
(P-08, P-09). Both are tagged `source: lead-relay` — the underlying findings live in my own artifacts,
but I did not independently re-derive them for this distillation; the lead surfaced them by
skimming my digest and I am the sole judge who accepted them as-is. One artifact (T-06 receipt)
yielded no durable candidate — recorded below, not silently skipped.

## Candidates considered

1. **ACCEPTED → P-08** (source: lead-relay, underlying finding from
   `receipt-harness-dev-ops-2026-08-18-1-eng-simp.md` F2; the lead's digest split this into two
   items — the vacuity finding and the cited correct-pattern remedy). I judged them as one rule: the
   remedy IS the action clause of the WHEN/DO, not a separate entry — a pattern naming only the
   failure without the fix would be half a rule, and the distill skill bans instance-listing across
   entries. Passes the six-spawns test: any verify clause anywhere that checks "old text gone"
   without checking "new text present" is the same vacuity, independent of this feature.
2. **ACCEPTED → P-09** (source: lead-relay, underlying finding from
   `receipt-harness-dev-ops-2026-08-19-8-eng-simp.md` Finding 1, digest item 3). Two-part rule:
   locate the exception by adjacent comment not line number (line numbers invalidate under
   cascading deletion), and verify via the ordered SET of ok-line texts, not a count (a count passes
   on a lost-case-masked-by-added-case swap). Both clauses are one rule about verifying a dead-code
   deletion is safe, not two situations, so one entry, not two.
3. **CHECKED, no durable candidate — `receipt-harness-dev-ops-T-06-c1.md`.** This receipt documents
   confirming a `_note` before/after diff and confirming (via `git diff`) that no key outside the
   intended hunk changed. That discipline is already covered by the existing G-07 ("byte-check
   before and after rather than assume") and P-05 (unfiltered git-status capture as evidence) — the
   T-06 receipt is a clean *application* of both, not a new situation. No entry added; the artifact
   was read in full before this conclusion.

No rejections with a "reject, unqualified" verdict — the two lead-relayed findings were accepted as
one merged entry each (P-08 folds two digest items; P-09 folds two clauses of one digest item), and
the third artifact yielded a checked-sound, no-candidate outcome rather than a rejection of a
proposed entry.

## Section counts

| Section | Before | After |
|---|---|---|
| Patterns | 6 (P-02..P-07) | 8 (P-02..P-09) |
| Gotchas | 10 (G-01..G-10) | 10 (unchanged) |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

File: 27 lines of 150-line budget (was 25).

## check-expertise.sh output (final, verbatim)

```
OK   .harness/expertise/harness-dev-ops.md
```

(First run after adding P-09 failed at 55 words, then 52 words — trimmed twice to <=50; final run
above is clean.)

## Layer

Both entries are craft — true of any repository's verify-clause or dead-code-deletion judgement, no
path/decision/invariant specific to this repo. No repository-tier file exists here
(`.harness/harness/expertise/` absent, not in `domain:`), so nothing was routed there. No
repository-specific candidate was found in any of the four artifacts to raise as an open question.
