# Operator ruling — FEAT-2229 F3-I after validate c3 (2026-11-21)

Answers Q1 from `r-20261121-validate-c3-validator` (handoff-validate-c3.md).

**Ruling: one more fix round that closes the whole class.** Not the narrow indentation cap, and not backlog-and-ship.

The fix round must apply every CommonMark rule that bears on locating a decision's section in
DECISIONS.md:
- fence openers, fence closers and ATX `## DEC-` headings take 0–3 spaces of indentation; 4 or
  more makes the line content (an indented code line);
- a backtick fence's info string may not contain a backtick;
- a closer is the opener's character, repeated at least as many times as the opener, followed by
  whitespace only (F3, landed);
- a fenced `## DEC-` line is never a heading (F2, landed).

Each rule is written test-first with its own actual-CLI case, then validate c4.

Rework accounting, as the operator was shown: the ledger measures 2 of 3 rounds and 38 of 90 minutes,
so this round is inside the signed ruling. The main session had misstated c3 as the last round. The
operator was also told this is the third patch to the same scanner, and chose closing the class over
the narrow cap.
