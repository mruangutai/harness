# PASS — security — 4a351faea95ad3776f130d0f42f303a4eee3e4b9

No independently exploitable security regression found. Both c1 T-01 conversion repairs are closed by source inspection; this is not an independently executed runtime pass. Findings/must-fix: none; severity: none.

## Pin, scope and boundary

Inspected whole range `b7af829c..4a351fae` and correction delta `688c5ef5..4a351fae`, never HEAD. `git diff 4a351faea95ad3776f130d0f42f303a4eee3e4b9 -- .claude tests .harness/harness/docs` returned empty, exit 0, binding inspected implementation files to the pin.

All 21 changed paths were scoped: seven implementation paths (`artifact_accessors.py`, `check-plan-routes.py`, `check_state/{board,ctx,runner,table}.py`, `feature-schema.json`) are IN for parsing, enforcement selection, diagnostics and retirement. Two decision/index documents are IN as the authority for the exemption. Twelve test/fixture paths are IN for subprocess construction, audit-output writes and adversarial-input coverage; they introduce no production endpoint. Swept the full diff for credential/injection surfaces; no added credentials, dependencies, network destinations, spreadsheet exports or production command construction found. Fixture subprocesses use argv lists; their generated shell uses a fixture-owned temporary log path.

## T-01 fixes and whole-feature assessment

- **c1 med oversized-number defect:** `check_state/board.py:138–162` now contains `int(s)` ValueError. Shipped claims skip None and continue (`:193–211`), retaining other usable collision identities. The new 4,301-digit-parent regression asserts no traceback AND one surviving issue-11 collision (`tests/integration/test-check-state-shipped.py:226–237`).
- **c1 low active Unicode regression:** the same converter restores `str.isdigit()` without the ASCII restriction; Arabic-Indic `٣` reaches `int()` as before. The paired-active regression binds `٣` versus integer 3 to one collision and no malformed-number finding (`:239–249`). Original med/low severities are retained here as closed dispositions, not new findings.
- The full-range diff leaves `feature_json_write.opt_int` unchanged (`:94–110`). `artifact_accessors._positive_issue_number` contains its ValueError (`:145–151`); parent/issue validators then raise documented FeatureJsonError (`:154–179`). Census `_entry` records that refusal (`feature_corpus.py:225–239`), allowing shipped comparison fallback. `board_lifecycle._github_numbers:952–968` still interprets opt_int's raise as unknown ownership, preserving broad LABEL checking.
- Classifier declaration counting precedes value extraction (`check_state/ctx.py:59–80`): duplicate collection/empty/numeric/quoted keys remain subjects; missing/unreadable/nested status is not shipped. The original c0 duplicate bypass is source-closed. Text-line classification, including exemption from strict parsing, is expressly DEC-252—not proof that ship ran. Editing a genuine `status: done` requires plan-write access and intentionally selects the approved exemption; no extra authentication guarantee is claimed.
- `_load_features` removes shipped subjects before artifact loads (`ctx.py:223–234`); lazy population carries only data (`:423–457`). INV-24 still compares usable shipped claims, including both iteration orders. INV-29/52 retain independent populations; corpus failures remain explicit. CLI preflight refusal precedes the shipped early return, and selector glob metacharacters are escaped (`runner.py:284–325`). No new execution or privilege-bearing sink consumes the raw comparison mapping.

## Evidence limits and guidance

Executed only read/search/diff inspection; no Python probes, tests, builds, linters or full suite. Role shell capability is git-diff-only; executable adversarial probes were therefore not attempted, and no runtime refusal/output is invented. QA owns execution assurance. Retained red-first.md “Rework round 2” reports discriminating c1 failures, baseline Unicode success and repaired success; these are historical receipts, not my runs.

Measured `b5b6fa70..4a351fae`: only feature.json review_sha and regate metadata differ. The b5b6fa70 log ends with 146 files and verify-exit=0; equivalent implementation is not literal exact-pin verification.

PRODUCT/docs/spec.md, docs/decisions.md and docs/architecture.md remain absent (docs listing contains neither); no control-plane substitute was used. Q-01 and disclosed live metadata/station issues are unchanged nonblocking disclosures. Open security questions: none. Source/tests/records untouched.
