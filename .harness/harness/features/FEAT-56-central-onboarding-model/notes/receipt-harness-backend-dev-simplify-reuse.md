# REUSE angle — FEAT-56 simplify pass

BLUF: three concrete reuse findings, all `applicable: true` (both touched paths — `bin/` and
`tests/`) — a third spelling of the `<repo>@<ref>:<path>` format string, a re-implemented
`repo_entry` selection rule, and two test helpers copied byte-for-byte from a sibling test module
instead of imported. No findings on the six `bin/` message sites or the prose surfaces (checked,
clean — see below).

## Findings

1. **`factory_config.py:472`** — `_check_product_configs`'s `factory_cli.fail(...)` call builds
   `f'{m["repo"]}@{m["ref"]}:{m["path"]}'`, a third independent spelling of the
   `<repo>@<ref>:<path>` format that `product_config` already builds at `factory_config.py:303`
   (`human_path = f"{repo_name}@{ref}:{_PRODUCT_CONFIG_PATH}"`) and `board_for` builds again at
   `factory_config.py:366` (`path = f"{repo_name}@{default_branch}:{_PRODUCT_CONFIG_PATH}"`).
   **Cost:** the join format now has three call sites to edit in lockstep if it ever changes
   (e.g. a separator, or reordering ref/path); `product_config_report`'s report rows already
   carry `repo`/`ref`/`path` as separate fields specifically so callers don't re-join them, and
   this call site re-joins anyway. **Alternative:** add one small helper (e.g.
   `_config_locator(repo, ref, path=_PRODUCT_CONFIG_PATH)`) next to `_PRODUCT_CONFIG_PATH` and
   have `product_config`, `board_for`, and `_check_product_configs` all call it instead of
   inlining the f-string three times. `applicable: true`.

2. **`factory_config.py:456-458`** — `_check_product_configs`'s `--repo` narrowing calls
   `repo_entry(fleet, repo_name)` for its validating side effect, then re-derives the same
   "find the entry whose name matches" rule itself: `[e for e in fleet["repos"] if e["name"]
   == repo_name]`. `repo_entry` (factory_config.py:256-266) already performs this exact search
   and already holds the matching entry — the second implementation is thrown away.
   **Cost:** two independent spellings of "match a repo by name" now exist in the same module,
   and they are not even consistent: `repo_entry` uses `entry.get("name")` (safe against a
   dict missing the key), the list comprehension uses `e["name"]` (raises `KeyError` on the same
   input `repo_entry` would have tolerated) — a future edit to one's matching rule silently
   leaves the other behind. **Alternative:** keep the `repo_entry` return value and use it
   directly: `entry = repo_entry(fleet, repo_name); fleet = dict(fleet, repos=[entry])`.
   `applicable: true`.

3. **`tests/unit/test-fleet-product-config.py:52-61,77-81`** — `patched_file_at_ref` and
   `write_fleet` are copied verbatim (identical body and docstring) from
   `tests/unit/test-factory-config.py:61-70,86-90`, the sibling suite for the same module
   (`factory_config`/`fc`). This is narrower than the repo-wide `check()`-harness convention
   (confirmed via grep: ~24 test files each define their own `check()`, a deliberate
   standalone-script pattern, so `check()` itself is NOT a finding here) — `patched_file_at_ref`
   and `write_fleet` exist nowhere else in `tests/`, only in these two files testing the same
   module. **Cost:** a change to how `factory_gh.file_at_ref` is monkeypatched, or to the fleet
   fixture's YAML-dump shape, must be made in both files or the two suites silently diverge on
   how they drive the same production module. **Alternative:** these two are small and
   test-module-local, so the standard fix is a shared `tests/unit/_factory_config_fixtures.py`
   (or similar) that both files import — or, if the project's convention is deliberately
   "no shared test modules, everything self-contained per file" (matching the `check()`
   pattern), note that convention explicitly rather than silently duplicating a second time.
   `applicable: true`.

## Checked and clean

- The six `bin/` message-string edits in the diff (`check-domain.sh`, `check-instruction-paths.py`,
  `check-state.sh`, `gh-sync.py`, `layout_migration.py`, `post-merge-sweep.sh`,
  `upgrade-config.py`) are all plain `print()`/`skip()`/comment prose rewordings (clarifying
  control-plane-vs-fleet-member language) — none of them are `FleetError`-shaped and none
  hand-roll a string that `factory_cli.body` or another existing formatter already produces.
- `product_config_report` (factory_config.py:328-353) composes `product_config` and only reads
  plain fields (`entry["name"]`, `entry["default_branch"]`) directly off the same entry it is
  already iterating — this is not a re-derivation of `repo_entry`'s search (there is no search:
  it already has the entry from the loop) and it does not rebuild the `<repo>@<ref>:<path>`
  string itself (`detail` comes from `str(exc)` on a caught `FleetError`). Clean.
- The 414-line `harness-init/SKILL.md` rewrite and the other doc/template/command edits carry
  no inline code fences in this diff (`git diff … | grep '^```'` — no hits), so there is no
  hand-rolled procedure to compare against an existing script; the only reuse-class finding
  possible there is prose duplication, which is altitude's angle, not mine. Not checked further.
  All of `harness-init/SKILL.md`, the templates, the commands, and the docs resolve to
  `applicable: false` regardless, per the dispatch's domain-guard note.
