#!/usr/bin/env python3
"""Tests for harness_yaml.py (T-03, not yet written when this lands).

RED by design (T-02): every test below imports `harness_yaml` from this same
`bin/` directory. Until T-03 creates that module, every test fails on import
and the suite is red. Plain `assert`, python3, stdlib only, shaped after
test-check-state.py's main()-returns-0/1 convention.

Nine tests, named to match PLAN.md T-02 exactly, in that order.
"""
import os
import subprocess
import sys
import tempfile

BIN_DIR = os.path.dirname(os.path.realpath(__file__))
if BIN_DIR not in sys.path:
    sys.path.insert(0, BIN_DIR)

# Repo root: four levels above .claude/skills/harness/bin. CLAUDE_PROJECT_DIR
# overrides when the caller has already resolved it (run-unit-tests.sh does).
REPO_ROOT = os.environ.get("CLAUDE_PROJECT_DIR") or os.path.abspath(
    os.path.join(BIN_DIR, "..", "..", "..", "..")
)
MANIFEST_PATH = os.path.join(REPO_ROOT, ".harness", "team-config.yaml")

# D-03 equivalence fixture: the PRE-change collect() output from
# check-domain.sh:105-126, run against this repo's real .harness/team-config.yaml
# and inlined here as literals (not derived from harness_yaml — that would prove
# nothing). manifest_domains() must return exactly these tuples for these agents.
COLLECT_FIXTURE = {
    "harness-backend-dev": (
        [
            "src/**",
            ".claude/skills/harness/bin/**",
            ".harness/*/features/*/notes/receipt-harness-backend-dev-*.md",
            ".harness/expertise/harness-backend-dev.md",
            ".harness/*/expertise/harness-backend-dev.md",
            ".harness/*/features/*/observations/harness-backend-dev.md",
        ],
        [
            "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
            "pyproject.toml", "uv.lock", "requirements.txt", "tsconfig.json",
        ],
    ),
    "harness-dev-ops": (
        [
            ".github/**",
            "Dockerfile",
            ".harness/harness.json",
            ".claude/skills/harness/bin/**",
            ".harness/*/features/*/notes/receipt-harness-dev-ops-*.md",
            ".harness/expertise/harness-dev-ops.md",
            ".harness/*/expertise/harness-dev-ops.md",
            ".harness/*/features/*/observations/harness-dev-ops.md",
        ],
        [
            "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
            "pyproject.toml", "uv.lock", "requirements.txt", "tsconfig.json",
        ],
    ),
    "harness-pm": (
        [
            ".harness/*/features/*/BRIEF.md",
            ".harness/*/features/*/PLAN.md",
        ".harness/*/features/*/plan.yaml",
            ".harness/*/features/*/notes/research-*.md",
            ".harness/notes/research-*.md",
            ".harness/*/features/*/notes/uat-*.md",
            ".harness/glossary.md",
            ".harness/expertise/harness-pm.md",
            ".harness/*/expertise/harness-pm.md",
            ".harness/*/features/*/observations/harness-pm.md",
        ],
        [
            "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
            "pyproject.toml", "uv.lock", "requirements.txt", "tsconfig.json",
        ],
    ),
    "harness-documentor": (
        [
            "docs/**",
            ".harness/*/docs/**",
            "README.md",
            ".harness/README.md",
            ".harness/*/features/*/notes/receipt-harness-documentor-*.md",
            ".harness/expertise/harness-documentor.md",
            ".harness/*/expertise/harness-documentor.md",
            ".harness/*/features/*/observations/harness-documentor.md",
        ],
        [
            "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
            "pyproject.toml", "uv.lock", "requirements.txt", "tsconfig.json",
        ],
    ),
    # These two live OUTSIDE teams[].members[] — bare top-level `orchestrator:`
    # and `leads:` — so a manifest_domains() that walks only teams[].members[]
    # would pass the four rows above while returning empty `mine` for both of
    # these, which turns into a silent exit-2-on-every-write once the hooks
    # convert. The pre-change collect() is a flat line scan and does not care
    # about nesting, so it must not either.
    "harness-eng-lead": (
        [
            ".harness/*/features/*/runs/*-eng/**",
            ".harness/expertise/harness-eng-lead.md",
            ".harness/*/expertise/harness-eng-lead.md",
            ".harness/*/features/*/observations/harness-eng-lead.md",
        ],
        [
            "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
            "pyproject.toml", "uv.lock", "requirements.txt", "tsconfig.json",
        ],
    ),
    "harness-orchestrator": (
        [
            ".harness/*/features/**",
            ".harness/*/features/*/notes/answers-*.md",
            ".harness/*/features/*/notes/ship-review-*.md",
            ".harness/expertise/harness-orchestrator.md",
            ".harness/*/expertise/harness-orchestrator.md",
            ".harness/*/features/*/observations/harness-orchestrator.md",
        ],
        [
            "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
            "pyproject.toml", "uv.lock", "requirements.txt", "tsconfig.json",
        ],
    ),
}


