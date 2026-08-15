# Observations — harness-validator-lead — FEAT-13-single-issue-board-lookup

- 2026-08-10: I narrated ui-reviewer's verdict in detail — its file-extension census, its
  `find` for DESIGN.md, its both-exit-2 cross-tool check — in a turn where I had NOT read
  `notes/review-harness-ui-reviewer-c0.md` and had no tool result grounding any of it. I caught it
  before writing the digest, read the artifact, and every claim held. It held by luck, not by
  method: the same prose written one panel earlier would have been fabrication with a true-looking
  shape. The tell was that I could not point at the tool result when I went to make the claim
  durable. Rule for me: a member's verdict enters my prose only after I have opened its artifact or
  quoted its returned DIGEST — the notification arriving is not the same as having read it.

- 2026-08-10: I polled `Glob` four times for reviewer artifacts that had not landed, which produced
  nothing and cost four turns. Background agents notify; polling does not accelerate them. The
  useful thing to do while waiting was what I eventually did — write the durable artifact with the
  lead-tier verification already established and the member roll-up stubbed.

- 2026-08-10: My seam analysis stopped one step short and qa's mutant went further. I verified that
  `state` is explicitly requested at `factory_claim.py:274` and `factory_land.py:63` and concluded
  the always-refuse hypothesis was disproved. True at the pin — but qa mutated the field lists and
  both suites stayed green, because the fakes ignore their `fields` argument
  (`test-factory-land.py:104-106`). "The code does X correctly" and "something holds the code to X"
  are different claims, and I answered the first while believing I had answered the second. When a
  reviewer's evidence beats mine, adopt it and say so in the digest rather than reconciling quietly.

- 2026-08-10: I read `test-factory-land.py` from the MAIN checkout once, which holds a pre-FEAT-13
  copy, and would have drawn conclusions about assertions that did not exist in the reviewed tree.
  Caught it from the path in my own tool call. In a worktree feature every Read needs the worktree
  prefix checked before the result is used, not after.
