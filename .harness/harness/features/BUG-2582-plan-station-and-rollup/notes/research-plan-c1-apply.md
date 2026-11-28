# BUG-2582 · plan c1 apply — evidence behind the applied findings

**Scope finding 1 holds only for a hand-written stub; the INV-34 remedy route already yields a startable record, so no dispatch-guard change is planned (D-04).** The other five findings are applied in the plan text (T-01, T-02, T-03) and two new tasks (T-04 witness, T-05 team file).

## Measured, not reasoned (worktree HEAD e69608659e31, HARNESS_AGENT_TYPE unset)

- `plan-merge.py apply` of the INV-34 stub (`schema`, `feature`, `status: plan`, `station_only: true`, `tasks: []`) onto an absent plan.yaml exits 0 and writes `approval: {status: pending}` plus a writer `drafted_at` — `plan_merge/union.py` `_seed_new_plan` seeds both on every creation, the stub included.
- Private-bin dispatch fixture (`tests/integration/test-lead-start-return.py` helpers, real `dispatch-guard.py`):
  - apply-created stub: harness-product-lead, harness-validator-lead and the scope reader all **start**;
  - hand-written stub with no `approval:`: all three **refused** before any claim (`records None`).
- So `_plan_preflight` → `_pending_plan_status_error` admits the prescribed stub today; the BUG-2565 run-01 lead did start, and was blocked only at `apply` (exit 5), consistent with this.
- Rejected routes: a guard allowance for a non-finished station-only record (widens an enforcement surface for a shape the remedy never produces); an explicit `approval:` in INV-34's stub text (`_seed_new_plan` refuses a creating proposal carrying approval, exit 8).
- Disclosure: the validator lead and scope reader also start on an apply-created stub — base behaviour, unchanged by this feature.

## Baselines at e69608659e31

- `tests/integration/test-lead-start-return.py`: 60 of 60 behaviour cases pass; with `--check-producers` 72 of 74, the two FAILs pre-existing: `producers/.claude/skills/harness/SKILL.md/lead header complies with the authority` (missing `mission named`) and `producers/.claude/skills/harness/references/plan-phase.md/plan and patch recipes carry their missions` (missing `reviewed field history`). T-05's verify asserts no FAIL beyond these two.
- `validate-digest.py` worst-member message spells `WORST member verdict`; tests match case-insensitively (scope finding 4).

## Finding → remedy

| Finding (panel-c1) | Remedy | Task |
|---|---|---|
| T-01 leaves plan start blocked | measured false for the prescribed stub; end-to-end start→convert witness; INV-34 sentence says the apply-written stub is startable | T-04, T-01 |
| T-02 keys relief by step | relief keyed by member index; duplicated reader step denies | T-02 |
| T-02 resolved-record identity | exactly one row per recomputed PF id, same reader string, exact `resolved`; historical rows exactly resolved; malformed panel denies | T-02 |
| red-first not discriminating | named reds carry code 5 + marker text, remedy-present-sentence-absent, worst-member text | T-01, T-02, T-04 |
| T-03 summary docs (form) | DEC-123 opening qualified; SPEC/harness-team carry mission, attribution, fail-closed | T-03 |
| should-not-exist: no trigger | apply step runs set-panel after record-panel; DEC-228 amended | T-05, T-03 |

## Open

- OQ-1 (non-blocking, signature): T-05 is planned in because Destination 2 requires it; strike T-05 (and DEC-228's amend row, SC-11) at signature to exclude it.
