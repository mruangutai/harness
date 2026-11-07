# PASS — a48a725e16321d3a3f9ef142a0b95e2e19a4de5e: GC-01(b) resolved; no regressions

All must-fix items are resolved. SC-01–05 are met at this pin. No new finding class, scope question or blocker; two previously accepted med substance complexity findings remain advisory under `gates.review: advisory_unless_high`.

## Consolidated dispositions

- **GC-01(b): RESOLVED (substance).** Code confirms baseline-compatible `INSTALL_COMMAND` probing, without missing-helper return or host-conditioned omissions. Independently, QA's immutable tip tests against host-archived `c4e8bbc8` bin on `harness-2169-repro`, without C loader, produce exactly five behavioral failures: Debian, Homebrew, Homebrew warning, generic and precedence. All five pass at tip. This meets literal SC-02, not merely source-level plausibility (`notes/qa-fix-c2.md`, fail-first section; `notes/review-harness-code-reviewer-c2.md`, stage 1).
- **F-1: RESOLVED (substance), no regression.** Grant suite exits 0 with 82 ok, including D-14a and SC-08, with and without C loader; code confirms refusal/earlier-session requirements retained.
- **GC-01(a): RESOLVED (substance), no regression.** Qualifying fixed runs pass 135/135 dispatch, 61/61 preflight and 57/57 start-return, with and without C loader. The chain takes 9.2/9.7 seconds. Base C-loader failures reproduce YAML reimport refusals, not invocation failure, supporting SC-01/04.

## Adequacy and reconciliation

QA alone supplied execution/falsification evidence: Ubuntu image, Python 3.14.4, sole system PyYAML 6.0.3; host `git archive` trees bind evidence to the assigned pin despite later HEAD movement. Code's inspection certifies mechanism and pinned SC-03 workflow / SC-05 fallback, not qualifying execution. Security confirms unchanged production surface. UI measured eight changed paths and correctly self-scoped out; this is not visual assurance.

QA initially marked the required unit kind satisfied despite missing Bun (exit 1). I rejected that classification and sent it back once. Its appended correction preserves the failure, supplies read-only Linux Bun 1.4.4 in the disposable image without changing PyYAML/product, and records full unit **exit 0, 57 files**. Full integration is **exit 0, 84 files**, non-root; root permission-test failures are retained, not concealed. `matrix_ok: true` is now supported by actual kind-level greens. Raw `/tmp/qa-c2/out/` logs are session-local; durable excerpts and construction/layout evidence are in the QA note. Bun follows CI's unpinned-version precedent; no claim of every-platform installation testing.

## Reader records

- QA **PASS**, corrected: `notes/qa-fix-c2.md`.
- Code **PASS**: `notes/review-harness-code-reviewer-c2.md`; retains accepted med complexity in `bug2169_cases` and `bug2169_advice`, no new findings.
- Security **PASS**: `notes/review-harness-security-reviewer-c2.md`; inspection only, no new security surface.
- UI **PASS**, out of scope: `notes/review-harness-ui-reviewer-c2.md`; measured no visual/interactive surface.

Fix step **skipped**: T-01 main-session-direct already completed under DEC-174 (`notes/receipt-main-session-fix-c2.md`, fix c19e12e4). Review delta `90caccaf..a48a725e`; all four readers evaluated this one tip. One QA adequacy send-back, no new implementation round. No source/test/config authored, no pin changes or GitHub writes. Must-fix: none. Open questions: none.
