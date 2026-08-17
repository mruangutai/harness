# Receipt — harness-dev-ops — FEAT-22 distillation (S-02)

BLUF: added 3 new Gotchas (G-08, G-09, G-10) to the craft-layer Expertise file, all self-derived
from my own three receipts this feature. No observations log existed (checked, absent). All three
lead-relayed digest-skim candidates were accepted verbatim-in-substance — none rejected, no cap
pressure, no displacement needed. Checker clean across the whole directory.

## Source material

No `observations/harness-dev-ops.md` exists for FEAT-22 — confirmed absent before starting, per
dispatch. All material came from my own three receipts:
- `notes/receipt-harness-dev-ops-2026-08-15-2-archreview-eng.md` (M-1: `git show --name-only`
  rename behavior)
- `notes/receipt-harness-dev-ops-2026-08-15-s02e.md` (Measurement 1: same rename-only fact,
  cross-checked on a bigger commit; Measurement 3: `audit-decisions.py` exits 0 despite findings)
- `notes/receipt-harness-dev-ops-2026-08-16-arch-refire.md` (awk fixture probe: whitespace-collapse
  clause false-REDs on interior markup, 3/6 headed variants)

## Candidates considered

The lead's three digest-skim candidates map 1:1 onto my own receipts (the lead skimmed the same
material I hold). I treat all three as **self-derived (c)**, not digest-relay (b): I re-derived each
independently from the primary receipt rather than taking the lead's phrasing, and the dispatch says
a self-derived candidate from my own receipts counts fully as (c). No independent digest-only
candidate existed beyond what my receipts already contained, so (b) = 0 by construction this run.

1. **Accepted → G-08.** `--name-only` prints only the destination path on a rename; `--name-status`
   carries both. Passes the six-spawns test: general git behavior, relevant to any verify script
   scanning diff output for renamed files in any repo.
2. **Accepted → G-09.** Whitespace-collapsing `awk`/`gsub` clauses false-RED when markup (bold,
   code span, blockquote prefix) lands inside the matched phrase. Passes: general lesson about
   testing prose-matching verify clauses against markup-variant fixtures, applicable wherever such
   clauses get written.
3. **Accepted → G-10.** Generalized from `audit-decisions.py`: a script's exit code is not
   evidence of its findings' outcome unless measured — reading for `sys.exit()` in source is not a
   substitute. Judged this as **one rule adjacent to, but distinct from, G-06**: G-06 is about a
   CLI author's own decision to normalize away meaningful exit codes; this one is about assuming an
   exit code encodes a result at all, discovered only by running the tool. Kept both — different
   failure mode, no overlap that would make one redundant.

No self-derived or relayed candidate was rejected this run — all three passed the test and there was
no cap pressure (Gotchas at 7/15 before, room for more).

## Section counts

| Section | Before | After |
|---|---|---|
| Patterns | 3 | 3 |
| Gotchas | 7 | 10 |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

## Accepted/rejected by source

- (a) observations log: 0 candidates (log did not exist)
- (b) digest-skim relay (lead's phrasing, distinct from my own derivation): 0 — see reasoning above,
  all three collapsed into (c)
- (c) self-derived from own receipts: 3 accepted, 0 rejected

## Checker

Ran verbatim: `bash .claude/skills/harness/bin/check-expertise.sh .harness/expertise/`

```
OK   .harness/expertise/harness-backend-dev.md
OK   .harness/expertise/harness-code-reviewer.md
OK   .harness/expertise/harness-dev-ops.md
OK   .harness/expertise/harness-documentor.md
OK   .harness/expertise/harness-eng-lead.md
OK   .harness/expertise/harness-orchestrator.md
OK   .harness/expertise/harness-pm.md
OK   .harness/expertise/harness-product-lead.md
OK   .harness/expertise/harness-qa.md
OK   .harness/expertise/harness-security-reviewer.md
OK   .harness/expertise/harness-ui-reviewer.md
OK   .harness/expertise/harness-validator-lead.md
OK   .harness/expertise/harness-visual-designer.md
EXIT=0
```

No violations anywhere in the directory — nothing to report for another agent's file.

## Layer

All three entries are craft (`.harness/expertise/harness-dev-ops.md`) — each passes "could this be
true and useful in a repository never seen": git rename-diff behavior, awk/gsub markup fragility,
and exit-code-doesn't-imply-outcome are all tool/shell facts, not this-repo facts. No
repository-layer file was created; none of the material turns on a path, decision or invariant
unique to this repo.
