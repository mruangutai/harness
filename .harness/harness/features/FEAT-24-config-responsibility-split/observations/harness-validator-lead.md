# Observations — harness-validator-lead — FEAT-24

- 2026-08-18: A member's ARTIFACT lands on disk before its RETURN arrives. I polled
  `notes/review-harness-ui-reviewer-2026-08-18-prebuild.md` into existence, read it, and had
  written `verdict: PASS` into both `state.yaml` and my `digest.md` members: block before any
  completion notification had reached me. The artifact is prose and carries no fenced VERDICT —
  the contract return travels separately and later. Inferring the token from the artifact is
  exactly the "never infer a verdict" failure, dressed up as evidence because I really had read
  a real file. Precedent that it matters here: FEAT-19's mode-A ui-reviewer returned FAIL on a
  single must_fix, so a reviewer's own token on a non-blocking medium is not predictable from
  its prose.

- 2026-08-18: Second same-day sighting of the product-lead's Q5 topology
  (`runs/2026-08-18-2-product/digest.md:25`) — a lead with one async member can be asked for a
  contract-valid return while that member is provably in flight. My `dispatched_at: seq-1` /
  `completed_at: seq-2` markers kept the run decidable, but note that I wrote `completed_at` on
  ARTIFACT-LANDING rather than on return-receipt, which makes the marker mean something weaker
  than the algorithm intends. Write `completed_at` when the return arrives, not when the file
  appears.

- 2026-08-18: Reading the plan tail I had not been handed (T-07..T-11) paid for itself twice:
  it surfaced T-08's `templates/harness.json` `_board_note` as a third operator-facing text
  surface my dispatch never named as a pointer (the reviewer swept it anyway, artifact
  :100-102), and it let me pre-measure `factory_cli.body`, `FleetError.__init__`,
  `gh-sync.py`'s `skip()`/`die()` and `board-station.py`'s `out()`/`err()` BEFORE the return
  landed. Both of my lead-tier additions came from those pre-measurements, not from reading the
  member's note — which is the difference between assessing and paraphrasing.

- 2026-08-18: `gh-sync.py:72-81` — both `skip()` and `die()` `print(...)` to STDOUT, not stderr.
  Any dispatch or plan clause telling a tool to emit "one line on stderr" in this file is asking
  for a primitive that does not exist there. Worth re-checking rather than assuming, because
  three of the four factory-family tools do write stderr.
