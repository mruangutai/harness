# BUG-2390 goalcheck — validate c1

PASS — SC-01/02/03 are met under the explicitly approved post-hoc reconstruction disposition. This closes c0's evidence finding, not by claiming the original red discriminated or preceded implementation correctly.

Review pin: `780f9138dc3423c45368aa5334f06bd2532e0e8f`; run: `r-20261122-3-validate-validator`. BRIEF, plan, source and historical receipts were inspected with `git show`/`git diff` at immutable refs. Product guidance: pinned AGENTS.md Project map and SPEC §§4.2/5.3. No tests, builds, formatters, code edits or replanning by this reader.

## Perspective outcomes

- **code maintainer — met:** honest object/array contracts and checked fixture narrowing satisfy SC-01; SC-02 has a discriminating immutable reconstruction accepted under the delegated advisor ruling. Both trace through T-01 (`plan.yaml:24`).
- **operator — met:** SC-03 retains object-gate and member-ops behavior, 214 passing tests, and existing assertion strength; its shared static proof is reconstructed, not an invented historical or runtime red. T-01 traces SC-03.

## Criterion outcomes

- **SC-01 — met / inspection.** `notes/review-harness-code-reviewer-c1.md:9,16` cites pinned `.omp/extensions/harness-hooks.ts:49–56,410,431–432,525,971–974,1686` and `tests/unit/omp-hooks.test.ts:38–44,181–189,228,3594,3619`: union signatures, checked object reads, actual ops-array forwarding and truthful fixture comment. Independently inspected these anchors and the full two-file diff; both files contain zero `as unknown as` occurrences. No replacement array-as-object assertion appears; the six inherited payload `as any` reads are unchanged, not newly introduced.
- **SC-02 — met / automated, under approved reconstruction.** Authority: pinned `notes/fix-c1.md:3–10` and this dispatch's explicit delegated approval. QA's `notes/review-harness-qa-c1.md:19–26` independently reproduces `bun run typecheck` at `2a479efdd027ecf5a95ad5fbf0dcde5fffb091c1`: exit 1, TS2345 at `omp-hooks.test.ts(2166,53)`, PolicyPayload/unknown[] not assignable to Dict. The existing member-ops test directly calls the production classifier with its recorded union payload. Independent diff confirms red production differs from `9eb07b4f` only by the unused exported alias; its signatures remain object-only, and red/final test bytes match. Green receipt `notes/receipts/T-01-verify-2.txt` records exit 0 at `a61290822c2645bcda7f99ee674d23cff6756dfb`; production/tests/configuration are unchanged from that execution to the review pin. QA additionally records current-pin typecheck exit 0 (`review-harness-qa-c1.md:16`). The literal original chronological test-first sequence was not achieved; the approved reconstruction, not rewritten history, discharges this criterion.
- **SC-03 — met / automated.** QA's current-pin literal verify exits 0 with 214 pass, 0 fail, 1554 expectations (`review-harness-qa-c1.md:13–16,30–34`); its unit runner also passes 65 files, including `tests/unit/test-omp-hooks.py` running the hook suite. Carrying tests: FEAT-2225 member-ops forwarding (`omp-hooks.test.ts:2149–2176`, array equality :2162), malformed-ops refusal (:2077–2079), and broad/narrow object-gate classification (:2533–2596). Pinned main baseline receipt and `research-patch-intake.md:35–36` record 214/0/1553. Independent baseline-to-pin diff has 24 removed and 25 added expect-bearing lines: 24 checked-read substitutions plus one added assertion inside the existing test (:2166); no test/skip/todo declarations change. Therefore test count stays 214 while executed expectations increase by exactly one. No removed, skipped or weakened assertions found. SC-02 supplies the approved static discrimination; no runtime red is required or claimed.

## Reconstruction boundaries and dispositions

Independent diffs confirm production `369096a4..780f9138` is empty; c0 implementation is restored unchanged. The original `T-01-red.txt` remains byte-identical and records TS2614 (missing export), which never established runner-contract discrimination. Commit history places reconstruction after original implementation. A wider fake alone remains assignable to an object-only callback; the new argument-position call fixes that evidence blind spot. It directly discriminates classifyPolicyRun, not independently each PolicyRunner/runPolicy seam. Its runtime execution reaches the array path but does not discriminate removal of the guard; no stronger runtime claim is made.

Pinned `plan.yaml:19–20` has `decisions: []` and `decisions_affected: []`: no amend/strike rows exist, hence no DEC disposition grades or DECISIONS.md-owning remediation task is applicable (DEC-254). T-01 owns both implementation files and traces all three criteria; no perspective or criterion is orphaned. No new approval is requested.

## Principles applied

- **Type System Discipline:** inspected the actual union signatures and checked narrowing, rather than accepting alias presence or cast-absence alone.
- **Never falsify the record** (PRINCIPLES §15): retained the original failed proof and distinguished approved post-hoc discrimination from original test-first chronology.

Open questions: none. QA owns execution/runner receipts; this assessment uses its c1 evidence and the code review, not reader re-testing. Live OMP host API validity remains outside the typecheck claim (SPEC §5.3).
