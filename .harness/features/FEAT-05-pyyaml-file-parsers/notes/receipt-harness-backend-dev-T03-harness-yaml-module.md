# Receipt — T-03 harness_yaml.py — harness-backend-dev

**BLUF:** `harness_yaml.py` is written and 8/9 of T-02's RED tests are now GREEN. The 9th
(`test_manifest_domains_matches_the_regex_walk_on_the_real_manifest`) cannot pass as-is: the real
`.harness/team-config.yaml:18` is not valid YAML (whitespace-preceded `#` inside a flow sequence
truncates the bracket, verified with a bare `yaml.safe_load`, independent of this module). That file
is outside every dev's domain. **BLOCKED on that one line — not on this module.**

## Verify — exact invocation, verbatim

```
CLAUDE_PROJECT_DIR=$(pwd) .claude/skills/harness/bin/run-unit-tests.sh; echo $?
```

Tail of the real run (9 pre-existing suites all `PASS`, confirmed above this excerpt):

```
PyYAML is not importable by this python3 interpreter; allowing this session once.
python3 -m pip install pyyaml
# if that fails with "externally-managed-environment" (PEP 668, e.g. Homebrew/Debian):
python3 -m pip install --user --break-system-packages pyyaml
ok   test_duplicate_key_raises
ok   test_nested_duplicate_key_raises
ok   test_bare_date_scalar_stays_str
ok   test_int_and_bool_resolvers_are_not_stripped
FAIL test_manifest_domains_matches_the_regex_walk_on_the_real_manifest: failed to parse YAML in
  /Users/molchairuangutai/GitHub/harness/.claude/worktrees/fix-harness-tooling-backlog/.harness/team-config.yaml:
  while parsing a flow sequence
  in "<unicode string>", line 18, column 11:
      writes: [.harness/features/*/BRIEF.md ## ...
              ^
expected ',' or ']', but got '<scalar>'
  in "<unicode string>", line 23, column 1:
    orchestrator:
    ^
ok   test_manifest_domains_excludes_non_canonical_read_true
ok   test_bootstrap_marker_lifecycle
ok   test_marker_self_unlinks_when_yaml_imports
ok   test_exactly_one_guarded_import_in_the_tree
FAIL test-harness-yaml.py
1
```

The stray `PyYAML is not importable...` lines are `test_bootstrap_marker_lifecycle` correctly
exercising the "yaml missing" branch (it sets `hy.yaml = None`) — not a real absence.
Exit code **1**. `test-gen-decisions-index.py` PASSed in this run — its RED-baseline failure (DEC-142
ruling over the 30-word cap) was pre-existing before this task and is `docs/harness/**`, the
documentor's domain, not mine.

## Why the 9th test cannot pass without a data fix

`load_file` parses the whole document up front. `.harness/team-config.yaml:18`:

```
writes: [.harness/features/*/BRIEF.md ## Approval, .harness/features/*/PLAN.md ## Approval, .harness/logs/**]
```

Stock PyYAML treats a whitespace-preceded `#` as a comment start even inside `[...]`, so the bracket
never closes for either entry and the parse fails before it ever reaches `orchestrator:`/`teams:`/
`leads:` — the subtrees `manifest_domains` actually reads. Confirmed with a bare `yaml.safe_load`
(no custom loader involved). **Zero-semantic-effect fix, proposed not applied:** quote the three
values — `writes: [".harness/features/*/BRIEF.md ## Approval", ".harness/features/*/PLAN.md ##
Approval", ".harness/logs/**"]`. `main_session` has no `name:`/`domain:` key so `manifest_domains`
never walks it — this is purely a document-parseability fix, no glob semantics change.

**Blast radius surveyed (read-only, not fixed):** three other `.harness/features/*/feature.yaml`
files also fail a bare `yaml.safe_load` for unrelated reasons (stray backtick, bad simple key,
`mapping values not allowed here` — `FEAT-03-subissue-mirror`, `FEAT-04-decisions-index`, this
feature's own `feature.yaml`). None of this feature's four committed `state.yaml` files carry a
duplicate `cost:` key (the "2 cost: keys" cost-report message is from that suite's own synthetic tmp
fixtures, not real data). All of this belongs to whichever task/owner next parses those files
whole — flagging now so it's not discovered mid-conversion.

## Public interface — final

- `INSTALL_COMMAND: str` — module-level constant, D-07 + Amendment 1 (`--user
  --break-system-packages`), `[reasoned, unverified]` note on ordering kept as a code comment.
  Lifetime: process.
- `DuplicateKeyError(Exception)` — `.key`, optional `.where`. Raised by the loader on any repeated
  mapping key, any depth.
- `YamlParseError(Exception)` — `.where`, `.original`. Raised on any other malformed YAML.
- `load_str(text: str, where: str) -> dict`
- `load_file(path: str) -> dict`
- `manifest_domains(manifest_path: str, agent: str) -> (mine: list[str], shared: list[str])` —
  generic recursive dict/list walk matching on any `dict` with both `name` and a list-valued
  `domain`, at any nesting depth (not just `teams[].members[]`); `shared` reads the top-level
  `shared:` key defensively. Every glob `str()`-coerced.
- `require_or_die() -> None`
- `require_or_bootstrap(root: str, payload: dict | None = None) -> bool` — `payload=None` reads
  `HOOK_PAYLOAD` env var (JSON), never stdin (correction to T-02's receipt, verified at
  `check-domain.sh:232-234`; see observations log). Identity chain: `payload["session_id"]` →
  `payload["transcript_path"]` basename stem → `CLAUDE_CODE_SESSION_ID` →
  `CLAUDE_CODE_BRIDGE_SESSION_ID` → fail closed.

All module-level state is the single `try: import yaml / except ImportError: yaml = None` plus pure
class definitions (no I/O). Exactly one `except ImportError` in the tree (test 9 confirms).

**One non-tested edge, noted for whoever writes T-12's callers:** if `load_str`/`load_file` is ever
reached while `yaml is None`, `_StrictSafeLoader` is undefined and the failure is a bare `NameError`
rather than a labeled message. It still fails closed (correct direction), just with a less legible
error; out of this task's tested contract.

## Files touched

- `.claude/skills/harness/bin/harness_yaml.py` (new)
- `.harness/features/FEAT-05-pyyaml-file-parsers/observations/harness-backend-dev.md` (appended)
- `.harness/features/FEAT-05-pyyaml-file-parsers/notes/receipt-harness-backend-dev-T03-harness-yaml-module.md` (this file)

## Open questions

- Q1 (blocking): `.harness/team-config.yaml:18`'s `main_session.writes` flow sequence is not valid
  YAML (whitespace-preceded `#` inside `[...]`) and blocks `test_manifest_domains_matches_the_regex_
  walk_on_the_real_manifest` — and will block every real `manifest_domains` call once T-04/T-05/T-12
  convert the hooks, since `load_file` parses the whole document. Fix proposed above (quote the three
  values, zero semantic effect). File is outside every dev's domain — needs a main-session/orchestrator
  edit, not a dev workaround.
- Q2 (non-blocking): three other `.harness/features/*/feature.yaml` files also fail a bare
  `yaml.safe_load` for unrelated reasons (see blast-radius survey above) — worth a pass before
  whichever task starts parsing `feature.yaml` with this module.
