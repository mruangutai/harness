# Distill — harness-pm — FEAT-2537

**BLUF.** I accepted all three candidates. C1 went to the repository tier as Gotcha G-16. To make room, I merged G-10 into G-05; both are about the argument to `check-plan-routes.py`. C2 replaced craft P-11. C3 replaced craft G-06 with a version that also covers grading. No section is over its cap, and the repository file is 34/40 lines. I reviewed no diff and ran no suite.

## Candidates

- **C1: accepted, repository tier, Gotchas.**
  - **Source.** My log, bullet 1.
  - **Verified.** In the control-plane copy, `plan_merge/check.py` `_rows_faults` tests `str(row.get('clause')) not in section`. That is an exact substring test, so newlines count.
  - **Why the repository tier.** It depends on one repository's gate.
  - **Room.** Gotchas were 15/15. I merged G-10 (passing a directory raises IsADirectoryError) into G-05 (pass your own plan). Both are about the same script and the same argument rule. The merged entry is no longer than the longer input, which frees a slot.
- **C2: accepted, craft, replaces P-11.**
  - **Source.** My log, bullets 2–3, and the "Gap" section of both the signoff ruling and the c0 ruling. At intake I caught the vacuous `{}` instance. The row-carrying foreign-version instance got through to validate untested.
  - **Overlap.**
    - P-16 grades signed prose against measured behaviour after the fact.
    - P-19 probes one boundary beyond the stated class contract when closing a defect class.
    - C2 is different from both. It works at plan time: enumerate what the removed predicate accepted, and require a test witness for each delta.
  - **Why P-11 was displaced.** It was the weakest survivor. It restates the preloaded harness-brief red flag "An SC quantifies over more than the work can touch", so dropping it loses nothing.
- **C3: accepted as a sharpened G-06, craft.**
  - **Source.** My goal-check note's SC-02 form note called the `json.loads` comparison "adequate". The c1 ruling then found a text-mode read that let a CRLF writer mutant pass, which cost an escalation.
  - **What changed.** Old G-06 only covered specifying raw versus normalized input. The replacement also covers grading: a normalized comparison is graded partial, never "adequate by argument". It drops the narrow original-entry passthrough sub-clause. A new entry would have needed a further displacement at 15/15, so I sharpened G-06 rather than adding one.

## Ops applied

| Tier | Batch | Ops |
|---|---|---|
| repository (harness) | `ad4e4eb509a4506e067083eed9ac5ed281406937e5d08f47380bc48859f33095` | replace G-05, drop G-10, add G-16 (Gotchas) |
| craft | `95fef527065e4f6e8b81a9fdc5f4c1030e6ab4a361f60ffe013fa73a4ce40986` | replace P-11 (Patterns), replace G-06 (Gotchas) |

The first craft attempt was refused with exit 14 because P-11 was 51 words. I trimmed it and re-applied. Nothing was written by the refused attempt.

Receipt: `notes/expertise-receipt-962af8f1608cedfb16a9398bf2262a5f70924b4b1040fddab0c6da7baab2a874.json`.

## Counts (before → after)

| Tier | Patterns | Gotchas | Outcomes | Open | Lines |
|---|---|---|---|---|---|
| repository (harness) | 12 → 12 | 15 → 15 | 2 → 2 | 0 → 0 | 34 → 34 / 40 |
| craft | 15 → 15 | 15 → 15 | 10 → 10 | 0 → 0 | 45 → 45 / 150 |
