# PASS — bounded test delta introduces no security regression

Pinned range: `90caccaf1ae0c5bc192d13efd199d6c90971adf0..a48a725e16321d3a3f9ef142a0b95e2e19a4de5e`; original baseline `c4e8bbc87e858bb2a0320efd766c7036cbcebb8b`. Inspection only, using Git blobs/diff rather than mutable HEAD. Read BRIEF, T-01, c2 receipt, c1 validator digest, must-fix-c0, own c1 note, PRODUCT CLAUDE/AGENTS and mapped SPEC §13 / DEC-174/225. No previous security findings require reopening.

## Measured census and scope

**8 changed paths, +170/-38: one Python test, six Markdown notes, one feature JSON record. Production is unchanged in this delta.**

- In scope: `tests/unit/test-lead-start-preflight.py` changes interpreted installation-advice assertions and introduces a test-only subprocess probe. At pinned lines 494–514 its Python program is constant, arguments use list-form argv without a shell, and prefixes/marker answers are test-authored. `sys.prefix` and `os.path.exists` changes occur only inside each child, before importing `harness_yaml`; they do not modify guard isolation or the parent process. Existing real-start, claim and hostile-origin controls remain unchanged.
- In scope as interpreted review/evidence: `notes/qa-fix-c1.md`, `notes/receipt-main-session-fix-c2.md`, and `notes/review-harness-{code,security,ui}-reviewer-c1.md`. They retain the prior failure and limitations; receipt claims are not independent execution evidence.
- Out of runtime-security scope: `notes/operator-rework-raise-2026-11-07.md` records the bounded operator ruling; `feature.json` records that ruling and the refused prior run, without changing policy or authorization logic. Its historical review pin is not substituted for this dispatch's explicit immutable pin.

All eight paths and complete hunks inspected; full-diff credential sweep found accounting fields/review prose only, no credential material. No new auth, secrets, data exposure, dependency or production import-isolation surface. Earlier security review covered the production import boundary; this is not its first audit.

## Existing finding dispositions — T-01, security lens only

- **F-1 (substance, previously unrated): remains resolved; no regression by inspection.** Grant test is unchanged in this delta; baseline-to-pin diff retains platform-command membership and the earlier-session diagnostic. No new runtime closure claimed.
- **GC-01(a) (substance, previously unrated): remains resolved per c1 QA/validator evidence; no regression by inspection.** Neither production imports nor single-install start assertions changed. No non-C-loader execution performed here.
- **GC-01(b) (substance, high, unchanged): source-level early-return/host-selection obstruction removed.** Pinned preflight lines 525–547 probe four simulated platform contexts and assert actual `INSTALL_COMMAND` commands plus warning; no missing-helper gate remains. Baseline-to-pin harness_yaml diff confirms that constant predates the fix and contains the old per-user fallback. The c2 receipt reports all five advice cases red at baseline and green fixed in the qualifying image; **execution/evidence closure remains QA's responsibility, not certified here. Source-only review is not full SC-02 certification.**

Threat boundaries assessed: subprocess output → advice assertions (Tampering), installation advice → operator (Tampering). No exploitable weakening identified. Findings/must-fix: none. Accepted med complexity items are not reopened. No tests, builds, linters, formatters, mutations or production execution performed. Only this report written. Open security questions: none.
