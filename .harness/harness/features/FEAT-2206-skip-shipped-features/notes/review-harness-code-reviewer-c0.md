# FAIL — FEAT-2206 pinned compliance review

Reviewed `b7af829c0207522b43f978b5275a2ebdc96b3210..fe49c8df3807d875f2cd44410559966cc836b9ab`, exact dispatched `.claude`, `tests`, `.harness/harness/docs` diff. No human-attributed commits; working-tree changes were only feature.json and plan.yaml (the disclosed post-pin review transition), not reviewed executable bytes.

## Stage 1 — compliance FAIL

1. **High · substance · T-01 · SC-01/SC-02:** `check_state/ctx.py:54-66` counts only status lines whose values match its token regex. For `status: done\nstatus: null\n` (likewise an empty or collection-valued second status), only `done` matches: an ambiguous/unreadable status is classified shipped, removed from all audit subjects, and explicit selection reports success without checks (`runner.py:319-321`). DEC-252 expressly requires two status lines to remain checked. **Fix:** establish exactly one top-level status declaration before accepting its value; add duplicate-valid-plus-null/empty/container regressions. This is a fail-open classification defect, not a request to restore strict parsing. **Evidence: source-derived [INFERENCE]; reviewer ran no executable verification.**
2. **Medium · substance · T-01 · SC-03:** raw shipped `factory: {repo: "acme/widget", issues: {"T-01": "²"}}` reaches `_inv24_shipped_claims` (`board.py:188-189`), whose number helper accepts `str(n).isdigit()` then calls `int(n)` (`board.py:138-146`). Superscript digits satisfy the former but cannot be converted by the latter: ValueError aborts the comparison instead of ignoring the unusable shipped field. The new raw-record path makes historical malformed values reach this conversion without schema grading. **Fix:** make numeric conversion total for raw JSON values and test an unusable Unicode-digit value beside a usable collision claim. **Evidence: source-derived [INFERENCE]; not executed by reviewer.**

SC-01 inspection: central exclusion is present before artifact loads (`ctx.py:216-226`), but finding 1 defeats its fail-closed boundary. SC-02 inspection: one-note early exit exists (`runner.py:319-321`), with the same classification defect. SC-03 comparison-only routing exists (`ctx.py:419-447`, `board.py:178-193`), but finding 2 violates malformed-value handling. SC-04 retirement and caller cutover are present (`table.py:240-245`, `check-plan-routes.py:1985`); source sweep found no obsolete INV-28/30 implementation callers. Amendments inspected against BRIEF/DEC-252, not used as acceptance authority.

## Evidence and scope

`notes/red-first.md` records baseline unit 10 failures / integration 8 failures and correctly disclaims newly-red INV-24/29/52 collision behavior. `notes/merge-fe49c8df3807d875f2cd44410559966cc836b9ab.log:1` binds the pin; its ending records 146 files and `verify-exit=0`. These recorded greens do not cover the two scenarios above. Literal T-01 verify matches dispatch. `notes/simplify-pass.md` covers the earlier simplification pin; final diff contains its shared wrapper and census reuse.

Mechanical code grade: **pass**, from QA's exact baseline/pin run; read `/private/tmp/f2206-qa-evidence/code-grade.txt` (56 PASS records, no SEVERITY/REASON REQUIRED). No reviewer builds/tests/lint/formatting/grading execution. **Stage 2 qualitative code-quality review deferred because Stage 1 did not pass.**

Missing product guidance: PRODUCT `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent; signed BRIEF, operator-settled grilling, and PRODUCT DEC-252 govern this bounded change. Approved loss of handoff-validate enforcement and deletion of the old INV-30 auth-sharing test are not findings.

## Principles applied

- **Migrate Callers, Then Delete Legacy APIs:** checked retirement removes implementations, imports, table rows and obsolete enforcing tests without compatibility aliases.

Open questions: none. Required next action: fix both T-01 compliance defects and have QA exercise the new cases; then complete Stage 2 at the new pin. No source changes made.
