# T-04 receipt — harness-dev-ops

**Verdict: BLOCKED.** Phase 1 (`.harness/harness.json`) landed clean. Phase 2
(`.claude/skills/harness/templates/harness.json`) is blocked by `check-domain.sh` — the path is
not in this agent's domain and not in `shared:`. No workaround was attempted (Bash rewrite would
be guardrail evasion per the dispatch and `check-domain.sh:246-247`).

## Blocking hook stderr (verbatim)

```
PreToolUse:Edit hook error: [${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/check-domain.sh]: check-domain: BLOCKED — harness-dev-ops may not write .claude/skills/harness/templates/harness.json
  Permitted for you: .github/**, Dockerfile, .harness/harness.json, .claude/skills/harness/bin/**, .harness/codebase/stack.md, .harness/features/*/notes/receipt-harness-dev-ops-*.md, .harness/expertise/harness-dev-ops.md, .harness/features/*/observations/harness-dev-ops.md
  Shared (allowed, serialized): package.json, package-lock.json, pnpm-lock.yaml, yarn.lock, pyproject.toml, uv.lock, requirements.txt, tsconfig.json
  If this path should be yours, it belongs in .harness/team-config.yaml — do not work around this hook.
```

## Verify clauses run (against the partial state: Phase 1 done, Phase 2 blocked)

**1. `python3 -c "import json,sys; [json.load(open(p)) for p in ['.harness/harness.json', '.claude/skills/harness/templates/harness.json']]"`**
Output: (none). Exit: 0. Both files still parse as valid JSON.

**2. `grep -c -e cost_model -e per_feature_usd -e per_run_usd -e warn_at_fraction -e _budgets_note .harness/harness.json .claude/skills/harness/templates/harness.json`**
```
.harness/harness.json:0
.claude/skills/harness/templates/harness.json:6
```
Exit: 0. Only `.harness/harness.json` is `:0` — the template is untouched (`:6`), as expected
given the block. This clause does NOT pass overall (SC-07 unmet for the template), consistent with
Phase 2 not landing.

**3. `grep -c max_total_cycles .harness/harness.json .claude/skills/harness/templates/harness.json`**
```
.claude/skills/harness/templates/harness.json:2
.harness/harness.json:2
```
Exit: 0. Both `:2` — the surviving key held byte-identical in both files (template was never
touched, so trivially still `:2`; `.harness/harness.json` confirmed post-edit).

**4. `.claude/skills/harness/bin/check-state.sh`**
Exit: 0. Only pre-existing orphaned-run `note`-level lines (unrelated FEAT-05/06/08 run-dir
housekeeping), no `bad`/violation output. Confirms T-02's removal of the `cost_model.rates` hard
check landed before this edit (D-02) — the repo does not fail check-state after stripping
`cost_model` from `.harness/harness.json`.

**5. `.claude/skills/harness/bin/run-unit-tests.sh`**
Exit: 0. `test-upgrade-config.py` and `test-team-catalog.py` (named in the dispatch as readers of
these config shapes) both report `PASS` within the full run. Full suite: `ALL PASSED` / all listed
scripts `PASS`.

## Files touched

- `.harness/harness.json` — removed `_cost_model_note`, the `cost_model` object, `_budgets_note`,
  and `per_feature_usd`/`per_run_usd`/`warn_at_fraction`/`_per_feature_rationale` from `budgets`.
  `budgets` now holds exactly `max_total_cycles` and `_max_total_cycles_rationale`, byte-identical
  to before the edit.
- `.claude/skills/harness/templates/harness.json` — NOT touched (blocked, see above).

## Open questions for the main session

- Q1: Phase 2 needs either (a) a `team-config.yaml` grant adding
  `.claude/skills/harness/templates/harness.json` (or a broader `templates/**`) to
  `harness-dev-ops`'s domain, or (b) a main-session-direct edit of the template file. Both are the
  main session's call. blocking: true.
