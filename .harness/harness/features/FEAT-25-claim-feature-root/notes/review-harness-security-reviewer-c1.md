# Security review — FEAT-25 cycle 1 — `d1ffd7f...8d7b273`

## Scope
Six files under `.claude/skills/harness/bin/`: `factory_claim.py`, `layout_fixtures.py`,
`layout_migration.py`, `test-factory-claim.py`, `test-factory-integration.py`,
`test-layout-migration.py`. `factory_claim.py` is in scope per Expertise P-01 (`bin/factory_*.py`
is a second untrusted-input surface: it builds paths and reads YAML from operator/board-influenced
values). The four `layout_*`/`test-*` non-`factory_claim` files are self-check/test tooling with
no external input — scoped out, verified by reading the diff, not assumed.

## What changed, security-relevant
1. `FEATURES_ROOT` repointed to `.harness/harness/features` (pure rename, matches the sibling
   migration units already landed — check-plan-routes.py, validate-feature-json.py,
   layout_migration.py per plan.yaml D-02's rejected-alternative note).
2. New `no_plan` blocker-gate kind: when a `feature:` label resolves but `plan.yaml` cannot be
   read, the refusal now names the absolute path that was tried (`factory_claim.py:187-199`),
   via `_BlockerCache.plan_path()` (`:99-102`, `os.path.abspath(os.path.join(root, feature,
   "plan.yaml"))`).
3. `layout_migration.py`/`layout_fixtures.py`: `factory_claim.py` added as a reader row/fixture
   pair for the migration self-check. No behavior change to `factory_claim.py` itself from this.

## Findings

### Traced and dismissed — not a finding, pre-existing and unchanged
`_BlockerCache.plan_path()`/`_plan()` builds the plan path from `feature` (the `feature:` label
value off a GitHub issue on the served board — see `_feature_of`, `factory_claim.py:50-63`) via
`os.path.join(self._features_root, feature, "plan.yaml")`. `os.path.join` follows Python's
usual rule: a `feature` value starting with `/` discards `features_root` entirely (absolute-path
injection), and a value containing `..` segments escapes it (relative traversal) — the OS resolves
both at `open()` time regardless of the new `os.path.abspath()` wrapper, which is a string
normalization only and changes no reachability.

I confirmed this join expression is **byte-for-byte unchanged from the base commit** (the diff
hunk shows the same `os.path.join(self._features_root, feature, "plan.yaml")` line moved, not
altered, from `task()` into the new `_plan()`), so this diff introduces no new reachability into
that primitive. Blast radius is also capped independent of the diff: `harness_yaml.load_plan`
wraps every `OSError` (including `FileNotFoundError`/`PermissionError`) into `YamlParseError`
(`harness_yaml.py:249-254`), which `factory_claim.py`'s `except harness_yaml.YamlParseError`
already catches — a traversal/absolute-path probe to a missing or unparseable target degrades to
the ordinary "no plan" refusal, never a crash (checked: `PlanSchemaError` is a `YamlParseError`
subclass, `harness_yaml.py:261`). To turn this into an actual gate bypass, the label-setter would
additionally need a real, schema-matching plan.yaml (top-level mapping, non-empty `tasks:` list)
sitting at a guessable absolute path on the factory host outside `FEATURES_ROOT` — a narrow,
low-likelihood gadget, and per Expertise P-02 the actor who can set a `feature:` label on a served
repo's issue already holds a trust tier the codebase's own design treats as acceptable input for
this exact code path (D-09's "tolerant read" of unresolvable `feature:` labels, cited in
`factory_claim.py`'s own module docstring, predates this diff). **Assessed-and-dismissed per
P-12/P-13, not new.**

### New in this diff, deliberate and reviewed — info, not a finding
The `no_plan` diagnostic (`factory_claim.py:187-199`) is a genuinely new disclosure: pre-diff, no
code path ever printed a filesystem path for "plan unreadable" (it was folded into the
path-free edge-(i) text). This diff makes it name the absolute path tried. I traced where that
text goes: `factory_cli.refuse()`/the bare `print(..., file=sys.stderr)` fallback both write to
**stderr only** (`factory_cli.py:32-52`) — never a GitHub comment, never stdout (C-3's stream
split, unaffected). No `gh` call in this diff posts the message anywhere. This is an intentional,
plan-reviewed decision — `plan.yaml` REQ-02/SC-04/D-03 explicitly require the refusal to "name the
absolute path that was tried" for operator debuggability, and the design note for D-02 states the
tradeoff was considered against a wildcard-root alternative and rejected specifically because it
would break this diagnostic contract. The exposure is: an absolute filesystem path on the factory
host, visible only to whoever reads that run's local stderr/log — not fed back automatically to
the label-setting actor. No secret, token, or PII in the disclosed value. Rating: **info**, not a
finding requiring remediation — recorded so a later reviewer does not re-raise it as novel.

## Other surfaces checked, nothing found
- **Secrets**: grepped the full six-file diff (not just `factory_claim.py`) per P-14 — no
  credential-shaped strings, tokens, or URLs with embedded auth in any of the six files.
- **YAML deserialization**: `harness_yaml.load_plan`'s loader is the codebase's one shared
  `safe_load`-equivalent path (`harness_yaml.py` — the sole `try: import yaml` at the top of the
  file, per its own docstring); this diff calls it through the same existing path, no new
  deserialization surface.
- **Fail-open on the trust boundary**: the new `no_plan` branch is strictly a new *refusal* kind
  (`_blocker_gate` returns a non-None gate tuple, same as the other three kinds) — it narrows
  the pre-existing `task() is None` catch-all rather than loosening it. No claim can proceed
  through this branch; checked `_main`'s use at `:379-387` — `gate is not None` always
  `continue`s or `refuse()`s, never falls through to `create_ref`.
- **Test files**: `test-factory-claim.py`/`test-factory-integration.py`/`test-layout-migration.py`
  changes are path-rename fixups plus new assertions for the `no_plan` branch and the migrated
  `FEATURES_ROOT` default; no subprocess/shell construction, no secrets, no new fixtures that
  weaken an existing assertion.

## Open question (non-blocking)
Provenance assumption per P-07: this review closes the label-injection question on "the actor who
can set a `feature:` label on a served repo's board issue is already inside the tool's accepted
trust tier" — inherited from D-09, not re-derived here. If board label-write is ever opened to a
wider audience than repo collaborators (e.g. a public triage bot, external contributor labels),
that assumption breaks and `_BlockerCache.plan_path` would warrant an actual confinement check
(`os.path.commonpath` or a reject-on-`/`/`..` guard) rather than reliance on `load_plan`'s
schema/OSError catch as the only backstop.