def test_duplicate_key_raises():
    """D-02, both directions: a repeated top-level key raises the module's
    own duplicate-key error, and a normal mapping is unaffected."""
    import harness_yaml as hy

    raised = False
    try:
        hy.load_str("id: first\nid: second\n", "t")
    except hy.DuplicateKeyError:
        raised = True
    assert raised, "expected hy.DuplicateKeyError on a repeated top-level key"

    result = hy.load_str("a: 1\nb: two\n", "t")
    assert result == {"a": 1, "b": "two"}, f"normal mapping came back wrong: {result!r}"


def test_nested_duplicate_key_raises():
    """The regex this replaces saw only column-0 duplicates; the loader must
    also raise on a repeat nested inside a mapping."""
    import harness_yaml as hy

    raised = False
    try:
        hy.load_str("outer:\n  id: first\n  id: second\n", "t")
    except hy.DuplicateKeyError:
        raised = True
    assert raised, "expected hy.DuplicateKeyError on a nested repeated key"


def test_bare_date_scalar_stays_str():
    """D-08: the timestamp resolver is stripped, so a bare date scalar stays str."""
    import harness_yaml as hy

    result = hy.load_str("d: 2026-07-31\n", "t")
    assert result["d"] == "2026-07-31", f"got {result['d']!r}"
    assert isinstance(result["d"], str), f"expected str, got {type(result['d'])}"


def test_int_and_bool_resolvers_are_not_stripped():
    """D-08 negative half: the strip is surgical (timestamp only), not blanket."""
    import harness_yaml as hy

    result = hy.load_str("cycles_used: 3\nschema_version: 2\nx: yes\n", "t")
    assert result["cycles_used"] == 3 and isinstance(result["cycles_used"], int)
    assert result["schema_version"] == 2 and isinstance(result["schema_version"], int)
    assert result["x"] is True, f"expected True, got {result['x']!r}"


def test_manifest_domains_matches_the_regex_walk_on_the_real_manifest():
    """D-03 equivalence proof: manifest_domains() must equal the pre-change
    collect() logic for every agent in this repo's real manifest."""
    import harness_yaml as hy

    for agent, (expected_mine, expected_shared) in COLLECT_FIXTURE.items():
        mine, shared = hy.manifest_domains(MANIFEST_PATH, agent)
        assert list(mine) == expected_mine, (
            f"{agent}: mine mismatch\n  got:      {list(mine)!r}\n  expected: {expected_mine!r}"
        )
        assert list(shared) == expected_shared, (
            f"{agent}: shared mismatch\n  got:      {list(shared)!r}\n  expected: {expected_shared!r}"
        )


def test_manifest_domains_excludes_non_canonical_read_true():
    """D-13: read: yes / read: True resolve truthy under safe_load and must be
    excluded from `mine`, same as the canonical read: true. read: no entries
    at otherwise-identical paths must still land in `mine`."""
    import harness_yaml as hy

    manifest = """
teams:
  - team-name: T
    members:
      - name: agentX
        domain:
          - { path: p-yes, read: yes }
          - { path: p-true, read: True }
          - { path: p-yes-off, read: no }
          - { path: p-true-off, read: no }
"""
    with tempfile.TemporaryDirectory() as tmp:
        manifest_path = os.path.join(tmp, "team-config.yaml")
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(manifest)
        mine, shared = hy.manifest_domains(manifest_path, "agentX")
        assert "p-yes" not in mine, f"read: yes leaked into mine: {mine!r}"
        assert "p-true" not in mine, f"read: True leaked into mine: {mine!r}"
        assert "p-yes-off" in mine, f"read: no wrongly excluded: {mine!r}"
        assert "p-true-off" in mine, f"read: no wrongly excluded: {mine!r}"


