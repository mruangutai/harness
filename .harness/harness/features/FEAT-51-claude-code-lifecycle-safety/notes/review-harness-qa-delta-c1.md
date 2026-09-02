# QA delta review — FEAT-51, cycle 2, pin `aab31504`

**BLUF: all 9 new cases across the two suites are genuinely discriminating — measured, not
trusted, against a real pre-fix `fa5ce88e` binary via `QUARANTINE_BIN`/`VALIDATE_DIGEST_BIN`
overrides in a disposable worktree. Both deletions (case 12's two byte-unchanged assertions)
are justified by direct measurement, not narrative. The two retargets (cases 9, 11) are a
genuine strengthening. F-1 has a permanent regression test that hits the exact combination
the premise note flagged as missing. `code_grade`: PASS (13/13, no FAIL line).**

## Suite counts at the pin

- `test-quarantine.py`: exit 0, **35 checks** (34 `PASS` lines + 1 trailing `PASS
  test-quarantine.py` summary line) — matches the lead's measurement.
- `test-validate-digest.py`: exit 0, **all green** across CLI (69), empty-red (1),
  dec156-worktree-red/joint-hint/etc, hook (19), T-09 (24), the 10 T-51 suspension cases,
  template (2), reviewer enum (18). `ALL PASSED.`

## New cases since `fa5ce88e`

`git diff fa5ce88e..aab31504 -- test-quarantine.py test-validate-digest.py` — **0 deletions
in the committed diff** (both files show insertions only; the receipt's claimed case-12
deletion and case-9/11 retarget happened inside dev-ops's own uncommitted cycle-1→cycle-2
iteration before `aab31504` was ever written, so they never appear as a `-` line against
`fa5ce88e`). New function defs: `case_9`, `case_10`, `case_11`, `case_12`, `case_13` in
`test-quarantine.py`; `_t51_missing_message` in `test-validate-digest.py`.

### Discrimination table — `test-quarantine.py`

Method: `git show fa5ce88e:.../quarantine.py` materialized into a real sibling-import-capable
tree via `git worktree add <abs path under .claude/worktrees/> fa5ce88e` (bash-write-guard
denies ad hoc scratch-file writes into `bin/`; a worktree is the sanctioned route per
Expertise G-06/repo-tier). `QUARANTINE_BIN` pointed at that worktree's `quarantine.py`, current
(pinned) `test-quarantine.py` run against it unmodified. Worktree removed after.

| case | assertion | pre-fix (`fa5ce88e`) | at pin (`aab31504`) | discriminating |
|---|---|---|---|---|
| 9 | exits 2 | **FAIL** (exit 0, `ADOPTED .../notes/feature.json`) | PASS | **yes** |
| 9 | canonical byte-unchanged | PASS (secondary) | PASS | no (paired w/ #9's exits-2, not standalone) |
| 10 | exits 2 | **FAIL** (exit 0, cross-feature overwrite) | PASS | **yes** |
| 10 | victim byte-unchanged | **FAIL** (victim overwritten) | PASS | **yes** |
| 11 | exits 2 | **FAIL** (exit 0, wrong-canonical adopt) | PASS | **yes** |
| 11 | canonical byte-unchanged | PASS (secondary) | PASS | no (same shape as #9) |
| 12 | exits 2 (sole remaining assertion) | **FAIL** (exit 0, symlink escape adopted) | PASS | **yes** |
| 13 | exits 2 | **FAIL** (exit 0, foreign-root adopt) | PASS | **yes** |
| 13 | victim byte-unchanged | PASS (secondary) | PASS | no (same shape) |

5/5 cases carry at least one assertion that flips red→green across the fix; each case's
primary `exits 2` check is that discriminator. The "byte-unchanged" secondaries on 9/11/13
passing on both binaries is expected and not a defect: on the pre-fix binary the containment
bug produces a wrong-but-different write target (one level shallow/deep, or a sibling
`notes/` path), so the intended canonical file is untouched for an unrelated reason — the
receipt's own framing, independently confirmed here by measurement rather than accepted from
its narrative.

### Case 12's two deleted assertions — verdict: justified

Case 12 (symlink escaping the quarantine dir) originally carried `escape target
byte-unchanged` and `canonical byte-unchanged` alongside `exits 2`. Measured directly: on the
pre-fix binary, `exits 2` is the only one of the three that goes red (exit 0 → 2). The two
byte-unchanged checks were never capable of catching this regression — `plan-merge.py`'s own
schema refusal on the escape file's non-plan-shaped content left both targets untouched on
old code too, for a reason unrelated to `quarantine.py`'s own containment. Deleting a
genuinely non-discriminating assertion, leaving the one real discriminator standing, is a
cleanup, not a weakening. **No hidden regression: the file's containment behavior is still
fully covered by `exits 2`, confirmed red on pre-fix, green at pin, above.**

### Cases 9 and 11 retarget (`plan.yaml` → `feature.json`) — verdict: strengthening

Measured against the true pre-fix `fa5ce88e` binary (not just the two intermediate binaries
the receipt used): `feature.json` takes `harness_merge.locked_update`, which has no
downstream schema guard of its own — unlike `plan.yaml`, which used to have `plan-merge.py
apply`'s `require_destination` capable of masking a missing quarantine.py-side containment
check by refusing for an unrelated reason. Table above shows both cases going **exit 0 →
exit 2** across the fix on `feature.json`, so quarantine.py's own refusal is now what's being
tested, not a downstream guard's coincidental agreement. This is a real strengthening,
verified independently rather than inherited from the receipt's own RED proof.

### `plan-sign-gate.py` route recognition — spot check

Grepped for the literal `quarantine` path-segment routing the finding described:
`plan-sign-gate.py` and `quarantine.py` both now route through the shared
`_quarantine_containment`/root-anchored regex rather than a bare basename+`quarantine`
substring check (confirmed at `quarantine.py:48-66`, cited above). Full re-audit of
`plan-sign-gate.py`'s own adopt-route recognition is the security/code reviewers' lane per
the dispatch's division of labor; not re-litigated here beyond confirming the shared helper
exists and is what `cmd_adopt` calls.

## F-1 regression coverage — YES, permanent test exists

`_t51_missing_message` (`test-validate-digest.py:1477`) fires `validate-digest.py --hook`
directly (not through the CLI wrapper) with `agent_type: harness-product-lead` (a **lead**,
satisfying the "lead/orchestrator payload" half of the combination), a live child claim
seeded via `_t51_fixture` (satisfying "live child claim"), and `last_assistant_message`
either fully **absent from the payload** or explicitly **`None`** — exactly the two variants
the premise-check note said were missing. Both are asserted `exit 2` and "parent claim still
live" (2 checks × 2 labels = 4 new checks).

**Measured against `fa5ce88e`'s `validate-digest.py`** (same worktree-override technique,
`VALIDATE_DIGEST_BIN`): all 4 new checks go **red** — exit 0, `check-digest: released the
#551 claim ... NOT VALIDATED`, i.e. reproduces the exact silent-release regression F-1
described. Full-suite run against the pre-fix binary: **4 FAILING**, all four belonging to
`_t51_missing_message`; every other case (65 others) stays green — confirms the fix is
narrowly targeted and this is the sole regression surface it touches. At the pin, all 4 pass
(`if _kids:` unconditional, `validate-digest.py:1712`).

## Verify

```
cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-51-claude-code-lifecycle-safety
python3 .claude/skills/harness/bin/test-quarantine.py; echo $?              # 35 checks, rc=0
python3 .claude/skills/harness/bin/test-validate-digest.py; echo $?         # ALL PASSED, rc=0
python3 .agents/skills/harness/bin/code-grade.py .claude/skills/harness/bin/quarantine.py
  # PASSING: 13, no FAIL line
```

Mutation-proof commands (worktree since removed; re-creatable):
```
git worktree add /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/<scratch> fa5ce88e
QUARANTINE_BIN=<scratch>/.claude/skills/harness/bin/quarantine.py \
  python3 .claude/skills/harness/bin/test-quarantine.py
VALIDATE_DIGEST_BIN=<scratch>/.claude/skills/harness/bin/validate-digest.py \
  python3 .claude/skills/harness/bin/test-validate-digest.py
git worktree remove /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/<scratch>
```

## Not re-litigated

REQ-01..07, D-01..19, the qa test matrix, the ui census, the signed SC-13 fail-open
`except Exception`, the seven `test-check-plan-routes.py` manifest-DEVIATION integration
failures (operator's accepted gate of record). Whether `plan-sign-gate.py`'s full adopt-route
logic is otherwise sound is the reviewers' lane, not re-audited here beyond the spot check
above.
