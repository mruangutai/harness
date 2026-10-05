#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CHECK = os.path.join(REPO_ROOT, ".claude", "skills", "harness", "bin",
                     "check-instruction-paths.py")
RESULTS = []

def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print(("PASS" if ok else "FAIL") + " - " + name + (" (" + detail + ")" if detail and not ok else ""))

def make_root(body):
    root = tempfile.mkdtemp()
    path = os.path.join(root, ".omp", "agents", "harness-backend-dev.md")
    os.makedirs(os.path.dirname(path))
    with open(path, "w") as handle:
        handle.write(body)
    return root, path

def run(root, *args):
    return subprocess.run([sys.executable, CHECK, "--root", root, *args], text=True, capture_output=True)






def case_path_directions():
    root, _ = make_root("` .harness/harness.json`\n```\n.omp/agents/harness-pm.md\n```\n")
    red = run(root)
    check("inline and fenced relative paths are both violations", red.returncode == 1 and ":1:" in red.stdout and ":3:" in red.stdout and "2 violation(s)" in red.stdout, red.stdout + red.stderr)
    root, _ = make_root("`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json`\n```\n<HARNESS_CONTROL_PLANE_ROOT>/.omp/agents/harness-pm.md\n```\n")
    green = run(root)
    check("control-plane anchored paths are clean", green.returncode == 0 and "0 violation(s)" in green.stdout, green.stdout + green.stderr)
    for body, label, detail in (
        ("`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness/features/F/BRIEF.md`\n", "control-plane feature path is refused", "feature-directory path anchored to the control plane"),
        ("`<HARNESS_FEATURE_TREE_ROOT>/.harness/harness.json`\n", "feature-tree control-plane path is refused", "control-plane path anchored to the feature tree"),
    ):
        root, _ = make_root(body)
        result = run(root)
        check(label, result.returncode == 1 and detail in result.stdout, result.stdout)
    root, _ = make_root("`<HARNESS_FEATURE_TREE_ROOT>/.harness/features/F/BRIEF.md`\n`<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/F/BRIEF.md`\n")
    check("both feature path shapes are accepted", run(root).returncode == 0)
    check("outside scope refuses", run(root, os.path.join(root, "nope.md")).returncode == 2)


def case_landed_feature_reads():
    """FEAT-1559 (amends DEC-214): a CONCRETE feature id names a landed record, so a path into it
    is a READ of the main corpus and takes the control-plane anchor; a sparse worktree does not
    hold it. A placeholder names the active feature, a write target, and keeps the feature tree."""
    landed = ".harness/harness/features/FEAT-23-ship-flow-fixes/notes/source.md"
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
    check("empty scope refuses", run(tempfile.mkdtemp()).returncode == 2)
    listed = subprocess.run([sys.executable, CHECK, "--root", REPO_ROOT, "--list-scope"], text=True, capture_output=True)
    for expected in ("harness-verification-rules/SKILL.md", "harness-expertise/SKILL.md", "harness-handoff/SKILL.md", "harness-backend-dev.md", "harness/templates/PLAN.md"):
        check("scope contains " + expected, expected in listed.stdout, listed.stdout)
    backend = os.path.join(REPO_ROOT, ".omp", "agents", "harness-backend-dev.md")
    debug_line = next(line for line in open(backend, encoding="utf-8")
                      if "harness-systematic-debugging/SKILL.md" in line).strip()
    relative_path = debug_line.split("`", 2)[1].replace(
        "<HARNESS_CONTROL_PLANE_ROOT>/", "")
    debug_path = os.path.join(REPO_ROOT, relative_path)
    product_cwd = tempfile.mkdtemp()
    product_path = os.path.join(product_cwd, relative_path)
    check("product clone can read anchored systematic-debugging skill",
          os.path.isfile(debug_path)
          and not os.path.exists(product_path)
          and "harness-systematic-debugging" in open(
              debug_path, encoding="utf-8").read(200),
          f"control={debug_path}; product={product_path}")




def main():
    for case in (case_path_directions, case_landed_feature_reads, case_scope_and_debug_read):
        case()
    if any(not row[1] for row in RESULTS):
        raise SystemExit(1)

if __name__ == "__main__":
    main()
