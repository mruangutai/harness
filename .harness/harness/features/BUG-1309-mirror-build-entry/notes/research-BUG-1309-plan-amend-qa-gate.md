# Plan amend for the qa matrix gate — BUG-1309

**Two new tasks and two new decisions give all three gate failures an owner. `check-plan-routes.py`
exits 0. `panel` is byte-identical. `approval.status` still reads `approved` — `apply` did NOT reset
it, and the main session must re-sign.** T-01..T-09 are untouched: no field of any existing task or
decision was amended, because neither remedy's file is in any of their `files:` lists and both
remedies are new work rather than an unfinished part of a `done` task.

## Which task owns which gate failure

| gate failure | owner | lane | files |
|---|---|---|---|
| §1 red SC-14 fixture | **T-10** | `main-session-direct` (D-11) | `tests/integration/test-hooks-install.py` |
| §2 `feature` unit floor, T-03 | **T-11** (BE-25..BE-30) | `team` / harness-backend-dev | `tests/unit/test-gh-sync-build-entry.py` |
| §3 `bugfix` unit floor, T-02/T-04/T-06/T-07 | **T-11** (BE-01..BE-24) | `team` / harness-backend-dev | both new `tests/unit/` files |

What each `verify:` actually proves:

- **T-10** — runs the whole file (4.6 s measured), fails on any `^FAIL:` line, and requires three
  named PASS labels including a NEW one, `the sweep removed the worktree by the normal path, never
  the build-entry retention branch`. That label cannot green while the retention branch fires, so
  the case can never be "fixed" by weakening it back to a bare `isdir` check.
- **T-11** — asserts one `PASS BE-NN ` line per id for all 30 ids via `seq -w 1 30`, so the block
  cannot pass while any case is absent or renumbered, and fails on any `^FAIL ` line.

## Lanes, measured with `check-domain.sh --resolve` (exit 0 each)

- `tests/integration/test-hooks-install.py` → harness-backend-dev, harness-dev-ops, harness-qa
- `tests/unit/test-feature-schema-build-entry.py` → harness-backend-dev, harness-dev-ops, harness-qa
- `tests/unit/test-gh-sync-build-entry.py` → harness-backend-dev, harness-dev-ops, harness-qa
- control: `post-merge-sweep.sh`, `check-state.sh` → harness-backend-dev, harness-dev-ops

## Overturned premise: the fixture repair is main-session-direct, not team (D-11)

The dispatch pinned T-10 to `team` on the `--resolve` grant. **A team grant cannot settle carve-out
membership**: the same resolver grants team on `post-merge-sweep.sh` and `check-state.sh` themselves
(control row above), which is exactly why this plan's signed `lanes` rows override it on T-04/T-06/T-07.
`DECISIONS.md:4360-4363` puts "**the test file of each**" gate inside the carve-out and states the
category governs, not the enumeration; case (e) of that file runs a real `git merge` through the
tracked `core.hooksPath` shim and executes `post-merge-sweep.sh` end to end (`test-hooks-install.py:388-432`).
The line drawn in D-11 is **exercises a gate**, never **imports a module a gate uses** — the wider
reading would drag `tests/integration/test-gh-sync.py` and `test-validate-feature-json.py` into the
carve-out, and this plan's own lanes rows place both in team. `lanes` itself was left untouched: a
new row would need `resolved_at` re-pinned, and `apply` refuses a differing top-level key (exit 7).

## T-07 has no unit-reachable seam, and D-10 says so instead of inventing one

`post-merge-sweep.sh:29-43` runs its whole body — including the retention branch at `:221-233` — inside
a `python3 -I -` heredoc fed on **stdin**. Nothing can import it. Its only unit-reachable input is
`feature_schema.BUILD_ENTRY_ERA_EXEMPT`, covered by BE-10, which is the exact property `:223` branches on
and the one the stale fixture turned on. Extracting that decision into a module purely to host a test
would be a runtime change made to satisfy a directory label — what DEC-217's Over clause forbids, one
level up — and enforcement-layer work besides. **T-07's retention cell stays discharged by
`tests/integration/test-post-merge-sweep.py` plus T-10's end-to-end case; the gap is recorded, not papered over.**

Every BE case was executed against live code at plan time (two throwaway probes): `recovery_command_for`'s
seven-row table incl. trailing slash, `record_build_entry`'s upgrade/never-downgrade pair,
`load_recorded`'s out-of-enum normalization and `save_recorded`'s drop, all five `skip` guard branches
(`gh-sync.py:187-190`, incl. the absent-`feature.json` branch no integration case reaches), the four
`_build_entry_preflight` outcomes, and the `_recover_terminal_conflict`/`_recover_terminal_report` tables
(the `int()` coercion at `:1234` is load-bearing — `main()` passes `--parent` through as a **string**,
`gh-sync.py:2208`). No REQ was added: every case traces to REQ-02/03/04/06/08/09/10 already in BRIEF.md.

`change_type: scaffolding` on T-11 is deliberate and precedented (BUG-1308 T-02): `bugfix` would fire
`fix_confined_to_tests_and_contract_docs`, demand an *integration* test of a unit-test task, and turn
the remedy into a fresh matrix failure.

## `check-plan-routes.py` — verbatim, exit 0

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
DEVIATION T-10 tests/integration/test-hooks-install.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-11 granted to harness-backend-dev, harness-dev-ops, harness-qa
0 violation(s) across 1 plan(s)
```

Exit status **0**. T-10's `DEVIATION` is the expected shape for a granted `main-session-direct` path —
identical to T-04/T-06/T-07's, and only `VIOLATION` lines gate.

## Integrity read-back

- `yaml.safe_load` loads the file; tasks T-01..T-11, decisions D-01..D-11.
- `panel`: sha256 `2a87bec4cff5e0b018343b5fb8c710a47f4c1ef81c5c834a6dfd67abf2d38ea5`, 3487 bytes,
  **identical before and after the amend**; seven findings, ids and dispositions unchanged
  (3 `resolved`, 4 `open`); `approval.rulings` still four.
- `approval.status` read back from the file: **`approved`**, dated 2026-09-04.

## Open question

**Q1 (blocking).** Adding T-10 and T-11 did **not** reset the approval. `plan-merge.py apply` seeds
`pending` only on a brand-new plan and otherwise carries the approval bytes forward verbatim; only
`sign-approval` writes that mapping, and pm is refused there. So the 2026-09-04 signature now covers a
task set the operator never saw, and no tool available to me can mark it pending. The main session must
re-sign (or record the amendment against the existing signature) before T-10/T-11 are dispatched. The
doctrine "re-planning resets approval" is unmechanized — worth a harness ticket in its own right.
