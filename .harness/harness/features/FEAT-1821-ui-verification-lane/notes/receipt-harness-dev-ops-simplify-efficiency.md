# EFFICIENCY receipt — FEAT-1821-ui-verification-lane

## Findings

None. The inspected diff adds one-shot UI verification work and its evidence contract; no measured or directly derived cost warrants a behavior-preserving change.

## Candidates skipped

- **Settled — `.github/workflows/tests.yml:88-99`:** `npm ci`, Chromium installation, and the explicit unit/integration boundary suites are deliberate CI evidence. Chromium installation is a settled requirement, and the full-suite boundary runs are not waste.
- **Settled — `.claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts:12-29` and `e2e/*:24-41`:** the 41 WebP captures are the settled evidence/reporter contract. Their capture and write work is required output, not redundant test overhead.
- **False-positive — `.claude/skills/harness/bin/dashboard/client/ui-reporter.ts:15-21,54-73`:** each of 23 reported test records filters the 22 inspection-evidence rows once (506 equality checks); each of 41 attached screenshots filters them once more (902), for 1,408 in-memory comparisons per UI run. A pre-indexed manifest would be behavior-preserving, touch no assertion, and belongs to frontend-dev, but the directly derived work is not measurable in hot-path milliseconds and is negligible beside browser execution; no finding.
- **Unmeasured/trivial — `.claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts:44-68`:** `sourceTokens()` walks the 15-file, 62,698-byte client source four times and reads 229,528 bytes total (the component-only pass is 41,434 bytes). Caching the source list/text would be behavior-preserving, touch no assertion, and belongs to frontend-dev; it would avoid 166,830 bytes of cache-resident reads once in the desktop-1440-only check, with no measured millisecond cost, so no finding.
- **Trivial — `.claude/skills/harness/bin/dashboard/client/fixture.ts:53-65`:** fixture setup copies the 96 KiB fixture root once and the 378-byte logical `FIX-SHIPPED` seed eleven times to create independently mutable states. The work occurs once per UI run and preserves deterministic isolation; no efficient alternative is justified.
- **Out of scope — all UI predicates:** repeated navigation, `networkidle` waits, and state-specific interactions execute distinct signed checks. Assessing whether any predicate can be reduced would change or re-litigate settled check coverage, not improve verification plumbing efficiency.

## Inspection boundary

Scope was exactly `ac486811c7f42be04fdfabac70d772c93218b995..23097d785fc6614686b3c38590df7934ed2e25d3`. No source, plan, test, or configuration file was modified; no formatter, linter, test, build, or validation command was run.
