# QA Expertise distillation — FEAT-31

## Relayed candidates — dispositions

1. **PASS-line count quoted upward, mixed-granularity.** ACCEPTED but re-homed to
   **repository tier**, not craft — it is a fact about *this* file (`run-unit-tests.sh:136,139`),
   not a portable rule. Craft P-13 already carries the general "state provenance/granularity/
   convention" lesson from an earlier round; adding this instance to craft would be a duplicate
   story per the "no instance lists" rule. Landed as repo `G-04`.
2. **Config test-matrix floor inadequate as literal read, filed as non-blocking, not a FAIL.**
   ACCEPTED into craft. Existing `P-15` already told you to *run the broader kind* — this
   sharpens the missing half: how to *classify* the shortfall (config finding needing a signed
   decision, not grounds to fail the feature). Replaced `P-15` in place (same slot, sharper
   text) rather than adding a new one — the old text and the new are the same lesson at two
   depths.
3. **Two dispatched questions left unruled; lead ruled them from evidence it verified directly.**
   ACCEPTED into craft as a calibration gotcha — genuinely new, not covered by any existing
   entry (`O-03`/`O-07` are adjacent but address different failure modes: labelling reasoned-vs-
   measured, and independence after a late fix). Displaced `O-05` (Phase-1-matches-plan
   coincidence) — narrower and rarer in applicability than "rule on what you can already prove."

## Self-derived (from my own two notes — not relayed, since I hold the sources)

- **Fixture realism checked one direction only** (fixtures match live data) but not the other
  (live shapes absent from any fixture, safe only by incidental code ordering). ACCEPTED —
  displaced `G-08` (a narrow "check the prior segment's note" gotcha, rarely applicable) with a
  generically useful realism-audit rule.
- **Static call-site count vs a runtime dead-code canary branch** (Q-CHECKCOUNT) — REJECTED as an
  entry. Too narrow to survive the "true in a repo never seen" test: it turns on one test file's
  own internal diagnostic-guard structure, not a repeatable QA behavior.
- **Mutation-proof cascade breadth as stronger evidence than isolated-case failure** (depth
  mutants, ~1/3 of suite went down) — REJECTED. Already substantially covered by `G-10`/`G-13`
  (precondition size, reproducing the real regression) at the same altitude; a third entry would
  be a story, not a sharper rule.
- **Event-name extrapolation in a probe (PreToolUse probed, PostToolUse registered)** — REJECTED.
  Close enough to `G-14`'s "model the distinguishing property, don't assume it" to be a duplicate
  at slightly different subject matter; not distinct enough to earn a cap slot.

## Counts

| Tier | Section | Before | After |
|---|---|---|---|
| craft | Patterns | 15/15 | 15/15 (P-15 replaced) |
| craft | Gotchas | 15/15 | 15/15 (G-08 replaced) |
| craft | Outcomes | 10/10 | 10/10 (O-05 replaced) |
| craft | Open | 1/5 | 1/5 (unchanged) |
| repo | Gotchas | 3/15 | 4/15 (G-04 added) |
| repo | Patterns/Outcomes/Open | 0 each | 0 each (unchanged) |

`check-expertise.sh` clean on both `.harness/expertise/` and `.harness/harness/expertise/` after
the edits (no ADVISORY against `harness-qa.md` in either).

## Process note

`expertise-merge.py` union-merges only; it does not drop or overwrite a same-ID entry with
different text (exit 7, CONFLICT — by design, per DEC-125). The three craft replacements above
were applied first through the tool (confirmed genuine same-ID conflicts, not accidental
duplicates), then resolved directly per the distill skill's own exit-7 row ("a real conflict —
resolve it yourself"). The repo-tier addition was a clean `apply` with no conflict.
