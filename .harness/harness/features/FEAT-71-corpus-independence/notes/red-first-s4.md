# Red-first receipt — slice S4 (probes, suite layout, skills, docs)

Baseline pin: `4a05030d` (origin/main). Baseline clone: `/private/tmp/feat71-base-s4` (the S4 test
files copied in, nothing else changed). Post-deletion simulation: `/private/tmp/feat71-post-s4`.
It is a clone at `84718357` with every S4 file and the main session's `.harness/harness.json`
overlaid, the two retired probes removed, and every non-survivor feature folder `git rm`'d and
committed there, leaving exactly the five survivors. Both clones were removed afterwards.
Every command ran with `CLAUDE_PROJECT_DIR` and `HARNESS_PROJECT_DIR` set to the root it ran in.

## Changed tests

### tests/integration/test-run-unit-tests-layout.py: FEAT-44 stand-in fixture removed

Command: `python3 tests/integration/test-run-unit-tests-layout.py`

- **Baseline: exit 1.** The baseline registry still names the dead FEAT-44 path, and the fixture
  no longer seeds it:
  ```
  FAIL git clean tree runs both sentinels MISCONFIGURED: documented exception is no longer tracked: .harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts
  FAIL git untracked rogue is not reported and both sentinels run MISCONFIGURED: documented exception is no longer tracked: .harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts
  ```
- **Worktree: exit 0**, 0 FAIL. **Post-deletion simulation: exit 0**, 16 PASS.

### tests/integration/test-run-unit-tests-shards.py: FEAT-44 stand-in fixture removed

Command: `python3 tests/integration/test-run-unit-tests-shards.py`

- **Baseline: exit 1.** Every git fixture is MISCONFIGURED for the same reason:
  ```
  FAIL empty shard succeeds without invoking the pool MISCONFIGURED: documented exception is no longer tracked: .harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts
  FAIL --kind accepted after --shard MISCONFIGURED: documented exception is no longer tracked: .harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts
  FAIL failing shard exits nonzero MISCONFIGURED: documented exception is no longer tracked: ...
  (plus 8 downstream shard/manifest FAILs that are empty because the runner refused)
  ```
- **Worktree: exit 0**, 0 FAIL. **Post-deletion simulation: exit 0**, 32 PASS.

### tests/integration/test-run-unit-tests-kinds.py: live-probe table is now the full locally_run set

`LIVE_KINDS` is now {handoff_comprehension, issue_types_live, omp_session_accessor}. A new
assertion requires that set to equal the `locally_run` kinds in `harness.json`. The matrix-claim
and dropped-kind loudness checks moved from the retired `inflight_claim_lifecycle_live` kind to
`issue_types_live`.

Command: `python3 tests/integration/test-run-unit-tests-kinds.py`

- **Baseline: exit 1.** The baseline config still registers the two retired probes:
  ```
  FAIL the locally_run kinds are exactly the declared live probes ['digest_object_contract_live', 'handoff_comprehension', 'inflight_claim_lifecycle_live', 'issue_types_live', 'omp_session_accessor']
  ```
- **Worktree: exit 0**, 0 FAIL. **Post-deletion simulation: exit 0**, 10 PASS.

### tests/unit/test-suite-layout.py: case 7 runs on a synthetic registry entry; live-entry path dropped

Case 7 now proves an entry is load-bearing with a synthetic `.harness/tools/probe-listed.ts` in a
git fixture: the layout is clean while the entry is listed, and the path is flagged once the entry
is cleared. Separate assertions require the live registry to be empty and the real layout to be
clean. The case-11 synthetic tracked list no longer includes `DOCUMENTED_EXCEPTIONS[0][0]`.

Command: `python3 tests/unit/test-suite-layout.py`

- **Baseline: exit 1.**
  ```
  FAIL case 7: live registry is empty (('.harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts', 'FEAT-44 evidence, ...'),)
  ```
- **Worktree: exit 1.** There are 2 FAILs, and both are the not-yet-deleted dead folder still
  tracked in the worktree index. The main session's folder deletion clears them:
  ```
  FAIL real layout is valid ['tracked test-shaped file outside tests/: .harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts']
  FAIL case 7: real layout is clean with the live registry [same]
  ```
- **Post-deletion simulation: exit 0**, 46 PASS, 0 FAIL.

### Unchanged tests run as gates

