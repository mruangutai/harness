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
            ".harness/codebase/api-surface.md",
            ".harness/codebase/domains/**",
            ".harness/features/*/notes/receipt-harness-backend-dev-*.md",
            ".harness/expertise/harness-backend-dev.md",
            ".harness/features/*/observations/harness-backend-dev.md",
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
            ".harness/codebase/stack.md",
            ".harness/features/*/notes/receipt-harness-dev-ops-*.md",
            ".harness/expertise/harness-dev-ops.md",
            ".harness/features/*/observations/harness-dev-ops.md",
        ],
        [
            "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
            "pyproject.toml", "uv.lock", "requirements.txt", "tsconfig.json",
        ],
    ),
    "harness-pm": (
        [
            ".harness/features/*/BRIEF.md",
            ".harness/features/*/PLAN.md",
            ".harness/features/*/notes/research-*.md",
            ".harness/notes/research-*.md",
            ".harness/features/*/notes/uat-*.md",
            ".harness/codebase/product-surface.md",
            ".harness/codebase/glossary.md",
            ".harness/expertise/harness-pm.md",
            ".harness/features/*/observations/harness-pm.md",
        ],
        [
            "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
            "pyproject.toml", "uv.lock", "requirements.txt", "tsconfig.json",
        ],
    ),
    "harness-documentor": (
        [
            "docs/**",
            "README.md",
            ".harness/README.md",
            ".harness/codebase/INDEX.md",
            ".harness/codebase/architecture.md",
            ".harness/expertise/harness-documentor.md",
            ".harness/features/*/observations/harness-documentor.md",
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
            ".harness/features/*/runs/*-eng/**",
            ".harness/expertise/harness-eng-lead.md",
            ".harness/features/*/observations/harness-eng-lead.md",
        ],
        [
            "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
            "pyproject.toml", "uv.lock", "requirements.txt", "tsconfig.json",
        ],
    ),
    "harness-orchestrator": (
        [
            ".harness/features/**",
            ".harness/features/*/notes/answers-*.md",
            ".harness/features/*/notes/ship-review-*.md",
            ".harness/expertise/harness-orchestrator.md",
            ".harness/features/*/observations/harness-orchestrator.md",
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
    """D-12's receipt as a standing test: exactly one `except ImportError` in
    the whole bin/ tree, and it lives in harness_yaml.py. The needle is
    assembled at runtime and test-*.py files are excluded from the scan, so
    this test file can never self-match (it lives in bin/ too)."""
    needle = "except" + " " + "ImportError"
    hits = []
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
        if needle in text:
            hits.append(name)
    assert set(hits) == {"harness_yaml.py"}, f"expected only harness_yaml.py, got {hits!r}"


TESTS = [
    test_duplicate_key_raises,
    test_nested_duplicate_key_raises,
    test_bare_date_scalar_stays_str,
    test_int_and_bool_resolvers_are_not_stripped,
    test_manifest_domains_matches_the_regex_walk_on_the_real_manifest,
    test_manifest_domains_excludes_non_canonical_read_true,
    test_bootstrap_marker_lifecycle,
    test_marker_self_unlinks_when_yaml_imports,
    test_exactly_one_guarded_import_in_the_tree,
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
