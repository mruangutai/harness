# DevOps Expertise distillation — FEAT-36

**BLUF:** No Expertise operation was accepted. The craft Patterns section is already at its 15-entry cap; no existing entry was weaker than the two novel candidates. The preservation candidate is already covered by G-07.

## Inputs and judgments

- Observations: the designated log is absent; accepted 0, rejected 0.
- Digest-skim candidates: accepted 0, rejected 3.
  - `runs/review-fix-eng/digest.md`: rejected. Stale CPython bytecode is a durable mutation-test risk, but craft Patterns is full and no existing rule merited displacement.
  - `runs/goal-check-fix-eng/digest.md`: rejected as covered by G-07: seed a pre-existing out-of-scope file and byte-check it before and after.
  - `runs/t01-eng/digest.md`: rejected. Runner/detection-registry agreement is durable, but craft Patterns is full and no existing rule merited displacement.

## Existing-entry audit

- Craft `.harness/expertise/harness-dev-ops.md`: keep P-02–P-05, P-07–P-17 and G-02–G-15; none are stale. Counts remain Patterns 15, Gotchas 13, Outcomes 0, Open 0.
- Repository `.harness/harness/expertise/harness-dev-ops.md`: keep P-01, G-01, G-02, G-04–G-06; none are stale. Counts remain Patterns 1, Gotchas 5, Outcomes 0, Open 0.

## Operations and scoped proof

- Exact applied operations: `[]`.
- A preliminary `P-18` merge attempt supplied only an entry line, without the canonical `## Patterns` heading required by the merge input shape; it parsed as empty and did not change Expertise. Final judgment remains no displacement at the full Patterns cap.
- Scoped check: `.agents/skills/harness/bin/check-expertise.sh .harness/expertise/harness-dev-ops.md` exited 0: `OK`; it emitted only the existing advisory that G-03 may be repository-layer. The repository Expertise file was unchanged, so its scoped check was not required.
