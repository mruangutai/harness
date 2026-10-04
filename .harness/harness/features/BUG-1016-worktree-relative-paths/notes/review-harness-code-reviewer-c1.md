# PASS with advisory — BUG-1016 pinned code review

Reviewed **af2a958ab06c0d6fc026b363b59fc3147e3982f1..8211687fd442258a4ae1a50d8e5375228a51b540**, not HEAD. Read all four SC-07 subjects with `git show` at that pin. fe8c50ea changes only feature.json; current tracked dirt is feature metadata, not implementation. No `[harness:human]` commits in the reviewed range.

## Stage 1 — spec compliance: PASS with nonblocking discrepancy

SC-01..SC-06 map to T-01's revised-input helpers, readiness/authorization ordering, resolver refusal, defaults, mixed-target guards and lifecycle tests. D-01's silent behavior is implemented; no unrelated production changes. The documented ast_edit array correction agrees with the supplied actual host schema and does not violate behavioral acceptance. No build amendments are listed in the build handoff.

**SC-07 inspection:** `.harness/harness/docs/DECISIONS.md:8013-8087`, `.harness/harness/docs/DECISIONS-INDEX.md:237`, `.omp/extensions/harness-hooks.ts:354-405,975-1014,1174-1187,1453-1459`, and `tests/unit/omp-hooks.test.ts:1279-1550` agree on seven tools, lexical rooting, resolver/claim authority, blank/default distinctions, guards, caching and host exclusions, except for the predicate discrepancy below.

- **R1 — med / substance / T-01 + T-02 / SC-01, SC-07:** `rootTarget` classifies a trimmed, unquoted target (`.omp/extensions/harness-hooks.ts:355-357`), whereas BRIEF Constraints specifies `isAbsolute`, first-character tilde and leading-scheme tests on each nonblank path-list entry. For example, a governed `read` with `path: '"~/notes.md"'` is nonblank, not absolute, does not begin with `~` or a scheme under that exact predicate, but the implementation returns it unchanged without resolving the feature root. DEC-251 (`DECISIONS.md:8029-8035`) explicitly documents this broader exclusion rather than the promised exact predicate. This is an uncommon input mismatch, not an authorization bypass demonstrated here. Align the path-argument predicate with BRIEF and retain edit-specific quoting semantics, or obtain an explicit acceptance amendment. Add a literal revised-input case for this distinction. **REASONED from pinned bytes; not executed.** No blocking must-fix.

## Stage 2 — code quality: PASS

Resolver reasons, blocking answers, throws and unusable roots refuse before execution; successful answers alone are cached, and readiness/authorization precede cache use. Original/revised post inputs converge lexically. Shared edit recognition preserves the pre-existing extraction interface and avoids divergent target parsers. New tests invoke registered handlers and assert literal revisions/refusal outputs, not merely fixture state. No changed Python path: `code_grade: n_a`.

## Dismissed candidates / boundaries

- ast_edit mutation-set omission: pre-existing, expressly disclosed; rooting does not introduce or worsen it. Out of scope.
- F1 rootedHooks duplication: previously disclosed flag-only; no new behavioral defect, not reopened.
- Singular ast_edit plan wording: actual `paths: string[]` and DEC-251 govern this supplied correction; not a new finding.
- CRLF edit recognition: the multiline matcher leaves line endings outside matched target text; the pinned mixed-ending test binds literal revised text. No demonstrated defect.
- Blank no-op assertions are accompanied by positive relative/mixed revisions; empty-return implementations fail the positive assertions.

No tests/build/lint/formatters or mutants were run. QA owns final execution of T-01 `python3 tests/unit/test-omp-hooks.py` and T-02 `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md`. Historical red-first/mutation claims remain receipt evidence, not my exercised verification.

Open questions: none. Source/tests/docs unchanged by this review.
