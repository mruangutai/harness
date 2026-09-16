# Code review — BUG-1699-lifecycle-cards — c0

**BLUF:** Stage 1 passes: the shipped scope satisfies the three BRIEF perspectives, SC-01–SC-16, and D-01–D-06 at `8ef4731e816f08dbc562206134c100b0c034a812..ed64ea9cc4ef92e3e54adfa0849a0147230b480b`. Stage 2 fails only the mandatory code-risk gate: two changed functions grade below their production/test bars. No lifecycle correctness defect survived review.

## Stage 1 — spec compliance: PASS

- **Operator perspective / SC-01–SC-03, SC-06–SC-09:** the shared active projection covers unique source, parent, and eligible task cards (`.claude/skills/harness/bin/gh_board.py:126-145`); signature opens before dynamic RESUME status (`.claude/commands/harness-plan.md:50-60`); reset/resume is atomic and classified from interrupted phase plus resulting tasks (`.claude/skills/harness/bin/plan-merge.py:798-916,2027-2039`); reconciliation compares and repairs each projected issue from one snapshot while retaining failed writes (`.claude/skills/harness/bin/board_lifecycle.py:488-526,1049-1094`). Ship semantics remain outside `cmd_status` and on the existing ship path.
- **Orchestrator perspective / SC-04, SC-05, SC-10:** Build, validation, and must-fix boundaries each have one ordered caller (`.claude/skills/harness/references/build-phase.md:13-18,35-38,50-66`); the fix reader DAG is unchanged; local station recording precedes remote writes and `_place` contains per-card `BoardError` (`.claude/skills/harness/bin/gh-sync.py:141-163,1491-1525`). Plan mutation itself remains network-free; only the receipt-gated PM caller projects Plan (`.claude/skills/harness-spec-driven/SKILL.md:133-137`).
- **Code-maintainer perspective / SC-11–SC-14:** `gh_board.project` is reused by status writes, INV-26, and reconciliation, excludes abandoned/terminal task cards, and does not close issues (`.claude/skills/harness/bin/gh_board.py:126-145,179-219`; `.claude/skills/harness/bin/check-state.py:2276-2338`; `.claude/skills/harness/bin/board_lifecycle.py:488-526`). Existing ship/open-child and abandonment paths were not replaced.
- **SC-15 inspection: PASS.** One projection policy is traced through all three consumers above. Reset/resume metadata is local to `plan.yaml`; signature removes it and emits RESUME. Exact caller anchors are signature (`harness-plan.md:50-57`), Plan reset (`harness-spec-driven/SKILL.md:133-137`), ordinary Build/Review and must-fix Building/next-boundary Review (`build-phase.md:13-18,35-38,50-66`).
- **SC-16 inspection: PASS.** Current truth is in DEC-138 (`DECISIONS.md:2956-2978`), DEC-203 (`:6170-6201`), DEC-220 (`:7098-7110`), DEC-224 (`:7247-7278`), and DEC-229 (`:7472-7495`); DEC-146's uncapped issue→projectItems lookup remains unchanged (`:3321-3333`). The generated summaries accurately state the lifecycle (`DECISIONS-INDEX.md:143,203,220,224,229`).
- **Decisions/tasks:** D-01–D-06 are implemented without mismatch; T-01–T-05 each discharge their traced criteria. The Main-authorized digest-contract edit is treated solely as process evidence, not lifecycle shipped behavior. No omission, mismatch, or scope leakage survives within the explicitly supplied shipped-path scope.

## Stage 2 — code quality: FAIL

Ranked findings:

1. **High · substance · T-01 · code-risk gate:** `.claude/skills/harness/bin/gh_board.py:126`, `project` grades 3 against production bar 4 (cyclomatic 9, cognitive 10, ABC 16.3; driver cyclomatic+cognitive). Concrete failure: any future lifecycle eligibility change must be made inside a function already beyond the reviewability bar, increasing the realistic risk that a new source/parent/task branch silently over-includes or omits a card. Required upgrade: refactor the projection into coherent helpers until grade 4+ while preserving its interface.
2. **High · substance · T-01 · code-risk gate:** `tests/integration/test-check-state-inv26.py:26`, `_inv26_fixture` grades 1 against test bar 3 (cyclomatic 14, cognitive 21, ABC 47.9; driver ABC). Concrete failure: when a new INV-26 miss case needs fixture setup, the high-branch shared builder makes it realistic to alter an unrelated fixture dimension and obtain a passing scenario that no longer isolates the intended eligibility/miss behavior. Required upgrade: split fixture construction by concern until grade 3+.
3. **Med · substance · T-03 · code-risk advisory:** `tests/integration/test-station-argument-spelling.py:288`, `case_lifecycle_checkpoint_order_and_negative_controls` grades 2 (cyclomatic 2, cognitive 1, ABC 39.4; driver ABC). Reason required: the function intentionally assembles one table of independent textual mutants against the same lifecycle interface, so the high assignment/call count is linear setup rather than control-flow complexity; retain as advisory, not a gate.

Assessed and dismissed:

- **Fail-open projection miss:** dismissed. Illegal station values raise; recorded task ids absent from the plan are intentionally outside projection, while mirrored-feature eligibility prevents INV-26 from fabricating placements.
- **Best-effort continuation:** dismissed. Status uses `_place` per card; reconciliation retains the failed finding and continues, then exits 1 while fixable residuals remain.
- **Reset/resume precedence:** dismissed. Review resumes only for an interrupted Review with every resulting task terminal; started work otherwise selects Building; repeated pending mutations recompute from retained resume context.
- **Caller ordering / reader serialization:** dismissed. The checkpoint-order guard includes discriminating negative controls, and no status call was added to `fix.yaml`.
- **Reconciliation snapshot/idempotency and foreign-repo leakage:** dismissed. Audit obtains one station snapshot, repairs finding issue numbers, and skips STATUS entirely when `--repo` is not the checkout's declared repository (`board_lifecycle.py:796-899`).
- **Stale authority / silent write failure:** dismissed for the cited anchors above; per-card failures are printed and do not suppress later writes.

No tests, builds, formatters, or linters were run, per dispatch. Mechanical grading was run against the immutable range and returned `code_grade: fail`.
