# FAIL — signed verify passes; a grant-test regression and operator-evidence gaps block clearance

Reviewed only `6c896d981ed17d2bae528818ecffa56400ae2666` against `c4e8bbc87e858bb2a0320efd766c7036cbcebb8b`, validate cycle 0. QA measured `1780b922..6c896d98` as plan-status-only. `severity_max: high` is the gating equivalent of retained **unrated**, not a re-rating of either reader's finding. No source/test/GitHub changes made.

## Ranked must-fix — both substance, T-01

1. **F-1 (QA; unrated): migrate the remaining D-14a install-advice assertion.** `tests/integration/test-check-domain-grant.py:359–362` still requires `pip install`; Debian now correctly prints `sudo apt install python3-yaml`. QA measures base exit 0 versus pin exit 1, 26/27. Reuse the platform-selected advice already used by adjacent SC-08 assertions. This is an owned regression, not a scope/operator question. The build note's claim of identical grant failures before/after is contradicted by QA's isolated measurement and must not be relied upon. Fix this before the final regression run.
2. **GC-01 (PM; unrated, narrowed): complete operator evidence.** Demonstrate a single-install **non-C-loader** start in the signed Ubuntu/CI source without changing production loader policy; capture semantic pre-fix failures for platform advice/warning behavior rather than merely the absence of the new helper. The fixed branch assertions pass, but return early at base and never examine old advice. Attach durable discriminating evidence, then rerun the affected checks at the next pin.

## Reconciliation and assurance

QA treats those two coverage gaps as advisory; PM grades SC-01/02 partial. I retain PM's narrower signed-outcome reading: the operator perspective explicitly promises “with or without its C loader,” and SC-02 requires branch/warning assertions that fail against pre-fix advice. A C-only image pass and missing-helper assertion do not discharge those promises. No scope change or operator approval is needed to finish them.

PM **withdraws** its initial missing-base/pin-evidence objection for C-loader/isolation/integration: fresh QA supplies qualifying environment identities, semantic red/green and preserved key excerpts. SC-04 is met; historical missing raw-log links are not a separate blocker. QA withdraws Q-1. Its four plant controls naturally pass at base, but the keep-all-YAML mutant independently makes all four fail (58/62): adequate discrimination, not another defect.

QA's signed suites pass **135/135, 62/62, 57/57**, zero FAIL cases, **13 s**, on image-owned PyYAML 6.0.3/libyaml and Python 3.14.4. Required bugfix kind is unit; `matrix_ok: true` means changed-behavior coverage, **not whole-runner green**. Both full kind runners exit 1 in this image; missing bun and common root/path failures predate the patch. The grant regression is newly introduced, not covered by that qualification. No whole-suite/CI-green claim is made.

Code and security inspect the preserved trust boundary without independent runtime execution. Code's two **med substance** grade-2 test-complexity findings are assessed and accepted, not gating: shared fixture lifecycle and flat named assertions justify their shape. UI scopes out after a 16-file census; no UI surface. PM outcomes: operator fail; CI pass; code maintainer pass. SC-01/02 partial; SC-03/04/05 met.

## Member receipts

All paths below are under this feature's `notes/`:
- QA **FAIL**: `review-harness-qa-c0.md` — sole execution/mutation evidence.
- Code **PASS**: `review-harness-code-reviewer-c0.md` — compliance and quality inspection.
- Security **PASS**: `review-harness-security-reviewer-c0.md` — trust-boundary inspection.
- UI **PASS**, out of scope: `review-harness-ui-reviewer-c0.md`.
- PM **FAIL**, reconciled: `research-BUG-2169-guard-yaml-reimport-goalcheck-validate-c0.md`.

Open questions: none. Route remediation to the main-session-direct T-01 owner; retain reader finding severities/kinds unchanged. No merge or ship clearance.
