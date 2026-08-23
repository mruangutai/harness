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
- 2026-08-23: FEAT-26 T-07 carried an absence-grep for a sentence that WRAPPED across two lines, so grep -q could never match and the '&& exit 1' could never fire; it read VERIFY-OK with the false sentence standing. Repaired to a python3 whole-file read with re.sub(r'\s+',' ') normalisation. Rule learned: an absence-assertion fails SILENTLY GREEN when the pattern's shape (multi-word, wrappable) does not match the matcher's unit (a line); a presence-assertion under the same weakness fails LOUDLY RED instead. Grade absence-greps by pattern span vs matcher unit, not by string length.
- 2026-08-23: plan-merge.py is ADD-ONLY (bin/plan-merge.py:262-277, exit 7 when an existing id carries a different value), so repairing a clause inside an EXISTING task cannot go through it - use Edit on plan.yaml directly.
- 2026-08-23: PostToolUse check-domain.sh resolves via CLAUDE_PROJECT_DIR = the MAIN repo, so it validated a worktree feature.json against main's STALE feature-schema.json and reported github.source_issues as an undeclared key. The worktree's own schema declares it. A worktree write can be denied by a schema the worktree does not use.
- 2026-08-23: goal-check FEAT-26. An SC saying "survives EVERY save, not just the last" cannot be
  graded by the shipped test, which asserted only the end state. Settled it by importing gh-sync.py
  in-process, wrapping save_recorded to re-read feature.json after each call, and running cmd_open:
  9 saves, all 9 carrying the list. In-process wrapping of the writer is how a per-step clause gets
  observed instead of inferred.
- 2026-08-23: goal-check FEAT-26. A schema SC's "shown to fail before it passes" is unobservable
  after the fact, but the falsifiability substance is reachable read-only: load the schema, delete
  the constraint in memory, re-validate the fixtures. All three rejecting fixtures went to zero
  errors — a red proof with no write to a file outside my domain.
- 2026-08-23: goal-check FEAT-26. notes/goal-check.md is NOT in harness-pm's domain
  (team-config.yaml grants notes/research-*.md and notes/uat-*.md only). A dispatch naming that path
  is asking for a denied write; wrote notes/research-FEAT-26-goal-check.md and said so.
