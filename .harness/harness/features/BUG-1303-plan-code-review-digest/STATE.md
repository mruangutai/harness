# STATE

## Current

- feature: BUG-1303-plan-code-review-digest
- run: .harness/harness/features/BUG-1303-plan-code-review-digest/runs/2026-09-05-14-validator/digest.md
- squad: validator
- status: validate-complete, ship-ready pending the operator's briefing decision

Validate phase closed. `review_sha` is pinned at `e2c800f1`, HEAD, tree clean. The c4 reviewer panel
returned FAIL with two `must_fix`; both were fixed in one cycle and independently confirmed resolved
at c5 (`notes/review-harness-code-reviewer-c5.md`, `notes/review-harness-qa-c5.md`). MF-1: the DEC-217
`DECISIONS-INDEX.md` row carried hand-written tags no regeneration reproduces, which reddened
`run-unit-tests.sh --kind integration` and falsified SC-06's byte-identity clause — regenerated, one
row moved, ruling text unchanged. MF-2: the plan-mode `code_grade` assertion retyped `n_a` instead of
deriving it, against SC-03's own words — it now probes `_pending_plan_review_error` across
`CODE_GRADE_VALUES` and keeps the single member that rule accepts, and reds loudly when zero or many
qualify. pm's goal-check grades **8 of 8 criteria met** at the new pin
(`notes/research-BUG-1303-goalcheck-validate-c5.md`). Gates at `e2c800f1`, all orchestrator-run:
digest-validator suite exit 0 / zero `^FAIL ` / `ALL PASSED`; `test-config-shape-matrix.py` 19/19;
`--kind integration` exit 0 over 46 files; index regeneration byte-identical; `check-state.sh` exit 0.
Panel `severity_max` is `med` with `must_fix: []` — under `gates.review: advisory_unless_high` nothing
gates. F-01, the build phase's blocking matrix-floor question, is **RESOLVED** by DEC-217, the
delegated-Advisor ruling the main session implemented at `e014ede3`. cycles_used 5 of 8; 17 runs of a
budget of 20 — informational, and each run of this phase resolved a named finding.
Briefing: `notes/ship-review-2026-09-05-validate.md`. Handoff: `notes/handoff-validate.md`.

## Open Questions

- F-02 — operator decision, non-blocking, the one live item the ship decision carries: DEC-217's two
  predicates `touches_runtime_code` and `fix_confined_to_tests_and_contract_docs` are documented in
  neither `.claude/skills/harness-qa-gate/SKILL.md` nor `.claude/skills/harness-verification-rules/SKILL.md`,
  where DEC-212's `touches_config_shape` is documented in both AND asserted by
  `tests/unit/test-config-shape-matrix.py`. qa evaluates these predicate names against a diff at gate
  time from its preloaded skills; their definitions exist only in `DECISIONS.md`. Raised `high` by the
  code reviewer, reconciled to `med` by the validator lead because the two predicates are exact
  complements so no diff can require zero kinds. Both remedy files resolve to `NOBODY` under
  `check-domain.sh` — main-session-only, unroutable to any squad. Evidence:
  `notes/review-harness-code-reviewer-c4.md`, restated at c5.
- Non-blocking, operator's to reconcile: applied literally to this feature's own diff,
  `touches_runtime_code` is TRUE — solely via `.claude/skills/harness/templates/harness.json`, which is
  not under `tests/**`, not `*.md` and not under `.harness/` — and
  `fix_confined_to_tests_and_contract_docs` is FALSE for that same file. So the matrix requires `unit`,
  where DEC-217's own worked example says BUG-1303 changes no runtime code and integration is its
  kind. The gate passes either way (both kinds are present and green), so this is a wording
  reconciliation, not a defect. Amending a signed Advisor ruling is not a squad's.
- Backlog, low: `.harness/harness.json:214-217` keeps the `__bug_class__` / `match_bug_class` leg while
  `test_kinds` defines no `__bug_class__` — a predicate placeholder that can never resolve, which
  `DECISIONS.md:5074` calls broken in another project's config. Not gating; DEC-217's retention of the
  leg is binding. Raised by the validator lead (VL-1).
- Harness defect, observed twice this run: a member's job returns `failed (exit 1)` with
  "Subagent called yield with null data" while its final message carries a complete, well-formed
  return, and the job preview can surface a SUPERSEDED draft whose verdict is the opposite of the
  agent's own artifact. Both harness-qa (c4) and harness-backend-dev (MF-2) hit it. A lead routing on
  tool status or on the preview would have discarded correct work or shipped a red gate.
- Harness defect, RECURRENCE, two independent leads this run: `check-domain.sh` guards
  `<run_dir>/digest.md` against replacement but applies no guard to `<run_dir>/state.yaml`, and
  `runs/` is gitignored so a Glob of it returns nothing. Each lead opened an existing run dir and
  silently replaced an earlier run's checkpoint before the digest write refused. Extend the guard to
  `state.yaml`. A stray `runs/2026-09-05-01-product/send-back-criteria.md` also remains — the
  orchestrator's `rm` of it was correctly refused as out-of-domain, so no tier holding a shell can
  remove it.
- Harness defect: the code reviewer reports its own injected persona text was byte-identical to the
  STALE main-checkout copy of `.omp/agents/harness-code-reviewer.md`, not the worktree's fixed copy —
  the reviewer of a fix to the reviewer's own contract was loaded with the pre-fix contract. Same root
  as the standing worktree-resolution defect below.
- Harness defect, carried from build and re-measured: inside a worktree, `handoff_done_when` authority
  pointers resolve against the MAIN checkout, so `brief-sc:` and `plan-task:` are UNUSABLE from here;
  only `finding:` and `approval:` can be spelled through `.claude/worktrees/`. Also carried:
  `bash-write-guard.sh` parses the whole command line textually, refusing `plan-merge.py apply
  --proposal -` when the proposal body contains an angle bracket.
- Documentation defect, cost one send-back this run: dispatch text templated
  `gen-decisions-index.py --apply`. That flag does not exist — the tool exits 2 and the BARE
  invocation is the in-place write.
