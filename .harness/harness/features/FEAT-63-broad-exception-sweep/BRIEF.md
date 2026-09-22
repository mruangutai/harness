# FEAT-63 broad exception sweep

## Problem

`check-state.py` still has 47 broad exception handlers. They hide unrelated defects behind the same silent or CANNOT RUN behavior as the boundary failures each row actually expects, while repeated subprocess and JSON work makes those boundaries harder to see. The checker therefore cannot distinguish a legitimately unavailable environment from a programming error, and no executable lock prevents broad catches or runner-source reparses from returning.

## Done when — by perspective

**operator**

The checker preserves its established output on the eight `test-check-state*.py` suites while environmental unavailability remains quiet, except that an unavailable `feature_schema` import for INV-23 is explicitly CANNOT RUN instead of silently falling back to a 300-cycle budget.

**code maintainer**

Every `check-state.py` handler catches the real boundary error, repeated environment and runner-source access is consolidated in `Ctx`, repo-module loading exposes one typed failure, and executable controls reject regressions without blocking reductions in legacy broad catches elsewhere.

**reader**

The reason for every deliberately silent handler remains beside that handler, and the consolidation audit states which shared loaders and per-file catch ceilings define the boundary.

## Success criteria

- SC-01 (operator): All eight existing `tests/integration/test-check-state*.py` suite receipts are byte-identical to baseline except a fixture that makes `feature_schema` unavailable reports INV-23 CANNOT RUN instead of using the 300-cycle fallback. — verify: automated (test); evidence: integration
- SC-02 (operator): All twelve checker subprocess calls use one `Ctx.spawn` boundary that returns `None` only for `OSError` or `subprocess.SubprocessError`, GitHub authentication is evaluated once through cached `Ctx.gh_ok`, and the runner reuses `Ctx.git_top`; tests show the previously silent missing-tool paths remain silent. — verify: automated (test); evidence: integration
- SC-03 (code maintainer): Every `Exception` raised during repository-module specification, loader validation, and registered or unregistered execution reaches checker callers as `harness_boundary.RepoModuleError` with its original cause; `KeyboardInterrupt`, `SystemExit`, and other `BaseException`-only process-control exceptions propagate unchanged, registration restoration is preserved, and `check-state.py` contains no `except Exception` or bare `except:`. — verify: automated (test); evidence: unit, integration
- SC-04 (code maintainer): One AST census enforces a zero broad-catch ceiling for `check-state.py`, freezes `harness_boundary.py` at its post-T-01 count when the lock lands, and freezes every unchanged non-check-state `bin/` script at its authoritative per-file `950b2f04` ceiling; a lower count passes, any per-file increase fails, and a mutant that adds one catch produces exactly one finding naming that script. — verify: automated (test); evidence: integration
- SC-05 (reader): The shared-source audit includes `load_feature_json` and `load_harness_json` and rejects a checker reparse of feature or harness JSON instead of consuming `ctx.record` or `ctx.config`. — verify: automated (test); evidence: integration
- SC-06 (reader): Inspection confirms that each existing silence rationale moved byte-for-byte with its narrowed handler and remains adjacent to the code whose quiet behavior it explains. — verify: inspection; evidence: code citation

## Verification gaps

None. The checker suites, boundary unit suite, consolidation audit, and source inspection cover every criterion.

## Constraints

- The behavior baseline is commit `950b2f04ae9d73c6ed2bf5fee261287b396c761f`.
- Preserve the current silent treatment of missing executables, absent GitHub CLI or authentication, non-repository execution, and unreadable optional input; do not turn environmental preconditions into findings.
- `read()` continues to return `None` only for `OSError`, and `station_of` preserves its current empty-string semantics while consuming parsed context.
- The DEC-138 environmental-precondition rationale exists once at `Ctx.spawn`; every other silence rationale moves byte-for-byte with its handler.
- DEC-174 requires main-session-direct execution; no builder or team dispatch is part of this feature.
- DEC-231 governs perspective-tagged success criteria; DEC-232 governs anchored task targets; DEC-179 governs the plan-time lane declaration.

## Out of scope

- Narrowing or otherwise rewriting the legacy broad catches in the other `bin/` scripts; those are a later wave.
- Turning environment-related silence into a finding or making an offline machine fail red.
- Extending the grader or review-skill rubric beyond the consolidation audit and tests named here.

## Approval

status: approved
approved-by: Mike (main session)
date: 2026-09-21
