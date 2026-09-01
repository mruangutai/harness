# Handoff — BUG-1071, build → validate — written at bf12a96b, seq-2

## Next

Dispatch `harness-validator-lead` to run the reviewer panel against `review_sha`
bf12a96b, base 75daa3bb. The diff is two files. Judge whether the era boundary is the
right rule and whether the four new assertions bind what they name — the code-review and
QA questions, not a UI one.

## Trust

- The gate is green on the real tree: exit 0, 0 violations, 32 INV-32 notes — 31 pre-era,
  1 undated — `check-state.sh` in this worktree — verified-at bf12a96b
- `test-check-state.py` is 151 ok / 0 FAIL, exit 0 — verified-at bf12a96b
- The four new cases were RED first, failing for the intended reasons: pre-era violated,
  boundary inexact, undated violated, markers absent — verified-at 75daa3bb + working tree
- The era guard is load-bearing, not decorative: excising ONLY the marked region flips the
  pre-era case from 0 violations to 1 — `case_inv32_era_guard_is_load_bearing` —
  verified-at bf12a96b
- The two pre-existing INV-32 cases still pass unchanged, so the fixture's new `date`
  parameter defaults post-era and disturbs nothing — verified-at bf12a96b
- `feature.json` was written through `feature_json_write.write_feature_json`, the locked
  writer, never a hand-edit — BUG-1030's own ruling — verified-at bf12a96b

## Dead ends

- Asserting on `check-state.sh`'s exit code in the new cases — a bare fixture holding only
  `plan.yaml` is red for unrelated reasons, so the assertion would bind those invariants
  instead of the guard; measured, and it is why the first green run still showed 4 FAIL —
  verified-at working tree, 2026-08-31
- Adding a `plan.yaml` to earn INV-17's main-session-direct handoff exemption — it would
  pull this record into INV-3 and, dated today, into INV-32's own post-era half —
  source: this build, 2026-08-31

## Working set

- `.claude/skills/harness/bin/check-state.sh` — `INV-32 ERA BEGIN/END (BUG-1071)`, 180-216
- `.claude/skills/harness/bin/test-check-state.py` — the four `case_inv32_*era*` cases, 3119-3201
- `.harness/harness/features/BUG-1071-inv32-era-guard/review_sha` — the pin
- `issue://1071` — the defect, with the measurements that opened it
