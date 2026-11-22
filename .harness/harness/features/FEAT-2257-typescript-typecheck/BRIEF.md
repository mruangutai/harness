# BRIEF — FEAT-2257 TypeScript typecheck

## Problem

Maintainers can merge TypeScript changes without a compiler checking the OMP extensions or their tests. At 120b131f the configured typecheck kind was unresolved and a scratch strict compiler run found eight errors in tests/unit/omp-hooks.test.ts; runtime tests alone did not surface them. Source: the operator-settled grilling artifact, not a production typecheck run by this planning team.

## Done when — by perspective

**operator** — I can rely on every pull request being refused when the repository's TypeScript does not typecheck, without changing the tests a task must write or bypassing Harness's execution boundary.

**code maintainer** — I can install and run the same pinned compiler locally and in CI, including on tests, and receive reviewed dependency updates. Static source coverage does not turn production sources into test code or break test-layout checks; existing hook assertions keep their meaning and the documented upgrade procedure remains reproducible.

**reader** — I can distinguish a command actually observed passing from an invented configuration, and audit the checked source set, committed configuration and remaining typing limitations.

## Success criteria

- SC-01 (code maintainer): The merge tree passes strict, no-emit checking of every git-tracked .ts file, including .omp/extensions/harness-hooks.ts, .omp/extensions/digest-schema.ts, tests/unit/omp-hooks.test.ts and tests/manual/probe-session-accessors.ts. QA demonstrates the compiler's failing state before the eight fixture errors are repaired; the integration regression independently enumerates tracked files, asserts each is in the compiler's file list, rejects compiler-suppression comments across that source set, and demonstrates one representative temporary type error makes the configured command fail.
  verify: automated evidence: integration
- SC-02 (code maintainer): Reading git show <review_sha>:package.json, git show <review_sha>:bun.lock and git show <review_sha>:tsconfig.json shows exact dev-only direct pins for typescript and @types/bun, a committed matching lockfile, a local compiler command, strict checking and no emission; no additional direct JS dependencies are introduced.
  verify: inspection
- SC-03 (operator): Reading git show <review_sha>:.github/workflows/tests.yml and its pinned CI logs shows bun install --frozen-lockfile before typecheck in checks and before the compiler-dependent integration regression in integration-shards. Dependency installation failure cannot be ignored or regenerate the lockfile.
  verify: inspection
- SC-04 (code maintainer): Reading git show <review_sha>:.gitignore and pinned-tree git check-ignore evidence shows node_modules/ ignored while package.json, bun.lock and tsconfig.json remain trackable.
  verify: inspection
- SC-05 (code maintainer): Reading git show <review_sha>:.github/dependabot.yml shows a bun ecosystem update entry for the repository root on a weekly schedule, preserving any pre-existing entries.
  verify: inspection
- SC-06 (operator): Reading git show <review_sha>:.github/workflows/tests.yml and pinned PR run evidence shows an unconditional typecheck step in checks on every pull_request, with no path filter, continue-on-error or success fallback. The required integration job still needs checks and integration-shards, retains its context identity, and refuses failed checks. A deliberate temporary type error is observed failing the same command before the clean merge tree passes.
  verify: inspection
- SC-07 (reader): Reading git show <review_sha>:.harness/harness.json shows test_kinds.typecheck active, cmd equal to the command actually executed, existing detect/exclude preserved, classifies_tests false, and _reason deleted. Reading git show <review_sha>:.claude/skills/harness/templates/harness.json shows the same broad typecheck detect and classifies_tests false without activating the template. A durable execution receipt records command, source/revision identity, exit 0 and output before activation, plus the capability precondition passing before the status flip; final pinned-tree evidence records the active command passing. Missing compiler/configuration never counts as a pass. Reading git show <review_sha>:.harness/harness/docs/DECISIONS.md shows DEC-213 separates source detection from test classification, documents the default-true capability and its mechanical consumers, permits static typecheck of manual sources without execution, and retains the normal-runner execution ban.
  verify: inspection
- SC-08 (operator): Comparing git show <review_sha>:.harness/harness.json with the feature's recorded pre-implementation base proves test_matrix and _matrix_provenance unchanged; no row acquires typecheck.
  verify: inspection
- SC-09 (code maintainer): The existing Bun hook suite passes with all existing runtime assertions retained. The eight compile errors are repaired through accurate test-fixture types/literal narrowing, not removed assertions, compiler suppression, weakened strictness or new any casts. QA records the compiler red-first separately; this existing runtime suite is a non-regression check, not a claim that previously passing assertions failed first.
  verify: automated evidence: unit
- SC-10 (reader): Inspection of git show <review_sha>:tests/unit/omp-hooks.test.ts and the pinned implementation diff confirms no changes to the production pi/ctx:any API typing, no new JS dependencies beyond typescript and @types/bun, and no linter or formatter adoption.
  verify: inspection
- SC-11 (code maintainer): Reading git show <review_sha>:README.md shows frozen installation, the exact local typecheck command, complete tracked-source coverage, the OMP-any limitation, weekly dependency updates, and bun update followed by committing reviewed package.json/bun.lock changes and rerunning verification. Reading git show <review_sha>:.harness/harness/docs/SPEC.md shows its TypeScript host-tool verification-gap paragraph reflects the verified active typecheck while retaining the pi/ctx:any live-host API limitation and the need for executable host/boundary evidence.
  verify: inspection
