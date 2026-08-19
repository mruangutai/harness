# EFFICIENCY angle — FEAT-25 plan surface — receipt

No EFFICIENCY findings. The plan's three `verify:` blocks were timed against `ada8e99`
(measured, not estimated) and none does wasted work by this angle's own bar (minutes,
hot-path milliseconds — DEC "the pass" per `harness-simplify` SKILL.md `## EFFICIENCY`).

## Timings (this checkout, `.claude/skills/harness/bin`)

| suite | time | run by |
|---|---|---|
| `test-factory-claim.py` | 0.07–0.08s | T-01 (113→115 ok), T-02 again (115→119 ok) |
| `test-factory-integration.py` | 6.60s | T-01 only |
| `test-layout-migration.py` | 0.50s | T-03 |
| `test-check-state.py` | 7.93s | T-03 (step 5, shared-fixture proof) |

Total across all three tasks' verify blocks, sequential: ≈15.2s. That is the ceiling for the
whole plan's test-running cost — not a hot path (no per-session or per-write gate here), and
well under "minutes."

## Why each full-suite run is boundary evidence, not waste

- **T-01** runs both suites touching `factory_claim.py`'s constant (`test-factory-claim.py`,
  `test-factory-integration.py`) once, at the task that changes the constant. This is the
  boundary the fix lands at — exactly the case the skill exempts.
- **T-02** re-runs `test-factory-claim.py` (0.08s) after depending on T-01, because T-02 adds
  four *new* cases to that same file and further edits `factory_claim.py`. It does **not**
  re-run `test-factory-integration.py` (6.6s) — the expensive suite runs exactly once across
  the whole plan. At 0.08s the re-run costs nothing regardless.
- **T-03** runs `test-layout-migration.py` (0.5s, the suite it's actually testing) plus
  `test-check-state.py` (7.93s) as intent step 5's explicit shared-fixture proof: T-03 edits
  `layout_fixtures.STUB`, and `test-check-state.py` builds its own sandbox from every STUB key,
  so it is the one place that dependency is exercised. No narrower invocation exists to reach
  for instead (see below), so this is forced, not a design choice that skipped a cheaper option.

**No test-selection alternative exists to be flagged as unused.** All four suites are
hand-rolled sequential scripts (`case_a()`, `case_b()`, … run unconditionally from
`if __name__ == "__main__"` in `test-check-state.py`; no `sys.argv`-driven case filter in any
of the four — checked directly, not inferred). A "targeted case binds equally" alternative,
which this angle is instructed to look for, is not available in this tooling; proposing one
would mean building test selection into four scripts, which is out of this plan's scope and a
much larger cost than 15s of CI time.

## `_BlockerCache` caching property (T-02)

T-02's intent for `plan_loaded()` explicitly requires it "go through the same caching path
`task()` uses… populate the cache by calling the same private load if it is not present yet."
As specified, this holds the one-read-per-poll property `_BlockerCache` exists for
(`factory_claim.py:88-90` docstring). No finding — the instruction itself enforces the
property this angle checks for; it does not merely permit it.

## Advisory on the record — CONFIRMED, not re-reported

The three prose-only corrections at `factory_claim.py:25-27`, `test-factory-claim.py:5`,
`test-factory-integration.py:31` carry no `verify:` gate (comma-form grep pattern vs
slash-form prose). Not an efficiency concern either way — confirming per the dispatch's
instruction to confirm-or-challenge, not re-flagging.

## Verdict

Empty return, honestly arrived at: every full-suite run is boundary evidence at the task that
changes the file it covers, the one duplicate run is 0.08s, and the one expensive suite
(`test-check-state.py`) has no cheaper invocation shape available.
