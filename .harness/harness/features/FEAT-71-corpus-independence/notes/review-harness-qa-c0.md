# QA gate — FEAT-71-corpus-independence, T-01, review_sha 3e6add2af05f5b801afec1ef69440fe54e1529a4 (base 4a05030d401593003209f525fd06e00802eccd36)

## BLUF
PASS. Unit (57 files) and integration (84 files) were both run at the exact pin in a standalone clone and both exit 0. Both required `cross_module` kinds are satisfied. The fail-first reds for SC-02 and SC-03 are reproduced by me against the baseline implementation. Findings are advisory only; one locally-run kind (`omp_session_accessor`) has no recorded run (see Q-1).

## Phase 1 — expected coverage (BRIEF + plan.yaml only, no source)
- SC-02 (unit): no executable id exemption survives; synthetic fixtures for RUNS_AGENT_EXEMPT, BUILD_ENTRY_ERA_EXEMPT, HANDOFF_EXEMPT_LITERAL, both `handoff_done_when_baseline` configs (project + template); `test-plan-depends-on` floor replaced by synthetic non-vacuity; unit live reads independent of corpus size.
- SC-03 (integration): corpus discovery, existing-flow gate, canonical-reader classification, conversion/non-regression run on synthetic data; `test-corpus-real-owner` floor replaced by asserted (not skipped) synthetic non-vacuity; independence assertions red at baseline, green on the five-folder tree.
- SC-01/04/05 are `inspection`: not QA-gated.
All expectations map to a test at the pin. Gaps: see Findings.

## Environment
- Clone: `git clone --no-local --no-hardlinks --revision=<full pin>` into a real-.git `/private/tmp/feat71-qa.1XCu9VpK` (removed after). HEAD = pin, `.git` a directory, exactly the five survivor folders present, `core.hooksPath` set, `refs/heads/main` = pin. A managed sparse pin was NOT used: a sparse worktree masks the five-corpus owner reads (red-first-S2 W-vs-G sections show the same suite differs by layout). `HARNESS_AGENT_TYPE` unset for the runs (G-07).
- Full stdout/stderr (kept): `/private/tmp/feat71-qa-unit.log` (2204 lines), `/private/tmp/feat71-qa-integration.log` (5837 lines).

## Matrix (harness.json: cross_module.always = [unit, integration]; plan T-01 change_type cross_module — vocabulary valid)
| kind | command (at pin clone root) | files discovered | result |
|---|---|---|---|
| unit | `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` | 57 | `pool: 8 workers, 57 files, 20.11s wall`, `exit=0`; 57 `-----` headers, none non-zero |
| integration | `python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration` | 84 | `pool: 8 workers, 84 files, 131.63s wall`, `exit=0`; 84 headers, none non-zero |

57 + 84 = 141, equal to the builder's all-kind receipt (`merge-3e6add2a….log`: `141 files`). I did not rerun `--kind all`; the standing builder receipt is a reference only.
Unit `FAIL` tokens in the log are only `test-factory-claim-mutation.py`'s deliberate mutation-proof prints (`MUTATION PROOF: 3/3 cases reddened`, `KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed`; G-09); graded on exit code.
Standalone detail: `test-corpus-real-owner` announces a SKIP only for the linked-active-worktree caller leg (there is none in a plain clone); the owner leg and the synthetic legs ran (`Ran 8 tests … OK`, verbose re-run: `test_the_walk_reaches_every_fixture_directory ok`, `test_an_empty_walk_is_rejected ok`). `test-corpus-non-regression` `Ran 7 tests … OK`, no skipped test (verbose re-run).

