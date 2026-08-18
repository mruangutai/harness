
- 2026-08-18 (FEAT-24 T-10): regenerating DECISIONS-INDEX.md does NOT touch the ruling right of
  ` :: ` — it is preserved from the existing file by DEC number. So a falsified ruling survives every
  regeneration silently, and the only thing that catches an over-long replacement is
  `test-gen-decisions-index.py`'s 30-word cap, which the index itself never states. Edit ruling,
  then run generator-diff AND that test, in that order.
- 2026-08-18 (FEAT-24 T-10): `AMEND_BOLD_RE` (`^\*\*Amendment(?:\s+(\d+))?\b`) makes any line opening
  `**Amendment` a counted amendment, comma included. And a `### DEC-NNN amendment` heading contains
  the substring `## DEC-`, which terminates a section for any verify that locates the next entry with
  `src.find("## DEC-", i+1)` — so the last entry in the file must take the bold inline form.
