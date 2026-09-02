# Receipt — harness-dev-ops — FEAT-51 fix cycle c1 — refresh COLLECT_FIXTURE

## Task
Add `.harness/*/features/*/quarantine/**` as the FIRST element of the `shared` glob list in each
of the six `COLLECT_FIXTURE` entries in `.claude/skills/harness/bin/test-harness-yaml.py`, matching
T-03's addition to the top-level `shared:` block of `.harness/team-config.yaml`.

## Independent count/line-number derivation

Ran `grep -n '"package\.json"'` against the target file before editing:

```
41:        [
42:            "package.json", ...
58:        [
57:...
58:            "package.json", ...
76:            "package.json", ...
92:            "package.json", ...
114:            "package.json", ...
128:            "package.json", ...
```

**Count: 6.** Matches the dispatch's claim exactly. The six shared-list opening lines (the line
holding `"package.json"` as first entry) were at **42, 58, 76, 92, 114, 128**, for
`harness-backend-dev`, `harness-dev-ops`, `harness-pm`, `harness-documentor`, `harness-eng-lead`,
`harness-orchestrator` respectively (confirmed against the dict-key text immediately preceding each
block).

## Confirmed collector semantics

Read `harness_yaml.py:438-441`:
```python
shared = []
for entry in (parsed.get("shared") or []):
    if isinstance(entry, dict) and "path" in entry:
        shared.append(str(entry["path"]))
```
Confirms manifest order is preserved verbatim.

Read `.harness/team-config.yaml:77-87` — the `shared:` block's first entry (line 79) is
`{ path: .harness/*/features/*/quarantine/** }`, followed by `package.json` and the other seven
unchanged entries in original order. So the quarantine glob must be first in each fixture's shared
list.

## Before (verbatim)

```
FAIL test_manifest_domains_matches_the_regex_walk_on_the_real_manifest: harness-backend-dev: shared mismatch
  got:      ['.harness/*/features/*/quarantine/**', 'package.json', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock', 'pyproject.toml', 'uv.lock', 'requirements.txt', 'tsconfig.json']
  expected: ['package.json', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock', 'pyproject.toml', 'uv.lock', 'requirements.txt', 'tsconfig.json']
```
(rc=1, this was the only FAIL line printed by `test-harness-yaml.py`; assert stopped at the first
fixture key reached, `harness-backend-dev`.)

## Edit made

Inserted `".harness/*/features/*/quarantine/**",` as a new first line ahead of the existing
`"package.json", ...` line, at each of the six sites (post-edit line numbers shift by +1 per prior
insertion, so the final positions are 42, 59, 78, 95, 118, 133 — one edit call touched all six in
one pass before any re-run). No other line in the file was reordered, reworded, or reflowed.

## After (verbatim, with captured exit status)

```
ok   test_merge_key_override_is_not_a_duplicate
ok   test_missing_pyyaml_is_reportable_not_a_second_crash
ok   test_duplicate_key_is_catchable_as_a_parse_error
ok   test_duplicate_key_raises
ok   test_nested_duplicate_key_raises
ok   test_bare_date_scalar_stays_str
ok   test_int_and_bool_resolvers_are_not_stripped
ok   test_manifest_domains_matches_the_regex_walk_on_the_real_manifest
ok   test_manifest_domains_excludes_non_canonical_read_true
ok   test_bootstrap_marker_lifecycle
ok   test_marker_self_unlinks_when_yaml_imports
ok   test_require_or_die_ignores_the_retired_project_dir_variable
ok   test_require_or_die_survives_a_missing_harness_boundary
ok   test_exactly_one_guarded_import_in_the_tree
ok   test_c_loader_is_used_when_libyaml_is_available
ok   test_load_plan_accepts_a_well_formed_plan
ok   test_every_required_task_field_is_actually_required
ok   test_load_plan_rejects_the_shapes_that_broke_PLAN_md
ok   test_load_plan_backticked_path_is_not_silently_cleaned
ok   test_load_plan_reports_line_and_column_on_malformed_yaml
ok   test_the_shipped_template_and_the_SPEC_example_both_satisfy_load_plan
ok   test_load_plan_accepts_a_station_only_record_and_only_with_a_station
rc=0
```

**Zero FAIL lines. rc=0.** (The PyYAML-bootstrap-marker diagnostic block interleaved above is
expected stderr/stdout noise from `test_bootstrap_marker_lifecycle` exercising fail-closed paths in
a sandboxed tempdir — not a failure; that test's own `ok` line follows it.)

## Discriminating-revert proof (scratch copy, outside the tracked tree)

Copied `test-harness-yaml.py` and `harness_yaml.py` to `/tmp/feat51-scratch/` (never inside the
worktree). Reverted exactly ONE site — `harness-eng-lead`'s shared list (post-edit line 118, chosen
because it is NOT the first fixture key, proving the loop reaches past `harness-backend-dev` before
catching a real regression) — by removing its quarantine-glob line, leaving the other five sites
fixed. Ran with `HARNESS_PROJECT_DIR` pointed at the real worktree manifest so `MANIFEST_PATH`
still resolved correctly:

```
FAIL test_manifest_domains_matches_the_regex_walk_on_the_real_manifest: harness-eng-lead: shared mismatch
  got:      ['.harness/*/features/*/quarantine/**', 'package.json', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock', 'pyproject.toml', 'uv.lock', 'requirements.txt', 'tsconfig.json']
  expected: ['package.json', 'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock', 'pyproject.toml', 'uv.lock', 'requirements.txt', 'tsconfig.json']
```
rc=1. Names `harness-eng-lead` specifically, confirming the assert discriminates on each fixture
entry rather than short-circuiting. (Two unrelated FAILs also appeared —
`test_marker_self_unlinks_when_yaml_imports` and `test_the_shipped_template_and_the_SPEC_example...`
— both artifacts of running from a bare `/tmp` scratch dir lacking the real repo's directory layout
(missing `../templates/plan.yaml`, different tempdir marker path); not related to this fix and
expected per this file's own G-17-style caveat about scratch-copy runs.)

Scratch copy discarded: `rm -rf /tmp/feat51-scratch` — confirmed gone (`ls` returned "No such file
or directory").

## Sites changed (final, post-edit line numbers)

| Line | Agent |
|---|---|
| 42 | harness-backend-dev |
| 59 | harness-dev-ops |
| 78 | harness-pm |
| 95 | harness-documentor |
| 118 | harness-eng-lead |
| 133 | harness-orchestrator |

## Git status observations

**Worktree** (`git -C .../FEAT-51-claude-code-lifecycle-safety status --porcelain`):
```
 M .claude/skills/harness/bin/test-harness-yaml.py
 M .harness/harness/features/FEAT-51-claude-code-lifecycle-safety/feature.json
?? .harness/harness/features/FEAT-51-claude-code-lifecycle-safety/notes/qa-2026-09-01-03-validator.md
```
The `test-harness-yaml.py` modification is mine (the only file I touched). The `feature.json`
modification and the untracked `qa-2026-09-01-03-validator.md` note were already present before I
started this task (confirmed by an initial `git status --porcelain` check at the start of my run) —
not mine.

**Main checkout** (`git -C /Users/molchairuangutai/GitHub/harness status --porcelain`): identical
set of untracked entries before and after my edit (six pre-existing untracked paths, all unrelated
to FEAT-51's fixture file). No new entries gained — confirms no cross-tree write hazard occurred.
