# Code review — FEAT-63 — c0

**FAIL.** Stage 1 found an SC-06 mismatch at pinned SHA `4066581f6cec2d6eab1fc5094740c13a8d144d7f`; per the review protocol, stage 2 did not proceed. Review range: `950b2f04ae9d73c6ed2bf5fee261287b396c761f..4066581f6cec2d6eab1fc5094740c13a8d144d7f`. The only working-tree change was post-pin `feature.json` metadata and was excluded. No `[harness:human]` commit is in the range.

## Stage 1 — spec compliance

- **SC-01 PASS.** All eight signed checker suites passed at the pin. The ruled INV-23 case passes at `tests/integration/test-check-state-feat59.py:1027-1043`: an unimportable `feature_schema` emits one NOTE-level CANNOT RUN and no 300-line fallback.
- **SC-02 PASS.** `Ctx.spawn` catches only `OSError`/`subprocess.SubprocessError` and retains the DEC-138 silence at `.claude/skills/harness/bin/check-state.py:562-575`; cached `gh_ok`, `git_top`, and the accepted eleven-plus-bootstrap split are at `:546-583`. The eight checker suites passed.
- **SC-03 PASS.** `RepoModuleError`, load-by-name/path, registration restoration, and call wrapping are at `.claude/skills/harness/bin/harness_boundary.py:369-440`; process-control exceptions escape because both wrappers catch `Exception`, while registered execution restores in the inner `BaseException` branch. The boundary unit gate passed, including registered/unregistered load failures, by-name import, call failure, registration restoration, `KeyboardInterrupt`, and `SystemExit`. The consolidation census reports zero broad catches in `check-state.py`.
- **SC-04 PASS.** One AST census and per-file ceilings are at `.claude/skills/harness/bin/check-plan-routes.py:2141-2223`; `harness_boundary.py` is frozen at the accepted count 6. Mutants for both checker syntaxes, legacy +1/-1, non-transfer, and an unlisted script pass at `tests/integration/test-check-plan-routes.py:2755-2801`. The live audit returned `0 consolidation finding(s) under bin/`.
- **SC-05 PASS.** Both JSON loaders are in `_SHARED_SOURCE_LOADERS` at `.claude/skills/harness/bin/check-plan-routes.py:1789-1794`, with discriminating mutants at `tests/integration/test-check-plan-routes.py:2741-2753`; the consolidation gate passed. `Ctx.record_error` reuse is at `.claude/skills/harness/bin/check-state.py:774-776`.
- **SC-06 FAIL (inspection, not inferred from tests).** The pre-existing silence rationales were checked against baseline `950b2f04`:
  - GitHub authentication: baseline `check-state.py:3088-3095`; wording is retained beside the narrowed shared handler at current `check-state.py:562-575` (moved from `_inv26_gh_ok` into `Ctx.spawn`). **PASS.**
  - INV-30 duplicate-report suppression: baseline `check-state.py:3453-3457`; the two-line rationale is unchanged and adjacent to the new `ctx.record` guard at current `check-state.py:3454-3459`. **PASS.**
  - INV-24 duplicate-report suppression: baseline `check-state.py:2413-2416` said `the parse failure is already a violation elsewhere; do not double-report`; current `check-state.py:2458-2461` changes it to `absent, or the parse failure ...`. It is adjacent, but not byte-for-byte. **FAIL.**
  - Era-config silence: baseline `check-state.py:671-674` said `The JSON-validity violation is raised on its own merit further down (`cj`).`; current `check-state.py:713-716` replaces it with new prose (`No config, or one that does not parse ...`). It is adjacent to the replacement guard, but not byte-for-byte. **FAIL.**

### Finding

- **CR-01 — med — substance — code-reviewer — T-02 / `.claude/skills/harness/bin/check-state.py:713-716,2458-2461`**: two pre-existing silence rationales were rewritten rather than moved byte-for-byte, violating SC-06 and T-02. **Failure scenario:** a maintainer comparing the narrowed handlers with their established quiet-behavior contract cannot distinguish preserved rationale from newly broadened `absent` behavior; the signed inspection criterion therefore cannot certify that narrowing alone changed. Restore the original rationale bytes adjacent to each new guard (additional separate prose may explain the new absent case).

Spec violation: `mismatch`, `.claude/skills/harness/bin/check-state.py`, `SC-06`.

## Stage 2 — code quality

**Not performed:** Stage 1 failed, and the protocol forbids proceeding. The mandatory mechanical code-risk audit was run separately for digest integrity: all 28 changed Python functions passed their applicable bars (`code_grade: pass`).

## Scoped gates

- `python3 tests/unit/test-harness-boundary.py` — ALL PASS.
- Eight signed `tests/integration/test-check-state*.py` suites — ALL PASS.
- `test-check-state-table.py`, `test-check-plan-routes.py`, and live `--consolidation-audit` — ALL PASS; zero live findings.
- `code-grade.py --base 950b2f04... --head 4066581f...` — PASSING: 28.
