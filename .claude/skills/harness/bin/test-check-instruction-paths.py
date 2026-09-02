#!/usr/bin/env python3
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHECK = os.path.join(HERE, "check-instruction-paths.py")
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

def main():
    root, path = make_root("` .harness/harness.json`\n```\n.claude/agents/harness-pm.md\n```\n")
    red = run(root)
    check("inline and fenced relative paths are both violations", red.returncode == 1 and ":1:" in red.stdout and ":3:" in red.stdout and "2 violation(s)" in red.stdout, red.stdout + red.stderr)
    root, _ = make_root("`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json`\n```\n<HARNESS_CONTROL_PLANE_ROOT>/.claude/agents/harness-pm.md\n```\n")
    green = run(root)
    check("control-plane anchored paths are clean", green.returncode == 0 and "0 violation(s)" in green.stdout, green.stdout + green.stderr)
    root, _ = make_root("`<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness/features/F/BRIEF.md`\n")
    wrong = run(root)
    check("control-plane feature path is refused", wrong.returncode == 1 and "feature-directory path anchored to the control plane" in wrong.stdout, wrong.stdout)
    root, _ = make_root("`<HARNESS_FEATURE_TREE_ROOT>/.harness/harness.json`\n")
    mirror = run(root)
    check("feature-tree control-plane path is refused", mirror.returncode == 1 and "control-plane path anchored to the feature tree" in mirror.stdout, mirror.stdout)
    root, _ = make_root("`<HARNESS_FEATURE_TREE_ROOT>/.harness/features/F/BRIEF.md`\n`<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/F/BRIEF.md`\n")
    shapes = run(root)
    check("both feature path shapes are accepted", shapes.returncode == 0, shapes.stdout + shapes.stderr)
    empty = tempfile.mkdtemp()
    no_scope = run(empty)
    check("empty scope refuses", no_scope.returncode == 2, no_scope.stdout + no_scope.stderr)
    repo_root = os.path.abspath(os.path.join(HERE, "../../../.."))
    listed = subprocess.run([sys.executable, CHECK, "--root", repo_root, "--list-scope"], text=True, capture_output=True)
    for expected in ("harness-qa-gate/SKILL.md", "harness-expertise/SKILL.md", "harness-handoff/SKILL.md"):
        check("scope contains " + expected, expected in listed.stdout, listed.stdout)
    outside = run(root, os.path.join(root, "nope.md"))
    check("outside scope refuses", outside.returncode == 2, outside.stdout + outside.stderr)
    failed = [row for row in RESULTS if not row[1]]
    if failed:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
