"""integration_support.py — the one import seam a tests/integration file needs before its other imports.

The runner (run-unit-tests.py, through run_pool.run_one) chdirs to the repository root and
launches each integration file as `python tests/integration/<file>.py`, so Python puts the
absolute tests/integration/ first on sys.path and this module imports with no setup of its own.
Importing it computes the three anchors once and puts bin/ and tests/ on sys.path (bin/ first,
then tests/, then tests/integration/ where Python put it), so the file can then import any bin
module, any shared tests/*_support.py module, and any sibling tests/integration/*_support.py.
No module name is shared between bin/, tests/ and tests/integration/, so the order picks nothing.

    from integration_support import ROOT, BIN, TESTS   # pathlib.Path, absolute, symlinks resolved

    ROOT   the repository root (the checkout holding tests/)
    BIN    ROOT/.claude/skills/harness/bin
    TESTS  ROOT/tests

Ordering: this import comes first, before any bin or tests/*_support.py import; ruff's E402 on
the imports after it is expected (`# noqa: E402` where the file lints). A file that needs str
paths (os.path.join, string concatenation, subprocess argv built by +) converts once at the top,
e.g. `HERE = str(BIN)`, rather than mixing Path and str below.

Overrides are the caller's job; this module reads no environment variable, so an override set for
one file reaches no other:
  - a bin override for a script under test (CHECK_STATE_BIN, PLAN_SIGN_GATE_BIN, ...): the file
    keeps `SCRIPT = os.environ.get("X_BIN") or str(BIN / "x.py")` as written;
  - a repository-root override (test-harness-yaml.py and test-validate-feature-json.py read
    HARNESS_PROJECT_DIR, test-plan-team.py reads HARNESS_PROJECT_DIR or the cwd): the file keeps
    its own `REPO = os.environ.get("HARNESS_PROJECT_DIR") or ...` with ROOT as the fallback only
    where the original fallback was this file's checkout;
  - a bin directory to import from instead of BIN: after this import the file inserts the
    override at sys.path[0] itself. It wins over BIN only for the modules it contains.
"""
import sys
from pathlib import Path

TESTS = Path(__file__).resolve().parents[1]
ROOT = TESTS.parent
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"

sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(BIN))
