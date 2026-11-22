# Patch intake — BUG-2253

Pending BRIEF and one-task plan are ready for main-session signature. All three assigned planning gates exited 0; no implementation or regressions were executed. T-01 is main-session-direct under DEC-174. No panel, readers or goal-check were dispatched.

## Scope and guidance

Settled facts and exclusions are inherited without re-investigation from `/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-BUG-2253-hook-hang-budget-and-gate-fail-lines-2026-11-21.md`; durable acceptance is `runs/2026-11-21-01-patch-product/acceptance.md`. Heading chosen: `Failing or mutated files:`. No additional D-NN is warranted for this reversible wording choice. Lanes use BUG-2187's structure and resolve at `3dd8bb677bb2936361e3952030fc24f15bf9afc6`.

PRODUCT is `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2253-hook-hang-budget-and-gate-fail-lines`. Its CLAUDE.md imports AGENTS.md; both were consulted. PRODUCT `docs/spec.md`, `docs/decisions.md`, and `docs/architecture.md` are absent (docs contains PRINCIPLES.md and invalid-states-audit.html). Missing guidance is disclosed in BRIEF and actual task intent, not fabricated. Relevant control-plane decision entries DEC-174, DEC-182 and DEC-225 were consulted through the index. Integration is active and detects this test directory; unrelated null runners are not used as evidence.

## Every T-01 files entry

- `.claude/skills/harness/bin/validate-digest.py`: only the failed independent-run diagnostic branch changes.
- `tests/integration/test-validate-digest.py`: six shared-budget arguments, rationale and behavioral regressions; narrow test selector keeps task verify below 60 seconds without running the large full suite.
- `tests/integration/canonical-reader-classification.json`: explicitly owned contingency for maintenance of affected existing reader entries if the source edit requires it. Intake audit currently reports zero unresolved sites, so no manifest change is asserted necessary now. Do not rewrite unrelated classifications or invent readers; record whether maintenance was needed after implementation.

No new scripts, infrastructure, output formats or policy changes are authorized. In-file budget rationale is the bounded documentation update. T-01 machine fields occupy fewer than 50 lines (intent excluded); route validation accepted the task.

## Behavioral regression strategy

SC-01: existing RUN_UNIT_TESTS_BIN stub produces nonzero pooled-shaped output with multiple FAIL and MUTATED file lines on both streams, all above more than 20 passing lines in concatenated output. Assert every full matching line in order before the unchanged tail, heading once, and unchanged refusal status. Separate no-match output asserts tail-only fallback. Base-red is the buried-file case against the exact base gate, not the already-correct fallback assertion.

SC-02: execute all six real call expressions through their enclosing functions with minimal isolated setup collaborators, selecting each target independently. Observe default effective 30 and two temporary constant values (0.05/0.10) at every site; the base executes original calls and fails on observed 3, not a missing constant. Retain actual helper/subprocess timeout handling and replace only launched command with a ready-signalling child that blocks indefinitely. Each of six site-specific probes must raise TimeoutExpired within the selected budget plus 0.5 seconds tolerance. Independent 2-second process-group watchdog kills/reaps failures: removing timeouts must fail rather than hang or pass. Readiness establishes actual blockage. Restore all globals/collaborators and preserve existing FIFO/symlink/deep-JSON cases. No source wording/count assertions carry an SC.

Execution must capture identical new regressions against isolated exact base and fixed subjects, preserving bootstrap/imports: commit identities, commands, cases, exits and full stdout/stderr. Each SC needs authentic defect-exposing base-red/fix-green evidence; intake checks prove none of these outcomes. Existing safety cases may pass at base. No UAT criterion or user-run test is required.

## Exact planning receipts

All commands below ran from PRODUCT above, once after successful artifact creation:

1. `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2253-hook-hang-budget-and-gate-fail-lines/.harness/harness/features/BUG-2253-hook-hang-budget-and-gate-fail-lines/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2253-hook-hang-budget-and-gate-fail-lines` — exit 0; 1 task, 3 anchors resolved, 0 failures.
2. `python3 .claude/skills/harness/bin/check-plan-routes.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2253-hook-hang-budget-and-gate-fail-lines/.harness/harness/features/BUG-2253-hook-hang-budget-and-gate-fail-lines/plan.yaml` — exit 0; 0 violations across 1 plan. Expected TASK DEVIATION reports main-session-direct despite generic grants, consistent with DEC-174; manifest resolves to control plane.
3. `python3 .claude/skills/harness/bin/check-plan-routes.py --canonical-reader-audit` — exit 0; 0 unresolved reader sites across 100 Python files. This mode accepts no feature argument: its parser treats other arguments as plan paths. The ordinary route command above is explicitly feature-scoped.

Controlled plan bootstrap initially exited 5 on an indentation error before writing plan.yaml; corrected proposal applied successfully, exit 0. Apply's automatic check-state notes unsigned BRIEF and absent Build-entry receipt, expected at pending intake; these were not suppressed or signed away. No APPROVAL-RESET receipt occurred and no remote sync was invoked. No builds, tests, lint or formatters were run.

## Principles applied

- Experience First — retain every failing-file diagnosis and the familiar tail rather than replacing one useful operator view with another.

## Open questions

None. Main alone records the preapproved signature and 1 round / 45 min ruling. Implementation and authentic behavioral red/green evidence remain unperformed by design.
