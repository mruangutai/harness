# Operator ruling after validate c2 BLOCKED — 2026-11-09

Asked (Q-02): should INV-52 salvage branch claims from shipped records the strict loader refuses,
or accept the lost protection as a waiver? Context given: a shipped record with a malformed field
fails strict parsing, is no longer reported (shipped features are not graded), and its branch claim
silently drops out of INV-52 — so a later feature could reuse its branch unnoticed. Signed SC-03
says INV-52 still detects landed branch collisions involving shipped records.

## Ruling

Mike Ruangutai: **"ok, we should fix that."** Salvage the claim — INV-52 reads strict-refused
shipped records through the same lenient comparison re-read INV-24 uses. Third rework round
granted: rework 3 rounds / 105 min.
