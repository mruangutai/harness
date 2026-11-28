"""unit_support.py — the one import seam a tests/unit file needs before its other imports.

The runner launches each unit file as `python <path>` with cwd at the repository root, so Python
puts tests/unit/ first on sys.path and this module imports with no setup of its own. Importing it
computes the three anchors once and puts bin/ and tests/ on sys.path (bin/ first), so the file can
then import any bin module and any shared tests/*_support.py module.

    from unit_support import ROOT, BIN, TESTS   # pathlib.Path, absolute
    from unit_support import load_script        # a bin script no plain import reaches

    ROOT   the repository root (the checkout holding tests/)
    BIN    ROOT/.claude/skills/harness/bin
    TESTS  ROOT/tests

A file that honours a bin override (test-check-state-shipped-ctx.py's CHECK_STATE_BIN_DIR) keeps
it: after this import it inserts the override at sys.path[0] itself. The override wins over BIN
only for the modules it contains; a module missing from it still imports from BIN. This module reads no environment variable, so an override set for one file reaches no other.
"""
import sys
from pathlib import Path

TESTS = Path(__file__).resolve().parents[1]
ROOT = TESTS.parent
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"

sys.path.insert(0, str(TESTS))
sys.path.insert(0, str(BIN))


def load_script(name, path=None, module_name=None, register=False):
    """Load a bin script a plain import cannot reach (a hyphenated name, or a copy an override
    variable names) and return it as a fresh module: `ws = load_script("worktree-state.py")`.

    `path` replaces BIN/name; `module_name` defaults to the file stem with hyphens as underscores;
    `register=True` binds the module in sys.modules before exec, which a script declaring
    dataclasses or a package submodule needs. harness_boundary.load_repo_module does the load, so
    a failed exec raises its RepoModuleError carrying the original exception.
    """
    from harness_boundary import load_repo_module
    module_name = module_name or Path(name).stem.replace("-", "_")
    return load_repo_module(module_name, path or BIN / name, register)