- SC-12 (operator): Reading git show <review_sha>:.harness/harness/features/FEAT-2257-typescript-typecheck/plan.yaml and execution receipts shows hook tests, compiler and capability regressions, both code_grade path spellings, suite-layout classification, template/live configuration, CI enforcement and activation executed main-session-direct inside the feature worktree, never through the enforcement being changed.
  verify: inspection
- SC-13 (code maintainer): Synthetic unit regressions prove a matching active or locally_run kind with classifies_tests false does not classify its source as test code; absent or true preserves existing classification and status/exclude semantics. Synthetic hygiene_uncertified assertions skip flagged broad patterns but retain their absent-flag failure. offenders() and select_control_candidate() inherit the matcher policy, and existing live-config suite-layout assertions pass after activation. QA demonstrates the new unit assertions fail first; a durable pre-capability receipt runs offenders()/hygiene_uncertified() against a config copy with active typecheck and no flag, recording the production-source offenders and uncertified broad patterns, not an actual TypeScript grading downgrade.
  verify: automated evidence: unit

## Verification gaps

- typecheck currently has cmd: null and status: unresolved. SC-01 rests on the existing runnable integration kind, SC-09/13 on unit, and SC-02/03/04/05/06/07/08/10/11/12 on pinned-artifact inspection; no criterion rests on the unresolved kind. T-04 closes source issue #2257 by running the real command successfully before activating it. Planning does not claim that production typecheck has passed.
- A PR can edit its own workflow, so this work does not independently protect the typecheck step from deletion. SC-06 is pinned workflow/run inspection, not a new self-protecting workflow guard; DEC-183's accepted limitation remains.
- The compiler cannot validate OMP's real extension API through existing pi/ctx:any. SC-10 preserves the operator's explicit exclusion; unit tests and this compiler do not claim live-host API compatibility. No browser/component surface is changed.
- ALTITUDE-1 is resolved by Main's operator-delegated advisor approval, recorded in runs/r-20261122-1-plan-product/altitude-ruling-c1.md, not by independent product design. T-04 owns the default-true classifies_tests capability, both code_grade path spellings, local suite-layout filter, both synthetic unit regressions and live/template false values, with an explicit passing capability precondition before activation. The live activation defect is suite-layout offenders()/hygiene_uncertified(); TypeScript complexity-bar misclassification is latent because code_grade currently selects only changed Python files. SC-13 proves classifier behavior, not a currently reachable TypeScript grade downgrade. The broad detect remains truthful source coverage; narrowing it was rejected for false coverage, not because QA maps files through detect.

## Constraints

- Source of scope: /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-typescript-typecheck-2026-11-22.md, settled observations at 120b131f. Every tracked .ts file and all eight current test errors are in scope (SC-01/09).
- Exact dev-only dependency pins, package.json, bun.lock, tsconfig.json, frozen CI installation, node_modules/ ignore and weekly bun Dependabot updates are operator-settled constraints (SC-02/03/04/05).
- DEC-98 and DEC-187 SUPPLY honest command activation and loud unresolved-runner semantics; .harness/harness.json _test_kinds_note requires an observed pass before filling cmd and removal of _reason (SC-07).
- DEC-35 and DEC-212 SUPPLY the existing task test floor. DEC-217 plus the operator's explicit ruling BLOCK test_matrix or provenance edits; CI, not a fail_first matrix entry, enforces every PR (SC-08).
- DEC-183 SUPPLIES the required integration context and accepted workflow self-protection limit. Reuse checks and its existing Bun setup; preserve the aggregator's dependency/result chain (SC-03/06).
- DEC-174 BLOCKS execution through changed enforcement, including gate tests; DEC-179 SUPPLIES declared main-session-direct routes for ungranted files (SC-12). All implementation edits remain in /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2257-typescript-typecheck.
- DEC-213 SUPPLIES directory-selected unit/integration discovery. The compiler regression belongs under tests/integration/; capability regressions belong in the existing tests/unit/ suites, without another registration system (SC-01/13). Main's approved D-01 amendment separates classifies_tests (boolean, absent means true) from source detection, documents both mechanical consumers and permits static checking of manual sources without execution. DEC-188/205 SUPPLY current-text rewrites, not a wholesale strike, new decision number or historical appendix (SC-07). T-04 owns DECISIONS.md, regenerated DECISIONS-INDEX.md and the targeted SPEC correction (SC-11). No upgrade-config.py edit: additive merge already supports the key; update _test_kinds_note only if it enumerates kind fields.

## Out of scope

- Typing the hooks' pi/ctx: any parameters against OMP's real extension API: that needs OMP's own type package and is a separate ticket if wanted.
- Adding typecheck to any test_matrix row (operator ruled no).
- Any other JS dependency, linter, or formatter.

## Approval

status: approved
approved-by: fable-advisor (delegated by Mike Ruangutai)
date: 2026-11-22
