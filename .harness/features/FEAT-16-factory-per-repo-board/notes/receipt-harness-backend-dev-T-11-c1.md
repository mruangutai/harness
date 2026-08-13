# Receipt — harness-backend-dev — T-11 — c1

## Task
T-11: Migrate the `factory_workspace` test fixture to a per-repo board.

## What changed
Edited the `good_fleet_dict` helper in
`.claude/skills/harness/bin/test-factory-workspace.py` — the sole fixture builder in the file.
Deleted the top-level `board:` key and moved its mapping (`owner`, `number`, `station_field`,
`stations` — unchanged values) onto the single `repos[0]` entry as its own `board:` key. No
assertion, case name, expected exit code, or any other fixture in the file was touched.

Confirmed before editing: `grep -n "board" test-factory-workspace.py` matched only the one
occurrence inside `good_fleet_dict` (line 49) — no other fixture in the file carries a
top-level or per-repo board, so this is the only helper that needed migration.

## Verify

Command (verbatim from plan T-11 and this dispatch):
```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit
```

Run with the exit code captured directly off the suite (not off `tail`):
```
$ .claude/skills/harness/bin/run-unit-tests.sh --kind unit > <scratch>/t11-verify2.txt 2>&1
$ echo "SUITE_EXIT=$?"
SUITE_EXIT=0
```

Verbatim output belonging to `test-factory-workspace.py` — the file this task edits —
extracted from that run:
```
ok    (A) missing checkout: exits 0
ok    (A) missing checkout: first call is clone
ok    (A) missing checkout: some later call checks out the issue branch
ok    (A) missing checkout: no fetch
ok    (B) existing checkout: exits 0
ok    (B) existing checkout: fetch is called
ok    (B) existing checkout: clone is never called
ok    (C) missing checkout: final command checks out the issue branch
ok    (C) existing checkout: final command checks out the issue branch
ok    (D) origin carries the ref: final checkout tracks origin
ok    (D) origin carries the ref: no command names both the issue branch and origin/<default_branch> together (the T-07 divergence bug)
ok    (E) origin has no ref: final checkout is created off origin/<default_branch>
ok    (F) existing local branch tracking origin: checked out as-is, not recreated with -b
ok    (F2) local branch diverges from origin (cut from default_branch): NOT a bare checkout (the fail-open shape)
ok    (F2) local branch diverges from origin (cut from default_branch): final command force-aligns onto origin/factory/issue-42
ok    (F2) local branch diverges from origin (cut from default_branch): still exits 0 (repaired, not refused)
ok    (F2) local branch diverges from origin (no upstream at all): NOT a bare checkout (the fail-open shape)
ok    (F2) local branch diverges from origin (no upstream at all): final command force-aligns onto origin/factory/issue-42
ok    (F2) local branch diverges from origin (no upstream at all): still exits 0 (repaired, not refused)
ok    (G) unlisted repo: exits 2
ok    (G) unlisted repo: zero git calls
ok    (H) a failing git command exits non-zero
ok    (I) happy path: stdout is exactly one JSON object
ok    (I) happy path: payload has path and branch
ok    (I) happy path: payload path is absolute
ok    (J) unlisted repo refusal: nothing on stdout
ok    (J) unlisted repo refusal: exactly one stderr line
ok    (J) unlisted repo refusal: that line names the repository
ok    (J) unlisted repo refusal: exits 2
ok    (K) a plain RuntimeError from run_git exits 2, not 1

30/30 checks passed.
PASS test-factory-workspace.py
```

Every case (A)–(K) runs through `run_main`, which calls `write_fleet(good_fleet_dict(...))`
and `fw._main` → `factory_config.load_fleet` — so the migrated fixture is exercised through
T-01's current loader on every case, not just constructed and discarded.

Tail of the full suite run (remaining files, for completeness — this run also included
`test-factory-config.py` at 73/73, `test-factory-land.py`, `test-no-distribution.py`, and
`test-validate-feature-json.py`, all `ALL PASS`):
```
ALL PASS
PASS test-no-distribution.py
PASS accepted_all_eleven_keys
PASS accepted_only_eight_required_keys
PASS accepted_omitting_optional_max_total_runs
PASS accepted_omitting_optional_github
PASS accepted_omitting_optional_factory
PASS rejected_omitting_required_feature_id
PASS rejected_omitting_required_branch
PASS rejected_omitting_required_pr
PASS rejected_omitting_required_status
PASS rejected_omitting_required_review_sha
PASS rejected_omitting_required_cycles_used
PASS rejected_omitting_required_max_total_cycles
PASS rejected_omitting_required_runs
PASS accepted_status_Backlog
PASS accepted_status_Plan
PASS accepted_status_Ready
PASS accepted_status_Building
PASS accepted_status_Review
PASS accepted_status_Done
PASS rejected_phase_undeclared
PASS rejected_undeclared_top_level_key
PASS rejected_undeclared_runs_item_key
PASS rejected_undeclared_github_sub_key
PASS rejected_prose_key_runs_item
PASS rejected_status_shipped
PASS rejected_status_lowercase_done
PASS rejected_pr_string_none
PASS cli_clean_file_exit_exactly_0
PASS cli_invalid_file_exit_exactly_1
PASS cli_invalid_file_stderr_names_branch
PASS cli_jsonschema_unavailable_exit_exactly_3
PASS cli_jsonschema_unavailable_not_0_or_1
PASS cli_jsonschema_unavailable_stderr_names_required
PASS json_extension_rejects_yaml_content
PASS yaml_extension_accepts_same_content
PASS problems_for_text_at_least_two_problems
PASS problems_for_text_display_path_in_every_line
PASS forced_unavailable_returns_non_empty
PASS forced_unavailable_single_line
PASS forced_unavailable_names_required
PASS forced_unavailable_names_install_command

ALL PASS
PASS test-validate-feature-json.py
```

**Correction note:** an earlier draft of this receipt attributed a `64/64 checks passed` line
to `test-factory-workspace.py`. That line actually belongs to `test-factory-land.py` (its
`(M1)`–`(M7)`/`(T04-1)` land-test cases), a different file entirely. `SUITE_EXIT=$?` was also
first measured against `tail`'s exit status, not the suite's. Both were caught before
returning and are corrected above: `test-factory-workspace.py` runs 30/30 checks, and
`SUITE_EXIT=0` is now the suite's own exit code, captured directly.

## TDD note
No new test/assertion was written — the task intent explicitly bars adding one ("no
assertion, no case name, no expected exit code, no other fixture"). This is a schema
migration of a fixture, not new production behavior, so the Iron Law's RED-before-code cycle
does not apply: nothing new is being asserted for the first time. The existing suite (already
green pre-edit, exercising the fixture through `load_fleet`) stayed green post-edit, which is
what the task requires.

## Scope confirmation
`git diff --stat` shows exactly one file changed, 10 insertions / 7 deletions, entirely
inside `good_fleet_dict`. No other file touched. `.harness/factory/fleet.yaml`,
`factory_config.py`, `factory_workspace.py`, and the DEC-174 carve-out scripts were not
opened for writing.
