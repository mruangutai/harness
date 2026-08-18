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

- 2026-08-17: I tried to send a mid-flight correction to a dispatched member and there is NO channel.
  Leads hold `Read, Glob, Grep, Agent, Write` only — no `SendMessage`. My attempt spawned one no-op
  agent (~88k tokens, zero work). A correction discovered after dispatch has exactly two homes: the
  next dispatch, or my own assessment when the member returns. Queue it; do not try to deliver it.

- 2026-08-17: a member's evidence table is pinned to the commit it ran at, and that pin goes stale
  silently. qa graded the SCs at `83e769b` while `review_sha` had moved to `490c37c`. Before
  consuming any prior gate's per-SC grades, read the header for ITS pin and diff it against the
  current one — then bound the delta from the intervening run's digest rather than assuming it is
  either harmless or fatal. Here it was comment-text-only in two files, which made the risk small
  and checkable instead of unknown.

- 2026-08-17: a task's `verify:` can be structurally blind to the SC it traces. T-02's clause grepped
  "plan surface"/"code surface" FILE-GLOBALLY while SC-05 required the pair under EACH of four
  angles — three angles satisfied the grep and the fourth was missing both. Green task verifies are
  not evidence for a distributive SC. When an SC quantifies over N items, check whether its task's
  clause quantifies too, or only existentially.