## Fail-first, reproduced independently (baseline implementation 4a05030d + pin's test files, `restore --source=<pin>`; env as red-first receipts)
Real RED, named assertion, intended dependency (not import/setup/arg error — each ran to its assertion with exit 1):
- SC-02 `tests/unit/test-feature-schema-build-entry.py` exit 1: `FAIL FEAT-71 feature_schema holds no per-feature id table {RUNS_AGENT_EXEMPT: 33 ids, BUILD_ENTRY_ERA_EXEMPT: 75 ids}`; `FAIL BE-02 … 150 short-circuited`; `FAIL BE-10 no receipt allows no merge … 150 allowed`; `FAIL FEAT-71 a runs entry without agent is refused at index 0 … 33 exempt`.
- SC-02 `tests/unit/test-gh-sync-build-entry.py` exit 1: `FAIL BE-31 … 75 not refused`; `FAIL BE-32 … 75 exempt`.
- SC-02 `tests/unit/test-feature-corpus-discovery.py` exit 1: `test_no_exemption_mechanism_exists … Lists differ: ['entries','exempt'] != ['entries']`.
- SC-02 (HANDOFF_EXEMPT_LITERAL + baseline config) `tests/integration/test-check-state-handoff.py` exit 1: `FAIL case (g.2)`, `case (g.3)` (prefix exemption), `case (t14-g)`, `FAIL FEAT-54 no harness.json names a feature-folder path (146 found)`.
- SC-03 `tests/integration/test-check-plan-routes.py --canonical-reader-self-test` exit 1: ten FAILs incl. `canonical_reader_planless_rows_read_no_plan`, `canonical_reader_planless_row_is_not_an_ownership_finding` (`T-02 task files omit this source`), `canonical_reader_audit_holds_without_a_feature_corpus`, `canonical_reader_live_audit_is_zero`.
Receipts (builder, retained): `notes/red-first-S1a.md` (all unit/integration reds above, incl. test-validate-feature-json T15-B 33 exempt, test-merge-gate T-05, test-post-merge-sweep T-07), `red-first-S1b.md`, `red-first-S2.md` R1/R2 (R2 = baseline test files vs committed deletion: `test-plan-depends-on` `4 files found, floor 67`; `test-corpus-real-owner` `AssertionError: 4 not greater than 70`; `test-factory-cli` FileNotFoundError FEAT-10; `test-feature-json-budget` FEAT-54), `red-first-s3.md` §C, `red-first-s4.md`.
Grade fix (S2 §Grade fix, CR-01): `test-code-grade.py` is in the unit run (`exit 0`); `check-plan-routes.py` helpers `_route_finding`, `_classification_task_files` split; the three target functions graded 3/3/2 before, 5/5/4 after, no allowlist edit. Behavior-preserving; its evidence is the same unit/integration suites green at the pin (`test-check-plan-routes.py exit 0`, `test-code-grade.py exit 0`). Only the builder's own evidence plus this rerun examined it.

fail_first tiers: SC-02 natural RED (new test vs baseline implementation) — semantic, not signature-absent, for BE-*, discovery and handoff. SC-03 natural RED for canonical-reader and, via the baseline test failing against the deleted corpus (R2), for the two floors.

## Findings (all advisory; task T-01)
1. kind=form, sev=low — SC-02's `evidence: unit` is carried partly by integration tests: HANDOFF_EXEMPT_LITERAL and the `handoff_done_when_baseline` assertions live in `tests/integration/test-check-state-handoff.py`, not `tests/unit/`. Unit and integration both pass, so the matrix is unaffected; the reds are real. Scenario: someone reading SC-02 as "unit only" finds no unit test for the handoff exemption.
2. kind=substance, sev=low — no red is possible, per the builder, for: `test-check-state-records.py` INV-37 (replacement assertion passes at baseline; only a converse run against the new implementation reddens the OLD file — red-first-S1b); `test-check-domain-post.py`; the template `harness.json` half of `handoff_done_when_baseline` (the template never carried the key; the test at `test-check-state-handoff.py:343` asserts both files but only the project file can ever have gone red). Those cases are evidence of intent, not discriminating tests. Scenario: re-adding a template baseline key would be caught only by the 343 loop, never shown to fire.
3. kind=substance, sev=low — `test_an_empty_walk_is_rejected` (`test-corpus-real-owner.py`) compares an emptied clone against a populated owner, so it proves mismatch detection; the real non-vacuity guard is `test_the_walk_reaches_every_fixture_directory` (exact set equality to `FIXTURE_DIRS`). The pair is sound; the first test name over-claims. I did not run a mutation proof on either.
4. kind=text-vs-intent (O-04), sev=low — SC-03 literally says "without … live-corpus reads", but `test-corpus-real-owner` (RealOwner), `test-plan-depends-on` case 9 and `canonical_reader_live_*` still read the live tree (integrity only, no size floor). The BRIEF's own wording ("pass on the retained five-folder corpus") and the grilling make this intent-satisfied; reported as text-unmet-but-intended, not a defect.
5. kind=proportionality, sev=info — two removed behaviours I checked only by pin diff and the suites above: kaya now falls under the uniform INV-17/INV-37 rules (no current violation per builder; I did not rerun a kaya check); `--conversion-manifest` CLI removal has no remaining reader (`grep` of tests and skills at the pin finds none).

## Open questions
- Q-1 (non-blocking, lead decides): `test_kinds.omp_session_accessor` is `locally_run` and its `detect` file `tests/manual/probe-omp-session-accessor.py` is changed (PROBE path repointed) and the extension moved. verification-rules require a recorded run under `notes/` for a touched locally_run surface. None exists. The signed BRIEF "Verification gaps" says relocation claims no fresh live run. My static check: moved `probe-session-accessors.ts` blob `e8df5c44b0ef8e3172e5c3055d6b0b6a2b26291d` equals the baseline evidence blob; `PROBE = ROOT / "tests/manual/probe-session-accessors.ts"` resolves. I treated the BRIEF's explicit acknowledgement as the exemption; the lead may disagree and BLOCK instead.

## Principles applied
Not loaded this run (no craft leaf read); none cited.
