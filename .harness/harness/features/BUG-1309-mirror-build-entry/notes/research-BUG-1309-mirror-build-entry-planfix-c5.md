# Plan fix c5 — era fixture literals, BUG-* symmetry, SC-06 corpus — BUG-1309

**All three residual defects c4 reported are now closed. Six `plan-merge.py amend` compare-and-swap
writes (T-04 `verify` + `intent`, T-05 `intent` twice, T-06 `intent`, T-07 `intent`) and one BRIEF
edit to SC-06's wording. `check-plan-routes.py` exits 0, `approval.status` is still `pending`, and
tasks 9 / decisions 9 / REQ 10 / SC 10 are unchanged. No task's implementation instructions moved.**

## D-e — era fixtures are named literals; no seam anywhere

The route: an era fixture is staged under a directory name the frozen `BUILD_ENTRY_ERA_EXEMPT`
snapshot **already contains**; a non-era fixture under a **synthetic id the snapshot cannot
contain**. No test extends the set, and no override hook is specified. Each of T-04/T-05/T-06/T-07
now opens its case list with a FIXTURE DIRECTORY NAMES block stating the frozen-literal fact and
naming that task's literals; each case then names its own fixture directory.

The only "have the test extend the set" clause was the one c4 flagged (T-04's `era-exempt continues`);
the sweep found no second one — `grep -n -i "add one such\|the test controls\|extend .*ERA_EXEMPT\|
monkeypatch\|override hook\|seam\|test-controlled" plan.yaml` returns one hit, T-08's unrelated
pre-existing "step 4's validate seam". Membership re-derived in the worktree with the T-06 generator
command: 75 names; `BUG-1030-stale-anchor-write-hazard`, `BUG-1071-inv32-era-guard`,
`FEAT-55-issue-types-created-work` are members, `FEAT-9001-fixture-non-era` and
`BUG-9001-fixture-non-era` are not.

| Task | era literal(s) | non-era literal(s) |
|---|---|---|
| T-04 | `BUG-1030-stale-anchor-write-hazard` (absent key), `BUG-1071-inv32-era-guard` (recovery-required) | `FEAT-9001-fixture-non-era`, `BUG-9001-fixture-non-era` |
| T-05 | `BUG-1030-stale-anchor-write-hazard` | `FEAT-9001-fixture-non-era` (named for every deny case) |
| T-06 | `FEAT-55-issue-types-created-work` (the shape INV-37 exists to catch) | `FEAT-9001-fixture-non-era` |
| T-07 | `BUG-1030-stale-anchor-write-hazard`, **shared by both era cases** — they differ in the RECORDED VALUE, which is what retention keys on | `FEAT-9001-fixture-non-era` |

Every era case stays paired with a non-era case differing ONLY in the directory name, the existing
"one without the other is a REJECTED return" language kept on each pair; T-06 gained that pair
language, which it lacked. T-06 also gained the ONE-DEFINITION clause, so all four tasks carry it in
consistent wording.

## D-f — the BUG-* half of REQ-01 is now asserted

New T-04 case **`T-04 BUG-named non-era absent refuses`** (plan.yaml:509) — the
`FEAT-9001-fixture-non-era` refusal fixture duplicated under `BUG-9001-fixture-non-era`, same
assertion (exit 2, `gh-sync: REFUSED`, `gh-sync.py open`). Its intent declares the pair to be the
only thing asserting REQ-01's FEAT-*/BUG-* symmetry clause and a one-sided change a REJECTED return.
Added verbatim to **T-04's `verify:` loop** (plan.yaml:399), second position. No case count is stated
in T-04's prose, and T-06 gained no case, so no count needed updating.

**c5b addendum (lead follow-up):** T-04's `traces:` is now `[REQ-06, REQ-01]` (plan.yaml:385-387,
one `plan-merge.py amend --field traces --yaml-value` compare-and-swap). Without REQ-01 the case
that asserts the FEAT-*/BUG-* symmetry was invisible to any REQ-coverage read — the exact failure
D-f exists to close. Nothing else changed; `check-plan-routes.py` still `0 violation(s) across 1
plan(s)`, EXIT=0, and tasks 9 / decisions 9 / REQ 10 / SC 10 / `approval.status: pending` hold.

## D-g — SC-06 names its corpus

`BRIEF.md:118-127`, wording only: retention keys on the RECORDED value and never on era membership —
a feature RECORDING `recovery-required` (the state a GitHub-unavailable recovery leaves) keeps its
worktree **even when it is era-exempt**, while an era-exempt feature with the key **ABSENT** is swept
normally, announcing that it predates the receipt; both halves graded by T-07's
`…recovery-required keeps the worktree` and `…absent build_entry is swept`. `verify: automated
evidence: integration` unchanged. This is the post-c4 R8/R10 reading, not the pre-c4 one.

## Measured after the edits

`yaml.safe_load` OK · tasks **9** · decisions **9** · REQ **10** · SC **10** ·
`approval.status: pending` · BRIEF `## Approval` `status: pending` · `status: plan` ·
every case name in each amended `verify:` appears verbatim in that task's `intent:` (machine-checked,
0 mismatches).

```
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-01 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-02 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-03 granted to harness-backend-dev, harness-dev-ops, harness-qa
DEVIATION T-04 .claude/skills/harness/bin/gh-sync.py, tests/integration/test-gh-sync.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-05: declared main-session-direct (.claude/settings.json, .claude/skills/harness/templates/settings.snippet.json, .omp/extensions/harness-hooks.ts ungranted)
DEVIATION T-06 .claude/skills/harness/bin/check-state.sh, .claude/skills/harness/bin/feature_schema.py, tests/integration/test-check-state.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
DEVIATION T-07 .claude/skills/harness/bin/post-merge-sweep.sh, tests/integration/test-post-merge-sweep.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-08: declared main-session-direct (.claude/skills/harness/references/github-mirror.md, .claude/skills/harness/SKILL.md ungranted)
OK T-09 granted to harness-documentor
0 violation(s) across 1 plan(s)
EXIT=0
```

## Reported, not changed

- D-08's `choice:` still describes era membership abstractly ("a feature whose directory basename is
  in that set"). That is the POLICY statement, not a fixture instruction, so no literal belongs there.
- T-05's allow-only cases (`opened`, `not-applicable`, `recovered-terminal`, `sync false`,
  `branch matching no feature`, `non-merge command`) are not era-sensitive; the fixture-name rule
  block covers them by stating every deny case must use `FEAT-9001-fixture-non-era`.
- Nothing outstanding. No open question.
