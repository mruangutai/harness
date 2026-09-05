# REUSE angle — BUG-1306 hermeticity diff — receipt

**Verdict: PASS, nothing found.** The two-hunk diff does not re-implement anything the tree
already has, and no other file must now be edited in lockstep with it.

## What I checked

- `grep -n "HARNESS_AGENT_TYPE" tests/` — only hits are inside this same file
  (`test-plan-merge.py:140`, `:1099`, `:1121`) plus an unrelated TS unit test
  (`omp-hooks.test.ts:311-333`, a different mechanism — the OMP host merging the var into a
  bash call's env, not a test scrubbing it). No sibling Python integration test references
  `HARNESS_AGENT_TYPE` at all, so there is no second spelling of this guard to keep in sync.
- `grep -n "environ\.pop|environ\[.HARNESS" tests/` — every hit is a *different* env var
  (`CLAUDE_PROJECT_DIR`/`HARNESS_PROJECT_DIR` in `test-harness-yaml.py` and
  `test-harness-boundary.py`, `LC_TIME` in `test-inflight-registry.py`, `FACTORY_DEBUG` in
  `test-factory-cli.py`, `HARNESS_GH_COST_LOG` in `test-gh-cost-log.py`/`test-factory-gh.py`,
  ambient wildcard-pop in `test-wayfind.py`). Each of these files rolls its own inline
  save/pop/restore for its own variable — that is this codebase's established, repeated
  pattern for scrubbing ambient environment in a script-style (non-pytest-fixture) suite.
  There is no shared helper (e.g. `with_clean_env(name)`) any of them import, so the new
  one-line `os.environ.pop("HARNESS_AGENT_TYPE", None)` at module import matches the existing
  convention rather than diverging from it.
- No `conftest.py` or `*bootstrap*` file exists under `tests/` or `tests/integration/`
  (glob came back empty) — confirms there is no shared fixture layer this pop should have
  been routed through instead.
- `tests/integration/test-expertise-merge.py:1-43` (sibling suite, same module-header
  convention, same `_anchor_*` sys.path shim) — does not touch `HARNESS_AGENT_TYPE` or any
  process environment at all, because `expertise-merge.py`'s CLI never calls
  `cmd_sign_approval`. Nothing to reuse or duplicate there.
- Within the same file, `case_1103_sign_approval_...` (~line 1107) builds
  `dict(os.environ, HARNESS_AGENT_TYPE="harness-pm")` and the negative control (~line 1130)
  builds a filtered dict excluding the same key. These are per-call-site test data (setting
  a *specific* identity for the case under test), not a second implementation of the
  module-level guard — they operate downstream of the already-hermetic `os.environ` the pop
  established, and are the byte-identical case bodies the contract's LEAVE item already
  covers. Not raised as a finding.

## Conclusion

No importable helper, constant, fixture, or shared bootstrap already scrubs
`HARNESS_AGENT_TYPE` (or models a "clean env for this suite" concept) anywhere in `tests/`.
No sibling integration test spells the same guard, so there is no second spelling requiring
lockstep edits. The one-line pop plus docstring sentence is the smallest change consistent
with this codebase's existing per-file inline env-scrubbing convention. Findings: none.
