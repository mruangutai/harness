# Research — FEAT-02 VERDICT shadowing in validate-digest.py

## Conclusion (BLUF)

The defect is real and wider than the BUILD ledger row states. It is not just the
`VERDICT:` regex — **all three top-level anchors are first-match-wins**, so an echoed
contract template shadows the entire real return, not just its verdict:

- `VERDICT:` — `re.search(r"^\s*VERDICT:\s*(\S+)", text, re.M)` at `validate-digest.py:380`.
  Against the template line `VERDICT: PASS | FAIL | BLOCKED | ESCALATE`, `(\S+)` captures
  `PASS` — a *valid* token. The shadow is silent, not a parse error.
- `DIGEST:` — `parse_digest` takes the **first** `DIGEST:` line (`:283-284`), so field
  validation runs against the echoed placeholder block, not the real one.
- `artifact:` — `re.search(r"^\s*artifact:\s*\S+", ...)` at `:388` is satisfied by the
  echoed `artifact: <path>`.

## Reproduced

A qa return that echoes the harness-handoff template and then returns a real
`VERDICT: FAIL` block exits 0 with `digest ok` — the FAIL block is never validated
(run 2026-07-27, scratchpad repro). Existing suite: 36 cases, green (exit 0).

## Fix shape (carried into PLAN D-01)

Anchor validation to the **last** `^\s*VERDICT:` line: slice the text from that line to
the end and run every existing check (verdict token, DIGEST presence, `parse_digest`,
artifact, lead roll-up) against the slice. The real return is by contract the final
thing an agent writes, so last-anchor routes it correctly; the echo becomes inert
preamble. If no `VERDICT:` line exists anywhere, fall back to whole-text validation so
the existing "no VERDICT" error and digest-field errors are preserved unchanged.

One mechanism fixes all three shadowed anchors; no new parsing code.

## Constraints checked

- stdlib-only: fix uses `re`/string slicing only. PyYAML not installed (confirmed constraint).
- Test harness already supports pre-fix proof: `VALIDATE_DIGEST_BIN` env override
  (`test-validate-digest.py:18`) exists exactly for "prove new cases fail against the
  saved pre-fix binary" (task-22 precedent).
- bugfix test matrix (`harness.json`): `unit` always + `__bug_class__` — the bug class
  here is "shadowed anchor", covered by the new unit cases themselves.

## Edge cases the tests must pin

1. Echo(PASS template) + real FAIL block → validates the real block (exit 0, and a
   deliberately-broken real block is rejected on *its* defects).
2. Echo + real block missing a required field → rejected (pre-fix: falsely accepted).
3. Echo before a valid lead return whose members carry FAIL → roll-up computed against
   the real top verdict, not the echoed PASS.
4. No-echo returns (all 36 existing cases) → byte-identical behavior.
5. Hook mode (`--hook`) — same shadowing path via `last_assistant_message`; needs at
   least one hook-mode case.

## Open

- Echo-only returns (agent pastes template, never writes a real block) remain
  accepted when the placeholders happen to be schema-valid. That is a content problem
  the validator cannot fully decide; out of scope, noted for the ledger.
