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
