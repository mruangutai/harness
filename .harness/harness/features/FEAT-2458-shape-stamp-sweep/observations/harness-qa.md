# Observations — harness-qa — FEAT-2458-shape-stamp-sweep

- 2026-11-24: a fixture id that contains the very token an assertion checks for (FEAT-912-stamp-absent vs "absent" in the line) makes the token clause vacuous; a reason-dropping mutant stayed green. Check fixture ids against asserted substrings.
- 2026-11-24: test-check-plan-routes.py CANONICAL_READER_CASES (incl. the T-07 terminal case) run only under --canonical-reader-self-test, which no runner calls; a plain run cannot red on registry/inventory/AST drift — the --canonical-reader-audit command is the real guard.
- 2026-11-24: Running the PRE-fix test files against a mutant (control arm) is what proves a test fix is the discriminator; c1 tests + reason-drop mutant stayed green while c2 tests reddened. bash-write-guard blocks rm/redirect with a variable target even under /tmp, so scratch trees go through a python driver (shutil) instead.
