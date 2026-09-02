#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import harness_boundary

ROOT = harness_boundary.resolve_root(HERE)
REF = os.environ.get("HARNESS_REVIEW_SHA") or "HEAD"
CHECKER = os.path.join(ROOT, ".claude/skills/harness/bin/check-instruction-paths.py")
ROWS = [
    ("SC-04 S1 read qa gate", ".claude/skills/harness-qa-gate/SKILL.md", r"\.harness/harness\.json", "HARNESS_CONTROL_PLANE_ROOT", 1),
    ("SC-04 S2 read expertise", ".claude/skills/harness-expertise/SKILL.md", r"\.harness/expertise/<your-agent-name>\.md", "HARNESS_CONTROL_PLANE_ROOT", 1),
    ("SC-04 S3 write receipt", ".claude/skills/harness-handoff/SKILL.md", r"\.harness/<repo>/features/<FEAT>/notes/receipt-<your-agent-name>-<runid>\.md", "HARNESS_FEATURE_TREE_ROOT", 1),
    ("SC-04 S4 read debugging skill", ".omp/agents/harness-backend-dev.md", r"\.(?:agents|claude)/skills/harness-systematic-debugging/SKILL\.md", "HARNESS_CONTROL_PLANE_ROOT", 1),
    ("SC-04 S5 read template config", ".claude/skills/harness/templates/PLAN.md", r"\.harness/team-config\.yaml", "HARNESS_CONTROL_PLANE_ROOT", 1),
    ("SC-11 S2 write observations", ".claude/skills/harness-expertise/SKILL.md", r"\.harness/<repo>/features/<FEAT>/observations/<your-agent-name>\.md", "HARNESS_FEATURE_TREE_ROOT", 2),
]

def direction_failures(content, token_regex, expected_anchor, min_occurrences=1):
    matches = list(re.finditer(r"<(HARNESS_CONTROL_PLANE_ROOT|HARNESS_FEATURE_TREE_ROOT)>/(" + token_regex + r")", content))
    failures = []
    if len(matches) < min_occurrences:
        failures.append("expected at least %d anchored occurrence(s), got %d" % (min_occurrences, len(matches)))
    for match in matches:
        if match.group(1) != expected_anchor:
            failures.append("wrong anchor %s, expected %s" % (match.group(1), expected_anchor))
    return failures

def show(path):
    result = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (REF, path)], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError("git show %s: %s" % (path, result.stderr.strip()))
    return result.stdout

def main():
    verified = subprocess.run(["git", "-C", ROOT, "rev-parse", "--verify", REF + "^{commit}"], text=True, capture_output=True)
    if verified.returncode:
        print("FAIL - unresolved review ref %s: %s" % (REF, verified.stderr.strip()))
        return 1
    failed = 0
    for name, path, token, expected, minimum in ROWS:
        content = show(path)
        problems = direction_failures(content, token, expected, minimum)
        wrong = "<HARNESS_CONTROL_PLANE_ROOT>/" if expected == "HARNESS_FEATURE_TREE_ROOT" else "<HARNESS_FEATURE_TREE_ROOT>/"
        bare = re.sub(r"\\", "", token).replace("(?:agents|claude)", "agents")
        wrong_fixture = wrong + bare * minimum
        bare_fixture = bare
        red = direction_failures(wrong_fixture, token, expected, minimum) and direction_failures(bare_fixture, token, expected, minimum)
        if name == "SC-11 S2 write observations":
            red = red and direction_failures("<HARNESS_FEATURE_TREE_ROOT>/" + bare + bare, token, expected, minimum)
        ok = not problems and red
        print(("PASS" if ok else "FAIL") + " - " + name + (" (%s)" % problems if problems else ""))
        failed += not ok
    scope = subprocess.run([sys.executable, CHECKER, "--root", ROOT, "--list-scope"], text=True, capture_output=True)
    paths = [p for p in scope.stdout.splitlines() if p]
    temp = tempfile.mkdtemp()
    try:
        for path in paths:
            target = os.path.join(temp, path)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w") as handle:
                handle.write(show(path))
        check = subprocess.run([sys.executable, CHECKER, "--root", temp], text=True, capture_output=True)
        summary = re.search(r"scanned (\d+) file\(s\), 0 violation\(s\)", check.stdout)
        ok = check.returncode == 0 and summary and int(summary.group(1)) == len(paths)
        print(("PASS" if ok else "FAIL") + " - reviewed-sha whole scope" + ("" if ok else "\n" + check.stdout + check.stderr))
        failed += not ok
    finally:
        shutil.rmtree(temp)
    return int(bool(failed))

if __name__ == "__main__":
    raise SystemExit(main())
