# T-03 RED/GREEN: receipt grants, current decisions, operating guidance and cumulative grading

Builder: BuildT03Docs. This task was main-session-direct (DEC-174) in worktree W =
`.claude/worktrees/harness/FEAT-2337-omp-native-gate-runtime`. HEAD was e3e6fff8 at start and
197e080b at finish; main committed the fix-run ruling in between. These are candidate-source
results from W only. The installed control-plane hooks were neither exercised nor redeployed.
No git writes in W. One exception: a `git fetch origin main`, run to check that DEC-255 was
unused, updated the shared `origin/main` remote-tracking ref.

## Recorded deviations and rulings applied

- **Grading base `d04c765a`, not `dd04e52a`.** Source:
  `notes/answers-2026-11-22-grading-base.md`. `FEAT2337_BASE =
  d04c765aba6ba5044492a622625894085b99a2bc` in `tests/unit/test-code-grade.py`, with the reason
  in a comment beside it. The intents' other `dd04e52a` references are untouched.
- **DEC-255 was unused when written.** The check covered W, `origin/main` (fetched), every local
  and remote branch, and every `.claude/worktrees/*/*` checkout. The only branch carrying a
  `## DEC-255` heading is `feat/FEAT-46-decision-standard` (ba21f032, 2026-09-04). That branch is
  abandoned and uses an older numbering, in which DEC-250..254 also differ from main, so it is
  not a concurrent allocation.
- **Fix-run receipts.** Source: `notes/answers-2026-11-22-fix-run-receipts.md`.
  - A fix run's receipts are recorded at the fixed tip, in `runs/fix-c<N>-validator/qa/`.
  - The run counts as a fix run only when the registered run id and `harness_mission: fix`
    agree.
  - `tested_commit` must equal the trusted checkout's clean HEAD and descend from `review_sha`.
  - This rule is stated in DEC-255, `fix.yaml`, `harness-validator-lead.md`, `harness-qa.md`,
    verification-rules and SPEC §9.3.
  - The code itself belongs to the separate T-02 follow-up and was not touched here. DEC-255
    names the open `_head_is_pin_error` question as #2356.

## Files changed (13 owned paths + this note)

- `.harness/team-config.yaml`: harness-qa gains
  `.harness/*/features/*/runs/*/qa/manifest-*.json`, and nothing wider.
- `.claude/skills/harness/templates/team-config.yaml`: harness-qa gains
  `.harness/features/*/runs/*/qa/manifest-*.json`. This is the template's unsegmented layout,
  placed beside its `notes/qa-*.md` grant.
- `tests/integration/test-check-domain-grant.py`:
  - `run_feat2337_receipt_grant_cases`, a table-driven block with 21 rows, runs in the default
    suite (drive discovers it).
  - `main(argv)` adds `--only run_<block>`. Any other argument exits 2.
- `tests/unit/test-code-grade.py`:
  - `--feat2337` mode: `check_feat2337_grade_two_mutant` plus `check_feat2337_self_grading`.
  - `_load_test_kinds` is the one test_kinds load, now also used by `check_self_grading`.
  - Default `main()` is unchanged and does not run the fixed-base check.
- `.harness/harness/docs/DECISIONS.md`:
  - DEC-100's declared clause is rewritten in place. It now covers async policy,
    `POLICY_TIMEOUT_MS = 30_000` matching `HOOK_HANG_BUDGET_S`, a process-group kill, broad
    gates reporting unavailable, matching narrow commands refused while unrelated ones are
    allowed, helper conventions, and the five parallel Bash gates combined in declared order.
  - The new DEC-255 is the receipt decision.
- `.harness/harness/docs/DECISIONS-INDEX.md`: regenerated, with hand tails for DEC-100 (28
  words) and DEC-255 (29 words).
- `.omp/agents/harness-qa.md`: the Writable line, a new § "Runner receipts", and the
  `kinds: []` refusal.
- `.omp/agents/harness-validator-lead.md`: the validate receipt paragraph, plus the fix-run
  paragraph with #2356.
- `.claude/skills/harness-verification-rules/SKILL.md`: the receipt section, plus the
  candidate-versus-installed rule.
- `.claude/skills/harness/teams/validate.yaml`: the qa step comment and prompt.
- `.claude/skills/harness/teams/fix.yaml`: the fix-run qa comment and prompt.
- `.harness/harness/docs/SPEC.md`:
  - index row 9;
  - §4.2: the timeout row, plus an "Asynchronous, bounded, parallel" paragraph;
  - new §9.3: receipts, trust boundary, and candidate-versus-installed identity, including the
    host launcher path, version and hash and the source pin.
