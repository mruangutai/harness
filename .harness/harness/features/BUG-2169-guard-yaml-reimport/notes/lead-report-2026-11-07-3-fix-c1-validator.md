# FAIL — 90caccaf1ae0c5bc192d13efd199d6c90971adf0: GC-01(b) remains partially open

F-1 and GC-01(a) are resolved; no regression or new finding class. SC-02 still lacks qualifying behavioral-red evidence for Homebrew, generic advice and warning disclosure. One high substance must-fix remains under T-01; no operator decision is needed.

## Consolidated dispositions and fix order

1. **GC-01(b): OPEN, substance, high (code; QA concurs after correction).** Debian printed advice now genuinely fails against the old text, but the missing-helper return still precedes the Homebrew/other/warning assertions (`tests/unit/test-lead-start-preflight.py:522-550`). Mac-only Homebrew evidence cannot satisfy BRIEF SC-02. Complete these behavioral assertions against pinned pre-fix advice in the qualifying image without depending on the new helper; preserve semantic-red and fixed-pin green evidence. This is the retained c0 obligation, not expanded scope.
2. **F-1: RESOLVED, substance.** QA measures D-14a and SC-08 green at tip; code confirms refusal exit 2 and earlier-session diagnostics remain required (`test-check-domain-grant.py:348-362`).
3. **GC-01(a): RESOLVED, substance.** QA executes immutable tip trees in harness-2169-repro with the sole system YAML extension removed; 135/135, 64/64, 57/57 and all exits 0. Equivalent C-loader runs also pass. No items regressed.

## Adequacy and reconciliation

QA's original PASS classified the same SC-02 omission nonblocking. Literal BRIEF SC-02 and c0 goalcheck require each branch/warning behavioral red; code's objection is correct. QA retracted its closure and returned FAIL, amending `notes/qa-fix-c1.md`. Security only certified unchanged production surface, not all-platform fail-first sufficiency; its narrower PASS is consistent. The two med substance grade-2 complexity findings remain accepted with existing written rationale, not blockers.

QA used host-built `git archive 90caccaf` trees, independent of later worktree HEAD, and Ubuntu python3 3.14.4 / PyYAML 6.0.3 at `/usr/lib/python3/dist-packages/yaml`. Named unit/integration files pass with and without C loader; matrix_ok is true, **not complete SC-02 assurance**. Full kind runners did not pass sandbox layout validation; evidence is the explicit planned per-file commands, not whole-suite clearance. Semantic base C-loader failures support SC-01/04; non-C-loader base starts already passed. Discard mislabeled base rows in historical `container.txt` containing failed Git checkout; corrected `container-base.txt` and fresh QA archive-based evidence support base claims. Empty historical Mac log is not evidence.

## Reader outcomes and provenance

- QA **FAIL**: `notes/qa-fix-c1.md` (corrected assessment; actual image execution).
- Code **FAIL**: `notes/review-harness-code-reviewer-c1.md` (inspection and risk grading; SC-03/05 pinned inspections met).
- Security **PASS**: `notes/review-harness-security-reviewer-c1.md` (inspection only; no new surface).
- UI **PASS**, out of scope: `notes/review-harness-ui-reviewer-c1.md` (measured ten-path census: two Python tests, seven notes, one JSON record; no UI).

Pinned delta: `6c896d981ed17d2bae528818ecffa56400ae2666..90caccaf1ae0c5bc192d13efd199d6c90971adf0`. Fix step **skipped**: main-session-direct T-01 already completed under DEC-174 (`notes/receipt-main-session-fix-c1.md`, fix b88c98c6); no dev dispatched and no source authored by readers. Four readers ran; zero internal send-backs. SC-01/03/04/05 met; SC-02 partial. Gate FAIL: must_fix nonempty and severity_max high. Open questions: none.
