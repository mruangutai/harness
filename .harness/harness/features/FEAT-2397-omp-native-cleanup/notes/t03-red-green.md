# T-03 red/green: redundant CLAUDE_PROJECT_DIR test setup removed

T-03 removes setup and adds no behaviour, so there is no red step. The proof has three parts. Each owned test file passes before the edit and passes after it. A grep shows each redundant assignment is gone, and the same grep shows the sanitizers are still there.

## Before (unedited, worktree HEAD afcb9816 + peer work in progress)
All 14 owned files exited 0. Files: test-branch-create-gate, test-check-domain-post, test-check-domain, test-check-state-corpus, test-check-state-shipped, test-corpus-non-regression, test-corpus-real-owner, test-feature-corpus, test-hooks-install, test-layout-migration, test-lead-start-return (integration). Also test-check-state-inv35, test-lead-start-preflight, test-prune-run-evidence (unit).

## Change
- Removed every `CLAUDE_PROJECT_DIR=<root>` assignment from the owned files. That is 18 sites across 13 files. `HARNESS_PROJECT_DIR=<root>` stays at every site. No bin/ script reads the host-owned name any more, because `harness_boundary.resolve_root` reads only HARNESS_PROJECT_DIR.
- Root markers are unchanged. These include test-layout-migration's `.harness/team-config.yaml` marker.
- The hermetic sanitizer is kept. test-prune-run-evidence.py:228 still clears both inherited names before setting HARNESS_PROJECT_DIR.
- Updated the root descriptions that read as current:
  - test-branch-create-gate fire(): "BOTH NAMES" is now "ONE NAME"
  - test-layout-migration: "BOTH NAMES, AND THE MARKER" is now "ONE NAME, AND THE MARKER"
  - test-check-domain-post: the case-F docstring now says `_derived` is a fallback for HARNESS_PROJECT_DIR, set through `_env`
- Not touched: root-nonredirect tests, historical comparison subjects (the sha-3952814 parity text stays) and prior-*.fixture.

## After
All 14 owned files exited 0.

Grep `CLAUDE_PROJECT_DIR` over the 14 files finds exactly one hit, the sanitizer:
`tests/unit/test-prune-run-evidence.py:228: env = {k: v ... if k not in ("CLAUDE_PROJECT_DIR", "HARNESS_PROJECT_DIR")}`

HARNESS_PROJECT_DIR is still present in each of the 14 files.

## Literal verify
`run-unit-tests.py --check-layout`, then `check-plan-routes.py --canonical-reader-audit`, then `tests/integration/test-hooks-install.py`, all under `set -eu`. The run exited 0, and test-hooks-install ended with EXIT=0.
