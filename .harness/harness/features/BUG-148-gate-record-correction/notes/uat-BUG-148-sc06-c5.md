# UAT — BUG-148 SC-06 — the operator's read of the corrected passages

**Result: SC-06 PASS**, in two halves with two different readers. Neither half is a re-run: this
note transcribes reads already performed. The operator never read the passage that now stands in
`DECISIONS.md` — he read its longer predecessor and sent it back on length. Do not read this note
as his signature on the shortened text.

SC-06 (`BRIEF.md:97-99`): "Reading both corrected passages, the operator confirms the correction
says what he meant, rewrites no ruling, and reads as current truth rather than as an apology
appended to history." `verify: uat`.

## Half 1 — FEAT-05 `STATE.md`, read by the OPERATOR at cycle 4

- **Who:** the operator, personally.
- **When:** cycle 4, before the cycle-5 wording fix (`651e60e2`).
- **What he read:** the corrected `## Current` passage in
  `.harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md` (at `review_sha`, lines 14-20:
  "Three gates green… **Corrected 2026-09-06 under BUG-148:**…"), together with the then-current,
  **longer** DEC-174 evidence paragraph.
- **Verdict:** facts **accepted**. He sent back **only** the DEC-174 passage, and only on
  **length** — not on accuracy, not on register, not on any ruling. The FEAT-05 half of SC-06 is
  therefore settled by the operator himself and is unaffected by the cycle-5 edit, which did not
  touch that file (byte-identical at `651e60e2`; source:
  `.harness/harness/features/BUG-148-gate-record-correction/STATE.md` `## Current`).

## Half 2 — the SHORTENED DEC-174 passage, read by `fable-advisor` at cycle 5

- **Who:** `fable-advisor`, acting under the operator's **standing authorisation for this feature**
  — *not* the operator. The main session relayed the result to the orchestrator as a **binding
  ruling**.
- **When:** cycle 5, after `651e60e2` shortened the evidence paragraph from 115 words / 10 lines to
  88 words / 8 lines.
- **What was read:** `DECISIONS.md` DEC-174's evidence paragraph at `651e60e2` (region lines 7-14
  of the `## DEC-174`..`## DEC-175` extract).
- **Verbatim ruling:** "SC-06 UAT PASS: the shortened DEC-174 passage is factual, concise,
  preserves the ruling/carve-out, and reads as current truth."

## The honest boundary

The operator's own eyes are on the **FEAT-05** passage and on the **superseded, longer** DEC-174
paragraph, which he rejected for length. The passage now in the authority was cleared by the
advisor under his standing authorisation, and that is the whole of the human evidence for it. If
the ship record needs the operator's own read of the shortened text, that read has not happened.
