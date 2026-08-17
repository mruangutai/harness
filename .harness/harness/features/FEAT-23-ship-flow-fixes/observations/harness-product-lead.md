# Observations — harness-product-lead — FEAT-23

- 2026-08-17: my anchor grep for MF-1's fold reported ABSENT what was present. The pattern
  `domain guard resolves` missed `plan.yaml:299-300` because the phrase is split across a line wrap
  inside a YAML block scalar ("Where the domain guard" / "resolves a touched path to NOBODY"). I was
  one step from reporting a missing RIPPLE site that pm had written correctly. Multi-word anchors do
  not survive block-scalar wrapping — grep a single distinctive token (`NOBODY`, `FLAG-ONLY`) and
  widen only to confirm.

- 2026-08-17: the dispatch named `runs/2026-08-17-2-archreview-eng/digest.md` by PATH while
  describing the CONTENTS of `digest-eng-lead-arch-b.md` in the same directory. Two concurrent
  eng-lead arch passes had written to one run dir; the second wrote a sibling filename rather than
  overwrite, and flagged the collision in its own Q1. Reading the named path alone would have made
  me fold the wrong finding set. Glob the run dir before trusting a single named digest — a run dir
  is not guaranteed to hold exactly one.

- 2026-08-17: verified counts beat quoted ones. `BRIEF.md:161-162` claimed "three of this feature's
  six tasks write there" of the GRANTED `bin/**` path; recounting each task's own `files:` gives 2
  granted (T-01, T-05) and 3 unowned (T-02, T-03, T-06). The number was right for the wrong set, so
  it read as plausible. Recount against the source list, never against the sentence's own logic.

- 2026-08-17: `validate-digest.py --hook` fired on my turn-end while a dispatched member was still
  in flight, demanding a DIGEST I could not honestly write. Recurrence of a defect already in
  STATE.md. The correct response is to keep taking tool-call turns rather than fabricate a verdict
  for a member that has not returned — a stop hook must not be able to extract a premature verdict.
