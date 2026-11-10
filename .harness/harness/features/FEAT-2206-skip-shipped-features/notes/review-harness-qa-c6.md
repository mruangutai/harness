# QA — FEAT-2206 validate c3 (QA c6, contract repair) — review_sha 7b8e2e1f485db72a4a574e04738533cb0ab821ed

**BLUF: PASS, unchanged from c5.** This note only repairs the return shape (strict schema JSON) and rules on my two c5 advisories. No new runs; no source, test, or fixture edits. All evidence is in the intact `review-harness-qa-c5.md` (60 + 86 files pass; INV-52 regression red at 4a351fae semantically and green at the pin on full and sparse arms; 8 shipped in the live corpus; 8cdbb362 historical log equivalent to the pin by a feature.json-only diff).

## Advisories from c5 — ruled
- **A1 (retracted).** I filed it as `proportionality`, but that kind means excessive planned work at scope task|mission; a missing direct unit test is not that. The integration test `test_inv52_keeps_the_branch_of_a_shipped_record_the_strict_loader_refuses` already pins the `_branch_entry` salvage end to end on both arms. The matrix is satisfied, so a missing direct unit test is not a defect. Wrong kind, no defect: dismissed.
- **A2 (retracted).** I read the plan wording "does not load" as a mismatch. That wording belongs to the plan.yaml refusal (`ctx.py:265`). A feature.json record refusal emits "does not parse" (`ctx.py:507`, same string at `seams.py:171`, `board.py:26`). The fixture makes `github.parent` invalid in the feature record and does not break plan loading, so "does not parse" is the correct token for the absence assertion. No form defect. What remains true is that mutation discrimination of that single absence clause was not run (O-05): unshown, not defective. The presence assertion carries the red.

No findings remain; the schema has no findings key.

## Provenance limits preserved (from c5, not re-run)
- Real-corpus count (10 landed / 8 shipped) read the live owner checkout, which was not captured at an immutable SHA (HEAD read after the run was 00998ef1). It is nonimmutable evidence (G-15).
- The standalone-clone verify half was not executed by me (it writes the shared merge log). Substitute: unit and integration kind runs at the pin. check-state, validators, and DECISIONS-INDEX at the pin are covered only by the historical log for 8cdbb362, whose code equivalence to 7b8e2e1f is shown by diff.
- The b7af829c red is crash-class; the 4a351fae red is the semantic one. SC-01/02 fail-first rest on recorded `red-first.md` receipts that I did not re-run.
- The INV-52 fix landed after the review round that raised it; only my own evidence has examined it, with no independent second review (O-07).

## Principles applied
- Build the Lever: reused the recorded c5 probe and commands instead of new runs.
