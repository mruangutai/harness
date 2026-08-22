# Observations — harness-pm — FEAT-26

- 2026-08-22: T-BRIEF-AMEND attempt 2 dispatch asserted "attempt 1 wrote nothing, BRIEF.md is still
  151 lines". False in the working tree: `wc -l` was 170 and a 19-line stale entry carrying the two
  falsified numbers (31 mutations, `222 of 222` at `Station: Done`) was already appended, uncommitted.
  Both guard md5s still matched because both guarded sections were untouched — md5 checks on the
  guarded sections cannot detect prior work in the section under edit. Re-derived the baseline from
  `git show HEAD:<path> | wc -l` (151) before writing, and replaced the stale entry rather than
  appending beside it, so the diff vs HEAD is exactly +13/-0.
- 2026-08-22: the board's field is literally named `Status` (`.harness/harness.json`
  `board.station_field`) while the harness's own vocabulary for it is "station". The stale entry had
  written `Station: Done`, which is neither the field's name nor a value on it.
