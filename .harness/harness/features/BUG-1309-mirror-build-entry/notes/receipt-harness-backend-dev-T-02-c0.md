# Receipt — harness-backend-dev — T-02 — c0

T-02 lands: `gh-sync.py open` now records the Build-entry outcome as a fifth-state
enum (`opened | recovery-required | not-applicable | recovered-terminal | absent`) per
D-04 and D-09, verified against T-01's schema enum (98c650f0).

## Verify (verbatim, from worktree root)

```
out=$(python3 tests/integration/test-gh-sync.py) || exit 1
if printf '%s\n' "$out" | grep -q '^FAIL'; then exit 1; fi
for n in "T-02 open records opened" "T-02 sync false records not-applicable" "T-02 unpinned repo records nothing" "T-02 first-call failure records recovery-required" "T-02 partial remote write records nothing" "T-02 second open stays opened" "T-02 opened never downgrades" "T-02 contract error records nothing"; do
  printf '%s\n' "$out" | grep -qF "ok    $n" || exit 1
done
echo VERIFY-PASS
```
Output: `VERIFY-PASS`. Runner totals: baseline (git-stashed, pre-T-02) 301 ok / 0 FAIL;
post-change 309 ok / 0 FAIL — the 8 new cases, no pre-existing case broken.

## Red-before-green, per case (full run at gh-sync.py:test-gh-sync.py, pre production
edits, post test-only edits)

- `T-02 open records opened` — RED: `FAIL` (build_entry never written).
- `T-02 sync false records not-applicable` — RED: `FAIL` (build_entry never written).
- `T-02 unpinned repo records nothing` — GREEN pre-change, honestly: production wrote
  the field nowhere yet, so absence held vacuously. Post-change it holds by construction
  (`_NO_RECORD` sentinel on the "repo not pinned" skip, D-09), not by accident.
- `T-02 first-call failure records recovery-required` — RED: `FAIL`.
- `T-02 partial remote write records nothing` — GREEN pre-change, same vacuous-absence
  reason as above; post-change the milestone genuinely creates (asserted via
  `milestone == 7`) and the parent-create failure still leaves the key absent (D-04).
- `T-02 second open stays opened` — RED: `FAIL`.
- `T-02 opened never downgrades` — GREEN pre-change: the fixture pre-seeds
  `build_entry: "opened"` and nothing overwrote it (nothing wrote the field at all).
  Post-change it holds because `record_build_entry`'s never-downgrade guard fires on a
  real attempted "recovery-required" write it must refuse.
- `T-02 contract error records nothing` — GREEN pre-change, same vacuous-absence
  reason; post-change `die()` still never calls `record_build_entry` (only `skip()`
  does), so the property is now a real, exercised guarantee, not an absence of code.

## Incidental fixes (in scope: found while making the T-02 change green)

1. Three pre-existing `load_recorded` default-dict equality checks (`T-06C`, `fix1 B
   row1a`, `fix1 B row1b`) broke on the new `build_entry: None` key — expected dicts
   updated to include it (test-gh-sync.py:1372-1398).
2. A genuine regression caught by the pre-existing `not_onboarded` case: `skip()`
   attempting `record_build_entry` for a feature dir whose `feature.json` does not
   exist yet crashed via `save_recorded`'s absent-file refusal instead of printing the
   SKIP line. Fixed by guarding the record attempt on `os.path.isfile(feature.json)`
   in `skip()` (gh-sync.py:172-176) — an un-onboarded tree is not a run any Build
   entry can attach to.

## Files touched

- `.claude/skills/harness/bin/gh-sync.py` — six edits per intent (read side, write
  side, `record_build_entry`, `_BUILD_ENTRY`/`_NO_RECORD` + `skip()` signature, the
  five call sites, `cmd_open`'s terminal write) plus the absent-feature.json guard.
- `tests/integration/test-gh-sync.py` — 8 new T-02 cases, 3 updated default-dict
  expectations, 2 new fake-gh fixtures (`FAKE_GH_FAIL_FIRST`, `FAKE_GH_PARTIAL`).

Every written value (`opened`, `not-applicable`, `recovery-required`) is inside T-01's
closed enum; nothing writes a fifth spelling. `cmd_start_task` untouched.

## Open questions

None.
