# Expertise — harness-data-engineer

## Patterns (max 15)
- P-01: WHEN judging whether a measured cost is negligible DO state it in the unit matching its
  frequency — per-call, per-session, or share of the surrounding budget — not a bare number. A
  reader cannot check "negligible" against a figure with no scale attached.
- P-02: WHEN grading whether a verify block proves its claimed guarantee DO check every named file
  individually and classify each as per-item, file-global, or absent before writing "no verify
  anywhere" — a partial gap reported as total is the error a reader remembers, not the finding.
- P-03: WHEN reporting a scope count (e.g. files changed) DO show the breakdown that produced it,
  not just the total — a bare number is indistinguishable from a lucky guess against an
  independent recount, and the breakdown is what lets a reviewer verify or refute it.
- P-04: WHEN a review angle returns zero findings DO report the checks performed, not just the
  count — enumerated checks let a zero read as evidence of coverage rather than silence.
- P-05: WHEN judging whether a proposed new seam (module, class, layer split) is justified DO
  check whether anything actually varies across it, not whether one could be drawn — extending
  an existing classifier/renderer pair often needs no new seam.
- P-06: WHEN a finding proposes deleting code as duplicating an existing guarantee (e.g. a sort
  reapplied to already-sorted input) DO check whether any test asserts the differing case before
  calling removal safe — proving the guarantee empirically outside the suite is not the same as
  the suite seeing it.

## Gotchas (max 15)
- G-01: WHEN timing-probing a CLI that shells out to an external service (e.g. `gh`) DO wire the
  fake-binary env vars first, or run from a directory outside any real target — probing from a
  real project root can reach production and issue live network calls.
- G-02: WHEN a docstring or spec claims a function raises but the code path returns silently DO
  enumerate every real caller before flagging it as a live risk — if every caller pre-filters the
  case, it is a stale docstring, not a runtime hole.
- G-03: WHEN a test fake for an external CLI matches only argv text DO check whether it also
  enforces the semantic shape — verb, response structure — a text-only fake lets a call that
  flips read to write, or returns a malformed response, pass silently.
- G-04: WHEN judging whether a manual sort after a language-native ordered enumeration (e.g. a
  bash glob) is redundant DO verify empirically — build fixtures out of order, inspect raw output
  — rather than assume; bash pathname expansion is already lexicographically sorted by the shell
  before the loop runs.
- G-05: WHEN a comment cites a numbered label (e.g. "CHANGE 1") as its rationale DO grep the file
  for that label before trusting it — a label existing only in a planning artifact narrates the
  plan's own bookkeeping, not a present fact, and goes stale once the plan closes.

## Outcomes (max 10)

## Open (max 5)
