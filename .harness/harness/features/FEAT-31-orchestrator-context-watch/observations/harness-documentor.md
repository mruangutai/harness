# Observations — harness-documentor — FEAT-31

- 2026-08-22 (T-09): appending a DECISIONS.md entry is two steps, not one. `gen-decisions-index.py`
  emits `⚠ RULING PENDING` for a new entry and preserves only text already right of ` :: `, so the
  row's ruling must be hand-written between two generator runs — and `test-gen-decisions-index.py`
  enforces a **30-word cap** on it. My 51-word first draft failed the task's own `verify:` line 3.
  Write the ruling short, then regenerate and re-run the test.
- 2026-08-22 (T-09): a dispatch's "verify X names N" can be true in a different notation. DEC-148
  writes "200k", not "200000", and for a different metric (avg cache-read/turn, not context size).
  The figure checked out; the like-for-like framing did not. Recorded the distinction in the entry
  rather than returning FAIL — a notation mismatch is not a factual one, but flattening it would
  have put a false equivalence into an authority file.
- 2026-08-22 (T-19): the task was dispatched twice with the same runid, and the tell was cheap — the
  dispatch's own before-run verify already PASSED, and `ls notes/` showed
  `receipt-harness-documentor-t19-c1.md` already on disk. Running the verify block before doing
  anything is what caught it; had I edited first I would have double-written the entry. The useful
  move on a duplicate dispatch is to re-derive the baseline from `git show HEAD:<file>` (which
  proves the working-tree edit is the cause) and audit the landed prose against source, rather than
  either redoing it or trusting the prior receipt.
- 2026-08-22 (T-19): `bash-write-guard.sh` rejected a `cat >> file <<'EOF'` heredoc, reporting the
  redirect target as `40` — a bare number from the heredoc body. Appending to a file I own must go
  through Read-then-Edit, not a shell redirect, whenever the content contains numerals.
