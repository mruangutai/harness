"""layout_fixtures.py — the ONE copy of the layout-detector fixture data (issue #382).

test-layout-migration.py and test-check-state.py both build sandboxed trees whose
reader stubs must carry the form fragments layout_migration's READER_TABLE matches.
Before this module the stub text, the reader lists and the marker's fleet content
were maintained in triplicate; units 3-7 edit the reader table, and every edit had
to be mirrored in three files in matching spellings or a suite reddened with a
failure that looked like a detector bug. Edit the table -> edit the stubs HERE, once.

The marker path itself is NOT restated anywhere: read `layout_migration.MARKER`.

Not a test file (the run-unit-tests.sh drift detector scans only test-*.py), and
every string below keeps its parens textually balanced — test-check-plan-routes.py
case_20 joins physical lines until paren depth balances, counting parens inside
string literals (issue #380 owns fixing that at the right altitude).
"""

# What the fleet-declaration marker holds in fixtures: one declared repository,
# org/repoA, whose segment `repoA` is the migrated root the evidence stubs use.
FLEET_TEXT = ("schema: factory-fleet/1\nrepos:\n  - name: org/repoA\n"
              "workspace_root: /tmp/harness-fixture-workspaces\n")

# One stub body per (reader file, form): the FRAGMENT the row's pattern matches, in
# the spelling the real file uses — a join, a grant path, a glob — never a copy of
# the real script.
STUB = {
    ".harness/team-config.yaml": {
        "legacy":   "agents:\n  x:\n    write:\n      - { path: .harness/features/*/notes/n.md }\n",
        "migrated": "agents:\n  x:\n    write:\n      - { path: .harness/repoA/features/*/notes/n.md }\n",
    },
    ".claude/skills/harness/bin/check-domain.sh": {
        "legacy":   "SWEEP_GLOBS=('.harness/features/*/plan.yaml')\n",
        "migrated": "SWEEP_GLOBS=('.harness/*/features/*/plan.yaml')\n",
    },
    ".claude/skills/harness/bin/check-plan-routes.py": {
        "legacy":   'plans = glob.glob(os.path.join(root, ".harness", "features", "*", "plan.yaml"))\n',
        "migrated": 'plans = glob.glob(os.path.join(root, ".harness", repo, "features", "*", "plan.yaml"))\n',
    },
    ".claude/skills/harness/bin/check-state.sh": {
        "legacy":   'for fy in glob.glob(os.path.join(H, "features", "*", "feature.json")):\n',
        "migrated": 'for fy in glob.glob(os.path.join(H, _repo, "features", "*", "feature.json")):\n',
    },
    ".claude/skills/harness/bin/factory_config.py": {
        "legacy":   '_PROBE = os.path.join("docs", "harness", "SPEC.md")\n',
        "migrated": '_PROBE = os.path.join(".harness", _name, "docs", "SPEC.md")\n',
    },
    ".claude/skills/harness/bin/gen-decisions-index.py": {
        "legacy":   'HEADER = "the authority is docs/harness/DECISIONS.md"\n',
        "migrated": 'HEADER = "the authority is .harness/repoA/docs/DECISIONS.md"\n',
    },
    ".claude/skills/harness/bin/harness_boundary.py": {
        "legacy":   'HARNESS_CONTROL_PLANE = ("docs/harness/**",)\n',
        "migrated": 'HARNESS_CONTROL_PLANE = (".harness/*/docs/**",)\n',
    },
}

FEATURES_READERS = [
    ".harness/team-config.yaml",
    ".claude/skills/harness/bin/check-domain.sh",
    ".claude/skills/harness/bin/check-plan-routes.py",
    ".claude/skills/harness/bin/check-state.sh",
]
DOCS_READERS = [
    ".claude/skills/harness/bin/factory_config.py",
    ".claude/skills/harness/bin/gen-decisions-index.py",
    ".claude/skills/harness/bin/harness_boundary.py",
]
