"""Feature-id probe support shared by the integration suites that prove a rule is uniform.

FEAT-71 deleted every per-feature exemption table. A suite that proves its rule now applies to
EVERY feature id probes synthetic ids PLUS every feature-id-shaped string a module still holds
as data — read from the module, never written in the test — so a reintroduced per-feature table
is probed without any test naming a real feature.
"""
import re

FEATURE_ID = re.compile(r"^(FEAT|BUG|PR)-[0-9]+")


def held_feature_ids(module):
    """Sorted feature-id-shaped strings held in `module`'s top-level collections."""
    held = set()
    for value in vars(module).values():
        if isinstance(value, (dict, set, frozenset, list, tuple)):
            held.update(m for m in value if isinstance(m, str) and FEATURE_ID.match(m))
    return sorted(held)
