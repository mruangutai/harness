# Receipt — T-02 helper tests, RED — harness-backend-dev

**BLUF:** `.claude/skills/harness/bin/test-harness-yaml.py` created with the nine named T-02 tests,
`run-unit-tests.sh`'s `SCRIPTS` array updated, and the full suite verified RED (exit 1, no
`MISCONFIGURED`, all 9 pre-existing suites still PASS). `harness_yaml.py` was NOT created — that's T-03.

## Verify — exact invocation, run twice, second run pasted verbatim (elision marked)

```
CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh; echo $?
```

```
[... 9 pre-existing suites' internal test output, unchanged from before this task, elided by me ...]
PASS test-validate-digest.py
PASS test-gh-sync.py
PASS test-check-state.py
PASS test-check-expertise.py
PASS test-gen-decisions-index.py
PASS test-bash-write-guard.py
PASS test-check-domain.py
PASS test-render-brief.py
PASS test-cost-report.py
FAIL test_duplicate_key_raises: No module named 'harness_yaml'
FAIL test_nested_duplicate_key_raises: No module named 'harness_yaml'
FAIL test_bare_date_scalar_stays_str: No module named 'harness_yaml'
FAIL test_int_and_bool_resolvers_are_not_stripped: No module named 'harness_yaml'
FAIL test_manifest_domains_matches_the_regex_walk_on_the_real_manifest: No module named 'harness_yaml'
FAIL test_manifest_domains_excludes_non_canonical_read_true: No module named 'harness_yaml'
FAIL test_bootstrap_marker_lifecycle: No module named 'harness_yaml'
FAIL test_marker_self_unlinks_when_yaml_imports: No module named 'harness_yaml'
FAIL test_exactly_one_guarded_import_in_the_tree: expected only harness_yaml.py, got []
FAIL test-harness-yaml.py
1
```

That final bare `1` is the literal `echo $?` output for the exact invocation above (re-run after the
fixture-strengthening and `_HAVE_YAML` -> `hy.yaml` fix below, to confirm both still hold RED). All 9
pre-existing suites report `PASS`. No `MISCONFIGURED` line anywhere in the output. Exit code **1**.

## The nine tests, in order

1. `test_duplicate_key_raises`
2. `test_nested_duplicate_key_raises`
3. `test_bare_date_scalar_stays_str`
4. `test_int_and_bool_resolvers_are_not_stripped`
5. `test_manifest_domains_matches_the_regex_walk_on_the_real_manifest`
6. `test_manifest_domains_excludes_non_canonical_read_true`
7. `test_bootstrap_marker_lifecycle`
8. `test_marker_self_unlinks_when_yaml_imports`
9. `test_exactly_one_guarded_import_in_the_tree`

## Interface T-03 must build to (decided here, cheap/reversible — test shape only)

- `harness_yaml.DuplicateKeyError` — a named exception class (not bare `Exception`), raised by
  `load_str`/`load_file` on a repeated mapping key at any nesting depth.
- `harness_yaml.load_str(text: str, where: str) -> dict`
- `harness_yaml.load_file(path: str) -> dict`
- `harness_yaml.manifest_domains(manifest_path: str, agent: str) -> (mine: list[str], shared: list[str])`
  — order-preserving, matching `check-domain.sh`'s pre-change `collect()` exactly, for EVERY agent in
  the manifest, not just `teams[].members[]` entries. Verified against the real
  `.harness/team-config.yaml` for `harness-backend-dev`, `harness-dev-ops`, `harness-pm`,
  `harness-documentor` (nested under `teams[].members[]`) AND `harness-eng-lead` (`leads:`) and
  `harness-orchestrator` (bare top-level `orchestrator:`) — the last two deliberately live outside
  `teams[].members[]` so an implementation that walks only that path passes the first four rows and
  silently returns empty `mine` for every lead and the orchestrator, which is empty-globs-on-every-
  write once T-04/T-05 convert the hooks. All six fixtures are inlined in the test file
  (`COLLECT_FIXTURE`), computed by running the extracted pre-change `collect()` regex logic directly
  against the real manifest, not by hand-tracing.
- Test 6's synthetic manifest has **no top-level `shared:` key at all** (only `teams:`).
  `manifest_domains` must therefore read the top-level `shared:` key defensively
  (e.g. `parsed.get("shared", [])`), not assume it is always present — a `KeyError` here must not be
  "fixed" by adding `shared: []` to the test fixture; that would be editing a test to pass.
- `harness_yaml.INSTALL_COMMAND` — string constant (untested directly here, referenced in T-03).
- `harness_yaml.require_or_die() -> None` — resolves project root via `CLAUDE_PROJECT_DIR` env (or
  cwd), unlinks `<root>/.harness/.pyyaml-bootstrap` if yaml is importable and it exists, else exits
  non-zero to stderr with `INSTALL_COMMAND`.
- `harness_yaml.require_or_bootstrap(root: str, payload: dict | None = None) -> bool` — `True` =
  allow, `False` = block. `payload=None` means read hook JSON from stdin (real hook usage); tests
  pass an explicit `{"session_id": ...}` dict to control identity deterministically. Marker path is
  `<root>/.harness/.pyyaml-bootstrap`.
- **No new module-level state.** PLAN.md:382 requires the module have none. Test 7 forces the
  "yaml missing" branch by setting `harness_yaml.yaml = None` directly (save/restore around the
  test) rather than introducing a flag like `_HAVE_YAML`. This pins the name the module's single
  `try: import yaml / except ImportError: yaml = None` must bind to at module scope — every
  "is yaml available" branch in `require_or_die`/`require_or_bootstrap` must check that same
  `yaml`/`None` binding, not a separately-tracked boolean, or the test cannot force the branch.

## Notable decisions (test-shape, reversible — not `## Decisions`-worthy)

- Test 9's needle (`"except ImportError"`) is assembled at runtime via string concatenation AND the
  scan excludes any `test-*.py` file in `bin/` — belt-and-suspenders against this test file
  self-matching once T-03 lands. Verified zero `except ImportError` occurrences in `bin/` today.
- Test 6's fixture is a synthetic temp manifest (not the real one) — the real manifest has zero
  non-canonical `read:` spellings (D-13), so a synthetic fixture is required to exercise the branch.

## Open questions

- None blocking. T-03 should treat the interface above as the contract; if it needs a different
  shape it must be a plan/PLAN.md decision, not a silent test edit.

## Files touched

- `.claude/skills/harness/bin/test-harness-yaml.py` (new)
- `.claude/skills/harness/bin/run-unit-tests.sh` (SCRIPTS array)
- `.harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-harness-backend-dev-T02-helper-tests-red.md` (this file)
- `.harness/features/FEAT-05-pyyaml-file-parsers/observations/harness-backend-dev.md` (new)
