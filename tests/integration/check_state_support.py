"""Fixture vocabulary shared by the test-check-state-*.py files.

Split out of tests/integration/test-check-state.py (issue #1527): that one file ran the
whole check-state.sh corpus serially and set the integration pool's wall clock on its
own. The cases moved into six sibling files by invariant family; every builder more than
one of those files uses lives here, unchanged, so the fixture shape stays defined once.

NOT NAMED test-*.py ON PURPOSE: suite_layout refuses a test-shaped file the runner's
tests/{unit,integration}/test-*.py glob would not select, so a shared module under
tests/integration/ has to carry a name outside that vocabulary.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import os
import subprocess
import sys

# Overridable so a fix can be proven RED against a reverted copy — the same
# VALIDATE_DIGEST_BIN escape test-validate-digest.py uses.
SCRIPT = os.environ.get("CHECK_STATE_BIN") or os.path.join(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", ".claude", "skills", "harness", "bin"), "check-state.sh"
)

# THE MARKER IS READ FROM THE RESOLVER ITSELF, never spelled again here: a fixture that
# writes its own copy of the filename stops being a fixture for the rule the moment the
# rule moves (FEAT-42 T-21). Imported from THIS file's directory, not SCRIPT's, so a
# reverted CHECK_STATE_BIN still grades against the live rule.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", ".claude", "skills", "harness", "bin"))
from isolated_bin import isolated_bin        # re-exported to the two mutation cases
import harness_boundary as _hb

HARNESS_JSON_SYNC_ON = """{
  "github": {"sync": true, "repo": "org/repo"}
}
"""

HARNESS_JSON_SYNC_OFF = """{
  "github": {"sync": false, "repo": null}
}
"""


def feature_yaml(parent_line):
    return f"""github:
{parent_line}
  issues:
    T-01: 41
"""


def _root_env(tmp, env=None, **extra):
    """The environment that points check-state.sh at the fixture `tmp` — and the MARKER
    without which the pointer is discarded (FEAT-42 T-12).

    BOTH NAMES. check-state.sh now resolves through harness_boundary.resolve_root, which
    reads HARNESS_PROJECT_DIR and no other name; the reverted sha-3952814 copy this suite is
    diffed against read HARNESS first and the host-owned name second. Both set to one value
    is the only spelling under which the two copies resolve the same root.

    AND THE MARKER. resolve_root honours the override only when .harness/team-config.yaml is
    readable underneath it. No builder in this file wrote one, so after the cutover every
    fixture fell back to the derived root and each case scanned the LIVE repository — wrong
    answers, and seconds per case instead of milliseconds.

    Written only when .harness ALREADY exists and only when it is not already there: the
    "no .harness/ — project not onboarded" case builds no directory at all and must keep
    reaching that branch, and INV-29's (e) and (f) write their own marker first.
    """
    env = dict(os.environ) if env is None else env
    env["CLAUDE_PROJECT_DIR"] = tmp
    env["HARNESS_PROJECT_DIR"] = tmp
    _m = os.path.join(tmp, _hb.MARKER)
    if os.path.isdir(os.path.join(tmp, ".harness")) and not os.path.exists(_m):
        os.makedirs(os.path.dirname(_m), exist_ok=True)
        with open(_m, "w") as _f:
            _f.write("agents: {}\n")
    env.update(extra)
    return env


def make_fixture(tmp, harness_json, parent_line):
    """Fixtures sit at .harness/harness/features/FEAT-TEST/ — one segment name,
    used consistently across every builder in this file (FEAT-21 T-06)."""
    h = os.path.join(tmp, ".harness")
    os.makedirs(os.path.join(h, "harness", "features", "FEAT-TEST"), exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write(harness_json)
    with open(os.path.join(h, "harness", "features", "FEAT-TEST", "feature.json"), "w") as f:
        f.write(feature_yaml(parent_line))
    return h


def run(tmp):
    env = _root_env(tmp)
    r = subprocess.run([SCRIPT], cwd=tmp, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout


def _run_with_gh(tmp, fake):
    env = dict(os.environ)
    env = _root_env(tmp, env)
    env["FACTORY_GH"] = fake
    r = subprocess.run([SCRIPT], cwd=tmp, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout


def _run_with_gh_streams(tmp, fake):
    """Both streams. A TRACEBACK GOES TO STDERR, so a case asserting the gate did not abort
    is blind if it reads stdout alone — measured: removing INV-26's try/except reddened the
    reports case and left the completes case green, because the traceback was never in the
    text it searched. The whole file being one python3 heredoc is what makes an abort total,
    and that is the property this second reader exists to see."""
    env = dict(os.environ)
    env = _root_env(tmp, env)
    env["FACTORY_GH"] = fake
    r = subprocess.run([SCRIPT], cwd=tmp, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout, r.stderr


# The hooks directory both INV-31's fixtures (test-check-state-worktrees.py) and
# BUG-1305's scaffold (test-check-state-records.py) plant a post-merge hook under.
_HOOKS_REL_T = os.path.join(".claude", "skills", "harness", "hooks")
