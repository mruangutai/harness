# Observations — harness-visual-designer — FEAT-11

- 2026-08-10: I measured `repositoryOwner(login:)` in isolation and wrote its exit code into
  DESIGN.md as if it held for the document the builder would actually send. It did not — the
  combined query's organization case exits 1, because a nested `projectV2(number:)` selection fails
  underneath the owner selection. Lesson: probe the FULL document being recommended, never the
  discriminating fragment alone. Exit code is a property of the whole query, not of the field the
  contract cares about.
- 2026-08-10: the falsified sentence that mattered most was not the one in the dispatch. The BLUF's
  "a response real `gh` never produces" was a stronger, more misleading overgeneralisation than the
  Contract 2 paragraph I was sent to fix. When one claim is falsified, grep the file for every
  restatement of the same premise before returning.
