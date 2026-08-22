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