| Command | Worktree | Post-deletion simulation |
|---|---|---|
| `python3 tests/unit/test-check-skill-refs.py` | exit 0 | exit 0 |
| `python3 tests/integration/test-check-instruction-paths.py` | exit 0 | exit 0 |
| `check-skill-refs.py` | ok | ok |
| `check-instruction-paths.py` | 0 violations | 0 violations |
| `check-decision-anchors.py` | exit 0 (28 anchors) | exit 0 (28 anchors) |
| `gen-decisions-index.py --stdout \| diff - DECISIONS-INDEX.md` | empty | empty |
| `run-unit-tests.py --check-layout` | exit 2 | exit 0 |

The worktree `--check-layout` reports only the still-tracked dead FEAT-44 evidence file.

### Pure deletions (no red possible)

The two retired probes were deleted along with the FEAT-44 registry entry. Nothing executes a
deleted file, so no test can go red on its absence. Their consumers are covered above: the kinds
set, the layout fixtures, and suite-layout case 7.

## Byte identity

`git hash-object tests/manual/probe-session-accessors.ts` gives
`e8df5c44b0ef8e3172e5c3055d6b0b6a2b26291d`. This equals the blob of
`4a05030d:.harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts`.

## Files changed

- `tests/manual/probe-inflight-claim-lifecycle.py`: deleted (operator retired it).
- `tests/manual/probe-digest-object-contract.py`: deleted (operator retired it).
- `tests/manual/probe-session-accessors.ts`: new. Byte-identical move of the FEAT-44 evidence
  extension out of the corpus.
- `tests/manual/probe-omp-session-accessor.py`: `PROBE` now points at the moved extension. The
  evidence README's reproduction command and measured result are now in the docstring, and the
  docstring no longer points into the dead folder.
- `.claude/skills/harness/bin/suite_layout.py`: `DOCUMENTED_EXCEPTIONS = ()`. The FEAT-44 entry is
  gone and the generic registry mechanism stays. The moved `.ts` is under `tests/`, so an entry
  for it would itself be flagged "unnecessary".
- `tests/integration/test-run-unit-tests-layout.py`: dead FEAT-44 stand-in fixture removed.
- `tests/integration/test-run-unit-tests-shards.py`: dead FEAT-44 stand-in fixture removed.
- `tests/integration/test-run-unit-tests-kinds.py`: `LIVE_KINDS` is now the current locally_run
  set, with an exact-set assertion. Lifecycle-probe checks were retargeted to `issue_types_live`.
- `tests/unit/test-suite-layout.py`: case 7 uses a synthetic registry entry and asserts the live
  registry is empty. The live-entry path was dropped from case 11 (ownership granted by Main).
- `.claude/skills/harness/SKILL.md`, `.claude/skills/harness-verification-rules/SKILL.md`: the
  FEAT-23 example path became `.../features/FEAT-9-example/<file>`. This is a synthetic concrete id
  plus a placeholder, so it satisfies both check-instruction-paths (concrete ids take the
  control-plane root) and check-skill-refs (placeholder paths are not existence-checked).
- `.claude/skills/harness-simplify/SKILL.md`: the "Source prompts (eight, verbatim)" pointer to
  FEAT-23 is dropped.
- `.harness/harness/docs/DECISIONS.md`:
  - Paths and line anchors into dead folders are now prose that keeps the bare ids, with no change
    to what any decision decides. Affected locations: FEAT-03 `feature.yaml`/`STATE.md`, FEAT-02
    and FEAT-05 `STATE.md`, `FEAT-08/PLAN.md:306`, the FEAT-23 research notes, the FEAT-22
    simplify-pass note, the BUG-1016 receipts note, and the `feature.json:41` anchor. That anchor
    resolved only through survivor feature folders.
  - FEAT-44 evidence and probe paths now point at the moved `tests/manual` files.
  - Removed DEC-204's live lifecycle-probe merge-gate sentence.
  - DEC-213's "sole live entry" clause now says the registry is empty.
  - Current truth for removed mechanisms, per Main: DEC-159 and DEC-215 (no
    `handoff_done_when_baseline` exemption: every handoff note carries all five sections) and
    DEC-220 (no era exception set: every feature needs the build-entry receipt).
  - DEC-250 (Main follow-up): the retired `inflight_claim_lifecycle_live` kind is no longer cited
    as the live lineage evidence. The lineage was proven live once, at FEAT-495, and no standing
    live probe exists. What DEC-250 decides is unchanged.
- `.harness/harness/docs/DECISIONS-INDEX.md`: regenerated by `gen-decisions-index.py`.
- `.harness/harness/docs/SPEC.md`: `ls features/FEAT-01-sso/runs/` became `ls features/<FEAT>/runs/`.
