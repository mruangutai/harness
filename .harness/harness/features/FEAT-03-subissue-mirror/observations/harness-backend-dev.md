# Observations — harness-backend-dev — FEAT-03-subissue-mirror

- 2026-07-31 (T-02): the task's own listed `verify:` lines (grep receipts + `run-unit-tests.sh`)
  never actually import or execute `wayfind.py` — `test-gh-sync.py`/`test-validate-digest.py` don't
  touch it, and the module-import verify checks `gh_issues.py` standalone, not through wayfind's
  `sys.path.insert`. A broken import (bad `realpath` line, `NameError` on the module alias) would
  leave every listed receipt green. Added two extra smoke checks myself: `python3 -c "...import
  wayfind..."` and `python3 wayfind.py` (no args, expect exit 1 from the usage branch) — neither
  calls `gh`. Worth the same gut-check on T-03–T-06, which edit `gh-sync.py` similarly and whose
  verify lists are also grep/suite-only.
- 2026-07-31 (T-03): the fake gh's `n=$(( $(grep -c "issue create" "$FAKE_LOG") + 40 ))` counter
  restarts at 40 per fresh `FAKE_LOG`/tmp dir. A crash-resume fixture that pre-seeds an issue
  number (e.g. `T-01: 41`) will collide with the number the fake assigns to the *next* real
  create in that same run, since the counter only counts creates already in the log — not a
  gh-sync.py bug, just a fixture trap for T-04–T-06 to watch for if they add similar fixtures.
- 2026-07-31 (T-03): `attach_sub_issue_args(repo, parent, child_id)` builds the endpoint on the
  PARENT's number, not the child's — a receipt asserting on "issues/&lt;child&gt;/sub_issues" in
  the call log will never match; assert on `sub_issue_id=<internal id>` in the payload instead.
- 2026-07-31 (T-05): the fake gh's generic `"api -X") case: *milestones -f* -> {"number":7}; else
  -> {}` already covers `PATCH repos/*/issues/*` with no new fake-gh case needed for abandon's
  not_planned closes. Used entirely fresh `tempfile.TemporaryDirectory()` per abandon fixture
  (rather than reusing one `tmp` and resetting `calls.log`) so each parent-origin fixture's fake
  numbering/log has no cross-fixture state to leak — cheap given each fixture is self-contained.
  Also confirmed empirically: `load_config`'s `gh auth status` runs before dispatch for every
  subcommand and IS logged (`"auth status"` line), so a "zero gh calls" receipt for a caller-error
  path must filter it, not assert a literally empty log — the existing "every call pins --repo"
  check already carries this same exception for that reason.
- 2026-07-31 (T-05): the fake-gh's log line is `echo "$*" | tr '\n' '§' >> LOG; echo >> LOG` — two
  physical lines per call (the args line, then a blank separator). A "log == [expected]" equality
  assertion after `calls()` (which is `splitlines()`) breaks on that blank line; filter `if l` or
  use `startswith`, don't assert exact list equality against the raw split.
