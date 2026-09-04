# FEAT-54 build QA gate — c2

## Verdict

**PASS.** At current HEAD `2ac5fe958319f9dfbcd4eb68e60016e8e95eaa48`, both configured required kinds pass, discovery is non-zero, and the sole c1 defect is repaired. The five-Authority integration case now requires the exact count-bearing refusal fragment `has 5 Authority: lines`; the shared header `handoff shape (DEC-159).` cannot satisfy that assertion. No adequacy or TDD must-fix remains.

## Phase 1 expectations and current delta

From the approved BRIEF and `plan.yaml`, before inspecting implementation, expected coverage was: unit coverage for shared block parsing, pointer grammar/resolution, AND semantics, and resolve-mode behavior; integration coverage for the real write and persisted-state gates, including each malformed count, all four authority types, edit enforcement, whole-file cap/no per-section cap, persisted no-re-resolution, and manual-probe registration/exclusion. The current suites contain those named cases. The only c1 delta was the under-bound five-Authority integration assertion; current HEAD changes that assertion (and the other count assertions consistently) without changing production code. No Phase 1 expectation is uncovered.

## Matrix evidence

`HARNESS_AGENT_TYPE` was removed from the environment for all invocations because the repository agent environment contaminates this runner, as established in c1. Command arguments and test selection were unchanged.

| Kind | Exact configured command | Result | Discovery and changed-contract evidence |
|---|---|---|---|
| unit | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | exit 0 | 24 files discovered; `test-handoff-done-when.py` ran and all 32 named cases passed, including `five authority`, `four authorities accepted`, and `all authorities required`. |
| integration | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | exit 0 | 44 files discovered; zero failed scripts. `test-check-state.py` ran and all 11 FEAT-54 cases passed; the registered integration bucket includes the repaired `test-check-domain.py`. |

Narrow discovery/execution confirmation: `python3 tests/integration/test-check-domain.py` exited 0 and printed all 22 named FEAT-54 handoff cases, including `handoff five Authority`. This establishes that the changed file executes and that the relevant case is not merely present on disk.

## SC-02 non-vacuity

The c1 failure mechanism was an assertion for the bare digit `5` over all stderr, which could be satisfied by the common `DEC-159` header. Current HEAD instead passes the single needle `has 5 Authority: lines` for the five-Authority fixture (`tests/integration/test-check-domain.py:4033-4043`). The production formatter emits the detail `## Done when has 5 Authority: lines; expected between 1 and 4` (`.claude/skills/harness/bin/handoff_done_when.py:115-119`), while the caller separately prepends `handoff shape (DEC-159).` (`.claude/skills/harness/bin/check-domain.sh:1568-1570`). Because `record` requires the full needle in lowercased stderr (`test-check-domain.py:3996-4001`), the header's digit cannot satisfy the case; omitting the count detail, changing 5 to another count, or emitting only the header makes the assertion false. The narrow real-hook run passed the named `handoff five Authority` case.

## Automated success-criterion evidence

- SC-01: `tests/integration/test-check-domain.py:4030-4032` — missing and valid Done-when write pair.
- SC-02: `tests/integration/test-check-domain.py:4033-4043` — five separate malformed-block refusals with exact count-bearing fragments.
- SC-03: `tests/integration/test-check-domain.py:4044-4057` — resolving/unresolvable pair for each authority type.
- SC-05: `tests/integration/test-check-domain.py:4077-4081` — exact 60/61-line boundary pair.
- SC-06: `tests/integration/test-check-domain.py:4063-4076` — edit without/with Done-when pair.
- SC-09: `tests/integration/test-run-unit-tests-kinds.py:21-40,69-98` — exact live registration, missing/empty mutants, and `--kind all` exclusion.
- SC-12: `tests/unit/test-handoff-done-when.py:89-94` — four resolve versus one unresolved authority, distinguishing AND from ANY.
- SC-13: `tests/integration/test-check-domain.py:4058-4062` — unknown prefix and bare source location, requiring all four legal prefixes.
- SC-14: `tests/integration/test-check-domain.py:4077-4082` and `tests/integration/test-check-state.py:2215-2227` — 60-line long-section note accepted by both gates.
- SC-15: `tests/integration/test-check-state.py:2182-2197` — absent targets remain unreported while shape and grammar remain enforced.

Inspection- and UAT-verified criteria are outside this matrix gate; no automated criterion lacks a named test.

## TDD assessment

The original behavioral implementation's TDD evidence remains adequate at current HEAD. The executor record (`notes/tdd-executor-record.md:3-18`) records same-session RED-before-GREEN for T-01/T-02, T-03/T-04, and T-06/T-07; it explicitly identifies the observed import failure and the two integration RED runs rather than recreating RED after implementation. Since c1's pin, `git diff d32df480271390e3bfdfc8e3ca921f0c9b695ed4..HEAD` changes only the integration count assertions plus orchestration metadata, not production behavior. The c2 repair strengthens an existing test oracle; it introduces no behavioral production change requiring a new test-first cycle. No TDD must-fix remains.

## Ranked residual must-fix

None.

No blocking open question remains.