- `README.md` § Guardrails: a receipts bullet, a bounded parallel runtime paragraph, and a
  receipt trust-boundary paragraph pointing to DEC-100 and DEC-255.

The guidance surfaces point to DEC-255 for the production command. Only DEC-255 states it. The
T-02 refusal prints the executable repair command.

Both T-02 behaviour changes are documented on the guidance surfaces:
- `suite: pass` with `kinds: []` is refused.
- An unconditional PASS requires a live harness-validator-lead parent with exactly one open
  registered run, so QA runs under validate or fix.

Doc facts were checked against code, not copied from the plan:
- `harness-hooks.ts`: `POLICY_TIMEOUT_MS = 30_000`, `killGroup` SIGKILL of the process group,
  the `classifyPolicyRun` timeout branches, and `BASH_GATES` with `Promise.allSettled`.
- `validate-digest.py`: `_repair_command`, `_lineage`, `_receipt_context`.
- `run-unit-tests.py`: `_write_manifest`, and `_tested_commit` reading git HEAD of the runner's
  root.
- `.gitignore`: `runs/**` is ignored, so receipts must be force-added.

The sweep found no `#919` rerun contract, `RUN_UNIT_TESTS_BIN` or `_reverify` text on any changed
standing surface. No historical feature record was edited.

## RED (tests written first; no config or doc edit yet)

`python3 tests/integration/test-check-domain-grant.py --only run_feat2337_receipt_grant_cases`
exited 1 with **14/21** passing. Failing rows:

- `[authored] QA writes its own unit receipt`: exit 2, "harness-qa may not write …/qa/manifest-unit.json".
- `[authored] QA writes its own integration receipt`: exit 2.
- `[template] QA writes its own receipt (template layout)`: exit 2.
- `[authored] the resolver routes a receipt to harness-qa`: `--resolve` returned `['harness-orchestrator', 'harness-validator-lead']`.
- `[authored] a claimed QA writes the receipt in its own feature worktree`: exit 2, domain refusal.
- `[authored] a claimed QA may not write another feature's receipt in that feature's worktree`:
  exit 2, but for the domain reason and not the claim rule. The row asserts "holds worktree
  claim", so it is red.
- `[authored] a claimed QA may not write its feature's receipt in the main checkout`: exit 2,
  domain reason rather than "belongs in worktree".

The refusal rows (state.yaml, digest.md, log, sibling run, outside or nested `qa/`, reviewer, dev)
pass at RED by design. They pin the grant's narrowness, which must survive GREEN.

`python3 tests/unit/test-code-grade.py --feat2337` against the committed tip, which did not yet
contain T-03, exited 1 with 3 failures:

    FAIL the committed tip grades tests/unit/test-code-grade.py:check_feat2337_self_grading
    FAIL the committed tip grades tests/unit/test-code-grade.py:check_feat2337_grade_two_mutant
    FAIL the committed tip grades tests/integration/test-check-domain-grant.py:run_feat2337_receipt_grant_cases

The same run graded 121 changed T-01/T-02 test functions, all >= 3. The mutant control printed
`ok … the new grade-2 test function check_mutant is rejected`.

**Red-first proof that a grade-2 mutant is rejected by the real `--feat2337` mode.** In a
throwaway clone (`git clone` of W into /tmp, never W), I committed the T-03 tree and then a second
commit appending a 12-branch `check_feat2337_mutant_probe` to `tests/unit/test-code-grade.py`.
`python3 tests/unit/test-code-grade.py --feat2337` exited 1:

    FAIL  feat2337: tests/unit/test-code-grade.py:check_feat2337_mutant_probe grade 2 (bar 3)
    1 failures

## GREEN

- After the two grant lines: `--only run_feat2337_receipt_grant_cases` exits 0, 21/21, 1.7 s.
- **Literal verify in W (uncommitted):** exits 1. Only the 3 "committed tip grades …" rows fail,
  because the T-03 tests are not committed yet. This is expected and is why the intent says to
  run it after the task commits.
