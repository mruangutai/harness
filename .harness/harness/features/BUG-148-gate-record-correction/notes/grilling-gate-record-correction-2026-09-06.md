# Grilling — gate-record correction — 2026-09-06

## Destination
Correct the two current false-positive claims that `gen-decisions-index.py --check` passed, without rewriting historical receipts.

## Settled
- Delivery shape → three separate flows: #148, #201, and #206 are independent.
- Execution order → #148, then #201, then #206.
- Scope → live records only; historical receipts, research notes, plans, and reviews remain unchanged.
- Live records → correct FEAT-05 `STATE.md` and DEC-174 in `DECISIONS.md`.
- Correction → add a dated note that `--check` did not exist and its apparent success could not verify index drift.

## Not yet specified
- None.

## Out of scope
- Editing historical feature artifacts or introducing a new index-drift check.

## Facts I verified (so pm does not re-derive them)
- `DECISIONS.md` DEC-174 lines 4308-4309 is the current authority that asserts `gen-decisions-index.py --check` was green.
- `FEAT-05-pyyaml-file-parsers/STATE.md` lines 14-15 is the sole current state assertion that the command exited 0.
- The current documented read-only drift check is `gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`.

<!-- Relocated verbatim on 2026-09-06 by the BUG-148 orchestrator, on the operator's ruling, from
     .harness/harness/notes/grilling-gate-record-correction-2026-09-06.md, so the approved intake
     record sits inside the feature directory SC-05's allowlist admits. Content is byte-identical
     above this comment; the source copy is untracked and resolves to NOBODY, so deleting it is the
     main session's act. -->
