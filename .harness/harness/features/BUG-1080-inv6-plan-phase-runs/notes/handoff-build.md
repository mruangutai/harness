# Handoff - BUG-1080, build -> validate - written at a2fb6c0b, seq-2

## Next

Dispatch `harness-validator-lead` to run the reviewer panel against `review_sha`
`a2fb6c0b`, base `9f2a0702`. The diff is three files, +158/-5. Judge whether the exemption
is keyed on the right thing, and whether the fail-closed default is actually closed.

- `.claude/skills/harness/bin/check-state.sh:419-460` - the runs loop and the INV-6 predicate
- `.claude/skills/harness/bin/feature-schema.json:61` - the closed `code_grade` enum
- `.claude/skills/harness/bin/test-check-state.py` - `case_inv6_*`, six cases
- `issue://1080` - the defect and its measurements
- `.harness/harness/features/BUG-1080-inv6-plan-phase-runs/notes/` - panel notes go here

## Trust

- claim - 161 ok / 0 FAIL, gate exit 0 with 0 violations, full `run-unit-tests.sh` exit 0
  with zero FAIL lines - verified-at a2fb6c0b - source: this build ran all three.
- claim - the six cases were red first - verified-at a2fb6c0b - source: pre-fix run gave
  exit 1 with exactly 2 FAIL, both the exemption cases; the four guard cases passed before
  and after, which is what makes them regression guards rather than new assertions.
- claim - the fail-closed default is load-bearing - verified-at a2fb6c0b - source: a mutant
  changing `entry.get("code_grade", "")` to `entry.get("code_grade", "n_a")` is caught by
  4 cases, two of them pre-existing (case e, case h).
- claim - `runs` stays a 3-tuple - verified-at a2fb6c0b - source: `grep 'in runs'` returns
  three unpackings, all still 3-wide.

## Dead ends

- Keying on `approval.status` - UNVERIFIED as a fix, ruled out by reasoning and now pinned
  by `case_inv6_exempt_survives_signature`. Source: handoff-plan.md, same entry.
- Treating the PRESENCE of `code_grade` as the exemption - source:
  `case_inv6_unknown_grade_fails_closed` fails on it; the value is read, not the key.

## Working set

- `.claude/skills/harness/bin/check-state.sh`
- `.claude/skills/harness/bin/test-check-state.py`
- `.claude/skills/harness/bin/feature-schema.json`
- `.harness/harness/features/BUG-1080-inv6-plan-phase-runs/feature.json`

## Not done here, and deliberately

FEAT-46's `feature.json` still records two validator runs without `code_grade: n_a`, so
INV-6 will keep firing on that feature until the field is backfilled. That backfill is the
main session's, after this merges - the field is not schema-legal until then.