- **Literal verify at a simulated committed tip** (throwaway clone: W's working tree committed
  over 197e080b): exits 0 in 3.5 s total. Results:
  - `PASS test-code-grade --feat2337`, with 144 changed Python test functions graded from
    d04c765a.
  - 21/21 receipt-grant cases.
  - Empty index diff.

  The clone also carried the fix-run builder's uncommitted `validate-digest.py` and
  `test-validate-digest.py` edits at that moment. At main's real T-03 commit, rerun the literal
  verify. It must exit 0.
- `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md` in W: empty.

Grades of every new or changed T-03 function (`code_grade`, as graded at the simulated tip):

| File | Function | Grade |
|---|---|---|
| test-code-grade.py | `_load_test_kinds` | 5 |
| test-code-grade.py | `check_self_grading` (refactored) | 4 |
| test-code-grade.py | `_base_bodies` | 4 |
| test-code-grade.py | `_is_changed` | 5 |
| test-code-grade.py | `_changed_test_records` | 4 |
| test-code-grade.py | `_print_graded` | 5 |
| test-code-grade.py | `check_feat2337_self_grading` | 4 |
| test-code-grade.py | `_grade_two_source` | 5 |
| test-code-grade.py | `_mutant_repository` | 4 |
| test-code-grade.py | `check_feat2337_grade_two_mutant` | 4 |
| test-code-grade.py | `feat2337_main` | 5 |
| test-code-grade.py | `_cli` | 5 |
| test-check-domain-grant.py | `_feat2337_root` | 5 |
| test-check-domain-grant.py | `_feat2337_detail` | 5 |
| test-check-domain-grant.py | `_feat2337_grant_results` | 4 |
| test-check-domain-grant.py | `_feat2337_resolve_results` | 4 |
| test-check-domain-grant.py | `_feat2337_claim_results` | 4 |
| test-check-domain-grant.py | `run_feat2337_receipt_grant_cases` | 4 |
| test-check-domain-grant.py | `main` | 4 |

There are no allowlist entries, and the cumulative check uses no allowlist. TypeScript
(`tests/unit/omp-hooks.test.ts`) is not Python-graded: it runs under Bun through
`tests/unit/test-omp-hooks.py`, and the `--feat2337` output says so.

## Default suites

- `python3 tests/integration/test-check-domain-grant.py`: exit 0, 0 FAIL lines, 14 s.
- `python3 tests/integration/test-gen-decisions-index.py`: exit 0, 0 FAIL lines.
- `python3 tests/unit/test-code-grade.py`: exit 1 with one failure,
  `FAIL validate-digest.py:check_qa_matrix_claim grade >= 4`. This is **expected-pending, not a
  T-03 defect.** It is legacy CR-01 self-grading of T-02's production function, which grades 3.
  - In a clean clone, that function is red at committed HEAD 197e080b and green at T-01 0419b533.
  - Routed by Main to BuildFixRunReceipt, which will split the function in `validate-digest.py`.

**Neighbour suites.** I ran 71 test files that read the changed surfaces (team-config, templates,
agents, skills, teams, SPEC, README, DECISIONS), excluding the validate-digest files the fix-run
builder is editing, with `run_pool.py -- <files>` in W: 70 exit 0, 1 exits 1.

- The red file is `test-check-plan-routes.py`: cases 04, 05, 15, 17, 19d and 19d2 fail with
  `DEVIATION <W>/.harness/team-config.yaml differs from <control plane>/.harness/team-config.yaml`.
- `check-plan-routes.py` resolves routes against the OWNER (control-plane) manifest and counts a
  parsed route difference as a violation. Inside a linked worktree, any branch that adds a grant
  therefore trips it until the grant is merged into the owner.
- The same file, with the T-03 grant, exits 0 (0 FAIL) in a standalone clone, which is what CI
  runs.
- Environment-only. No test was weakened, and it clears once main carries the grant. The
  standing Plan-route gate run inside W reports the same DEVIATION until merge.

## Observations for Main (outside T-03's files)

- **merge-gate.py timeout outcome.** A `merge-gate.py` process killed at the budget takes the
  helper path in `classifyPolicyRun`: not blocked, with a reason. Its own caught failures still
  exit 2. DEC-100 now states exactly this ("refuses its own failures at exit 2"; past the budget,
  the non-blocking reason). Before T-01 a hang froze the session; now a hung merge-gate lets
  the call proceed. The plan's classification list did not name merge-gate.
- **A claimed QA writing another feature's artifact inside its own worktree** is allowed: the
  feature-artifact rule keys on a root-relative path. This is pre-existing behaviour, identical
  for the existing `notes/qa-*.md` grant. The new grant neither widens nor tests it.
