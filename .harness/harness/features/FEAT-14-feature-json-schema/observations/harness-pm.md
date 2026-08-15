# Observations — harness-pm — FEAT-14

- 2026-08-10 (send-back cycle 1): making a previously-OPTIONAL key REQUIRED can arm an invariant
  that was disarmed by that key's ABSENCE. `check-state.sh` INV-17 line 451
  (`if _phase not in PHASE_ORDER: continue`) kept FEAT-01/FEAT-02 quiet only because they carried no
  `phase`. D-02's backfill would have demanded six handoff notes that cannot honestly be written.
  Found by reading the reader's guard clause, not by censusing values — the value census (all four
  live `phase` values legal) said nothing about it. Lesson shape: when a schema turns a key from
  optional to required, grep every reader for a branch keyed on that key's ABSENCE.
- 2026-08-10: a baseline recorded as substring text goes stale two ways — the message text is
  renamed by the same feature (INV-18's `no feature.yaml` becomes `no feature.json`), or the
  substring is generic enough to absorb a NEW instance (`BRIEF.md is NOT approved` matching a
  feature that did not exist when the baseline was taken). Both were in my own T-08 verify.
- 2026-08-10: `check-plan-routes.py`'s 50-line machine-field budget counts `files:` entries. A
  fourteen-file migration task spends 14 of 50 before one verify line, so it effectively has a
  ~30-line verify budget. T-04 sits at exactly 50 and T-08 at 49 — no headroom on either.
- 2026-08-10: `.harness/features/` holds FIFTEEN directories and FOURTEEN `feature.yaml` files at
  `06ae963`; FEAT-15-domain-product-base has runs/ and no feature file. A corpus figure taken by
  globbing `feature.yaml` and a figure taken by globbing directories disagree by one.

- 2026-08-12 (FEAT-14 T-09): an absence-sweep with named exemptions must anchor on exact substrings
  asserted present exactly once, then strip-and-recheck the remainder. A `count == N` variant passes
  a delete-one/add-one swap; the strip-and-recheck form fails all four mutants I simulated.
- 2026-08-12: a `verify:` regex without `re.M` + `^` anchoring matched a prose cross-reference 158
  lines above the real heading and inspected the wrong section — silent, and green for the wrong
  reason. Re-derive which LINE a capture resolves to, never just that it matched.
- 2026-08-12: prove a block scalar survived by running the `safe_load`-loaded string itself, not a
  sed slice of the file — the slice keeps the indent and the heredoc delimiter never terminates.
