# F2 documentation amendment — PASS

SPEC §5.3 and DEC-253 now qualify every close-integrity promise with the operator-approved local-default-branch boundary (notes/answers-2026-11-21-f2-ruling.md). No other section or decision changed.

## Changed sentences, verbatim (physical lines after edit)

- `.harness/harness/docs/SPEC.md:945-946`: Fabricated, missing, unreceipted or file-inconsistent evidence refuses live yield and replay/merge, and durable close verifies against the default branch as the local repository records it.
- `SPEC.md:947-949` (added): Unreceipted content hidden by deliberately moving default-branch refs (`git update-ref`, `git branch -f`, `git symbolic-ref`) is a stated close-time boundary, refused at `merge-gate.py merge-distill` against the live remote; hardening is tracked in #2251.
- `SPEC.md:973-974`: Close, against the default branch as the local repository records it, and replay retain receipt/file integrity after supersession; there is no independent queue.
- `.harness/harness/docs/DECISIONS.md:8201-8203`: Missing, fabricated, unreceipted or file-inconsistent evidence refuses live yield and replay/merge, and durable close verifies against the default branch as the local repository records it.
- `DECISIONS.md:8204-8206` (added): Unreceipted content hidden by deliberately moving default-branch refs (`git update-ref`, `git branch -f`, `git symbolic-ref`) is a stated close-time boundary, refused at `merge-gate.py merge-distill` against the live remote; hardening is tracked in #2251.
- `DECISIONS.md:8224-8226`: Receipt/file integrity remains required at close, against the default branch as the local repository records it, and replay; this is neither an independent ledger nor a queue.

## Preservation evidence

Captured complete pre-edit bytes in persistent shell variables; compared post-edit bytes using Python byte equality and SequenceMatcher, without tests or git. Both non-target-section comparisons returned True; before/after SHA256 of concatenated bytes outside each assigned section:

- SPEC: `296f3a35a3cf8b40b34af76be06f0592cc4bef26d6becfbcff9b8dcf893bef27`
- DECISIONS: `74827103d840e66c780bfc90cd1ddfc8f9d19f63fb6b5fea600603f974d9383c`

Changed spans only: SPEC old 945–946 → new 945–950 and old 969 → new 973–974; DECISIONS old 8202 → new 8202–8206 and old 8221 → new 8225–8226. Unchanged neighboring sentences inside those spans remain verbatim, including “Emitting an op alone is not completion.” All other bytes match. The scoped close sweep found two promises in each section; all four are qualified.

Touched files: the two documentation paths above and this receipt (all under the supplied feature worktree). Initial baseline collection encountered an environment-size error and then a Python bytes-literal syntax error; corrected read-only collection succeeded with the retained original bytes. No tests, goalcheck, builds, git commands, or broader audits ran. Main owns any subsequent verification. Open questions: none.