def test_bootstrap_marker_lifecycle():
    """E3, four cases: absent -> writes marker, grants. present + same identity
    -> grants silently. present + different identity -> blocks. marker write
    fails (read-only dir) -> blocks. Forces the "yaml missing" branch by setting
    the module's own `yaml` binding to None rather than introducing new
    module-level state (PLAN.md:382 forbids that) or uninstalling real PyYAML —
    the single `try: import yaml / except ImportError: yaml = None` is the
    binding every "is yaml available" branch must route through."""
    import harness_yaml as hy

    with tempfile.TemporaryDirectory() as tmp:
        harness_dir = os.path.join(tmp, ".harness")
        os.makedirs(harness_dir, exist_ok=True)
        marker = os.path.join(harness_dir, ".pyyaml-bootstrap")

        orig_yaml = hy.yaml
        hy.yaml = None
        try:
            # case 1: absent -> writes marker, allows
            allowed_1 = hy.require_or_bootstrap(tmp, payload={"session_id": "sess-A"})
            assert allowed_1 is True, "expected allow on first (absent-marker) call"
            assert os.path.exists(marker), "expected the marker to be written"

            # case 2: present, same identity -> allows silently
            allowed_2 = hy.require_or_bootstrap(tmp, payload={"session_id": "sess-A"})
            assert allowed_2 is True, "expected silent allow when identity matches"

            # case 3: present, different identity -> blocks
            allowed_3 = hy.require_or_bootstrap(tmp, payload={"session_id": "sess-B"})
            assert allowed_3 is False, "expected block when identity differs"

            # case 4: marker write fails (read-only dir) -> blocks
            os.remove(marker)
            os.chmod(harness_dir, 0o500)
            try:
                allowed_4 = hy.require_or_bootstrap(tmp, payload={"session_id": "sess-C"})
                assert allowed_4 is False, "expected block when the marker write fails"
            finally:
                os.chmod(harness_dir, 0o700)
        finally:
            hy.yaml = orig_yaml


def test_marker_self_unlinks_when_yaml_imports():
    """require_or_die() unlinks an existing marker and returns normally when
    yaml is importable. A bare `import harness_yaml` must NOT touch the marker
    — the module's only import-time behaviour is the single `import yaml`."""
    import harness_yaml as hy

    with tempfile.TemporaryDirectory() as tmp:
        harness_dir = os.path.join(tmp, ".harness")
        os.makedirs(harness_dir, exist_ok=True)
        marker = os.path.join(harness_dir, ".pyyaml-bootstrap")

        with open(marker, "w", encoding="utf-8") as f:
            f.write("sess-A")

        orig_project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
        os.environ["CLAUDE_PROJECT_DIR"] = tmp
        try:
            hy.require_or_die()  # yaml is importable in this environment (T-01)
        finally:
            if orig_project_dir is None:
                os.environ.pop("CLAUDE_PROJECT_DIR", None)
            else:
                os.environ["CLAUDE_PROJECT_DIR"] = orig_project_dir
        assert not os.path.exists(marker), "require_or_die() must unlink the marker"

        # Recreate the marker; a bare import (no require_or_die/require_or_bootstrap
        # call) must leave it untouched.
        with open(marker, "w", encoding="utf-8") as f:
            f.write("sess-A")
        env = dict(os.environ)
        env["CLAUDE_PROJECT_DIR"] = tmp
        subprocess.run(
            [sys.executable, "-c", "import harness_yaml"],
            cwd=BIN_DIR, env=env, check=True,
        )
        assert os.path.exists(marker), "a bare import must not unlink the marker"


