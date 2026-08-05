# Expertise — harness-pm

## Patterns (max 15)
- P-01: WHEN a `verify:` grep would already have passed before the change DO label it
  non-discriminating and name a substitute command whose result only the change can produce.
  An absence-grep that was already empty proves nothing. Exemplar: the `## Verify receipts`
  section of a shipped plan under `.harness/features/`.
- P-02: WHEN a criterion will cite automated evidence from a test kind DO check that kind's detect
  globs match files on the surface being changed: a non-null runner matching zero files here is a
  gate that proves nothing. Widen the runner as a task rather than downgrading the criterion to
  inspection.
- P-03: WHEN a criterion declares automated verification DO NOT admit a source-code reading as its
  evidence — that converts it to inspection, and the method is fixed at approval. Name the passing
  test, or return the criterion not met.
- P-04: WHEN a criterion enumerates N clauses, shapes or personas DO count the enumerated items in
  its own prose against the fixture cases, and diff a sibling criterion's fixture set against it.
  Under-fixturing, not wrong behaviour, is the dominant defect — reading the implementation will
  not show it.
- P-05: WHEN an enumerating criterion is delivered for only some of its clauses DO grade it not
  met, never partial. A requirement not delivered in full is not honestly covered, and the missing
  clauses are the gap the next pass has to close.

## Gotchas (max 15)
- G-01: WHEN citing a `file:line` after editing that file DO re-grep the anchor at final state and
  re-read the line before describing it. Numbers captured mid-edit mix pre- and post-edit
  positions, and a pointer can be right while the prose gloss of it is wrong.
- G-02: WHEN a dispatch names the artifact path to write DO check it against your own write grant
  first. A dispatch naming a path is not evidence the path is granted, and the domain guard blocks
  the write.
- G-03: WHEN collecting command evidence for an automated criterion DO redirect the run to a file
  and grep it. Piping a multi-script runner to `tail`/`head` truncates the earlier output away and
  reports the pipe's exit status, not the runner's — the evidence disappears silently.
- G-04: WHEN re-deriving counts, lists or partitions in a revision pass DO include the items you
  added earlier in that same pass. Your own additions are the likeliest staleness source, and a
  self-describing list that under-counts itself still reads as authoritative.

## Outcomes (max 10)

## Open (max 5)
