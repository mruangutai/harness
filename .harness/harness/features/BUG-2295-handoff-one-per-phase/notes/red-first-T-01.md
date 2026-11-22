# Red-first evidence — BUG-2295 T-01

## Tests added (tests/integration/test-check-domain-post.py)
`_handoff_cycle_suffix_cases`, called from `run_handoff_done_when` after the cap cases:
- `handoff canonical {build,validate,plan} accepted` — Write, valid content, want exit 0.
- `handoff {build-c1,validate-c12,plan-c305} Write refused` — valid content, want exit 2
  with stderr naming `notes/handoff-<phase>.md` and `supersede`.
- `handoff {…} Edit refused` — existing suffixed file, reconstructable Edit, same want.
- `handoff {…} refused Edit leaves file unchanged`.
Existing cap, missing-section and Done when cases are retained unchanged.

## RED — production check-domain.py identical to base dd04e52a
`git diff --quiet dd04e52a -- .claude/skills/harness/bin/check-domain.py` → identical.
`python3 tests/integration/test-check-domain-post.py` → rc=1. Assertion failures (not setup errors):
```
ok    handoff canonical build accepted
ok    handoff canonical validate accepted
ok    handoff canonical plan accepted
FAIL  handoff build-c1 Write refused exit 0:
FAIL  handoff build-c1 Edit refused exit 0:
FAIL  handoff validate-c12 Write refused exit 0:
FAIL  handoff validate-c12 Edit refused exit 0:
FAIL  handoff plan-c305 Write refused exit 0:
FAIL  handoff plan-c305 Edit refused exit 0:
```
(The "refused Edit leaves file unchanged" rows pass at base: a PRE hook never writes.)

## GREEN — after the check-domain.py fix
`python3 tests/integration/test-check-domain-post.py` → rc=0, 96 `ok`, no FAIL; all twelve
rows above `ok`.
`.agents/skills/harness/bin/run-unit-tests.py --kind unit` → rc=0.
`.agents/skills/harness/bin/run-unit-tests.py --kind integration` → rc=0 (91 files).