def test_exactly_one_guarded_import_in_the_tree():
    """Two-assertion rule replacing the old single exact-set check.

    D-12 (PLAN.md:229) is scoped to `import yaml`, not to guarded imports in
    general — a guard on some other dependency (e.g. jsonschema, D-04) violates
    no signed decision. The old single assertion widened D-12's scope by
    accident: it treated ANY guarded import anywhere in bin/ as equivalent to a
    yaml fallback. Splitting into two assertions restores D-12 to its actual
    scope at full strength while still capping the general pattern.

    The needle is assembled at runtime and test-*.py files are excluded from
    the scan, so this test file can never self-match (it lives in bin/ too).
    """
    needle = "except" + " " + "ImportError"
    yaml_tokens = ("import yaml", "from yaml")
    guarded_hits = []       # any file with the `except ImportError` needle
    yaml_guarded_hits = []  # subset: needle AND a yaml import token, same file
    for name in sorted(os.listdir(BIN_DIR)):
        if name.startswith("test-"):
            continue
        if not (name.endswith(".py") or name.endswith(".sh")):
            continue
        path = os.path.join(BIN_DIR, name)
        try:
            text = open(path, encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        if needle not in text:
            continue
        guarded_hits.append(name)
        # Substring check is safe here: "import yaml" is NOT a substring of
        # "import harness_yaml" (verified) because "import " is followed
        # immediately by "yaml" only in the former — there is no leading
        # space collapse that would make "harness_yaml" match. Do not
        # "simplify" this into a bare `"yaml" in text` check — that WOULD
        # false-positive on `import harness_yaml`.
        if any(tok in text for tok in yaml_tokens):
            yaml_guarded_hits.append(name)

    # Assertion 1 — D-12 at full strength, restored to its real scope: a
    # guarded YAML import (needle + yaml token co-occurring in the SAME file)
    # exists in exactly one file. This must stay `==`, not a subset — D-12
    # forbids a second yaml fallback path from ever landing unnoticed.
    # factory_decompose.py has a real, unguarded `import yaml` today; wrapping
    # it in a guard would trip this assertion, and that failing loud is
    # correct — do not weaken this assertion to accommodate that file.
    assert set(yaml_guarded_hits) == {"harness_yaml.py"}, (
        f"expected only harness_yaml.py to guard a yaml import, got {yaml_guarded_hits!r}"
    )

    # Assertion 2 — the generalised anti-fallback rule: one guarded import per
    # required dependency, each living in the module whose job IS that
    # dependency's policy. FEAT-14 (D-04) added jsonschema as a second
    # required dependency, so feature_schema.py is now allowed alongside
    # harness_yaml.py. check-domain.sh is T-06's tight try around
    # `import feature_schema` — T-06 is main-session-direct and lands AFTER
    # this fix, so it holds zero occurrences of the needle right now. This
    # MUST be a subset (`<=`), never `==`: an equality assertion sized to all
    # three fails immediately (check-domain.sh is empty today), and one sized
    # to today's two goes red the moment T-06 lands with nothing driving it.
    # Subset is what spans that window without losing the cap.
    # feature-worktree.py added 2026-08-20 by operator ruling (FEAT-30 Q1). T-01's SIGNED
    # intent required it: "import harness_boundary lazily and, if the import fails, exit 2
    # with a message naming the module." It guards a FIRST-PARTY sibling, which is the same
    # category check-domain.sh is already allowed for — not a fourth third-party fallback,
    # which is what this cap exists to prevent. The alternative considered and rejected was
    # dropping the guard: it breaks no test today, because NOTHING exercises the guarded
    # branch, but it departs from signed text to buy nothing.
    allowed = {"harness_yaml.py", "feature_schema.py", "check-domain.sh",
               "feature-worktree.py"}
    assert set(guarded_hits) <= allowed, (
        f"unexpected guarded-import file(s) outside the allowed set: "
        f"{set(guarded_hits) - allowed!r}"
    )


def test_missing_pyyaml_is_reportable_not_a_second_crash():
    """Review finding 1: with PyYAML absent, load_str could not report its own
    premise failing.

    `yaml.load(...)` raised `AttributeError: 'NoneType' has no attribute 'load'`, and
    Python then evaluated `except yaml.YAMLError` — raising a SECOND AttributeError
    that escaped uncaught. So on a machine with no PyYAML, check-state reported every
    file as "does not parse: 'NoneType' object has no attribute 'YAMLError'" and the
    plain scripts died with a raw traceback. The user never saw INSTALL_COMMAND, in
    the one scenario this feature exists for.

    `require_or_die` was written as the gate for exactly this and had ZERO production
    callers, so nothing intercepted it upstream either.
    """
    import harness_yaml as hy
    saved = hy.yaml
    try:
        hy.yaml = None
        try:
            hy.load_str("a: 1", "probe")
            return False, "no exception raised at all"
        except hy.MissingDependency as e:
            if "pip install" not in str(e):
                return False, f"message lacks the install command: {e}"
        except Exception as e:
            return False, f"raised {type(e).__name__}, not MissingDependency: {e}"
    finally:
        hy.yaml = saved
    # And it must be catchable by a caller that only knows about YamlParseError.
    if not issubclass(hy.MissingDependency, hy.YamlParseError):
        return False, "MissingDependency does not subclass YamlParseError"
    return True, ""


def test_duplicate_key_is_catchable_as_a_parse_error():
    """Review findings 2, 3 and 5.

    DuplicateKeyError was a bare Exception, so `except YamlParseError` did NOT catch
    it — and gh-sync.py and upgrade-config.py both wrote exactly that, believing they
    had covered "the file is unreadable". A duplicated key made each die with a raw
    traceback reading "the tool is broken" when the truth was "your file is",
    defeating the very handler each had just added.

    Finding 5: the message must also carry DEC-156's guidance, because removing
    check-state.sh's dedicated scan dropped that wording from the codebase entirely
    while a comment claimed it was preserved.
    """
    import harness_yaml as hy
    if not issubclass(hy.DuplicateKeyError, hy.YamlParseError):
        return False, "DuplicateKeyError does not subclass YamlParseError"
    # The position must be the DUPLICATE's own line, not merely "a" position. A first
    # version of the mark fix passed the loop's last key_node, so the number was right
    # only when the duplicate happened to be last — which it was, in the fixture I
    # tested with. Asserting a SPECIFIC line is what makes this discriminating.
    try:
        hy.load_str("a: 1\nb: 2\nc: 3\na: 4\n", "probe")
        return False, "a duplicate key on line 4 did not raise"
    except hy.DuplicateKeyError as e:
        if "line 4" not in str(e):
            return False, f"reported the wrong line for a line-4 duplicate: {e}"
    try:
        hy.load_str("cost: 1\ncost: 2\n", "probe")
        return False, "a duplicate key did not raise"
    except hy.YamlParseError as e:          # the caller's generic handler
        if "DEC-156" not in str(e):
            return False, f"message lacks DEC-156 guidance: {e}"
        if not isinstance(e, hy.DuplicateKeyError):
            return False, "caught as YamlParseError but is not a DuplicateKeyError"
    return True, ""


def test_merge_key_override_is_not_a_duplicate():
    """Review finding 3: `flatten_mapping` ran BEFORE the duplicate scan.

    It splices merge-key (`<<: *anchor`) entries into node.value, so an explicit
    override of an inherited key counted as a duplicate — which it is not.
    `{<<: *base, b: 3}` is legal YAML with well-defined override semantics and stdlib
    safe_load returns `b: 3`.

    Not reachable from this repo's files (no anchors), but harness is a portable
    framework: a downstream project that DRYs its domain lists with `<<:` would have
    BOTH write hooks fail closed on every write, blaming the user for a duplicate key
    in valid YAML. A guard wrong about the rulebook is this feature's own failure mode,
    and being wrong in the strict direction is no better.
    """
    import harness_yaml as hy
    import yaml as _y
    DOC = "base: &b {a: 1, b: 2}\nchild: {<<: *b, b: 3}\n"
    try:
        got = hy.load_str(DOC, "probe")["child"]
    except hy.DuplicateKeyError:
        return False, "a legal merge-key override raised DuplicateKeyError"
    want = _y.safe_load(DOC)["child"]
    if got != want:
        return False, f"merge semantics differ from stdlib: {got} != {want}"
    # ...and real duplicates must STILL raise, at both depths.
    for label, doc in (("top-level", "cost: 1\ncost: 2\n"),
                       ("nested", "steps:\n  - id: s\n    cost: 1\n    cost: 2\n")):
        try:
            hy.load_str(doc, "probe")
            return False, f"a {label} duplicate stopped raising"
        except hy.DuplicateKeyError:
            pass
    return True, ""


def test_c_loader_is_used_when_libyaml_is_available():
    """The LOADER CHOICE is pinned, because reverting it is invisible (PR #149 LOW-5).

    Forcing the pure-Python SafeLoader back left 13/13 and 12/12 green while costing 7.3x
    on this tree's corpus — a performance decision with no assertion behind it is a default
    waiting to be restored by the next person who tidies the class statement.

    Conditional on the build: a source install of PyYAML without libyaml is legal, and this
    must not fail there. That is the point of asserting AGREEMENT with the build rather than
    asserting the C loader unconditionally.
    """
    import yaml
    import harness_yaml as hy

    has_c = getattr(yaml, "__with_libyaml__", False) and hasattr(yaml, "CSafeLoader")
    assert hy._LOADER_IS_C == bool(has_c), (
        f"libyaml available={has_c} but _LOADER_IS_C={hy._LOADER_IS_C} — "
        f"the loader choice drifted from the build")
    # And the two overrides survive whichever base was chosen. Duplicate detection is the
    # one that would vanish silently if a future base bypassed the Python constructor: the
    # 92-file equivalence corpus contains NO duplicate keys, so it could never have caught it.
    try:
        hy.load_str("a: 1\nb:\n  c: 1\n  c: 2\n", "dup-fixture")
        raise AssertionError("a nested duplicate key did not raise under the active loader")
    except hy.DuplicateKeyError as e:
        assert e.key == "c", f"wrong key reported: {e.key!r}"
        assert e.mark is not None and e.mark.line >= 0, "line/column lost under this loader"


GOOD_PLAN = """schema: plan/1
feature: FEAT-TEST
approval:
  status: approved
tasks:
  - id: T-01
    title: do the thing
    change_type: logic
    execution_mode: main-session-direct
    execution_reason: carve-out
    traces: [REQ-01]
    depends_on: []
    status: pending
    files:
      - src/a.py
      - src/b.py
    verify: |
      python3 -m pytest
    intent: |
      Do the thing, carefully.
"""


def _plan(tmp, text):
    p = os.path.join(tmp, "plan.yaml")
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def test_load_plan_accepts_a_well_formed_plan():
    """The discriminator. Every rejection case below passes against a load_plan that
    rejects everything, so one acceptance case is what makes them mean anything."""
    import harness_yaml as hy

    with tempfile.TemporaryDirectory() as tmp:
        doc = hy.load_plan(_plan(tmp, GOOD_PLAN))
        assert doc["tasks"][0]["files"] == ["src/a.py", "src/b.py"], doc["tasks"][0]["files"]
        assert doc["tasks"][0]["verify"] == "python3 -m pytest\n", repr(doc["tasks"][0]["verify"])


def test_every_required_task_field_is_actually_required():
    """EVERY entry in REQUIRED_TASK_FIELDS, generated FROM the tuple.

    Review found `intent:` had been added to REQUIRED_TASK_FIELDS with no test at all:
    dropping it back out left all three suites green. A fixture that CARRIES a field
    cannot assert the field is required — `case_23j`'s 12-line `intent:` pins that intent
    stays OUT of the budget, which is a different claim.

    Generated from the tuple rather than listed, so a field added to production and not
    to a list here cannot go unexercised. There is no list to forget.
    """
    # Imported HERE, not at module scope: this file deliberately has no top-level
    # `import yaml`, because test_missing_pyyaml_is_reportable_not_a_second_crash
    # exercises the absent-parser path.
    import yaml
    import harness_yaml as hy

    # PIN THE TUPLE'S CONTENTS FIRST. A loop generated from REQUIRED_TASK_FIELDS cannot
    # notice a field being removed FROM it — the loop just stops testing that field and
    # stays green. Measured: dropping "intent" back out left this test passing until this
    # assertion existed. Generation protects against a field ADDED and untested; only an
    # explicit set protects against one DELETED.
    assert set(hy.REQUIRED_TASK_FIELDS) == {
        "id", "title", "change_type", "execution_mode", "files", "verify", "intent"
    }, (f"REQUIRED_TASK_FIELDS changed to {hy.REQUIRED_TASK_FIELDS}. If that is "
        f"deliberate, update this set and say why in the commit — `intent:` in "
        f"particular is what teams/build.yaml dispatches on.")
    for field in hy.REQUIRED_TASK_FIELDS:
        doc = yaml.safe_load(GOOD_PLAN)
        del doc["tasks"][0][field]
        with tempfile.TemporaryDirectory() as tmp:
            try:
                hy.load_plan(_plan(tmp, yaml.safe_dump(doc)))
            except hy.PlanSchemaError as e:
                assert field in str(e), (
                    f"omitting {field!r} raised, but the message does not name it: {e}")
            else:
                raise AssertionError(
                    f"a plan with no {field!r} loaded CLEAN — it is in "
                    f"REQUIRED_TASK_FIELDS but nothing enforces it")


def test_load_plan_rejects_the_shapes_that_broke_PLAN_md():
    """The three failures issue #147 was filed about, now unrepresentable.

    Measured on the pre-change tree: `safe_load` fails on 35 of the 36 task blocks in
    the four live plans. 26 carry a `files:` that begins with a backtick — markdown
    decoration inside a data field — and one of those 26 is ALSO `execution_mode:
    **SPLIT`, which YAML reads as an alias; it is the same block, not a 27th. The
    other 9 put a second `": "` inside a plain scalar via `execution_mode: <mode> —
    reason: ...`.

    The cases below are NOT a census of those 35. Two are drawn from the corpus; the
    rest are shapes the loader must also refuse. Each must raise a YamlParseError
    subclass rather than silently resolving something nobody wrote.
    """
    import harness_yaml as hy

    cases = {
        "backticked files value (the 26-case class)":
            GOOD_PLAN.replace("      - src/a.py", "      - `src/a.py`"),
        "bolded execution_mode (FEAT-08 T-04's **SPLIT)":
            GOOD_PLAN.replace("execution_mode: main-session-direct",
                              "execution_mode: **SPLIT (D-10, amended)**"),
        "files: as a bare string, not a list":
            GOOD_PLAN.replace("    files:\n      - src/a.py\n      - src/b.py",
                              "    files: src/a.py, src/b.py"),
        "an unknown execution_mode token":
            GOOD_PLAN.replace("execution_mode: main-session-direct", "execution_mode: solo"),
        "a duplicate task id":
            GOOD_PLAN + GOOD_PLAN[GOOD_PLAN.index("  - id: T-01"):],
        "no tasks at all":
            "schema: plan/1\nfeature: FEAT-TEST\ntasks: []\n",
        "a task missing verify:":
            GOOD_PLAN.replace("    verify: |\n      python3 -m pytest\n", ""),
    }
    for label, text in cases.items():
        with tempfile.TemporaryDirectory() as tmp:
            try:
                hy.load_plan(_plan(tmp, text))
            except hy.YamlParseError:
                continue
            raise AssertionError(f"ACCEPTED what it must reject: {label}")


def test_load_plan_backticked_path_is_not_silently_cleaned():
    """The SECOND #147 question: may an entry carry an annotation like `(delete)`?

    No — and the loader is what says so, not a cleanup heuristic. The old `_clean()`
    stripped backticks and a trailing comma but not a parenthetical, so
    `` `bin/cost-report.py` (delete) `` resolved ONLY because a `/**` grant swallowed
    the suffix. Under a narrower grant it was a false violation. Here the value is
    the literal string, so a resolver gets exactly what the author wrote and can say
    it resolves to nothing — rather than guessing which characters were commentary.
    """
    import harness_yaml as hy

    text = GOOD_PLAN.replace("      - src/a.py", "      - src/a.py (delete)")
    with tempfile.TemporaryDirectory() as tmp:
        doc = hy.load_plan(_plan(tmp, text))
        got = doc["tasks"][0]["files"][0]
        assert got == "src/a.py (delete)", f"loader altered the authored value: {got!r}"


def test_load_plan_reports_line_and_column_on_malformed_yaml():
    """A denial that says only "does not parse" on a 300-line plan is a loop the
    author cannot exit. YamlParseError already carries the original exception; this
    pins that it survives to the caller."""
    import harness_yaml as hy

    with tempfile.TemporaryDirectory() as tmp:
        try:
            hy.load_plan(_plan(tmp, "tasks:\n  - id: T-01\n   bad: indent\n"))
        except hy.YamlParseError as e:
            assert "line" in str(e.original).lower(), f"no position in: {e.original}"
            return
        raise AssertionError("malformed YAML was accepted")


def test_the_shipped_template_and_the_SPEC_example_both_satisfy_load_plan():
    """The template, the normative SPEC example, and the loader must agree — mechanically.

    THIS IS ISSUE #147 ITSELF. That ticket exists because `templates/PLAN.md` prescribed one
    `files:` shape while the parser accepted three: an author following the template was
    correct, and an author ignoring it was also correct, and nothing could tell them apart.
    Prose cannot hold two files in agreement; a test can.

    Both artifacts are loaded through the real `load_plan`, so a template that drifts out of
    schema fails here rather than at the next planning session. SPEC.md:1701-1702's previous
    example was itself illegal YAML — three keys on one line — and shipped that way because
    nothing ever tried to parse it.
    """
    import re
    import harness_yaml as hy

    here = os.path.dirname(os.path.abspath(__file__))

    tmpl = os.path.join(here, "..", "templates", "plan.yaml")
    hy.load_plan(tmpl)  # raises on any drift

    spec = open(os.path.join(here, "..", "..", "..", "..", ".harness", "harness", "docs", "SPEC.md"),
                encoding="utf-8").read()
    m = re.search(r"```yaml\n(# plan\.yaml.*?)\n```", spec, re.S)
    assert m, "SPEC.md no longer carries a normative plan.yaml example"
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "plan.yaml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(m.group(1))
        hy.load_plan(path)


TESTS = [
    test_merge_key_override_is_not_a_duplicate,
    test_missing_pyyaml_is_reportable_not_a_second_crash,
    test_duplicate_key_is_catchable_as_a_parse_error,
    test_duplicate_key_raises,
    test_nested_duplicate_key_raises,
    test_bare_date_scalar_stays_str,
    test_int_and_bool_resolvers_are_not_stripped,
    test_manifest_domains_matches_the_regex_walk_on_the_real_manifest,
    test_manifest_domains_excludes_non_canonical_read_true,
    test_bootstrap_marker_lifecycle,
    test_marker_self_unlinks_when_yaml_imports,
    test_exactly_one_guarded_import_in_the_tree,
    # REGISTERED, and the first attempt was not. This file collects from an
    # explicit list, so a test appended after it is defined and never run —
    # which is issue #133's own theme ("logic correct, nothing calls it")
    # landing inside the change that cites it. Caught by mutation, not by review.
    test_c_loader_is_used_when_libyaml_is_available,
    # issue #147 — plan.yaml replaces the markdown-that-looks-like-YAML format.
    test_load_plan_accepts_a_well_formed_plan,
    test_every_required_task_field_is_actually_required,
    test_load_plan_rejects_the_shapes_that_broke_PLAN_md,
    test_load_plan_backticked_path_is_not_silently_cleaned,
    test_load_plan_reports_line_and_column_on_malformed_yaml,
    test_the_shipped_template_and_the_SPEC_example_both_satisfy_load_plan,
]


def main():
    failures = 0
    for t in TESTS:
        try:
            t()
        except Exception as e:  # noqa: BLE001 - a test failing for any reason is a FAIL
            failures += 1
            print(f"FAIL {t.__name__}: {e}")
        else:
            print(f"ok   {t.__name__}")
    if failures:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
