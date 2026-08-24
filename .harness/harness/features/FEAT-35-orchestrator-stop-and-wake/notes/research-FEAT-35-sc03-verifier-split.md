# SC-03 amended by verifier split — FEAT-35

**Done, first pass, 0 send-backs.** SC-03 is now two clauses, each naming its verifier and citing
evidence that already exists. Nothing in it waits on a future run. `verify: inspection` unchanged,
no `evidence:` key added. `BRIEF.md:98-116`.

## What changed and why it was possible

SC-03 was never untestable — it named a verifier who cannot be an orchestrator. The three failed
grades (c0 empty candidate set, c1 non-unique nonce, c2 `context-watch.py:53` and `:303-304`
hard-filtering to `harness-orchestrator`) are all the same defect seen from three angles: one
criterion asked one tier to prove two things, and only one of them was in that tier's reach.

The proxy the operator rejected — accepting the tool's *refusal* as evidence of fail-closed
behaviour — would have graded a safety property nobody specified in place of the property that was
specified. The split proves the specified thing instead.

**Clause A, the SHAPE**, reviewer with its own `agentType` as stand-in. Proves the two-call
sequence, match-count logic and id derivation. Explicitly does NOT claim `context-watch.py` accepted
the reviewer-derived id — `review-harness-code-reviewer-c2.md:53` records that rejection, and the
amended text routes that row to Clause B by name. Evidence: `:36-43` (exactly one match, id
`a1e373d16aeba8a17` correctly derived) and `runs/2026-08-24-03-validator/digest.md`.

**Clause B, the SUBJECT**, main session against a live orchestrator. Both measurements quoted
verbatim: sidecar `agent-ad292e24ec60c589b.meta.json`, and the row
`current=330,527 peak=330,527 entries=149` with the warning in DEC-198's own voice.

**Deleted:** "stays unexercised until a real orchestrator runs it after merge." It became false the
moment the operator exercised it; leaving it would have been a falsified statement in a signed
artifact (PRINCIPLES rule 15).

## Diff scope — verified

`git diff -- .../BRIEF.md` is one hunk, `@@ -95,18 +95,25 @@`, entirely inside the SC-03 bullet.
SC-01, SC-02, SC-04 through SC-07, Problem, Goal, Requirements, Constraints and Verification gaps
are byte unchanged. `## Approval` is byte-unchanged and outside the hunk — pm never signs.

`review_sha` appears in the BRIEF only as the placeholder token `<review_sha>` (`:89`, `:119`); no
literal sha is carried, so `a2a373b1ef351f94b0a4310bea928f1384727a08` was neither written nor
removed, per the dispatch.

## Open

- Q1 (non-blocking, for the main session): the amended SC-03 asserts both clauses already met, but
  the pm tier does not sign, and does not re-grade under this dispatch. The re-grade and the
  re-signature are the main session's.
