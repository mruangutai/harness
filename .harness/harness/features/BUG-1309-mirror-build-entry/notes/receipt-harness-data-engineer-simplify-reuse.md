# REUSE angle — BUG-1309-mirror-build-entry

BLUF: the era-set membership test has exactly ONE definition (`feature_schema.BUILD_ENTRY_ERA_EXEMPT`);
every one of the five sites named in the dispatch reads it by import, none re-derives the set. Two
smaller genuine duplications exist beneath it: the *basename-of-feature-dir* derivation that feeds
that membership test, and the terminal-allow-set literal. Two findings below; ranked, with #1 the
recommended single apply.

## Required check: does the era set have one definition?

**Yes — one definition, five importing sites, zero local redefinitions.** Checked at source:

- `feature_schema.py:226` — the one definition (`BUILD_ENTRY_ERA_EXEMPT = {...}`).
- `gh-sync.py:1361,1380` — reads `feature_schema.BUILD_ENTRY_ERA_EXEMPT` directly.
- `check-state.sh:2002` — reads `_fs37.BUILD_ENTRY_ERA_EXEMPT` (imported at `check-state.sh:1987`).
- `post-merge-sweep.sh:223` — reads `feature_schema.BUILD_ENTRY_ERA_EXEMPT` (imported at line 42,
  after `sys.path.insert` at line 38 — the heredoc **can** import; it already does, for this and
  three other modules, so nothing here is import-blocked).
- `merge-gate.py:132` — reads `feature_schema.BUILD_ENTRY_ERA_EXEMPT` (imported at line 11).

No second set literal, no re-derived membership predicate anywhere in the diff. Clean.

## Findings, ranked

### 1 (highest value) — the basename-of-feature-dir derivation feeding era-membership is hand-rolled at three sites, and one already needed a fix the others didn't inherit

- `feature_schema.py:326` — `os.path.basename(feat_dir.rstrip("/"))` (inside `recovery_command_for`).
- `gh-sync.py:1360` — `feature_id = os.path.basename(feat_dir.rstrip("/"))`, identical expression.
- `merge-gate.py:130` — `feat = os.path.basename(feat_dir)`, **missing the `rstrip("/")`.**

**Concrete cost:** `gh-sync.py:1360` needed a dedicated fix (T-12, referenced by the new unit test
at `tests/unit/test-gh-sync-build-entry.py:149-151`, case BE-23: "a trailing slash... Depends on
T-12's rstrip fix at gh-sync.py:1360, already landed") because `os.path.basename` on a
trailing-slash path returns `""`, silently defeating the era-exempt lookup. `merge-gate.py:130`
carries the same bug shape and did **not** get the fix — it is only safe today because its one
caller (`feature_for` at `merge-gate.py:94-101`) builds `feat_dir` from `os.path.dirname(glob_path)`,
which never has a trailing slash. That safety is incidental to the call site, not to the expression
itself; a future caller of `feature_for`'s pattern with a slash-terminated path reproduces the exact
bug T-12 just closed, and nothing forces the two to stay in sync.

**Alternative:** add one function to `feature_schema.py` — e.g. `feature_id_from_dir(feat_dir)`
returning `os.path.basename(feat_dir.rstrip("/"))` — and have `recovery_command_for` (line 326),
`gh-sync.py:1360`, and `merge-gate.py:130` all call it instead of restating the expression. This is
distinct from the existing `_feature_dir_name(display)` (line 307), which parses arbitrary display
TEXT for a `features/` segment and is documented as solving a different problem (no real path
available); it should stay as-is. The new helper is for callers that already hold a real `feat_dir`.

### 2 — the terminal-allow-set `{"opened", "not-applicable", "recovered-terminal"}` is a literal restated twice, not imported

- `merge-gate.py:135` — `if entry in {"opened", "not-applicable", "recovered-terminal"}:`
- `post-merge-sweep.sh:228` — `elif entry not in {"opened", "not-applicable", "recovered-terminal"}:`

Both files already `import feature_schema` (for `BUILD_ENTRY_ERA_EXEMPT`), so nothing blocks either
from reading a shared constant instead. No such constant exists in `feature_schema.py` today.

**Concrete cost:** a future terminal state (the schema enum at `feature-schema.json:98` already
lists a fifth value, `recovery-required`, deliberately excluded from this set) must be added to two
literal sets by hand; missing one silently changes only that site's behavior with no error.

**Alternative:** add `BUILD_ENTRY_TERMINAL_STATES = frozenset({"opened", "not-applicable",
"recovered-terminal"})` to `feature_schema.py` and have both sites read it. Checked test coupling
first (per the dispatch's instruction): `tests/integration/test-merge-gate.py:70-73` and
`tests/unit/test-validate-feature-json.py:527-531` assert against the *values* and resulting
behavior, never against the literal set's source text, so this substitution changes no assertion.

## Checked, not flagged

- **Recovery-notice sentence** (`recover-terminal <path> --yes`) at `gh-sync.py:1368-1369,1373-1374,
  1384-1385`, `merge-gate.py:133`, `post-merge-sweep.sh:227,232`: each occurrence is a distinct full
  sentence with its own prefix (`refuse(...)` vs. two different `print(..., file=sys.stderr)`
  notices), not a restated constant — only the trailing clause is shared prose, and per the
  dispatch's own framing each site's full wording is independently asserted by a test. Not worth
  the churn of extracting a sub-string for four call sites whose surrounding sentences already
  differ; noted, not proposed.
- **`feature_schema.recovery_command_for` / `_feature_dir_name`**: both have exactly the call sites
  the dispatch asked about (`recovery_command_for` at `gh-sync.py:1362` and `merge-gate.py:143`;
  `_feature_dir_name` used only inside `feature_schema.py:351`, itself). No hand-rolled duplicate of
  either found.
- **New unit-test fixtures** (`tests/unit/test-gh-sync-build-entry.py`,
  `tests/unit/test-feature-schema-build-entry.py`) vs. `tests/integration/test-gh-sync.py`: the repo
  ships no shared test-helpers module anywhere under `tests/` (confirmed by glob — no
  `conftest.py`/`helpers.py` exists), so per-file fixture helpers are the established convention, not
  a regression. `write_feature_json`/`read_feature_json` exist in both the integration file
  (pre-dating this diff, `write_feature_json(path, **fields)` builds a doc from kwarg defaults) and
  the new unit file (`write_feature_json(d, doc)` dumps a pre-built doc) — same names, different
  signatures and purposes (subprocess end-to-end fixture vs. in-process unit fixture); not
  duplication. The two new unit files each define their own `feat_dir(tmp, name)` helper
  (near-identical bodies) — intra-diff, both new, four lines each, no existing importable home to
  point at; below the bar for a finding.

## Single highest-value recommendation

**Finding #1** (basename-of-feature-dir derivation). It is not just a style duplication — the tree
already demonstrated the failure mode (T-12's rstrip fix, proven necessary by a real trailing-slash
bug and now pinned by a unit test) at one of the three sites, and the other hand-rolled site did not
inherit the fix. Extracting the one predicate closes that latent gap permanently instead of leaving
it to be independently rediscovered at `merge-gate.py:130` if that call site's input ever changes
shape. Finding #2 is real but lower stakes: both sites are and remain internally consistent with each
other today, so the cost is only future drift, not an already-demonstrated defect class.
