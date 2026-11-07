# QA gate — BUG-2180 T-01 @ 556a23ffea8dafcf5110e80fe25a42ee2542ff2b (base 4a05030d)

**Verdict: PASS.** Matrix satisfied (unit + integration), literal T-01 verify green in 5.97 s, every automated SC has fail-first evidence reproduced by me against a base bin. Pinned checkout `.pins/BUG-2180-inv26-fleet-routing--validate-c0--harness-qa` (HEAD verified = pin). No source/test edits.

## Phase 1 expectations (source-blind, from BRIEF/plan)
SC-01 bound-only routing + misplaced twin + distinct repos sharing a number + owner-sync-off; SC-02 mixed owner/bound run with owner controls kept; SC-03 GhError (unresolved-issue) -> CANNOT VERIFY naming feature+error, others still compared; SC-04 unresolvable binding -> CANNOT VERIFY, no owner fallback, healthy feature compared. All map to a test (below); no Phase 1 gap except two minor notes.

## Matrix (product `.harness/harness.json`)
- T-01 change_type `bugfix`: `when unit if touches_runtime_code` (board.py is runtime code -> TRUE), `integration if fix_confined_to_tests_and_contract_docs` (FALSE, code touched; integration still run per assignment and covers the behavior), `__bug_class__` placeholder (unresolvable, no-fire).
- unit: `run-unit-tests.py --kind unit` -> exit 0, "pool: 8 workers, 57 files, 24.93s", every discovered file attributed (runner self-check lines 1985-1986). The 4 `FAIL BUG-1290 5a/5b/5c` lines are the deliberate mutation-proof output of test-factory-claim-mutation.py (known; graded on exit code).
- integration: `run-unit-tests.py --kind integration` -> exit 0, "84 files, 157.71s", `test-check-state-inv26.py (exit 0, 13.73s)` included.
- Discovery semantics: directory-split (tests/unit vs tests/integration); runner validates layout first and attributes every discovered file; counts are files, one PASS per script (not cases).
- Adequacy note (not a gate failure): no tests/unit file binds INV-26 routing (grep: only a prose mention in test-config-shape-matrix.py). Per DEC-217 the unit floor is the unit kind running green for a code bugfix; a ceremonial unit copy is explicitly rejected. Behavioral evidence is integration only.
- `locally_run` kinds: none touched (change surface is check_state/board.py, no inflight/handoff/issue-type surface).

## T-01 literal verify
`python3 tests/integration/test-check-state-inv26.py` -> exit 0, 37 `ok`, 0 `FAIL`, wall 5.97 s (<60 s). Cases x.1..x.6 all `ok`. (Under the full runner, 13.73 s under load.)

## SHA equivalence
`git diff --quiet 554f219e 556a23ff -- board.py test-check-state-inv26.py` -> exit 0: both code files at the review pin are byte-identical to build seam 554f219e. Pin-vs-seam delta is feature.json only (pin registration). Test file at pin is also identical to f1032619 (test-first commit): the tests that went red are the tests that pass.

## Build-note claim validation
- f1032619 touches ONLY `tests/integration/test-check-state-inv26.py` (+244/-1); `git diff --quiet 4a05030d f1032619 -- .claude/skills/harness/bin` -> unchanged (base board.py intact). Claim confirmed.
- Reproduced RED myself: scratch base bin (`git archive 4a05030d .claude/skills/harness/bin` -> /tmp/bug2180-base, board.py verified identical to base blob) + `CHECK_STATE_BIN=/tmp/bug2180-base/.claude/skills/harness/bin/check-state.py python3 tests/integration/test-check-state-inv26.py` (pinned test file): **exit 1, 31 `ok` (old v/w controls), 6 `FAIL` = x.1..x.6**. Matches the build note's 31 passing / x.1-x.6 failing / exit 1; final 37 ok matches.
- Failure kind is semantic (not setup/import): x.1/x.2/x.5 `factory_gh.GhError ... Could not resolve to an Issue` traceback with owner `org/repo` asked `[14,16,17]`; x.3 `calls=[]` (bound feature never checked with owner sync off); x.4 `by_repo={'org/repo': {16,17,40,41}}` (bound numbers unioned into owner read); x.6 `owner_asked={16,17,40,41}` (owner fell back). No ImportError/ModuleNotFound/collection error.

## fail_first (natural RED at the base bin; tier: natural red, pre-fix code, named test)
Evidence command/output: the red run above (exit=1, lines quoted here): `FAIL - (x.1) a bound feature's cards are read from its own repository...`, `FAIL - (x.2) a misplaced bound card is a VIOLATION...`, `FAIL - (x.3) with owner sync off...`, `FAIL - (x.4) mixed owner and bound features...`, `FAIL - (x.5) a failed board read is CANNOT VERIFY...`, `FAIL - (x.6) an unresolvable binding is CANNOT VERIFY...`.
- SC-01: x.1 (test-check-state-inv26.py:732-744), x.2 (746-757), x.3 (759-770: owner sync off), x.4 (772-790: shared number 41 across repos).
- SC-02: x.4 (772-790, mixed owner/bound; owner FEAT-O not flagged, owner asked exactly {40,41}) + pre-existing 31 v/w controls green at base and final; x.5/x.6 keep owner FEAT-O Backlog finding (806, 823).
- SC-03: x.5 (792-807): GhError "Could not resolve to an Issue with the number of 17", exit 1, CANNOT VERIFY naming FEAT-B, FEAT-O still compared.
- SC-04: x.6 (809-826): FEAT-M/org/gone CANNOT VERIFY, owner asked only {40,41}, healthy FEAT-O compared.

## Coverage gaps / adequacy (minor, advisory)
- x.5 exercises only `factory_gh.GhError`; the `gh_board.BoardError` branch the plan names has no dedicated case (SC-03 text names only GhError). Form/proportionality, T-01.
- No unit-bucket test for INV-26 (see matrix note; DEC-217-consistent).
- Live Kaya smoke in the build note is the builder's claim; I did not rerun it (not assigned; fake gh covers routing).
- Guidance docs spec/decisions/architecture absent in product (as stated); no unresolved guidance question surfaced.

## Principles applied
Not citing craft leaves (none read this run).
