## Patterns (max 15)
- P-01: CANARY-7f3a9b — this line exists only to prove Expertise injection fires.
- P-02: WHEN a task's listed verify steps are grep receipts plus a test suite that imports code
  standalone DO add a smoke check that actually imports/executes the changed module through its
  real call path — a broken import can leave every listed receipt green.
- P-03: WHEN asserting a call was removed via a log grep DO scope the grep to the payload, not the
  path — a path-only absence grep can vacuously "prove" removal while unrelated calls sharing that
  path remain.
- P-04: WHEN a task claims a change is byte-identical to a previously deployed file DO diff against
  the copy under `~/.claude/skills/harness/bin/` as the pre-change reference, rather than trusting
  the claim from context alone.

## Gotchas (max 15)
- G-01: The harness repo has no application source; src/** is empty here.
- G-02: WHEN a test suite's docstring or label claims a specific contract DO treat it as an
  unverified claim and check the adjacent assertion actually matches it — a stale label can
  propagate across review tiers as if it were a measurement.
- G-03: WHEN writing fixtures against the fake-gh test harness DO read its logging and
  issue-numbering behavior in `.claude/skills/harness/bin/test-gh-sync.py` first — assumptions
  about counters, log format, or which calls get logged fail loudly but still cost a debug cycle.

## Outcomes (max 10)

## Open (max 5)
