# QA gate — review-c4 — BUG-1309-mirror-build-entry @ af132780

## Verdict: PASS — matrix_ok: true, suite: pass, failures: 0

The cycle-4 fix (`feature_for` skips non-dict JSON records before branch matching; the
denial message now interpolates `feat`, defaulting to the literal `"this feature"` until a
document actually matches) is adequately covered, and all three postures the fix must hold
simultaneously are each bound by a named case. No FAIL, no BLOCKED kind.

## Change type and required kinds

Diff (`af132780`, tip == pin, empty delta between them):
`.claude/skills/harness/bin/merge-gate.py` (+5/-1 lines of production code) and
`tests/integration/test-merge-gate.py` (test revision, 18 cases retained).

This is `change_type: bugfix` against `test_matrix.bugfix` in `.harness/harness.json:203-219`:
`always: []`; `when: unit if touches_runtime_code` fires (merge-gate.py is production code) →
**unit required**. `when: integration if fix_confined_to_tests_and_contract_docs` does NOT fire
(production file changed, not test-only) — the matrix does not obligate integration by that leg.
`__bug_class__`/`match_bug_class` is the known-placeholder clause (repo Expertise G-08) — no
taxonomy entry fires, contributes nothing.

**qa addition above the floor:** `integration` is required in practice because the fix's own
regression evidence lives entirely in `tests/integration/test-merge-gate.py` — the file the diff
itself changed. Required kinds this cycle: **unit, integration**.

## Per-kind results

| kind | command | exit | discovered |
|---|---|---|---|
| integration (targeted) | `python3 tests/integration/test-merge-gate.py` | 0 | 18 cases, all `ok`, `ALL PASSED` |
| integration (targeted) | `python3 tests/integration/test-gh-sync.py` | 0 | 28 cases, all `ok`, `ALL PASSED` |
| unit (targeted, T-05-adjacent) | `python3 tests/unit/test-omp-hooks.py` | 0 | `bun test`: 56 pass / 0 fail / 100 expect() calls |
| unit (full bucket) | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | 33 files, pool-run, all PASS |
| integration (full bucket) | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | 50 files, pool-run (75.7s wall), includes `test-merge-gate.py` and `test-gh-sync.py`, all PASS |

`env -u HARNESS_AGENT_TYPE` used throughout per repo-tier G-07 (its presence spuriously fails
`test-plan-merge.py`, unrelated to this diff).

Exit codes are corroborated by named-case counts (18/28/56/33-files/50-files), not bare codes
alone — none of these ran over an empty discovered set.

## Adequacy of the revised 18th case

The prior "T-05 non-object feature record fails closed" case (asserted `deny` +
`"could not evaluate"` when the *matched* feature's own `feature.json` was malformed) is gone.
It is replaced by "T-05 unrelated non-object feature record does not block healthy merge"
(`test-merge-gate.py:124-131`): a healthy `entry="opened"` feature plus an **unrelated**
`FEAT-9002-unrelated-malformed/feature.json` holding `[]` → asserts `rc==0 and d is None`. This
is the correct control for the cycle-3 finding (an unrelated malformed record must not decide a
different feature's merge) and is a genuinely different assertion from what it replaced, not a
relabeling.

## Posture binding table

| posture | bound by | assertion |
|---|---|---|
| (a) internal error on a MATCHED feature denies, naming that feature | `T-05 empty plan fails closed` (`test-merge-gate.py:118-123`) | `d == "deny" and "FEAT-9001-fixture-non-era" in reason` — `plan.yaml` truncated to empty forces `feature_schema.recovery_command_for` to raise *after* `feat` is set from the matched `feat_dir` (merge-gate.py:140), landing in the `except Exception` naming branch (merge-gate.py:157) |
| (b) failed GitHub read on a feature owing nothing allows, no decision, DEC-138 stderr | `T-05 gh outage with no matching feature allows` (`test-merge-gate.py:111-112`) | `d is None and "could not verify" in r.stderr` |
| (c) malformed record for a DIFFERENT feature is invisible | `T-05 unrelated non-object feature record does not block healthy merge` (`test-merge-gate.py:124-131`) | `r.returncode == 0 and d is None` with a healthy feature present |

All three postures are bound by name. (a) and (b) are mutually exclusive by construction (a
requires `document` matched; b requires `document is None`), so no case — and no useful
reconstruction — can hold both at once.

**Coverage gap, not a defect:** no case in the standing suite exercises posture (a) or (b)
*together with* (c) in one fixture — i.e., nothing pins that a malformed unrelated record stays
invisible while the current feature is independently hitting an internal error, or while it is
independently gh-outage-allowed. I reconstructed both pairs by hand in a throwaway `/tmp` fixture
(not committed, not in the tracked tree) reusing the suite's own `fixture()`/`gate()` shapes
against `merge-gate.sh`:

- (a)+(c): matched `FEAT-9001` with an empty `plan.yaml` *and* an unrelated malformed
  `FEAT-9002-unrelated-malformed/feature.json=[]` present → denied, reason still names
  `FEAT-9001-fixture-non-era`. No conflict.
- (b)+(c): gh-outage, no-match-owing-nothing (`branch="other"`) *and* an unrelated malformed
  `FEAT-9003-unrelated-malformed/feature.json=[]` present → allowed, `d is None`, DEC-138 stderr
  present. No conflict.

Both pairs currently hold clean — this is a reasoned-and-measured absence of conflict, not a
finding of a live defect. But since neither pair is bound by any test **in the suite itself**, a
future edit that narrows the `isinstance(document, dict)` guard to only fire on `feature_for`'s
*first* match, or that reorders the `feat` assignment relative to the internal-error path, could
regress either pairing silently. Recommend a dev/test-owner add one case per pair; not gating
this cycle since no defect was found and authoring tests is outside this dispatch's non-goals.

## Files touched

Exactly this note.
