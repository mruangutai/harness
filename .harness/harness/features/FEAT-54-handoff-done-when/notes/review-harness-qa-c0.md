# QA gate — FEAT-54 handoff Done when — review `e75767df`

## BLUF

**FAIL.** The configured unit and integration matrix is green with non-empty discovery (24 unit files, 44 integration files), and SC-07/08/09/11 pass their prescribed automated/inspection procedures. SC-04 fails because the exact review-time state command exits 1 on an existing handoff violation. No output line names `Done when`, but SC-04 requires both exit 0 and no such line. SC-10 remains pending operator UAT and is not marked met.

## Phase 1 expectations and delta

Before reading implementation, BRIEF/plan required: unit coverage of block shape, all four authority grammars/resolvers, resolve-on/off separation, AND semantics, and invalid authority types; integration coverage through both real gates for missing/valid/malformed/edit/cap behavior, frozen-baseline behavior, no persisted target re-resolution, no per-section cap, and SC-09 registration/isolation; review-time corpus and source inspections for SC-04/07/08/11. Phase 2 found each expected permanent test. The only gate gap is the live-corpus SC-04 failure below; SC-10 is intentionally UAT-only.

## Matrix

Diff-inferred types are `logic`, `cross_module`, `config` with `touches_config_shape`, `docs`, and `scaffolding`. Logic and cross-module changes require unit; cross-module and the new config container consumed by `check-state.sh` require integration. Docs/scaffolding add no kind. Commands were run from the assigned worktree with `HARNESS_AGENT_TYPE` unset:

| Kind | State | Command | Exit | Discovery |
|---|---|---|---:|---:|
| unit | satisfied | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | 24 files |
| integration | satisfied | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | 44 files |
| handoff_comprehension | locally-run, not executed in this review | `tests/manual/probe-handoff-comprehension.py` | n/a | n/a |

The manual probe is absent from `test_matrix`; per the dispatch and SC-09 it was assessed through integration coverage, not nondeterministically executed. `tests/integration/test-run-unit-tests-kinds.py:21-40,69-98` positively checks the real registration, discriminates removal/empty detect, proves `--kind all` executes non-empty unit and integration controls, and proves the manual probe does not execute.

## Success-criterion evidence

- SC-01: `tests/integration/test-check-domain.py:4030-4032` (missing refusal plus valid allow).
- SC-02: `tests/integration/test-check-domain.py:4033-4043` (five separately named malformed shapes).
- SC-03: `tests/integration/test-check-domain.py:4044-4057` (resolving/unresolvable pair for each authority type).
- SC-04: **FAIL** — exact root command `bash .claude/skills/harness/bin/check-state.sh` exited **1**. Its first line was `VIOLATION FEAT-51-claude-code-lifecycle-safety: status is 'done' but notes/handoff-validate.md is missing`. A separate exact-output search found **zero** lines naming `Done when`.
- SC-05: `tests/integration/test-check-domain.py:4077-4081` (60 allowed, 61 refused with cap message).
- SC-06: `tests/integration/test-check-domain.py:4063-4076` (edited missing section refused; compliant edit allowed), plus `tests/integration/test-check-state.py:2188-2197` for baseline/present-shape behavior.
- SC-07: **PASS inspection at review SHA.** `git show` source has the write-gate import/call only at `.claude/skills/harness/bin/check-domain.sh:1562,1567` with `resolve=True`, and the state-gate import/call only at `.claude/skills/harness/bin/check-state.sh:54,1251` with `resolve=False`. Full gate-source search found no second Done-when body parser or target reader.
- SC-08: **PASS inspection at review SHA.** Presence controls: template `.claude/skills/harness/templates/HANDOFF.md:4,37-40`; playbook `.claude/skills/harness/SKILL.md:311-315`; decision record `.harness/harness/docs/DECISIONS.md:3699-3713,6698-6701`; write gate `.claude/skills/harness/bin/check-domain.sh:1547-1558`; state gate `.claude/skills/harness/bin/check-state.sh:1069-1070,1213-1214`. Searches for current four-section claims found none. The surviving `check-state.sh:1199` and `:1218` mentions are the two SC-08 historical exemptions; `DECISIONS.md:3765` likewise describes the historical first live four-section handoff rather than current contract.
- SC-09: **PASS automated** — `tests/integration/test-run-unit-tests-kinds.py:21-40,69-98`, executed inside the 44-file green integration kind. The real probe was not run.
- SC-10: **PENDING OPERATOR UAT** — not met by this review.
- SC-11: **PASS inspection.** `git merge-base main e75767df...` returned `0ec44965...`. The primary `comm -12` printed nothing. The positive `comm -23` printed exactly two non-empty paths: FEAT-54 `handoff-build.md` and `handoff-plan.md`. The added-only arm printed the same two paths; `diff` between the sorted sets exited 0 with no output.
- SC-12: `tests/unit/test-handoff-done-when.py:85-91` (four resolving accepted; same block with one bad refused exactly once).
- SC-13: `tests/integration/test-check-domain.py:4058-4062` (unknown prefix and bare source location each refused with all four prefixes).
- SC-14: `tests/integration/test-check-domain.py:4077-4082` and `tests/integration/test-check-state.py:2215-2227` (60-line long-section cases accepted through both gates).
- SC-15: `tests/integration/test-check-state.py:2188-2197` (absent targets stay clean; malformed shape and grammar remain reported).

## Finding

### F-QA-01 — SC-04 review-time state gate is red

- **Severity:** high
- **Concrete failure scenario:** entering Harness at the pinned commit runs `check-state.sh`, receives exit 1, and blocks orchestration before this feature can be treated as state-clean. SC-04 is therefore false even though the new Done-when-specific corpus portion emits no line.
- **Evidence:** exact required command above; first output line names missing `.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/notes/handoff-validate.md`; SC-04 contract at `BRIEF.md:89-101` requires exit 0.
- **Owner lane:** **Main direct corpus/state reconciliation**. If the remedy changes `.claude/skills/harness/bin/check-state.sh`, `handoff_done_when.py`, gate tests, or `run-unit-tests.sh`, it is **Main direct mutation under DEC-174**.

## Test-first audit

History shows partial compliance. `tests/integration/test-check-state.py` landed in `9d4d03c` before state-gate implementation `fd98b16`. However, `handoff_done_when.py`, `check-domain.sh`, and their unit/integration tests first appear together in `157377d`, while the SC-09 config/probe landed in `a3e0e8b` before its registration/isolation test `ec0f897`. Those sequences do not preserve independently recorded RED-before-production evidence. Per the verification rules this is an audit finding, not an additional matrix failure.
