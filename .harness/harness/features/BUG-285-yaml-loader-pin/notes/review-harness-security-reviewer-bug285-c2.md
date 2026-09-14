# Security re-review — BUG-285 remedy at `ab0c9987`

**BLUF: PASS. Cycle-1 validator F1 is CLOSED.** The remedy converts the remaining non-mapping nested `factory` fail-open into a deliberate refusal and routes quoted issue numbers through the shared coercion. The only production `load_factory` caller reaches it before the first local ledger write or remote mutation; `factory_cli.run` intentionally propagates its `SystemExit(2)` without a traceback or partial abort. No new security defect was found relative to `592e6412`.

## Boundary trace

- **Untrusted/malformed local state → reader:** `factory_decompose.load_factory` reads operator- or tool-writable `feature.json` (`.claude/skills/harness/bin/factory_decompose.py:111-166`). A present non-mapping `factory` now calls `factory_cli.refuse`, naming the path, rather than returning `_empty_factory` (`:126-133`).
- **Reader → mutation:** the only production caller is `_main` at `factory_decompose.py:519`. It loads and classifies the ledger before issue-type detection and before `ensure_labels`, which the source marks as the first remote write (`:519-541`). The changed integration scenario confirms this input exits 2 with zero mutating calls.
- **Exception boundary:** `factory_cli.run` has `except SystemExit: raise` before its `BaseException` trap (`factory_cli.py:72-96`). Therefore the intentional issue-#208 refusal remains one stderr line naming `feature.json`, exit 2, without an `unexpected failure` wrapper or traceback. Direct library callers must handle `SystemExit`, but repository search found no production caller other than `_main`, which is inside this boundary.
- **Numeric compatibility/integrity:** `parent` and each `issues` member use `feature_json_write.opt_int` (`factory_decompose.py:137-148`). Input `"7"` becomes issue 7, preventing the old duplicate-parent/task path. `true` remains excluded because Python booleans subclass integers (`feature_json_write.py:180-196`); treating it as absent is the settled contract. An actor able to replace a recorded number with `true` already has the same ledger-write capability needed to delete or replace it, so this creates no privilege delta. Legitimate writers emit integer issue numbers, never booleans or quoted numbers.
- **Writer compatibility:** `_factory_block` serializes the in-memory mapping and integer/`None` values (`factory_decompose.py:182-199`); all internal `write_factory` calls receive factory state loaded/coerced by this reader or numeric results from GitHub. It cannot emit a non-mapping `factory`, and it emits quoted legacy numbers back as integers. Thus the writer cannot produce the newly refused shape.
- **Ordering/disclosure:** refusal occurs before `write_factory`, `ensure_labels`, issue creation, board mutation, or edge mutation. Its diagnostic exposes only the local path and fixed remediation text, no document values, tokens, or traceback. Read-only preflight/board checks may precede `load_factory`; no partway mutation can precede refusal.

## Prior finding adjudication

**Cycle-1 validator F1 — CLOSED.** Concrete former scenario: input `{"factory":"x"}`; caller `factory_decompose._main`; wrong outcome at `592e6412` was an empty ledger followed by duplicate parent/task issue creation. At `ab0c9987`, `load_factory` refuses before mutation. The sibling input `{"factory":{"parent":"7"}}` now preserves parent 7 through shared coercion, so it no longer triggers duplicate parent creation.

The cycle-1 security note's separate LOW nested-depth/`RecursionError` message-quality advisory is unchanged by remedy `592e6412..ab0c9987`; it is not a new remedy defect and remains fail-closed under `factory_cli.run`.

## Security census and threat model

Remedy code surface: `.claude/skills/harness/bin/factory_decompose.py` is in scope for Tampering, Information disclosure, and denial/fail-closed behavior across the local-state-to-GitHub boundary. `tests/integration/test-factory-decompose.py` and `tests/integration/test-gh-sync-open.py` contain only fixtures/assertions and no shipped trust boundary. The five added feature notes/receipts are review records, contain no credentials, and add no runtime surface. No auth, SQL/shell/template injection, SSRF, redirect, dependency, credential, or cross-user data surface is introduced.

STRIDE: malformed ledger tampering is mitigated by refusal before mutation; disclosure is mitigated because diagnostics contain a path/fixed reason only; duplicate-issue integrity risk from quoted numbers is mitigated by canonical coercion. Availability remains intentionally fail-closed for corrupt state.

## Verification

- `python3 tests/integration/test-factory-decompose.py` — **177/177 checks passed**, including non-mapping refusal/path, zero mutation, quoted-parent coercion, bool exclusion, non-UTF-8 refusal, and writer atomicity/compatibility.
- `python3 tests/integration/test-gh-sync-open.py` — **ALL PASSED**, confirming the shared-reader caller remains compatible.

No findings. `severity_max: low` (scoped-in clean review; no actionable finding); `must_fix: []`.
