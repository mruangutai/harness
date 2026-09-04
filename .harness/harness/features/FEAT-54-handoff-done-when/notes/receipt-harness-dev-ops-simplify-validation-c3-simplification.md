# SIMPLIFICATION — FEAT-54 validation c3 repairs

## BLUF

PASS with three advisory-only simplification candidates. No source or test edit is authorized or applied in this dispatch. The c3 regressions remain independently falsifying: nested and duplicate Done-when failures retain separate fixtures and diagnostics, strict ATX rejection retains both malformed-heading cases beside a valid Approval control, and containment retains separate finding/approval cases plus valid controls.

## Advisory findings

1. **File:** `.claude/skills/harness/bin/handoff_done_when.py` **Line:** 26. **Summary:** trailing `[ \t]*` is redundant after `line.strip()` under `fullmatch`. **Concrete cost:** the accepted-heading grammar is expressed twice, making later anchoring edits harder to reason about and suggesting the suffix still changes acceptance when it cannot. **Alternative:** retain `fullmatch` and `line.strip()` but use `r"##[ \t]+Done when"`; this preserves exact anchoring and does not merge the nested/duplicate checks. **Classification:** advisory-only; Main-direct file, no apply.

2. **File:** `.claude/skills/harness/bin/handoff_done_when.py` **Lines:** 89-90. **Summary:** the same resolved target is statted twice to obtain mode and size. **Concrete cost:** every finding/approval resolution performs an unnecessary filesystem metadata lookup and the two facts are needlessly acquired through separate calls. **Alternative:** bind one `metadata = resolved.stat()` and read `metadata.st_mode` and `metadata.st_size`; retain the existing resolve/containment/regular-file/read ordering unchanged. **Classification:** advisory-only; Main-direct file, no apply.

3. **File:** `tests/integration/test-check-state.py` **Lines:** 2213-2223. **Summary:** `_feat54_baseline_cases` copies every case-map entry into an identically named local before use. **Concrete cost:** ten aliases add an unnecessary mapping-to-local pipeline and force each added/renamed case to be represented in both the map and the alias preamble. **Alternative:** pass `notes["missing"]`, `notes["nested"]`, and the other entries directly to each already-separate `_feat54_check_case` call. Keep distinct nested/duplicate calls and their distinct needles, and keep the `HANDOFF_GOOD` positive control unchanged. **Classification:** advisory-only; Main-direct test file, no apply.

## Preservation inspection

- Unit cases at `tests/unit/test-handoff-done-when.py:54-70,105-143,169-192` keep a well-formed positive control, separate nested/duplicate malformed notes, valid Approval resolution, two strict-ATX negatives, and symmetric finding/approval containment cases.
- Write-gate cases at `tests/integration/test-check-domain.py:4040-4064,4067-4105,4108-4134` keep the valid note, distinct nested/duplicate diagnostics, valid pointer controls, strict-ATX negatives, and finding/approval unsafe-target coverage.
- State-gate cases at `tests/integration/test-check-state.py:2178-2258` keep separate nested/duplicate note construction and assertions, plus the non-baselined resolving positive control.
- The five representation-only repaired digests listed in `notes/qa-validation-c3.md:36-44` repeat summary evidence but are frozen run records with no actual drift; no simplification is recommended there.

## Evidence and changes

Inspection only. Per dispatch, no command, test, suite, validator, formatter, or linter was run. Source changes: zero. Test changes: zero. Files written: this receipt only.
