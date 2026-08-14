# Observations — harness-visual-designer — FEAT-19

- 2026-08-13: Sent to fix a count of "four" refusal branches to five, per the ui-reviewer's c1
  read of plan.yaml. Measured it myself at HEAD: SEVEN. The plan had been re-authored between the
  review and my dispatch, adding two step-4b branches (fleet absent; fleet present but unloadable).
  Both the review's number and the dispatch's number were stale by one re-authoring. Anchor: the
  reviewer cited `plan.yaml:99-127`, already wrong lines by the time I opened it.
- 2026-08-13: `grep -c "raise ProductConfigError"` UNDERCOUNTS — YAML block scalars wrap the phrase
  across lines. Two of the seven were invisible to a line-wise grep (5b-ii malformed, and step 6
  which says "raises", not "raise"). Whitespace-normalize the block first, then regex.
- 2026-08-13: I filled row 7's missing `what` and missed row 6's, one row up, in the same c1 pass —
  then restated the miss in three more places (BLUF "six of the seven", the "Rows 1–6 satisfy both
  slot rules" summary line, and row 7's "the only one with no specified text"). The row I was sent
  to fix was one of four edits. Live instance of P-02: when a per-row audit finds ONE gap, re-run
  the same audit against every row before writing the summary — the summary sentences are where the
  false premise gets its widest reach, and they read as prose so the row-level check skips them.
