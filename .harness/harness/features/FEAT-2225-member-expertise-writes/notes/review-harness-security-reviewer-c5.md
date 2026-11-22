# FEAT-2225 security review — c5

**PASS — C4-F1's index correction is present at the exact pin; no new exploitable surface. C4-W1 remains low/form advisory.** Review pin `7065b650ab3b94bae3175978bfd0cf0d62478c89`; previous pin `a5d8687f31c9f05fa77f4d16f3634c3869f47b1f`; carried base `594af2a8`.

## Independently measured delta

Read `notes/review-harness-security-reviewer-c4.md` first. Exact previous-pin→review-pin diff contains eight paths: DECISIONS-INDEX.md, feature.json, the documentor fix receipt, and five c4 review/research notes. Only the index changes product guidance: `.harness/harness/docs/DECISIONS-INDEX.md:236` changes `[expertise,dispatch,worktree,map]` to `[expertise,dispatch,state,worktree]`; ruling, references and target line remain unchanged. The other seven paths record run history/evidence, including prior FAILs, rather than changing authorization. No source, tests, dependencies, credentials, endpoints or output interpreter are added. Reviewed the complete delta for credential disclosure; none identified.

**C4-F1 CLOSED, SC-06 index clause:** exact pinned diff matches the correction in `notes/receipt-harness-documentor-fix-c4.md`; fix `8257a2e02d84a1fb32f91b24d645cd9404bf092e`→review-pin diff for the index is empty. The receipt records regeneration comparison and the named integration test red→green. This review confirms pinned content, not a fresh execution of either check; QA owns final automated verification.

## Carried assessment and advisory

Full base→pin path census reassessed: host/core/guards/schema/merge remain identity and tampering surfaces; skills/personas/SPEC/decisions remain authority promises; tests and feature records remain evidence surfaces. All implementation and authoritative SPEC/DECISIONS bytes are unchanged from c4, so their security grades carry by `notes/review-harness-security-reviewer-c4.md`, “Boundary and containment” and “Remaining promises and evidence reuse.” **F1/F3 remain CLOSED**, including registered identity/lineage and five capability-class/both-tier/all-verb evidence. No newly exposed authority or evidence bypass appears in the eight-path delta.

**F2 remains an operator-accepted boundary, not a finding or repaired vulnerability.** `notes/answers-2026-11-21-f2-ruling.md` accepts local-ref-relative verification and tracks #2251. Carry c4's original exploit history and source-derived fresh-remote replay/blob-agreement plus DEC-220 owner/mirror containment; no exploit rerun or broader containment claim.

**C4-W1 — low, kind form, advisory retained:** `notes/review-harness-code-reviewer-c4.md:13` identifies unqualified live-yield wording at SPEC `:945` and DEC-253 `:8201-8202`, although live yield shares the local-ref verifier with durable close. Neither passage nor verifier changed in this delta. The same accepted local-ref boundary applies to both; the prose should not imply live yield is stronger. This remains wording-only, nonblocking, and does not reopen F2 or require implementation changes.

STRIDE carried: host→application E/T mitigated; mutable local refs→close/live-yield acceptance T **unmitigated, explicitly operator-accepted**; PR→shared Expertise T mitigated by remote replay/blob agreement and owner/mirror checks. Open questions: none. Must-fix: none. No source edits, tests, builds, lint, formatters, exploit reruns, commits or pushes; only read-only git diffs and this note.
