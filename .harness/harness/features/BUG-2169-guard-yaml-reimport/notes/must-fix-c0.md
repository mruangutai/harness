# Must-fix - BUG-2169 - validate c0 at 6c896d98

Consolidated by harness-validator-lead, run `2026-11-07-2-validate-validator` (human report
`runs/2026-11-07-2-validate-validator/digest.md`; reader notes `notes/*-c0.md`). The lead's
return verdict was FAIL; the host did not append its record (#2171), so the run is closed
BLOCKED as a refused return. Findings below are transcribed from that return verbatim in substance.

1. **F-1 - substance - T-01 (qa).** `tests/integration/test-check-domain-grant.py:359-362`
   D-14a still asserts `"pip install"`; on the Debian image the fixed advice is `apt`, so it is
   green at base and red at the pin (26/27). Migrate it to the platform-selected advice.
2. **GC-01 - substance - T-01 (pm).** (a) SC-01: no qualifying single-install start without
   PyYAML's C loader was executed. (b) SC-02: at base the advice assertions returned early at
   the missing helper, so no assertion failed on the old advice's behaviour.

Accepted, not must-fix: two med grade-2 complexity findings (code), with the written reasons in
`notes/build-evidence-2026-11-07.md`.
