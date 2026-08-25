"""layout_fixtures.py — the ONE copy of the layout-detector fixture data (issue #382).

test-layout-migration.py and test-check-state.py both build sandboxed trees whose
reader stubs must carry the form fragments layout_migration's READER_TABLE matches.
Before this module the stub text, the reader lists and the marker's fleet content
were maintained in triplicate; units 3-7 edit the reader table, and every edit had
to be mirrored in three files in matching spellings or a suite reddened with a
failure that looked like a detector bug. Edit the table -> edit the stubs HERE, once.

The marker path itself is NOT restated anywhere: read `layout_migration.MARKER`.

Not a test file (the run-unit-tests.sh drift detector scans only test-*.py). The
paren-balance constraint that binds layout_migration.py's table (issue #380) is NOT
load-bearing here — this file contains none of case_20's probe predicates, so it is
skipped by that scanner. Do not inherit that audit into fixture edits.
"""

import layout_migration as _lm

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
    ".agents/skills/harness/bin/check-domain.sh": {
        "legacy":   "SWEEP_GLOBS=('.harness/features/*/plan.yaml')\n",
        "migrated": "SWEEP_GLOBS=('.harness/*/features/*/plan.yaml')\n",
    },
    ".agents/skills/harness/bin/check-plan-routes.py": {
        "legacy":   'plans = glob.glob(os.path.join(root, ".harness", "features", "*", "plan.yaml"))\n',
        "migrated": 'plans = glob.glob(os.path.join(root, ".harness", repo, "features", "*", "plan.yaml"))\n',
    },
    ".agents/skills/harness/bin/check-state.sh": {
        "legacy":   'for fy in glob.glob(os.path.join(H, "features", "*", "feature.json")):\n',
        "migrated": 'for fy in glob.glob(os.path.join(H, _repo, "features", "*", "feature.json")):\n',
    },
    ".agents/skills/harness/bin/factory_claim.py": {
        "legacy":   'FEATURES_ROOT = os.path.join(r(), ".harness", "features")\n',
        "migrated": 'FEATURES_ROOT = os.path.join(r(), ".harness", _seg, "features")\n',
    },
    ".agents/skills/harness/bin/factory_config.py": {
        "legacy":   '_PROBE = os.path.join("docs", "harness", "SPEC.md")\n',
        "migrated": '_PROBE = os.path.join(".harness", _name, "docs", "SPEC.md")\n',
    },
    ".agents/skills/harness/bin/gen-decisions-index.py": {
        "legacy":   'HEADER = "the authority is docs/harness/DECISIONS.md"\n',
        "migrated": 'HEADER = "the authority is .harness/repoA/docs/DECISIONS.md"\n',
    },
    ".agents/skills/harness/bin/harness_boundary.py": {
        "legacy":   'HARNESS_CONTROL_PLANE = ("docs/harness/**",)\n',
        "migrated": 'HARNESS_CONTROL_PLANE = (".harness/*/docs/**",)\n',
    },
}

# The path->surface grouping is DERIVED from the detector's own table, never
# restated (reuse review, 2026-08-14): restating it here recreated one layer down
# the drift class #382 fixed — a renamed table row would silently stop being
# covered by the fixtures.
FEATURES_READERS = [r.path for r in _lm.READER_TABLE if r.surface == "features"]
DOCS_READERS = [r.path for r in _lm.READER_TABLE if r.surface == "docs"]

# And the stub set must cover the table exactly — a drifted key is a LOUD import
# error, not a quietly narrowed suite.
if set(STUB) != {r.path for r in _lm.READER_TABLE}:
    raise RuntimeError(
        "layout_fixtures.STUB keys do not match layout_migration.READER_TABLE: "
        + repr(set(STUB) ^ {r.path for r in _lm.READER_TABLE}))
