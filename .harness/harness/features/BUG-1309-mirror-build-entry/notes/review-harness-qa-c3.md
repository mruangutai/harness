# QA gate re-run — BUG-1309-mirror-build-entry, cycle 3

Pin: `0f8ec4bda7c96050d2d9bcddb30f96132cde5b54` (worktree `.claude/worktrees/harness/BUG-1309-mirror-build-entry`).
Change: fail-closed remediation of `.claude/skills/harness/bin/merge-gate.py`, wrapping the
build-entry evaluation body (from `import feature_schema` through the final `deny(...)`) in
`try/except Exception: deny("...could not evaluate this feature's Build-entry receipt...")`.
Test file `tests/integration/test-merge-gate.py` grew by 12 lines / 2 new cases (verified via
`git show 0f8ec4bd -- tests/integration/test-merge-gate.py`).

## Matrix resolution

`change_type: bugfix` (harness.json:203-219). Predicates evaluated against the diff:
- `touches_runtime_code` → **true** (merge-gate.py is production code) → requires **unit**.
- `fix_confined_to_tests_and_contract_docs` → **false** (production file changed, not test-only)
  → **integration** is not matrix-obligated for this change.
- `match_bug_class` (`__bug_class__`) → per this repo's own QA Expertise (G-08, repository tier),
  no bug-class taxonomy entry currently resolves for any diff — this leg is an unresolvable
  placeholder and contributes nothing to the floor.

**Matrix floor: `unit` only.** I additionally ran `integration` because that is where
`test-merge-gate.py` itself lives and is the only suite directly exercising the new except-branch —
running it is a floor-exceeding addition the diff clearly warrants, not a matrix requirement.

## Results

| kind | state | cmd | discovered | result |
|---|---|---|---|---|
| unit | satisfied | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 33 files, 1291 `ok`/`PASS` lines (incl. `test-omp-hooks.py`: bun test, 56 pass / 0 fail) | exit 0, zero FAIL |
| integration (added) | satisfied | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 50 files | exit 0, zero FAIL/ERROR across 3951 output lines |
| `test-merge-gate.py` (within integration) | satisfied | same runner | **18/18** `ok` lines, `ALL PASSED`, exit 0 | pass |
| `test-gh-sync.py` (adjacent, requested) | satisfied | same runner | **322** `ok` lines in its block, exit 0 (48.86s) | pass |
| `test-omp-hooks.py` (adjacent, requested) | satisfied | same runner (unit kind) | **56 pass / 0 fail** (bun test) | exit 0 |

Ran with `env -u HARNESS_AGENT_TYPE` per this repo's own Expertise G-07 (setting it produces a false
`test-plan-merge.py` regression unrelated to this diff).

`matrix_ok: true` — the one matrix-required kind (`unit`) is satisfied, and every kind I added
beyond the floor is also satisfied.

## Adequacy of the 18 `test-merge-gate.py` cases (the actual question)

Only **2 of 18** cases are new at this pin and bind the fail-closed behavior directly:
- `T-05 empty plan fails closed` — `plan.yaml` truncated to 0 bytes → asserts `d == "deny"` and
  `"could not evaluate" in reason`.
- `T-05 non-object feature record fails closed` — `feature.json` rewritten to a JSON array →
  same assertion.

Both exercise the new `except Exception: deny(...)` arm specifically (the `"could not evaluate"`
string appears nowhere else in `merge-gate.py`). The remaining 16 cases are pre-existing
allow/deny-logic coverage, unchanged at this pin.

**Yes — the two opposite postures ARE separately pinned, and by three independent signals, not one:**
- `T-05 gh outage with no matching feature allows` (line 112, pre-existing, unchanged): a `gh`
  subprocess failure → `d is None` (allow) and `"could not verify"` in stderr. This is the DEC-138
  posture — mirror-read failure never gates.
- `T-05 empty plan fails closed` / `T-05 non-object feature record fails closed` (new): a local,
  internal evaluation error → `d == "deny"` and `"could not evaluate"` in reason. This is the new
  fail-closed posture.

These are discriminated on (a) opposite decision (`None` vs `"deny"`), (b) disjoint message text
(`"could not verify"` vs `"could not evaluate"`), and (c) disjoint trigger (external `gh` process
failure vs malformed local feature record raising inside the try body) — a regression that
collapsed the two postures into one answer would flip at least one of these three signals, so the
suite is not vacuously green on this axis. This is a **reasoned** conclusion from reading the
assertions and the corresponding code branches at the pin (not a fresh mutation run in this
dispatch — author-nothing scope) but the discrimination is structural (different message constants
literally cannot both match), not incidental.

No new case targets the third possible confusion — an internal exception occurring *while* `gh`
is also unreachable (compound failure) — but the two pre-existing/new cases above are sufficient to
pin the contract's two opposite answers separately; this is a minor residual gap, not a finding
against the fix.

## Coverage gaps / findings

None rising to a finding. The remediation is narrowly scoped, the fail-closed arm is directly
tested by name, and the DEC-138 allow-on-read-failure posture remains independently pinned and
green at this pin.
