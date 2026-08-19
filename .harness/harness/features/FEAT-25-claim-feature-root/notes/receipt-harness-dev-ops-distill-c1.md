# Receipt — harness-dev-ops — distillation

**Result: 3 accepted, 0 rejected (1 self-derived — P-10; 1 relay verified against own receipt — G-11;
1 self-derived — G-12). +1 Pattern, +2 Gotchas. Checker: OK.**

## Section counts

| Section | Before | After |
|---|---|---|
| Patterns | 8 | 9 |
| Gotchas | 10 | 12 |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

## Candidates — judged

1. **Accepted (G-11).** Verified against my own `receipt-harness-dev-ops-verify-T-03-c1.md`:
   `git rev-parse HEAD` and `git rev-parse d1ffd7f` both resolved to `d1ffd7fa1e...`, so the
   `git diff --name-only d1ffd7f...HEAD` printed nothing by construction — HEAD had not moved off
   the base, not because nothing changed. My receipt already explained this in prose, but the
   digest's point stands: an empty three-dot diff is ambiguous between "no changes" and "nothing
   committed" unless HEAD position is checked first. That's the general, actionable rule —
   distilled as a gotcha about auditing diffs, not a claim about that specific run.

2. **Accepted (G-12).** Verified against my own `receipt-harness-dev-ops-simplify-efficiency-c1.md`:
   the `run-unit-tests.sh --kind unit` row reports `3.878s (total, time)` with no exit code beside
   it, and no ok-count is given for that suite (only the three underlying `.py` files got ok-counts).
   Self-derived gap, worth a standing rule: report exit code and ok-count alongside any timing used
   as evidence.

3. **Accepted (P-10).** Self-derived, from all three verify receipts (T-01/T-02/T-03), each of which
   independently re-extracted the task's `verify:` block via `yaml.safe_load` and byte-diffed it
   against the dispatch's quoted copy before running it. I checked this wasn't already covered:
   P-05/P-06 cover git-status *snapshotting* as evidence, P-07 covers *measuring* an unmeasured
   gate — neither covers re-extracting and byte-diffing the command itself against its source
   before trusting a dispatch's transcription of it. Distinct enough to earn its own entry rather
   than a fold-in.

## expertise_update ops (see DIGEST for the canonical list)

- add, Patterns, P-10 — verify-command re-extraction + byte-diff, self-derived from all three
  verify receipts.
- add, Gotchas, G-11 — three-dot diff / HEAD-position check, relay candidate 1, verified against
  T-03 receipt.
- add, Gotchas, G-12 — exit-code + ok-count alongside timing evidence, self-derived from simplify
  efficiency receipt.

## Checker

```
.claude/skills/harness/bin/check-expertise.sh .harness/expertise/harness-dev-ops.md
OK   .harness/expertise/harness-dev-ops.md
```
