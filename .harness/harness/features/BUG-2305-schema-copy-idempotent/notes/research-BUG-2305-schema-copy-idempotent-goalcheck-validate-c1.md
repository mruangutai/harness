# Goal-check — BUG-2305

Both perspectives and all four SCs are discharged at the pin. DEC-237's amendment and coupled index pass inspection; QA supplies the automated evidence. No product defect found.

Pin: 297913318472d066ecb9d5eb3f83ee2ca82c3ad7; base: 7f9cc9d8. Read the pinned four-file diff and pinned source, tests, decision and index. No tests/build/lint/formatters run; no production changes authored.

## Perspectives — one line each

- **operator — pass:** SC-01/SC-02 are carried by tests/unit/omp-hooks.test.ts:1743–1859 (every persona, both shapes, independent/reordered copies, canonical identity, all refusal variants and later invalid item); .omp/extensions/harness-hooks.ts:379–427 and :1474–1490 implement exact-copy-only acceptance and canonical re-injection before claims. QA's notes/review-harness-qa-c1.md:16,24–26,35–37 confirms 164/164 at this pin and reproduced relevant base failures.
- **code maintainer — pass:** SC-03 is carried by tests/unit/omp-hooks.test.ts:1702–1723, :1743–1786 and :1862–1873; the diff removes the note constant, emission and obsolete expectations without removing unrelated return paths. QA's notes/review-harness-qa-c1.md:16,27–28,38 proves green at pin and note-removal reds against base. SC-04 is met by the pinned DEC-237 amendment and coupled index below.

## SC outcomes

- SC-01 met — tests/unit/omp-hooks.test.ts:1743–1786; QA notes/review-harness-qa-c1.md:16,24–25,31,35 records pinned green and genuine base assertion failures. Base fail-fast stops at the first persona; all sixteen pass at the pin.
- SC-02 met — tests/unit/omp-hooks.test.ts:1789–1859; QA notes/review-harness-qa-c1.md:16,26,32,37 records pinned green, later-item diagnostic red against base, and preserved refusal controls correctly green before and after the fix.
- SC-03 met — tests/unit/omp-hooks.test.ts:1709, :1721–1723, :1785 and retained no-control coverage; QA notes/review-harness-qa-c1.md:16,27–28,38 reproduces note-removal assertion failures against base and confirms pinned green.
- SC-04 met (inspection) — pin above, .harness/harness/docs/DECISIONS.md:7917–7928; index .harness/harness/docs/DECISIONS-INDEX.md:231–237. Diff changes only Dispatch owns schema delivery, and adjusts all six subsequent index anchors by +5; pinned heading positions agree.

## Decision dispositions

- decisions_affected[0], DEC-237 amend → D-01: **met**, inspection at pin above, .harness/harness/docs/DECISIONS.md:7917–7928. The blanket clause is replaced, not merely mentioned: exact same-target structural bundle plus strict pair, canonical re-injection, changed/non-strict/incomplete/batch-top-level/non-Harness refusals, later-item refusal and fail-closed loading are explicit. Yield/live validation and durable-record policy at :7930–7958 are unchanged in the base-to-pin diff. Coupled index is present and correctly shifted. T-01 owns both documents; no amendment remedy needed.
- DEC-174, DEC-179, DEC-225, DEC-188 and DEC-254 are keep rows, not amend/strike outcomes, and are not graded. All six rows carry exactly dec/disposition/clause/successor/reason; D-01 exists and T-01 owns DECISIONS.md plus its index, satisfying DEC-254's five-field/ownership obligations (:8264–8284). Narrowing rather than striking is consistent with DEC-188.

## Findings and dismissed concerns

No substance/form product findings. Former evidence dependency (reader harness-pm, task T-01, severity informational, kind form) is resolved by notes/review-harness-qa-c1.md:16–38: QA independently ran the literal verify at the pin and reproduced the builder's five named base assertion failures. No source remedy or replan is required.

Dismissed: #2257 static-type runner gap is signed and disclosed, not a new finding; batch-top-level and non-Harness refusal are intentional; OMP persistence is out of scope. Missing PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are recorded by the approved BRIEF; no substitute guidance was invented.

QA advisories retained: refusal variants were green on base and over-permissive-mutant discrimination remains unshown; the base fail-fast loop demonstrates the first persona's red, not sixteen independently observed reds; reordered-key red is not isolated. These do not negate the criterion's exact-copy regression proof or pinned passing assertions. The general unit runner does not execute this Bun file; the literal T-01 verify does and was run directly by QA (:15–16). No claim of broader runner coverage is made.

## Principles applied

Experience First — graded the operator's repeat-dispatch loop and maintainer's regression/documentation promises separately; implementation convenience and source inspection do not replace the promised automated evidence.

## Open questions

None. Q-01 resolved by the final QA artifact cited above. No checks were rerun by pm.
