#!/usr/bin/env python3
from integration_support import ROOT, BIN

import os  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402

import harness_boundary  # noqa: E402
from check_support import Checks  # noqa: E402

REPO_ROOT = str(ROOT)
CHECK = str(BIN / "check-instruction-paths.py")
CHECKER = harness_boundary.load_repo_module("check_instruction_paths", CHECK)

C = Checks()
check = C.check
# Every case's temp roots live under one directory that main() removes at the end.
_BASE = []


def scratch_dir():
    return tempfile.mkdtemp(dir=_BASE[0])


def make_root(body):
    root = scratch_dir()
    path = os.path.join(root, ".omp", "agents", "harness-backend-dev.md")
    os.makedirs(os.path.dirname(path))
    with open(path, "w") as handle:
        handle.write(body)
    return root, path


def run(root, *args):
    return subprocess.run([sys.executable, CHECK, "--root", root, *args], text=True, capture_output=True)


# FEAT-2397: inject-expertise.py loads this checker IN PROCESS and calls `violations(path,
# root)` over its four files, so every row's CLI answer must equal the direct seam's.
PATH_DIRECTIONS = (
    ("inline and fenced relative paths are both violations",
     "` .harness/harness.json`\n```\n.omp/agents/harness-pm.md\n```\n",
     1, (":1:", ":3:", "2 violation(s)")),
    ("control-plane anchored paths are clean",
     "`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json`\n```\n"
     "<HARNESS_CONTROL_PLANE_ROOT>/.omp/agents/harness-pm.md\n```\n",
     0, ("0 violation(s)",)),
    ("control-plane feature path is refused",
     "`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness/features/F/BRIEF.md`\n",
     1, ("feature-directory path anchored to the control plane",)),
    ("feature-tree control-plane path is refused",
     "`<HARNESS_FEATURE_TREE_ROOT>/.harness/harness.json`\n",
     1, ("control-plane path anchored to the feature tree",)),
    ("both feature path shapes are accepted",
     "`<HARNESS_FEATURE_TREE_ROOT>/.harness/features/F/BRIEF.md`\n"
     "`<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/F/BRIEF.md`\n",
     0, ()),
)


def _direct_rows(root, path):
    return [f"VIOLATION {os.path.relpath(path, root)}:{line}: {reason}: {token}"
            for line, reason, token in CHECKER.violations(path, root)]


def case_path_directions():
    for label, body, code, needles in PATH_DIRECTIONS:
        root, path = make_root(body)
        result = run(root)
        check(label, result.returncode == code and all(n in result.stdout for n in needles),
              result.stdout + result.stderr)
        cli_rows = [line for line in result.stdout.splitlines() if line.startswith("VIOLATION ")]
        check(f"direct violations() equals the CLI: {label}",
              _direct_rows(root, path) == cli_rows, result.stdout)
    check("outside scope refuses", run(root, os.path.join(root, "nope.md")).returncode == 2)


def case_expertise_destinations():
    """FEAT-2225 (DEC-253): a distill member writes its Expertise in the feature worktree, so those
    destinations take the feature-tree anchor; reading them from the control plane stays legal."""
    root, _ = make_root("`<HARNESS_FEATURE_TREE_ROOT>/.harness/expertise/<agent>.md`\n"
                        "`<HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/expertise/<agent>.md`\n"
                        "`<HARNESS_CONTROL_PLANE_ROOT>/.harness/expertise/<agent>.md`\n")
    result = run(root)
    check("FEAT-2225 (DEC-253): Expertise destinations take either anchor",
          result.returncode == 0 and "0 violation(s)" in result.stdout, result.stdout)
    root, _ = make_root("`<HARNESS_FEATURE_TREE_ROOT>/.harness/expertise-notes/x.md`\n")
    result = run(root)
    check("FEAT-2225: only a real expertise directory is a feature-tree write",
          result.returncode == 1 and "control-plane path anchored to the feature tree" in result.stdout, result.stdout)


def case_landed_feature_reads():
    """FEAT-1559 (amends DEC-214): a CONCRETE feature id names a landed record, so a path into it
    is a READ of the main corpus and takes the control-plane anchor; a sparse worktree does not
    hold it. A placeholder names the active feature, a write target, and keeps the feature tree."""
    landed = ".harness/harness/features/FEAT-90-fixture-landed/notes/source.md"
    root, _ = make_root(f"`<HARNESS_CONTROL_PLANE_ROOT>/{landed}`\n"
                        f"```\n<HARNESS_CONTROL_PLANE_ROOT>/.harness/kaya/features/BUG-7-x/BRIEF.md\n```\n")
    clean = run(root)
    check("a landed feature read at the control plane is clean",
          clean.returncode == 0 and "0 violation(s)" in clean.stdout, clean.stdout + clean.stderr)
    root, _ = make_root(f"`<HARNESS_FEATURE_TREE_ROOT>/{landed}`\n")
    refused = run(root)
    check("a landed feature read at the feature tree is refused",
          refused.returncode == 1 and "landed feature" in refused.stdout, refused.stdout)
    for placeholder in ("FEAT-NN-slug", "<feat>", "<FEAT>"):
        root, _ = make_root(f"`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness/features/{placeholder}/BRIEF.md`\n")
        result = run(root)
        check(f"a placeholder feature ({placeholder}) at the control plane is still refused",
              result.returncode == 1 and "anchored to the control plane" in result.stdout, result.stdout)


def case_scope_and_debug_read():
    check("empty scope refuses", run(scratch_dir()).returncode == 2)
    listed = run(REPO_ROOT, "--list-scope")
    for expected in ("harness-verification-rules/SKILL.md", "harness-expertise/SKILL.md", "harness-handoff/SKILL.md", "harness-backend-dev.md", "harness/templates/PLAN.md"):
        check("scope contains " + expected, expected in listed.stdout, listed.stdout)
    backend = os.path.join(REPO_ROOT, ".omp", "agents", "harness-backend-dev.md")
    debug_line = next(line for line in open(backend, encoding="utf-8")
                      if "harness-systematic-debugging/SKILL.md" in line).strip()
    relative_path = debug_line.split("`", 2)[1].replace(
        "<HARNESS_CONTROL_PLANE_ROOT>/", "")
    debug_path = os.path.join(REPO_ROOT, relative_path)
    product_cwd = scratch_dir()
    product_path = os.path.join(product_cwd, relative_path)
    check("product clone can read anchored systematic-debugging skill",
          os.path.isfile(debug_path)
          and not os.path.exists(product_path)
          and "harness-systematic-debugging" in open(
              debug_path, encoding="utf-8").read(200),
          f"control={debug_path}; product={product_path}")


def main():
    with tempfile.TemporaryDirectory() as base:
        _BASE.append(base)
        for case in (case_path_directions, case_expertise_destinations, case_landed_feature_reads,
                     case_scope_and_debug_read):
            case()
    sys.exit(C.report())


if __name__ == "__main__":
    main()
